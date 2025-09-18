from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Optional

class ShardRegistry:
    """
    Simple file-backed shard registry.
    Stores metadata per-shard and a pointer to the current v{ts}.
    Registry file: <index_root>/shards/registry.json
    """

    def __init__(self, index_root: Path):
        self.index_root = Path(index_root)
        self.shards_dir = self.index_root / "shards"
        self.registry_path = self.shards_dir / "registry.json"
        self._data: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.registry_path.exists():
            try:
                self._data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def _atomic_write(self):
        tmp = self.registry_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
        os.replace(str(tmp), str(self.registry_path))

    def refresh_from_disk(self) -> Dict[str, dict]:
        """
        Scan shards/ directory and populate registry entries for each shard found.
        """
        if not self.shards_dir.exists():
            self._data = {}
            self._atomic_write()
            return self._data
        out = {}
        for shard_dir in sorted([p for p in self.shards_dir.iterdir() if p.is_dir()]):
            cur = shard_dir / "current"
            cur_name = cur.read_text(encoding="utf-8").strip() if cur.exists() else None
            vdir = shard_dir / cur_name if cur_name else None
            node_count = None
            last_build = None
            if vdir and vdir.exists():
                mf = vdir / "manifest.json"
                if mf.exists():
                    try:
                        mfj = json.loads(mf.read_text(encoding="utf-8"))
                        node_count = mfj.get("node_count")
                        last_build = mfj.get("created")
                    except Exception:
                        pass
            out[shard_dir.name] = {
                "shard_id": shard_dir.name,
                "current": cur_name,
                "node_count": node_count,
                "last_build": last_build,
            }
        self._data = out
        self._atomic_write()
        return self._data

    def list_shards(self) -> Dict[str, dict]:
        self._load()
        return self._data

    def get_shard(self, shard_id: str) -> Optional[dict]:
        self._load()
        return self._data.get(shard_id)
