# app/core/storage/partitioned_filelog.py
from __future__ import annotations
import json
import os
from pathlib import Path
from hashlib import blake2b
from datetime import datetime, timezone
from typing import Iterable, Optional, Dict, Any
import typing

# Note: We compute the partitions root dynamically (inside _partitions_root)
# so tests that monkeypatch filelog.LOG_DIR (tmp_path) will be respected.

DEFAULT_PARTITIONS_SUBPATH = Path("data") / "log" / "partitions"


def _partitions_root() -> Path:
    """
    Determine the partitions root directory.

    Priority:
      1. env var PARTITIONS_ROOT if set
      2. if app.core.storage.filelog exposes LOG_DIR, use LOG_DIR / "partitions"
      3. fallback to default data/log/partitions
    """
    env = os.environ.get("PARTITIONS_ROOT")
    if env:
        return Path(env)
    # avoid importing at module import time to reduce circular-import risk;
    # import lazily and fetch LOG_DIR if available
    try:
        from app.core.storage import filelog  # type: ignore
        if hasattr(filelog, "LOG_DIR"):
            return Path(getattr(filelog, "LOG_DIR")) / "partitions"
    except Exception:
        # ignore import errors/circular import; use default
        pass
    return DEFAULT_PARTITIONS_SUBPATH


def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def _shard_for_key(key: str, shard_count: int = 16) -> str:
    """
    Deterministic shard name for a given key (e.g., tenant_id or context_id).
    Uses blake2b to get stable digest and maps to 0..shard_count-1.
    """
    h = blake2b(key.encode("utf-8"), digest_size=8).digest()
    idx = int.from_bytes(h, "big") % shard_count
    return f"shard_{idx:02d}"


def append_event_partition(key: str, stream: str, event: Dict[str, Any], shard_count: int = 16) -> Path:
    """
    Append an event JSON line to the partitioned stream file.
    key: used to pick shard (tenant id, context id, etc.)
    stream: logical stream name, e.g., 'relationships'
    event: dict to serialize (will get ts if not present)
    Returns the path written to.
    """
    root = _partitions_root()
    shard = _shard_for_key(key, shard_count=shard_count)
    shard_dir = root / shard
    _ensure_dir(shard_dir)
    fname = f"{stream}.jsonl"
    path = shard_dir / fname

    ev = dict(event)
    if "ts" not in ev:
        ev["ts"] = datetime.now(timezone.utc).isoformat()
    line = json.dumps(ev, ensure_ascii=False)
    # append atomically via text append
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return path


def iter_partition_events(stream: str, partitions_root: Optional[Path] = None) -> Iterable[Dict[str, Any]]:
    """
    Iterate JSON lines across all shard files for the given stream, in shard order.
    Note: ordering across shards is not global. Consumers should be aware.
    """
    root = partitions_root or _partitions_root()
    if not root.exists():
        return
    # iterate shards sorted for determinism
    for shard_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        p = shard_dir / f"{stream}.jsonl"
        if not p.exists():
            continue
        with p.open("r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    yield json.loads(ln)
                except Exception:
                    continue


def list_shards(partitions_root: Optional[Path] = None) -> Iterable[str]:
    root = partitions_root or _partitions_root()
    if not root.exists():
        return []
    return sorted([p.name for p in root.iterdir() if p.is_dir()])
