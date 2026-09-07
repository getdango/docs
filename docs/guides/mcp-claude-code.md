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

`dango mcp setup` must be run from inside your Dango project (it needs to know which project to
point your LLM client at). It configures each detected client differently, because each one has a
genuinely different config model — not one design applied three times:

### Claude Code

```bash
dango mcp setup
```

Runs `claude mcp add --scope local`, Claude Code's own install command, instead of writing a config
file directly. **Local scope** is private to you and keyed by this project's absolute path — it
lives in `~/.claude.json`, not `~/.claude/settings.json`, and never touches any other Dango project
on your machine. This requires the `claude` CLI to be on your `PATH` (a separate thing from the
Claude Code app itself — if setup reports it can't find `claude`, make sure it's on your `PATH` and
re-run `dango mcp setup`).

To verify or remove the connection yourself:

```bash
claude mcp get dango       # shows scope, command, and connection status
claude mcp remove dango --scope local
```

### Cursor

`dango mcp setup` writes a project-scoped `.cursor/mcp.json` in your project root. Unlike Claude
Code, Cursor has no private per-project scope and no native CLI install command — its project
config is designed to be **committed to git and shared with your team**. To keep that safe, the
entry uses a bare `dango` command (resolved via each teammate's own `PATH` once they activate their
own venv, not an absolute path baked in for one machine) and Cursor's `${workspaceFolder}`
substitution for the project root:

```json
{
  "mcpServers": {
    "dango": {
      "command": "dango",
      "args": ["mcp", "run"],
      "env": { "DANGO_PROJECT_ROOT": "${workspaceFolder}" }
    }
  }
}
```

Commit this file if you want the whole team connected. `dango mcp setup` will warn you (without
blocking) if your git working tree is dirty or you're on `main`/`master` when it writes this file,
the same way `dango source add` and `dango model add` do.

### Windsurf

Windsurf has no project-scoped MCP config at all — this is a hard limitation of Windsurf itself, not
something Dango can work around. `dango mcp setup` writes the global
`~/.codeium/windsurf/mcp_config.json`, with your current project's path injected as
`DANGO_PROJECT_ROOT` so at least that one project is unambiguous:

> **Windsurf can only be connected to one Dango project at a time.** Running `dango mcp setup` again
> from a different project overwrites this configuration. If you work across multiple Dango
> projects, prefer Claude Code or Cursor.

### Verify

```bash
dango mcp status
```

Reports which supported clients were detected and whether each one is actually configured **for
the project you're running the command from** — Claude Code via `claude mcp get dango`, Cursor by
reading the project's own `.cursor/mcp.json`, Windsurf by reading its global config file:

```
✓ Claude Code: dango MCP configured (local scope)
✓ Cursor: dango MCP configured
```

### Remove

```bash
dango mcp remove
```

Reverses whatever `dango mcp setup` configured for this project — `claude mcp remove dango --scope
local` for Claude Code, and deleting the `dango` key from Cursor's and Windsurf's config files.

### Manual configuration

If your client isn't auto-detected, or you'd rather configure it by hand: Claude Code accepts the
same `claude mcp add` command shown above; Cursor and Windsurf both read the `{"mcpServers": {...}}`
JSON shape shown above from `.cursor/mcp.json` (project) or `~/.codeium/windsurf/mcp_config.json`
(global) respectively. Whichever client you're configuring, set `DANGO_PROJECT_ROOT` to your
project's absolute path in the entry's `env` — `dango mcp run` prefers it over guessing from the
current directory, which matters because MCP clients spawn the server once per session and keep it
running for the whole session, so the directory the server happened to start in can drift from the
project you actually meant.

### Version safety

The server checks its own version against the version recorded when the project was created (`dango
init`), once at startup, and prints a warning to its logs (not to you directly — MCP server output
isn't shown in the chat) if they differ. This catches the case where a stale or mismatched `dango`
binary ends up pointed at a newer or older project than it was built for — re-run `dango mcp setup`
from the project's own environment if you see stale results and suspect this.

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
- **`run_transform`** acquires the same `DbtLock` `dango run` (CLI) uses before calling dbt, mirroring
  the CLI command exactly. If the lock is already held by another sync or dbt run, the tool returns
  a clean `{"status": "failed", "error": ...}` rather than corrupting the warehouse or raising a raw
  exception — see the [dbt Workflows](../workflows/dbt-workflows.md) page for more on the
  `DbtLock` model.
- **`run_doctor`** calls the identical credential-health function `dango doctor` uses.
- **`add_source`** only writes the `sources.yml` entry. It does not create credentials — for
  OAuth sources you still need to run `dango oauth <source_type>` yourself, and for API-key sources
  you still need to add the key to `.dlt/secrets.toml`. An agent cannot get your data flowing
  end-to-end without you completing that step.
- **`create_model`** writes a `.sql` file and updates `schema.yml`; it does not run anything. You
  (or the agent, via `run_transform`) still have to build the model before it materializes.
- **`add_source`**, **`create_model`**, and **`add_schedule`** check your project's git state before
  returning. If your project is a git repo and you're on `main`/`master`, or the working tree has
  uncommitted changes, the tool's response includes a `git_warning` key (a list of warning strings)
  alongside the normal result — for example, on `main` with a clean tree you'd see something like
  `"On branch 'main' — this change will be written directly to that branch. Consider creating a
  feature branch first."` This is advisory only: the tool still writes the file and reports success,
  it just gives the agent (and you) a heads-up so an LLM-driven session doesn't silently commit
  mutations straight to your default branch. Non-git projects and clean feature branches get no
  `git_warning` key at all.

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
