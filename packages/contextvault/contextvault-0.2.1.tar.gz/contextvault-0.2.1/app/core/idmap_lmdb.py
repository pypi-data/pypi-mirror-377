# app/core/idmap_lmdb.py
"""
Light wrapper to provide an idmap store. Uses lmdb if available, otherwise falls
back to a simple JSON file map.

API:
  - IdMap.open(path) -> IdMap instance
  - idmap.get_id(str) -> int or None
  - idmap.get_str(id) -> str or None
  - idmap.put(str, id) -> None
  - idmap.sync() -> persist (no-op for LMDB)
  - idmap.close()
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import lmdb
except Exception:
    lmdb = None  # optional


class IdMapJSON:
    def __init__(self, path: Path):
        self.path = path
        self._map: Dict[str, int] = {}
        self._rev: Dict[int, str] = {}
        if path.exists():
            try:
                self._map = json.loads(path.read_text(encoding="utf-8"))
                for k, v in self._map.items():
                    self._rev[int(v)] = k
            except Exception:
                self._map = {}
                self._rev = {}

    def get_id(self, s: str) -> Optional[int]:
        return self._map.get(s)

    def get_str(self, i: int) -> Optional[str]:
        return self._rev.get(int(i))

    def put(self, s: str, i: int) -> None:
        self._map[s] = int(i)
        self._rev[int(i)] = s

    def sync(self) -> None:
        self.path.write_text(json.dumps(self._map, ensure_ascii=False), encoding="utf-8")

    def close(self) -> None:
        self.sync()


class IdMapLMDB:
    def __init__(self, path: Path, map_size: int = 1 << 30):
        # path is directory; store env in path / "idmap.lmdb"
        env_path = path
        env_path.mkdir(parents=True, exist_ok=True)
        self.env = lmdb.open(str(env_path), map_size=map_size, max_dbs=1, subdir=True)
        self.db = self.env.open_db(b"idmap")

    def get_id(self, s: str) -> Optional[int]:
        with self.env.begin(db=self.db) as txn:
            b = txn.get(s.encode("utf-8"))
            if not b:
                return None
            return int(b.decode("ascii"))

    def get_str(self, i: int) -> Optional[str]:
        # LMDB reverse lookup would require another db; for now, not implemented
        return None

    def put(self, s: str, i: int) -> None:
        with self.env.begin(write=True, db=self.db) as txn:
            txn.put(s.encode("utf-8"), str(int(i)).encode("ascii"))

    def sync(self) -> None:
        pass

    def close(self) -> None:
        self.env.close()


def open_idmap(path: Path) -> Any:
    """
    Returns an IdMap instance. If lmdb is present, returns IdMapLMDB(path),
    otherwise returns IdMapJSON(path/'idmap.json').
    """
    if lmdb is not None:
        return IdMapLMDB(path)
    else:
        return IdMapJSON(path / "idmap.json")
