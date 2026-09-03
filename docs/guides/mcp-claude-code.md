# Use Dango with Claude Code

Connect Claude Code (or any MCP-compatible coding agent — Cursor, Windsurf) directly to your Dango
project. Once connected, your agent can list your data sources, inspect table schemas and dbt
lineage, run read-only SQL, and — with your permission — trigger syncs, run dbt, and scaffold new
models, all without you copy-pasting context back and forth.

---

## Overview

Dango ships an MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server: `dango mcp
run`. You don't run this command yourself — your LLM client spawns it automatically once it's
configured. It talks to your client over stdio (standard input/output on the local machine), not
over the network.

The server exposes 15 tools:

- **8 read tools** — list sources, inspect schemas, browse the catalog, trace lineage, read model
  SQL, run read-only queries, check sync history
- **7 mutation tools** — trigger syncs and dbt runs, create sources/models/schedules

---

## Setup

### Automatic

```bash
dango mcp setup
```

This detects which supported LLM clients are installed on your machine (by checking whether their
config directory exists) and writes a `dango` entry into each one's MCP config file:

| Client | Config file |
|--------|-------------|
| Claude Code | `~/.claude/settings.json` |
| Cursor | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |

The write is atomic (temp file + rename) and preserves the file's existing contents and
permissions — it merges a `dango` key into `mcpServers` rather than overwriting the whole file, so
your other client settings are untouched.

Restart your LLM client afterward to pick up the new server.

### Verify

```bash
dango mcp status
```

Reports which supported clients were detected and whether each one's config file actually has the
`dango` entry, e.g.:

```
✓ Claude Code: dango MCP configured
✓ Cursor: dango MCP configured
```

### Manual configuration

If your client isn't auto-detected yet, or you'd rather edit the config yourself, add this to the
client's MCP config file under `mcpServers`:

```json
{
  "mcpServers": {
    "dango": {
      "command": "/path/to/your/project/venv/bin/dango",
      "args": ["mcp", "run"]
    }
  }
}
```

`command` should point at the `dango` executable inside the same virtualenv you installed Dango
into (`dango mcp setup` resolves this automatically from `sys.executable`; falls back to the bare
`dango` command, relying on `PATH`, if it can't find a venv-local binary). MCP clients run one
server process per project — if you work across multiple Dango projects, `dango mcp run` picks up
whichever project you're in the same way any other `dango` command does (it walks up from the
current directory to find `project.yml`).

---

## Available tools

### Read tools

| Tool | Purpose |
|------|---------|
| `list_sources()` | List all configured data sources with their sync status and row counts. |
| `get_table_schema(table_name, schema=None)` | Get the schema (columns, types) for a table in the warehouse. |
| `get_catalog(source_filter=None)` | Get the data catalog: all tables grouped by schema with row counts. |
| `get_lineage(model_name=None)` | Get dbt lineage from the manifest — source → staging → intermediate → mart flow. |
| `list_models()` | List all dbt models with their layer, schema, and file path. |
| `get_model_sql(model_name)` | Get the SQL source for a dbt model. |
| `query(sql, row_limit=500)` | Run a read-only SQL query against the DuckDB warehouse. Single `SELECT` (or `WITH ... SELECT`) only. |
| `get_sync_history(source_name=None, limit=10)` | Get recent sync history for a source, or the most recent entries across all sources. |

### Mutation tools

| Tool | Purpose |
|------|---------|
| `run_sync(source_name, full_refresh=False)` | Sync a data source. Respects the existing lock and queue semantics. |
| `run_transform(select=None, full_refresh=False)` | Run dbt transformations. Equivalent to `dango run`. |
| `run_doctor()` | Check credential health for all configured sources. Equivalent to `dango doctor`. |
| `add_source(source_type, source_name, description="")` | Add a new data source to `sources.yml`. |
| `list_source_types()` | List all available source types in the Dango registry. |
| `create_model(model_name, layer, upstream_refs, description="")` | Create a new dbt model with correct structure and naming conventions. |
| `add_schedule(schedule_name, cron, sources, timezone="UTC", skip_dbt=False)` | Add a new sync schedule. |

---

## Worked examples

The tool calls and results below are real output from actually running these tools against a
scratch test project (one CSV source, `orders_csv`, synced once) — not hand-written illustrations.

### "What tables do I have?"

The agent starts broad with `list_sources()`, then drills into the catalog:

```
> list_sources()
[
  {
    "name": "orders_csv",
    "type": "csv",
    "enabled": true,
    "last_sync": "2026-09-03T08:45:58.971287+00:00",
    "rows": 4,
    "status": "synced"
  }
]

> get_catalog()
{
  "tables_by_schema": {
    "main": ["_dango_file_metadata"],
    "raw_orders_csv": ["orders_csv"],
    "staging": ["stg_orders_csv__orders_csv"]
  },
  "total": 3
}

> get_table_schema("stg_orders_csv__orders_csv")
{
  "table_name": "stg_orders_csv__orders_csv",
  "schema": "staging",
  "columns": [
    {"name": "order_id", "type": "BIGINT"},
    {"name": "customer_id", "type": "BIGINT"},
    {"name": "amount", "type": "DOUBLE"},
    {"name": "order_date", "type": "DATE"}
  ]
}
```

