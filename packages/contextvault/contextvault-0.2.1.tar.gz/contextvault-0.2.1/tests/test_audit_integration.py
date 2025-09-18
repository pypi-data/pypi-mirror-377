# tests/test_audit_integration.py
import os
import sys
import importlib
import json
from pathlib import Path

def test_index_and_delete_writes_audit(tmp_path, monkeypatch):
    # Point audit path to tmp file via env var before importing the module
    audit_file = tmp_path / "audit.log"
    monkeypatch.setenv("INDEX_AUDIT_PATH", str(audit_file))

    # Ensure sqlite is not enabled for this test (we test JSON path)
    monkeypatch.setenv("INDEX_BACKEND", "")

    # Force a clean re-import of app.core.indexer so it picks up env vars
    if "app.core.indexer" in sys.modules:
        del sys.modules["app.core.indexer"]
    mod = importlib.import_module("app.core.indexer")

    # create a sample context
    cid = "test_ctx_1"
    metadata = {
        "original_filename": "myfile.txt",
        "category": "tests",
        "collection": "colA",
        "entry_type": "raw",
        "raw_content": "this is some sample raw content",
        "timestamp": "2025-01-01T00:00:00Z"
    }

    # index the context
    mod.index_context(cid, metadata)

    # check audit contains an index_context JSON line
    assert audit_file.exists()
    with open(audit_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    assert any('"action":"index_context"' in line and '"status":"ok"' in line for line in lines)

    # now delete the context
    res = mod.delete_context(cid)
    assert res is True

    # check audit for delete_context entry
    with open(audit_file, "r", encoding="utf-8") as f:
        lines2 = f.read().splitlines()
    assert any('"action":"delete_context"' in line for line in lines2)
