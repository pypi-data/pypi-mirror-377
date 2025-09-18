"""
# tests/test_p3_relationships.py
import json
import pytest
import httpx
from app.main import app

@pytest.mark.anyio
async def test_p2_policy_meta_fields():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # create object
        r = await ac.post("/objects", json={"object_type":"dataset"})
        assert r.status_code == 200
        oid = r.json()["object_id"]

        # create context; pass object_type to help policy resolution
        r = await ac.post(
            f"/objects/{oid}/contexts?object_type=dataset",
            content=json.dumps({"k":"v"}),
            headers={"Content-Type":"application/json"},
        )
        assert r.status_code == 200, r.text
        meta = r.json()["meta"]
        # P2 fields present
        assert "status" in meta
        assert "trust" in meta
        assert isinstance(meta.get("flags", []), list)
"""