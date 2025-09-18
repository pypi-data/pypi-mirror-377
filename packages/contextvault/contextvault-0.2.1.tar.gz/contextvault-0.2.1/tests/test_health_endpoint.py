# tests/test_health_endpoint.py
from fastapi.testclient import TestClient
from app.main import app  # adjust if your app factory is different

client = TestClient(app)

def test_ping():
    r = client.get("/health/ping")
    assert r.status_code == 200
    j = r.json()
    assert "ping" in j and j["ping"] == "pong"

def test_health_contains_index():
    r = client.get("/health")
    assert r.status_code == 200
    j = r.json()
    assert "status" in j
    assert "index" in j
    # index should at least contain doc_count key (fallbacks may vary)
    assert ("doc_count" in j["index"]) or ("error" in j["index"])
