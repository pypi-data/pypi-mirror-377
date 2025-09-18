# app/core/search.py
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import re

# Default contexts directory (can be patched in tests)
DATA_DIR = Path("data")
DATA_CONTEXTS_DIR = DATA_DIR / "contexts"

def _iter_context_files(contexts_dir: Path = DATA_CONTEXTS_DIR):
    """
    Yield (context_id, path) tuples for files that look like context metadata or text content.
    Accepts:
      - data/contexts/<ctx_id>/meta.json
      - data/contexts/<ctx_id>/content.txt or *.md
      - data/contexts/<ctx_id>.json (flat layout)
    """
    if not contexts_dir.exists():
        return
    # flat json files
    for p in contexts_dir.glob("*.json"):
        ctx_id = p.stem
        yield ctx_id, p
    # nested dirs
    for ctx_dir in contexts_dir.iterdir():
        if not ctx_dir.is_dir():
            continue
        ctx_id = ctx_dir.name
        # look for meta.json
        meta = ctx_dir / "meta.json"
        if meta.exists():
            yield ctx_id, meta
        # common content files
        for name in ("content.txt", "content.md", "body.txt", "body.md"):
            f = ctx_dir / name
            if f.exists():
                yield ctx_id, f
        # any .txt/.md file
        for f in ctx_dir.glob("*.txt"):
            yield ctx_id, f
        for f in ctx_dir.glob("*.md"):
            yield ctx_id, f

def _read_text_file(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

def _read_json_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def _tokenize(text: str) -> List[str]:
    # simple word tokenizer, lowercase
    return re.findall(r"\w+", text.lower())

def _score_text_match(text: str, query_tokens: List[str]) -> int:
    if not text:
        return 0
    tokens = _tokenize(text)
    # count occurrences of query tokens
    score = 0
    for qt in query_tokens:
        score += tokens.count(qt)
    return score

def keyword_search(query: str, contexts_dir: Path = DATA_CONTEXTS_DIR, max_results: int = 50) -> List[Dict[str, Any]]:
    """
    Keyword search across metadata JSON and plain text content.
    Returns a list of matches: {"context_id": str, "score": int, "match_fields": {...}}
    """
    q = (query or "").strip()
    if not q:
        return []

    q_tokens = _tokenize(q)
    matches: List[Tuple[int, str, Dict[str, Any]]] = []  # (score, ctx_id, details)

    for ctx_id, path in _iter_context_files(contexts_dir):
        score = 0
        details: Dict[str, Any] = {"matched_in": []}
        if path.suffix.lower() in (".json",):
            data = _read_json_file(path)
            if isinstance(data, dict):
                # search in top-level string fields
                for k, v in data.items():
                    if isinstance(v, str):
                        s = _score_text_match(v, q_tokens)
                        if s > 0:
                            score += s
                            details["matched_in"].append({"field": k, "score": s})
                # also attempt to search in nested text under 'metadata'/'description'
                for field in ("description", "text", "content"):
                    val = data.get(field)
                    if isinstance(val, str):
                        s = _score_text_match(val, q_tokens)
                        if s > 0:
                            score += s
                            details["matched_in"].append({"field": field, "score": s})
        else:
            # treat as plain text
            txt = _read_text_file(path) or ""
            s = _score_text_match(txt, q_tokens)
            if s > 0:
                score += s
                details["matched_in"].append({"field": path.name, "score": s})

        # add filename/context-id matches (higher boost)
        if any(tok in ctx_id.lower() for tok in q_tokens):
            score += 3
            details["matched_in"].append({"field": "context_id", "score": 3})

        if score > 0:
            matches.append((score, ctx_id, details))

    # sort by score desc
    matches.sort(key=lambda x: (-x[0], x[1]))
    results = []
    for sc, cid, det in matches[:max_results]:
        results.append({"context_id": cid, "score": sc, "details": det})
    return results

def semantic_search_placeholder(text: str) -> Dict[str, Any]:
    """
    Placeholder for semantic/vector search. Returns 501-style response body.
    Keep signature so tests and clients can be wired later.
    """
    return {"error": "semantic search not implemented", "requested_text": text}
