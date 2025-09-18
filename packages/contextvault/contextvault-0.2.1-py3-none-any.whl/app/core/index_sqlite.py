# app/core/index_sqlite.py
"""
SQLite-backed inverted index for ContextVault.

Simple design:
- terms(term TEXT PRIMARY KEY, df INTEGER)
- postings(term TEXT, doc_id TEXT, positions TEXT, freq INTEGER)
- docs(doc_id TEXT PRIMARY KEY, metadata TEXT)

Positions are stored as comma-separated ints in the postings row.
Metadata stored as JSON string.

Provides:
- init_db(path)
- index_document(doc_id, text, metadata)
- delete_document(doc_id)
- search_terms(q, limit=50)
- list_index_stats()
"""

import sqlite3
import json
import math
import os
import threading
from typing import List, Dict, Tuple

_LOCK = threading.RLock()

def _connect(path: str):
    # allow multi-threaded access from tests/async contexts; callers should manage concurrency
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db(path: str):
    """Create database and tables if they don't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _LOCK:
        conn = _connect(path)
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS docs (
                doc_id TEXT PRIMARY KEY,
                metadata TEXT
            );

            CREATE TABLE IF NOT EXISTS terms (
                term TEXT PRIMARY KEY,
                df INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS postings (
                term TEXT,
                doc_id TEXT,
                positions TEXT,
                freq INTEGER,
                PRIMARY KEY (term, doc_id),
                FOREIGN KEY (term) REFERENCES terms(term),
                FOREIGN KEY (doc_id) REFERENCES docs(doc_id)
            );

            CREATE INDEX IF NOT EXISTS idx_postings_term ON postings(term);
            CREATE INDEX IF NOT EXISTS idx_postings_doc ON postings(doc_id);
            """
        )
        conn.commit()
        conn.close()

def _tokenize(text: str) -> List[Tuple[str, int]]:
    """
    Very small deterministic tokenizer:
    - lowercase
    - keep alphanumerics
    - split on non-alnum
    returns list of (token, position)
    """
    tokens = []
    pos = 0
    cur = []
    for ch in text:
        if ch.isalnum():
            cur.append(ch.lower())
        else:
            if cur:
                token = "".join(cur)
                tokens.append((token, pos))
                pos += 1
                cur = []
    if cur:
        token = "".join(cur)
        tokens.append((token, pos))
    return tokens

