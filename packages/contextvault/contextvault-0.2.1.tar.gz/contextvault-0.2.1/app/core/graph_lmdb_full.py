# app/core/graph_lmdb_full.py
"""
LMDB/mmap indices writer + safe fallback stub.

Behavior:
- If the `lmdb` Python package is available, uses a GraphLMDBFull class
  that writes compact LMDB env data as in the original implementation.
- If `lmdb` is NOT available, provides a fallback write_lmdb_from_shard()
  implementation that creates a readable LMDB-like stub by copying the
  shard vdir into an output directory and writing a simple metadata file.

Public API (unchanged):
- write_lmdb_from_shard(shard_vdir: Path, lmdb_out_root: Path, map_size: int = 1<<24) -> Optional[Path]

Notes:
- This file is defensive: it will not raise ImportError at import time
  if `lmdb` is missing. It logs errors and returns None on failures.
"""

from __future__ import annotations
import struct
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

log = logging.getLogger("graph_lmdb_full")

UINT32 = "<I"
UINT32_SIZE = 4

# Try to import lmdb; if unavailable, set a flag and use copy-based fallback
try:
    import lmdb  # type: ignore
    _HAS_LMDB = True
except Exception:
    lmdb = None  # type: ignore
    _HAS_LMDB = False
    log.debug("lmdb not available; graph_lmdb_full will use fallback stub.")


