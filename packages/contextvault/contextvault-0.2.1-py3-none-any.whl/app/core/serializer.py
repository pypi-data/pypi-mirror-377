import uuid
import zipfile
import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
import json

from fastapi import UploadFile
from PIL import Image
import uuid

from app.core.utils import (
    generate_hash,
    encode_binary_to_image,
    decode_image_to_binary,
)
from app.core.metadata import (
    register_context,
    get_original_filename,
    get_zip_length,
)
from app.core.context_object import context_object
from app.core.indexer import index_context

BASE_DIR = Path("data")
BASE_DIR.mkdir(parents=True, exist_ok=True)
EXTRACT_DIR = BASE_DIR / "extractions"
EXTRACT_DIR.mkdir(parents=True, exist_ok=True)


# --- simple, centralized category detector ---
def detect_category_from_filename(filename: str) -> str:
    ext = (Path(filename).suffix or "").lower()

    FILE_TYPE_MAP = {
        "ip": [".ip"],
        "geolocation": [".geojson", ".gpx", ".kml", ".shp", ".topojson", ".csv"],
        "text": [".txt", ".md", ".log"],
        "document": [".pdf", ".docx", ".odt"],
        "structured": [".csv", ".xls", ".xlsx", ".json", ".xml", ".yaml", ".yml"],
        "sql": [".sql", ".db", ".sqlite"],
        "archive": [".zip", ".tar", ".gz"],
        "image": [".png", ".jpg", ".jpeg", ".bmp", ".webp"],
        "audio": [".mp3", ".wav", ".aac", ".flac"],
        "video": [".mp4", ".mov", ".mkv", ".avi"],
        "animation": [".gif", ".apng"],
        "scientific": [
            ".fasta", ".fastq", ".vcf", ".mol", ".sdf", ".cml", ".smiles",
            ".pdb", ".mmcif", ".bam", ".sam", ".gff", ".ab1", ".tex",
            ".mathml", ".graphml", ".dot", ".gml"
        ],
        "ai_ml": [".pkl", ".pt", ".onnx", ".h5", ".ini", ".env", ".toml"],
    }

    for cat, exts in FILE_TYPE_MAP.items():
        if ext in exts:
            return cat
    return "files"  # safe default


# -------------------------
# Core create/decode
# -------------------------
async def create_context_from_upload(
    upload: UploadFile,
    collection_name: str = None,
    category_override: str = None,
    compress: bool = False,
):
    """Wrap file into ZIP, encode as PNG, register metadata, index, add entry."""
    context_id = uuid.uuid4().hex[:8]

    try:
        file_bytes = await upload.read()
        version_hash = generate_hash(file_bytes)

        # ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            compression = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
            with zipfile.ZipFile(tmp_zip.name, "w", compression=compression) as zf:
                zf.writestr(upload.filename, file_bytes)

            zip_path = Path(tmp_zip.name)
            zip_bytes = zip_path.read_bytes()
            zip_size = len(zip_bytes)
            zip_name_only = zip_path.name

        # PNG
        img = encode_binary_to_image(zip_bytes)
        image_name = f"ctx_{context_id}.png"
        image_path = BASE_DIR / image_name
        img.save(image_path)

        # metadata
        register_context(
            context_id=context_id,
            version_hash=version_hash,
            zip_name=zip_name_only,
            image_name=image_name,
            source_name=upload.filename,
            zip_len=zip_size,
        )

        # category
        category = category_override or detect_category_from_filename(upload.filename)

        # entry
        entry = {
            "file_name": upload.filename,
            "version_hash": version_hash,
            "zip_file": zip_name_only,
            "image_file": image_name,
            "metadata": None,
        }

        if collection_name:
            context_object.add_entry_to_collection(collection_name, category, context_id, entry)
        else:
            context_object.add_entry(category=category, entry_id=context_id, entry=entry)

        # index (non-fatal)
        try:
            index_context(
                context_id=context_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "original_filename": upload.filename,
                    "zip_file": zip_name_only,
                    "image_file": image_name,
                    "version_hash": version_hash,
                    "category": category,
                    "collection": collection_name or "default",
                    "compressed": compress,
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "context_id": context_id,
            "image_file": image_name,
            "version_hash": version_hash,
            "original_filename": upload.filename,
            "category": category,
            "collection": collection_name or "default",
            "compressed": compress,
            "entry_type": "file",
        }

    except Exception as e:
        return {"status": "error", "detail": str(e), "context_id": context_id}


