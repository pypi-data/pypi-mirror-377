# tests/test_index_sqlite.py
import os
import json
import tempfile
import pytest

from app.core.index_sqlite import SQLiteIndex, init_db

def test_index_create_search_delete(tmp_path):
    db_path = str(tmp_path / "index.sqlite")
    # ensure db dir exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    idx = SQLiteIndex(db_path)

    # index some docs
    idx.index_document("doc1", "The quick brown fox jumps over the lazy dog", {"title": "Doc One"})
    idx.index_document("doc2", "Quick brown foxes are quick and active", {"title": "Doc Two"})
    idx.index_document("doc3", "An unrelated sentence about healthcare and medicine", {"title": "Health Doc"})

    stats = idx.list_index_stats()
    assert stats["doc_count"] == 3
    assert stats["term_count"] > 0
    assert stats["posting_count"] > 0

    # search for 'quick brown'
    results = idx.search_terms("quick brown", limit=10)
    assert isinstance(results, list)
    # doc1 and doc2 should appear; doc2 likely higher score due to term frequency
    doc_ids = [r["doc_id"] for r in results]
    assert "doc1" in doc_ids
    assert "doc2" in doc_ids

    # delete doc2 and ensure it's removed
    idx.delete_document("doc2")
    stats2 = idx.list_index_stats()
    assert stats2["doc_count"] == 2

    # Searching 'quick' should not return doc2
    results_after = idx.search_terms("quick", limit=10)
    doc_ids_after = [r["doc_id"] for r in results_after]
    assert "doc2" not in doc_ids_after

def test_index_overwrite(tmp_path):
    db_path = str(tmp_path / "index.sqlite")
    idx = SQLiteIndex(db_path)
    idx.index_document("d", "apple banana apple", {"t": "a"})
    res1 = idx.search_terms("apple")
    assert any(r["doc_id"] == "d" for r in res1)
    # overwrite with different content
    idx.index_document("d", "banana", {"t": "b"})
    res2 = idx.search_terms("apple")
    # after overwrite, apple should no longer be present in results
    assert not any(r["doc_id"] == "d" for r in res2)
    res3 = idx.search_terms("banana")
    assert any(r["doc_id"] == "d" for r in res3)
