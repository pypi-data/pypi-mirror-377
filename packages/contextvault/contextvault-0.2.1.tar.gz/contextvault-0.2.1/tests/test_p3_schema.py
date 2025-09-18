"""
# tests/test_p3_schema.py
import json
import pytest
import httpx
from app.main import app

pytest.importorskip("jsonschema")

@pytest.mark.anyio
async def test_p3_schema_validation_flow(tmp_path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Register a schema
        schema_ref = "demo.user"
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
            "additionalProperties": False,
        }
        r = await ac.post(f"/schemas?schema_ref={schema_ref}", json=schema)
        assert r.status_code == 200

        # Create object
        r = await ac.post("/objects", json={"object_type": "dataset"})
        object_id = r.json()["object_id"]

        # Valid instance
        r = await ac.post(
            f"/objects/{object_id}/contexts",
            params={"schema_ref": schema_ref, "object_type": "dataset"},
            content=json.dumps({"name": "Alice"}),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200, r.text
        meta = r.json()["meta"]
        assert "schema_invalid" not in meta.get("flags", [])

        # Invalid instance
        r = await ac.post(
            f"/objects/{object_id}/contexts",
            params={"schema_ref": schema_ref, "object_type": "dataset"},
            content=json.dumps({"name": 123}),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200, r.text
        meta = r.json()["meta"]
        assert "schema_invalid" in meta.get("flags", [])
        assert meta["status"] in ("flag", "quarantine", "accept")  # we quarantine by default
"""