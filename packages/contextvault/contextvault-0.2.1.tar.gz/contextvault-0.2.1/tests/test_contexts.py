import io
from pathlib import Path
from tests.utils import log_result


def test_create_and_decode_file_context(client):
    test_name = "create_and_decode_file_context"
    try:
        file_content = b"Hello from ContextVault"
        files = {"upload": ("hello.txt", io.BytesIO(file_content), "text/plain")}
        response = client.post("/create_context/?compress=false", files=files)
        assert response.status_code == 200
        data = response.json()
        assert data["context_id"]

        # Ensure correct file path resolution
        img_path = Path(data["image"])
        if not img_path.exists():
            img_path = Path(__file__).parents[1] / data["image"]

        with open(img_path, "rb") as f:
            # use the real filename so metadata matches
            decode_resp = client.post(
                "/decode_context_raw/", files={"image": (img_path.name, f, "image/png")}
            )
        assert decode_resp.status_code == 200
        decode_data = decode_resp.json()
        assert decode_data["status"] == "success"

        log_result(test_name, "PASS")
    except Exception as e:
        log_result(test_name, "FAIL", str(e))
        raise


def test_create_and_decode_raw_context(client):
    test_name = "create_and_decode_raw_context"
    try:
        # Send raw JSON directly
        payload = {"foo": "bar", "count": 42}
        response = client.post("/create_context/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["entry_type"] == "raw"

        img_path = Path(data["image"])
        if not img_path.exists():
            img_path = Path(__file__).parents[1] / data["image"]

        with open(img_path, "rb") as f:
            # use the real filename so metadata matches
            decode_resp = client.post(
                "/decode_context_raw/", files={"image": (img_path.name, f, "image/png")}
            )
        assert decode_resp.status_code == 200
        decode_data = decode_resp.json()
        assert decode_data["entry_type"] == "raw"
        assert "raw_content" in decode_data

        log_result(test_name, "PASS")
    except Exception as e:
        log_result(test_name, "FAIL", str(e))
        raise
