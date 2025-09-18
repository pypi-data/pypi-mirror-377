# File: tests/test_encryption.py
from app.core.security.encryption import encrypt_bytes, decrypt_bytes, generate_key

def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    data = b"contextvault-encryption-test"
    enc = encrypt_bytes(data, key)
    dec = decrypt_bytes(enc, key)
    assert dec == data
