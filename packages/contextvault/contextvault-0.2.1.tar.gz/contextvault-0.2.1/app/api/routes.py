# File: app/api/routes.py
from typing import List, Optional, Union
from fastapi import Request
from fastapi import APIRouter, UploadFile, File, Body, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.serializer import (
    create_context_from_upload,
    create_context_from_raw,
    decode_context_from_image_raw,
    bulk_create_context,
    create_context_for_collection,
    bulk_create_context_for_collection,
)
from app.core.context_object import context_object
from app.core.indexer import search_index
from app.core.metadata_extractor import extract_metadata
from app.core.serializer import create_context_from_multiple_uploads

# -------------------------
# NEW imports for encryption handling
# -------------------------
import os
import tempfile
from pathlib import Path
from starlette.datastructures import UploadFile as StarletteUploadFile  # kept for compatibility checks

from app.core.security.encryption import encrypt_file, decrypt_file, decrypt_bytes

router = APIRouter()

# Ensure data dir exists (matches existing project layout)
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------
# Context
# -------------------------
@router.post("/create_context/", tags=["Context"], summary="Create a new context (file or raw)")
async def create_context(
    request: Request,
    upload: UploadFile = File(None),
    compress: bool = False,
):
    """
    Create context from UploadFile or raw data. This wraps existing serializer functions and
    then ensures any produced ZIP/PNG files are encrypted at rest (.enc).
    """
    if upload:
        result = await create_context_from_upload(upload, compress=compress)
    else:
        try:
            raw_data = await request.json()  # try JSON first
        except Exception:
            raw_data = (await request.body()).decode("utf-8")  # fallback to plain text
        result = await create_context_from_raw(raw_data, compress=compress)

    if result.get("status") == "error":
        return JSONResponse(
            status_code=500,
            content={"message": "Failed to create context", "details": result.get("detail", "Unknown error")},
        )

    # -------------------------
    # Encrypt generated files (ZIP + PNG) if present
    # -------------------------
    try:
        if "zip_file" in result and result["zip_file"]:
            zip_path = DATA_DIR / result["zip_file"] if not Path(result["zip_file"]).is_absolute() else Path(result["zip_file"])
            if zip_path.exists():
                enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                encrypt_file(str(zip_path), str(enc_zip_path))
                zip_path.unlink()
                result["zip_file"] = enc_zip_path.name

        if "image_file" in result and result["image_file"]:
            img_path = DATA_DIR / result["image_file"] if not Path(result["image_file"]).is_absolute() else Path(result["image_file"])
            if img_path.exists():
                enc_img_path = img_path.with_name(img_path.name + ".enc")
                encrypt_file(str(img_path), str(enc_img_path))
                img_path.unlink()
                result["image_file"] = enc_img_path.name

        result["encrypted"] = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {e}")

    return {
        "message": "Context created successfully",
        "context_id": result["context_id"],
        "image": f"data/{result['image_file']}" if result.get("image_file") else None,
        "hash": result.get("version_hash"),
        "original_filename": result.get("original_filename", "raw_data"),
        "compressed": result.get("compressed", False),
        "entry_type": result.get("entry_type"),
        "encrypted": result.get("encrypted", False),
    }


