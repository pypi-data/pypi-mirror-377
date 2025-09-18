# tests/test_retention.py
import os
import importlib
import json
from pathlib import Path
import time
from datetime import datetime, timedelta, timezone

def test_cleanup_expired(tmp_path, monkeypatch):
    # use a fresh JSON index file in tmp_path
    idx_file = tmp_path / "genai_index.json"
    idx_file.parent.mkdir(parents=True, exist_ok=True)

    # create two contexts: one expired, one valid
    expired_id = "ctx_expired"
    valid_id = "ctx_valid"
    now = datetime.now(timezone.utc)
    expired_ts = (now - timedelta(days=1)).isoformat()
    valid_ts = (now + timedelta(days=1)).isoformat()

    data = {
        expired_id: {"source_filename": "a.txt", "entry_type": "raw", "raw_content": "old", "expires_at": expired_ts},
        valid_id: {"source_filename": "b.txt", "entry_type": "raw", "raw_content": "new", "expires_at": valid_ts}
    }
    with idx_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # monkeypatch the FILES_INDEX path used by retention
    monkeypatch.setenv("INDEX_AUDIT_PATH", str(tmp_path / "audit.log"))
    # ensure indexer.delete_context is available: import app.core.indexer and reload with FILES_INDEX pointing to tmp file
    import app.core.indexer as idxmod
    # monkeypatching the path inside indexer module to point to tmp path
    idxmod.FILES_INDEX = Path(idx_file)

    # import retention and run cleanup
    import importlib
    import app.core.retention as retention
    importlib.reload(retention)

    summary = retention.cleanup_expired()
    assert summary["scanned"] == 2
    assert expired_id in summary["deleted_ids"]
    assert valid_id not in summary["deleted_ids"]

    # Verify JSON index file no longer contains expired_id
    with idx_file.open("r", encoding="utf-8") as f:
        remaining = json.load(f)
    assert expired_id not in remaining
    assert valid_id in remaining
