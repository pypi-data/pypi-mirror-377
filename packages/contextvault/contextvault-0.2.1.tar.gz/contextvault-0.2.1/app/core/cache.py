# app/core/cache.py
"""
Simple cache used for integration tests + metrics.

- SimpleCache: LRU-ish cache with thread-safety.
- cache: module-level singleton used by other modules.
- The cache reports hit/miss counts to app.core.metrics.
"""

from collections import OrderedDict
import threading
from typing import Any, Optional, Dict

# Import local metrics collector (best-effort)
try:
    from app.core.metrics import metrics  # type: ignore
except Exception:
    metrics = None  # metrics optional (best-effort)

class SimpleCache:
    def __init__(self, maxsize: int = 4096):
        self.maxsize = int(maxsize)
        self.lock = threading.RLock()
        self._d = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        with self.lock:
            if key in self._d:
                val = self._d.pop(key)
                self._d[key] = val
                self.hits += 1
                # report metric
                try:
                    if metrics is not None:
                        metrics.increment("cache.hits")
                except Exception:
                    pass
                return val
            self.misses += 1
            try:
                if metrics is not None:
                    metrics.increment("cache.misses")
            except Exception:
                pass
            return default

    def set(self, key: Any, value: Any) -> None:
        with self.lock:
            if key in self._d:
                self._d.pop(key)
            self._d[key] = value
            if len(self._d) > self.maxsize:
                try:
                    self._d.popitem(last=False)
                except Exception:
                    pass

    def clear(self) -> None:
        with self.lock:
            self._d.clear()
            self.hits = 0
            self.misses = 0

    def stats(self) -> Dict[str, int]:
        with self.lock:
            return {"hits": self.hits, "misses": self.misses, "entries": len(self._d)}

# module-level cache instance
cache = SimpleCache(maxsize=4096)
