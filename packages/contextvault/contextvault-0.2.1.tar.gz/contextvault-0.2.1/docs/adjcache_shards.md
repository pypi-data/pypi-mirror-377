# Adjcache shards — Phase 2 notes

This file documents the per-shard index layout and basic admin commands.

Layout:
- `data/index/adjcache/shards/<shard-id>/v{ts}/`
  - `idmap.json` — node_id -> local-int
  - `parents.index.json` — local-int -> [offset,count]
  - `parents.adj.bin` — packed uint32 adjacency ints
  - `children.*` — same for children
  - `manifest.json` — metadata
  - `current` (in shard root) — pointer to latest v{ts} dir

CLI:
- `python scripts/build_shard_index.py --shard <id> --input events.jsonl`

API:
- `POST /adjcache/shard/{shard_id}/build?input_file=path` — build shard from file or partition streams.
- `GET  /adjcache/shards` — list shards and metadata.

Notes:
- Builds are atomic per-v{ts} and update `current` pointer.
- `AdjCache.load_shard_view()` loads all shard pointers by default.
