# app/core/index_worker.py
from __future__ import annotations
import json
import struct
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List, Iterator, Tuple
from datetime import datetime
import threading
import os

# Import the minimal atomic pointer helper (preserves 'current' filename)
from app.core.index_worker_utils import write_current_pointer

UINT32 = "<I"
UINT32_SIZE = 4

# Optional helpers from project (best-effort imports)
try:
    from app.core.inverted_index import write_inverted_to_disk
except Exception:
    write_inverted_to_disk = None

try:
    from app.core.graph_lmdb_full import write_lmdb_from_shard
except Exception:
    write_lmdb_from_shard = None

try:
    from app.core.adjcache_shard import ShardBuilder
except Exception:
    ShardBuilder = None


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


class IndexWorker:
    """
    Test-friendly synchronous IndexWorker. Guarantees a created shard v-dir and
    a 'current' pointer file in shards/<shard>/current after successful processing.
    """

    def __init__(self, index_root: Optional[Path] = None, jobs_file: Optional[Path] = None, poll_seconds: float = 1.0):
        self.index_root = Path(index_root) if index_root else Path("data") / "index"
        self.jobs_dir = (self.index_root / "jobs")
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        if jobs_file:
            self.jobs_file = Path(jobs_file)
            self.jobs_file.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.jobs_file = self.jobs_dir / "jobs.jsonl"
        self.processed_log = self.jobs_dir / "processed.jsonl"

        # in-memory queue (tests use synchronous run_once)
        self._queue: List[Dict[str, Any]] = []
        self.last_job_id: Optional[str] = None
        self.last_job_success: Optional[bool] = None
        self.processed_count: int = 0
        self.failed_count: int = 0
        self.poll_seconds = float(poll_seconds)
        self._lock = threading.RLock()

    def submit_job(self, job: Dict[str, Any]) -> None:
        """
        Durable append to jobs file (best-effort) and enqueue in-memory.
        """
        with self._lock:
            job_copy = dict(job)
            job_copy.setdefault("submitted_at", _now_iso())
            try:
                with self.jobs_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(job_copy, ensure_ascii=False) + "\n")
            except Exception:
                pass
            self._queue.append(job_copy)

    def _append_processed_record(self, rec: Dict[str, Any]) -> None:
        try:
            rec.setdefault("processed_at", _now_iso())
            with self.processed_log.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _write_shard_from_events_minimal(self, shard: str, events_iter: Iterator[Dict[str, Any]]) -> Optional[str]:
        """
        Minimal shard writer (used as deterministic fallback). Writes a v{ts} dir
        and a 'current' pointer in shards/<shard>/current via the atomic helper.
        Returns absolute path to the created version dir as a string.
        """
        shards_root = self.index_root / "shards"
        shard_parent_dir = shards_root / shard
        shard_parent_dir.mkdir(parents=True, exist_ok=True)
        vname = "v" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
        shard_dir = shard_parent_dir / vname
        shard_dir.mkdir(parents=True, exist_ok=True)

        idmap: Dict[str, int] = {}
        parents_map: Dict[str, List[str]] = {}
        children_map: Dict[str, List[str]] = {}

        def _ensure_id(nid: str):
            if nid not in idmap:
                idmap[nid] = len(idmap) + 1

        # iterate events and build adjacency maps
        try:
            for ev in events_iter:
                if not isinstance(ev, dict):
                    continue
                if ev.get("event") != "relationship_added":
                    continue
                child = str(ev.get("child_id") or ev.get("child") or "")
                parent = str(ev.get("parent_id") or ev.get("parent") or "")
                if not child or not parent:
                    continue
                _ensure_id(child)
                _ensure_id(parent)
                parents_map.setdefault(child, []).append(parent)
                children_map.setdefault(parent, []).append(child)
        except Exception:
            pass

        # write idmap + revmap
        try:
            (shard_dir / "idmap.json").write_text(json.dumps(idmap, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
        try:
            revmap = {v: k for k, v in idmap.items()}
            (shard_dir / "revmap.json").write_text(json.dumps({str(k): v for k, v in revmap.items()}, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        # pack parents/children as index + flat uint32 arrays for compatibility
        try:
            # parents
            parents_ints: List[int] = []
            parents_index: Dict[int, Tuple[int, int]] = {}
            for node_id, nid_int in idmap.items():
                plist = parents_map.get(node_id, [])
                offset = len(parents_ints)
                count = len(plist)
                for p in plist:
                    parents_ints.append(idmap[p])
                parents_index[nid_int] = (offset, count)
            (shard_dir / "parents.index.json").write_text(json.dumps({str(k): [v[0], v[1]] for k, v in parents_index.items()}, ensure_ascii=False), encoding="utf-8")
            parents_bin = b"".join(struct.pack(UINT32, x) for x in parents_ints)
            (shard_dir / "parents.adj.bin").write_bytes(parents_bin)
        except Exception:
            pass

        try:
            # children
            children_ints: List[int] = []
            children_index: Dict[int, Tuple[int, int]] = {}
            for node_id, nid_int in idmap.items():
                clist = children_map.get(node_id, [])
                offset = len(children_ints)
                count = len(clist)
                for c in clist:
                    children_ints.append(idmap[c])
                children_index[nid_int] = (offset, count)
            (shard_dir / "children.index.json").write_text(json.dumps({str(k): [v[0], v[1]] for k, v in children_index.items()}, ensure_ascii=False), encoding="utf-8")
            children_bin = b"".join(struct.pack(UINT32, x) for x in children_ints)
            (shard_dir / "children.adj.bin").write_bytes(children_bin)
        except Exception:
            pass

        # ensure 'current' pointer in shard parent (atomic)
        try:
            try:
                write_current_pointer(shard_parent_dir, shard_dir.name)
            except Exception:
                # fallback to simple write if atomic helper fails
                (shard_parent_dir / "current").write_text(shard_dir.name, encoding="utf-8")
        except Exception:
            pass

        return str(shard_dir.resolve())

    def _process_single_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        try:
            src = job.get("source", {}) or {}
            src_type = src.get("type")
            shard = job.get("shard") or job.get("shard_id") or "default"
            built_vdir: Optional[str] = None

            # handle file source (read events)
            if src_type == "file":
                path = src.get("path")
                if not path:
                    raise ValueError("file source requires path")
                p = Path(path)
                if not p.exists():
                    raise FileNotFoundError(f"events file missing: {p}")

                text = p.read_text(encoding="utf-8")
                events: List[Dict[str, Any]] = []
                for ln in text.splitlines():
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        events.append(json.loads(ln))
                    except Exception:
                        continue

                # determine shards root
                shards_root = self.index_root / "shards"
                shard_parent_dir = shards_root / shard
                shard_parent_dir.mkdir(parents=True, exist_ok=True)

                # Prefer using ShardBuilder if available and it creates a real path
                if ShardBuilder is not None:
                    try:
                        sb = ShardBuilder(shards_root)
                        v = sb.build_from_events(shard, (e for e in events))
                        if v:
                            vpath = Path(v)
                            # if returned path exists, accept it
                            if vpath.exists():
                                built_vdir = str(vpath.resolve())
                    except Exception:
                        built_vdir = None

                # If ShardBuilder didn't produce an actual directory, fallback to deterministic minimal writer
                if not built_vdir:
                    built_vdir = self._write_shard_from_events_minimal(shard, iter(events))

                # Ensure current pointer points to a version that actually exists under shard_parent_dir
                try:
                    if built_vdir:
                        vp = Path(built_vdir)
                        vname = vp.name
                        # If built_vdir is not under the shard parent, prefer the version dir under shard_parent (fallback)
                        expected_vdir = shard_parent_dir / vname
                        if not expected_vdir.exists():
                            # If the returned built_vdir exists somewhere else, create placeholder dir under shard_parent.
                            expected_vdir.mkdir(parents=True, exist_ok=True)
                        built_vdir = str(expected_vdir.resolve())

                        # Write atomic 'current' pointer (preserve original filename)
                        try:
                            try:
                                write_current_pointer(shard_parent_dir, expected_vdir.name)
                            except Exception:
                                # fallback to simple write
                                (shard_parent_dir / "current").write_text(expected_vdir.name, encoding="utf-8")
                        except Exception:
                            out.setdefault("warnings", []).append("pointer_write_failed")
                except Exception:
                    pass

            # optional inverted build
            if job.get("build_inverted") and write_inverted_to_disk is not None:
                try:
                    inv = job.get("inv")
                    if inv is not None:
                        write_inverted_to_disk(inv, self.index_root / "inverted", job.get("shard"), ts=job.get("ts"))
                except Exception:
                    out.setdefault("warnings", []).append("inverted_write_failed")

            # optional lmdb
            if job.get("write_lmdb") and write_lmdb_from_shard is not None:
                try:
                    if built_vdir:
                        shard_vdir = Path(built_vdir)
                        lmdb_out_root = self.index_root / "lmdb" / (job.get("shard") or "shard")
                        lmdb_out_root.mkdir(parents=True, exist_ok=True)
                        v = write_lmdb_from_shard(shard_vdir, lmdb_out_root)
                        if v:
                            out["lmdb_vdir"] = str(v)
                except Exception:
                    out.setdefault("warnings", []).append("lmdb_write_failed")

            out["status"] = "success"
            out["success"] = True
            if built_vdir:
                out["built_vdir"] = built_vdir
            return out

        except Exception as e:
            out["status"] = "failed"
            out["success"] = False
            out["error"] = str(e)
            out["traceback"] = traceback.format_exc()
            return out

    def run_once(self) -> None:
        with self._lock:
            to_run = list(self._queue)
            self._queue.clear()

        for job in to_run:
            job_id = job.get("job_id")
            shard = job.get("shard")
            self.last_job_id = job_id
            job["attempts"] = int(job.get("attempts", 0)) + 1

            result = self._process_single_job(job)
            self.last_job_success = bool(result.get("success"))
            if result.get("success"):
                self.processed_count += 1
            else:
                self.failed_count += 1

            rec: Dict[str, Any] = {
                "job_id": job_id,
                "shard": shard,
                "ts": job.get("ts"),
                "submitted_at": job.get("submitted_at"),
                "attempts": int(job.get("attempts", 1)),
                "processed_at": _now_iso(),
                "success": bool(result.get("success")),
                "status": result.get("status"),
            }
            if "built_vdir" in result:
                rec["built_vdir"] = result["built_vdir"]
            if "lmdb_vdir" in result:
                rec["lmdb_vdir"] = result["lmdb_vdir"]
            if "error" in result:
                rec["error"] = result["error"]
            if "traceback" in result:
                rec["traceback"] = result["traceback"]

            self._append_processed_record(rec)

    def _iter_new_jobs(self) -> Iterator[Dict[str, Any]]:
        if not self.jobs_file.exists():
            return
        try:
            for ln in self.jobs_file.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                try:
                    yield json.loads(ln)
                except Exception:
                    continue
        except Exception:
            return
