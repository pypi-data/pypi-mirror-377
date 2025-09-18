# 📜 Changelog

## [v1.0.0 Candidate] - 2025-09-12

### 🚀 Added

- **SQLite inverted index** (`app/core/index_sqlite.py`) with migration from JSON index.
  - Scales keyword search to 10k+ contexts.
  - Migration script: `scripts/migrate_json_to_sqlite.py`.
- **Audit logging enhancements**
  - Append-only JSON-lines with rotation & retention (size- and date-based).
  - Admin-only endpoints: `/admin/audit/tail`, `/admin/audit/export`.
  - Lazy `get_audit()` to honor env var changes.
- **Retention policies & scheduler**
  - `cleanup_expired()` + `delete_versions_older_than()` in `app/core/retention.py`.
  - Background scheduler (`RetentionScheduler`) wired to FastAPI startup/shutdown.
- **Health endpoint** extended with deep index consistency check (JSON vs SQLite).
  - Reports mismatches, `ok: true/false`.

### ✅ Changed

- Project status bumped to **v1.0.0 Candidate (SaaS-ready)**.
- Updated `README.md` with SaaS features, examples for audit tail/export, updated project structure.

### 🛠 Fixed

- Tests for audit rotation, retention scheduler, and health consistency stabilized.
- JSON index corruption handling: added `scripts/find_bad_json.py` and rebuild script from SQLite.

### 📦 Deferred (Future Sprint)

- Video handling (hash-linked refs + thumbnails).
- Incremental versioning (diff storage).
- Multi-tenant foundation (namespaces / DB separation).
- Audit UI (browser tail/export).

---

## [v0.9] - 2025-06-30

- Core serialization to PNG implemented.
- Basic metadata, versioning, and search (JSON inverted index).
- Raw/file contexts, collections, and snapshots supported.
- Minimal CLI and health endpoints.
