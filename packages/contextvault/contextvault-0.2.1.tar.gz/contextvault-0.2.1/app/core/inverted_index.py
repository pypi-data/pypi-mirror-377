# app/core/inverted_index.py
"""
app/core/inverted_index.py

Inverted-index helpers used by IndexWorker and tests.

Key changes:
- Uses app.core.cache.cache as _INV_CACHE (so _INV_CACHE.stats() exists)
- _load_postings_into_cache uses _INV_CACHE.get/set for caching behavior
- read_postings_for_term returns PostingsResult list-like object with .stats
- write_inverted_to_disk returns a Path as tests expect
"""

from __future__ import annotations
import os
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator, Tuple, Union
import logging

from app.core.cache import cache as _INV_CACHE  # use the cache instance

log = logging.getLogger("inverted_index")


def _atomic_write_text(path: Path, text: str) -> None:
    dirpath = path.parent
    dirpath.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=str(dirpath))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                log.debug("fsync unavailable for file fd")
        try:
            dirfd = os.open(str(dirpath), os.O_DIRECTORY)
            try:
                os.fsync(dirfd)
            finally:
                os.close(dirfd)
        except Exception:
            log.debug("dir fsync not available for %s", dirpath)
        os.replace(tmp, str(path))
    finally:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except Exception:
                pass


def _normalize_term(t: str) -> str:
    if t is None:
        return ""
    return str(t).strip().lower()


def _tokenize_text(text: str) -> List[str]:
    if not text:
        return []
    return [tok.strip().lower() for tok in str(text).split() if tok.strip()]


def build_inverted_from_events(events_iter: Iterator[Dict[str, Any]]) -> Dict[str, List[str]]:
    inv: Dict[str, List[str]] = {}

    def _add(term: str, doc: str):
        if not term or not doc:
            return
        t = _normalize_term(term)
        lst = inv.setdefault(t, [])
        if doc not in lst:
            lst.append(doc)

    for ev in events_iter:
        try:
            if not isinstance(ev, dict):
                continue

            if ev.get("event") == "relationship_added":
                parent = ev.get("parent") or ev.get("parent_id")
                child = ev.get("child") or ev.get("child_id")
                if parent and child:
                    _add(parent, child)
                    title = ev.get("title") or ev.get("text")
                    if title:
                        for tok in _tokenize_text(title):
                            _add(tok, child)
                    continue

            if "term" in ev and ("doc_id" in ev or "doc" in ev):
                term = ev.get("term")
                doc = ev.get("doc_id") or ev.get("doc")
                _add(term, doc)
                continue

            if "text" in ev and "doc_id" in ev:
                text = ev.get("text") or ""
                doc = ev.get("doc_id")
                for token in _tokenize_text(text):
                    _add(token, doc)
                continue

            if "title" in ev and ("child" in ev or "child_id" in ev):
                doc = ev.get("child") or ev.get("child_id")
                for token in _tokenize_text(ev.get("title") or ""):
                    _add(token, doc)
                continue

            if "doc_id" in ev:
                doc = ev.get("doc_id")
                for k, v in ev.items():
                    if k == "doc_id":
                        continue
                    token = str(v)
                    _add(token, doc)
        except Exception:
            log.debug("skipping malformed event in build_inverted_from_events: %r", ev)
            continue

    return inv


