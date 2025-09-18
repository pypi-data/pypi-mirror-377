# app/api/p1_dag.py
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException

from pydantic import BaseModel

from app.core.graph import add_relationship, get_parents, get_children, trace

# Use a clear prefix so routes don't collide with other handlers.
router = APIRouter(prefix="/dag", tags=["dag"])

class RelAddRequest(BaseModel):
    child: str
    parent: str
    rel_type: Optional[str] = "parent"


class MultiRelAddRequest(BaseModel):
    child: str
    parents: List[str]
    rel_type: Optional[str] = "parent"


@router.post("/relationships")
def api_add_relationship(body: MultiRelAddRequest = Body(...)):
    """
    Add one or more parent edges for a child context.
    Appends relationship_added events to `data/log/relationships.jsonl`.
    """
    if not body.child or not body.parents:
        raise HTTPException(status_code=400, detail="child and parents are required")

    for p in body.parents:
        add_relationship(child_id=body.child, parent_id=p, rel_type=body.rel_type or "parent")
    return {"child": body.child, "parents": body.parents}


@router.get("/relationships/{context_id}")
def api_get_relationships(context_id: str, direction: Optional[str] = "parents"):
    """
    Return parents or children for a context.
    direction: 'parents' (default) or 'children'
    """
    if direction == "parents":
        parents = get_parents(context_id)
        return {"context_id": context_id, "parents": parents}
    elif direction == "children":
        children = get_children(context_id)
        return {"context_id": context_id, "children": children}
    else:
        raise HTTPException(status_code=400, detail="direction must be 'parents' or 'children'")


@router.get("/lineage/trace/{context_id}")
def api_trace(context_id: str, direction: Optional[str] = "up", max_depth: Optional[int] = 5):
    """
    Trace lineage starting from context_id.
    direction: 'up' (parents) or 'down' (children)
    """
    if direction not in ("up", "down"):
        raise HTTPException(status_code=400, detail="direction must be 'up' or 'down'")
    if max_depth is None or max_depth < 1:
        max_depth = 1
    levels = trace(context_id=context_id, direction=direction, max_depth=max_depth)
    return levels
