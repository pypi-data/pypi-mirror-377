# app/core/adjcache_shard.py
"""
Per-shard adjacency index writer (hardened).

Responsibilities (unchanged API):
- Build a compact per-shard adjacency index from an iterator of relationship events.
- Emit an atomic shard directory:
    <out_root>/shards/<shard_id>/v{ts}/
      - idmap.json
      - revmap.json
      - parents.index.json
      - parents.adj.bin
      - children.index.json
      - children.adj.bin
      - manifest.json
  and update `<out_root>/shards/<shard_id>/current` to point to the v{ts} directory.

Notes:
- Writes JSON and binary files atomically (temp-in-same-dir + os.replace).
- Performs best-effort fsync on files and directories.
- Works on Windows and POSIX; atomicity of directory move may vary on some filesystems,
  but this is the conservative pattern used in the rest of the codebase.
- Interface unchanged: build_from_events(shard_id, events) -> Path to vdir
"""

from __future__ import annotations

import json
import os
import struct
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Iterator, Dict, List, Optional
from datetime import datetime

log = logging.getLogger("adjcache_shard")

UINT32 = "<I"
UINT32_SIZE = 4


def _now_ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


def _atomic_write_text(path: Path, text: str) -> None:
    """
    Atomically write text to `path` by writing to a same-dir temp file then os.replace.
    Best-effort fsync of file and directory.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmppath = tempfile.mkstemp(prefix=".tmp_", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                log.debug("fsync(file) unavailable for %s", path)
        # fsync dir (best-effort)
        try:
            dfd = os.open(str(path.parent), os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            log.debug("dir fsync not available for %s", path.parent)
        os.replace(tmppath, str(path))
    finally:
        if os.path.exists(tmppath):
            try:
                os.remove(tmppath)
            except Exception:
                pass


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """
    Atomically write bytes to `path`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmppath = tempfile.mkstemp(prefix=".tmp_", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                log.debug("fsync(file) unavailable for %s", path)
        # fsync dir (best-effort)
        try:
            dfd = os.open(str(path.parent), os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            log.debug("dir fsync not available for %s", path.parent)
        os.replace(tmppath, str(path))
    finally:
        if os.path.exists(tmppath):
            try:
                os.remove(tmppath)
            except Exception:
                pass


class ShardBuilder:
    """
    Build a per-shard adjacency index.

    Usage:
        sb = ShardBuilder(Path("data/index/adjcache"))
        dest = sb.build_from_events("shard1", events_iter)

    Returns Path to created v{ts} directory (Path).
    """

    def __init__(self, out_root: Path):
        self.out_root = Path(out_root)

    @staticmethod
    def _normalize_event(ev: dict) -> Optional[tuple]:
        """
        Return (child, parent) if this event represents a relationship_added, else None.
        Accepts both old and new event shapes.
        """
        if not ev or ev.get("event") != "relationship_added":
            return None
        child = ev.get("child_id") or (ev.get("to") or {}).get("id") or ev.get("child")
        parent = ev.get("parent_id") or (ev.get("from") or {}).get("id") or ev.get("parent")
        if not child or not parent:
            return None
        return str(child), str(parent)

    def _write_index_bin_and_json(
        self, tmpdir: Path, name: str, revmap: List[str], map_src: Dict[str, List[str]], idmap: Dict[str, int]
    ) -> None:
        """
        Write <name>.adj.bin and <name>.index.json into tmpdir using atomic writes.
        - revmap: ordered list of node ids (index -> node_id)
        - map_src: node_id -> [neighbor_node_id, ...] for this side
        - idmap: node_id -> int
        """
        adj_list: List[int] = []
        index: Dict[str, List[int]] = {}
        offset = 0
        for node_id in revmap:
            nbrs = map_src.get(node_id, [])
            # ensure we only index known nodes (present in idmap)
            idxs = [idmap[n] for n in nbrs if n in idmap]
            adj_list.extend(idxs)
            index[str(idmap[node_id])] = [offset, len(idxs)]
            offset += len(idxs)

        # write binary as contiguous uint32 little-endian
        bin_path = tmpdir / f"{name}.adj.bin"
        try:
            # pack into bytes first (safer to write full buffer)
            buf = bytearray()
            for v in adj_list:
                buf.extend(struct.pack(UINT32, v))
            _atomic_write_bytes(bin_path, bytes(buf))
        except Exception:
            log.exception("failed writing binary adjacency for %s", name)
            raise

        # write index json atomically
        idx_path = tmpdir / f"{name}.index.json"
        try:
            _atomic_write_text(idx_path, json.dumps(index, ensure_ascii=False))
        except Exception:
            log.exception("failed writing index json for %s", name)
            raise

    def build_from_events(self, shard_id: str, events: Iterator[dict]) -> Path:
        """
        Build shard index from events iterator and atomically install it under:
            <out_root>/shards/<shard_id>/v{ts}/

        Returns the Path to the created v{ts} directory.
        """
        # collect adjacency into in-memory maps
        parents: Dict[str, List[str]] = {}
        children: Dict[str, List[str]] = {}
        nodes = set()
        event_count = 0

        for ev in events:
            pair = self._normalize_event(ev)
            if not pair:
                continue
            child, parent = pair
            parents.setdefault(child, []).append(parent)
            children.setdefault(parent, []).append(child)
            nodes.add(child)
            nodes.add(parent)
            event_count += 1

        # stable ordering for idmap
        revmap = sorted(nodes)
        idmap = {nid: i for i, nid in enumerate(revmap)}

        ts = _now_ts()
        shard_parent = self.out_root / "shards" / str(shard_id)
        shard_parent.mkdir(parents=True, exist_ok=True)
        vdir_name = f"v{ts}"

        # create a tmpdir under shard_parent to keep same filesystem
        tmp_dir = Path(tempfile.mkdtemp(prefix=f"{vdir_name}.tmp.", dir=str(shard_parent)))
        try:
            # write idmap.json (mapping node_id -> int)
            idmap_path = tmp_dir / "idmap.json"
            try:
                _atomic_write_text(idmap_path, json.dumps(idmap, ensure_ascii=False))
            except Exception:
                log.exception("failed writing idmap.json")
                raise

            # write revmap.json (index -> node_id) — useful for readers
            revmap_path = tmp_dir / "revmap.json"
            try:
                _atomic_write_text(revmap_path, json.dumps(revmap, ensure_ascii=False))
            except Exception:
                log.exception("failed writing revmap.json")
                raise

            # write parents & children adjacency (atomic)
            try:
                self._write_index_bin_and_json(tmp_dir, "parents", revmap, parents, idmap)
            except Exception:
                log.exception("failed writing parents adjacency")
                raise

            try:
                self._write_index_bin_and_json(tmp_dir, "children", revmap, children, idmap)
            except Exception:
                log.exception("failed writing children adjacency")
                raise

            # manifest
            manifest = {
                "version": ts,
                "created": datetime.utcnow().isoformat() + "Z",
                "node_count": len(revmap),
                "event_count": event_count,
            }
            try:
                _atomic_write_text(tmp_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False))
            except Exception:
                log.exception("failed writing manifest.json")
                raise

            # final destination
            dest_dir = shard_parent / vdir_name
            if dest_dir.exists():
                # avoid leaving partial stale data: remove existing dir (rare)
                try:
                    shutil.rmtree(dest_dir)
                except Exception:
                    log.exception("failed removing existing dest_dir %s", dest_dir)
                    raise

            # move tmp_dir -> dest_dir (shutil.move is used; atomicity depends on platform)
            try:
                shutil.move(str(tmp_dir), str(dest_dir))
                # if move successful, ensure dest_dir exists and tmp_dir no longer present
            except Exception:
                log.exception("failed moving tmp_dir to dest_dir")
                # try cleanup
                if tmp_dir.exists():
                    try:
                        shutil.rmtree(tmp_dir)
                    except Exception:
                        pass
                raise

            # atomically update the current pointer
            current_file = shard_parent / "current"
            try:
                _atomic_write_text(current_file, vdir_name)
            except Exception:
                # fallback: try a replace via tmp file
                try:
                    tmp_current = shard_parent / f"current.tmp.{ts}"
                    tmp_current.write_text(vdir_name, encoding="utf-8")
                    os.replace(str(tmp_current), str(current_file))
                except Exception:
                    log.exception("failed updating current pointer for shard %s", shard_id)
                    # don't fail the whole build because of pointer write; just log

            log.info("ShardBuilder: built shard=%s vdir=%s nodes=%d events=%d", shard_id, dest_dir, len(revmap), event_count)
            return dest_dir

        except Exception:
            # cleanup on any failure
            if tmp_dir.exists():
                try:
                    shutil.rmtree(tmp_dir)
                except Exception:
                    pass
            raise
