from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Body

from app.core.adjcache import AdjCache
from app.core.adjcache_shard import ShardBuilder
from app.core.shard_registry import ShardRegistry
import json
from pathlib import Path

router = APIRouter(prefix="/adjcache", tags=["adjcache"])

# singleton instance (simple; swap for DI later)
_ADJ = AdjCache()
_SHARD_BUILDER = ShardBuilder(Path("data") / "index" / "adjcache")
_REG = ShardRegistry(Path("data") / "index" / "adjcache")

@router.post("/build")
def api_build(use_mmap: Optional[bool] = Query(False)):
    """Build in-memory adjacency from relationship streams and optionally persist mmap index."""
    use_mmap = bool(use_mmap)
    _ADJ.mmap_mode = bool(use_mmap)
    manifest = _ADJ.build_from_streams()
    if use_mmap:
        dest = _ADJ.dump_mmap_index()
        return {"manifest": manifest, "mmap_index": str(dest)}
    return {"manifest": manifest}

@router.post("/load")
def api_load():
    ok = _ADJ.load_mmap_index()
    if not ok:
        raise HTTPException(status_code=404, detail="no mmap index found")
    return {"ok": True, "stats": _ADJ.stats()}

@router.post("/shard/{shard_id}/build")
def api_build_shard(shard_id: str, input_file: Optional[str] = Query(None)):
    """
    Build a single shard from a JSONL input file (each line is a JSON event),
    or from the default partitioned streams if input_file is omitted.
    """
    # if input_file is provided, stream from it
    def iter_file(path: str):
        p = Path(path)
        if not p.exists():
            return
        for ln in p.read_text(encoding="utf-8").splitlines():
            try:
                yield json.loads(ln)
            except Exception:
                continue

    if input_file:
        src_iter = iter_file(input_file)
    else:
        # fallback to default streams (partitioned). We build shard from the global event iterator.
        src_iter = _ADJ._iter_relationship_events()

    dest = _SHARD_BUILDER.build_from_events(shard_id, src_iter)
    return {"ok": True, "shard": shard_id, "index_path": str(dest)}

@router.get("/shards")
def api_list_shards():
    shards_root = Path("data") / "index" / "adjcache" / "shards"
    if not shards_root.exists():
        return {"shards": []}
    out = []
    for s in sorted([p.name for p in shards_root.iterdir() if p.is_dir()]):
        cur = shards_root / s / "current"
        cur_name = cur.read_text(encoding="utf-8").strip() if cur.exists() else None
        vdir = shards_root / s / cur_name if cur_name else None
        node_count = None
        if vdir and vdir.exists():
            mf = vdir / "manifest.json"
            if mf.exists():
                try:
                    node_count = json.loads(mf.read_text()).get("node_count")
                except Exception:
                    node_count = None
        out.append({"shard_id": s, "current": cur_name, "node_count": node_count})
    return {"shards": out}

@router.post("/registry/refresh")
def api_registry_refresh():
    data = _REG.refresh_from_disk()
    return {"ok": True, "registry": data}

@router.get("/registry")
def api_registry_get():
    return {"registry": _REG.list_shards()}
