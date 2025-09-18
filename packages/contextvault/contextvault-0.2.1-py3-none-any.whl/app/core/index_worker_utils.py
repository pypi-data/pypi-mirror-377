# app/core/index_worker_utils.py
"""
IndexWorker utilities (atomic pointer writes)

Small, dependency-light helpers used by IndexWorker to atomically write
the shard 'current' pointer file. Designed to be minimally invasive so
existing logic and filenames are preserved.
"""

from __future__ import annotations
import os
import tempfile
from pathlib import Path
import logging
from typing import Any
import json

log = logging.getLogger("indexworker.utils")


def _atomic_write_text(target_path: Path, text: str) -> None:
    """
    Atomically write `text` to `target_path` using a same-directory temp file,
    fsync the file and (best-effort) the containing directory, then rename.
    """
    dirpath = target_path.parent
    dirpath.mkdir(parents=True, exist_ok=True)

    fd = None
    tmp_path = None
    try:
        # mkstemp in same dir to allow atomic replace on same filesystem
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=str(dirpath))
        # write text
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                # best-effort
                log.debug("fsync unavailable on file descriptor for %s", tmp_path)
        fd = None  # fd handled by fdopen context
        # fsync the directory (best-effort)
        try:
            dirfd = os.open(str(dirpath), os.O_DIRECTORY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except Exception:
            log.debug("directory fsync not available for %s", dirpath)
        # atomic replace
        os.replace(tmp_path, str(target_path))
    finally:
        # cleanup temp if something went wrong and tmp_path remains
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def atomic_write_json(target_path: Path, data: Any) -> None:
    """
    Convenience wrapper to write JSON atomically.
    """
    _atomic_write_text(target_path, json.dumps(data, ensure_ascii=False, indent=2))


def write_current_pointer(shard_parent_dir: Path, version_name: str) -> None:
    """
    Write the 'current' pointer file under `shard_parent_dir` with the contents
    `version_name` (string). Uses atomic write to avoid partial writes.
    Preserves the original filename 'current' used in other parts of the repo.
    """
    target = shard_parent_dir / "current"
    try:
        _atomic_write_text(target, version_name)
        log.info("Wrote atomic current pointer: %s -> %s", target, version_name)
    except Exception:
        # As a last-resort fallback (should be rare), attempt to write directly
        try:
            target.write_text(version_name, encoding="utf-8")
            log.warning("Fallback wrote current pointer directly: %s", target)
        except Exception:
            log.exception("Failed to write current pointer to %s", target)
            raise
