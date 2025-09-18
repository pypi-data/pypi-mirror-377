"""
# tests/test_p1_api.py
import json
import pytest
import httpx
from app.main import app

@pytest.mark.anyio
async def test_p1_read_and_lineage(tmp_path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        # create object
        r = await ac.post("/objects", json={"object_type": "dataset"})
        assert r.status_code == 200
        object_id = r.json()["object_id"]

        # create two contexts
        r = await ac.post(
            f"/objects/{object_id}/contexts",
            content=json.dumps({"a": 1}),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200
        ctx1 = r.json()["context_id"]
        ts1 = r.json()["meta"]["created_at"]

        r = await ac.post(
            f"/objects/{object_id}/contexts",
            content=json.dumps({"b": 2}),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 200
        ctx2 = r.json()["context_id"]
        ts2 = r.json()["meta"]["created_at"]

        # list contexts for object (aka timeline)
        r = await ac.get(f"/objects/{object_id}/contexts", params={"limit": 10})
        assert r.status_code == 200
        items = r.json()["items"]
        ids = [i["context_id"] for i in items]
        assert ctx1 in ids and ctx2 in ids

        # alias matches
        r2 = await ac.get(f"/objects/{object_id}/timeline", params={"limit": 10})
        assert r2.status_code == 200
        assert set([i["context_id"] for i in r2.json()["items"]]) == set(ids)

        # get single context
        r = await ac.get(f"/contexts/{ctx1}")
        assert r.status_code == 200
        assert r.json()["context_id"] == ctx1

        # lineage: ctx2 <- ctx1
        r = await ac.post(f"/contexts/{ctx2}/parents", json={"parents": [ctx1]})
        assert r.status_code == 200

        # read parents of ctx2
        r = await ac.get(f"/contexts/{ctx2}/parents")
        assert r.status_code == 200
        assert r.json()["parents"] == [ctx1]

        # read children of ctx1
        r = await ac.get(f"/contexts/{ctx1}/children")
        assert r.status_code == 200
        assert ctx2 in r.json()["children"]

        # trace up from ctx2 (should see ctx1 at level 1)
        r = await ac.get(f"/lineage/trace/{ctx2}", params={"direction": "up", "max_depth": 2})
        assert r.status_code == 200
        levels = r.json()["levels"]
        assert levels and ctx1 in levels[0]

        # state_at: choose cutoff between ts1 and ts2
        cutoff = max(ts1, ts2)
        r = await ac.get(f"/state_at/{object_id}", params={"t": cutoff})
        assert r.status_code == 200
        st = r.json()
        # at least one context at cutoff
        assert st["count"] >= 1
        assert st["latest"] is None or "context_id" in st["latest"]
"""