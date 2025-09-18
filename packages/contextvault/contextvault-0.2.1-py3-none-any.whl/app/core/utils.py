# app/core/utils.py

import hashlib
from PIL import Image
import io
import math
import numpy as np
import zlib


def generate_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_binary_to_image(data: bytes) -> Image.Image:
    """
    Encode arbitrary bytes into a grayscale PNG.
    Pads with zeros up to a square.
    """
    n_pixels = math.ceil(len(data) ** 0.5)
    padded = data + b"\x00" * (n_pixels * n_pixels - len(data))
    arr = np.frombuffer(padded, dtype=np.uint8).reshape((n_pixels, n_pixels))
    return Image.fromarray(arr, mode="L")


def decode_image_to_binary(image_path: str) -> bytes:
    """
    Decode a grayscale PNG produced by encode_binary_to_image back to raw bytes
    (still includes any padding).
    """
    img = Image.open(image_path).convert("L")
    arr = np.array(img, dtype=np.uint8)
    return arr.tobytes()


# ---------- Compression helpers ----------

MAGIC = b"CV01"  # header for context-object snapshots

def pack_payload(raw: bytes, with_header: bool, level: int = 6) -> bytes:
    """
    Compress raw bytes with zlib. Optionally prepend a small header with length,
    used for context-object snapshots so we can strip padding without external metadata.
    """
    comp = zlib.compress(raw, level)
    if with_header:
        length = len(comp).to_bytes(4, "big")
        return MAGIC + length + comp
    return comp


def unpack_payload(buf: bytes, with_header: bool, known_len: int | None = None) -> bytes:
    """
    Reverse of pack_payload.
    - If with_header=True: expect MAGIC + len(4) + compressed, ignore trailing padding.
    - If with_header=False: use known_len if provided to trim padding; else try to decompress as-is,
      falling back to returning buf on failure (back-compat for uncompressed historical data).
    """
    try:
        if with_header:
            if not buf.startswith(MAGIC) or len(buf) < 8:
                # No header found; fall back to try decompress whole buffer
                return zlib.decompress(buf)
            comp_len = int.from_bytes(buf[4:8], "big")
            comp = buf[8:8 + comp_len]
            return zlib.decompress(comp)

        # without header (per-file images): we rely on metadata len to slice tight
        slice_bytes = buf[:known_len] if known_len is not None else buf
        try:
            return zlib.decompress(slice_bytes)
        except Exception:
            # Backward compatibility: old images stored raw ZIP (no compression)
            return slice_bytes
    except Exception:
        # As a last resort, return original buffer (caller may still succeed if it was raw ZIP)
        return buf
