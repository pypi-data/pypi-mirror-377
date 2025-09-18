# app/core/sharder.py
"""
Simple shard assignment utility.

Responsibilities:
- Deterministic round-robin shard assignment for keys (small baseline).
- Persist a simple mapping file at <index_root>/shards_map.json to keep assignments stable across restarts.
- Provide helper functions:
    - get_shard_for_key(index_root, key, num_shards) -> str
    - load_shard_map(index_root) -> dict
    - save_shard_map(index_root, map)
    - rebalance_shards(index_root, shard_ids) -> dict  # simple rebalance / idempotent

Notes:
- This is intentionally minimal and deterministic; it *does not* implement consistent hashing.
- Keep it pure-Python and safe for tests.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List
import hashlib
import logging

log = logging.getLogger("sharder")


def _map_file(index_root: Path) -> Path:
    p = Path(index_root) / "shards_map.json"
    return p


def load_shard_map(index_root: Path) -> Dict[str, str]:
    p = _map_file(index_root)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        log.exception("failed loading shard_map")
        return {}


def save_shard_map(index_root: Path, mapping: Dict[str, str]) -> None:
    p = _map_file(index_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(".tmp_" + p.name)
    tmp.write_text(json.dumps(mapping, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(p))


def _default_shard_list(num_shards: int) -> List[str]:
    return [f"shard-{i}" for i in range(num_shards)]


def get_shard_for_key(index_root: Path, key: str, num_shards: int = 4) -> str:
    """
    Deterministically assign `key` to one of num_shards shards.
    Uses sha1(key) % num_shards for stable mapping.
    """
    if not key:
        return "shard-0"
    # compute int from sha1
    h = hashlib.sha1(key.encode("utf-8")).hexdigest()
    v = int(h[:8], 16)
    idx = v % max(1, int(num_shards))
    shard = f"shard-{idx}"
    return shard


def rebalance_shards(index_root: Path, shard_ids: List[str]) -> Dict[str, str]:
    """
    Create/overwrite a simple mapping for keys -> shard_id for small known keys.
    This is a helper for small deployments where keys are known upfront.

    Returns the created mapping (empty mapping here as we cannot enumerate all keys).
    """
    # For baseline, we store the available shard ids as metadata so other components can see them.
    meta = {"shard_ids": shard_ids, "updated": __import__("time").time()}
    p = Path(index_root) / "shard_ids.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(".tmp_" + p.name)
    tmp.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(p))
    return meta