@router.post("/decode_context_raw/", tags=["Context"], summary="Decode a previously created context")
async def decode_context_raw(image: UploadFile = File(...)):
    """
    Accepts an uploaded image or an uploaded encrypted file (.enc). If `.enc` file is received,
    it is decrypted in-memory and forwarded to the existing decode_context_from_image_raw(...)
    serializer.

    Uses a tiny shim object (FakeUpload) that implements the minimal async API the decoder expects,
    avoiding direct construction of starlette UploadFile which varies across versions.
    """
    # Read uploaded bytes (we consume the stream)
    uploaded_bytes = await image.read()
    original_filename = getattr(image, "filename", "upload") or "upload"
    is_encrypted_upload = original_filename.endswith(".enc")

    tmp_spooled = tempfile.SpooledTemporaryFile()
    try:
        if is_encrypted_upload:
            try:
                plaintext = decrypt_bytes(uploaded_bytes)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decrypt uploaded file: {e}")
            tmp_spooled.write(plaintext)
            fake_filename = original_filename[: -len(".enc")] or "upload"
        else:
            tmp_spooled.write(uploaded_bytes)
            fake_filename = original_filename

        tmp_spooled.seek(0)

        # Minimal shim object implementing the small async UploadFile-like surface required by the decoder.
        class FakeUpload:
            def __init__(self, filename: str, fileobj, content_type: str = "application/octet-stream"):
                self.filename = filename
                self.file = fileobj
                self.content_type = content_type

            async def read(self):
                # ensure we read from current file position
                # SpooledTemporaryFile.read() is sync, but decoder may await .read()
                return self.file.read()

            async def seek(self, pos):
                return self.file.seek(pos)

            # Some code expects .close() to exist
            async def close(self):
                try:
                    self.file.close()
                except Exception:
                    pass

            # Provide attribute-like fallback for code that expects .file
            def get_file(self):
                return self.file

        fake_upload = FakeUpload(fake_filename, tmp_spooled, getattr(image, "content_type", "application/octet-stream"))

        # Call the existing decode function (it should work with this shim)
        result = await decode_context_from_image_raw(fake_upload)

    finally:
        try:
            tmp_spooled.close()
        except Exception:
            pass  # ignore cleanup issues

    if result.get("status") == "error":
        return JSONResponse(
            status_code=500,
            content={
                "message": "Failed to decode context",
                "details": result.get("detail", "Unknown error"),
            },
        )
    return result


@router.post("/bulk_create_context/", tags=["Context"], summary="Create contexts for multiple files in one request")
async def bulk_create_context_api(uploads: List[UploadFile] = File(...), compress: bool = False):
    """
    Call existing bulk_create_context(...) serializer, then encrypt produced files in results.
    bulk_create_context is expected to return a list of per-file results (or a structure similar).
    """
    results = await bulk_create_context(uploads, compress=compress)

    # If serializer returned status/error shape, bubble it
    if isinstance(results, dict) and results.get("status") == "error":
        return JSONResponse(status_code=500, content={"message": "Bulk create failed", "details": results.get("detail", "Unknown error")})

    # Iterate and encrypt any files reported
    try:
        # Handle list-of-results
        if isinstance(results, list):
            for res in results:
                if not res or not isinstance(res, dict):
                    continue
                # encrypt zip_file if present
                if "zip_file" in res and res["zip_file"]:
                    zip_path = DATA_DIR / res["zip_file"] if not Path(res["zip_file"]).is_absolute() else Path(res["zip_file"])
                    if zip_path.exists():
                        enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                        encrypt_file(str(zip_path), str(enc_zip_path))
                        zip_path.unlink()
                        res["zip_file"] = enc_zip_path.name
                # encrypt image_file if present
                if "image_file" in res and res["image_file"]:
                    img_path = DATA_DIR / res["image_file"] if not Path(res["image_file"]).is_absolute() else Path(res["image_file"])
                    if img_path.exists():
                        enc_img_path = img_path.with_name(img_path.name + ".enc")
                        encrypt_file(str(img_path), str(enc_img_path))
                        img_path.unlink()
                        res["image_file"] = enc_img_path.name
                res["encrypted"] = True
        # If serializer returns single dict
        elif isinstance(results, dict):
            res = results
            if res.get("status") != "error":
                if "zip_file" in res and res["zip_file"]:
                    zip_path = DATA_DIR / res["zip_file"] if not Path(res["zip_file"]).is_absolute() else Path(res["zip_file"])
                    if zip_path.exists():
                        enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                        encrypt_file(str(zip_path), str(enc_zip_path))
                        zip_path.unlink()
                        res["zip_file"] = enc_zip_path.name
                if "image_file" in res and res["image_file"]:
                    img_path = DATA_DIR / res["image_file"] if not Path(res["image_file"]).is_absolute() else Path(res["image_file"])
                    if img_path.exists():
                        enc_img_path = img_path.with_name(img_path.name + ".enc")
                        encrypt_file(str(img_path), str(enc_img_path))
                        img_path.unlink()
                        res["image_file"] = enc_img_path.name
                res["encrypted"] = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed during bulk create: {e}")

    return results