async def create_context_from_raw(
    raw_data,
    collection_name: str = None,
    category_override: str = "raw",
    compress: bool = False,
):
    """Wrap raw text/JSON into ZIP → PNG → register metadata → index → add entry."""
    context_id = uuid.uuid4().hex[:8]

    try:
        # Convert dict to JSON string if needed
        if isinstance(raw_data, dict):
            raw_bytes = json.dumps(raw_data).encode("utf-8")
        elif isinstance(raw_data, str):
            raw_bytes = raw_data.encode("utf-8")
        else:
            raise ValueError("raw_data must be str or dict")

        version_hash = generate_hash(raw_bytes)

        # ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            compression = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
            with zipfile.ZipFile(tmp_zip.name, "w", compression=compression) as zf:
                zf.writestr("raw.txt", raw_bytes)

            zip_path = Path(tmp_zip.name)
            zip_bytes = zip_path.read_bytes()
            zip_size = len(zip_bytes)
            zip_name_only = zip_path.name

        # PNG
        img = encode_binary_to_image(zip_bytes)
        image_name = f"ctx_{context_id}.png"
        image_path = BASE_DIR / image_name
        img.save(image_path)

        # metadata
        register_context(
            context_id=context_id,
            version_hash=version_hash,
            zip_name=zip_name_only,
            image_name=image_name,
            source_name="raw_data",
            zip_len=zip_size,
        )

        # entry
        entry = {
            "file_name": "raw_data",
            "version_hash": version_hash,
            "zip_file": zip_name_only,
            "image_file": image_name,
            "metadata": None,
        }

        if collection_name:
            context_object.add_entry_to_collection(collection_name, category_override, context_id, entry)
        else:
            context_object.add_entry(category_override, context_id, entry)

        # index
        try:
            index_context(
                context_id=context_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "original_filename": "raw_data",
                    "zip_file": zip_name_only,
                    "image_file": image_name,
                    "version_hash": version_hash,
                    "category": category_override,
                    "collection": collection_name or "default",
                    "compressed": compress,
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "context_id": context_id,
            "image_file": image_name,
            "version_hash": version_hash,
            "original_filename": "raw_data",
            "category": category_override,
            "collection": collection_name or "default",
            "compressed": compress,
            "entry_type": "raw",
        }

    except Exception as e:
        return {"status": "error", "detail": str(e), "context_id": context_id}


