# tests/test_admin_audit_api.py
import os
import sys
import importlib
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

def test_admin_audit_endpoints(tmp_path, monkeypatch):
    audit_file = tmp_path / "audit.log"
    monkeypatch.setenv("INDEX_AUDIT_PATH", str(audit_file))
    # create some audit lines
    from app.core.audit_log import get_audit
    aud = get_audit()
    aud.append({"actor":"t","action":"a"})
    aud.append({"actor":"t","action":"b"})

    # monkeypatch auth.decode_access_token to simulate admin
    import app.auth as auth_mod
    monkeypatch.setattr(auth_mod, "decode_access_token", lambda token: {"role":"admin","email":"a@example.com"})

    # include router into temp app
    from app.api.admin_audit import router as admin_router
    app = FastAPI()
    app.include_router(admin_router)
    client = TestClient(app)

    headers = {"Authorization": "Bearer faketoken"}
    r = client.get("/admin/audit/tail?lines=10", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert "entries" in j and isinstance(j["entries"], list)

    r2 = client.get("/admin/audit/export", headers=headers)
    assert r2.status_code == 200
    # response content should contain at least one line
    assert r2.content and len(r2.content) > 0
