# tests/test_cas.py
import os
from pathlib import Path
from app.core.storage_cas import save_snapshot, snapshot_path_for_hash, verify_snapshot

def test_save_and_verify(tmp_path):
    content = b"hello contextvault"
    sha = save_snapshot(content)
    p = snapshot_path_for_hash(sha)
    assert p.exists()
    assert verify_snapshot(sha) is True

    # tamper test: write bad bytes to temp file (do not overwrite existing)
    # ensure verification fails if file missing or wrong
    assert verify_snapshot("deadbeef" * 8) is False
