# DuckDB Snapshots

How Dango creates read-only database snapshots for safe notebook access.

---

## Why Snapshots?

DuckDB enforces a **single-writer-process** constraint — only one process can hold a write lock at a time. This creates a problem for notebooks:

- **Syncs and dbt transforms** need write access to `data/warehouse.duckdb`
- **Notebooks** need read access to query the data
- Even a `read_only=True` DuckDB connection acquires a shared lock that **blocks write operations** from other processes

Snapshots solve this by giving notebooks their own independent copy of the database. The snapshot is a regular file copy — no DuckDB locks involved — so syncs, dbt, and notebooks can all run concurrently without blocking each other.

For more on DuckDB's concurrency model, see [Core Concepts — DuckDB](../core-concepts/duckdb.md).

## How Snapshots Work

When you open a notebook (and Marimo isn't already running), Dango:

1. **Copies** `data/warehouse.duckdb` to `.dango/snapshots/warehouse_{user}_{timestamp}.duckdb`
2. **Cleans up** old snapshots for the same user (keeps the 3 most recent)
3. **Sets** the `DANGO_NOTEBOOK_DB_PATH` environment variable to point Marimo at the snapshot
4. **Starts** Marimo with the snapshot path in its environment
5. **Connects** — the notebook's `setup` cell reads `DANGO_NOTEBOOK_DB_PATH` and opens the snapshot in read-only mode (see [Templates — DuckDB Connection Pattern](templates.md#duckdb-connection-pattern))

```
data/warehouse.duckdb ──copy──> .dango/snapshots/warehouse_admin_20260515_143022.duckdb
                                           │
                                    Marimo reads from here
                                    (read-only, independent copy)
```

## Snapshot Lifecycle

### File Location

Snapshots are stored in `.dango/snapshots/` inside your project directory:

```
.dango/
└── snapshots/
    ├── warehouse_admin_20260515_143022.duckdb
    ├── warehouse_admin_20260514_091500.duckdb
    └── warehouse_dev_20260515_100000.duckdb
```

### Naming Convention

```
warehouse_{username}_{YYYYMMDD_HHMMSS}.duckdb
```

- **username** — the user who created the snapshot (`cli` for CLI sessions, email address for web UI)
- **timestamp** — when the snapshot was created

### Retention

Dango keeps **3 snapshots per user**. Before creating a new snapshot, older snapshots for the same user are automatically deleted. This prevents disk usage from growing unbounded.

### Size Considerations

Each snapshot is a full copy of `data/warehouse.duckdb`. For a 500 MB warehouse, each snapshot adds 500 MB to disk. With the 3-per-user retention limit:

- **1 user**: up to 1.5 GB of snapshot storage
- **3 users**: up to 4.5 GB of snapshot storage

Monitor disk usage with `dango status` — the health dashboard shows DuckDB capacity including snapshot sizes.

## Managing Snapshots

### Create a Snapshot Manually

```bash
dango snapshot db --user myname
```

Output:

```
✓ Snapshot created: warehouse_myname_20260515_143022.duckdb
  Path: /path/to/project/.dango/snapshots/warehouse_myname_20260515_143022.duckdb
  Size: 42.1 MB
```

This is useful when you want a snapshot without opening a notebook — for example, to share a point-in-time copy with a colleague.

### View Snapshots

Snapshots are files in `.dango/snapshots/`. List them with:

```bash
ls .dango/snapshots/
```

### Cleanup

Old snapshots are cleaned up automatically (3 per user). To manually remove all snapshots:

```bash
rm .dango/snapshots/warehouse_*.duckdb
```

## Read-Only Mode

The snapshot itself is a regular DuckDB file that could theoretically be written to. As defense-in-depth, all notebook templates connect with `config={"access_mode": "read_only"}`:

```python
conn = duckdb.connect(db_path, config={"access_mode": "read_only"})
```

This ensures that even if a notebook cell tries to run `INSERT`, `UPDATE`, `DELETE`, or `DROP`, DuckDB will reject the operation.

## Troubleshooting

### Warehouse not found

```
Warehouse database not found at data/warehouse.duckdb. Run a sync first to create it.
```

The warehouse doesn't exist yet. Sync at least one source first:

```bash
dango sync <source_name>
```

If Marimo starts without a warehouse (e.g., no sources configured yet), the snapshot step is skipped and the notebook's `setup` cell will try to connect to `data/warehouse.duckdb` directly.

### Stale data in notebook

Snapshots are created when Marimo starts. If Marimo is already running when you open a new notebook, it reuses the existing session — no new snapshot is created.

To get fresh data:

1. Release all notebook locks (see [File Locking](file-locking.md))
2. Stop Marimo: `dango stop`
3. Re-open your notebook: `dango notebook open my_analysis` (see [Getting Started](getting-started.md#step-2-open-a-notebook))

This creates a new snapshot from the current warehouse state.

### Disk space concerns

If snapshots are consuming too much disk, you can:

1. Reduce the number of active users (fewer users = fewer snapshots)
2. Manually delete old snapshots: `rm .dango/snapshots/warehouse_*.duckdb`
3. Run `dango cleanup` to free disk space from logs and cache (note: `cleanup` does not remove snapshots — use option 2 for that)

## Related

- [File Locking](file-locking.md) — how snapshots prevent lock conflicts
- [DuckDB & Single-Writer](../core-concepts/duckdb.md) — understanding DuckDB's write model
- [Getting Started with Notebooks](getting-started.md) — notebook basics
