# app/core/integrity.py
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Iterable, Optional, Tuple

BASE = Path("data")
LOG_DIR = BASE / "log"
MANIFEST_DIR = BASE / "manifest"
MIRROR_DIR = BASE / "mirror"

MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
MIRROR_DIR.mkdir(parents=True, exist_ok=True)


def _line_hash(line: str) -> str:
    """SHA256 of the raw line (utf-8)."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def _extract_primary_id(ev: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """
    Heuristic: extract the primary id and its type from a log event.
    Returns (id_field_name, id_value) or (None, None) if not found.
    """
    for candidate in ("context_id", "object_id", "edge_id", "schema_ref"):
        if candidate in ev and ev.get(candidate):
            return candidate, str(ev.get(candidate))
    # fallback: maybe an 'id' field
    if "id" in ev:
        return "id", str(ev.get("id"))
    return None, None


def iter_log_files(log_dir: Optional[Path] = None) -> Iterable[Path]:
    ld = log_dir or LOG_DIR
    for p in sorted(ld.glob("*.jsonl")):
        yield p


def generate_manifest(
    log_file: Path,
    manifest_out: Optional[Path] = None,
    include_line_index: bool = True,
) -> Path:
    """
    Generate a manifest for a single log file.
    Manifest is a JSONL file with entries:
      {
        "file": "<relative filename>",
        "line_index": <0-based index>,
        "line_hash": "<sha256>",
        "primary_id_field": "context_id",
        "primary_id": "abc123",
        "raw": <optional short preview or omitted>
      }
    Returns path to manifest file written.
    """
    if not log_file.exists():
        raise FileNotFoundError(log_file)

    manifest_out = manifest_out or (MANIFEST_DIR / f"{log_file.stem}.manifest.jsonl")
    with log_file.open("r", encoding="utf-8") as rf, manifest_out.open("w", encoding="utf-8") as wf:
        for idx, raw in enumerate(rf):
            line = raw.rstrip("\n")
            if not line:
                continue
            h = _line_hash(line)
            try:
                ev = json.loads(line)
            except Exception:
                ev = None
            id_field, id_value = (None, None)
            if isinstance(ev, dict):
                id_field, id_value = _extract_primary_id(ev)
            entry = {
                "file": str(log_file.name),
                "line_index": idx if include_line_index else None,
                "line_hash": h,
                "primary_id_field": id_field,
                "primary_id": id_value,
            }
            # write compact
            wf.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return manifest_out


def generate_all_manifests(log_dir: Optional[Path] = None) -> Dict[str, Path]:
    """Generate manifests for all *.jsonl files inside log_dir (defaults to data/log)."""
    out = {}
    for log_file in iter_log_files(log_dir):
        mf = generate_manifest(log_file)
        out[str(log_file.name)] = mf
    return out


def verify_manifest(manifest_file: Path, log_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Verify a manifest against current log file content.
    Returns a report:
      {
        "manifest": "<path>",
        "log": "<matching log>",
        "ok": True/False,
        "mismatches": [ {line_index, expected_hash, actual_hash, note}, ... ],
        "missing_lines": [ ... ],
        "extra_lines": [ ... ]
      }
    """
    if not manifest_file.exists():
        raise FileNotFoundError(manifest_file)
    # read manifest entries
    entries = []
    with manifest_file.open("r", encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                entries.append(json.loads(ln))
    if not entries:
        return {"manifest": str(manifest_file), "ok": True, "mismatches": [], "missing_lines": [], "extra_lines": []}

    log_name = entries[0].get("file")
    log_dir = log_dir or LOG_DIR
    log_path = (log_dir / log_name)
    if not log_path.exists():
        return {"manifest": str(manifest_file), "ok": False, "error": f"log file not found: {log_path}"}

    mismatches = []
    missing = []
    extra = []

    # Read current file lines into map index->hash
    current_hashes = []
    with log_path.open("r", encoding="utf-8") as lf:
        for ln in lf:
            current_hashes.append(_line_hash(ln.rstrip("\n")))

    # compare by index where possible
    for entry in entries:
        idx = entry.get("line_index")
        expected = entry.get("line_hash")
        if idx is None:
            # can't verify without index — skip
            continue
        if idx >= len(current_hashes):
            missing.append({"line_index": idx, "expected_hash": expected})
        else:
            actual = current_hashes[idx]
            if actual != expected:
                mismatches.append({"line_index": idx, "expected_hash": expected, "actual_hash": actual})

    # extra lines in current file (newer appended)
    if len(current_hashes) > max((e.get("line_index", -1) for e in entries), default=-1) + 1:
        # indexes beyond last manifest entry are "extra"
        last_idx = max((e.get("line_index", -1) for e in entries), default=-1)
        extra = [{"line_index": i, "actual_hash": current_hashes[i]} for i in range(last_idx + 1, len(current_hashes))]

    ok = not (mismatches or missing)
    report = {
        "manifest": str(manifest_file),
        "log": str(log_path),
        "ok": ok,
        "mismatches": mismatches,
        "missing_lines": missing,
        "extra_lines": extra,
    }
    return report


def mirror_logs(target_dir: Optional[Path] = None) -> Path:
    """
    Simple mirror: copy current log files to a mirror directory under data/mirror/<timestamp>/
    Uses streaming copies (no heavy memory).
    Returns path to mirror folder.
    """
    from shutil import copy2
    from datetime import datetime

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dst = (MIRROR_DIR / ts)
    dst.mkdir(parents=True, exist_ok=True)
    for p in iter_log_files():
        copy2(p, dst / p.name)
    return dst
