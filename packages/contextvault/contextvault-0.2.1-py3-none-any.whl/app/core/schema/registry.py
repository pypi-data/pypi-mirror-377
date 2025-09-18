# File: app/core/schema/registry.py
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, Any, Optional

SCHEMA_DIR = Path("data/schemas")
SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_PATH = SCHEMA_DIR / "registry.json"

def _load_registry() -> Dict[str, str]:
    if not REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save_registry(reg: Dict[str, str]) -> None:
    REGISTRY_PATH.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")

def _safe_name(ref: str) -> str:
    # safe filename from ref (letters, digits, dot, dash)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", ref)

def put_schema(schema_ref: str, schema: Dict[str, Any]) -> str:
    fname = f"{_safe_name(schema_ref)}.json"
    path = SCHEMA_DIR / fname
    path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
    reg = _load_registry()
    reg[schema_ref] = fname
    _save_registry(reg)
    return str(path)

def get_schema(schema_ref: str) -> Optional[Dict[str, Any]]:
    reg = _load_registry()
    fname = reg.get(schema_ref)
    if not fname:
        return None
    path = SCHEMA_DIR / fname
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def list_schemas() -> Dict[str, str]:
    return _load_registry()
