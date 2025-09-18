# app/core/coordinator.py
"""
Minimal Coordinator for partitioned ingestion.

API:
  - Coordinator(index_root: Path)
  - submit_job(job: dict) -> None  (durable append to jobs.jsonl)
  - run_once() -> List[Dict[str, Any]]  (pick up jobs, try to run them, write processed.jsonl)

Behavior:
- Durable append to jobs.jsonl (best-effort).
- run_once reads jobs.jsonl, de-duplicates already processed jobs by job_id recorded in processed.jsonl,
  and attempts to process unprocessed jobs. Processing is delegated to IndexWorker if available,
  otherwise does an inline best-effort processing for file sources (shard + inverted).
- run_once appends a processed record for each job to processed.jsonl.
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
import threading
import logging

log = logging.getLogger("coordinator")


class Coordinator:
    def __init__(self, index_root: Path):
        self.index_root = Path(index_root)
        self.jobs_dir = self.index_root / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self.jobs_file = self.jobs_dir / "jobs.jsonl"
        self.processed_file = self.jobs_dir / "processed.jsonl"
        self._lock = threading.RLock()

    def submit_job(self, job: Dict[str, Any]) -> None:
        """
        Durable append a job record to jobs.jsonl. Adds a ts if missing.
        """
        with self._lock:
            job_copy = dict(job)
            job_copy.setdefault("ts", time.strftime("%Y%m%d%H%M%S"))
            try:
                with self.jobs_file.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(job_copy, ensure_ascii=False) + "\n")
                    fh.flush()
                log.info("Coordinator: submitted job %s", job_copy.get("job_id"))
            except Exception:
                log.exception("failed to append job to %s", self.jobs_file)

    def _read_jobs(self) -> List[Dict[str, Any]]:
        """
        Read jobs.jsonl and return list of job dicts (preserve order).
        """
        if not self.jobs_file.exists():
            return []
        try:
            with self.jobs_file.open("r", encoding="utf-8") as fh:
                out = []
                for ln in fh:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        out.append(json.loads(ln))
                    except Exception:
                        log.debug("malformed job line skipped")
                return out
        except Exception:
            log.exception("failed reading jobs file")
            return []

    def _read_processed_job_ids(self) -> set:
        """
        Return a set of job_id values already recorded in processed.jsonl.
        """
        seen = set()
        if not self.processed_file.exists():
            return seen
        try:
            with self.processed_file.open("r", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if not ln:
                        continue
                    try:
                        rec = json.loads(ln)
                        jid = rec.get("job_id")
                        if jid:
                            seen.add(jid)
                    except Exception:
                        continue
        except Exception:
            log.exception("failed reading processed file")
        return seen

    def _append_processed(self, rec: Dict[str, Any]) -> None:
        """
        Append a processed record to processed.jsonl (durable append).
        """
        try:
            with self.processed_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                fh.flush()
        except Exception:
            log.exception("failed writing processed record")

    def run_once(self) -> List[Dict[str, Any]]:
        """
        Process pending jobs once.

        Returns a list of result dicts (one per job attempted).
        Each result contains keys: job_id, status, success (bool), ts_processed, and optional details.
        """
        results: List[Dict[str, Any]] = []
        with self._lock:
            jobs = self._read_jobs()
            processed_ids = self._read_processed_job_ids()

            for job in jobs:
                job_id = job.get("job_id") or f"job-{job.get('shard')}-{job.get('ts')}"
                if job_id in processed_ids:
                    # already processed previously; skip but record a lightweight result
                    results.append({"job_id": job_id, "status": "skipped_already_processed", "success": True, "ts_processed": time.strftime("%Y%m%d%H%M%S")})
                    continue

                # attempt to process the job
                rec: Dict[str, Any] = {"job_id": job_id, "status": None, "success": False, "ts_processed": time.strftime("%Y%m%d%H%M%S")}
                try:
                    # Prefer IndexWorker if available
                    try:
                        from app.core.index_worker import IndexWorker
                        w = IndexWorker(index_root=self.index_root)
                        # submit and run synchronously
                        w.submit_job(job)
                        w.run_once()
                        # inspect last_job_success
                        ok = bool(w.last_job_success)
                        rec["success"] = ok
                        rec["status"] = "submitted_to_indexworker" if ok else "indexworker_failed"
                        if w.last_job_id:
                            rec["worker_job_id"] = w.last_job_id
                        if w.last_job_success is not None:
                            rec["worker_success"] = bool(w.last_job_success)
                        # if IndexWorker appended built_vdir, include it
                        # IndexWorker writes to processed.jsonl internally but we still append here for coordinator provenance
                        results.append(rec)
                        # durable append
                        self._append_processed(rec)
                        continue
                    except Exception:
                        log.debug("IndexWorker not available or failed to run; falling back to inline processing")

                    # Inline fallback for simple file source jobs
                    src = job.get("source", {}) or {}
                    if src.get("type") == "file" and src.get("path"):
                        path = Path(src.get("path"))
                        if not path.exists():
                            rec["status"] = "source_file_missing"
                            rec["error"] = f"missing {path}"
                            rec["success"] = False
                            results.append(rec)
                            self._append_processed(rec)
                            continue
                        # best-effort inline processing: use ShardBuilder and inverted writer
                        try:
                            from app.core.adjcache_shard import ShardBuilder
                            from app.core.inverted_index import build_inverted_from_events, write_inverted_to_disk
                            text = path.read_text(encoding="utf-8")
                            events = [json.loads(ln) for ln in text.splitlines() if ln.strip()]
                            shards_root = self.index_root / "shards"
                            sb = ShardBuilder(shards_root)
                            vdir = sb.build_from_events(job.get("shard") or job.get("shard_id") or "default", (e for e in events))
                            inv = build_inverted_from_events((e for e in events))
                            inv_vdir = write_inverted_to_disk(inv, self.index_root / "inverted", job.get("shard") or job.get("shard_id") or "default", ts=job.get("ts"))
                            rec["status"] = "done_inline"
                            rec["success"] = True
                            if vdir:
                                rec["shard_vdir"] = str(vdir)
                            if inv_vdir:
                                rec["inverted_vdir"] = str(inv_vdir)
                        except Exception as e:
                            rec["status"] = "inline_processing_failed"
                            rec["error"] = str(e)
                            rec["traceback"] = traceback.format_exc()
                            rec["success"] = False
                        results.append(rec)
                        self._append_processed(rec)
                        continue

                    # if job type unknown
                    rec["status"] = "unknown_job_type"
                    rec["success"] = False
                    results.append(rec)
                    self._append_processed(rec)

                except Exception as e:
                    rec["status"] = "exception"
                    rec["error"] = str(e)
                    rec["traceback"] = traceback.format_exc()
                    rec["success"] = False
                    results.append(rec)
                    self._append_processed(rec)
            return results
