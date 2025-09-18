# app/api/p1_inverted.py
from __future__ import annotations
from fastapi import APIRouter, Query, HTTPException
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from app.core.inverted_index import read_postings_for_term, write_inverted_to_disk, build_inverted_from_events

router = APIRouter(prefix="/inverted", tags=["inverted"])

class BuildSpec(BaseModel):
    shard: str
    events_path: str
    ts: Optional[str] = None

@router.post("/build")
def api_build(spec: BuildSpec):
    # small wrapper for ad-hoc builds: reads events file and writes inverted index under data/index/inverted
    evpath = Path(spec.events_path)
    if not evpath.exists():
        raise HTTPException(status_code=404, detail="events file not found")
    def iter_events():
        with evpath.open("r", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                yield __import__("json").loads(ln)
    inv = build_inverted_from_events(iter_events())
    dest = write_inverted_to_disk(inv, Path("data") / "index" / "inverted", spec.shard, ts=spec.ts)
    return {"ok": True, "dest": str(dest)}

@router.get("/query/{shard}/{term}")
def api_query(shard: str, term: str = Query(...)):
    shard_root = Path("data") / "index" / "inverted" / shard
    if not shard_root.exists():
        raise HTTPException(status_code=404, detail="shard not found")
    postings = read_postings_for_term(shard_root, term)
    return {"shard": shard, "term": term, "postings": postings}
