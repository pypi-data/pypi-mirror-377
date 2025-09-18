# app/core/indexer.py
"""
Combined indexer with JSON + optional sqlite backend.
Uses lazy audit getter get_audit() from app.core.audit_log so env changes are honored.

This file was updated to:
- store snapshots in Content-Addressed Storage (CAS) via app.core.storage_cas
- compute/set version_hash for contexts when snapshot bytes are available
- provide verify_context_snapshot(context_id) helper to validate stored snapshot integrity
- keep CAS files immutable (delete_context removes only index entry)
"""

import os
import json
import math
import base64
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Any, Optional

# CAS helper (new)
from app.core.storage_cas import save_snapshot, verify_snapshot, snapshot_path_for_hash

# --- file indexes (unchanged) ---
FILES_INDEX = Path("data/index/genai_index.json")
SNAPSHOT_INDEX = Path("data/index/contextobj_index.json")
FILES_INDEX.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Utilities (unchanged)
# -----------------------------
def _load_json(path: Path) -> dict:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    out, buf = [], []
    for ch in text.lower():
        if ch.isalnum():
            buf.append(ch)
        else:
            if buf:
                out.append("".join(buf))
                buf = []
    if buf:
        out.append("".join(buf))
    return out

def _tf_vector(text: str) -> Dict[str, float]:
    toks = _tokenize(text)
    if not toks:
        return {}
    c = Counter(toks)
    total = sum(c.values())
    return {k: v / total for k, v in c.items()}

def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(t, 0.0) * b.get(t, 0.0) for t in set(a) | set(b))
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)

# -----------------------------
# Lazy audit getter
# -----------------------------
try:
    from app.core.audit_log import get_audit
except Exception:
    def get_audit():
        class _Noop:
            def append(self, *a, **kw): pass
            def tail(self, *a, **kw): return []
        return _Noop()

# -----------------------------
# Optional sqlite backend connector
# -----------------------------
_INDEX_BACKEND = os.environ.get("INDEX_BACKEND", "").lower()
_USE_SQLITE = _INDEX_BACKEND == "sqlite"
_sqlite_available = False
_sqlite_index_document = None
_sqlite_delete_document = None
_sqlite_search_terms = None
_sqlite_list_stats = None

if _USE_SQLITE:
    try:
        from app.core.index_sqlite import SQLiteIndex
        SQLITE_PATH = os.environ.get("INDEX_SQLITE_PATH", "data/index/index.sqlite")
        _sqlite_impl = SQLiteIndex(SQLITE_PATH)
        _sqlite_available = True

        def _sqlite_index_document(doc_id: str, text: str, metadata: dict = None):
            return _sqlite_impl.index_document(doc_id, text, metadata)

        def _sqlite_delete_document(doc_id: str):
            return _sqlite_impl.delete_document(doc_id)

        def _sqlite_search_terms(q: str, limit: int = 50):
            return _sqlite_impl.search_terms(q, limit=limit)

        def _sqlite_list_stats():
            return _sqlite_impl.list_index_stats()

        _sqlite_index_document = _sqlite_index_document
        _sqlite_delete_document = _sqlite_delete_document
        _sqlite_search_terms = _sqlite_search_terms
        _sqlite_list_stats = _sqlite_list_stats

    except Exception:
        _sqlite_available = False

def _sqlite_enabled() -> bool:
    return _USE_SQLITE and _sqlite_available

