---
name: sqlite
description: Recommended SQLite defaults (PRAGMAs and STRICT tables). Use when setting up a new project that uses SQLite, or when adding new SQLite tables to an existing project.
---

Apply these when starting a new SQLite project or adding tables. They are the sane defaults SQLite ships without.

## Connection PRAGMAs

Run these on **every new connection** (except `journal_mode`, see below). They are per-connection state, not stored in the DB file. If your library has a "connection init" hook, put them there.

```sql
PRAGMA journal_mode = WAL;      -- set once, persists in the DB file
PRAGMA busy_timeout = 5000;     -- wait 5s on a locked DB instead of erroring
PRAGMA synchronous = NORMAL;    -- safe to lower from FULL only under WAL
PRAGMA foreign_keys = ON;       -- SQLite ignores FK constraints unless you enable this
```

## Tables

Create tables as `STRICT` so column types are enforced:

```sql
CREATE TABLE user (id INTEGER PRIMARY KEY, name TEXT NOT NULL) STRICT;
```

## Gotchas

- **`foreign_keys`, `busy_timeout`, `synchronous` reset per connection.** Missing them on any connection silently drops the behavior (e.g. FK constraints stop being enforced). Set them on connection open.
- **`journal_mode = WAL` is different**: it persists in the DB file, so set it once. WAL needs the DB on **local disk** (breaks on network filesystems) and adds `-wal` and `-shm` sidecar files next to the DB.
- **`synchronous = NORMAL` durability**: an OS crash or power loss can lose the last few committed transactions. The DB stays consistent (no corruption) — only the tail is lost. `NORMAL` is almost always the right choice; `FULL` is rarely needed. If you genuinely cannot afford to lose any committed write, you shouldn't be on SQLite at all — use a DB replicated across regions.
- **STRICT allows only `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB`, `ANY`.** No `VARCHAR`, `DATETIME`, `BOOLEAN`, etc. Use `ANY` for a column that needs to hold mixed types.
