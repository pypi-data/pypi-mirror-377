# File: app/core/storage/filelog.py
from __future__ import annotations

import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional, Iterator, List, Any

# Keep your existing constants and helpers
LOG_DIR = Path(os.environ.get("FILELOG_ROOT", "data/log"))
LOG_DIR.mkdir(parents=True, exist_ok=True)

# P3: include relationships
Stream = Literal["objects", "contexts", "lineage", "relationships"]

PRIMARY_ID_FIELD: dict[str, str] = {
    "objects": "object_id",
    "contexts": "context_id",
    "lineage": "edge_id",
    "relationships": "rel_id",
}

def _stream_paths(stream: Stream) -> tuple[Path, Path, Path]:
    log = LOG_DIR / f"{stream}.jsonl"
    idx = LOG_DIR / f"{stream}.idx.json"
    lock = LOG_DIR / f"{stream}.lock"
    return log, idx, lock

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _acquire_lock(lock_path: Path, timeout: float = 5.0, poll: float = 0.05) -> None:
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() > deadline:
                raise TimeoutError(f"Could not acquire lock: {lock_path}")
            time.sleep(poll)

def _release_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass

def _load_index(idx_path: Path) -> dict:
    if not idx_path.exists():
        return {}
    try:
        with idx_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_index(idx_path: Path, index: dict) -> None:
    # Windows-friendly atomic replace
    tmp = idx_path.with_name(idx_path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    for _ in range(5):
        try:
            tmp.replace(idx_path)
            return
        except PermissionError:
            time.sleep(0.05)
    tmp.replace(idx_path)

# Try to import partitioned helpers if available
try:
    from app.core.storage.partitioned_filelog import append_event_partition, iter_partition_events, list_shards
except Exception:
    append_event_partition = None
    iter_partition_events = None
    list_shards = None


def append_event(stream: Stream, event: dict) -> None:
    """
    Append event to a stream.

    Backwards-compatible: this ALWAYS appends to the legacy single-file log
    (data/log/<stream>.jsonl) and updates the legacy index. If partitioned logs
    are enabled (USE_PARTITIONED_LOG=1) and the partitioned helper is available,
    we also append to the partition shard (best-effort). This keeps immediate
    visibility for existing reads/tests while allowing partition ingestion later.
    """
    # Lazy import partitioned helpers to respect test monkeypatches
    global append_event_partition, iter_partition_events, list_shards
    if append_event_partition is None:
        try:
            from app.core.storage.partitioned_filelog import append_event_partition as _aep, iter_partition_events as _ipe, list_shards as _ls
            append_event_partition = _aep
            iter_partition_events = _ipe
            list_shards = _ls
        except Exception:
            append_event_partition = None
            iter_partition_events = None
            list_shards = None

    log_path, idx_path, lock_path = _stream_paths(stream)
    id_field = PRIMARY_ID_FIELD[stream]

    # ensure ts
    if "ts" not in event or not event["ts"]:
        event["ts"] = _now_iso()

    # ensure id
    if id_field not in event or not event[id_field]:
        if stream == "objects":
            event[id_field] = str(uuid.uuid4())
        elif stream == "contexts":
            event[id_field] = f"ctx_{uuid.uuid4().hex[:12]}"
        elif stream == "lineage":
            event[id_field] = f"edge_{uuid.uuid4().hex[:12]}"
        elif stream == "relationships":
            event[id_field] = f"rel_{uuid.uuid4().hex[:12]}"

    # Try partitioned append (best-effort) but DO NOT return early.
    use_partitioned = os.environ.get("USE_PARTITIONED_LOG", "0") == "1" and append_event_partition is not None
    if use_partitioned:
        # choose key heuristically
        key = None
        try:
            if stream == "relationships":
                key = event.get("child_id") or (event.get("from") or {}).get("id") or (event.get("to") or {}).get("id") or event.get(id_field)
            elif stream == "contexts":
                key = event.get("object_id") or event.get(id_field)
            elif stream == "objects":
                key = event.get(id_field)
            elif stream == "lineage":
                key = event.get(id_field) or event.get("child_id") or event.get("parent_id")
        except Exception:
            key = None
        if not key:
            key = event.get(id_field)
        if key:
            try:
                append_event_partition(key=key, stream=stream, event=event)
            except Exception:
                # swallow partition write failure — we always fall back to legacy write
                pass

    # Legacy single-file append (always executed)
    _acquire_lock(lock_path)
    try:
        index = _load_index(idx_path)
        with log_path.open("ab") as f:
            offset = f.tell()
            line = (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            f.write(line)
        index[str(event[id_field])] = offset
        _save_index(idx_path, index)
    finally:
        _release_lock(lock_path)


def _iter_legacy_events(path: Path) -> Iterator[dict]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def iter_events(stream: Stream) -> Iterator[dict]:
    """
    Iterate events for a logical stream.

    This yields events from the legacy single-file log first (if present) and
    then yields events from partitioned shards (if partitioned support is available).
    This makes read paths see partitioned writes immediately.
    """
    # yield legacy events first for deterministic ordering in tests/backwards uses
    log_path, _, _ = _stream_paths(stream)
    yield from _iter_legacy_events(log_path)

    # then yield from partitioned shards if supported
    if iter_partition_events is not None:
        yield from iter_partition_events(stream)


def get_event_by_id(stream: Stream, id_field: str, id_value: str) -> Optional[dict]:
    """
    Lookup event by id. First consults legacy index + file (fast), then scans partitioned files.
    """
    log_path, idx_path, _ = _stream_paths(stream)
    index = _load_index(idx_path)

    if id_value in index:
        try:
            with log_path.open("rb") as f:
                f.seek(index[id_value])
                line = f.readline()
            if line:
                obj = json.loads(line)
                if obj.get(id_field) == id_value:
                    return obj
        except Exception:
            pass

    # fallback: scan legacy file fully (in case index was stale)
    if log_path.exists():
        with log_path.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get(id_field) == id_value:
                        return obj
                except Exception:
                    continue

    # finally scan partitioned logs (if available)
    if iter_partition_events is not None:
        for ev in iter_partition_events(stream):
            # Some partitioned events may not include the id_field in top-level (unlikely), handle gracefully
            if ev.get(id_field) == id_value:
                return ev
            # For relationships we also support legacy field names (e.g., child_id/parent_id)
            if stream == "relationships":
                # check rel_id fallback
                if ev.get("rel_id") == id_value:
                    return ev
    return None


# --- P1 helpers (kept) ---
def find_events_by_field(stream: Stream, field: str, value: Any, *, since_ts: str | None = None) -> List[dict]:
    out: List[dict] = []
    for ev in iter_events(stream):
        if ev.get(field) == value:
            if since_ts and ev.get("ts") and ev["ts"] < since_ts:
                continue
            out.append(ev)
    return out

def latest_event_by_field(stream: Stream, field: str, value: Any) -> dict | None:
    last = None
    for ev in iter_events(stream):
        if ev.get(field) == value:
            last = ev
    return last
