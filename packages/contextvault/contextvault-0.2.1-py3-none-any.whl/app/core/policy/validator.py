# File: app/core/policy/validator.py
from __future__ import annotations
from typing import Any, Dict, List, Tuple, Optional

from app.core.policy.loader import load_policy

try:
    import jsonschema  # type: ignore
except Exception:
    jsonschema = None  # graceful degrade


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _compute_trust(status: str, flags: List[str], rules: Dict[str, Any]) -> float:
    trust_cfg = rules.get("trust") or {}
    base = float(trust_cfg.get("base", 0.5))
    penalty = float(trust_cfg.get("flag_penalty", 0.1))
    q_trust = float(trust_cfg.get("quarantine_trust", 0.2))
    floor = float(trust_cfg.get("accept_floor", 0.3))
    ceil = float(trust_cfg.get("accept_ceiling", 0.95))

    if status == "reject":
        return 0.0
    if status == "quarantine":
        return q_trust
    t = base - penalty * len(flags)
    return _clamp(t, floor, ceil)


def _merge_rules(defaults: Dict[str, Any], sub: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(defaults or {})
    for k, v in (sub or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            nv = dict(out[k])
            nv.update(v)
            out[k] = nv
        else:
            out[k] = v
    return out


def _rules_for_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
    policy = load_policy()
    defaults = policy.raw.get("defaults", {}) or {}
    object_type = (meta.get("extra") or {}).get("object_type") or "default"
    subtype = (policy.raw.get("by_object_type", {}) or {}).get(object_type, {}) or {}
    return _merge_rules(defaults, subtype)


def evaluate_ingest(
    meta: Dict[str, Any]
) -> Tuple[str, List[str], float, Dict[str, Any]]:
    """Back-compat entrypoint: no payload/schema. Size/hash checks only."""
    return evaluate_ingest_extended(meta, payload=None, schema=None, schema_ref=None)


def evaluate_ingest_extended(
    meta: Dict[str, Any],
    *,
    payload: Optional[Any],
    schema: Optional[Dict[str, Any]],
    schema_ref: Optional[str],
) -> Tuple[str, List[str], float, Dict[str, Any]]:
    """
    Extended evaluation:
      - size_bounds
      - hash_check (allow-list)
      - schema_validate (if schema provided OR policy.enabled=True)
    """
    rules = _rules_for_meta(meta)

    flags: List[str] = []
    details: Dict[str, Any] = {}
    status = "accept"

    # 1) size_bounds on payload length proxy (zip_len recorded in meta)
    sb = (rules.get("size_bounds") or {})
    max_zip = sb.get("max_zip_bytes")
    if isinstance(max_zip, (int, float)):
        zip_len = meta.get("zip_len")
        if isinstance(zip_len, (int, float)) and zip_len > max_zip:
            status = "reject"
            flags.append("too_large")
            details["size_bounds"] = {"zip_len": zip_len, "max_zip_bytes": max_zip}

    # 2) hash_check allow-list
    if status != "reject":
        hc = (rules.get("hash_check") or {})
        allowed = hc.get("allowed") or []
        vhash = meta.get("version_hash")
        if allowed and vhash not in allowed:
            flags.append("hash_not_allowed")
            details["hash_check"] = {"version_hash": vhash, "allowed_count": len(allowed)}

    # 3) schema validation
    sv = (rules.get("schema_validate") or {})
    policy_enabled = bool(sv.get("enabled"))
    want_validate = policy_enabled or (schema is not None)

    if status != "reject" and want_validate:
        if schema is None:
            # Policy-enabled but no schema provided
            flags.append("schema_missing")
            details["schema_validate"] = {"error": "schema not provided", "schema_ref": schema_ref}
            status = "quarantine"
        else:
            if payload is None or not isinstance(payload, (dict, list, str, int, float, bool, type(None))):
                # If not JSON-like, we can't validate meaningfully
                flags.append("schema_unsupported_payload")
                details.setdefault("schema_validate", {})["note"] = "payload not JSON-like"
                status = "quarantine"
            else:
                if jsonschema is None:
                    flags.append("schema_unavailable")
                    details.setdefault("schema_validate", {})["note"] = "jsonschema not installed"
                    # keep 'flag', don't block ingest
                else:
                    try:
                        jsonschema.validate(instance=payload, schema=schema)  # type: ignore
                    except Exception as e:
                        flags.append("schema_invalid")
                        details["schema_validate"] = {"error": repr(e), "schema_ref": schema_ref}
                        status = "quarantine"

    trust = _compute_trust(status, flags, rules)
    return status, flags, trust, details
