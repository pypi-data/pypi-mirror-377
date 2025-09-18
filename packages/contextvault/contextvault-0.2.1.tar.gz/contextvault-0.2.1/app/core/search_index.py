# app/core/search_index.py
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Iterator, Optional
from collections import defaultdict, Counter
from datetime import datetime

from app.core.search import _tokenize

# Default index root
INDEX_ROOT = Path("data") / "index" / "inverted"

def _ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


class InvertedIndexBuilder:
    """
    Build an inverted index from contexts in a contexts_dir.
    Produces a directory: data/index/inverted/v{ts}/ with:
      - manifest.json
      - lexicon.json  (term -> postings_filename)
      - postings/<term_slug>.jsonl  (each line: {"context_id": "ctx1", "tf": N})

    This is intentionally simple and readable; you can swap to binary formats later.
    """

    def __init__(self, contexts_dir: Path = Path("data") / "contexts", out_root: Path = INDEX_ROOT):
        self.contexts_dir = Path(contexts_dir)
        self.out_root = Path(out_root)

    def _iter_contexts(self) -> Iterator[Tuple[str, Path, Optional[str]]]:
        """Yield (context_id, path, text) where path is json or text file. Text may be None."""
        if not self.contexts_dir.exists():
            return
        # flat json files
        for p in self.contexts_dir.glob("*.json"):
            ctx_id = p.stem
            yield ctx_id, p, None
        # nested dirs
        for ctx_dir in self.contexts_dir.iterdir():
            if not ctx_dir.is_dir():
                continue
            ctx_id = ctx_dir.name
            # meta.json
            meta = ctx_dir / "meta.json"
            if meta.exists():
                yield ctx_id, meta, None
            # content files
            for name in ("content.txt", "content.md", "body.txt", "body.md"):
                f = ctx_dir / name
                if f.exists():
                    yield ctx_id, f, None
            # any txt/md
            for f in ctx_dir.glob("*.txt"):
                yield ctx_id, f, None
            for f in ctx_dir.glob("*.md"):
                yield ctx_id, f, None

    def _read_text(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    def build(self) -> Tuple[Path, Dict]:
        """Build index and return (dest_dir, manifest)

        Manifest includes term_count and context_count.
        """
        # collect token -> Counter(context_id -> tf)
        postings: Dict[str, Counter] = defaultdict(Counter)
        ctx_count = 0
        for ctx_id, path, _ in self._iter_contexts():
            # read content depending on file
            txt = ""
            if path.suffix.lower() in (".json",):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    # join string fields heuristically
                    fields = []
                    for k, v in data.items():
                        if isinstance(v, str):
                            fields.append(v)
                    txt = "\n".join(fields)
                except Exception:
                    txt = ""
            else:
                txt = self._read_text(path)

            if not txt:
                continue
            ctx_count += 1
            tokens = _tokenize(txt)
            tf = Counter(tokens)
            for tok, cnt in tf.items():
                postings[tok][ctx_id] = cnt

        # write index
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dest = self.out_root / f"v{ts}"
        postings_dir = dest / "postings"
        _ensure_dir(postings_dir)

        lexicon = {}
        for term, counter in postings.items():
            # slugify term for filename
            slug = re.sub(r"[^a-z0-9_-]", "_", term.lower())
            fname = f"{slug}.jsonl"
            ppath = postings_dir / fname
            with ppath.open("w", encoding="utf-8") as f:
                for ctx_id, tf in counter.items():
                    f.write(json.dumps({"context_id": ctx_id, "tf": int(tf)}) + "\n")
            lexicon[term] = str(Path("postings") / fname)

        manifest = {
            "version": ts,
            "created": datetime.utcnow().isoformat() + "Z",
            "term_count": len(lexicon),
            "context_count": ctx_count,
        }
        (dest / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (dest / "lexicon.json").write_text(json.dumps(lexicon, ensure_ascii=False), encoding="utf-8")

        return dest, manifest


class InvertedIndexReader:
    """Read an inverted index. Does not load all postings into memory — it streams per-term postings from files.

    Usage:
      reader = InvertedIndexReader(index_root)
      reader.reload_if_new()
      results = reader.query_term('invoice') -> list of (context_id, tf)
    """

    def __init__(self, index_root: Path = INDEX_ROOT):
        self.index_root = Path(index_root)
        self.current_ptr: Optional[str] = None
        self.lexicon: Dict[str, str] = {}
        self._base_dir: Optional[Path] = None

        # simple LRU cache for hot postings (term -> list[(ctx,tf)])
        self._cache: Dict[str, List[Tuple[str, int]]] = {}
        self._cache_size = 1024
        self.reload_if_new()

    def _read_current_pointer(self) -> Optional[str]:
        ptr = self.index_root / "current"
        if ptr.exists():
            try:
                return ptr.read_text(encoding="utf-8").strip()
            except Exception:
                return None
        # fallback: pick latest v*
        if not self.index_root.exists():
            return None
        candidates = sorted([p.name for p in self.index_root.iterdir() if p.is_dir() and p.name.startswith("v")], reverse=True)
        return candidates[0] if candidates else None

    def _load_index_dir(self, dir_name: str):
        base = self.index_root / dir_name
        lex = {}
        lex_path = base / "lexicon.json"
        if lex_path.exists():
            try:
                lex = json.loads(lex_path.read_text(encoding="utf-8"))
            except Exception:
                lex = {}
        self.lexicon = lex
        self._base_dir = base
        self.current_ptr = dir_name

    def reload_if_new(self):
        new_ptr = self._read_current_pointer()
        if new_ptr and new_ptr != self.current_ptr:
            try:
                self._load_index_dir(new_ptr)
            except Exception:
                return

    def _read_postings(self, relpath: str) -> List[Tuple[str, int]]:
        if not self._base_dir:
            return []
        p = self._base_dir / relpath
        if not p.exists():
            return []
        # caching
        if relpath in self._cache:
            return self._cache[relpath]
        res = []
        with p.open("r", encoding="utf-8") as f:
            for ln in f:
                try:
                    j = json.loads(ln)
                    res.append((j.get("context_id"), int(j.get("tf", 0))))
                except Exception:
                    continue
        # update cache LRU simple policy
        if len(self._cache) >= self._cache_size:
            # pop an arbitrary key (not true LRU to keep code simple)
            self._cache.pop(next(iter(self._cache)))
        self._cache[relpath] = res
        return res

    def query_term(self, term: str) -> List[Tuple[str, int]]:
        self.reload_if_new()
        if not term:
            return []
        rel = self.lexicon.get(term)
        if not rel:
            return []
        return self._read_postings(rel)

    def query_multiterm(self, terms: List[str], max_results: int = 50) -> List[Dict]:
        # naive merge: sum tf scores across terms
        agg: Dict[str, int] = {}
        for t in terms:
            rows = self.query_term(t)
            for ctx_id, tf in rows:
                agg[ctx_id] = agg.get(ctx_id, 0) + tf
        items = sorted(agg.items(), key=lambda x: (-x[1], x[0]))
        return [{"context_id": k, "score": v} for k, v in items[:max_results]]
