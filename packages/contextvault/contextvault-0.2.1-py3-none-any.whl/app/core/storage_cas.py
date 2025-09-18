# app/core/storage_cas.py
"""
Minimal content-addressed storage helper for ContextVault.

- save_snapshot(bytes) -> sha256 hex string (writes to data/snapshots/<sha>.png)
- snapshot_path(sha) -> Path
- verify_snapshot(sha) -> bool (recompute SHA256 and compare)
"""

from pathlib import Path
import hashlib
import os

SNAPSHOT_DIR = Path(os.environ.get("SNAPSHOT_DIR", "data/snapshots"))
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def _sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def snapshot_path_for_hash(sha: str) -> Path:
    return SNAPSHOT_DIR / f"{sha}.png"

def save_snapshot(content_bytes: bytes) -> str:
    """
    Save bytes to CAS. If a file with the sha already exists, do not overwrite.
    Returns the sha hex string.
    """
    sha = _sha256_bytes(content_bytes)
    p = snapshot_path_for_hash(sha)
    if not p.exists():
        tmp = p.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            f.write(content_bytes)
            try:
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(str(tmp), str(p))
    return sha

def verify_snapshot(sha: str) -> bool:
    """
    Recompute SHA256 of snapshot file and compare to sha.
    Returns True if matches, False otherwise (or file missing).
    """
    p = snapshot_path_for_hash(sha)
    if not p.exists():
        return False
    try:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest() == sha
    except Exception:
        return False
