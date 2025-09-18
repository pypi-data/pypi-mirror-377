# File: app/core/security/encryption.py
"""
AES-GCM encryption helpers for ContextVault.

Behavior:
- If CTXVAULT_AES_KEY is set in env (base64 32 bytes) it is used.
- If not set, an ephemeral base64 key is generated at runtime and used.
  WARNING: ephemeral key is for local dev / tests only. Set CTXVAULT_AES_KEY
  in production to maintain data recoverability across restarts.
"""

import os
import base64
import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

log = logging.getLogger("contextvault.encryption")

# env key (base64 string expected)
_ENV_KEY = os.getenv("CTXVAULT_AES_KEY")

# if no env key, we'll lazily generate an ephemeral one for this process
_EPHEMERAL_KEY_B64: Optional[str] = None

def generate_key() -> str:
    """Generate a random 256-bit key as base64 string."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

def _get_effective_key_b64() -> str:
    global _EPHEMERAL_KEY_B64
    if _ENV_KEY:
        return _ENV_KEY
    if _EPHEMERAL_KEY_B64:
        return _EPHEMERAL_KEY_B64
    # generate ephemeral key and warn
    _EPHEMERAL_KEY_B64 = generate_key()
    log.warning(
        "CTXVAULT_AES_KEY not set — generating ephemeral AES key for this process. "
        "Data encrypted with this key will NOT be recoverable after a restart. "
        "Set CTXVAULT_AES_KEY in your .env for persistent encryption."
    )
    return _EPHEMERAL_KEY_B64

def _get_key_bytes(key_b64: Optional[str] = None) -> bytes:
    use_b64 = key_b64 or _get_effective_key_b64()
    try:
        kb = base64.urlsafe_b64decode(use_b64.encode())
    except Exception as e:
        raise ValueError("Invalid base64 AES key") from e
    if len(kb) != 32:
        raise ValueError("AES key must be 32 bytes (base64-encoded).")
    return kb

def encrypt_bytes(data: bytes, key_b64: Optional[str] = None) -> bytes:
    key = _get_key_bytes(key_b64)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct

def decrypt_bytes(token: bytes, key_b64: Optional[str] = None) -> bytes:
    key = _get_key_bytes(key_b64)
    aesgcm = AESGCM(key)
    nonce, ct = token[:12], token[12:]
    return aesgcm.decrypt(nonce, ct, None)

def encrypt_file(input_path: str, output_path: str, key_b64: Optional[str] = None):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"{input_path} not found")
    data = p.read_bytes()
    enc = encrypt_bytes(data, key_b64)
    Path(output_path).write_bytes(enc)

def decrypt_file(input_path: str, output_path: str, key_b64: Optional[str] = None):
    p = Path(input_path)
    if not p.exists():
        raise FileNotFoundError(f"{input_path} not found")
    enc = p.read_bytes()
    dec = decrypt_bytes(enc, key_b64)
    Path(output_path).write_bytes(dec)
