# app/api/health.py
"""
Public Health API for ContextVault with deep index consistency check.

Endpoints:
- GET /health       : service + index stats + deep consistency
- GET /health/ping  : liveness
"""

import time
import os
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from pathlib import Path

router = APIRouter(prefix="/health", tags=["health"])

# defaults
SQLITE_PATH_DEFAULT = os.environ.get("INDEX_SQLITE_PATH", "data/index/index.sqlite")
JSON_INDEX_PATH = Path(os.environ.get("FILES_INDEX_PATH", "data/index/genai_index.json"))

class IndexConsistency(BaseModel):
    json_doc_count: Optional[int]
    sqlite_doc_count: Optional[int]
    mismatch: bool
    json_only_ids: List[str] = []
    sqlite_only_ids: List[str] = []
    ok: bool

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    time: float
    index: Dict[str, Any]
    index_consistency: IndexConsistency

_START_TS = time.time()

# helper: read JSON doc ids
def _read_json_doc_ids(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return list(data.keys())
            # fallback for other shapes
            return []
    except Exception:
        return []

# helper: read sqlite doc ids (docs table)
def _read_sqlite_doc_ids(sqlite_path: str) -> List[str]:
    try:
        import sqlite3
        p = Path(sqlite_path)
        if not p.exists():
            return []
        conn = sqlite3.connect(str(p))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT doc_id FROM docs")
        rows = cur.fetchall()
        doc_ids = [r["doc_id"] for r in rows if "doc_id" in r.keys()]
        conn.close()
        return doc_ids
    except Exception:
        return []

# wrapper to get index stats via indexer if possible
def _get_index_stats() -> Dict[str, Any]:
    try:
        from app.core.indexer import list_index_stats
        return list_index_stats() or {}
    except Exception:
        # fallback: attempt to read sqlite counts directly if file present
        sqlite_path = os.environ.get("INDEX_SQLITE_PATH", SQLITE_PATH_DEFAULT)
        ids = _read_sqlite_doc_ids(sqlite_path)
        return {"doc_count": len(ids)}

@router.get("", response_model=HealthResponse)
def health():
    stats = _get_index_stats()
    # deep consistency check
    json_path = Path(os.environ.get("FILES_INDEX_PATH", str(JSON_INDEX_PATH)))
    json_ids = _read_json_doc_ids(json_path)
    sqlite_ids = []
    sqlite_path = os.environ.get("INDEX_SQLITE_PATH", SQLITE_PATH_DEFAULT)
    # only check sqlite if backend seems enabled/present
    if sqlite_path and Path(sqlite_path).exists():
        sqlite_ids = _read_sqlite_doc_ids(sqlite_path)

    json_count = len(json_ids) if json_ids is not None else None
    sqlite_count = len(sqlite_ids) if sqlite_ids is not None else None
    mismatch = (json_count is not None and sqlite_count is not None and json_count != sqlite_count)
    # compute set differences (limit output sizes to avoid huge payloads)
    json_set = set(json_ids)
    sqlite_set = set(sqlite_ids)
    json_only = sorted(list(json_set - sqlite_set))[:200]
    sqlite_only = sorted(list(sqlite_set - json_set))[:200]
    ok = (not mismatch) and (len(json_only) == 0 and len(sqlite_only) == 0)

    consistency = {
        "json_doc_count": json_count,
        "sqlite_doc_count": sqlite_count,
        "mismatch": mismatch,
        "json_only_ids": json_only,
        "sqlite_only_ids": sqlite_only,
        "ok": ok,
    }

    return {
        "status": "ok" if not stats.get("error") else "degraded",
        "uptime_seconds": time.time() - _START_TS,
        "time": time.time(),
        "index": stats,
        "index_consistency": consistency,
    }

@router.get("/ping")
def ping():
    return {"ping": "pong", "time": time.time()}
