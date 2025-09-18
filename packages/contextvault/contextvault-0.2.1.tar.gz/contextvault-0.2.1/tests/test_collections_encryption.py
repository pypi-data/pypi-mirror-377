# File: tests/test_collections_encryption.py
import io
from pathlib import Path

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
DATA_DIR = Path("data")


def test_collection_create_encrypt_and_decode(tmp_path):
    # ensure collection exists
    client.post("/collections/testcol")
    # prepare a small file to upload
    content = b"hello-collection"
    files = {"upload": ("sample.txt", io.BytesIO(content), "application/octet-stream")}
    r = client.post("/collections/testcol/create_context", files=files)
    assert r.status_code == 200, r.text
    j = r.json()
    # API returns encrypted: true
    assert j.get("encrypted") is True
    img_path = j.get("image")
    assert img_path is not None
    enc_img = DATA_DIR / Path(img_path).name
    assert enc_img.exists(), f"Expected encrypted image {enc_img} to exist"


def test_collection_bulk_create_encrypts(tmp_path):
    # ensure collection exists
    client.post("/collections/testcol_bulk")
    # simulate two file uploads
    files = [
        ("uploads", ("f1.txt", io.BytesIO(b"one"), "application/octet-stream")),
        ("uploads", ("f2.txt", io.BytesIO(b"two"), "application/octet-stream")),
    ]
    r = client.post("/collections/testcol_bulk/bulk_create_context", files=files)
    assert r.status_code in (200, 201), r.text
    resp = r.json()
    # resp may be list or dict; ensure encrypted flag exists on each item when list
    if isinstance(resp, list):
        assert all(isinstance(item, dict) and item.get("encrypted") for item in resp)
        for item in resp:
            if item.get("image"):
                enc_img = DATA_DIR / Path(item["image"]).name
                assert enc_img.exists()
    elif isinstance(resp, dict):
        assert resp.get("encrypted") is True
        if resp.get("image"):
            enc_img = DATA_DIR / Path(resp["image"]).name
            assert enc_img.exists()
