# File Locking

How notebook file locking prevents conflicts in multi-user environments.

---

## Overview

When multiple users have access to the same Dango project, two people could try to edit the same notebook at the same time. Dango prevents this with **file-level locks** — time-limited, heartbeat-refreshed locks that ensure only one user edits a notebook at a time.

Locks are:

- **Automatic** — acquired when you open a notebook, released when you close it
- **Time-limited** — expire after 15 minutes without a heartbeat
- **Per-notebook** — each notebook has its own independent lock

## How Locking Works

1. **User opens a notebook** — Dango acquires a lock in the `notebook_locks` database table
2. **Lock is granted** — the lock expires in 15 minutes unless refreshed
3. **Heartbeat runs** — a background thread (CLI) or API call (Web UI) refreshes the lock every 60 seconds
4. **Each heartbeat** resets the expiry to 15 minutes from now
5. **User closes the notebook** — Dango releases the lock immediately
6. **If the user disappears** (crash, network loss) — the lock expires after the last heartbeat + 15 minutes

## Heartbeat Mechanism

| Parameter | Value |
|-----------|-------|
| Lock duration | 15 minutes |
| Heartbeat interval | 60 seconds |
| Stale lock timeout | 900 seconds (15 minutes since last heartbeat) |

=== "CLI"

    When you run `dango notebook open`, a background thread sends heartbeats every 60 seconds:

    ```
    ✓ Marimo started (PID 12345)

      Open in browser: http://localhost:7805/?file=my_analysis.py

    Press Ctrl+C to release lock and exit.
    ```

    The heartbeat thread runs until you press Ctrl+C or the process is killed.

=== "Web UI"

    The browser sends heartbeat requests to `POST /api/notebooks/{name}/heartbeat` every 60 seconds while the notebook is open. If the browser tab is closed, heartbeats stop and the lock expires.

## Stale Lock Recovery

Stale locks are cleaned up automatically. Every lock operation (acquire, release, refresh) first deletes any locks whose `expires_at` timestamp has passed. Additionally, locks whose last heartbeat exceeds 900 seconds (15 minutes) are proactively expired.

This means:

- If a CLI session crashes, the lock expires within 15 minutes
- If a browser tab is closed without releasing, the lock expires within 15 minutes
- No manual intervention is needed in most cases

## Locked Notebook Behavior

When you try to open a notebook that's locked by another user:

=== "CLI"

    ```
    Error: Notebook 'my_analysis' is locked by admin@example.com.
    ```

    You'll need to wait for the lock to be released or ask the lock holder to release it.

=== "Web UI"

    The notebook shows a lock icon with the lock holder's name and expiry time. You have two options:

    - **Wait** — the lock will expire if the holder is inactive
    - **Make a Copy** — creates a copy of the notebook (e.g., `my_analysis_copy_20260515_143022.py`) that you can edit independently

## Force Unlock

Users with the `notebooks.manage` permission can force-release a lock regardless of who holds it.

=== "Web UI"

    Click the lock icon on a locked notebook, then click **Force Unlock**. The lock holder receives a WebSocket notification that their lock was revoked.

=== "API"

    ```bash
    curl -X DELETE http://localhost:8800/api/notebooks/my_analysis/lock
    ```

!!! warning
    Force-unlocking a notebook while someone is actively editing it can cause them to lose unsaved work. Marimo auto-saves frequently, but any in-progress cell edits may be lost.

## Permissions

Notebook operations require specific permissions:

| Permission | Actions | Default Roles |
|------------|---------|---------------|
| `notebooks.view` | List notebooks, view metadata | All roles |
| `notebooks.execute` | Create, open, edit, delete (own), lock/unlock | Editor, Admin |
| `notebooks.manage` | Force unlock, delete others' notebooks | Admin |

See [Permissions Reference](../reference/permissions.md) for the full permissions list.

## Idle Auto-Shutdown

When no notebooks have active locks for a sustained period, the Marimo server shuts down automatically to free resources.

=== "Local"

    | Parameter | Value |
    |-----------|-------|
    | Idle timeout | **2 hours** |
    | Warning | 5 minutes before shutdown (via WebSocket) |
    | Check interval | Every 5 minutes |

=== "Cloud"

    | Parameter | Value |
    |-----------|-------|
    | Idle timeout | **1 hour** |
    | Warning | 5 minutes before shutdown (via WebSocket) |
    | Check interval | Every 5 minutes |

The idle checker monitors the `notebook_locks` table. As long as any non-expired lock exists, the idle timer resets. Once all locks are released (or expired), the countdown begins.

When the idle timer fires:

1. A WebSocket warning is broadcast 5 minutes before shutdown
2. After the timeout, all remaining locks are released
3. The Marimo server process is stopped
4. The PID file (`.dango/marimo.pid`) is cleaned up

The next `dango notebook open` (or web UI Open) automatically restarts Marimo with a fresh snapshot.

## Lock Storage

Locks are stored in the `notebook_locks` table in `.dango/dango.db` (SQLite):

| Column | Type | Description |
|--------|------|-------------|
| `notebook_id` | TEXT (PK) | Notebook name (filename stem) |
| `locked_by` | TEXT | Username or email of the lock holder |
| `locked_at` | DATETIME | When the lock was first acquired |
| `expires_at` | DATETIME | When the lock expires (refreshed by heartbeat) |
| `last_heartbeat_at` | DATETIME | Timestamp of the most recent heartbeat |

## Troubleshooting

### Lock appears stuck

If a lock persists longer than expected:

1. **Wait 15 minutes** — the lock will expire automatically if heartbeats have stopped
2. **Force unlock** (admin) — use the Web UI or API to force-release the lock
3. **Check for stale processes** — if the CLI session that acquired the lock is still running but hung, kill the process and the lock will expire

### "Lock not held by you" error

```
Lock not held by you or has expired.
```

This means:

- Your lock expired while you were editing (no heartbeat for 15+ minutes)
- Another user force-released your lock

Re-open the notebook to acquire a fresh lock. Any unsaved edits in your browser may still be intact — Marimo auto-saves to the `.py` file.

### Idle shutdown warning

```
Notebook server will shut down in 5 minutes due to inactivity.
```

This WebSocket notification appears when no notebooks have been actively locked for most of the idle timeout period. To prevent shutdown, open a notebook (which acquires a lock and resets the idle timer).
