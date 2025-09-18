"""
# tests/test_p0_api.py
import json
import pytest
import httpx

from app.main import app


@pytest.mark.anyio
async def test_p0_object_and_context_flow(tmp_path):
    # Use ASGITransport for in-process FastAPI testing (httpx >= 0.28)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1) Create an object
        r = await ac.post("/objects", json={"object_type": "dataset", "attrs": {"name": "demo"}})
        assert r.status_code == 200, r.text
        object_id = r.json()["object_id"]
        assert isinstance(object_id, str) and len(object_id) > 0

        # 2) Fetch the object
        r = await ac.get(f"/objects/{object_id}")
        assert r.status_code == 200, r.text
        obj = r.json()
        assert obj["object_id"] == object_id
        assert obj["object_type"] == "dataset"
        assert "ts" in obj  # event timestamp should be present

        # 3) Create a context (raw JSON) for that object
        r = await ac.post(
            f"/objects/{object_id}/contexts",
            content=json.dumps({"hello": "world"}),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200, r.text
        body = r.json()

        # Your serializer returns 8-hex context ids (no "ctx_" prefix)
        ctx_id = body["context_id"]
        assert isinstance(ctx_id, str) and len(ctx_id) >= 6

        # Adapter adds meta (including object_id)
        meta = body.get("meta", {})
        assert meta.get("object_id") == object_id

        # If the route returns png_path, it should end with ctx_<id>.png
        png_path = body.get("png_path")
        if png_path:
            assert png_path.endswith(f"ctx_{ctx_id}.png")

        # 4) Add lineage parents
        r = await ac.post(
            f"/contexts/{ctx_id}/parents",
            json={"parents": ["ctx_fake1", "ctx_fake2"]},
        )
        assert r.status_code == 200, r.text
        lineage = r.json()
        assert lineage["context_id"] == ctx_id
        assert lineage["parents"] == ["ctx_fake1", "ctx_fake2"]


# Optional: enable this if you want to test file-upload flow too.
# Keep it off by default to avoid relying on external files.
@pytest.mark.anyio
async def test_p0_file_upload_flow(tmp_path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create object
        r = await ac.post("/objects", json={"object_type": "dataset"})
        assert r.status_code == 200, r.text
        object_id = r.json()["object_id"]

        # Prepare a small temp file to upload
        file_path = tmp_path / "sample.txt"
        file_path.write_text("hello-contextvault", encoding="utf-8")

        # Upload file as a context for the object (multipart/form-data)
        with file_path.open("rb") as f:
            files = {"upload": ("sample.txt", f, "text/plain")}
            r = await ac.post(f"/objects/{object_id}/contexts", files=files)

        assert r.status_code == 200, r.text
        data = r.json()
        ctx_id = data["context_id"]
        assert isinstance(ctx_id, str) and len(ctx_id) >= 6
        meta = data.get("meta", {})
        assert meta.get("object_id") == object_id
        png_path = data.get("png_path")
        if png_path:
            assert png_path.endswith(f"ctx_{ctx_id}.png")
"""