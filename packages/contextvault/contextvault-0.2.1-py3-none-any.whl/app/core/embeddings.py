# app/core/embeddings.py
from __future__ import annotations
import json
import math
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

BASE = Path("data")
INDEX_DIR = BASE / "index"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
EMB_PATH = INDEX_DIR / "embeddings.jsonl"

# ---- persistence ----
def _append_embedding_record(record: Dict[str, Any]) -> None:
    with EMB_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def _load_all_embeddings() -> List[Dict[str, Any]]:
    if not EMB_PATH.exists():
        return []
    out = []
    with EMB_PATH.open("r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                out.append(json.loads(ln))
            except Exception:
                continue
    return out

# ---- helper: deterministic stub embedder ----
def compute_embedding_from_text(text: str, dim: int = 64) -> List[float]:
    """
    Deterministic embedding stub using SHA256 digest mapped into floats.
    Replace this function with a real model later.
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # expand digest into dim floats by repeating and slicing
    out = []
    b = h
    while len(out) < dim:
        # convert bytes to integers and normalize
        for i in range(0, len(b), 4):
            if len(out) >= dim:
                break
            chunk = b[i : i + 4]
            val = int.from_bytes(chunk, "big")
            # map to [-1, 1]
            out.append(((val % 1000000) / 1000000.0) * 2 - 1)
        b = hashlib.sha256(b).digest()
    # normalize to unit length
    norm = math.sqrt(sum(x * x for x in out)) or 1.0
    out = [x / norm for x in out]
    return out

# ---- indexing and search API ----
def index_vector(
    id: str,
    context_id: str,
    object_id: Optional[str],
    vector: List[float],
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Append an embedding record to the embeddings index.
    id: unique id for this vector (could be same as context_id or a separate id).
    """
    rec = {
        "id": id,
        "context_id": context_id,
        "object_id": object_id,
        "vector": vector,
        "meta": meta or {},
    }
    _append_embedding_record(rec)

def _cosine(a: List[float], b: List[float]) -> float:
    # assume both normalized (but protect)
    if not a or not b:
        return -1.0
    # dot / (||a|| * ||b||)
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)

def search_vector(query_vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
    """
    Return top_k records (id, context_id, object_id, score, meta).
    """
    all_recs = _load_all_embeddings()
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for rec in all_recs:
        vec = rec.get("vector")
        if not vec:
            continue
        # if lengths mismatch, skip
        if len(vec) != len(query_vector):
            continue
        score = _cosine(query_vector, vec)
        scored.append((score, rec))
    # sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    out = []
    for score, rec in scored[:top_k]:
        out.append(
            {
                "id": rec.get("id"),
                "context_id": rec.get("context_id"),
                "object_id": rec.get("object_id"),
                "score": float(score),
                "meta": rec.get("meta", {}),
            }
        )
    return out

# convenience: embed text then search
def embed_and_search_text(text: str, top_k: int = 10, dim: int = 64) -> List[Dict[str, Any]]:
    v = compute_embedding_from_text(text, dim=dim)
    return search_vector(v, top_k=top_k)
