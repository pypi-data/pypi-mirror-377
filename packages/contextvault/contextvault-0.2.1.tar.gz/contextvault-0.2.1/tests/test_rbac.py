# File: tests/test_rbac.py
import io
from fastapi.testclient import TestClient
from app.main import app
from app.auth import create_access_token, bearer

client = TestClient(app)


def test_token_issue_and_ui_access():
    # Create tokens using the demo users from app.auth
    admin_token = create_access_token(subject="admin", role="admin")
    viewer_token = create_access_token(subject="viewer", role="viewer")

    # Unauthenticated access -> 401
    r = client.get("/ui/test")
    assert r.status_code == 401, r.text

    # Viewer can access /ui/test
    r = client.get("/ui/test", headers={"Authorization": bearer(viewer_token)})
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["user"]["sub"] == "viewer"
    assert j["user"]["role"] == "viewer"

    # Admin can access /ui/test
    r = client.get("/ui/test", headers={"Authorization": bearer(admin_token)})
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["user"]["sub"] == "admin"
    assert j["user"]["role"] == "admin"

    # Admin-only path example: call an admin subpath that triggers admin check in middleware
    r = client.get("/ui/admin/secret", headers={"Authorization": bearer(viewer_token)})
    assert r.status_code == 403  # viewer lacks admin role

    r = client.get("/ui/admin/secret", headers={"Authorization": bearer(admin_token)})
    # There's no explicit handler for /ui/admin/secret in main; middleware allows reach-through only if admin.
    # Since no route exists, expect 404 if middleware allowed us to reach app routing.
    assert r.status_code in (404, 200)
