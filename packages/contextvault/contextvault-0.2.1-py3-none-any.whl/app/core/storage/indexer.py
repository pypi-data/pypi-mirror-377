# File: app/core/storage/indexer.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Any
from app.core.storage.filelog import iter_events

INDEX_DIR = Path("data/index")
INDEX_DIR.mkdir(parents=True, exist_ok=True)

def reindex_all() -> Dict[str, str]:
    """Build derived indexes from logs."""
    paths = {}

    # 1) contexts_by_object.json
    by_obj: Dict[str, List[Dict[str, Any]]] = {}
    for ev in iter_events("contexts") or []:
        oid = ev.get("object_id")
        if not oid:
            continue
        by_obj.setdefault(oid, []).append({"context_id": ev.get("context_id"), "ts": ev.get("ts")})
    p1 = INDEX_DIR / "contexts_by_object.json"
    p1.write_text(json.dumps(by_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["contexts_by_object"] = str(p1)

    # 2) lineage_children.json
    children: Dict[str, List[str]] = {}
    for ev in iter_events("lineage") or []:
        child = ev.get("context_id")
        for parent in ev.get("parents", []) or []:
            children.setdefault(parent, [])
            if child and child not in children[parent]:
                children[parent].append(child)
    p2 = INDEX_DIR / "lineage_children.json"
    p2.write_text(json.dumps(children, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["lineage_children"] = str(p2)

    return paths