From here the agent has enough to answer in plain English, or to follow up with `query()` for
actual numbers.

### "Build me a marts model for order revenue"

The agent traces lineage before writing anything, so the model refs the right upstream table:

```
> get_lineage()
{
  "model_count": 1,
  "source_count": 1,
  "models": [
    {"name": "stg_orders_csv__orders_csv", "schema": "staging", "layer": "staging"}
  ]
}

> create_model(
    model_name="fct_orders",
    layer="marts",
    upstream_refs=["stg_orders_csv__orders_csv"],
    description="Daily order metrics from orders_csv"
  )
{
  "status": "created",
  "file_path": "dbt/models/marts/fct_orders.sql",
  "sql_scaffold": "with stg_orders_csv__orders_csv as (select * from {{ ref('stg_orders_csv__orders_csv') }})\n\n-- TODO: add aggregations and business metrics here\n\nselect * from stg_orders_csv__orders_csv\n",
  "warnings": [],
  "next_steps": [
    "Edit fct_orders.sql to add your business logic",
    "Run: dango run to test"
  ]
}
```

`create_model` enforces Dango's naming convention as a feature, not an afterthought — staging
models must start with `stg_`, intermediate with `int_`, and marts with `fct_` or `dim_`. An agent
that tries to name a marts model something else gets pushed back immediately instead of writing a
model that violates the convention:

```
> create_model(model_name="orders_summary", layer="marts", upstream_refs=["stg_orders_csv__orders_csv"])
{
  "error": "Marts models must be named fct_<metric> or dim_<entity>"
}
```

It also flags a common anti-pattern — marts models referencing raw tables instead of
staging/intermediate ones — as a warning in the response rather than silently allowing it.

### "Why did last night's sync fail?"

```
> get_sync_history("orders_csv")
[
  {
    "timestamp": "2026-09-03T08:45:58.971287+00:00",
    "status": "success",
    "duration_seconds": 0.59,
    "rows_processed": 4,
    "full_refresh": true,
    "error_message": null,
    "source": "orders_csv"
  },
  {
    "timestamp": "2026-09-03T08:45:45.569894+00:00",
    "status": "failed",
    "duration_seconds": 0.03,
    "rows_processed": 0,
    "full_refresh": true,
    "error_message": "CSV config missing for source: orders_csv",
    "source": "orders_csv"
  }
]
```

The `error_message` field on the failed entry is often enough on its own — here it's a
configuration problem, not credentials. For credential-shaped failures (expired OAuth tokens,
missing API keys), the agent follows up with `run_doctor()`, which checks every configured source
and reports `ok`, `missing`, `expired`, or `expiring_soon` per source (the same statuses `dango
doctor` reports on the command line):

```
> run_doctor()
[
  {"source": "orders_csv", "type": "csv", "auth_type": "none", "status": "ok", "detail": ""}
]
```

---

## Safety

Mutation tools are not a separate, less-validated path — most of them call the exact same
functions the CLI commands use:

- **`run_sync`** calls `dango.ingestion.run_sync` — the identical function `dango sync` uses,
  including its internal `DbtLock` acquisition around both the data load and the post-sync dbt
  step. Concurrent syncs and dbt runs are serialized the same way regardless of whether they were
  triggered from the CLI or from an agent.
- **`run_doctor`** calls the identical credential-health function `dango doctor` uses.
- **`add_source`** only writes the `sources.yml` entry. It does not create credentials — for
  OAuth sources you still need to run `dango oauth <source_type>` yourself, and for API-key sources
  you still need to add the key to `.dlt/secrets.toml`. An agent cannot get your data flowing
  end-to-end without you completing that step.
- **`create_model`** writes a `.sql` file and updates `schema.yml`; it does not run anything. You
  (or the agent, via `run_transform`) still have to build the model before it materializes.

!!! warning "`run_transform` does not hold `DbtLock`"
    Unlike `dango run` (CLI) and the dbt step `run_sync` performs internally, the `run_transform`
    MCP tool calls dbt directly without acquiring Dango's `DbtLock`. Per DuckDB's single-writer
    constraint, calling it while another sync or dbt run is in progress is not protected the way
    the CLI's own `dango run` is — see the [dbt Workflows](../workflows/dbt-workflows.md) page's
    note on running `dbt` directly. Avoid asking your agent to run transforms while a sync is
    already in flight; check `list_sources()`/`get_sync_history()` first if in doubt. This is
    tracked as an open item for a future fix.

---

## Auth

The MCP server has no separate authentication layer of its own. It's a local stdio process, spawned
directly by your LLM client and communicating over stdin/stdout on your machine — there's no
network listener to authenticate against. Whatever access the OS user running your LLM client has
to your project directory (the same access you'd have running `dango` commands yourself in a
terminal) is the access the agent has. It does not use, and does not need, Dango's web-app API-key
mechanism — that mechanism authenticates HTTP requests to the Dango web server, a different surface
entirely.

---

## Next Steps

- [dlt Workflows](../workflows/dlt-workflows.md) - Source configuration and sync internals
- [dbt Workflows](../workflows/dbt-workflows.md) - Direct dbt access and the `DbtLock` model
- [Troubleshooting](../workflows/troubleshooting.md) - General troubleshooting guide