# -----------------------------
# Public: per-file indexing (uses lazy audit)
# -----------------------------
def index_context(context_id: str, metadata: dict):
    """
    Index a context and store snapshot in CAS (if snapshot bytes available).

    metadata can contain:
      - entry_type: "file" | "raw"
      - raw_content: str (for raw entries)
      - file_bytes_b64: base64-encoded bytes for the uploaded file (if API provides bytes)
      - original_filename, category, collection, timestamp, tags, summary, etc.

    This function:
      - attempts to obtain snapshot bytes from metadata
      - saves snapshot to CAS and sets version_hash = sha256
      - writes index JSON entry
      - indexes into sqlite if enabled
      - writes audit entries
    """
    index_data = _load_json(FILES_INDEX)

    entry_type = metadata.get("entry_type", "file")
    raw_content = metadata.get("raw_content")

    # Try to obtain bytes for snapshot
    file_bytes: Optional[bytes] = None
    fb64 = metadata.get("file_bytes_b64")
    if fb64:
        try:
            file_bytes = base64.b64decode(fb64)
        except Exception:
            file_bytes = None

    # If raw content provided and no file bytes, use UTF-8 bytes of raw_content
    if file_bytes is None and entry_type == "raw" and raw_content is not None:
        try:
            file_bytes = str(raw_content).encode("utf-8")
        except Exception:
            file_bytes = None

    version_hash = metadata.get("version_hash")

    # If we have snapshot bytes, save to CAS and set version_hash
    if file_bytes is not None:
        try:
            version_hash = save_snapshot(file_bytes)
        except Exception:
            # fallback: keep provided version_hash if any
            version_hash = metadata.get("version_hash")

    emb_text_parts = [
        str(metadata.get("original_filename", "")),
        str(metadata.get("category", "")),
        str(metadata.get("collection", "")),
    ]
    if entry_type == "raw" and raw_content:
        emb_text_parts.append(str(raw_content))

    emb_text = " ".join(emb_text_parts)
    emb_vec = _tf_vector(emb_text)

    # Build index entry (unified shape)
    entry = {
        "context_id": context_id,
        "timestamp": metadata.get("timestamp"),
        "source_filename": metadata.get("original_filename"),
        "zip_file": metadata.get("zip_file"),
        # store image_file as CAS path if version_hash present
        "image_file": str(snapshot_path_for_hash(version_hash)) if version_hash else metadata.get("image_file"),
        "version_hash": version_hash,
        "category": metadata.get("category"),
        "collection": metadata.get("collection"),
        "entry_type": entry_type,
        "tags": metadata.get("tags", []),
        "summary": metadata.get("summary"),
        "embedding": emb_vec,
    }

    if entry_type == "raw" and raw_content:
        entry["raw_content"] = raw_content

    # persist JSON index (primary)
    try:
        index_data[context_id] = entry
        _save_json(FILES_INDEX, index_data)
        try:
            get_audit().append({
                "actor": "system",
                "action": "index_context",
                "context_id": context_id,
                "backend": "json",
                "version_hash": version_hash,
                "status": "ok"
            })
        except Exception:
            pass
    except Exception as e:
        try:
            get_audit().append({
                "actor": "system",
                "action": "index_context",
                "context_id": context_id,
                "backend": "json",
                "status": "error",
                "error": str(e)
            })
        except Exception:
            pass
        raise

    # optional sqlite indexing (keyword)
    if _sqlite_enabled():
        try:
            parts = [
                str(entry.get("source_filename", "")),
                str(entry.get("category", "")),
                str(entry.get("collection", "")),
                str(entry.get("version_hash", "")),
            ]
            if entry_type == "raw" and entry.get("raw_content"):
                parts.append(str(entry.get("raw_content")))
            text_to_index = " ".join(parts)
            _sqlite_index_document(context_id, text_to_index, metadata)
            try:
                get_audit().append({
                    "actor": "system",
                    "action": "index_context",
                    "context_id": context_id,
                    "backend": "sqlite",
                    "version_hash": version_hash,
                    "status": "ok"
                })
            except Exception:
                pass
        except Exception as e:
            try:
                get_audit().append({
                    "actor": "system",
                    "action": "index_context",
                    "context_id": context_id,
                    "backend": "sqlite",
                    "status": "error",
                    "error": str(e)
                })
            except Exception:
                pass

# -----------------------------
# Public: delete context (CAS-aware)
# -----------------------------
def delete_context(context_id: str) -> bool:
    """
    Delete context metadata (index). CAS files are immutable and are NOT removed by this call.
    To remove CAS blobs, run a separate admin GC/migration.
    """
    idx = _load_json(FILES_INDEX)
    if context_id not in idx:
        try:
            get_audit().append({
                "actor": "system",
                "action": "delete_context",
                "context_id": context_id,
                "status": "missing"
            })
        except Exception:
            pass
        return False

    try:
        # remove from JSON index only
        entry = idx.pop(context_id, None)
        _save_json(FILES_INDEX, idx)
        try:
            get_audit().append({
                "actor": "system",
                "action": "delete_context",
                "context_id": context_id,
                "version_hash": (entry or {}).get("version_hash"),
                "backend": "json",
                "status": "ok"
            })
        except Exception:
            pass
    except Exception as e:
        try:
            get_audit().append({
                "actor": "system",
                "action": "delete_context",
                "context_id": context_id,
                "backend": "json",
                "status": "error",
                "error": str(e)
            })
        except Exception:
            pass
        raise

    if _sqlite_enabled():
        try:
            _sqlite_delete_document(context_id)
            try:
                get_audit().append({
                    "actor": "system",
                    "action": "delete_context",
                    "context_id": context_id,
                    "backend": "sqlite",
                    "status": "ok"
                })
            except Exception:
                pass
        except Exception as e:
            try:
                get_audit().append({
                    "actor": "system",
                    "action": "delete_context",
                    "context_id": context_id,
                    "backend": "sqlite",
                    "status": "error",
                    "error": str(e)
                })
            except Exception:
                pass

    return True

