# app/core/replication.py
"""
Simple replication baseline.

Responsibilities:
- Replicate shard v{ts} directories to a replica root (local filesystem).
- Provide idempotent functions:
    - sync_shard(index_root, shard_id, replica_root, vname=None) -> Path|None
        Copies the specified vdir (or current pointer if vname None) to replica_root/<shard_id>/<vname>/
    - replicate_all(index_root, replica_root) -> List[Path]  # replicate all shards' current vdirs
    - run_replication_once(index_root, replica_root) -> dict (summary)
- Write replication metadata at <replica_root>/replication_manifest.json listing timestamps.
- Safe (does not delete source) and best-effort (logs errors).
"""

from __future__ import annotations
import shutil
import os
import json
from pathlib import Path
from typing import Optional, List, Dict
import logging

log = logging.getLogger("replication")


def _shard_current_vdir(index_root: Path, shard_id: str) -> Optional[Path]:
    shards_root = Path(index_root) / "shards" / shard_id
    curf = shards_root / "current"
    if not curf.exists():
        return None
    try:
        vname = curf.read_text(encoding="utf-8").strip()
        vdir = shards_root / vname
        if vdir.exists() and vdir.is_dir():
            return vdir
    except Exception:
        log.exception("failed reading current pointer for %s", shard_id)
    return None


def sync_shard(index_root: Path, shard_id: str, replica_root: Path, vname: Optional[str] = None) -> Optional[Path]:
    """
    Copy a single shard vdir to the replica root. If vname None, use current pointer.
    Returns path to replica vdir on success, else None.
    """
    try:
        idx = Path(index_root)
        replica_root = Path(replica_root)
        shard_parent = idx / "shards" / shard_id
        if vname:
            src = shard_parent / str(vname)
        else:
            src = _shard_current_vdir(index_root, shard_id)
        if not src or not src.exists():
            log.debug("no source vdir for shard %s", shard_id)
            return None
        dest = replica_root / "shards" / shard_id / src.name
        if dest.exists():
            # already replicated; idempotent
            log.debug("replica already present %s", dest)
            return dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        # copytree could raise; use shutil.copytree
        shutil.copytree(src, dest)
        _write_replication_manifest(replica_root, shard_id, src.name)
        log.info("replicated shard %s -> %s", src, dest)
        return dest
    except Exception:
        log.exception("sync_shard failed for %s", shard_id)
        return None


def replicate_all(index_root: Path, replica_root: Path) -> List[Path]:
    """
    Replicate the current vdir of every shard under index_root to replica_root.
    Returns list of successfully replicated paths.
    """
    out: List[Path] = []
    shards_dir = Path(index_root) / "shards"
    if not shards_dir.exists():
        return out
    for shard in shards_dir.iterdir():
        if not shard.is_dir():
            continue
        shard_id = shard.name
        try:
            rp = sync_shard(index_root, shard_id, replica_root)
            if rp:
                out.append(rp)
        except Exception:
            log.exception("replicate_all: failed for shard %s", shard_id)
    return out


def _write_replication_manifest(replica_root: Path, shard_id: str, vname: str) -> None:
    manifest = Path(replica_root) / "replication_manifest.json"
    obj: Dict[str, Dict[str, str]] = {}
    if manifest.exists():
        try:
            obj = json.loads(manifest.read_text(encoding="utf-8"))
        except Exception:
            obj = {}
    obj.setdefault(shard_id, {})
    obj[shard_id]["last_vdir"] = vname
    obj[shard_id]["last_replicated"] = __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())
    tmp = manifest.with_name(".tmp_" + manifest.name)
    tmp.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    os.replace(str(tmp), str(manifest))


def run_replication_once(index_root: Path, replica_root: Path) -> Dict[str, List[str]]:
    """
    Run replication for all shards and return a summary:
      {"replicated": [<paths>], "failed": [<shard_ids>]}
    """
    succeeded: List[str] = []
    failed: List[str] = []
    for p in replicate_all(Path(index_root), Path(replica_root)):
        try:
            succeeded.append(str(p))
        except Exception:
            pass
    # compute failed shards by comparing list of shards
    shards_dir = Path(index_root) / "shards"
    if shards_dir.exists():
        for shard in shards_dir.iterdir():
            if not shard.is_dir():
                continue
            # if shard not present in succeeded list, consider it failed
            found = any(str(shard.name) in s for s in succeeded)
            if not found:
                failed.append(shard.name)
    return {"replicated": succeeded, "failed": failed}
