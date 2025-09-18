# app/core/adjcache.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator
from collections import defaultdict
import struct
import mmap
import threading
from datetime import datetime

# safe imports for optional project helpers
try:
    from app.core.storage.filelog import iter_events
except Exception:
    iter_events = None

try:
    from app.core.storage.partitioned_filelog import iter_partition_events
except Exception:
    iter_partition_events = None

UINT32 = "<I"
UINT32_SIZE = 4


def _now_ts() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H%M%S")


# -------------------------
# Module-level tiny LRU with stats
# -------------------------
class _TinyLRU:
    def __init__(self, capacity: int = 2048):
        self.capacity = int(capacity)
        self._d = {}
        self._order = []
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()

    def get(self, k):
        with self._lock:
            v = self._d.get(k)
            if v is not None:
                # move to end (most-recent)
                try:
                    self._order.remove(k)
                except Exception:
                    pass
                self._order.append(k)
                self._hits += 1
            else:
                self._misses += 1
            return v

    def put(self, k, v):
        with self._lock:
            if k in self._d:
                self._d[k] = v
                try:
                    self._order.remove(k)
                except Exception:
                    pass
                self._order.append(k)
                return
            if len(self._order) >= self.capacity:
                old = self._order.pop(0)
                try:
                    del self._d[old]
                except Exception:
                    pass
            self._d[k] = v
            self._order.append(k)

    def clear(self):
        with self._lock:
            self._d.clear()
            self._order.clear()
            self._hits = 0
            self._misses = 0

    def stats(self):
        with self._lock:
            return {"hits": int(self._hits), "misses": int(self._misses), "size": len(self._d)}


# exported module-level cache used by tests / API
_ADJ_CACHE = _TinyLRU(2048)


