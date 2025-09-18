# app/api/p1_index_worker.py
from __future__ import annotations
from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from app.core.index_worker import IndexWorker

router = APIRouter(prefix="/index", tags=["index"])

# singleton worker instance for simple deployments
_worker = IndexWorker()

class JobSpec(BaseModel):
    job_id: Optional[str]
    shard: str
    source: dict
    build_inverted: Optional[bool] = False
    ts: Optional[str] = None
    max_retries: Optional[int] = None

@router.post("/jobs", summary="Submit an index job")
def submit_job(spec: JobSpec = Body(...)):
    job = spec.dict(exclude_none=True)
    if not job.get("shard") or not job.get("source"):
        raise HTTPException(status_code=400, detail="shard and source required")
    try:
        _worker.submit_job(job)
        return {"ok": True, "jobs_file": str(_worker.jobs_file), "job": job}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/status", summary="Get index worker status")
def jobs_status():
    try:
        status = _worker.worker_status()
        return {"ok": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/processed", summary="Tail processed job audit log")
def processed_tail(limit: Optional[int] = Query(20, ge=1, le=1000)):
    """
    Return the most recent 'limit' records from the worker processed log (processed.jsonl).
    """
    try:
        path = Path(_worker.jobs_dir) / "processed.jsonl"
        if not path.exists():
            return {"ok": True, "records": []}
        # read file and return last 'limit'
        with path.open("r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        tail = lines[-int(limit):] if lines else []
        records: List[Dict[str, Any]] = []
        for ln in tail:
            try:
                records.append(json.loads(ln))
            except Exception:
                records.append({"raw": ln})
        return {"ok": True, "records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/start", summary="Start background worker thread")
def jobs_start():
    try:
        _worker.start()
        return {"ok": True, "running": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/stop", summary="Stop background worker thread")
def jobs_stop():
    try:
        _worker.stop()
        return {"ok": True, "running": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
