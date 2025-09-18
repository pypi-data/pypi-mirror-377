# File: app/core/policy/loader.py
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Dict
import yaml  # pip install pyyaml

POLICY_PATH = Path("policies/contextvault.yml")

class Policy:
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw or {}

    def for_object_type(self, object_type: str) -> Dict[str, Any]:
        res = {}
        defaults = self.raw.get("defaults", {}) or {}
        subtype = (self.raw.get("by_object_type", {}) or {}).get(object_type or "", {}) or {}
        # shallow merge (good enough for P2)
        res.update(defaults)
        for k, v in subtype.items():
            if isinstance(v, dict):
                merged = dict(defaults.get(k, {}))
                merged.update(v)
                res[k] = merged
            else:
                res[k] = v
        return res

def load_policy() -> Policy:
    if not POLICY_PATH.exists():
        # create a default file on first run
        POLICY_PATH.parent.mkdir(parents=True, exist_ok=True)
        POLICY_PATH.write_text(json.dumps({
            "version": 1,
            "defaults": {"size_bounds":{"max_zip_bytes": 104857600},"trust":{"base":0.5,"flag_penalty":0.1,"quarantine_trust":0.2,"accept_floor":0.3,"accept_ceiling":0.95},"hash_check":{"allowed":[]},"schema_validate":{"enabled":False}},
            "by_object_type": {}
        }, indent=2), encoding="utf-8")
        return Policy({"version":1,"defaults":{"size_bounds":{"max_zip_bytes":104857600},"trust":{"base":0.5,"flag_penalty":0.1,"quarantine_trust":0.2,"accept_floor":0.3,"accept_ceiling":0.95},"hash_check":{"allowed":[]},"schema_validate":{"enabled":False}},"by_object_type":{}})
    with POLICY_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return Policy(data)
