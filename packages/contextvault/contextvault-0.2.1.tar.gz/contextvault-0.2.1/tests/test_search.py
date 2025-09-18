from tests.utils import log_result

def test_keyword_search(client):
    test_name = "keyword_search"
    try:
        resp = client.get("/search_index?q=ContextVault")
        assert resp.status_code == 200
        data = resp.json()
        assert "files" in data
        log_result(test_name, "PASS")
    except Exception as e:
        log_result(test_name, "FAIL", str(e))
        raise


def test_semantic_search(client):
    test_name = "semantic_search"
    try:
        resp = client.get("/semantic_search?q=hello&scope=files&top_k=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        log_result(test_name, "PASS")
    except Exception as e:
        log_result(test_name, "FAIL", str(e))
        raise