def write_inverted_to_disk(inv: Dict[str, List[str]], out_root: Union[Path, str], shard: str, ts: Optional[str] = None) -> Optional[Path]:
    try:
        if isinstance(out_root, (str,)):
            out_root = Path(out_root)

        if ts is None:
            ts = time.strftime("%Y%m%d%H%M%S", time.gmtime())

        shard_root = out_root / str(shard)
        vdir = shard_root / ("v" + ts)
        vdir.mkdir(parents=True, exist_ok=True)

        inverted_json_path = vdir / "inverted.json"
        try:
            _atomic_write_text(inverted_json_path, json.dumps(inv, ensure_ascii=False, indent=2))
        except Exception:
            with open(inverted_json_path, "w", encoding="utf-8") as fh:
                json.dump(inv, fh, ensure_ascii=False, indent=2)

        postings_path = vdir / "postings.bin"
        fd, tmp_path = tempfile.mkstemp(prefix=".tmp_", dir=str(vdir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                for term, docs in inv.items():
                    obj = {"term": term, "postings": docs}
                    fh.write(json.dumps(obj, ensure_ascii=False) + "\n")
                fh.flush()
                try:
                    os.fsync(fh.fileno())
                except Exception:
                    log.debug("fsync unavailable for postings file")
            try:
                dirfd = os.open(str(vdir), os.O_DIRECTORY)
                try:
                    os.fsync(dirfd)
                finally:
                    os.close(dirfd)
            except Exception:
                log.debug("dir fsync not available for %s", vdir)
            os.replace(tmp_path, str(postings_path))
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        pointer_file = shard_root / "current_inverted"
        try:
            _atomic_write_text(pointer_file, vdir.name)
        except Exception:
            try:
                pointer_file.write_text(vdir.name, encoding="utf-8")
            except Exception:
                log.debug("failed to update current_inverted for shard %s", shard)

        log.info("Wrote inverted index for shard=%s at %s", shard, str(vdir))
        # store mapping in cache immediately for fast subsequent reads
        try:
            key = (str(shard_root.resolve()), vdir.name)
            _INV_CACHE.set(key, {k.lower(): list(v) for k, v in inv.items()})
        except Exception:
            pass

        return vdir
    except Exception as e:
        log.exception("write_inverted_to_disk failed: %s", e)
        return None


def _load_postings_into_cache(shard_root: Path, vdir_name: str) -> Dict[str, List[str]]:
    key = (str(shard_root.resolve()), vdir_name)
    # consult cache first
    cached = _INV_CACHE.get(key, None)
    if cached is not None:
        return cached

    mapping: Dict[str, List[str]] = {}
    vdir = shard_root / vdir_name
    postings_path = vdir / "postings.bin"
    if not postings_path.exists():
        inv_json = vdir / "inverted.json"
        if inv_json.exists():
            try:
                with open(inv_json, "r", encoding="utf-8") as fh:
                    mapping = json.load(fh)
                    mapping = {str(k).lower(): list(v) for k, v in mapping.items()}
            except Exception:
                mapping = {}
        _INV_CACHE.set(key, mapping)
        return mapping

    try:
        with open(postings_path, "r", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    obj = json.loads(ln)
                    term = _normalize_term(obj.get("term"))
                    postings = obj.get("postings") or []
                    mapping[term] = list(postings)
                except Exception:
                    continue
    except Exception:
        log.exception("failed to read postings file %s", postings_path)

    _INV_CACHE.set(key, mapping)
    return mapping


class PostingsResult(list):
    def __init__(self, seq: Optional[List[str]] = None):
        super().__init__(seq or [])
        self.stats: Dict[str, Any] = {}

    def with_stats(self, stats: Dict[str, Any]) -> "PostingsResult":
        self.stats = stats or {}
        return self


def read_postings_for_term(*args) -> PostingsResult:
    """
    Flexible signature:
      read_postings_for_term(shard_root_path: Path, term: str)
      read_postings_for_term(out_root: Path, shard: str, term: str)
    """
    shard_root: Optional[Path] = None
    term: Optional[str] = None

    if len(args) == 2:
        shard_root = Path(args[0])
        term = args[1]
    elif len(args) == 3:
        out_root = args[0]
        shard = args[1]
        term = args[2]
        if isinstance(out_root, (str,)):
            out_root = Path(out_root)
        shard_root = out_root / str(shard)
    else:
        raise TypeError("read_postings_for_term expects (shard_root, term) or (out_root, shard, term)")

    if term is None:
        return PostingsResult([]).with_stats({"count": 0})

    vdir_name = None
    pointer_file = shard_root / "current_inverted"
    if pointer_file.exists():
        try:
            vdir_name = pointer_file.read_text(encoding="utf-8").strip()
        except Exception:
            vdir_name = None

    if not vdir_name:
        try:
            dirs = [d for d in shard_root.iterdir() if d.is_dir() and d.name.startswith("v")]
            if dirs:
                dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                vdir_name = dirs[0].name
        except Exception:
            vdir_name = None

    if not vdir_name:
        return PostingsResult([]).with_stats({"count": 0})

    mapping = _load_postings_into_cache(shard_root, vdir_name)
    postings = mapping.get(_normalize_term(term), [])
    res = PostingsResult(list(postings))
    res.stats = {"count": len(res), "vdir": vdir_name}
    return res


__all__ = [
    "build_inverted_from_events",
    "write_inverted_to_disk",
    "read_postings_for_term",
    "_INV_CACHE",
    "PostingsResult",
]
