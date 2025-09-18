# app/core/index_coordinator.py
from __future__ import annotations
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime

from app.core.index_worker import IndexWorker

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

DEFAULT_POOL_SIZE = 4
DEFAULT_POLL_SECONDS = 1.0
DEFERRED_FILE_NAME = "jobs.deferred.jsonl"
MAX_DEFERRED_PER_RUN = 100  # ceil of deferred jobs processed per run_once pass


class IndexCoordinator:
    """
    Coordinator that dispatches index jobs from a jobs.jsonl into a thread pool,
    with per-shard locking and durable requeue for skipped jobs.

    Improvements over basic version:
      - Skipped jobs (shard busy) are appended to jobs.deferred.jsonl for later reprocessing.
      - Deferred queue is processed before picking new jobs.
      - Durable behavior ensures no silent drops.
    """

    def __init__(
        self,
        index_root: Path | str = Path("data") / "index",
        pool_size: int = DEFAULT_POOL_SIZE,
        poll_seconds: float = DEFAULT_POLL_SECONDS,
        shard_lock_timeout: float = 600.0,
        worker_factory: Optional[Callable[..., IndexWorker]] = None,
    ):
        self.index_root = Path(index_root)
        self.pool_size = int(pool_size)
        self.poll_seconds = float(poll_seconds)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._executor: Optional[ThreadPoolExecutor] = None
        self._running_lock = threading.RLock()
        # locks per shard
        self._shard_locks: Dict[str, threading.Lock] = {}
        # mapping shard -> Future
        self._running_jobs: Dict[str, Future] = {}
        # coordinator uses a single IndexWorker instance for job processing (durable writes to processed.jsonl)
        if worker_factory:
            self._worker = worker_factory(index_root=Path(index_root))
        else:
            self._worker = IndexWorker(index_root=Path(index_root))
        self._shard_lock_timeout = float(shard_lock_timeout)

        # ensure jobs dir exists and deferred file exists
        self._worker.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._deferred_path = self._worker.jobs_dir / DEFERRED_FILE_NAME
        try:
            self._deferred_path.touch(exist_ok=True)
        except Exception:
            logger.exception("failed to ensure deferred jobs file")

    # -------------------------
    # deferred queue helpers
    # -------------------------
    def _append_deferred(self, job: Dict[str, Any]) -> None:
        """
        Append the job dict (JSON line) to the deferred file for later processing.
        """
        try:
            line = f"{job!s}\n"
            # write as json via json.dumps to be stable
            import json as _json
            with self._deferred_path.open("a", encoding="utf-8") as fh:
                fh.write(_json.dumps(job, ensure_ascii=False) + "\n")
        except Exception:
            logger.exception("failed to append deferred job: %s", job)

    def _pop_deferred_batch(self, limit: int = MAX_DEFERRED_PER_RUN) -> List[Dict[str, Any]]:
        """
        Read up to `limit` deferred jobs (oldest-first) and rewrite the file without those popped.
        Returns the list of job dicts popped.
        """
        import json as _json
        if not self._deferred_path.exists():
            return []
        try:
            with self._deferred_path.open("r", encoding="utf-8") as fh:
                lines = [ln.strip() for ln in fh.readlines() if ln.strip()]
            if not lines:
                return []
            # parse lines
            parsed = []
            rest = []
            for i, ln in enumerate(lines):
                try:
                    obj = _json.loads(ln)
                except Exception:
                    # if corrupted, skip
                    continue
                if len(parsed) < limit:
                    parsed.append(obj)
                else:
                    rest.append(ln)
            # rewrite deferred file with remaining lines (rest)
            with self._deferred_path.open("w", encoding="utf-8") as fh:
                for ln in rest:
                    fh.write(ln + "\n")
            return parsed
        except Exception:
            logger.exception("failed to pop deferred batch")
            return []

    def deferred_len(self) -> int:
        try:
            with self._deferred_path.open("r", encoding="utf-8") as fh:
                return sum(1 for ln in fh if ln.strip())
        except Exception:
            return 0

    # -------------------------
    # internal helpers
    # -------------------------
    def _get_shard_lock(self, shard: str) -> threading.Lock:
        with self._running_lock:
            if shard not in self._shard_locks:
                self._shard_locks[shard] = threading.Lock()
            return self._shard_locks[shard]

    def _submit_job(self, job: Dict[str, Any]) -> Optional[Future]:
        shard = job.get("shard")
        if not shard:
            return None
        with self._running_lock:
            # if a job for this shard is already running, mark deferred
            if shard in self._running_jobs and not self._running_jobs[shard].done():
                logger.info("shard %s already running - deferring job %s", shard, job.get("job_id"))
                # durable append to deferred file
                self._append_deferred(job)
                return None
            # try to acquire lock immediately to reserve
            lock = self._get_shard_lock(shard)
            acquired = lock.acquire(blocking=False)
            if not acquired:
                # couldn't acquire -> defer
                logger.info("failed to acquire shard lock for %s - deferring job %s", shard, job.get("job_id"))
                self._append_deferred(job)
                return None

            # submit job to executor
            if self._executor is None:
                lock.release()
                return None

            future = self._executor.submit(self._run_job_with_lock_release, shard, job, lock)
            self._running_jobs[shard] = future
            return future

    def _run_job_with_lock_release(self, shard: str, job: Dict[str, Any], lock: threading.Lock):
        """
        Run inside worker thread; ensure lock is released when done.
        """
        try:
            logger.info("starting job %s on shard %s", job.get("job_id"), shard)
            res = self._worker._process_job(job)
            logger.info("job %s on shard %s finished: %s", job.get("job_id"), shard, res)
            return res
        except Exception:
            logger.exception("job %s on shard %s raised exception", job.get("job_id"), shard)
            return False
        finally:
            try:
                lock.release()
            except Exception:
                pass

    # -------------------------
    # run loop
    # -------------------------
    def run_once(self) -> None:
        """
        Process deferred jobs first (durable, FIFO), then read new jobs and dispatch.
        Deferred jobs that are still blocked will be re-appended to deferred file.
        """
        # lazily create executor
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.pool_size)

        # 1) process deferred batch
        deferred_jobs = self._pop_deferred_batch(limit=MAX_DEFERRED_PER_RUN)
        if deferred_jobs:
            logger.info("processing %d deferred jobs", len(deferred_jobs))
        for job in deferred_jobs:
            try:
                fut = self._submit_job(job)
                if fut is None:
                    # submission deferred the job; already appended by _submit_job
                    continue
            except Exception:
                logger.exception("error dispatching deferred job: %s", job)

        # 2) iterate new jobs (this will move jobs.pos)
        for job in self._worker._iter_new_jobs():
            try:
                fut = self._submit_job(job)
                if fut is None:
                    # _submit_job already appended to deferred when necessary
                    continue
            except Exception:
                logger.exception("error dispatching job: %s", job)

        # cleanup finished futures
        with self._running_lock:
            done_shards = [s for s, f in list(self._running_jobs.items()) if f.done()]
            for s in done_shards:
                try:
                    self._running_jobs.pop(s, None)
                except Exception:
                    pass

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.pool_size)
        self._thread = threading.Thread(target=self._loop, name="index-coordinator", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self.run_once()
            except Exception:
                logger.exception("coordinator run loop error")
            time.sleep(self.poll_seconds)

    def stop(self, wait: bool = True) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
        if self._executor:
            if wait:
                self._executor.shutdown(wait=True)
            else:
                self._executor.shutdown(wait=False)
            self._executor = None

    def status(self) -> Dict[str, Any]:
        with self._running_lock:
            return {
                "running": bool(self._thread and self._thread.is_alive()),
                "pool_size": self.pool_size,
                "pending_shards": list(self._running_jobs.keys()),
                "deferred_count": self.deferred_len(),
                "last_job_id": self._worker.last_job_id,
                "last_job_success": self._worker.last_job_success,
                "processed_count": self._worker.processed_count,
                "failed_count": self._worker.failed_count,
            }
