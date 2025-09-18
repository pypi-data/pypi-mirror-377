# app/core/semantic.py
"""
Simple Semantic Vector index + search stub (pure-Python).

Purpose:
- Provide a minimal, safe API for indexing vectors and performing nearest-neighbour
  searches so other code/components can call vector APIs without depending on
  external libraries (FAISS, Annoy, Milvus, etc).
- Store vectors on-disk in a simple JSON format so they persist between runs.
- Provide an easy replacement point for a production vector backend later.

API:
- index_vectors(index_root: Path, shard: str, vectors: Dict[str, List[float]], ts: Optional[str] = None) -> Optional[Path]
    * vectors: mapping from doc_id -> vector (list of floats)
    * writes to: <index_root>/vectors/<shard>/v{ts}/vectors.json and meta.json
    * returns Path to created vdir or None on failure

- search_vectors(query: List[float], index_root: Path, shard: Optional[str] = None, top_k: int = 10) -> List[Tuple[str, float]]
    * If shard is None, searches across all shards under <index_root>/vectors
    * Returns list of (doc_id, score) ordered by descending similarity (cosine)
    * Pure-python: O(N * D) scan — OK for small dev datasets and tests.

Notes / Limitations:
- This is a stub: linear scan, JSON storage, no compression, not optimized for large corpora.
- Replaceable: later you can implement the same API with FAISS or a remote vector DB without changing call sites.
"""

from __future__ import annotations
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import threading
import logging
import tempfile
import os

log = logging.getLogger("semantic")

_lock = threading.RLock()


def _now_ts() -> str:
    return time.strftime("%Y%m%d%H%M%S", time.gmtime())


def _normalize_vector(vec: List[float]) -> List[float]:
    # ensure all entries are floats and compute normalization if needed
    return [float(x) for x in vec]


def _cosine_score(a: List[float], b: List[float]) -> float:
    # compute cosine similarity; if zero-vector return 0
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


def index_vectors(index_root: Path, shard: str, vectors: Dict[str, List[float]], ts: Optional[str] = None) -> Optional[Path]:
    """
    Index (persist) a batch of vectors for a shard.

    Writes:
      <index_root>/vectors/<shard>/v{ts}/vectors.json  (mapping id -> vector list)
      <index_root>/vectors/<shard>/v{ts}/meta.json     (metadata)

    Returns:
      Path to created vdir (Path) on success, or None on failure.
    """
    try:
        idxroot = Path(index_root) / "vectors"
        shard_root = idxroot / str(shard)
        shard_root.mkdir(parents=True, exist_ok=True)
        version = ts or _now_ts()
        vname = "v" + str(version)
        vdir = shard_root / vname
        # create a temp dir inside shard_root then rename for atomicity
        tmpdir = Path(tempfile.mkdtemp(prefix=f"{vname}.tmp.", dir=str(shard_root)))
        try:
            # normalize vectors
            normed: Dict[str, List[float]] = {}
            for docid, vec in vectors.items():
                normed[str(docid)] = _normalize_vector(list(vec))

            # write vectors.json atomically (via tmp file then replace)
            vec_path = tmpdir / "vectors.json"
            meta_path = tmpdir / "meta.json"
            vec_path.write_text(json.dumps(normed, ensure_ascii=False), encoding="utf-8")
            meta = {
                "shard": shard,
                "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "count": len(normed),
                "version": vname,
            }
            meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")

            # move tmpdir -> vdir
            if vdir.exists():
                # if exists, choose unique suffix to avoid overwriting
                vdir = shard_root / (vname + "-" + _now_ts())
            os.replace(str(tmpdir), str(vdir))
            return vdir
        except Exception:
            # cleanup tmpdir on failure
            try:
                if tmpdir.exists():
                    import shutil
                    shutil.rmtree(tmpdir)
            except Exception:
                pass
            raise
    except Exception:
        log.exception("index_vectors failed")
        return None


def _load_vectors_from_vdir(vdir: Path) -> Dict[str, List[float]]:
    vec_file = vdir / "vectors.json"
    if not vec_file.exists():
        return {}
    try:
        data = json.loads(vec_file.read_text(encoding="utf-8"))
        # ensure vectors are lists of floats
        return {str(k): [float(x) for x in v] for k, v in data.items()}
    except Exception:
        log.exception("failed loading vectors from %s", vdir)
        return {}


def search_vectors(query: List[float], index_root: Path, shard: Optional[str] = None, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    Linear-scan nearest neighbour search using cosine similarity.

    Args:
      query: list of floats
      index_root: Path to the index root (where 'vectors' lives)
      shard: optional shard id to restrict search
      top_k: number of top results to return

    Returns:
      List of tuples (doc_id, score) sorted by descending score.
    """
    q = _normalize_vector(list(query))
    idxroot = Path(index_root) / "vectors"
    if not idxroot.exists():
        return []

    candidates: List[Tuple[str, float]] = []
    with _lock:
        if shard:
            shard_dirs = [idxroot / str(shard)]
        else:
            shard_dirs = [p for p in idxroot.iterdir() if p.is_dir()]

        for s in shard_dirs:
            if not s.exists():
                continue
            # find latest vdir for shard (by name sort)
            vdirs = [p for p in s.iterdir() if p.is_dir() and p.name.startswith("v")]
            if not vdirs:
                continue
            vdirs.sort(key=lambda p: p.name, reverse=True)
            vdir = vdirs[0]
            vecs = _load_vectors_from_vdir(vdir)
            for docid, vec in vecs.items():
                score = _cosine_score(q, vec)
                if score > 0.0:
                    candidates.append((docid, score))

    # sort by score desc and return top_k
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[:top_k]
