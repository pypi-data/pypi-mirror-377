# app/core/metrics.py
"""
Minimal metrics collector.

- metrics.increment(name, value=1)
- metrics.get(name) -> int
- metrics.dump() -> dict of all metrics
- Intended for programmatic access; not a full metrics server.
"""

from __future__ import annotations
import threading
from typing import Dict

class MetricsCollector:
    def __init__(self):
        self._lock = threading.RLock()
        self._store: Dict[str, int] = {}

    def increment(self, name: str, value: int = 1) -> None:
        if not name:
            return
        with self._lock:
            self._store[name] = self._store.get(name, 0) + int(value)

    def get(self, name: str) -> int:
        with self._lock:
            return int(self._store.get(name, 0))

    def dump(self) -> Dict[str, int]:
        with self._lock:
            # return a shallow copy
            return dict(self._store)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

# module-level singleton
metrics = MetricsCollector()
