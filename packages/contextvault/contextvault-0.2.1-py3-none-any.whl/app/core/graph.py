# app/core/graph.py
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional, Set, Tuple
from datetime import datetime, timezone

from app.core.storage.filelog import append_event
# new: partitioned append
from app.core.storage.partitioned_filelog import append_event_partition

LOG_DIR = Path("data") / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REL_PATH = LOG_DIR / "relationships.jsonl"


def _iter_relationship_events(path: Path = REL_PATH) -> Iterable[Dict[str, Any]]:
    """Yield parsed JSON lines from relationships log (skip malformed)."""
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                yield json.loads(ln)
            except Exception:
                continue


def add_relationship(child_id: str, parent_id: str, rel_type: str = "parent", ts: Optional[str] = None) -> None:
    """
    Append a relationship edge to the relationships log.
    child_id <- parent_id (parent is upstream)
    rel_type: free-form label (default 'parent')
    """
    ev = {
        "event": "relationship_added",
        "child_id": child_id,
        "parent_id": parent_id,
        "rel_type": rel_type,
        "ts": ts or datetime.now(timezone.utc).isoformat(),
        # keep rel_id field for compatibility
        "rel_id": None,
    }
    # Use generic append so id assignment + legacy index logic run. append_event will also
    # write to partition files if partitioning is enabled.
    try:
        append_event("relationships", ev)
    except Exception:
        # fallback to partitioned append only if needed
        try:
            from app.core.storage.partitioned_filelog import append_event_partition
            append_event_partition(key=child_id, stream="relationships", event=ev)
        except Exception:
            # as last resort, re-raise so callers know
            raise


def _build_adjacency() -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Returns (parents_map, children_map).
    parents_map[child] = [parent_id,...]
    children_map[parent] = [child_id,...]
    """
    parents: Dict[str, List[str]] = {}
    children: Dict[str, List[str]] = {}

    for ev in _iter_relationship_events():
        if ev.get("event") != "relationship_added":
            continue
        child = ev.get("child_id")
        parent = ev.get("parent_id")
        if not child or not parent:
            continue
        parents.setdefault(child, []).append(parent)
        children.setdefault(parent, []).append(child)

    return parents, children


def get_parents(context_id: str) -> List[str]:
    parents, _ = _build_adjacency()
    return parents.get(context_id, [])


def get_children(context_id: str) -> List[str]:
    _, children = _build_adjacency()
    return children.get(context_id, [])


def trace(context_id: str, direction: str = "up", max_depth: int = 5) -> Dict[str, List[List[str]]]:
    """
    Breadth-first trace in 'up' (parents) or 'down' (children) direction.
    Returns {"levels": [[ids at depth=1], [ids at depth=2], ...]} (depth-ordered).
    Does not deduplicate across levels (but avoids cycles using visited set).
    """
    if direction not in ("up", "down"):
        raise ValueError("direction must be 'up' or 'down'")

    parents_map, children_map = _build_adjacency()
    get_neighbors = (lambda nid: parents_map.get(nid, [])) if direction == "up" else (lambda nid: children_map.get(nid, []))

    visited: Set[str] = set([context_id])
    current_level: List[str] = [context_id]
    levels: List[List[str]] = []

    for depth in range(max_depth):
        next_level: List[str] = []
        for node in current_level:
            for nb in get_neighbors(node):
                if nb in visited:
                    continue
                visited.add(nb)
                next_level.append(nb)
        if not next_level:
            break
        levels.append(next_level.copy())
        current_level = next_level

    return {"levels": levels}
