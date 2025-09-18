# tests/test_retention_scheduler.py
import os
import importlib
import time
from pathlib import Path
from app.core.scheduler import RetentionScheduler

def test_scheduler_runs(monkeypatch, tmp_path):
    flag = tmp_path / "flag.txt"
    def fake_cleanup():
        with flag.open("w", encoding="utf-8") as f:
            f.write("ran")
        return {"deleted": 0}

    sched = RetentionScheduler(fake_cleanup, interval_seconds=1)
    sched.start()
    # wait for a couple of intervals
    time.sleep(2.5)
    sched.stop()
    assert flag.exists()
    assert flag.read_text() == "ran"
