# app/core/audit_log.py
"""
AuditLog with rotation & lazy getter (backward-compatible).

Compatibility:
- Legacy constructor params supported:
    AuditLog(path, rotate_size=bytes, max_rotations=N)
  where rotate_size is in bytes and max_rotations is number of rotated files to keep.
- Newer env-driven config also supported:
    INDEX_AUDIT_PATH
    AUDIT_MAX_SIZE_MB
    AUDIT_RETENTION_FILES
    AUDIT_RETENTION_DAYS

Rotation behavior:
- If max_rotations (legacy) is provided and > 0, perform numeric rotation:
    audit.log -> audit.log.1 ; audit.log.1 -> audit.log.2 ; keep up to max_rotations
- Otherwise, use timestamped rotation: audit.YYYYMMDDTHHMMSSZ.log

append() pre-checks size-based rotation and rotates before writing.
tail(n) returns last n parsed JSON entries (skips malformed lines).
get_audit() returns a lazy singleton (recreated when env config changes).
"""

from __future__ import annotations
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

# defaults from env
_DEFAULT_PATH = Path(os.environ.get("INDEX_AUDIT_PATH", "data/audit/audit.log"))
_DEFAULT_MAX_SIZE_MB = int(os.environ.get("AUDIT_MAX_SIZE_MB", "10"))
_DEFAULT_RETENTION_FILES = int(os.environ.get("AUDIT_RETENTION_FILES", "5"))
_DEFAULT_RETENTION_DAYS = int(os.environ.get("AUDIT_RETENTION_DAYS", "30"))

_lock = threading.RLock()

