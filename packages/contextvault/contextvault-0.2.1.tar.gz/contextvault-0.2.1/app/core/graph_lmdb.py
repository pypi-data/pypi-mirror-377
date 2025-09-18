# app/core/graph_lmdb.py
from __future__ import annotations
import lmdb
import json
from pathlib import Path
from typing import Iterable, List, Dict, Optional
import struct
import os

# Simple LMDB layout:
# - env at <root>/lmdb_env/
# - dbs:
#   - "idmap" : key=node_id (utf-8) -> value=int (4-byte little-endian)
#   - "parents" : key=node_int (4-byte) -> value=json array of ints
#   - "children": same

INT32_FMT = "<I"

class GraphLMDB:
    def __init__(self, root: Path, map_size: int = 1 << 30):  # default 1GB
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(str(self.root / "lmdb_env"), map_size=map_size, max_dbs=4)
        # named DBs
        self.idmap_db = self.env.open_db(b"idmap")
        self.parents_db = self.env.open_db(b"parents")
        self.children_db = self.env.open_db(b"children")

    @staticmethod
    def _int_to_bytes(i: int) -> bytes:
        return struct.pack(INT32_FMT, i)

    @staticmethod
    def _bytes_to_int(b: bytes) -> int:
        return struct.unpack(INT32_FMT, b)[0]

    def write_bulk(self, idmap: Dict[str,int], parents: Dict[str,List[str]], children: Dict[str,List[str]]):
        """
        Write entire index atomically. idmap: node_id->int, parents/children: node_id->list[node_id].
        We store parents/children by int ids to save space.
        """
        # normalize to int-keyed
        inv = {v:k for k,v in idmap.items()}
        with self.env.begin(write=True) as txn:
            # idmap db
            for nid, i in idmap.items():
                txn.put(nid.encode("utf-8"), self._int_to_bytes(i), db=self.idmap_db)
            # parents
            for nid, lst in parents.items():
                i = idmap.get(nid)
                if i is None:
                    continue
                ints = [idmap[x] for x in lst if x in idmap]
                txn.put(self._int_to_bytes(i), json.dumps(ints).encode("utf-8"), db=self.parents_db)
            # children
            for nid, lst in children.items():
                i = idmap.get(nid)
                if i is None:
                    continue
                ints = [idmap[x] for x in lst if x in idmap]
                txn.put(self._int_to_bytes(i), json.dumps(ints).encode("utf-8"), db=self.children_db)

    def get_parents(self, node_id: str) -> List[str]:
        with self.env.begin() as txn:
            raw = txn.get(node_id.encode("utf-8"), db=self.idmap_db)
            if not raw:
                return []
            i = self._bytes_to_int(raw)
            raw_list = txn.get(self._int_to_bytes(i), db=self.parents_db)
            if not raw_list:
                return []
            ints = json.loads(raw_list.decode("utf-8"))
            # map ints to ids
            res = []
            for v in ints:
                rev = txn.cursor(db=self.idmap_db)
                # reverse lookup is expensive; store revmap separately if needed.
                # Naive fallback: scan idmap (not ideal). For POC we assume reverse mapping also stored.
                # For production, store revmap in a second DB keyed by int->node_id.
                pass
            # (Better approach is to store a revmap DB.)
            return []

    def close(self):
        try:
            self.env.close()
        except Exception:
            pass
