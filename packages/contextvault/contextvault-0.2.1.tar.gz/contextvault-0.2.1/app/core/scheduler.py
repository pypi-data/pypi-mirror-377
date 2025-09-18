# app/core/scheduler.py
"""
Lightweight retention scheduler.

Starts a background thread that runs a provided callable at an interval.
Designed to be started/stopped via FastAPI startup/shutdown events.

Config via env:
- RETENTION_INTERVAL_SECONDS (int) default 86400 (24h)
- RETENTION_ENABLED (bool) default true
"""

import threading
import time
import os
import traceback
from typing import Callable, Optional

DEFAULT_INTERVAL = int(os.environ.get("RETENTION_INTERVAL_SECONDS", "86400"))
ENABLED = os.environ.get("RETENTION_ENABLED", "true").lower() not in ("0", "false", "no")

class RetentionScheduler:
    def __init__(self, func: Callable[[], dict], interval_seconds: int = DEFAULT_INTERVAL):
        self.func = func
        self.interval = max(1, int(interval_seconds))
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _loop(self):
        while not self._stop.wait(self.interval):
            try:
                # call function and optionally log/record results
                res = self.func()
                # best-effort print (can be replaced by proper logging)
                print(f"[RetentionScheduler] run at {time.ctime()}: {res}")
            except Exception:
                print("[RetentionScheduler] error running scheduled task:")
                traceback.print_exc()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="retention-scheduler")
        self._thread.start()
        print("[RetentionScheduler] started; interval:", self.interval, "s")

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        print("[RetentionScheduler] stopped")
