# app/api/p1_coordinator.py
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path

from app.core.index_coordinator import IndexCoordinator

router = APIRouter(prefix="/coord", tags=["coord"])

# singleton coordinator
_COORD = IndexCoordinator(index_root=Path("data") / "index", pool_size=4)

class StartSpec(BaseModel):
    pool_size: Optional[int] = None
    poll_seconds: Optional[float] = None

@router.post("/start", summary="Start the index coordinator background thread")
def coord_start(spec: StartSpec = Body(None)):
    try:
        if spec and spec.pool_size:
            _COORD.pool_size = int(spec.pool_size)
        if spec and spec.poll_seconds:
            _COORD.poll_seconds = float(spec.poll_seconds)
        _COORD.start()
        return {"ok": True, "running": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop", summary="Stop the index coordinator")
def coord_stop():
    try:
        _COORD.stop(wait=True)
        return {"ok": True, "running": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", summary="Coordinator status")
def coord_status():
    try:
        return {"ok": True, "status": _COORD.status()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
