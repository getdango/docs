# Notebook Templates

Pre-built notebook templates for common data exploration tasks.

---

## Overview

Dango ships with three starter templates that provide a ready-to-use structure for common notebook workflows:

| Template | Purpose | Cells | Best For |
|----------|---------|-------|----------|
| `explore` | Browse schemas, tables, and run ad-hoc queries | 4 | Getting familiar with your data |
| `quality` | Row counts, column metadata, null analysis | 4 | Data quality checks and audits |
| `blank` | Minimal DuckDB connection only | 1 | Custom analysis from scratch |

## Using Templates

Specify a template when creating a notebook:

```bash
# Data exploration (default)
dango notebook new --template explore --name my_exploration

# Data quality checks
dango notebook new --template quality --name quality_check

# Blank canvas
dango notebook new --template blank --name custom_analysis
```

If you omit `--template`, the `explore` template is used by default. See [Getting Started](getting-started.md) for a full walkthrough of creating and opening notebooks.

## Explore Template

The explore template sets up a connection to your warehouse and lists all available tables, with a cell for ad-hoc SQL queries.

**Cells:**

| Cell | Purpose |
|------|---------|
| `guidance` | Markdown introduction with tips |
| `setup` | DuckDB connection (read-only) |
| `list_tables` | Lists all user-created tables across schemas |
| `sample_query` | Editable SQL query cell |

**Full code:**

```python
import marimo

app = marimo.App()


@app.cell
def guidance():
    """Introductory guidance for the explore notebook."""
    import marimo as mo

    return (
        mo.md(
            """
# Data Exploration

This notebook is connected to your DuckDB warehouse in **read-only** mode.
Each cell's output appears below it — edit the SQL in `sample_query` to explore
your data.

**Tip:** Use `mo.ui.table(df)` for interactive, sortable tables.
"""
        ),
    )


@app.cell
def setup():
    """Connect to the local DuckDB warehouse in read-only mode."""
    import os

    import duckdb

    db_path = os.environ.get("DANGO_NOTEBOOK_DB_PATH", "data/warehouse.duckdb")
    conn = duckdb.connect(db_path, config={"access_mode": "read_only"})
    return (conn,)


@app.cell
def list_tables(conn):
    """List all user-created tables across schemas."""
    tables = conn.sql(
        "SELECT table_schema, table_name "
        "FROM information_schema.tables "
        "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
        "ORDER BY table_schema, table_name"
    )
    return (tables,)


@app.cell
def sample_query(conn):
    """Run an ad-hoc query — edit the SQL below to explore your data."""
    # Edit the query below to explore your data
    result = conn.sql("SELECT 1 AS hello")
    return (result,)
```

## Quality Template

The quality template provides row counts across all tables and a column metadata cell for inspecting specific tables.

**Cells:**

| Cell | Purpose |
|------|---------|
| `guidance` | Markdown introduction with tips |
| `setup` | DuckDB connection (read-only) |
| `row_counts` | Computes row counts for every table in the warehouse |
| `null_analysis` | Column metadata for a target table (edit the WHERE clause) |

**Full code:**

```python
import marimo

app = marimo.App()


@app.cell
def guidance():
    """Introductory guidance for the quality notebook."""
    import marimo as mo

    return (
        mo.md(
            """
# Data Quality

This notebook shows **row counts** and **column metadata** for tables in your
DuckDB warehouse (read-only). Each cell's output appears below it — edit the
WHERE clause in `null_analysis` to inspect a specific table.

**Tip:** Use `mo.ui.table(df)` for interactive, sortable tables.
"""
        ),
    )


@app.cell
def setup():
    """Connect to the local DuckDB warehouse in read-only mode."""
    import os

    import duckdb

    db_path = os.environ.get("DANGO_NOTEBOOK_DB_PATH", "data/warehouse.duckdb")
    conn = duckdb.connect(db_path, config={"access_mode": "read_only"})
    return (conn,)


@app.cell
def row_counts(conn):
    """Compute row counts for every table in the warehouse."""
    tables = conn.execute(
        "SELECT table_schema, table_name "
        "FROM information_schema.tables "
        "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
        "ORDER BY table_schema, table_name"
    ).fetchall()
    counts = []
    for schema, table in tables:
        n = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
        counts.append({"schema": schema, "table": table, "row_count": n})
    return (counts,)


@app.cell
def null_analysis(conn):
    """Show column metadata for a target table — edit the WHERE clause."""
    # Replace with your target table
    result = conn.sql(
        "SELECT column_name, data_type "
        "FROM information_schema.columns "
        "WHERE table_schema = 'raw' "
        "ORDER BY ordinal_position "
        "LIMIT 20"
    )
    return (result,)
```

## Blank Template

The blank template provides only a DuckDB connection cell — a clean starting point for custom analysis.

**Cell:**

| Cell | Purpose |
|------|---------|
| `setup` | DuckDB connection (read-only) |

**Full code:**

```python
import marimo

app = marimo.App()


@app.cell
def setup():
    """Connect to the local DuckDB warehouse in read-only mode."""
    import os

    import duckdb

    db_path = os.environ.get("DANGO_NOTEBOOK_DB_PATH", "data/warehouse.duckdb")
    conn = duckdb.connect(db_path, config={"access_mode": "read_only"})
    return (conn,)
```

## DuckDB Connection Pattern

All templates share the same connection pattern in their `setup` cell:

```python
import os
import duckdb

db_path = os.environ.get("DANGO_NOTEBOOK_DB_PATH", "data/warehouse.duckdb")
conn = duckdb.connect(db_path, config={"access_mode": "read_only"})
```

**How it works:**

- `DANGO_NOTEBOOK_DB_PATH` — set automatically by Dango when starting Marimo, pointing to the [DuckDB snapshot](duckdb-snapshots.md) in `.dango/snapshots/`
- If the environment variable is not set (e.g., running the notebook manually), it falls back to `data/warehouse.duckdb`
- `config={"access_mode": "read_only"}` — defense-in-depth; prevents accidental writes even though the snapshot is already a copy

!!! warning
    Do not change the access mode to `read_write`. Notebooks should never write to the warehouse directly — all data loading goes through `dango sync` and dbt transforms.

For more on why snapshots are used instead of connecting directly to the warehouse, see [DuckDB Snapshots](duckdb-snapshots.md).

## Creating Custom Templates

Notebook files are standard Marimo Python scripts stored in the `notebooks/` directory. To create a reusable starting point:

1. Create a notebook: `dango notebook new --template blank --name my_template`
2. Open and customize it: `dango notebook open my_template`
3. Copy the file to use as a base for future notebooks

The key requirement is the `setup` cell with the DuckDB connection pattern shown above.