# -------------------------
# Context Object (global)
# -------------------------
@router.get("/context_object/", tags=["Context Object"], summary="Get current state of the central Context Object")
def get_context_object():
    return JSONResponse(content=context_object.get_full_state())


@router.post("/add_to_context/", tags=["Context Object"], summary="Add an entry to the default collection")
async def add_to_context(category: str = Body(...), entry_id: str = Body(...), entry: dict = Body(...)):
    context_object.add_entry(category, entry_id, entry)
    return {"status": "added", "category": category, "entry_id": entry_id}


@router.get("/context_versions/", tags=["Context Object"], summary="List all saved Context Object versions")
def context_versions():
    return {"versions": context_object.list_versions()}


@router.get("/load_context_version/{version_hash}", tags=["Context Object"], summary="Load a specific Context Object version")
def load_context_version(version_hash: str):
    try:
        data = context_object.load_version(version_hash)
        return {"version": version_hash, "context": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Version {version_hash} not found")


@router.get("/load_context_snapshot", tags=["Context Object"], summary="Get metadata of the latest saved snapshot")
def load_context_snapshot():
    snapshot = context_object.get_latest_snapshot()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshots found")
    return {"latest_snapshot": snapshot}


@router.get("/context_snapshot_image/{version_hash}", tags=["Context Object"], summary="Get path to a snapshot PNG by version")
def context_snapshot_image(version_hash: str):
    p = context_object.get_snapshot_image_path(version_hash)
    if not p:
        raise HTTPException(status_code=404, detail="Snapshot image not found")
    return {"path": p}


@router.get("/search_context", tags=["Context Object"], summary="Search entries in the Context Object")
def search_context(
    q: str = Query(..., description="Keyword to match against file name / category / entry id"),
    collection: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    return {"results": context_object.search(q=q, collection=collection, category=category, limit=limit)}


@router.get("/metadata_preview/{collection}/{category}/{entry_id}", tags=["Context Object"], summary="Get metadata for a specific entry")
def metadata_preview(collection: str, category: str, entry_id: str):
    entry = context_object.get_entry(collection, category, entry_id)
    if not entry:
        raise HTTPException(
            status_code=404,
            detail=f"Entry not found for collection='{collection}', category='{category}', entry_id='{entry_id}'",
        )
    return {
        "collection": collection,
        "category": category,
        "entry_id": entry_id,
        "file_name": entry.get("file_name"),
        "version_hash": entry.get("version_hash"),
        "zip_file": entry.get("zip_file"),
        "image_file": entry.get("image_file"),
        "metadata": entry.get("metadata") or {},
    }


# --- Deletions: default collection ---
@router.delete("/context_entry/{category}/{entry_id}", tags=["Context Object"], summary="Delete an entry from the default collection")
def delete_default_entry(category: str, entry_id: str):
    try:
        version = context_object.delete_entry(category=category, entry_id=entry_id, collection_name=None)
        return {"status": "deleted", "collection": "default", "category": category, "entry_id": entry_id, "new_version": version}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/context_entry/{category}/{entry_id}/conditional", tags=["Context Object"], summary="Conditionally hard-delete an entry (default collection)")
def conditional_delete_default_entry(
    category: str,
    entry_id: str,
    confirm: bool = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    if_version_equals: Optional[str] = Body(None, embed=True),
    if_created_before: Optional[str] = Body(None, embed=True),
    dry_run: bool = Body(False, embed=True),
):
    try:
        res = context_object.delete_entry(
            category=category,
            entry_id=entry_id,
            collection_name=None,
            confirm=confirm,
            reason=reason,
            if_version_equals=if_version_equals,
            if_created_before=if_created_before,
            dry_run=dry_run,
        )
        return res
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=412, detail=str(e))


# -------------------------
# Collections
# -------------------------
@router.post("/collections/{name}", tags=["Collections"], summary="Create a collection (idempotent)")
def create_collection(name: str):
    context_object.add_collection(name)
    return {"status": "ok", "collection": name, "collections": context_object.list_collections()}


@router.get("/collections/{name}", tags=["Collections"], summary="Get a collection by name")
def get_collection(name: str):
    col = context_object.get_collection(name)
    if not col:
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")
    return col


@router.delete("/collections/{name}", tags=["Collections"], summary="Delete an entire collection")
def delete_collection(name: str):
    try:
        version = context_object.delete_collection(name)
        return {"status": "deleted", "collection": name, "new_version": version}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/collections", tags=["Collections"], summary="List collections")
def list_collections():
    return {"collections": context_object.list_collections()}


@router.post("/collections/{name}/entries", tags=["Collections"], summary="Add an entry to a specific collection")
def add_entry_to_collection(name: str, category: str = Body(...), entry_id: str = Body(...), entry: dict = Body(...)):
    context_object.add_entry_to_collection(name, category, entry_id, entry)
    return {"status": "added", "collection": name, "category": category, "entry_id": entry_id}


@router.get("/collections/{name}/entries/{category}", tags=["Collections"], summary="List entries in a collection/category")
def list_entries_in_category(name: str, category: str):
    ids = context_object.list_entries_in_category(name, category)
    return {"collection": name, "category": category, "entry_ids": ids}


@router.get("/collections/{name}/entries/{category}/{entry_id}", tags=["Collections"], summary="Get a single entry")
def get_entry_in_category(name: str, category: str, entry_id: str):
    e = context_object.get_entry(name, category, entry_id)
    if not e:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"collection": name, "category": category, "entry_id": entry_id, "entry": e}


