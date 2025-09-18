# app/core/graph_mmap.py
from __future__ import annotations
import json
import struct
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import mmap
import os

UINT32 = "<I"


class MMapAdjacency:
    """
    Memory-map wrapper that provides neighbor slices for an adjacency binary file
    and an index (offsets,length) mapping.
    """
    def __init__(self, bin_path: Path, index_json: Path):
        self.bin_path = bin_path
        self.index_json = index_json
        self._bin_f = None
        self._mmap = None
        self.index: Dict[str, Tuple[int, int]] = {}
        self._load()

    def _load(self):
        # load index
        with self.index_json.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        # index maps string id to [offset, length]
        self.index = {k: (int(v[0]), int(v[1])) for k, v in raw.items()}
        # open and mmap binary adjacency
        self._bin_f = self.bin_path.open("rb")
        self._mmap = mmap.mmap(self._bin_f.fileno(), 0, access=mmap.ACCESS_READ)

    def get_neighbors_ids(self, nid: int) -> List[int]:
        entry = self.index.get(str(nid))
        if not entry:
            return []
        off, length = entry
        if length == 0:
            return []
        # each value is a uint32, little-endian
        start = off * 4
        end = start + length * 4
        data = self._mmap[start:end]
        res = []
        for i in range(0, len(data), 4):
            v = struct.unpack(UINT32, data[i:i+4])[0]
            res.append(v)
        return res

    def close(self):
        try:
            if self._mmap:
                self._mmap.close()
            if self._bin_f:
                self._bin_f.close()
        except Exception:
            pass


class GraphMMap:
    """
    High-level reader that loads idmap.json and parents/children adjacency.
    Supports atomic reload when index publishes a new 'current' pointer.
    """
    def __init__(self, index_root: Path):
        self.index_root = Path(index_root)
        self.current_ptr = None  # directory name under index_root
        self._lock = threading.RLock()
        self._idmap: Dict[str, int] = {}
        self._revmap: Dict[int, str] = {}
        self.parents: Optional[MMapAdjacency] = None
        self.children: Optional[MMapAdjacency] = None
        self.manifest = {}
        self._load_current_index()

    def _read_current_pointer(self) -> Optional[str]:
        # pointer file contains the name of current index dir (e.g., v202401...)
        ptr = self.index_root / "current"
        if ptr.exists():
            try:
                return ptr.read_text(encoding="utf-8").strip()
            except Exception:
                return None
        # fallback: pick the latest v* dir
        candidates = sorted([p.name for p in self.index_root.iterdir() if p.is_dir() and p.name.startswith("v")], reverse=True)
        return candidates[0] if candidates else None

    def _load_index_dir(self, dir_name: str):
        base = self.index_root / dir_name
        if not base.exists():
            raise FileNotFoundError(base)
        # load idmap
        idmap_path = base / "idmap.json"
        if not idmap_path.exists():
            raise FileNotFoundError(idmap_path)
        try:
            data = json.loads(idmap_path.read_text(encoding="utf-8"))
            idmap = {k: int(v) for k, v in data.items()}
        except Exception:
            idmap = {}
        revmap = {int(v): k for k, v in idmap.items()}

        # load adjacency
        parents_bin = base / "parents.adj.bin"
        parents_idx = base / "parents.index.json"
        children_bin = base / "children.adj.bin"
        children_idx = base / "children.index.json"

        parents = MMapAdjacency(parents_bin, parents_idx)
        children = MMapAdjacency(children_bin, children_idx)

        manifest = {}
        mf = base / "manifest.json"
        if mf.exists():
            try:
                manifest = json.loads(mf.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}

        return idmap, revmap, parents, children, manifest

    def _load_current_index(self):
        dir_name = self._read_current_pointer()
        if not dir_name:
            return
        with self._lock:
            try:
                idmap, revmap, parents, children, manifest = self._load_index_dir(dir_name)
                # swap in atomically
                old_parents, old_children = self.parents, self.children
                self._idmap = idmap
                self._revmap = revmap
                self.parents = parents
                self.children = children
                self.manifest = manifest
                self.current_ptr = dir_name
                # close old mmaps
                try:
                    if old_parents:
                        old_parents.close()
                    if old_children:
                        old_children.close()
                except Exception:
                    pass
            except Exception:
                # load failed; keep previous
                return

    def reload_if_new(self):
        # check pointer; if changed, reload
        new_ptr = self._read_current_pointer()
        if new_ptr and new_ptr != self.current_ptr:
            self._load_current_index()

    def _id_for(self, context_id: str) -> Optional[int]:
        return self._idmap.get(context_id)

    def _str_for(self, nid: int) -> Optional[str]:
        return self._revmap.get(int(nid))

    def get_parents(self, context_id: str) -> List[str]:
        with self._lock:
            nid = self._id_for(context_id)
            if nid is None or not self.parents:
                return []
            ids = self.parents.get_neighbors_ids(nid)
            return [self._str_for(i) for i in ids if self._str_for(i) is not None]

    def get_children(self, context_id: str) -> List[str]:
        with self._lock:
            nid = self._id_for(context_id)
            if nid is None or not self.children:
                return []
            ids = self.children.get_neighbors_ids(nid)
            return [self._str_for(i) for i in ids if self._str_for(i) is not None]

    def trace(self, context_id: str, direction: str = "up", max_depth: int = 5) -> Dict[str, List[List[str]]]:
        if direction not in ("up", "down"):
            raise ValueError("direction must be 'up' or 'down'")
        with self._lock:
            nid = self._id_for(context_id)
            if nid is None:
                return {"levels": []}
            get_neighbors = (lambda x: self.parents.get_neighbors_ids(x)) if direction == "up" else (lambda x: self.children.get_neighbors_ids(x))
            visited = set([nid])
            current = [nid]
            levels = []
            for depth in range(max_depth):
                next_level = []
                for node in current:
                    for nb in get_neighbors(node):
                        if nb in visited:
                            continue
                        visited.add(nb)
                        next_level.append(nb)
                if not next_level:
                    break
                levels.append([self._str_for(n) for n in next_level if self._str_for(n) is not None])
                current = next_level
            return {"levels": levels}

    def stats(self) -> Dict[str, int]:
        return {
            "node_count": len(self._idmap),
            "current_index": self.current_ptr or "",
            **({} if not self.manifest else self.manifest)
        }