# -------------------------
# LMDB-backed implementation (used when lmdb is available)
# -------------------------
if _HAS_LMDB:
    class GraphLMDBFull:
        """
        Compact LMDB-backed adjacency store.

        Layout:
          <out_root>/lmdb/<shard>/v{ts}/lmdb_env/ -> LMDB environment
          DBs:
            - idmap: key=node_id (utf-8) -> 4-byte int
            - revmap: key=4-byte int -> node_id (utf-8)
            - parents: key=4-byte int -> packed uint32 list (binary)
            - children: key=4-byte int -> packed uint32 list (binary)
        """

        def __init__(self, root: Path, map_size: int = 1 << 24):
            # default map_size lowered to 16MB (1<<24) to avoid disk-space issues in CI/temp dirs.
            self.root = Path(root)
            self.root.mkdir(parents=True, exist_ok=True)
            self.env_path = self.root / "lmdb_env"
            self.env_path.mkdir(parents=True, exist_ok=True)
            # create/open env with a conservative map_size
            try:
                self.env = lmdb.open(str(self.env_path), map_size=map_size, max_dbs=6)
                # named DBs
                self.idmap_db = self.env.open_db(b"idmap")
                self.revmap_db = self.env.open_db(b"revmap")
                self.parents_db = self.env.open_db(b"parents")
                self.children_db = self.env.open_db(b"children")
            except Exception:
                log.exception("failed to create/open lmdb env at %s", self.env_path)
                raise

        # helpers
        def _i2b(self, i: int) -> bytes:
            return struct.pack(UINT32, i)

        def _b2i(self, b: bytes) -> int:
            return struct.unpack(UINT32, b)[0]

        def close(self):
            try:
                # sync + close gracefully
                try:
                    self.env.sync()
                except Exception:
                    log.debug("lmdb env sync failed (continuing to close)")
                try:
                    self.env.close()
                except Exception:
                    log.debug("lmdb env close failed")
            except Exception:
                log.exception("error closing lmdb env")

        # high-level: write already int-keyed parents/children arrays and idmap
        def write_bulk_ints(self, idmap: Dict[str, int], parents_ints: Dict[int, List[int]], children_ints: Dict[int, List[int]]):
            """
            Atomically write idmap + revmap + parents/children (as packed uint32 arrays).
            """
            try:
                with self.env.begin(write=True) as txn:
                    # idmap: node_id -> int (4-byte)
                    for nid, i in idmap.items():
                        txn.put(nid.encode("utf-8"), self._i2b(i), db=self.idmap_db)
                    # revmap: int -> node_id
                    for nid, i in idmap.items():
                        txn.put(self._i2b(i), nid.encode("utf-8"), db=self.revmap_db)
                    # parents: int -> packed uint32 bytes
                    for i, lst in parents_ints.items():
                        if not lst:
                            txn.put(self._i2b(i), b"", db=self.parents_db)
                        else:
                            buf = b"".join(self._i2b(x) for x in lst)
                            txn.put(self._i2b(i), buf, db=self.parents_db)
                    # children
                    for i, lst in children_ints.items():
                        if not lst:
                            txn.put(self._i2b(i), b"", db=self.children_db)
                        else:
                            buf = b"".join(self._i2b(x) for x in lst)
                            txn.put(self._i2b(i), buf, db=self.children_db)
            except Exception:
                log.exception("write_bulk_ints failed")

        def get_parents(self, node_id: str) -> List[str]:
            try:
                with self.env.begin() as txn:
                    raw = txn.get(node_id.encode("utf-8"), db=self.idmap_db)
                    if not raw:
                        return []
                    i = self._b2i(raw)
                    rawbuf = txn.get(self._i2b(i), db=self.parents_db) or b""
                    res: List[str] = []
                    for off in range(0, len(rawbuf), UINT32_SIZE):
                        v = self._b2i(rawbuf[off:off + UINT32_SIZE])
                        s = txn.get(self._i2b(v), db=self.revmap_db)
                        if s:
                            res.append(s.decode("utf-8"))
                    return res
            except Exception:
                log.exception("get_parents failed for %s", node_id)
                return []

        def get_children(self, node_id: str) -> List[str]:
            try:
                with self.env.begin() as txn:
                    raw = txn.get(node_id.encode("utf-8"), db=self.idmap_db)
                    if not raw:
                        return []
                    i = self._b2i(raw)
                    rawbuf = txn.get(self._i2b(i), db=self.children_db) or b""
                    res: List[str] = []
                    for off in range(0, len(rawbuf), UINT32_SIZE):
                        v = self._b2i(rawbuf[off:off + UINT32_SIZE])
                        s = txn.get(self._i2b(v), db=self.revmap_db)
                        if s:
                            res.append(s.decode("utf-8"))
                    return res
            except Exception:
                log.exception("get_children failed for %s", node_id)
                return []


    # Public convenience function using LMDB when available
    def write_lmdb_from_shard(shard_vdir: Path, lmdb_out_root: Path, map_size: int = 1 << 24) -> Optional[Path]:
        """
        Read shard adjacency files and write a compact LMDB snapshot under lmdb_out_root/<vdir>/.
        Returns the out_vdir Path or None on failure.
        """
        shard_vdir = Path(shard_vdir)
        if not shard_vdir.exists() or not shard_vdir.is_dir():
            log.debug("shard_vdir missing: %s", shard_vdir)
            return None

        # read idmap
        idmap_path = shard_vdir / "idmap.json"
        parents_idx_path = shard_vdir / "parents.index.json"
        parents_bin_path = shard_vdir / "parents.adj.bin"
        children_idx_path = shard_vdir / "children.index.json"
        children_bin_path = shard_vdir / "children.adj.bin"

        if not idmap_path.exists():
            log.debug("idmap missing in shard_vdir: %s", shard_vdir)
            return None

        try:
            idmap_raw = json.loads(idmap_path.read_text(encoding="utf-8"))
            idmap = {str(k): int(v) for k, v in idmap_raw.items()}
        except Exception:
            log.exception("failed parsing idmap.json in %s", shard_vdir)
            return None

        # load parents index & bin as int arrays
        parents_index = {}
        children_index = {}
        try:
            if parents_idx_path.exists() and parents_bin_path.exists():
                parents_index = {int(k): tuple(v) for k, v in json.loads(parents_idx_path.read_text(encoding="utf-8")).items()}
                parents_bytes = parents_bin_path.read_bytes()
                parents_ints = []
                for off in range(0, len(parents_bytes), UINT32_SIZE):
                    parents_ints.append(struct.unpack(UINT32, parents_bytes[off:off + UINT32_SIZE])[0])
            else:
                parents_ints = []
        except Exception:
            log.exception("failed reading parents adjacency in %s", shard_vdir)
            parents_ints = []

        try:
            if children_idx_path.exists() and children_bin_path.exists():
                children_index = {int(k): tuple(v) for k, v in json.loads(children_idx_path.read_text(encoding="utf-8")).items()}
                children_bytes = children_bin_path.read_bytes()
                children_ints = []
                for off in range(0, len(children_bytes), UINT32_SIZE):
                    children_ints.append(struct.unpack(UINT32, children_bytes[off:off + UINT32_SIZE])[0])
            else:
                children_ints = []
        except Exception:
            log.exception("failed reading children adjacency in %s", shard_vdir)
            children_ints = []

        # assemble mapping from int node -> list[int] for parents and children
        parents_map_ints: Dict[int, List[int]] = {}
        for nid_int, oc in parents_index.items():
            off, count = oc
            if count == 0:
                parents_map_ints[nid_int] = []
                continue
            slice_vals = parents_ints[off: off + count]
            parents_map_ints[nid_int] = list(slice_vals)

        children_map_ints: Dict[int, List[int]] = {}
        for nid_int, oc in children_index.items():
            off, count = oc
            if count == 0:
                children_map_ints[nid_int] = []
                continue
            slice_vals = children_ints[off: off + count]
            children_map_ints[nid_int] = list(slice_vals)

        vname = shard_vdir.name
        out_vdir = Path(lmdb_out_root) / vname
        out_vdir.mkdir(parents=True, exist_ok=True)

        try:
            g = GraphLMDBFull(out_vdir, map_size=map_size)
            g.write_bulk_ints(idmap, parents_map_ints, children_map_ints)
            g.close()
            log.info("write_lmdb_from_shard wrote LMDB env at %s", out_vdir)
            return out_vdir
        except Exception:
            log.exception("write_lmdb_from_shard failed for %s", shard_vdir)
            return None

