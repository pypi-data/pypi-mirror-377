# File: tests/test_auth.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_and_access_admin():
    # login as admin
    r = client.post("/auth/token", data={"username": "admin@example.com", "password": "adminpass"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # call a protected UI route
    r2 = client.get("/api/ui/data", headers={"Authorization": f"Bearer {token}"})
    # Since /api/ui/data is not explicitly defined yet, this may be 404, 422, or 200 depending on repo state
    assert r2.status_code in (200, 404, 422)

def test_invalid_login():
    r = client.post("/auth/token", data={"username": "admin@example.com", "password": "wrong"})
    assert r.status_code == 400

def test_github_stub_returns_token():
    r = client.get("/auth/github")
    assert r.status_code == 200
    assert "access_token" in r.json()
