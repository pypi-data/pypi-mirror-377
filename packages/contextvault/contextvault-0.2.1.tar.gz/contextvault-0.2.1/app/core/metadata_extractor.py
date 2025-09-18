# app/core/metadata_extractor.py

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Optional libs (all guarded)
try:
    from PIL import Image, ExifTags
except Exception:
    Image = None
    ExifTags = None

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    import docx  # python-docx
except Exception:
    docx = None

try:
    import openpyxl
except Exception:
    openpyxl = None


@dataclass
class MetaResult:
    """Normalized metadata wrapper."""
    ok: bool
    kind: str
    meta: Dict[str, Any]
    warnings: Optional[list[str]] = None


# ---------- Public API ----------

def extract_metadata_from_bytes(
    filename: str,
    content: bytes,
    category_hint: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience entrypoint when you have bytes. We write to a temp file and delegate to _from_path.
    """
    suffix = Path(filename).suffix or ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = Path(tmp.name)

    try:
        return extract_metadata(tmp_path, category_hint=category_hint, original_name=filename)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def extract_metadata(
    file_path: Path | str,
    category_hint: Optional[str] = None,
    original_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main metadata extractor.
    Returns a dict; always safe to JSON-serialize. All exceptions are absorbed into `warnings`.
    """
    p = Path(file_path)
    ext = (p.suffix or "").lower()
    category = category_hint or _guess_category(ext)

    meta: Dict[str, Any] = {
        "filename": original_name or p.name,
        "size_bytes": p.stat().st_size if p.exists() else None,
        "category": category,
        "extension": ext,
        "warnings": [],
    }

    try:
        if category == "image":
            _merge(meta, _image_meta(p))
        elif category == "document":
            # prioritize PDF, fallback to DOCX
            if ext == ".pdf":
                _merge(meta, _pdf_meta(p))
            elif ext == ".docx":
                _merge(meta, _docx_meta(p))
            else:
                _merge(meta, _generic_textish_meta(p))
        elif category == "text":
            _merge(meta, _generic_textish_meta(p))
        elif category == "structured":
            if ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
                _merge(meta, _xlsx_meta(p))
            elif ext == ".csv":
                _merge(meta, _csv_meta(p))
            elif ext == ".json":
                _merge(meta, _json_meta(p))
            else:
                _merge(meta, _generic_textish_meta(p))
        elif category == "audio":
            _merge(meta, _ffprobe_meta(p, media_type="audio"))
        elif category == "video":
            _merge(meta, _ffprobe_meta(p, media_type="video"))
        elif category == "archive":
            _merge(meta, _archive_meta(p))
        else:
            # scientific/sql/ai_ml/ip/geolocation/unknown -> best effort text/json
            if ext == ".json":
                _merge(meta, _json_meta(p))
            else:
                _merge(meta, _generic_textish_meta(p))
    except Exception as e:
        meta["warnings"].append(f"extractor-error: {type(e).__name__}: {str(e)}")

    return meta


# ---------- Helpers / Extractors ----------

def _merge(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    for k, v in (src or {}).items():
        dst[k] = v


def _guess_category(ext: str) -> str:
    # Light guess; keep in sync with serializer’s detection
    if ext in (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif", ".tiff"):
        return "image" if ext != ".gif" else "animation"
    if ext in (".pdf", ".docx", ".odt"):
        return "document"
    if ext in (".txt", ".md", ".log"):
        return "text"
    if ext in (".csv", ".xls", ".xlsx", ".json", ".xml", ".yaml", ".yml"):
        return "structured"
    if ext in (".mp3", ".wav", ".aac", ".flac"):
        return "audio"
    if ext in (".mp4", ".mov", ".mkv", ".avi"):
        return "video"
    if ext in (".zip", ".tar", ".gz"):
        return "archive"
    return "unknown"


def _image_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "image"}
    if Image is None:
        out["warnings"] = ["Pillow not installed; limited metadata"]
        return out

    with Image.open(path) as im:
        out.update({
            "format": im.format,
            "mode": im.mode,
            "width": im.width,
            "height": im.height,
        })
        # EXIF
        try:
            exif_data = im._getexif() if hasattr(im, "_getexif") else None
            if exif_data:
                label = {ExifTags.TAGS.get(k, str(k)): v for k, v in exif_data.items()}
                out["exif"] = _safe_json(label)
        except Exception:
            pass
    return out


def _pdf_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "pdf"}
    if PdfReader is None:
        out["warnings"] = ["PyPDF2 not installed; limited PDF metadata"]
        return out
    reader = PdfReader(str(path))
    info = reader.metadata or {}
    out.update({
        "pages": len(reader.pages),
        "title": getattr(info, "title", None) or info.get("/Title"),
        "author": getattr(info, "author", None) or info.get("/Author"),
        "producer": getattr(info, "producer", None) or info.get("/Producer"),
        "creator": getattr(info, "creator", None) or info.get("/Creator"),
        "subject": getattr(info, "subject", None) or info.get("/Subject"),
    })
    return out


def _docx_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "docx"}
    if docx is None:
        out["warnings"] = ["python-docx not installed; limited DOCX metadata"]
        return out
    d = docx.Document(str(path))
    core = d.core_properties
    out.update({
        "title": core.title,
        "author": core.author,
        "last_modified_by": core.last_modified_by,
        "created": core.created.isoformat() if core.created else None,
        "modified": core.modified.isoformat() if core.modified else None,
        "subject": core.subject,
    })
    return out


