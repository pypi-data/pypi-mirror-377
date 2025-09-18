# tests/test_health_consistency.py
import os
import importlib
import json
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient

def test_health_consistency(tmp_path, monkeypatch):
    # create a small sqlite and json index to compare
    json_path = tmp_path / "genai_index.json"
    sqlite_path = tmp_path / "index.sqlite"

    # create json index with two docs
    data = {
        "d1": {"source_filename": "a.txt"},
        "d2": {"source_filename": "b.txt"}
    }
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    # create sqlite docs table with only d1
    import sqlite3
    conn = sqlite3.connect(str(sqlite_path))
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE docs (doc_id TEXT PRIMARY KEY, metadata TEXT);
    """)
    cur.execute("INSERT INTO docs (doc_id, metadata) VALUES (?, ?)", ("d1", '{"source_filename":"a.txt"}'))
    conn.commit()
    conn.close()

    # point env vars
    monkeypatch.setenv("FILES_INDEX_PATH", str(json_path))
    monkeypatch.setenv("INDEX_SQLITE_PATH", str(sqlite_path))

    # reload health module to pick new env values if necessary
    if "app.api.health" in importlib.sys.modules:
        importlib.reload(importlib.import_module("app.api.health"))

    from app.api.health import router as health_router  # ensure importable
    # import your app and include the router for test (or assume app already includes it)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(health_router)

    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert "index_consistency" in j
    ic = j["index_consistency"]
    assert ic["json_doc_count"] == 2
    assert ic["sqlite_doc_count"] == 1
    assert ic["mismatch"] is True
    # ensure d2 is reported as json_only
    assert "d2" in ic["json_only_ids"]

