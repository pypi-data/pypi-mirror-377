# Index format (prototype)

This document describes the prototype index layout produced by `scripts/build_graph_index.py`
and consumed by `app/core/graph_mmap.py`.

Directory layout (one published index version):
data/index/v{timestamp}/
manifest.json # { "version": "...", "node_count": N, "edge_count": E, "created": "ISO" }
idmap.json # {"context_string": id (int), ...} OR idmap.lmdb if LMDB used
parents.adj.bin # uint32 array of concatenated parent node ids (little-endian)
parents.index.json # {"<id>": [offset, length], ...} offsets are uint32 counts (index into parents.adj.bin)
children.adj.bin
children.index.json

Notes:

- `id` values are contiguous uint32 allocated by the builder (0..N-1).
- `parents.adj.bin` and `children.adj.bin` store packed 4-byte unsigned ints (little-endian).
  Each node's neighbors are contiguous; `index.json` maps node id to `[offset, length]` where:
  - `offset` is the starting index (in numbers, not bytes) into the adj.bin array
  - `length` is the number of uint32 neighbor entries
- Index `offset` × 4 gives byte offset in the `.bin` file.
- The builder writes into `data/index/v{ts}/...` and then atomically renames that directory
  into `data/index/current` (or replaces a symlink). `graph_mmap` watches the `manifest.json`
  path and can reload atomically.

This prototype uses JSON for the index metadata (for readability and easy testing).
For larger production deployments you can replace `index.json` with a compact binary index
(e.g. a flat uint64 offset table) and store `idmap` in LMDB for fast lookups.
