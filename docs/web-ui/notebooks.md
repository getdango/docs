# Notebooks Page

Create, open, and manage Marimo notebooks from the web interface.

---

## Overview

The Notebooks page (`/notebooks`) lets you create and manage [Marimo](https://marimo.io/) notebooks for data exploration and quality analysis. Notebooks open directly in the browser with a read-only snapshot of your DuckDB warehouse, so notebook queries never block data syncs.

Navigate to **Notebooks** in the top navigation bar.

!!! info "Editor role required"
    Creating, opening, and managing notebooks requires the **editor** or **admin** role. Viewers can see the notebooks list but cannot interact with them.

## Notebooks Table

The table shows all notebooks in your project:

| Column | Description |
|--------|-------------|
| **Name** | Notebook name. A yellow "missing file" badge appears if the `.py` file has been deleted from disk. |
| **Author** | Email of the user who created the notebook, or "—" if unknown. |
| **Last Modified** | Relative time since the file was last changed (e.g., "2h ago"). |
| **Lock Status** | Current editing state (see [Lock Indicators](#lock-indicators) below). |
| **Actions** | Context-dependent buttons (see [Actions](#actions) below). |

### Lock Indicators

Notebooks use file locking to prevent conflicting edits:

| Status | Badge Color | Meaning |
|--------|-------------|---------|
| **Available** | Green | No one is editing — you can open it. |
| **Editing (Xh ago)** | Blue | You are currently editing this notebook. |
| **Locked by user@example.com** | Orange | Another user is editing. You can copy the notebook or wait. |

### Actions

The available actions depend on the notebook's lock state and your role:

| Lock State | Available Actions |
|------------|-------------------|
| **Not locked** | Open, Delete |
| **Locked by you** | Release Lock, Delete |
| **Locked by another user** | Copy, Force Unlock (admin only), Delete |

## Creating a Notebook

1. Click the **New Notebook** button (top-right).
2. Choose a template from the dropdown:
    - **Blank** — empty notebook
    - **Data Exploration** — pre-configured with DuckDB connection and sample queries
    - **Data Quality** — template for data quality checks and profiling
3. Enter a name in the modal (letters, numbers, and underscores only).
4. Click **Create**.

The notebook appears in the table and is ready to open.

## Opening a Notebook

1. Click **Open** on an available (unlocked) notebook.
2. Dango acquires a lock, creates a DuckDB snapshot, and starts the Marimo server.
3. Marimo opens in a new browser tab.

While editing, a heartbeat signal is sent every 60 seconds to keep the lock active. Locks expire 15 minutes after the last heartbeat, so if you close the tab without releasing the lock, it becomes available to other users within 15 minutes.

!!! tip "DuckDB snapshot"
    Notebooks work against a read-only snapshot of your warehouse, not the live database. This means your notebook queries never block syncs or dbt runs. The snapshot is created when you open the notebook.

## Lock Management

### Releasing Your Lock

When you're done editing, click **Release Lock** in the notebooks table. This frees the notebook for other users.

### Force Unlock (Admin)

If a user's session crashes and their lock persists, an admin can click **Force Unlock** to release it. The locked-out user receives a notification:

> Your lock on "notebook_name" has been revoked by an administrator.

This notification appears as a yellow banner on their Notebooks page.

## Copying a Notebook

If a notebook is locked by another user, click **Copy** to create a duplicate with a new name. This lets you work on your own version without waiting for the lock to be released.

## Deleting a Notebook

1. Click **Delete** on the notebook row.
2. Confirm in the modal: "Are you sure you want to delete notebook_name? This cannot be undone."
3. Click **Delete** to confirm.

Non-admin users can only delete notebooks they created. Locked notebooks cannot be deleted until the lock is released.

??? info "How it works"
    - **List notebooks:** `GET /api/notebooks` returns all notebooks with lock state, author, and file existence status.
    - **Create:** `POST /api/notebooks` with `{name, template}`. Name must match `[a-zA-Z0-9_]+`.
    - **Open (acquire lock):** `POST /api/notebooks/{name}/lock` acquires the lock, creates a DuckDB snapshot, and starts Marimo. Returns a `marimo_url` to open in a new tab.
    - **Heartbeat:** `POST /api/notebooks/{name}/heartbeat` every 60 seconds to keep the lock alive.
    - **Release lock:** `POST /api/notebooks/{name}/release` releases your own lock.
    - **Force unlock:** `DELETE /api/notebooks/{name}/lock` (admin only) releases another user's lock and sends a WebSocket `notebook_lock_revoked` event.
    - **Copy:** `POST /api/notebooks/{name}/copy` creates a duplicate file.
    - **Delete:** `DELETE /api/notebooks/{name}` removes the notebook file and metadata.

## Troubleshooting

**"Notebook is locked by..." but the user isn't editing**
:   The user's browser may have closed without releasing the lock. Ask an admin to click **Force Unlock**, or wait for the heartbeat to expire (the lock releases automatically when heartbeats stop).

**Notebook opens but Marimo shows a blank page**
:   The Marimo server may not have started yet. Wait a few seconds and refresh the Marimo tab. On cloud deployments, Marimo is proxied through the Dango web server — check that the server is running.

**"Notebook file not found" error**
:   The notebook's `.py` file was deleted from disk but the metadata still exists. The table shows a yellow "missing file" badge. Create a new notebook with the same name to replace it.

## Related Pages

- [Dashboard Page](dashboard.md) — platform overview and service status
- [Catalog Page](catalog.md) — browse tables and columns for query reference
- [Sources Page](sources.md) — check source sync status and data availability
