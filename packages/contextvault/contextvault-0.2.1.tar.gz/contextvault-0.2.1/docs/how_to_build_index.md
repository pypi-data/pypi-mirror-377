# How to build and publish the graph index

1. Ensure your relationships log exists:

   - `data/log/relationships.jsonl`

2. Run the builder:
   ```bash
   python scripts/build_graph_index.py --log data/log/relationships.jsonl --out data/index --publish
   ```
   pytest tests/core/test_graph_mmap.py -q
   pytest tests/scripts/test_build_graph_index.py -q

---

## `tools/benchmark_index_vs_jsonl.py`

```python
#!/usr/bin/env python3
"""
Simple micro-benchmark comparing JSONL adjacency rebuild vs mmap reader for get_parents.
Create a synthetic log and compare:
  - Time to rebuild adjacency dict (python) and query
  - Time to build index + mmap reader query

This is a simple tool to get rough numbers.
"""
from __future__ import annotations
import time
import json
from pathlib import Path
from scripts.build_graph_index import build_index
from app.core.graph import _build_adjacency
from app.core.graph_mmap import GraphMMap
import random

def make_synthetic(log_path: Path, node_count=10000, avg_deg=3):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    import uuid
    nodes = [f"n{idx}" for idx in range(node_count)]
    with log_path.open("w", encoding="utf-8") as f:
        for i in range(node_count):
            for _ in range(avg_deg):
                child = random.choice(nodes)
                parent = random.choice(nodes)
                ev = {"event":"relationship_added","child_id":child,"parent_id":parent,"rel_type":"parent","ts":"2025-01-01T00:00:00Z"}
                f.write(json.dumps(ev) + "\n")
    return nodes

def benchmark(tmp_dir: Path):
    log = tmp_dir / "relationships.jsonl"
    nodes = make_synthetic(log, node_count=2000, avg_deg=3)
    # benchmark JSONL rebuild
    t0 = time.time()
    parents_map, children_map = _build_adjacency(log)
    t1 = time.time()
    print("JSONL rebuild time:", t1 - t0)
    # pick random queries
    queries = random.sample(nodes, 100)
    tq0 = time.time()
    for q in queries:
        _ = parents_map.get(q, [])
    tq1 = time.time()
    print("JSONL query loop time (100):", tq1 - tq0)

    # build index
    out = tmp_dir.parent / "index"
    dest, manifest = build_index(log, out)
    # publish pointer
    (out / "current").write_text(dest.name, encoding="utf-8")
    gm = GraphMMap(out)
    t2 = time.time()
    # mmap query
    tq2_0 = time.time()
    for q in queries:
        _ = gm.get_parents(q)
    tq2_1 = time.time()
    print("mmap query loop time (100):", tq2_1 - tq2_0)
    print("manifest:", manifest)

if __name__ == "__main__":
    import sys
    tmp = Path("tmp_bench")
    benchmark(tmp)
```
