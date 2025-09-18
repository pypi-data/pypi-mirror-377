# app/api/p2_admin.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, HTTPException, Body

from app.core.graph import _iter_relationship_events, _build_adjacency, REL_PATH

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/export/{context_id}")
def api_export_subgraph(context_id: str, direction: Optional[str] = "up", max_depth: Optional[int] = 5, include_dot: Optional[bool] = False):
    """
    Export a subgraph (trace) starting from context_id.
    direction: 'up' or 'down'
    max_depth: integer depth
    include_dot: if true, include a Graphviz DOT string (useful for visualization)
    Response:
      {
        "context_id": "...",
        "direction": "up",
        "max_depth": 3,
        "trace": {"levels": [...]},   # same shape as graph.trace
        "nodes": {"id": {"parents":[...],"children":[...]} ...},  # adjacency subgraph
        "dot": "digraph { ... }"  # only if include_dot
      }
    """
    if direction not in ("up", "down"):
        raise HTTPException(status_code=400, detail="direction must be 'up' or 'down'")

    max_depth = max_depth or 1
    # use existing trace to get nodes (levels)
    from app.core.graph import trace, get_parents, get_children

    trace_res = trace(context_id=context_id, direction=direction, max_depth=max_depth)
    # flatten nodes
    nodes_seen: Set[str] = set([context_id])
    for lvl in trace_res.get("levels", []):
        for nid in lvl:
            nodes_seen.add(nid)

    # build adjacency for every node in nodes_seen
    parents_map, children_map = _build_adjacency()
    sub_nodes: Dict[str, Dict[str, List[str]]] = {}
    for n in nodes_seen:
        sub_nodes[n] = {
            "parents": parents_map.get(n, []),
            "children": children_map.get(n, []),
        }

    resp = {
        "context_id": context_id,
        "direction": direction,
        "max_depth": max_depth,
        "trace": trace_res,
        "nodes": sub_nodes,
    }

    if include_dot:
        # construct basic DOT (directed). Use parents->child edges for clarity.
        dot_lines = ["digraph ctx_subgraph {"]
        # include the focal node as bold
        dot_lines.append(f'  "{context_id}" [style=filled, fillcolor=lightgrey];')
        for child, parents in parents_map.items():
            if child not in nodes_seen:
                continue
            for p in parents:
                if p not in nodes_seen:
                    continue
                dot_lines.append(f'  "{p}" -> "{child}";')
        dot_lines.append("}")
        resp["dot"] = "\n".join(dot_lines)

    return resp


@router.get("/stats")
def api_stats():
    """
    Provide simple statistics about relationships log:
      - total_events
      - total_unique_edges
      - total_nodes
      - log_path
    """
    total_events = 0
    edges: Set[Tuple[str, str, str]] = set()
    nodes: Set[str] = set()
    for ev in _iter_relationship_events():
        total_events += 1
        if ev.get("event") != "relationship_added":
            continue
        c = ev.get("child_id")
        p = ev.get("parent_id")
        t = ev.get("rel_type", "parent")
        if c and p:
            edges.add((c, p, t))
            nodes.add(c)
            nodes.add(p)

    return {
        "total_events": total_events,
        "total_unique_edges": len(edges),
        "total_nodes": len(nodes),
        "log_path": str(REL_PATH),
    }


class CompactPreviewRequest(BaseModel := __import__("pydantic").BaseModel):  # keep explicit runtime import to avoid circular
    """
    Request body for compaction preview:
      { "output_path": "data/log/relationships_compacted.jsonl", "dry_run": true }
    """
    output_path: Optional[str] = "data/log/relationships_compacted.jsonl"
    dry_run: Optional[bool] = True


@router.post("/compact/preview")
def api_compact_preview(body: CompactPreviewRequest = Body(...)):
    """
    Analyze the relationships log and produce a compaction preview.
    Does NOT modify existing logs unless you run the scripts/compact_relationships.py utility.
    Returns:
      { "original_events": N, "unique_edges": M, "output_path": "...", "sample_lines": [...] }
    """
    # Build unique edges preserving first-seen order
    seen_edges: Set[Tuple[str, str, str]] = set()
    unique_events: List[Dict] = []
    total_events = 0
    for ev in _iter_relationship_events():
        total_events += 1
        if ev.get("event") != "relationship_added":
            continue
        key = (ev.get("child_id"), ev.get("parent_id"), ev.get("rel_type", "parent"))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        unique_events.append(ev)

    sample_lines = []
    for ev in unique_events[:50]:
        sample_lines.append(ev)

    return {
        "original_events": total_events,
        "unique_edges": len(unique_events),
        "output_path": body.output_path,
        "dry_run": body.dry_run,
        "sample_lines": sample_lines,
    }