# -----------------------------
# Helper: verify snapshot integrity for a context
# -----------------------------
def verify_context_snapshot(context_id: str) -> Tuple[bool, str]:
    """
    Verify that the CAS snapshot for the given context matches the stored version_hash.

    Returns (ok: bool, message: str)
    - ok == True means snapshot exists and hash matched
    - ok == False means missing or mismatch; message explains reason
    """
    files = _load_json(FILES_INDEX)
    rec = files.get(context_id)
    if not rec:
        return False, "context not found in index"

    vh = rec.get("version_hash")
    if not vh:
        return False, "no version_hash available"

    # verify CAS file exists and hash matches
    try:
        ok = verify_snapshot(vh)
        if ok:
            return True, "ok"
        else:
            try:
                get_audit().append({
                    "actor": "system",
                    "action": "verify_context_snapshot",
                    "context_id": context_id,
                    "version_hash": vh,
                    "status": "mismatch"
                })
            except Exception:
                pass
            return False, "hash mismatch or missing file"
    except Exception as e:
        try:
            get_audit().append({
                "actor": "system",
                "action": "verify_context_snapshot",
                "context_id": context_id,
                "version_hash": vh,
                "status": "error",
                "error": str(e)
            })
        except Exception:
            pass
        return False, f"error: {e}"

# -----------------------------
# Snapshots, searches, semantics (unchanged)
# -----------------------------
def index_context_object_snapshot(version_hash: str, snapshot_meta: dict, context_doc: dict) -> None:
    idx = _load_json(SNAPSHOT_INDEX)

    text_parts = [
        f"version:{version_hash}",
        f"collections:{snapshot_meta.get('collections')}",
        f"total_entries:{snapshot_meta.get('total_entries')}",
    ]
    try:
        for col in context_doc.get("collections", []):
            text_parts.append(str(col.get("name", "")))
            for cat in (col.get("entries", {}) or {}).keys():
                text_parts.append(str(cat))
    except Exception:
        pass

    text = " ".join(text_parts)
    emb = _tf_vector(text)

    idx[version_hash] = {
        "version_hash": version_hash,
        "timestamp": snapshot_meta.get("timestamp"),
        "snapshot_image": snapshot_meta.get("snapshot_image"),
        "collections": snapshot_meta.get("collections"),
        "total_entries": snapshot_meta.get("total_entries"),
        "embedding": emb,
    }
    _save_json(SNAPSHOT_INDEX, idx)

def search_index(query: str) -> dict:
    q = query.strip().lower()

    if _sqlite_enabled():
        try:
            results = _sqlite_search_terms(q, limit=100) or []
        except Exception:
            results = []

        file_hits = []
        for r in results:
            doc_id = r.get("doc_id")
            meta = r.get("metadata", {}) or {}
            rec = {"context_id": doc_id, **meta}
            rec["_keyword_score"] = r.get("score")
            rec["_term_positions"] = r.get("term_positions", {})
            file_hits.append(rec)

        snaps = _load_json(SNAPSHOT_INDEX)
        snap_hits = []
        for vh, rec in snaps.items():
            hay = f"{vh} {rec.get('snapshot_image','')}".lower()
            if q in hay:
                snap_hits.append({"version_hash": vh, **rec})

        return {"files": file_hits, "snapshots": snap_hits}

    files = _load_json(FILES_INDEX)
    snaps = _load_json(SNAPSHOT_INDEX)

    file_hits = []
    for cid, rec in files.items():
        hay = " ".join(
            str(rec.get(k, "")) for k in ["source_filename", "zip_file", "image_file", "version_hash"]
        ).lower()

        matched = False
        if q in hay:
            matched = True

        if not matched and rec.get("entry_type") == "raw":
            rc = str(rec.get("raw_content", "")).lower()
            if q in rc:
                matched = True
                rec = {**rec, "match_in_raw": True}

        if matched:
            file_hits.append({"context_id": cid, **rec})

    snap_hits = []
    for vh, rec in snaps.items():
        hay = f"{vh} {rec.get('snapshot_image','')}".lower()
        if q in hay:
            snap_hits.append({"version_hash": vh, **rec})

    return {"files": file_hits, "snapshots": snap_hits}

def semantic_search(q: str, scope: str = "all", top_k: int = 10) -> dict:
    q_vec = _tf_vector(q)

    results: List[Tuple[float, str, dict]] = []

    if scope in ("files", "all"):
        files = _load_json(FILES_INDEX)
        for cid, rec in files.items():
            score = _cosine(q_vec, rec.get("embedding") or {})
            if score > 0:
                results.append((score, "file", {"context_id": cid, **rec}))

    if scope in ("snapshots", "all"):
        snaps = _load_json(SNAPSHOT_INDEX)
        for vh, rec in snaps.items():
            score = _cosine(q_vec, rec.get("embedding") or {})
            if score > 0:
                results.append((score, "snapshot", {"version_hash": vh, **rec}))

    results.sort(key=lambda x: x[0], reverse=True)
    results = results[: max(1, int(top_k))]

    return {
        "query": q,
        "scope": scope,
        "results": [
            {"score": round(score, 4), "type": kind, "record": rec}
            for score, kind, rec in results
        ],
    }

def list_index_stats() -> Dict[str, Any]:
    if _sqlite_enabled():
        try:
            return _sqlite_list_stats() or {}
        except Exception:
            pass

    files = _load_json(FILES_INDEX)
    snaps = _load_json(SNAPSHOT_INDEX)
    return {
        "doc_count": len(files),
        "snapshot_count": len(snaps),
    }
