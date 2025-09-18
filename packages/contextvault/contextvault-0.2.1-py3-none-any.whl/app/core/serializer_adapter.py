# File: app/core/serializer_adapter.py
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile

# Your existing serializer (DO NOT MODIFY)
from app.core.serializer import (
    create_context_from_upload as _create_upload,   # async
    create_context_from_raw as _create_raw,         # async (expects str|dict)
)

# Optional helpers you already use; if any import fails, we degrade gracefully.
try:
    from app.core.metadata import get_zip_length  # type: ignore
except Exception:
    def get_zip_length(_image_name: str) -> Optional[int]:
        return None

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _write_meta(context_id: str, meta: Dict[str, Any]) -> Path:
    meta_path = DATA_DIR / f"ctx_{context_id}.meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta_path

async def create_context_from_file(
    upload: UploadFile,
    compress: bool,
    extra_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Adapter -> uses your existing async create_context_from_upload(upload, ...)
    Returns: { context_id, png_path, meta }
    """
    result = await _create_upload(upload, collection_name=None, category_override=None, compress=compress)

    # Your serializer returns image_file (e.g., ctx_<id>.png) inside data/
    context_id = result.get("context_id")
    image_name = result.get("image_file")
    if not context_id or not image_name:
        raise RuntimeError("Serializer did not return expected keys (context_id, image_file).")

    png_path = str(DATA_DIR / image_name)

    # Build additive meta (non-invasive; your existing register_context stays as-is)
    base_meta: Dict[str, Any] = {
        "context_id": context_id,
        "created_at": _now_iso(),
        "source": "file",
        "original_filename": result.get("original_filename"),
        "compressed": bool(result.get("compressed")),
        "version_hash": result.get("version_hash"),
        "category": result.get("category"),
        "collection": result.get("collection"),
        "zip_len": get_zip_length(image_name) if image_name else None,
    }

    # Carry object linkage through (key for our P0 slice)
    if extra_metadata:
        base_meta.update({"object_id": extra_metadata.get("object_id"), "extra": {k: v for k, v in extra_metadata.items() if k != "object_id"}})

    _write_meta(context_id, base_meta)

    return {
        "context_id": context_id,
        "png_path": png_path,
        "meta": base_meta,
        # Note: no zip_path — your flow stores ZIP only inside PNG, which we keep.
    }

async def create_context_from_raw(
    raw_bytes: bytes,
    compress: bool,
    extra_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Adapter -> uses your existing async create_context_from_raw(raw_data, ...)
    Your raw endpoint expects str|dict, so we decode bytes as UTF-8 and try JSON.
    """
    # 1) Try JSON
    raw_data: Any
    try:
        raw_str = raw_bytes.decode("utf-8")
        try:
            raw_data = json.loads(raw_str)  # dict case
        except json.JSONDecodeError:
            raw_data = raw_str               # plain text case
    except UnicodeDecodeError:
        # If truly binary bytes arrive here, surface a clear error.
        raise ValueError("Raw body is not valid UTF-8 text/JSON. Send a file instead via 'upload'.")

    result = await _create_raw(raw_data, collection_name=None, category_override="raw", compress=compress)

    context_id = result.get("context_id")
    image_name = result.get("image_file")
    if not context_id or not image_name:
        raise RuntimeError("Serializer did not return expected keys (context_id, image_file).")

    png_path = str(DATA_DIR / image_name)

    base_meta: Dict[str, Any] = {
        "context_id": context_id,
        "created_at": _now_iso(),
        "source": "raw",
        "original_filename": result.get("original_filename"),
        "compressed": bool(result.get("compressed")),
        "version_hash": result.get("version_hash"),
        "category": result.get("category"),
        "collection": result.get("collection"),
        "zip_len": get_zip_length(image_name) if image_name else None,
    }

    if extra_metadata:
        base_meta.update({"object_id": extra_metadata.get("object_id"), "extra": {k: v for k, v in extra_metadata.items() if k != "object_id"}})

    _write_meta(context_id, base_meta)

    return {
        "context_id": context_id,
        "png_path": png_path,
        "meta": base_meta,
    }
