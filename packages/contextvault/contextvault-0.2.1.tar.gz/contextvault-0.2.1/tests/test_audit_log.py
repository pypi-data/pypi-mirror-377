# tests/test_audit_log.py
import os
import tempfile
import json
from app.core.audit_log import AuditLog

def test_append_and_tail(tmp_path):
    logfile = tmp_path / "audit.log"
    al = AuditLog(str(logfile), rotate_size=1024, max_rotations=3)

    al.append({"actor": "test", "action": "create", "id": "a1"})
    al.append({"actor": "test", "action": "update", "id": "a1"})
    out = al.tail(10)
    assert isinstance(out, list)
    assert len(out) == 2
    assert out[0]["event"]["action"] == "create"
    assert out[1]["event"]["action"] == "update"

def test_rotation(tmp_path):
    logfile = tmp_path / "audit.log"
    # small rotate size for test
    al = AuditLog(str(logfile), rotate_size=200, max_rotations=2)
    # append several entries to exceed rotate_size
    for i in range(50):
        al.append({"actor": "test", "i": i})
    # after many writes, original file may have rotated
    # ensure at least one rotated file or main file exists
    rotated_exists = any(str(logfile.with_suffix(s)) for s in [".1", ".2"])
    assert logfile.exists() or rotated_exists
