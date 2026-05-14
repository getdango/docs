# DuckDB & Single-Writer

DuckDB is Dango's embedded analytical database. It stores all your ingested data locally in a single file (`data/warehouse.duckdb`) and provides fast SQL queries without requiring a separate database server. However, DuckDB enforces a **single-writer** constraint: only one process can write to the database at a time.

This page explains how Dango manages this constraint so that syncs, transformations, notebooks, and Metabase can all work together without conflicts.

## Overview

DuckDB uses file-level locking. When a process opens the database for writing, it acquires an exclusive lock on the file. Any other process that tries to write will fail immediately. Even read-only connections can interfere: a `read_only=True` connection acquires a shared lock that blocks exclusive (write) locks from other processes.

Dango handles this with three mechanisms:

1. **DbtLock** &mdash; a file-based lock that serializes all write operations (syncs and dbt runs)
2. **Read-only snapshots** &mdash; separate database copies for notebooks
3. **Docker `:ro` mounts** &mdash; filesystem-level read-only access for Metabase

## How Dango Manages Write Access

All write operations go through the **DbtLock** system (`dango/utils/dbt_lock.py`). This is a file-based lock using OS-level primitives (`fcntl.flock()` on Unix/macOS, `msvcrt.locking()` on Windows).

### Lock files

The lock uses two files in your project directory:

| File | Purpose |
|------|---------|
| `.dango/state/dbt.lock` | The actual file handle for OS-level locking |
| `.dango/state/dbt.lock.json` | Metadata about the lock holder |

The lock info file contains details about who holds the lock:

```json
{
  "pid": 12345,
  "source": "ui",
  "operation": "sync google_sheets",
  "started_at": "2026-05-14T10:30:00",
  "hostname": "my-laptop"
}
```

### Stale lock detection

If a process crashes while holding the lock, the lock file remains on disk. Dango automatically detects and cleans up stale locks before every lock acquisition attempt:

1. Reads the PID from `.dango/state/dbt.lock.json`
2. Checks if a process with that PID is still running (using `psutil`)
3. If the process is dead, removes both lock files

This means stale locks are cleaned up automatically &mdash; you should rarely need to intervene manually.

## Sync Queuing

When you click **Sync Now** in the web UI while another sync or dbt run is already in progress, the new sync doesn't fail immediately. Instead, it **waits up to 5 minutes** for the lock to become available.

The queuing behavior:

- The sync enters a `lock_waiting` state (visible in the UI via WebSocket updates)
- It retries acquiring the lock every 5 seconds
- If the lock becomes available within 5 minutes, the sync proceeds normally
- If the timeout expires, the sync fails with a message identifying the current lock holder

=== "Web UI"

    Web-triggered syncs wait up to **300 seconds** (5 minutes) before timing out.

=== "CLI"

    CLI syncs (`dango sync`) fail immediately if the lock is held. They do not queue.

??? info "How sync subprocesses work"
    Syncs run in a separate subprocess to keep the DuckDB write lock out of the web server process. Progress is tracked via `.dango/state/sync_status_{sync_id}.json` files that are written atomically. The web UI receives real-time updates through WebSocket events.

## Notebooks

Marimo notebooks need to query your warehouse data, but a direct `read_only=True` connection would acquire a shared lock that blocks write operations (syncs and dbt runs) in other processes.

### Read-only snapshots

Instead of connecting directly, Dango creates a **snapshot copy** of the database for each notebook session:

- **Location:** `.dango/snapshots/`
- **Naming:** `warehouse_{username}_{YYYYMMDD_HHMMSS}.duckdb`
- **Retention:** 3 snapshots per user (oldest are deleted automatically)

When you open a notebook, Dango copies `data/warehouse.duckdb` to the snapshots directory using `shutil.copy2()`. The notebook connects to this copy, so it can read freely without interfering with write operations.