class AuditLog:
    def __init__(
        self,
        path: str | Path = None,
        # legacy params (bytes, count)
        rotate_size: Optional[int] = None,
        max_rotations: Optional[int] = None,
        # new params (MB, count, days)
        max_size_mb: Optional[int] = None,
        retention_files: Optional[int] = None,
        retention_days: Optional[int] = None,
    ):
        """
        Supports legacy (rotate_size, max_rotations) and new (max_size_mb, retention_files, retention_days).
        Legacy args take precedence when provided.
        """
        self.path = Path(path or os.environ.get("INDEX_AUDIT_PATH", str(_DEFAULT_PATH)))
        # legacy: rotate_size in bytes
        self.rotate_size = int(rotate_size) if rotate_size is not None else None
        self.max_rotations = int(max_rotations) if max_rotations is not None else None

        # new style
        if max_size_mb is not None:
            self.max_size_mb = int(max_size_mb)
        else:
            self.max_size_mb = int(os.environ.get("AUDIT_MAX_SIZE_MB", str(_DEFAULT_MAX_SIZE_MB)))

        if retention_files is not None:
            self.retention_files = int(retention_files)
        else:
            self.retention_files = int(os.environ.get("AUDIT_RETENTION_FILES", str(_DEFAULT_RETENTION_FILES)))

        if retention_days is not None:
            self.retention_days = int(retention_days)
        else:
            self.retention_days = int(os.environ.get("AUDIT_RETENTION_DAYS", str(_DEFAULT_RETENTION_DAYS)))

        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _current_filename(self) -> Path:
        return self.path

    def _current_size(self) -> int:
        p = self._current_filename()
        try:
            return p.stat().st_size if p.exists() else 0
        except Exception:
            return 0

    def _should_rotate(self) -> bool:
        """
        Decide if rotation should occur based on legacy rotate_size (bytes) or new max_size_mb.
        """
        size = self._current_size()
        # legacy rotate_size (bytes) has precedence
        if self.rotate_size is not None:
            try:
                return size >= int(self.rotate_size)
            except Exception:
                return False
        # fallback to MB-based check
        try:
            return size >= (int(self.max_size_mb) * 1024 * 1024)
        except Exception:
            return False

    def rotate_now(self) -> Optional[Path]:
        """
        Rotate current audit file.
        If legacy numeric rotation is configured (max_rotations > 0), use numeric scheme:
            audit.log -> audit.log.1 ; audit.log.1 -> audit.log.2 ; maintain up to max_rotations
        Otherwise use timestamped rotation: audit.YYYYMMDDTHHMMSSZ.log
        Returns rotated Path or None.
        """
        with _lock:
            p = self._current_filename()
            if not p.exists():
                return None

            # If legacy rotation configured, perform numeric rotation
            if self.max_rotations and self.max_rotations > 0:
                try:
                    # remove oldest beyond max_rotations
                    oldest = p.with_suffix(p.suffix + f".{self.max_rotations}")
                    if oldest.exists():
                        try:
                            oldest.unlink(missing_ok=True)
                        except Exception:
                            pass
                    # shift existing: from max-1 down to 1
                    for i in range(self.max_rotations - 1, 0, -1):
                        src = p.with_suffix(p.suffix + f".{i}")
                        dst = p.with_suffix(p.suffix + f".{i+1}")
                        if src.exists():
                            try:
                                os.replace(str(src), str(dst))
                            except Exception:
                                try:
                                    os.rename(str(src), str(dst))
                                except Exception:
                                    pass
                    # finally move current to .1
                    dst1 = p.with_suffix(p.suffix + ".1")
                    try:
                        os.replace(str(p), str(dst1))
                    except Exception:
                        try:
                            os.rename(str(p), str(dst1))
                        except Exception:
                            # fallback: copy then truncate
                            try:
                                from shutil import copyfile
                                copyfile(str(p), str(dst1))
                                p.unlink(missing_ok=True)
                            except Exception:
                                return None
                    # enforce age-based cleanup for rotated files (optional)
                    self._enforce_retention_numeric()
                    return dst1
                except Exception:
                    # if numeric rotation fails, fall back to timestamp rotation below
                    pass

            # Timestamped rotation (fallback/new style)
            try:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                rotated = p.with_name(p.stem + f".{ts}" + p.suffix)
                os.replace(str(p), str(rotated))
            except Exception:
                try:
                    from shutil import copyfile
                    rotated = p.with_name(p.stem + f".{ts}" + p.suffix)
                    copyfile(str(p), str(rotated))
                    p.unlink(missing_ok=True)
                except Exception:
                    return None

            # Enforce new-style retention
            self._enforce_retention()
            return rotated

    def _enforce_retention_numeric(self):
        """
        Enforce numeric-rotation retention (age-based deletion, if retention_days set).
        Keeps the numeric rotated files up to max_rotations; also remove older than retention_days.
        """
        p = self._current_filename()
        # remove age-based
        if self.retention_days and self.retention_days > 0:
            cutoff = time.time() - (self.retention_days * 86400)
            for i in range(1, (self.max_rotations or 0) + 1):
                f = p.with_suffix(p.suffix + f".{i}")
                try:
                    if f.exists() and f.stat().st_mtime < cutoff:
                        f.unlink(missing_ok=True)
                except Exception:
                    pass

    def _enforce_retention(self):
        """
        Enforce new-style retention for timestamped rotated files.
        Keep up to self.retention_files timestamped rotated files and age-based deletion.
        """
        p = self._current_filename()
        rot_glob = list(p.parent.glob(p.stem + ".*" + p.suffix))
        # sort by mtime descending
        rot_sorted = sorted(rot_glob, key=lambda x: x.stat().st_mtime, reverse=True)
        # delete older than retention_files
        for old in rot_sorted[self.retention_files :]:
            try:
                old.unlink(missing_ok=True)
            except Exception:
                pass
        # age-based removal
        if self.retention_days > 0:
            cutoff = time.time() - (self.retention_days * 86400)
            for f in list(p.parent.glob(p.stem + ".*" + p.suffix)):
                try:
                    if f.stat().st_mtime < cutoff:
                        f.unlink(missing_ok=True)
                except Exception:
                    pass

    def append(self, event: Dict, flush: bool = True) -> None:
        """
        Append a JSON-line audit entry. Performs pre-append rotation if needed.
        """
        entry = {"ts": datetime.utcnow().isoformat() + "Z", "ts_epoch": time.time(), "event": event}
        line = json.dumps(entry, separators=(",", ":"), ensure_ascii=False) + "\n"
        with _lock:
            try:
                if self._should_rotate():
                    self.rotate_now()
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(line)
                    if flush:
                        f.flush()
                        try:
                            os.fsync(f.fileno())
                        except Exception:
                            pass
            except Exception:
                # best-effort fallback: atomic temp+replace
                try:
                    tmp = self.path.with_suffix(".tmp")
                    with open(tmp, "w", encoding="utf-8") as f:
                        f.write(line)
                        if flush:
                            f.flush()
                            try:
                                os.fsync(f.fileno())
                            except Exception:
                                pass
                    os.replace(str(tmp), str(self.path))
                except Exception:
                    # swallow; audit must not break app
                    pass

    def tail(self, n: int = 100) -> List[Dict]:
        p = self._current_filename()
        if not p.exists():
            return []
        out = []
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                lines = f.read().splitlines()
            for line in lines[-n:]:
                if not line.strip():
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    # skip malformed
                    continue
        except Exception:
            return []
        return out

    def list_rotated_files(self) -> List[str]:
        p = self._current_filename()
        # include numeric and timestamped rotated variants
        files = []
        # numeric
        if self.max_rotations and self.max_rotations > 0:
            for i in range(1, self.max_rotations + 1):
                f = p.with_suffix(p.suffix + f".{i}")
                if f.exists():
                    files.append(str(f))
        # timestamped
        for f in sorted(p.parent.glob(p.stem + ".*" + p.suffix), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.exists() and f not in [Path(x) for x in files]:
                files.append(str(f))
        return files

# Lazy singleton getter
_AUDIT_SINGLETON: Optional[AuditLog] = None
_AUDIT_SINGLETON_CONFIG: Dict = {}

def get_audit() -> AuditLog:
    """
    Return singleton AuditLog. Recreate if env config changed.
    """
    global _AUDIT_SINGLETON, _AUDIT_SINGLETON_CONFIG
    path = os.environ.get("INDEX_AUDIT_PATH", str(_DEFAULT_PATH))
    max_size_mb = int(os.environ.get("AUDIT_MAX_SIZE_MB", str(_DEFAULT_MAX_SIZE_MB)))
    retention_files = int(os.environ.get("AUDIT_RETENTION_FILES", str(_DEFAULT_RETENTION_FILES)))
    retention_days = int(os.environ.get("AUDIT_RETENTION_DAYS", str(_DEFAULT_RETENTION_DAYS)))
    cfg = {"path": path, "max_size_mb": max_size_mb, "retention_files": retention_files, "retention_days": retention_days}

    # if singleton exists and no legacy override, reuse
    if _AUDIT_SINGLETON is None:
        _AUDIT_SINGLETON = AuditLog(path, max_size_mb=max_size_mb, retention_files=retention_files, retention_days=retention_days)
        _AUDIT_SINGLETON_CONFIG = cfg
        return _AUDIT_SINGLETON

    # if env-driven config changed, recreate
    if _AUDIT_SINGLETON_CONFIG != cfg:
        _AUDIT_SINGLETON = AuditLog(path, max_size_mb=max_size_mb, retention_files=retention_files, retention_days=retention_days)
        _AUDIT_SINGLETON_CONFIG = cfg
    return _AUDIT_SINGLETON
