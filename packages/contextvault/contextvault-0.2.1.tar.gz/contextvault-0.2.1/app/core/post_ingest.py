# app/core/post_ingest.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Iterable, Optional

from app.core.storage.filelog import append_event
from app.core.storage.filelog import get_event_by_id  # may be useful
from app.core.policy.validator import evaluate_ingest_extended

BASE = Path("data")
LOG_DIR = BASE / "log"
CONTEXTS_LOG = LOG_DIR / "contexts.jsonl"


def iter_context_events(path: Path = CONTEXTS_LOG) -> Iterable[Dict[str, Any]]:
    """Yield parsed JSON events from contexts.jsonl (skip malformed lines)."""
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                ev = json.loads(ln)
            except Exception:
                # skip malformed lines
                continue
            yield ev


def _is_context_record(ev: Dict[str, Any]) -> bool:
    # consider both created and migrated and post-validation events as source records,
    # but only process events that contain a context_id and meta.
    return ev.get("event") in ("context_created", "context_migrated") and ev.get("context_id") and ev.get("meta")


def run_post_ingest_validation(
    *,
    limit: Optional[int] = None,
    object_id: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Scan contexts log and re-evaluate each context through the ingest policy logic.

    - If current evaluation differs from stored meta, append a non-destructive event:
      event = "context_post_validated" with the new meta and a note.
    - Returns a summary of processed / changed counts and changed items.

    Note: This is conservative — it uses stored meta (no payload decoding).
    """
    processed = 0
    changed = 0
    changed_items = []

    for ev in iter_context_events():
        if limit is not None and processed >= limit:
            break

        if not _is_context_record(ev):
            continue

        ctx_id = ev.get("context_id")
        meta = ev.get("meta") or {}

        # Optionally scope to object_id
        if object_id and meta.get("object_id") != object_id:
            continue

        # Re-evaluate using policy engine (no payload here)
        # evaluate_ingest_extended returns (status, flags, trust, details)
        status, flags, trust, details = evaluate_ingest_extended(meta, payload=None, schema=None, schema_ref=None)

        # Normalize existing fields for comparison
        existing_status = meta.get("status")
        existing_flags = meta.get("flags", [])
        existing_trust = meta.get("trust")

        # Decide if something changed
        if status != existing_status or flags != existing_flags or trust != existing_trust:
            processed += 1
            change = {
                "context_id": ctx_id,
                "old": {"status": existing_status, "flags": existing_flags, "trust": existing_trust},
                "new": {"status": status, "flags": flags, "trust": trust, "details": details},
            }
            changed += 1
            changed_items.append(change)

            if not dry_run:
                # Append a non-destructive 'context_post_validated' event (so original lines remain)
                append_event(
                    "contexts",
                    {
                        "event": "context_post_validated",
                        "context_id": ctx_id,
                        "meta": {
                            **meta,
                            "status": status,
                            "flags": flags,
                            "trust": trust,
                            # attach details if present
                            **({"validation_details": details} if details else {}),
                        },
                        "ts": None,
                        "note": "post-ingest revalidation appended by post_ingest script",
                    },
                )
        else:
            processed += 1

    summary = {"processed": processed, "changed": changed, "changed_items": changed_items}
    return summary
