import json
from pathlib import Path

METADATA_FILE = Path("data/metadata.json")
METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_metadata():
    if not METADATA_FILE.exists():
        return {}
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_metadata(metadata: dict):
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


def register_context(
    context_id: str,
    version_hash: str,
    zip_name: str,
    image_name: str,
    source_name: str,
    zip_len: int,
    entry_type: str = "file",   # <-- NEW field, defaults to "file"
):
    """
    Register a new context with all necessary metadata.
    Stores entry_type ("file" or "raw") for downstream logic.
    """
    metadata = load_metadata()
    metadata[image_name] = {
        "context_id": context_id,
        "version_hash": version_hash,
        "zip_name": zip_name,
        "source_name": source_name,
        "zip_len": zip_len,        # critical for decoding
        "entry_type": entry_type,  # <-- NEW field
    }
    save_metadata(metadata)


def get_original_filename(image_name: str):
    """
    Retrieve the original filename uploaded for a given context image.
    """
    metadata = load_metadata()
    if image_name in metadata:
        return metadata[image_name].get("source_name")
    return None


def get_zip_length(image_name: str):
    """
    Retrieve the original ZIP length for decoding.
    """
    metadata = load_metadata()
    if image_name in metadata:
        return metadata[image_name].get("zip_len")
    return None


def get_entry_type(image_name: str) -> str:
    """
    Retrieve the entry type ("file" or "raw") for a given context image.
    Defaults to "file" if not present (for backward compatibility).
    """
    metadata = load_metadata()
    if image_name in metadata:
        return metadata[image_name].get("entry_type", "file")
    return "file"