def _xlsx_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "xlsx"}
    if openpyxl is None:
        out["warnings"] = ["openpyxl not installed; limited XLSX metadata"]
        return out
    wb = openpyxl.load_workbook(filename=str(path), read_only=True, data_only=True)
    sheets = {}
    for ws in wb.worksheets:
        # read-only mode: use dimensions if available
        try:
            dims = ws.calculate_dimension()
            # A1:Z20 → sizes are approximations; keep safe
            rows, cols = _dimension_to_counts(dims)
        except Exception:
            rows = cols = None
        sheets[ws.title] = {"rows": rows, "cols": cols}
    out["sheets"] = sheets
    try:
        props = wb.properties
        out["creator"] = props.creator
        out["created"] = props.created.isoformat() if props.created else None
    except Exception:
        pass
    return out


def _dimension_to_counts(dim: str) -> Tuple[Optional[int], Optional[int]]:
    # very rough: "A1:C10" -> rows=10, cols=3
    try:
        if ":" not in dim:
            return None, None
        left, right = dim.split(":")
        cols = _col_to_num(right.rstrip("0123456789")) - _col_to_num(left.rstrip("0123456789")) + 1
        r1 = int(''.join(filter(str.isdigit, left)))
        r2 = int(''.join(filter(str.isdigit, right)))
        rows = r2 - r1 + 1
        return rows, cols
    except Exception:
        return None, None


def _col_to_num(s: str) -> int:
    # "A"->1, "Z"->26, "AA"->27...
    total = 0
    for ch in s.upper():
        if 'A' <= ch <= 'Z':
            total = total * 26 + (ord(ch) - ord('A') + 1)
    return total


def _csv_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "csv"}
    try:
        import csv
        rows = 0
        cols = None
        with path.open("r", newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows += 1
                if i == 0:
                    cols = len(row)
        out.update({"rows": rows, "cols": cols})
    except Exception as e:
        out["warnings"] = [f"csv-error: {str(e)}"]
    return out


def _json_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "json"}
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        if isinstance(data, dict):
            out["keys"] = list(data.keys())[:50]
        elif isinstance(data, list):
            out["items"] = len(data)
        else:
            out["value_type"] = type(data).__name__
    except Exception as e:
        out["warnings"] = [f"json-error: {str(e)}"]
    return out


def _generic_textish_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "textish"}
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        out.update({
            "chars": len(text),
            "lines": text.count("\n") + 1 if text else 0,
            "sample_head": text[:200],
        })
    except Exception as e:
        out["warnings"] = [f"text-read-error: {str(e)}"]
    return out


def _archive_meta(path: Path) -> Dict[str, Any]:
    out = {"type": "archive"}
    try:
        import zipfile
        names = []
        with zipfile.ZipFile(str(path), "r") as zf:
            for zi in zf.infolist()[:50]:
                names.append(zi.filename)
        out["files_preview"] = names
        out["count"] = len(names)
    except Exception as e:
        out["warnings"] = [f"archive-error: {str(e)}"]
    return out


def _ffprobe_meta(path: Path, media_type: str) -> Dict[str, Any]:
    """
    Extract duration/codec/bitrate using ffprobe (if available).
    """
    out = {"type": media_type}
    try:
        cmd = [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", str(path)
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if proc.returncode == 0 and proc.stdout:
            j = json.loads(proc.stdout)
            fmt = j.get("format", {})
            out["duration"] = _safe_float(fmt.get("duration"))
            out["bit_rate"] = _safe_int(fmt.get("bit_rate"))
            # First relevant stream
            streams = j.get("streams", [])
            if streams:
                s0 = streams[0]
                out["codec_name"] = s0.get("codec_name")
                out["sample_rate"] = _safe_int(s0.get("sample_rate"))
                out["width"] = s0.get("width")
                out["height"] = s0.get("height")
        else:
            out.setdefault("warnings", []).append("ffprobe not available or failed")
    except FileNotFoundError:
        out.setdefault("warnings", []).append("ffprobe not installed")
    except Exception as e:
        out.setdefault("warnings", []).append(f"ffprobe-error: {str(e)}")
    return out


def _safe_int(x: Any) -> Optional[int]:
    try:
        return int(x)
    except Exception:
        return None


def _safe_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None


def _safe_json(obj: Any) -> Any:
    try:
        json.dumps(obj)  # will raise if not serializable
        return obj
    except Exception:
        return str(obj)
