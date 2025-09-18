# app/api/p1_search.py
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List, Dict, Any
import logging

from app.core.inverted_index import read_postings_for_term, _normalize_term

log = logging.getLogger("p1_search")
# Mount router under /search so tests calling /search/keyword resolve correctly
router = APIRouter(prefix="/search")


@router.get("/keyword")
def keyword_search(q: str = Query(...), limit: int = 10, index_root: str = Query("data/index")):
    """
    Query keyword across inverted indexes located under <index_root>/inverted/<shard>/v*
    Returns JSON:
      { "ok": True, "term": "<normalized>", "postings": [...], "results": [...] }
    """
    try:
        term = _normalize_term(q)
        idx = Path(index_root)
        inverted_root = idx / "inverted"
        if not inverted_root.exists():
            return JSONResponse(status_code=200, content={"ok": True, "term": term, "postings": [], "results": []})

        postings_agg: List[str] = []
        results_enriched: List[Dict[str, Any]] = []

        # iterate shards under inverted_root
        shards = [d for d in inverted_root.iterdir() if d.is_dir()]
        shards.sort(key=lambda p: p.name)
        for shard_dir in shards:
            try:
                # read_postings_for_term accepts (shard_root, term)
                res = read_postings_for_term(shard_dir, term)
                docs = list(res)
                # append to postings_agg unique
                for d in docs:
                    if d not in postings_agg:
                        postings_agg.append(d)
                        # basic enrichment: include doc id and shard for results list
                        results_enriched.append({"id": d, "shard": shard_dir.name})
                    if len(postings_agg) >= limit:
                        break
                if len(postings_agg) >= limit:
                    break
            except Exception as e:
                log.exception("error reading postings for shard %s: %s", shard_dir, e)
                continue

        return JSONResponse(status_code=200, content={"ok": True, "term": term, "postings": postings_agg, "results": results_enriched})
    except Exception as e:
        log.exception("keyword search failed: %s", e)
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