# -------------------------
# Fallback (pure-Python) implementation when lmdb is not installed
# -------------------------
else:
    import shutil
    import time

    def write_lmdb_from_shard(shard_vdir: Path, lmdb_out_root: Path, map_size: int = 1 << 24) -> Optional[Path]:
        """
        Fallback writer: copy the shard_vdir into lmdb_out_root/<vname> and add a metadata file.
        This preserves the same return type/signature as the LMDB-backed function and is safe
        for environments without `lmdb`.
        """
        shard_vdir = Path(shard_vdir)
        if not shard_vdir.exists() or not shard_vdir.is_dir():
            log.debug("shard_vdir missing (fallback): %s", shard_vdir)
            return None

        try:
            lmdb_out_root = Path(lmdb_out_root)
            lmdb_out_root.mkdir(parents=True, exist_ok=True)
            vname = shard_vdir.name
            out_vdir = lmdb_out_root / vname
            if out_vdir.exists():
                out_vdir = lmdb_out_root / f"{vname}-{time.strftime('%Y%m%d%H%M%S')}"
            # copytree
            shutil.copytree(shard_vdir, out_vdir)
            # write metadata so callers can detect this is a stub
            meta = {
                "source_shard": str(shard_vdir),
                "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "type": "lmdb_fallback_stub",
            }
            try:
                (out_vdir / "lmdb_stub_meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
            except Exception:
                log.debug("failed writing lmdb_stub_meta.json to %s", out_vdir)
            log.info("lmdb fallback: wrote stub at %s", out_vdir)
            return out_vdir
        except Exception:
            log.exception("lmdb fallback write_lmdb_from_shard failed for %s", shard_vdir)
            return None
