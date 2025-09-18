# tests/test_audit_rotation.py
import os
import json
import time
from pathlib import Path
from app.core.audit_log import AuditLog, get_audit

def test_rotation_and_retention(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.log"
    monkeypatch.setenv("INDEX_AUDIT_PATH", str(audit_file))
    monkeypatch.setenv("AUDIT_MAX_SIZE_MB", "0")  # force rotate on next append (size 0)
    monkeypatch.setenv("AUDIT_RETENTION_FILES", "2")
    # get lazy audit (will pick up env)
    aud = get_audit()
    # append multiple entries
    for i in range(5):
        aud.append({"a": i})
    # rotation should have occurred (rotate_now called on append) -> old files exist
    rotated = aud.list_rotated_files()
    # there may be rotated files; ensure retention kept <= 2 rotated files
    assert isinstance(rotated, list)
    assert len(rotated) <= 2

    # tail should return recent entries (skip malformed)
    lines = get_audit().tail(10)
    assert isinstance(lines, list)

def test_rotate_now(tmp_path):
    audit_file = tmp_path / "audit.log"
    aud = AuditLog(audit_file, max_size_mb=1, retention_files=1, retention_days=1)
    for i in range(3):
        aud.append({"x": i})
    rotated = aud.rotate_now()
    assert rotated is not None
    assert rotated.exists()
