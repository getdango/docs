# Notebooks

Interactive data exploration with Marimo notebooks and DuckDB.

---

## Overview

Dashboards show you what's happening — notebooks let you ask *why*. Dango integrates [Marimo](https://marimo.io), a reactive Python notebook, with your DuckDB warehouse so you can run ad-hoc queries, build visualizations, and investigate data issues without leaving the platform.

Key features:

- **Reactive Python notebooks** — Marimo cells re-execute automatically when dependencies change
- **DuckDB snapshots** — notebooks query a read-only copy of your warehouse, so syncs and transforms are never blocked (see [DuckDB core concepts](../core-concepts/duckdb.md))
- **File locking** — time-limited locks with heartbeat prevent conflicts when multiple users edit notebooks
- **Starter templates** — pre-built notebooks for data exploration and quality checks

## How It Works

When you open a notebook, Dango performs these steps automatically:

1. **Lock** — acquires a file-level lock so no one else can edit the same notebook
2. **Snapshot** — copies `data/warehouse.duckdb` to `.dango/snapshots/` (if Marimo isn't already running)
3. **Start** — launches the Marimo server (headless, on port 7805)
4. **Connect** — opens the notebook in your browser, connected to the read-only snapshot
5. **Release** — when you're done (Ctrl+C or release via web UI), the lock is released

## Quick Start

```bash
# Create a notebook from the explore template
dango notebook new --template explore --name my_analysis

# Open it in Marimo
dango notebook open my_analysis

# Press Ctrl+C to release the lock and exit
```

## Key Concepts

| Concept | Description | Learn More |
|---------|-------------|------------|
| **Templates** | Pre-built notebooks for exploration, quality checks, or a blank canvas | [Templates](templates.md) |
| **DuckDB Snapshots** | Read-only database copies that isolate notebooks from write operations | [DuckDB Snapshots](duckdb-snapshots.md) |
| **File Locking** | Time-limited locks with heartbeat to prevent editing conflicts | [File Locking](file-locking.md) |
| **Idle Shutdown** | Automatic server shutdown after inactivity (2h local, 1h cloud) | [File Locking](file-locking.md#idle-auto-shutdown) |

## CLI vs Web UI

=== "CLI"

    ```bash
    # List notebooks
    dango notebook

    # Create a notebook
    dango notebook new --template explore --name my_analysis

    # Open a notebook (locks, snapshots, starts Marimo)
    dango notebook open my_analysis
    ```

=== "Web UI"

    Navigate to **Notebooks** in the sidebar. From there you can:

    - View all notebooks with lock status
    - Create a new notebook from a template
    - Click **Open** to acquire a lock and launch Marimo
    - Release locks or make copies of locked notebooks

    See [Web UI — Notebooks](../web-ui/notebooks.md) for details.

## Next Steps

<div class="grid cards" markdown>

-   :material-play-circle:{ .lg .middle } **Getting Started**

    ---

    Step-by-step guide to creating, opening, and querying your first notebook.

    [:octicons-arrow-right-24: Getting Started](getting-started.md)

-   :material-file-document-multiple:{ .lg .middle } **Templates**

    ---

    Pre-built notebooks for data exploration, quality checks, and custom analysis.

    [:octicons-arrow-right-24: Templates](templates.md)

-   :material-database-sync:{ .lg .middle } **DuckDB Snapshots**

    ---

    How read-only snapshots keep notebooks isolated from write operations.

    [:octicons-arrow-right-24: DuckDB Snapshots](duckdb-snapshots.md)

-   :material-lock:{ .lg .middle } **File Locking**

    ---

    Heartbeat-based locks, idle shutdown, and multi-user conflict prevention.

    [:octicons-arrow-right-24: File Locking](file-locking.md)

</div>
