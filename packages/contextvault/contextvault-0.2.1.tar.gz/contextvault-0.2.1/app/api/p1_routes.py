# File: app/api/p1_routes.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

LOG_DIR = Path("data/log")
CONTEXTS_LOG = LOG_DIR / "contexts.jsonl"
LINEAGE_LOG = LOG_DIR / "lineage.jsonl"


# ------------------------------
# Helpers to read JSONL
# ------------------------------
def _scan_jsonl(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


# ------------------------------
# Single context
# ------------------------------
@router.get("/contexts/{context_id}")
def get_context(context_id: str) -> Dict[str, Any]:
    for ev in _scan_jsonl(CONTEXTS_LOG) or []:
        if ev.get("event") == "context_created" and ev.get("context_id") == context_id:
            return {
                "context_id": ev.get("context_id"),
                "object_id": ev.get("object_id"),
                "meta": ev.get("meta", {}),
                "artifacts": ev.get("artifacts", {}),
            }
    raise HTTPException(status_code=404, detail="Context not found")


# ------------------------------
# List contexts for an object (timeline list)
# ------------------------------
@router.get("/objects/{object_id}/contexts")
def list_object_contexts(
    object_id: str,
    limit: int = Query(50, ge=1, le=500),
    cursor: Optional[str] = Query(None),
) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for ev in _scan_jsonl(CONTEXTS_LOG) or []:
        if ev.get("event") == "context_created" and ev.get("object_id") == object_id:
            items.append(
                {
                    "context_id": ev.get("context_id"),
                    "meta": ev.get("meta", {}),
                    "artifacts": ev.get("artifacts", {}),
                }
            )

    # sort by created_at (ISO string)
    def _ts(it):
        return it.get("meta", {}).get("created_at") or ""

    items.sort(key=_ts)  # ascending

    if cursor:
        try:
            idx = next(i for i, it in enumerate(items) if it["context_id"] == cursor)
            items = items[idx + 1 :]
        except StopIteration:
            items = []

    return {"items": items[:limit]}


# ------------------------------
# Alias for timeline (explicit implementation)
# ------------------------------
@router.get("/objects/{object_id}/timeline")
def timeline(
    object_id: str,
    limit: int = Query(50, ge=1, le=500),
) -> Dict[str, Any]:
    # Explicitly read the same log to ensure parity with /contexts
    items: List[Dict[str, Any]] = []
    for ev in _scan_jsonl(CONTEXTS_LOG) or []:
        if ev.get("event") == "context_created" and ev.get("object_id") == object_id:
            items.append(
                {
                    "context_id": ev.get("context_id"),
                    "meta": ev.get("meta", {}),
                    "artifacts": ev.get("artifacts", {}),
                }
            )

    def _ts(it):
        return it.get("meta", {}).get("created_at") or ""

    items.sort(key=_ts)
    return {"items": items[:limit]}


# ------------------------------
# Lineage: parents / children
# ------------------------------
@router.get("/contexts/{context_id}/parents")
def get_context_parents(context_id: str) -> Dict[str, Any]:
    parents: List[str] = []
    for ev in _scan_jsonl(LINEAGE_LOG) or []:
        if ev.get("event") == "lineage_added" and ev.get("context_id") == context_id:
            pid = ev.get("parent_id")
            if pid:
                parents.append(pid)
    return {"context_id": context_id, "parents": parents}


@router.get("/contexts/{context_id}/children")
def get_context_children(context_id: str) -> Dict[str, Any]:
    children: List[str] = []
    for ev in _scan_jsonl(LINEAGE_LOG) or []:
        if ev.get("event") == "lineage_added" and ev.get("parent_id") == context_id:
            cid = ev.get("context_id")
            if cid:
                children.append(cid)
    return {"context_id": context_id, "children": children}


# ------------------------------
# Lineage trace with levels
# ------------------------------
def _load_lineage_maps():
    parents_of: dict[str, Set[str]] = {}
    children_of: dict[str, Set[str]] = {}
    for ev in _scan_jsonl(LINEAGE_LOG) or []:
        if ev.get("event") != "lineage_added":
            continue
        child = ev.get("context_id")
        parent = ev.get("parent_id")
        if not child or not parent:
            continue
        parents_of.setdefault(child, set()).add(parent)
        children_of.setdefault(parent, set()).add(child)
    return parents_of, children_of


def _bfs_levels(start_id: str, next_fn, max_depth: int) -> list[list[str]]:
    seen = {start_id}
    frontier = [start_id]
    levels: list[list[str]] = []
    for _ in range(max_depth):
        nxt: list[str] = []
        for node in frontier:
            for neigh in next_fn(node):
                if neigh not in seen:
                    seen.add(neigh)
                    nxt.append(neigh)
        if not nxt:
            break
        levels.append(nxt)
        frontier = nxt
    return levels


@router.get("/lineage/trace/{context_id}")
def trace_lineage(
    context_id: str,
    direction: str = Query("both", pattern="^(up|down|both)$"),
    max_depth: int = Query(3, ge=1, le=10),
):
    parents_of, children_of = _load_lineage_maps()

    def parents_fn(n: str):
        return parents_of.get(n, set())

    def children_fn(n: str):
        return children_of.get(n, set())

    if direction == "up":
        levels = _bfs_levels(context_id, parents_fn, max_depth)
        return {"context_id": context_id, "direction": "up", "levels": levels}

    if direction == "down":
        levels = _bfs_levels(context_id, children_fn, max_depth)
        return {"context_id": context_id, "direction": "down", "levels": levels}

    up_levels = _bfs_levels(context_id, parents_fn, max_depth)
    down_levels = _bfs_levels(context_id, children_fn, max_depth)
    return {
        "context_id": context_id,
        "direction": "both",
        "up_levels": up_levels,
        "down_levels": down_levels,
    }


# ------------------------------
# Cursor endpoint (optional)
# ------------------------------
@router.get("/objects/{object_id}/contexts/cursor")
def list_object_contexts_cursor(
    object_id: str,
    cursor: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    return list_object_contexts(object_id, limit=limit, cursor=cursor)


# ------------------------------
# State at time t (ISO8601) — now includes 'count'
# ------------------------------
@router.get("/state_at/{object_id}")
def state_at(
    object_id: str,
    t: str = Query(..., description="ISO8601 timestamp; returns last context at or before t"),
) -> Dict[str, Any]:
    cutoff = _parse_iso(t)
    if cutoff is None:
        raise HTTPException(status_code=400, detail="Invalid timestamp format for 't'")

    candidates: List[Dict[str, Any]] = []
    for ev in _scan_jsonl(CONTEXTS_LOG) or []:
        if ev.get("event") != "context_created" or ev.get("object_id") != object_id:
            continue
        meta = ev.get("meta", {}) or {}
        ts = meta.get("created_at")
        dt = _parse_iso(ts) if isinstance(ts, str) else None
        if dt and dt <= cutoff:
            candidates.append(
                {
                    "context_id": ev.get("context_id"),
                    "meta": meta,
                    "artifacts": ev.get("artifacts", {}),
                }
            )

    count = len(candidates)
    if count == 0:
        return {"object_id": object_id, "as_of": t, "count": 0, "latest": None, "items": []}

    # choose the latest by created_at
    candidates.sort(key=lambda it: it.get("meta", {}).get("created_at") or "")
    latest = candidates[-1]

    return {
        "object_id": object_id,
        "as_of": t,
        "count": count,
        "latest": latest,
        "items": candidates,
    }
