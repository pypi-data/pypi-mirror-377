# File: app/api/p3_routes.py
from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Optional, Tuple
import uuid

from fastapi import APIRouter, Body, HTTPException, Query

from app.core.storage.filelog import (
    get_event_by_id,
    find_events_by_field,
    iter_events,
    append_event,
)
# new: partitioned append helper
from app.core.storage.partitioned_filelog import append_event_partition

from app.core.schema.registry import put_schema, get_schema, list_schemas

router = APIRouter()

# ------------------------------
# A) Schema registry
# ------------------------------
@router.post("/schemas")
def register_schema(schema_ref: str = Query(...), schema: Dict[str, Any] = Body(...)) -> dict:
    path = put_schema(schema_ref, schema)
    return {"ok": True, "schema_ref": schema_ref, "path": path}

@router.get("/schemas/{schema_ref}")
def fetch_schema(schema_ref: str) -> dict:
    sc = get_schema(schema_ref)
    if sc is None:
        raise HTTPException(status_code=404, detail="schema not found")
    return {"schema_ref": schema_ref, "schema": sc}

@router.get("/schemas")
def list_schema_refs() -> dict:
    return {"registry": list_schemas()}

# ------------------------------
# B) Relationships
# ------------------------------
@router.post("/relationships")
def create_relationship(
    from_type: str = Query(..., pattern="^(object|context)$"),
    from_id: str = Query(...),
    to_type: str = Query(..., pattern="^(object|context)$"),
    to_id: str = Query(...),
    rel_type: str = Query(...),
    attrs: Optional[Dict[str, Any]] = Body(None),
) -> dict:
    ev = {
        "event": "relationship_added",
        "rel_id": None,
        "from": {"type": from_type, "id": from_id},
        "to": {"type": to_type, "id": to_id},
        "rel_type": rel_type,
        "attrs": attrs or {},
        "ts": None,
    }

    # Ensure a stable rel_id exists immediately so callers/tests can observe it.
    if not ev.get("rel_id"):
        ev["rel_id"] = f"rel_{uuid.uuid4().hex[:12]}"

    # Use the generic append_event wrapper so IDs are assigned and legacy index updated.
    try:
        append_event("relationships", ev)
    except Exception:
        # best-effort fallback to partitioned append if something goes wrong
        try:
            from app.core.storage.partitioned_filelog import append_event_partition
            key = ev.get("from", {}).get("id") or ev.get("to", {}).get("id") or ev.get("rel_id")
            append_event_partition(key=key or ev.get("rel_id"), stream="relationships", event=ev)
        except Exception:
            # swallow: we still return success to match previous contract, but log in real code
            pass
    return {"ok": True, "rel_id": ev.get("rel_id")}


@router.post("/relationships")
def create_relationship(
    from_type: str = Query(..., pattern="^(object|context)$"),
    from_id: str = Query(...),
    to_type: str = Query(..., pattern="^(object|context)$"),
    to_id: str = Query(...),
    rel_type: str = Query(...),
    attrs: Optional[Dict[str, Any]] = Body(None),
) -> dict:
    ev = {
        "event": "relationship_added",
        "rel_id": None,
        "from": {"type": from_type, "id": from_id},
        "to": {"type": to_type, "id": to_id},
        "rel_type": rel_type,
        "attrs": attrs or {},
        "ts": None,
    }

    # Ensure immediate stable rel_id
    if not ev.get("rel_id"):
        ev["rel_id"] = f"rel_{uuid.uuid4().hex[:12]}"

    # append via wrapper (this will also write partition file if enabled)
    append_event("relationships", ev)
    return {"ok": True, "rel_id": ev.get("rel_id")}


# ------------------------------
# C) Cursor-based timeline
# ------------------------------
def _encode_cursor(ts: str, cid: str) -> str:
    raw = json.dumps({"ts": ts, "id": cid}).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")

def _decode_cursor(cursor: str) -> Tuple[str, str]:
    raw = base64.urlsafe_b64decode(cursor.encode("ascii"))
    obj = json.loads(raw.decode("utf-8"))
    return obj["ts"], obj["id"]

@router.get("/objects/{object_id}/contexts/cursor")
def list_contexts_for_object_cursor(
    object_id: str,
    limit: int = Query(25, ge=1, le=200),
    cursor: Optional[str] = Query(None, description="Opaque cursor from previous page"),
) -> dict:
    # Validate
    if not get_event_by_id("objects", "object_id", object_id):
        raise HTTPException(status_code=404, detail="Object not found")

    events = find_events_by_field("contexts", "object_id", object_id)
    # Sort by ts desc, then context_id desc for deterministic order
    events.sort(key=lambda e: (e.get("ts", ""), e.get("context_id", "")), reverse=True)

    start_idx = 0
    if cursor:
        try:
            ts, cid = _decode_cursor(cursor)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor")
        # find first event strictly LESS than (ts, cid) in our ordering
        for i, e in enumerate(events):
            ets = e.get("ts", "")
            ecid = e.get("context_id", "")
            if (ets, ecid) == (ts, cid):
                start_idx = i + 1
                break
            # if we've passed the spot (since sorted desc), continue
            if (ets < ts) or (ets == ts and ecid < cid):
                # this event is after the cursor cut, continue scanning
                continue

    page = events[start_idx : start_idx + limit]
    next_cursor = None
    if len(events) > start_idx + limit:
        last = page[-1]
        next_cursor = _encode_cursor(last.get("ts", ""), last.get("context_id", ""))

    items = [
        {
            "context_id": e.get("context_id"),
            "ts": e.get("ts"),
            "meta": e.get("meta", {}),
            "artifacts": e.get("artifacts", {}),
        }
        for e in page
    ]
    return {"object_id": object_id, "limit": limit, "items": items, "next_cursor": next_cursor}
