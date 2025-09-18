# File: app/api/p0_routes.py
from __future__ import annotations

import json
import uuid
import importlib
import importlib.util
import sys
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Body, File, HTTPException, Request, UploadFile

from app.core.storage.filelog import append_event, get_event_by_id
from app.core.policy.validator import evaluate_ingest_extended
from app.core.schema.registry import get_schema
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------
# Robust serializer loader (looks for app.core.serializer)
# ---------------------------------------------------------------------
def _load_serializer_module():
    # 1) normal import path
    try:
        return importlib.import_module("app.core.serializer")
    except Exception:
        pass
    # 2) file-path fallback (helps during --reload on Windows)
    app_dir = Path(__file__).resolve().parents[1]  # .../app
    ser_path = app_dir / "core" / "serializer.py"
    if not ser_path.exists():
        raise RuntimeError(f"Cannot find serializer at {ser_path}")
    spec = importlib.util.spec_from_file_location("app.core.serializer", ser_path)  # type: ignore
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to build spec for app.core.serializer")
    mod = importlib.util.module_from_spec(spec)
    # register so future imports work
    sys.modules["app.core.serializer"] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def _get_serializer_funcs():
    _ser = _load_serializer_module()
    try:
        return _ser.create_context_from_upload, _ser.create_context_from_raw
    except AttributeError as e:
        raise RuntimeError(f"serializer missing required functions: {e}")

# ---------------------------------------------------------------------
# Objects
# ---------------------------------------------------------------------
@router.post("/objects")
def create_object(
    object_type: str = Body(..., embed=True),
    attrs: dict | None = Body(None, embed=True),
) -> dict:
    object_id = str(uuid.uuid4())
    append_event(
        "objects",
        {
            "event": "object_created",
            "object_id": object_id,
            "object_type": object_type,
            "attrs": attrs or {},
            "version": 1,
            "ts": None,
        },
    )
    return {"object_id": object_id}


@router.get("/objects/{object_id}")
def get_object(object_id: str) -> dict:
    obj = get_event_by_id("objects", "object_id", object_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj

# ---------------------------------------------------------------------
# Context creation (file or raw) linked to object
# ---------------------------------------------------------------------
@router.post("/objects/{object_id}/contexts")
async def create_object_context(
    object_id: str,
    request: Request,
    upload: UploadFile = File(None),
    compress: bool = False,
    object_type: str | None = None,
    schema_ref: str | None = None,
) -> dict:
    # Validate object exists
    if not get_event_by_id("objects", "object_id", object_id):
        raise HTTPException(status_code=404, detail="Parent object not found")

    ser_create_upload, ser_create_raw = _get_serializer_funcs()
    payload_for_schema = None

    # A) File upload path -> call your serializer (no extra params)
    if upload is not None:
        result = await ser_create_upload(
            upload,
            collection_name=None,
            category_override=None,
            compress=compress,
        )

    # B) Raw body path -> detect JSON (dict) or plain text (str)
    else:
        raw_bytes = await request.body()
        if not raw_bytes:
            raise HTTPException(
                status_code=400,
                detail="No input provided (file upload or raw body required)",
            )

        # Try JSON → dict; else fallback to UTF-8 text
        raw_data: str | dict
        try:
            payload_for_schema = json.loads(raw_bytes.decode("utf-8"))
            if isinstance(payload_for_schema, dict):
                raw_data = payload_for_schema
            elif isinstance(payload_for_schema, list):
                raw_data = json.dumps(payload_for_schema)
            else:
                raw_data = json.dumps(payload_for_schema)
        except Exception:
            raw_data = raw_bytes.decode("utf-8", errors="replace")
            payload_for_schema = None  # not JSON

        result = await ser_create_raw(
            raw_data,
            collection_name=None,
            category_override="raw",
            compress=compress,
        )

    # Expect keys from serializer
    context_id = result.get("context_id")
    if not context_id:
        raise HTTPException(status_code=500, detail="Serializer did not return context_id")

    # ---------- CHANGED BLOCK (add object_id + created_at) ----------
    meta = {
        "version_hash": result.get("version_hash"),
        "category": result.get("category"),
        "collection": result.get("collection"),
        "compressed": result.get("compressed", False),
        "original_filename": result.get("original_filename"),
        "object_id": object_id,  # <- required by tests
        "created_at": datetime.now(timezone.utc).isoformat(),  # <- required by tests
        "extra": {"object_type": object_type} if object_type else {},
    }
    # ---------------------------------------------------------------

    # Optional schema for RAW JSON only
    schema = get_schema(schema_ref) if schema_ref else None

    # Evaluate ingest (safe even with sparse meta)
    status, flags, trust, details = evaluate_ingest_extended(
        meta, payload=payload_for_schema, schema=schema, schema_ref=schema_ref
    )
    meta["status"] = status
    meta["flags"] = flags
    meta["trust"] = trust
    if details:
        meta.setdefault("validation", {})["details"] = details

    if status == "reject":
        raise HTTPException(
            status_code=422, detail={"message": "context rejected by policy", "meta": meta}
        )

    # Artifacts (we only know the PNG file name from serializer)
    artifacts = {}
    if "image_file" in result:
        artifacts["image_file"] = str(result["image_file"])

    # Log the object-linked context
    append_event(
        "contexts",
        {
            "event": "context_created",
            "context_id": context_id,
            "object_id": object_id,
            "meta": meta,
            "artifacts": artifacts,
            "ts": None,
        },
    )

    # Return the serializer result plus enriched meta
    return {"context_id": context_id, **result, "meta": meta}

# ---------------------------------------------------------------------
# Lineage
# ---------------------------------------------------------------------
class ParentsBody(BaseModel):
    parents: list[str]

@router.post("/contexts/{context_id}/parents")
def add_context_parents(context_id: str, body: ParentsBody) -> dict:
    # Validate child exists
    if not get_event_by_id("contexts", "context_id", context_id):
        raise HTTPException(status_code=404, detail="Context not found")

    parents = body.parents
    if not parents:
        raise HTTPException(status_code=400, detail="parents list cannot be empty")

    for pid in parents:
        append_event(
            "lineage",
            {
                "event": "lineage_added",
                "edge_id": None,
                "context_id": context_id,
                "parent_id": pid,
                "ts": None,
            },
        )
    return {"context_id": context_id, "parents": parents}