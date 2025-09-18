# app/api/p1_lmdb.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path

from app.core.graph_lmdb_full import write_lmdb_from_shard

router = APIRouter(prefix="/lmdb", tags=["lmdb"])

class BuildSpec(BaseModel):
    shard: str
    vdir: Optional[str] = None  # optional: v{ts} directory name; if omitted, build from latest shard vdir
    index_root: Optional[str] = None  # optional override, default uses app data/index

@router.post("/build", summary="Build LMDB snapshot for a shard vdir (or latest if omitted)")
def api_build_lmdb(spec: BuildSpec = Body(...)):
    try:
        index_root = Path(spec.index_root) if spec.index_root else Path("data") / "index"
        shard_root = index_root / "shards" / spec.shard
        if not shard_root.exists():
            raise HTTPException(status_code=404, detail=f"shard directory not found: {shard_root}")

        # choose vdir
        if spec.vdir:
            vdir = shard_root / spec.vdir
            if not vdir.exists():
                raise HTTPException(status_code=404, detail=f"vdir not found: {vdir}")
        else:
            # pick latest v*
            candidates = sorted([p for p in shard_root.iterdir() if p.is_dir() and p.name.startswith("v")], reverse=True)
            if not candidates:
                raise HTTPException(status_code=404, detail=f"no vdirs under shard {spec.shard}")
            vdir = candidates[0]

        # write LMDB to index_root/lmdb/<shard>/v{ts}
        lmdb_out_root = index_root / "lmdb" / spec.shard
        dest = write_lmdb_from_shard(vdir, lmdb_out_root)
        if not dest:
            raise HTTPException(status_code=500, detail="lmdb write failed")
        return {"ok": True, "lmdb_vdir": str(dest)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{shard}", summary="List LMDB vdirs for a shard (if any)")
def api_lmdb_status(shard: str, index_root: Optional[str] = None):
    index_root = Path(index_root) if index_root else Path("data") / "index"
    lmdb_root = index_root / "lmdb" / shard
    if not lmdb_root.exists():
        return {"ok": True, "lmdb_vdirs": []}
    vdirs = sorted([p.name for p in lmdb_root.iterdir() if p.is_dir() and p.name.startswith("v")], reverse=True)
    return {"ok": True, "lmdb_vdirs": vdirs}
