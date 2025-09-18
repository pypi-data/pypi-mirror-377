from tests.utils import log_result

def test_create_collection_and_add_entry(client):
    test_name = "create_collection_and_add_entry"
    try:
        resp = client.post("/collections/mytest")
        assert resp.status_code == 200
        assert resp.json()["collection"] == "mytest"

        entry = {"dummy": "data"}
        resp = client.post(
            "/collections/mytest/entries",
            json={"category": "testcat", "entry_id": "entry1", "entry": entry}
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "added"

        log_result(test_name, "PASS")
    except Exception as e:
        log_result(test_name, "FAIL", str(e))
        raise