# -------------------------
# AdjCache implementation
# -------------------------
class AdjCache:
    """
    Lightweight adjacency cache with optional shard-aware mmap-backed reads.

    - build_from_streams: builds an in-memory adjacency (parents/children) and idmap
    - dump_mmap_index/load_mmap_index: persist and load single-index mmap format
    - load_shard_view: discover shard vdirs under index_root/shards/<shard>/v*/ and register them for shard mmap reads.
    """

    def __init__(self, index_root: Path = Path("data") / "index" / "adjcache", mmap_mode: bool = False):
        self.index_root = Path(index_root)
        self.mmap_mode = bool(mmap_mode)
        # in-memory stores
        self._parents: Dict[str, List[str]] = {}
        self._children: Dict[str, List[str]] = {}
        # idmap (node_id -> int) used for mmap
        self._idmap: Dict[str, int] = {}
        self._revmap: List[str] = []
        # mmap artifacts for the single-index mode
        self._parents_index: Dict[int, Tuple[int, int]] = {}
        self._children_index: Dict[int, Tuple[int, int]] = {}
        self._parents_mmap = None
        self._children_mmap = None
        self._parents_file = None
        self._children_file = None
        # shard-aware maps: shard -> idmap/rev/index/mmaps
        self._shard_idmaps: Dict[str, Dict[str, int]] = {}
        self._shard_revmap: Dict[str, List[str]] = {}
        self._shard_parents_index: Dict[str, Dict[int, Tuple[int, int]]] = {}
        self._shard_children_index: Dict[str, Dict[int, Tuple[int, int]]] = {}
        self._shard_parents_mm: Dict[str, Tuple[Path, mmap.mmap]] = {}
        self._shard_children_mm: Dict[str, Tuple[Path, mmap.mmap]] = {}
        # node -> shard routing
        self._node_to_shard: Dict[str, str] = {}
        # lock for reloads
        self._lock = threading.RLock()
        self._loaded_ptr: Optional[str] = None

    # ----------------------
    # Build helpers
    # ----------------------
    def _iter_relationship_events(self) -> Iterator[dict]:
        if iter_events is not None:
            for ev in iter_events("relationships"):
                yield ev
        if iter_partition_events is not None:
            for ev in iter_partition_events("relationships"):
                yield ev

    def build_from_streams(self, events: Optional[Iterator[dict]] = None) -> dict:
        """
        Build adjacency (in-memory) from event iterator or from default relationship streams.
        Returns manifest dict.
        """
        with self._lock:
            parents = defaultdict(list)
            children = defaultdict(list)
            nodes = set()
            it = events if events is not None else self._iter_relationship_events()
            if it is None:
                self._parents = {}
                self._children = {}
                self._idmap = {}
                self._revmap = []
                return {"created": datetime.utcnow().isoformat() + "Z", "node_count": 0, "edges_parents": 0, "edges_children": 0}
            for ev in it:
                if not ev:
                    continue
                if ev.get("event") != "relationship_added":
                    continue
                child = ev.get("child_id") or (ev.get("to") or {}).get("id")
                parent = ev.get("parent_id") or (ev.get("from") or {}).get("id")
                if not child or not parent:
                    continue
                parents[child].append(parent)
                children[parent].append(child)
                nodes.add(child)
                nodes.add(parent)
            # assign
            self._parents = {k: v[:] for k, v in parents.items()}
            self._children = {k: v[:] for k, v in children.items()}
            # create idmap
            idlist = sorted(nodes)
            self._idmap = {nid: i for i, nid in enumerate(idlist)}
            self._revmap = idlist
            manifest = {
                "created": datetime.utcnow().isoformat() + "Z",
                "node_count": len(idlist),
                "edges_parents": sum(len(v) for v in parents.values()),
                "edges_children": sum(len(v) for v in children.values()),
            }
            return manifest

    # ----------------------
    # Simple query API (in-memory) with module-level hot cache integration
    # ----------------------
    def get_parents(self, node_id: str) -> List[str]:
        with self._lock:
            # if node belongs to a shard with mmap, route there (no caching across shards)
            shard = self._node_to_shard.get(node_id)
            cache_key = f"adj:parents:{node_id}"
            if shard:
                # read directly from shard mmap; still put small cache entry
                res = self._read_neighbors_mmap_shard(shard, node_id, side="parents")
                try:
                    _ADJ_CACHE.put(cache_key, res)
                except Exception:
                    pass
                return list(res)
            # check cache first
            try:
                cached = _ADJ_CACHE.get(cache_key)
            except Exception:
                cached = None
            if cached is not None:
                # return a shallow copy to avoid accidental mutation
                return list(cached)
            # not in cache -> read from memory or mmap single-index
            if not self.mmap_mode:
                res = self._parents.get(node_id, [])[:]
            else:
                res = self._read_neighbors_mmap(node_id, side="parents")
            # update cache
            try:
                _ADJ_CACHE.put(cache_key, res)
            except Exception:
                pass
            return list(res)

    def get_children(self, node_id: str) -> List[str]:
        with self._lock:
            shard = self._node_to_shard.get(node_id)
            cache_key = f"adj:children:{node_id}"
            if shard:
                res = self._read_neighbors_mmap_shard(shard, node_id, side="children")
                try:
                    _ADJ_CACHE.put(cache_key, res)
                except Exception:
                    pass
                return list(res)
            try:
                cached = _ADJ_CACHE.get(cache_key)
            except Exception:
                cached = None
            if cached is not None:
                return list(cached)
            if not self.mmap_mode:
                res = self._children.get(node_id, [])[:]
            else:
                res = self._read_neighbors_mmap(node_id, side="children")
            try:
                _ADJ_CACHE.put(cache_key, res)
            except Exception:
                pass
            return list(res)

    def trace(self, node_id: str, direction: str = "up", max_depth: int = 5) -> Dict[str, List[List[str]]]:
        if direction not in ("up", "down"):
            raise ValueError("direction must be 'up' or 'down'")
        with self._lock:
            getn = (self.get_parents if direction == "up" else self.get_children)
            visited = set([node_id])
            current = [node_id]
            levels = []
            for _ in range(max_depth):
                nxt = []
                for n in current:
                    for nb in getn(n):
                        if nb in visited:
                            continue
                        visited.add(nb)
                        nxt.append(nb)
                if not nxt:
                    break
                levels.append(nxt[:])
                current = nxt
            return {"levels": levels}

    # ----------------------
    # Mmap write/read helpers (single-index)
    # ----------------------
    def dump_mmap_index(self, out_root: Optional[Path] = None) -> Path:
        with self._lock:
            out_root = Path(out_root) if out_root else self.index_root
            ts = _now_ts()
            dest = out_root / f"v{ts}"
            dest.mkdir(parents=True, exist_ok=True)
            (dest / "idmap.json").write_text(json.dumps(self._idmap, ensure_ascii=False), encoding="utf-8")

            def write_side(map_src: Dict[str, List[str]], name: str):
                adj = []
                index = {}
                offset = 0
                for nid in self._revmap:
                    lst = map_src.get(nid, [])
                    idxs = [self._idmap[x] for x in lst if x in self._idmap]
                    for v in idxs:
                        adj.append(v)
                    index[str(self._idmap[nid])] = [offset, len(idxs)]
                    offset += len(idxs)
                bin_path = dest / f"{name}.adj.bin"
                with bin_path.open("wb") as bf:
                    for v in adj:
                        bf.write(struct.pack(UINT32, v))
                (dest / f"{name}.index.json").write_text(json.dumps(index), encoding="utf-8")
                return len(self._revmap), len(adj)

            write_side(self._parents, "parents")
            write_side(self._children, "children")
            (dest / "manifest.json").write_text(json.dumps({
                "version": ts,
                "created": datetime.utcnow().isoformat() + "Z",
                "node_count": len(self._revmap)
            }), encoding="utf-8")
            (out_root / "current").write_text(dest.name, encoding="utf-8")
            return dest

    def load_mmap_index(self, index_dir: Optional[Path] = None) -> bool:
        with self._lock:
            root = Path(index_dir) if index_dir else self.index_root
            ptr = root / "current"
            if ptr.exists():
                dirname = ptr.read_text(encoding="utf-8").strip()
                base = root / dirname
            else:
                candidates = sorted([p for p in root.iterdir() if p.is_dir() and p.name.startswith("v")], reverse=True)
                if not candidates:
                    return False
                base = candidates[0]
            idmap_path = base / "idmap.json"
            if not idmap_path.exists():
                return False
            idmap_raw = json.loads(idmap_path.read_text(encoding="utf-8"))
            self._idmap = {str(k): int(v) for k, v in idmap_raw.items()}
            rev = [None] * (max(int(x) for x in self._idmap.values()) + 1)
            for k, v in self._idmap.items():
                rev[v] = k
            self._revmap = rev

            def _load_side(name: str):
                idx_path = base / f"{name}.index.json"
                bin_path = base / f"{name}.adj.bin"
                if not idx_path.exists() or not bin_path.exists():
                    return {}, None
                idx = json.loads(idx_path.read_text(encoding="utf-8"))
                f = bin_path.open("r+b")
                mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                return {int(k): tuple(v) for k, v in idx.items()}, (f, mm)

            idx_parents, parents_pair = _load_side("parents")
            idx_children, children_pair = _load_side("children")
            self._parents_index = idx_parents
            self._children_index = idx_children
            if parents_pair:
                self._parents_file, self._parents_mmap = parents_pair
            else:
                self._parents_file = None
                self._parents_mmap = None
            if children_pair:
                self._children_file, self._children_mmap = children_pair
            else:
                self._children_file = None
                self._children_mmap = None
            self._loaded_ptr = base.name
            self.mmap_mode = True
            return True

    def _read_neighbors_mmap(self, node_id: str, side: str = "parents") -> List[str]:
        if node_id not in self._idmap:
            return []
        nid = self._idmap[node_id]
        if side == "parents":
            idx = self._parents_index.get(nid)
            mm = self._parents_mmap
            rev = self._revmap
        else:
            idx = self._children_index.get(nid)
            mm = self._children_mmap
            rev = self._revmap
        if not idx or mm is None:
            return []
        offset, count = idx
        if count == 0:
            return []
        start = offset * UINT32_SIZE
        end = (offset + count) * UINT32_SIZE
        raw = mm[start:end]
        res = []
        for i in range(0, len(raw), UINT32_SIZE):
            v = struct.unpack(UINT32, raw[i : i + UINT32_SIZE])[0]
            res.append(rev[v])
        return res

    # ----------------------
    # Shard helpers
    # ----------------------
    def load_shard_view(self, shards_root: Optional[Path] = None) -> bool:
        with self._lock:
            root = shards_root if shards_root else (self.index_root.parent / "shards" if self.index_root else Path("data") / "index" / "shards")
            if self.index_root and (self.index_root / "shards").exists():
                root = self.index_root / "shards"
            if not root.exists() or not root.is_dir():
                return False
            loaded_any = False
            for shard_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
                try:
                    vdirs = sorted([d for d in shard_dir.iterdir() if d.is_dir() and d.name.startswith("v")], reverse=True)
                    if not vdirs:
                        continue
                    vdir = vdirs[0]
                    idmap_path = vdir / "idmap.json"
                    if not idmap_path.exists():
                        continue
                    idmap_raw = json.loads(idmap_path.read_text(encoding="utf-8"))
                    idmap = {str(k): int(v) for k, v in idmap_raw.items()}
                    rev = [None] * (max(int(x) for x in idmap.values()) + 1)
                    for k, v in idmap.items():
                        rev[v] = k

                    def _load_side(name: str):
                        idx_path = vdir / f"{name}.index.json"
                        bin_path = vdir / f"{name}.adj.bin"
                        if not idx_path.exists() or not bin_path.exists():
                            return {}, None
                        idx_raw = json.loads(idx_path.read_text(encoding="utf-8"))
                        idx = {int(k): tuple(v) for k, v in idx_raw.items()}
                        f = bin_path.open("r+b")
                        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                        return idx, (f, mm)

                    p_idx, p_pair = _load_side("parents")
                    c_idx, c_pair = _load_side("children")

                    shard = shard_dir.name
                    self._shard_idmaps[shard] = idmap
                    self._shard_revmap[shard] = rev
                    self._shard_parents_index[shard] = p_idx
                    self._shard_children_index[shard] = c_idx
                    if p_pair:
                        self._shard_parents_mm[shard] = (vdir / "parents.adj.bin", p_pair[1])
                    if c_pair:
                        self._shard_children_mm[shard] = (vdir / "children.adj.bin", c_pair[1])
                    for nid in idmap.keys():
                        self._node_to_shard[nid] = shard
                    loaded_any = True
                except Exception:
                    continue
            if loaded_any:
                self.mmap_mode = True
            return loaded_any

    def _read_neighbors_mmap_shard(self, shard_id: str, node_id: str, side: str = "parents") -> List[str]:
        if shard_id not in self._shard_idmaps:
            return []
        idmap = self._shard_idmaps.get(shard_id)
        rev = self._shard_revmap.get(shard_id)
        idx_map = self._shard_parents_index.get(shard_id) if side == "parents" else self._shard_children_index.get(shard_id)
        mm_pair = self._shard_parents_mm.get(shard_id) if side == "parents" else self._shard_children_mm.get(shard_id)
        if not idmap or node_id not in idmap:
            return []
        nid = idmap[node_id]
        if not idx_map or mm_pair is None:
            return []
        idx = idx_map.get(nid)
        if not idx:
            return []
        offset, count = idx
        if count == 0:
            return []
        fpath, mm = mm_pair
        start = offset * UINT32_SIZE
        end = (offset + count) * UINT32_SIZE
        raw = mm[start:end]
        res = []
        for i in range(0, len(raw), UINT32_SIZE):
            v = struct.unpack(UINT32, raw[i : i + UINT32_SIZE])[0]
            res.append(rev[v])
        return res

    # ----------------------
    # Utility
    # ----------------------
    def stats(self) -> dict:
        with self._lock:
            return {
                "mmap_mode": self.mmap_mode,
                "nodes_in_mem": len(self._revmap) if self._revmap else len(self._idmap),
                "parents_loaded": len(self._parents) if self._parents else len(self._parents_index),
                "children_loaded": len(self._children) if self._children else len(self._children_index),
                "loaded_ptr": self._loaded_ptr,
                "shards_loaded": list(self._shard_idmaps.keys()),
                "node_routing_entries": len(self._node_to_shard),
            }


# module-level AdjCache singleton (tests may import _ADJ)
try:
    _ADJ = AdjCache(index_root=Path("data") / "index")
except Exception:
    _ADJ = AdjCache()