async def decode_context_from_image_raw(image: UploadFile):
    """Decode a context PNG back to the original file(s)."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(await image.read())
            tmp_img.flush()
            temp_image_path = Path(tmp_img.name)

        decoded_bytes = decode_image_to_binary(str(temp_image_path))

        # Instead of trusting upload filename, use actual stored metadata
        # Get the first metadata entry whose image_name matches this file's content
        image_name = Path(image.filename).name
        zip_len = get_zip_length(image_name)
        if zip_len is None:
            return {"status": "error", "detail": f"Metadata not found for {image_name}"}

        zip_data = decoded_bytes[:zip_len]

        stem = Path(image_name).stem
        recovered_zip_path = EXTRACT_DIR / f"{stem}_recovered.zip"
        recovered_zip_path.write_bytes(zip_data)

        extracted_path = EXTRACT_DIR / f"extracted_{uuid.uuid4().hex[:8]}"
        extracted_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(BytesIO(zip_data), "r") as zip_ref:
            zip_ref.extractall(extracted_path)

        original_name = get_original_filename(image_name)

        raw_content = None
        if original_name == "raw_data":
            raw_file = extracted_path / "raw.txt"
            if raw_file.exists():
                raw_content = raw_file.read_text(encoding="utf-8")

        return {
            "status": "success",
            "recovered_zip": str(recovered_zip_path),
            "extracted_to": str(extracted_path),
            "original_filename": original_name,
            "restored_path": str(extracted_path),
            "entry_type": "raw" if original_name == "raw_data" else "file",
            "raw_content": raw_content,
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}



# -------------------------
# Bulk helpers
# -------------------------
async def bulk_create_context(uploads: list[UploadFile], collection_name: str = None, compress: bool = False):
    results = []
    for up in uploads:
        res = await create_context_from_upload(up, collection_name=collection_name, compress=compress)
        results.append(res)
    return results


async def create_context_for_collection(name: str, upload: UploadFile, compress: bool = False):
    return await create_context_from_upload(upload, collection_name=name, compress=compress)


async def bulk_create_context_for_collection(name: str, uploads: list[UploadFile], compress: bool = False):
    return await bulk_create_context(uploads, collection_name=name, compress=compress)


# -------------------------
# Combine contexts 
# -------------------------

async def create_context_from_multiple_uploads(
    uploads: list,
    collection_name: str = None,
    category_override: str = None,
    compress: bool = False,
):
    """
    Wrap multiple uploaded files into a single ZIP -> PNG -> register & index.
    Returns the same result shape as create_context_from_upload.
    """
    context_id = uuid.uuid4().hex[:8]
    try:
        # Create ZIP containing all uploads
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            compression = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
            with zipfile.ZipFile(tmp_zip.name, "w", compression=compression) as zf:
                for up in uploads:
                    # ensure read is awaited (UploadFile)
                    file_bytes = await up.read()
                    fname = up.filename or f"file_{uuid.uuid4().hex[:8]}"
                    zf.writestr(fname, file_bytes)

            zip_path = Path(tmp_zip.name)
            zip_bytes = zip_path.read_bytes()
            zip_size = len(zip_bytes)
            zip_name_only = zip_path.name

        # compute version hash
        version_hash = generate_hash(zip_bytes)

        # encode to PNG (reuse your helper)
        img = encode_binary_to_image(zip_bytes)
        image_name = f"ctx_{context_id}.png"
        image_path = BASE_DIR / image_name
        img.save(image_path)

        # register metadata
        register_context(
            context_id=context_id,
            version_hash=version_hash,
            zip_name=zip_name_only,
            image_name=image_name,
            source_name=";".join([up.filename or "" for up in uploads]),
            zip_len=zip_size,
        )

        # determine category (default archive)
        category = category_override or "archive"

        entry = {
            "file_name": ";".join([up.filename or "" for up in uploads]),
            "version_hash": version_hash,
            "zip_file": zip_name_only,
            "image_file": image_name,
            "metadata": None,
        }

        if collection_name:
            context_object.add_entry_to_collection(collection_name, category, context_id, entry)
        else:
            context_object.add_entry(category=category, entry_id=context_id, entry=entry)

        # index (non-fatal)
        try:
            index_context(
                context_id=context_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "original_filename": entry["file_name"],
                    "zip_file": zip_name_only,
                    "image_file": image_name,
                    "version_hash": version_hash,
                    "category": category,
                    "collection": collection_name or "default",
                    "compressed": compress,
                },
            )
        except Exception:
            pass

        return {
            "status": "success",
            "context_id": context_id,
            "image_file": image_name,
            "version_hash": version_hash,
            "original_filename": entry["file_name"],
            "category": category,
            "collection": collection_name or "default",
            "compressed": compress,
            "entry_type": "file-multi",
        }

    except Exception as e:
        return {"status": "error", "detail": str(e), "context_id": context_id}