@router.delete("/collections/{name}/entries/{category}/{entry_id}", tags=["Collections"], summary="Delete an entry from a specific collection")
def delete_entry_from_collection(name: str, category: str, entry_id: str):
    try:
        version = context_object.delete_entry(category=category, entry_id=entry_id, collection_name=name)
        return {"status": "deleted", "collection": name, "category": category, "entry_id": entry_id, "new_version": version}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/collections/{name}/create_context", tags=["Collections"], summary="Create a context directly into a specific collection")
async def collection_create_context(name: str, upload: UploadFile = File(...), compress: bool = False):
    result = await create_context_for_collection(name, upload, compress=compress)
    if result.get("status") == "error":
        return JSONResponse(
            status_code=500,
            content={
                "message": "Failed to create context",
                "details": result.get("detail", "Unknown error"),
                "collection": name,
            },
        )

    # Encrypt files if present
    try:
        if "zip_file" in result and result["zip_file"]:
            zip_path = DATA_DIR / result["zip_file"] if not Path(result["zip_file"]).is_absolute() else Path(result["zip_file"])
            if zip_path.exists():
                enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                encrypt_file(str(zip_path), str(enc_zip_path))
                zip_path.unlink()
                result["zip_file"] = enc_zip_path.name

        if "image_file" in result and result["image_file"]:
            img_path = DATA_DIR / result["image_file"] if not Path(result["image_file"]).is_absolute() else Path(result["image_file"])
            if img_path.exists():
                enc_img_path = img_path.with_name(img_path.name + ".enc")
                encrypt_file(str(img_path), str(enc_img_path))
                img_path.unlink()
                result["image_file"] = enc_img_path.name

        result["encrypted"] = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {e}")

    return {
        "message": "Context created successfully",
        "collection": name,
        "context_id": result["context_id"],
        "image": f"data/{result['image_file']}" if result.get("image_file") else None,
        "hash": result["version_hash"],
        "original_filename": result.get("original_filename"),
        "compressed": result.get("compressed"),
        "encrypted": result.get("encrypted", False),
    }


