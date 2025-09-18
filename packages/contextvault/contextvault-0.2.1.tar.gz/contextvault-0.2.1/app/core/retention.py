# app/core/retention.py
"""
Retention utilities for ContextVault.

Provides:
- cleanup_expired(now_ts=None)
- delete_versions_older_than(days)
- policy registry: register_policy(name, fn), unregister_policy(name), run_policies(*args, **kwargs)

Implementation notes:
- Dynamically reads FILES_INDEX and delete_context from app.core.indexer at runtime,
  so tests can monkeypatch those symbols.
- Emits audit events if app.core.audit_log.AuditLog is available.
- All audit logging is best-effort (errors swallowed so main flow isn't blocked).
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Callable
import time
import os
import json
from pathlib import Path
import importlib

# Simple in-process policy registry
_POLICY_REGISTRY: Dict[str, Callable[..., Any]] = {}

_AUDIT_ENV = os.environ.get("INDEX_AUDIT_PATH", "data/audit/audit.log")

# -------------------------
# Dynamic imports / helpers
# -------------------------
def _get_indexer_symbols():
    """
    Dynamically import app.core.indexer and app.core.audit_log at runtime.
    Returns tuple: (FILES_INDEX_path: Path or None, delete_context_callable_or_None, AuditLog_or_None)
    """
    files_index = None
    delete_fn = None
    AuditLog = None
    try:
        idx = importlib.import_module("app.core.indexer")
        files_index = getattr(idx, "FILES_INDEX", None)
        delete_fn = getattr(idx, "delete_context", None)
    except Exception:
        files_index = None
        delete_fn = None

    try:
        audit_mod = importlib.import_module("app.core.audit_log")
        AuditLog = getattr(audit_mod, "AuditLog", None)
    except Exception:
        AuditLog = None

    return files_index, delete_fn, AuditLog

def _make_auditor(AuditLog):
    if not AuditLog:
        return None
    try:
        return AuditLog(os.environ.get("INDEX_AUDIT_PATH", _AUDIT_ENV))
    except Exception:
        try:
            return AuditLog(_AUDIT_ENV)
        except Exception:
            return None

def _parse_iso_or_epoch(val) -> Optional[float]:
    if val is None:
        return None
    try:
        if isinstance(val, (int, float)):
            return float(val)
        s = str(val)
        # try ISO
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except Exception:
            # fallback numeric string
            return float(s)
    except Exception:
        return None

# -------------------------
# Core: cleanup_expired
# -------------------------
def cleanup_expired(now_ts: Optional[float] = None) -> Dict[str, Any]:
    """
    Scan the configured FILES_INDEX and delete contexts whose metadata.expires_at <= now.
    Returns summary: {"scanned": N, "deleted": M, "deleted_ids": [...], "errors": [...] }
    """
    if now_ts is None:
        now_ts = time.time()

    files_index_attr, delete_fn, AuditLog = _get_indexer_symbols()
    if files_index_attr is not None:
        try:
            files_index_path = Path(files_index_attr)
        except Exception:
            files_index_path = Path(str(files_index_attr))
    else:
        files_index_path = Path("data/index/genai_index.json")

    delete_context = delete_fn  # may be None
    _aud = _make_auditor(AuditLog)

    summary = {"scanned": 0, "deleted": 0, "deleted_ids": [], "errors": []}
    if not files_index_path.exists():
        return summary

    try:
        with files_index_path.open("r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        return {"scanned": 0, "deleted": 0, "deleted_ids": [], "errors": [f"load_error:{e}"]}

    for cid, rec in list(index_data.items()):
        summary["scanned"] += 1
        expires_raw = rec.get("expires_at")
        expires_ts = _parse_iso_or_epoch(expires_raw)
        if expires_ts is None:
            continue
        if expires_ts <= now_ts:
            try:
                if delete_context:
                    ok = delete_context(cid)
                    if ok:
                        summary["deleted"] += 1
                        summary["deleted_ids"].append(cid)
                    else:
                        summary["errors"].append(f"delete_failed:{cid}")
                else:
                    # fallback: remove from JSON directly
                    index_data.pop(cid, None)
                    try:
                        with files_index_path.open("w", encoding="utf-8") as f:
                            json.dump(index_data, f, indent=2, ensure_ascii=False)
                        summary["deleted"] += 1
                        summary["deleted_ids"].append(cid)
                    except Exception as e:
                        summary["errors"].append(f"write_failed:{cid}:{e}")

                try:
                    if _aud:
                        _aud.append({
                            "actor": "system",
                            "action": "retention_delete",
                            "context_id": cid,
                            "expires_at": expires_raw,
                            "ts": time.time()
                        })
                except Exception:
                    pass
            except Exception as e:
                summary["errors"].append(f"exception:{cid}:{e}")

    return summary

# -------------------------
# Helper: delete_versions_older_than
# -------------------------
def delete_versions_older_than(days: int) -> Dict[str, Any]:
    """
    Delete contexts whose metadata.timestamp is older than 'days'.
    Expects metadata['timestamp'] to be ISO8601 or epoch.
    Returns summary similar to cleanup_expired().
    """
    try:
        days_i = int(days)
    except Exception:
        return {"error": "invalid_days"}

    cutoff_ts = time.time() - (days_i * 86400)
    files_index_attr, delete_fn, AuditLog = _get_indexer_symbols()
    if files_index_attr is not None:
        try:
            files_index_path = Path(files_index_attr)
        except Exception:
            files_index_path = Path(str(files_index_attr))
    else:
        files_index_path = Path("data/index/genai_index.json")

    delete_context = delete_fn
    _aud = _make_auditor(AuditLog)

    summary = {"scanned": 0, "deleted": 0, "deleted_ids": [], "errors": []}
    if not files_index_path.exists():
        return summary

    try:
        with files_index_path.open("r", encoding="utf-8") as f:
            index_data = json.load(f)
    except Exception as e:
        return {"scanned": 0, "deleted": 0, "deleted_ids": [], "errors": [f"load_error:{e}"]}

    for cid, rec in list(index_data.items()):
        summary["scanned"] += 1
        ts_raw = rec.get("timestamp") or rec.get("created_at")
        ts = _parse_iso_or_epoch(ts_raw)
        if ts is None:
            continue
        if ts <= cutoff_ts:
            try:
                if delete_context:
                    ok = delete_context(cid)
                    if ok:
                        summary["deleted"] += 1
                        summary["deleted_ids"].append(cid)
                    else:
                        summary["errors"].append(f"delete_failed:{cid}")
                else:
                    index_data.pop(cid, None)
                    try:
                        with files_index_path.open("w", encoding="utf-8") as f:
                            json.dump(index_data, f, indent=2, ensure_ascii=False)
                        summary["deleted"] += 1
                        summary["deleted_ids"].append(cid)
                    except Exception as e:
                        summary["errors"].append(f"write_failed:{cid}:{e}")
                try:
                    if _aud:
                        _aud.append({
                            "actor": "system",
                            "action": "delete_versions_older_than",
                            "context_id": cid,
                            "timestamp": ts_raw,
                            "cutoff_ts": cutoff_ts,
                            "ts": time.time()
                        })
                except Exception:
                    pass
            except Exception as e:
                summary["errors"].append(f"exception:{cid}:{e}")

    return summary

# -------------------------
# Policy registry functions
# -------------------------
def register_policy(name: str, fn: Any) -> bool:
    """
    Register a named policy.

    Accepts:
    - a callable, or
    - any object (which will be wrapped into a callable that returns the object).

    Returns True if registered, False if name already exists.
    """
    if name in _POLICY_REGISTRY:
        return False

    # If fn is callable, register as-is. If not, coerce into a callable wrapper.
    if callable(fn):
        _POLICY_REGISTRY[name] = fn  # type: ignore
    else:
        # Wrap non-callable value into a callable that returns it when invoked.
        def _wrapper(*args, _value=fn, **kwargs):
            return _value
        _POLICY_REGISTRY[name] = _wrapper  # type: ignore
    return True

def unregister_policy(name: str) -> bool:
    """
    Unregister a named policy. Returns True if removed, False if not found.
    """
    if name in _POLICY_REGISTRY:
        _POLICY_REGISTRY.pop(name, None)
        return True
    return False

def run_policies(*args, **kwargs) -> Dict[str, Any]:
    """
    Run all registered policies sequentially. Accepts any args/kwargs and forwards them to each policy.
    Returns aggregate results:
    { "policies": {name: result}, "summary": {...} }
    """
    results = {}
    summary = {"policies_run": 0, "deleted_total": 0, "errors": []}
    for name, fn in list(_POLICY_REGISTRY.items()):
        try:
            res = fn(*args, **kwargs)
            results[name] = res
            summary["policies_run"] += 1
            # try to aggregate deleted counts if present
            if isinstance(res, dict) and "deleted" in res and isinstance(res["deleted"], int):
                summary["deleted_total"] += res["deleted"]
        except Exception as e:
            results[name] = {"error": str(e)}
            summary["errors"].append(f"{name}:{e}")
    return {"policies": results, "summary": summary}
