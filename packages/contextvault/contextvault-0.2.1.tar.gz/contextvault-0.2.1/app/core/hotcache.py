# app/core/hotcache.py
from __future__ import annotations
import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Optional, Dict, Tuple
import functools

class HotLRUCache:
    """
    Thread-safe LRU cache with basic metrics.

    Usage:
        cache = HotLRUCache(max_size=1000, default_ttl=60.0)

        # explicit usage
        v = cache.get(key)
        if v is None:
            v = expensive()
            cache.put(key, v)

        # as decorator
        @cache.memoize()
        def expensive(arg1, arg2):
            ...

    Stats:
        cache.hits, cache.misses, cache.evictions, cache.requests
    """

    def __init__(self, max_size: int = 4096, default_ttl: Optional[float] = None):
        self.max_size = int(max_size)
        self.default_ttl = float(default_ttl) if default_ttl is not None else None
        self._lock = threading.RLock()
        # OrderedDict: key -> (value, expiry_ts or None)
        self._data: "OrderedDict[Any, Tuple[Any, Optional[float]]]" = OrderedDict()
        # metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.requests = 0
        self.last_evicted_key = None

    # --------------------
    # core operations
    # --------------------
    def _now(self) -> float:
        return time.time()

    def _is_expired(self, expiry: Optional[float]) -> bool:
        return expiry is not None and expiry <= self._now()

    def get(self, key: Any) -> Any:
        with self._lock:
            self.requests += 1
            item = self._data.get(key)
            if item is None:
                self.misses += 1
                return None
            value, expiry = item
            if self._is_expired(expiry):
                # expired -> remove and count as miss
                try:
                    del self._data[key]
                except KeyError:
                    pass
                self.misses += 1
                return None
            # promote to end (most recently used)
            try:
                self._data.move_to_end(key, last=True)
            except Exception:
                pass
            self.hits += 1
            return value

    def put(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        expiry = None
        if ttl is None:
            ttl = self.default_ttl
        if ttl is not None:
            expiry = self._now() + float(ttl)
        with self._lock:
            if key in self._data:
                # update and move to end
                self._data[key] = (value, expiry)
                try:
                    self._data.move_to_end(key, last=True)
                except Exception:
                    pass
                return
            self._data[key] = (value, expiry)
            # evict if over capacity
            while len(self._data) > self.max_size:
                old_key, _ = self._data.popitem(last=False)  # pop LRU
                self.evictions += 1
                self.last_evicted_key = old_key

    def invalidate(self, key: Any) -> None:
        with self._lock:
            if key in self._data:
                try:
                    del self._data[key]
                except KeyError:
                    pass

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self.hits = self.misses = self.evictions = self.requests = 0
            self.last_evicted_key = None

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "max_size": self.max_size,
                "current_size": len(self._data),
                "hits": int(self.hits),
                "misses": int(self.misses),
                "evictions": int(self.evictions),
                "requests": int(self.requests),
                "last_evicted_key": repr(self.last_evicted_key),
            }

    # --------------------
    # decorator helper
    # --------------------
    def memoize(self, ttl: Optional[float] = None):
        """
        Return a decorator that memoizes function calls using the cache.
        Cache key is (func.__module__, func.__name__, args, kwargs) which is
        converted to a repr string; this is simple and robust for debugging
        but not the most efficient keying scheme (adjust if needed).
        """

        def decorator(fn: Callable):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                # build a simple key - keep it deterministic
                try:
                    k = (fn.__module__, fn.__name__, args, tuple(sorted(kwargs.items())))
                except Exception:
                    # fallback to repr
                    k = (fn.__module__, fn.__name__, repr(args), repr(kwargs))
                key = repr(k)
                val = self.get(key)
                if val is not None:
                    return val
                # compute and store
                res = fn(*args, **kwargs)
                self.put(key, res, ttl=ttl)
                return res

            def cache_clear():
                # allow clearing by attribute
                try:
                    self.invalidate(repr((fn.__module__, fn.__name__, (), ())))
                except Exception:
                    pass

            wrapper.cache_clear = cache_clear  # type: ignore
            return wrapper

        return decorator