!!! tip "Snapshots are point-in-time"
    Your notebook sees data as it was when the snapshot was created. If a sync runs while you're working, your notebook won't see the new data until you create a fresh snapshot.

### Why not just use `read_only=True`?

A DuckDB connection opened with `read_only=True` (or `config={"access_mode": "read_only"}`) still acquires a **shared lock** at the OS level. While multiple shared locks can coexist, they block any process from acquiring an **exclusive lock** for writing. This means a notebook with a read-only connection would prevent syncs from running.

The snapshot approach avoids this entirely &mdash; the notebook operates on a separate file.

## Metabase

Metabase connects to DuckDB through a JDBC driver (MotherDuck DuckDB driver). The driver **ignores** any `read_only` configuration in the Metabase connection settings &mdash; it always attempts to acquire a write lock.

### Docker `:ro` volume mount

Dango solves this with a filesystem-level read-only mount in Docker:

```yaml
volumes:
  # :ro prevents Metabase JDBC driver from acquiring DuckDB write lock.
  # The driver ignores read_only config; filesystem-level :ro is required.
  - ./data:/data:ro
```

The `:ro` flag makes the entire `/data` directory read-only inside the Metabase container. The driver physically cannot create lock files or write to the database, so it falls back to read-only access. Meanwhile, the host system (where syncs and dbt run) retains full write access.

!!! warning "Don't remove the `:ro` flag"
    Without `:ro`, Metabase will acquire a write lock on the database, blocking all syncs and transformations. This is the most common cause of "database is locked" errors in cloud deployments.

## "Database Is Locked" Error

If you see a "database is locked" error, it means another process holds an exclusive lock on `data/warehouse.duckdb`.

### Diagnosis

Check who holds the lock:

```bash
cat .dango/state/dbt.lock.json
```

This shows the PID, operation, and start time of the lock holder.

### Resolution

1. **Wait for the operation to finish.** Most syncs complete within a few minutes. The lock info shows when it started.

2. **Check for stale locks.** If the process that acquired the lock has crashed, the next lock acquisition attempt will clean it up automatically. You can trigger this by running any sync or dbt command.

3. **Manual cleanup.** If automatic detection fails (e.g., the PID was reused by another process):

    ```bash
    rm .dango/state/dbt.lock .dango/state/dbt.lock.json
    ```

    !!! danger "Only do this if you're certain no sync or dbt run is active"
        Removing the lock while an operation is in progress can lead to data corruption from concurrent writes.

4. **Check Metabase.** In cloud deployments, verify that the Docker volume mount uses `:ro`. Without it, Metabase holds a persistent write lock.

### Prevention

- Don't run `dango sync` from the CLI while a web-triggered sync is in progress
- In cloud deployments, always use the `:ro` volume mount for Metabase
- For notebooks, always use Dango's snapshot system instead of connecting directly to the warehouse

## Key Points

- DuckDB allows only **one writer** at a time &mdash; all writes are serialized through DbtLock
- The lock file at `.dango/state/dbt.lock.json` shows who holds the lock and since when
- **Stale locks** are automatically cleaned up by checking if the holder's PID is still alive
- Web UI syncs **queue for up to 5 minutes**; CLI syncs fail immediately if locked
- Notebooks use **snapshot copies** to avoid interfering with writes
- Metabase uses a Docker **`:ro` volume mount** because the JDBC driver ignores `read_only` config
- `read_only=True` connections still acquire shared locks that block writers &mdash; snapshots and `:ro` mounts are the correct solutions

## Related

- [Data Layers](data-layers.md) &mdash; how data flows through raw, staging, and mart layers in DuckDB
- [Local vs Cloud](local-vs-cloud.md) &mdash; behavioral differences between deployment modes
- [DuckDB Snapshots](../notebooks/duckdb-snapshots.md) &mdash; detailed guide to notebook snapshots
- [Sync Modes](../data-sources/sync-modes.md) &mdash; incremental loading and full refresh strategies
- [Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md) &mdash; automating syncs with schedules
