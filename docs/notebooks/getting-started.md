# Getting Started with Notebooks

Create and open your first Marimo notebook connected to your warehouse.

---

## Prerequisites

Before using notebooks, make sure you have:

- An initialized Dango project (`dango init`)
- At least one data source synced (`dango sync <source>`) so the warehouse has data to query
- Marimo is bundled with Dango — no separate install needed

## Step 1: Create a Notebook

=== "CLI"

    ```bash
    dango notebook new --template explore --name my_analysis
    ```

    Output:

    ```
    ✓ Created notebook my_analysis from 'explore' template
      notebooks/my_analysis.py
    ```

    Available templates:

    | Template | Description |
    |----------|-------------|
    | `explore` | Lists schemas and tables with a sample query cell (default) |
    | `quality` | Row counts, column metadata, and null analysis |
    | `blank` | Minimal setup — just a DuckDB connection cell |

    See [Templates](templates.md) for full details and code.

=== "Web UI"

    1. Navigate to **Notebooks** in the sidebar
    2. Click **New Notebook**
    3. Enter a name and select a template
    4. Click **Create**

## Step 2: Open a Notebook

=== "CLI"

    ```bash
    dango notebook open my_analysis
    ```

    Output:

    ```
    ✓ Created DuckDB snapshot at warehouse_cli_20260515_143022.duckdb
    Starting Marimo server...
    ✓ Marimo started (PID 12345)

      Open in browser: http://localhost:7805/?file=my_analysis.py

    Press Ctrl+C to release lock and exit.
    ```

=== "Web UI"

    1. Navigate to **Notebooks** in the sidebar
    2. Click **Open** next to the notebook name
    3. Marimo opens in a new tab (or embedded in the Dango UI on cloud deployments)

Behind the scenes, `dango notebook open` performs four steps:

1. **Acquires a file lock** — prevents other users from editing the same notebook
2. **Creates a DuckDB snapshot** — copies `data/warehouse.duckdb` to `.dango/snapshots/` for read-only access
3. **Starts the Marimo server** — runs on port 7805 (if not already running)
4. **Opens your browser** — navigates to the notebook URL

## Step 3: Query Your Data

Every template includes a setup cell that connects to your DuckDB warehouse in read-only mode. You can query your data using several patterns:

### Direct SQL Display

```python
# Returns a Marimo-rendered table
result = conn.sql("SELECT * FROM raw.customers LIMIT 10")
```

### SQL to DataFrame

```python
# Convert to a pandas DataFrame
df = conn.sql("SELECT customer_id, email FROM raw.customers").fetchdf()
```

### SQL to Python Lists

```python
# Get raw rows as a list of tuples
rows = conn.sql("SELECT COUNT(*) FROM raw.orders").fetchall()
```

!!! tip
    Use `mo.ui.table(df)` for interactive, sortable tables in Marimo. This is built into Marimo's UI toolkit.

## Step 4: Save and Exit

=== "CLI"

    Press **Ctrl+C** in the terminal where `dango notebook open` is running. This releases the lock and exits.

    ```
    ✓ Lock released.
    ```

    Marimo auto-saves your notebook — your edits are written to the `.py` file as you work.

=== "Web UI"

    Click **Release Lock** in the Notebooks page. The lock is released and the notebook is available for others to edit.

If you forget to release the lock, it expires automatically after 15 minutes without a heartbeat refresh. See [File Locking](file-locking.md) for details.

## Recommended Packages

These packages work well inside Marimo notebooks for data analysis:

| Package | Use Case | Example |
|---------|----------|---------|
| `pandas` | DataFrames, groupby, pivot tables | `df = conn.sql("...").fetchdf()` |
| `polars` | Fast DataFrames (alternative to pandas) | `df = conn.sql("...").pl()` |
| `matplotlib` | Static charts and plots | `plt.bar(df["name"], df["count"])` |
| `seaborn` | Statistical visualizations | `sns.heatmap(df.corr())` |

!!! note
    Install additional packages into your project's virtual environment (`pip install pandas matplotlib`) before using them in notebooks.

## Listing Notebooks

```bash
dango notebook
```

Output:

```
         Notebooks
┌──────────────┬────────┬─────────┬──────────────────┐
│ Name         │ Author │ Size    │ Last Modified    │
├──────────────┼────────┼─────────┼──────────────────┤
│ my_analysis  │ cli    │ 1.2 KB  │ 2026-05-15 14:30 │
│ data_quality │ admin  │ 1.8 KB  │ 2026-05-14 09:15 │
└──────────────┴────────┴─────────┴──────────────────┘
```

## Troubleshooting

### Notebook is locked

```
Error: Notebook 'my_analysis' is locked by admin@example.com.
```

Another user is editing this notebook. Wait for them to finish, or ask an admin to force-release the lock. You can also make a copy:

- **Web UI:** Click **Make a Copy** to create an editable copy
- **CLI:** Create a new notebook and copy the content manually

See [File Locking — Locked Notebook Behavior](file-locking.md#locked-notebook-behavior) for details.

### Warehouse not found

```
Error: Warehouse database not found at data/warehouse.duckdb. Run a sync first to create it.
```

You need to sync at least one data source before opening a notebook:

```bash
dango sync <source_name>
```

### Marimo already running

```
RuntimeError: Marimo is already running (PID 12345).
Stop it with 'dango stop'
```

The Marimo server is already running from another session. Either:

- Open your notebook in the existing server: `http://localhost:7805/?file=my_analysis.py`
- Stop Marimo and restart: `dango stop` then `dango notebook open my_analysis`

### Data seems stale

The DuckDB snapshot is created when Marimo starts. If you've synced new data since then, the notebook still shows the old data. To refresh:

1. Release your lock (Ctrl+C or via Web UI)
2. Re-open the notebook — a new snapshot is created if Marimo restarts

See [DuckDB Snapshots](duckdb-snapshots.md) for more on snapshot lifecycle.

## Related

- [Templates](templates.md) — built-in notebook templates for common analyses
- [DuckDB Snapshots](duckdb-snapshots.md) — how notebooks access your data safely
- [File Locking](file-locking.md) — understanding lock isolation