class SQLiteIndex:
    def __init__(self, path: str):
        self.path = path
        init_db(self.path)

    def _conn(self):
        return _connect(self.path)

    def index_document(self, doc_id: str, text: str, metadata: dict = None):
        """
        Index a document: tokenizes text, stores docs row, postings, and updates df.
        Overwrites existing doc if present.
        """
        metadata = metadata or {}
        tokens = _tokenize(text)
        # build term -> positions list
        term_positions = {}
        for token, pos in tokens:
            term_positions.setdefault(token, []).append(pos)

        with _LOCK:
            conn = self._conn()
            cur = conn.cursor()
            # Upsert docs row
            cur.execute("INSERT OR REPLACE INTO docs(doc_id, metadata) VALUES (?, ?)",
                        (doc_id, json.dumps(metadata)))
            # For existing doc, we must remove old postings and decrement df for affected terms.
            # Simpler: delete any existing postings for this doc, then re-add and recompute df for touched terms.
            # Find existing terms for doc
            cur.execute("SELECT term FROM postings WHERE doc_id = ?", (doc_id,))
            existing_terms = [r["term"] for r in cur.fetchall()]
            if existing_terms:
                for term in existing_terms:
                    # remove posting
                    cur.execute("DELETE FROM postings WHERE term = ? AND doc_id = ?", (term, doc_id))
                    # decrement df
                    cur.execute("UPDATE terms SET df = df - 1 WHERE term = ?", (term,))
                # cleanup any terms with df <= 0
                cur.execute("DELETE FROM terms WHERE df <= 0")

            # Insert new postings and update df
            for term, positions in term_positions.items():
                pos_str = ",".join(str(p) for p in positions)
                freq = len(positions)
                # insert posting
                cur.execute(
                    "INSERT OR REPLACE INTO postings(term, doc_id, positions, freq) VALUES (?, ?, ?, ?)",
                    (term, doc_id, pos_str, freq)
                )
                # upsert term df
                cur.execute(
                    "INSERT INTO terms(term, df) VALUES(?, 1) ON CONFLICT(term) DO UPDATE SET df = df + 1",
                    (term,)
                )
            conn.commit()
            conn.close()

    def delete_document(self, doc_id: str):
        """Delete a document and update term df accordingly."""
        with _LOCK:
            conn = self._conn()
            cur = conn.cursor()
            cur.execute("SELECT term FROM postings WHERE doc_id = ?", (doc_id,))
            terms = [r["term"] for r in cur.fetchall()]
            # remove postings
            cur.execute("DELETE FROM postings WHERE doc_id = ?", (doc_id,))
            # remove doc
            cur.execute("DELETE FROM docs WHERE doc_id = ?", (doc_id,))
            # decrement df for each term
            for term in terms:
                cur.execute("UPDATE terms SET df = df - 1 WHERE term = ?", (term,))
            cur.execute("DELETE FROM terms WHERE df <= 0")
            conn.commit()
            conn.close()

    def list_index_stats(self) -> dict:
        """Return basic stats: doc_count, term_count, total_postings."""
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as cnt FROM docs")
        doc_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM terms")
        term_count = cur.fetchone()["cnt"]
        cur.execute("SELECT COUNT(*) as cnt FROM postings")
        postings = cur.fetchone()["cnt"]
        conn.close()
        return {
            "doc_count": doc_count,
            "term_count": term_count,
            "posting_count": postings
        }

    def _get_total_docs(self, cur) -> int:
        cur.execute("SELECT COUNT(*) as cnt FROM docs")
        return cur.fetchone()["cnt"]

    def search_terms(self, q: str, limit: int = 50) -> List[Dict]:
        """
        Search query q (simple term query, supports multiple terms).
        Returns list of dicts: {doc_id, score, snippets?}
        Uses a simple TF-IDF-ish score:
           score(doc) = sum_over_terms( tf * log(1 + N / (1 + df)) )
        """
        tokens = [t for t, _ in _tokenize(q)]
        if not tokens:
            return []

        with _LOCK:
            conn = self._conn()
            cur = conn.cursor()
            N = self._get_total_docs(cur) or 1

            # Gather postings for each term
            doc_scores = {}
            doc_positions = {}
            for term in tokens:
                cur.execute("SELECT df FROM terms WHERE term = ?", (term,))
                row = cur.fetchone()
                df = row["df"] if row else 0
                # get postings
                cur.execute("SELECT doc_id, positions, freq FROM postings WHERE term = ?", (term,))
                rows = cur.fetchall()
                idf = math.log(1.0 + (N / (1 + df))) if df > 0 else math.log(1.0 + N)
                for r in rows:
                    doc_id = r["doc_id"]
                    tf = r["freq"]
                    score = tf * idf
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + score
                    # store positions for snippet generation
                    doc_positions.setdefault(doc_id, {})[term] = r["positions"]
            # convert to sorted list
            results = []
            if not doc_scores:
                conn.close()
                return []
            # optionally fetch metadata/title/snippet
            for doc_id, score in sorted(doc_scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]:
                cur.execute("SELECT metadata FROM docs WHERE doc_id = ?", (doc_id,))
                row = cur.fetchone()
                meta = json.loads(row["metadata"]) if row and row["metadata"] else {}
                results.append({
                    "doc_id": doc_id,
                    "score": float(score),
                    "metadata": meta,
                    "term_positions": doc_positions.get(doc_id, {})
                })
            conn.close()
            return results