@router.post("/collections/{name}/bulk_create_context", tags=["Collections"], summary="Bulk-create contexts into a specific collection")
async def collection_bulk_create_context(name: str, uploads: List[UploadFile] = File(...), compress: bool = False):
    results = await bulk_create_context_for_collection(name, uploads, compress=compress)

    if isinstance(results, dict) and results.get("status") == "error":
        return JSONResponse(status_code=500, content={"message": "Bulk create failed", "details": results.get("detail", "Unknown error")})

    try:
        if isinstance(results, list):
            for res in results:
                if not res or not isinstance(res, dict):
                    continue
                if "zip_file" in res and res["zip_file"]:
                    zip_path = DATA_DIR / res["zip_file"] if not Path(res["zip_file"]).is_absolute() else Path(res["zip_file"])
                    if zip_path.exists():
                        enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                        encrypt_file(str(zip_path), str(enc_zip_path))
                        zip_path.unlink()
                        res["zip_file"] = enc_zip_path.name
                if "image_file" in res and res["image_file"]:
                    img_path = DATA_DIR / res["image_file"] if not Path(res["image_file"]).is_absolute() else Path(res["image_file"])
                    if img_path.exists():
                        enc_img_path = img_path.with_name(img_path.name + ".enc")
                        encrypt_file(str(img_path), str(enc_img_path))
                        img_path.unlink()
                        res["image_file"] = enc_img_path.name
                res["encrypted"] = True
        elif isinstance(results, dict):
            res = results
            if res.get("status") != "error":
                if "zip_file" in res and res["zip_file"]:
                    zip_path = DATA_DIR / res["zip_file"] if not Path(res["zip_file"]).is_absolute() else Path(res["zip_file"])
                    if zip_path.exists():
                        enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                        encrypt_file(str(zip_path), str(enc_zip_path))
                        zip_path.unlink()
                        res["zip_file"] = enc_zip_path.name
                if "image_file" in res and res["image_file"]:
                    img_path = DATA_DIR / res["image_file"] if not Path(res["image_file"]).is_absolute() else Path(res["image_file"])
                    if img_path.exists():
                        enc_img_path = img_path.with_name(img_path.name + ".enc")
                        encrypt_file(str(img_path), str(enc_img_path))
                        img_path.unlink()
                        res["image_file"] = enc_img_path.name
                res["encrypted"] = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed during collection bulk create: {e}")

    return results


@router.post("/collections/{name}/snapshot", tags=["Collections"], summary="Create a snapshot image for a specific collection")
def collection_snapshot(name: str):
    try:
        v = context_object.save_collection_snapshot(name)
        return {"collection": name, "version": v}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Collection '{name}' not found")


@router.get("/collections/{name}/versions", tags=["Collections"], summary="List snapshot versions for a collection")
def collection_versions(name: str):
    return {"collection": name, "versions": context_object.list_collection_versions(name)}


@router.get("/collections/{name}/load/{version_hash}", tags=["Collections"], summary="Load a specific collection snapshot version")
def collection_load_version(name: str, version_hash: str):
    try:
        data = context_object.load_collection_version(name, version_hash)
        return {"collection": name, "version": version_hash, "data": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Collection snapshot not found")


@router.get("/collections/{name}/snapshot_image/{version_hash}", tags=["Collections"], summary="Get path to a collection snapshot PNG by version")
def collection_snapshot_image(name: str, version_hash: str):
    p = context_object.get_collection_snapshot_image_path(name, version_hash)
    if not p:
        raise HTTPException(status_code=404, detail="Collection snapshot image not found")
    return {"path": p}


@router.get("/collections/{name}/snapshot_latest", tags=["Collections"], summary="Get metadata of the latest collection snapshot")
def collection_snapshot_latest(name: str):
    snap = context_object.get_collection_latest_snapshot(name)
    if not snap:
        raise HTTPException(status_code=404, detail="No collection snapshots found")
    return {"latest_snapshot": snap}


@router.delete("/collections/{name}/entries/{category}/{entry_id}/conditional", tags=["Collections"], summary="Conditionally hard-delete an entry (named collection)")
def conditional_delete_from_collection(
    name: str,
    category: str,
    entry_id: str,
    confirm: bool = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    if_version_equals: Optional[str] = Body(None, embed=True),
    if_created_before: Optional[str] = Body(None, embed=True),
    dry_run: bool = Body(False, embed=True),
):
    try:
        res = context_object.delete_entry(
            category=category,
            entry_id=entry_id,
            collection_name=name,
            confirm=confirm,
            reason=reason,
            if_version_equals=if_version_equals,
            if_created_before=if_created_before,
            dry_run=dry_run,
        )
        return res
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=412, detail=str(e))


@router.post("/collections/{name}/entries/{category}/{entry_id}/soft_delete", tags=["Collections"], summary="Conditionally soft-delete (tombstone) an entry")
def conditional_soft_delete(
    name: str,
    category: str,
    entry_id: str,
    confirm: bool = Body(..., embed=True),
    reason: Optional[str] = Body(None, embed=True),
    if_version_equals: Optional[str] = Body(None, embed=True),
    if_created_before: Optional[str] = Body(None, embed=True),
    dry_run: bool = Body(False, embed=True),
):
    try:
        res = context_object.soft_delete_entry(
            category=category,
            entry_id=entry_id,
            collection_name=name,
            confirm=confirm,
            reason=reason,
            if_version_equals=if_version_equals,
            if_created_before=if_created_before,
            dry_run=dry_run,
        )
        return res
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=412, detail=str(e))


# -------------------------
# Search
# -------------------------
@router.get("/search_index", tags=["Search"], summary="Search file contexts & context-object snapshots")
def search_index_api(q: str = Query(...)):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query 'q' must not be empty.")
    return search_index(q)


@router.get("/semantic_search", tags=["Search"], summary="Semantic-ish search (cosine TF) across files and/or snapshots")
def semantic_search_api(q: str, scope: str = "files", top_k: int = 10):
    from app.core.indexer import semantic_search
    return semantic_search(q=q, scope=scope, top_k=top_k)

# ----------------------------
# combine contexts
# ----------------------------

@router.post("/create_context_multi/", tags=["Context"], summary="Create one context from multiple uploaded files")
async def create_context_multi(uploads: List[UploadFile] = File(...), compress: bool = False, collection: str = None):
    """
    Create a single context (one PNG) which contains a ZIP of all provided uploads.
    """
    result = await create_context_from_multiple_uploads(uploads, collection_name=collection, compress=compress)
    if result.get("status") == "error":
        return JSONResponse(status_code=500, content={"message": "Failed to create multi-file context", "details": result.get("detail", "Unknown error")})

    # encryption flow (same as create_context)
    try:
        if "zip_file" in result and result["zip_file"]:
            zip_path = DATA_DIR / result["zip_file"] if not Path(result["zip_file"]).is_absolute() else Path(result["zip_file"])
            if zip_path.exists():
                enc_zip_path = zip_path.with_name(zip_path.name + ".enc")
                encrypt_file(str(zip_path), str(enc_zip_path))
                zip_path.unlink()
                result["zip_file"] = enc_zip_path.name

        if "image_file" in result and result["image_file"]:
            img_path = DATA_DIR / result["image_file"] if not Path(result["image_file"]).is_absolute() else Path(result["image_file"])
            if img_path.exists():
                enc_img_path = img_path.with_name(img_path.name + ".enc")
                encrypt_file(str(img_path), str(enc_img_path))
                img_path.unlink()
                result["image_file"] = enc_img_path.name

        result["encrypted"] = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {e}")

    return {
        "message": "Multi-file context created successfully",
        "context_id": result["context_id"],
        "image": f"data/{result['image_file']}" if result.get("image_file") else None,
        "hash": result.get("version_hash"),
        "original_filename": result.get("original_filename", ""),
        "compressed": result.get("compressed", False),
        "entry_type": result.get("entry_type"),
        "encrypted": result.get("encrypted", False),
    }