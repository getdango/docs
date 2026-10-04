# Use Dango with Claude Code

Connect Claude Code (or any MCP-compatible coding agent — Cursor, Windsurf) directly to your Dango
project. Once connected, your agent can inspect your sources, models, catalog and lineage, run
read-only SQL, configure sources and models, run syncs and dbt, manage schedules, and read logs and
documentation, all without you copy-pasting context back and forth.

---

## Overview

Dango ships an MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server: `dango mcp
run`. You don't run this command yourself — your LLM client spawns it automatically once it's
configured. It talks to your client over stdio (standard input/output on the local machine), not
over the network.

The server exposes about 50 tools in eight groups:

- **Sources** — discover source types, create, update, enable/disable, validate and remove sources
- **Models** — create, update, validate and remove dbt models
- **Run & diagnose** — run syncs and dbt, check project and credential health, read logs and sync
  history, detect schema drift
- **Schedules** — create, change, enable/disable and remove schedules
- **Catalog & warehouse** — browse tables and lineage, run read-only SQL
- **Governance / PII** — scan for PII and manage per-column overrides
- **Docs** — read and edit model and source documentation, check coverage, regenerate dbt docs
- **Remote** — status, logs, queries, syncs and pushes for a deployed Dango server

Your client lists every tool with its full parameter schema (`tools/list`), so this page documents the
main parameters and the behaviors that matter, not every argument.

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

Tools are listed with their main parameters; defaults are shown where they matter. Every tool
returns a JSON object (or list); a failure is reported in the result, usually as an `error` key,
so the agent can read it and fix the call.

### Sources

| Tool | Purpose |
|------|---------|
| `list_sources()` | List configured sources with `type`, `enabled`, `last_sync`, `rows` and `status`. |
| `list_source_types()` | List the source types in the registry, with `auth_type`, `category` and `setup_supported`. `setup_supported: false` means the type can only be configured with the `dango source add` wizard. |
| `get_source_setup_schema(source_type)` | Describe the settings a type needs: fields, defaults and how each is handled. Agents supply only fields marked `managed_by: "agent"`; `user_secret` and `oauth` fields are handled by you. `rest_api`, `dlt_native` and types with `setup_supported: false` are CLI-only. |
| `create_source(source_type, source_name, config=None, description=None, empty_sync_policy=None, file_path=None)` | Configure a new source with validated settings. `file_path` (`local_files` only; `~` is expanded) copies a local CSV, JSON, JSONL or Parquet file into `data/uploads/<source_name>/`; leave `directory` out when you use it. The legacy `csv` type is not accepted for new sources: use `local_files`. Returns `credentials_required` and `next_steps` for anything you must supply. |
| `update_source(source_name, config=None, description=None, empty_sync_policy=None)` | Change a source's settings with the same validation. Pass only the keys to change; a key set to `None` or empty resets to its default. |
| `set_source_enabled(source_name, enabled)` | Enable or disable a source. Disabled sources are skipped by sync. |
| `remove_source(source_name, dry_run=False, force=False)` | Remove a source's `sources.yml` entry, staging files, `config.toml` section and monitors. Call with `dry_run=True` first and show the result to the user (`downstream_models`, `monitors_removed`, `files_removed`). `force=True` is required when models depend on the source. Warehouse data and `.env` are not touched. |
| `validate_source(source_name, check_connectivity=False)` | Read-only readiness check: missing settings, unset credentials and, for file sources, the number of matching files. Returns `ready` and `issues`. `check_connectivity=True` also validates OAuth tokens against the provider. |

### Models

| Tool | Purpose |
|------|---------|
| `list_models()` | List dbt models with layer, schema and file path. Like `get_model_sql` and `get_lineage`, it reads the dbt manifest, which a sync or `run_transform` produces. |
| `get_model_sql(model_name)` | Get a model's SQL source. |
| `create_model(model_name, layer, upstream_refs=None, description="", sql=None, columns=None)` | Create an `intermediate` or `marts` model with real SQL, docs and column tests. Runs `dbt parse` before and after writing and rolls back on a failure it caused. Staging models are generated by sync; use `update_model` to customize one. Omit `sql` for a scaffold built from `upstream_refs`. |
| `update_model(model_name, sql=None, description=None, columns=None)` | Update an existing model's SQL and/or `schema.yml` docs. Works on staging models too: changing a staging model's SQL marks it customized so sync stops regenerating it. A `data_tests` list you pass replaces that column's existing list. |
| `validate_model(model_name, layer, sql)` | Static checks without writing anything: refs exist, lineage, cycles, naming, name not already taken. `dbt parse` runs on `create_model` and `update_model`. |
| `remove_model(model_name, drop_table=True, dry_run=False, force=False)` | Remove a custom (`intermediate` or `marts`) model: SQL file, `schema.yml` entry, monitors and, by default, the warehouse table. Call with `dry_run=True` first; `force=True` is required when downstream models exist. Staging models cannot be removed (remove the source instead). |

### Run & diagnose

| Tool | Purpose |
|------|---------|
| `run_sync(source_name=None, full_refresh=False, since=None, until=None, backfill=None, limit=None, dry_run=False, allow_schema_changes=False, allow_empty_replace=None)` | Sync sources; equivalent to `dango sync`. Omit `source_name` to sync all enabled sources. Blocks until the sync finishes, so a long first sync can exceed your client's tool timeout (for Claude Code, `MCP_TOOL_TIMEOUT`). `full_refresh=True` drops existing data and reloads it. `dry_run=True` reports what would run without loading anything. |
| `run_transform(select=None, full_refresh=False)` | Run `dbt build` (models and tests); equivalent to `dango run`. Returns `status`, dbt `output`, structured `results` (including the failing nodes and why) and `post_build`. Any failing model or test reports `failed`. |
| `run_doctor()` | Check credential health for every configured source (`ok`, `missing`, `expired`, `expiring_soon`); equivalent to `dango doctor`. Always fresh: it bypasses the short credential-health cache that `dango doctor` may serve. |
| `validate_project(check_connectivity=False, include_passed=False)` | Run the same checks as `dango validate` and return the warnings and failures. Does not modify config or the warehouse, but runs `dbt parse`. |
| `get_logs(log="activity", lines=100, level=None, source=None, contains=None)` | Read the tail of a log: `activity`, `dango` or `dbt`. Secrets are redacted; `lines` is clamped to 1 through 500. |
| `get_sync_history(source_name=None, limit=10)` | Recent sync results for one source, or the latest entries across all sources. |
| `get_platform_status()` | Whether this project's Dango server is running, scheduler status, who holds the dbt/sync write lock, and warehouse file info. |
| `get_warehouse_health()` | Find orphaned raw tables (no matching configured source) and report DuckDB health. |
| `get_schema_drift(source=None, table_name=None, limit=50)` | List schema drift events and the sources whose dbt run is skipped until drift is accepted (`needs_attention`). |
| `accept_schema_drift(source)` | Accept a source's current schema as the new baseline, unblocking dbt. Review `get_schema_drift` and update affected models first. |

### Schedules

| Tool | Purpose |
|------|---------|
| `list_schedules()` | List schedules with settings, computed `next_run`, and (when this project's server is running) whether each is `loaded` in the live scheduler. |
| `add_schedule(schedule_name, cron, sources, timezone="UTC", skip_dbt=False)` | Add a sync schedule. `skip_dbt=True` syncs without running dbt afterwards. |
| `update_schedule(schedule_name, cron=None, sources=None, timezone=None, skip_dbt=None)` | Change only the arguments you pass. |
| `set_schedule_enabled(schedule_name, enabled)` | Enable or disable a schedule without deleting it. |
| `remove_schedule(schedule_name)` | Permanently remove a schedule. |
| `reload_schedules()` | Re-read `schedules.yml` and apply it to the running scheduler. The tools above already do this; use it after editing the file by hand. |

Every schedule change is saved first, then Dango tries to apply it to the scheduler of **this
project's own** running server. The `activation` field in the result says what happened:

- `reloaded` — the running scheduler was reloaded (`loaded` says whether it now holds the schedule).
- `server_not_running` — saved, but Dango isn't running for this project; the schedule starts on the
  next `dango start`.
- `reload_failed` — saved, but the reload request failed or returned an error; `activation_detail`
  says why, and restarting `dango start` applies it.

### Catalog & warehouse

| Tool | Purpose |
|------|---------|
| `get_catalog(source_filter=None)` | All tables grouped by schema. |
| `get_table_schema(table_name, schema=None)` | Columns, types, descriptions and data tests for a table. Descriptions come from the dbt docs; undocumented items have `description: null`. |
| `get_lineage(model_name=None)` | dbt lineage from the manifest: the full model summary, or one model's `depends_on` and `referenced_by`. |
| `query(sql, row_limit=500)` | Run a read-only query: a single `SELECT` or `WITH ... SELECT`, up to 102,400 characters, at most 500 rows, with a timeout of `api.query_timeout_seconds` (default 30). PII-flagged columns are masked by name; see [limits](#what-the-agent-cant-do-limits). |

### Governance / PII

| Tool | Purpose |
|------|---------|
| `scan_pii(source, table_name=None)` | Scan a source's raw tables for PII and refresh the cached findings. The first run may download a language model, which needs network access. |
| `get_pii_findings(source=None, table_name=None, limit=100)` | List cached findings with their `effective_status` after overrides. Never includes sample values. |
| `list_pii_overrides(source=None)` | List per-column overrides: `pii` (force-mask) and `not_pii` (dismissed false positive). |
| `set_pii_override(source, table_name, column_name, pii_status="pii", reason=None)` | Mark a raw column as PII so `query` masks it. Only `pii` is accepted: an agent can tighten but never loosen classification. |
| `delete_pii_override(source, table_name, column_name)` | Delete a `not_pii` override, which re-masks the column. A `pii` override cannot be deleted over MCP because that would unmask the column. |

Marking a column `not_pii` is something only you can do, with `dango governance pii-set` or the web
UI.

### Docs

| Tool | Purpose |
|------|---------|
| `get_model_docs(model_name)` | A model's documentation and how it compares with the warehouse columns. |
| `get_source_docs(source_name)` | A source's documentation and its raw tables' docs. Returns both the source description from `.dango/sources.yml` and the dbt source description. |
| `docs_coverage(layer=None)` | Documentation coverage per model, using the same placeholder rules as `dango validate`. |
| `update_source_table_docs(source_name, table, description=None, columns=None)` | Edit a raw table's docs in `dbt/models/staging/sources_<source>.yml`. Columns merge by name; other content is preserved, but YAML comments are lost. The table must already exist in the file (sync creates it). |
| `generate_docs()` | Regenerate dbt docs (`dbt docs generate`). Holds the dbt lock; retry if the warehouse is busy. |

Model and column docs are edited with `update_model`; the source's own description with
`update_source(description=...)`.

### Remote

These tools act on the server created by `dango deploy`, over SSH, using the deployment recorded in
your project. Without one they return an error telling you to run `dango deploy` first.

| Tool | Purpose |
|------|---------|
| `remote_status()` | The server's resources, services, DuckDB size, versions, last syncs, last deployment and backup. |
| `remote_history(limit=10)` | Recent deployments from the server's deploy journal, newest first. |
| `remote_logs(service="dango", lines=100)` | Tail of the `dango`, `caddy` or `metabase` log. `lines` is clamped to 1 through 500 and output is capped at 200 KB. Only secret patterns are redacted; log text can still contain non-secret personal data. |
| `remote_query(sql, timeout=30)` | Read-only `SELECT` against the deployed warehouse (`timeout` 1 to 120 seconds). PII-flagged columns are masked by name, using both your local findings and the server's. |
| `remote_sync(source_name, full_refresh=False, backfill=None, wait=True)` | Sync one source on the server. The server runs the configuration it was last pushed, so sources or changes you haven't pushed aren't there. `source_name` must exist in your local `sources.yml`. `wait=True` blocks up to an hour (which can exceed your client's timeout; the sync keeps running on the server); `wait=False` starts it and returns immediately. |
| `remote_push(dry_run=True, confirm=False)` | Push local config and dbt files to the server and rebuild changed models. Defaults to a dry run that lists what would change (the git checks run on the dry run too). See [limits](#what-the-agent-cant-do-limits). |

---

## Worked examples

The tool calls and results below are real output from running these tools through the actual MCP
server (`dango mcp run`) against a scratch test project, not hand-written illustrations. Long
fields are replaced with `…` and marked as trimmed; no value is edited. File paths from the scratch
project are shortened to `…/`.

### "Add my orders CSV and build a revenue model"

The agent starts by asking what the source type needs, then creates the source. `file_path` points
at the file you gave it (a leading `~` is expanded), and Dango copies it into
`data/uploads/<source_name>/`. The agent leaves `directory` out when it passes `file_path`; a
different `directory` is rejected. A local file needs no credentials, so `credentials_required` is
empty. (Schema trimmed; the file path is shortened.)

```
> get_source_setup_schema("local_files")
{
  "source_type": "local_files",
  "display_name": "File Import (CSV, JSON, Parquet)",
  "description": "…",
  "auth_type": "none",
  "setup_supported": true,
  "supports_empty_sync_policy": true,
  "fields": [
    {
      "name": "directory",
      "type": "path",
      "required": true,
      "default": "data/uploads",
      "choices": null,
      "help": "…",
      "prompt": "…",
      "managed_by": "agent"
    },
    {
      "name": "file_pattern",
      "type": "string",
      "required": true,
      "default": "*",
      "choices": null,
      "help": "…",
      "prompt": "…",
      "managed_by": "agent"
    },
    {
      "name": "notes",
      "type": "text",
      "required": false,
      "default": null,
      "choices": null,
      "help": "…",
      "prompt": "…",
      "managed_by": "agent"
    }
  ],
  "resources": null,
  "setup_guide": "…",
  "first_sync_note": null,
  "note": "To import a local file, pass file_path to create_source and omit 'directory': the file is copied to data/uploads/<source_name>/."
}
```

```
> create_source(source_type="local_files", source_name="orders_csv", description="Orders exported from the shop", file_path="/path/to/orders.csv")
{
  "status": "created",
  "source_name": "orders_csv",
  "source_type": "local_files",
  "source_config": {
    "name": "orders_csv",
    "type": "local_files",
    "enabled": true,
    "description": "Orders exported from the shop",
    "local_files": {
      "directory": "data/uploads/orders_csv",
      "file_pattern": "*"
    },
    "empty_sync_policy": "block"
  },
  "files_changed": [
    ".dango/sources.yml",
    "data/uploads/orders_csv/orders.csv"
  ],
  "credentials_required": [],
  "warnings": [],
  "validation_errors": [],
  "next_steps": [
    "Then call validate_source('orders_csv') and run_sync(source_name='orders_csv')"
  ]
}
```

Before syncing, `validate_source` confirms the file was found. `run_sync` then loads it and builds
the staging model:

```
> validate_source("orders_csv")
{
  "source_name": "orders_csv",
  "type": "local_files",
  "enabled": true,
  "ready": true,
  "issues": [],
  "files_found": 1
}
```

```
> run_sync(source_name="orders_csv")
{
  "success_count": 1,
  "failed_count": 0,
  "skipped_count": 0,
  "success_sources": [
    "orders_csv"
  ],
  "failed_sources": [],
  "skipped_sources": [],
  "results": [
    {
      "status": "success",
      "new": 1,
      "updated": 0,
      "deleted": 0,
      "skipped": 0,
      "total_rows": 4,
      "source": "orders_csv",
      "rows_loaded": 4,
      "files_processed": 1,
      "uses_replace_mode": true
    }
  ],
  "oauth_warnings": [],
  "transform_status": "success",
  "transform_error": null,
  "hooks_status": "success",
  "hooks_failed": [],
  "metabase": "not_running",
  "status": "completed",
  "warnings": []
}
```

Next the agent writes a marts model. `validate_model` checks the SQL without writing anything, and
here it catches a wrong guess at the staging model's name, with a suggestion:

```
> validate_model(model_name="fct_daily_revenue", layer="marts", sql="select order_date, sum(amount) as revenue, count(*) as orders from {{ ref('stg_orders_csv__orders') }} group by order_date")
{
  "valid": false,
  "error": "ref('stg_orders_csv__orders') does not match any model, seed or snapshot (did you mean 'stg_orders_csv__orders_csv'?)",
  "errors": [
    "ref('stg_orders_csv__orders') does not match any model, seed or snapshot (did you mean 'stg_orders_csv__orders_csv'?)"
  ]
}
```

With the corrected name it passes:

```
> validate_model(model_name="fct_daily_revenue", layer="marts", sql="select order_date, sum(amount) as revenue, count(*) as orders from {{ ref('stg_orders_csv__orders_csv') }} group by order_date")
{
  "valid": true,
  "model_name": "fct_daily_revenue",
  "warnings": [],
  "refs": [
    "stg_orders_csv__orders_csv"
  ],
  "sources": []
}
```

`create_model` writes the SQL file and its `schema.yml` entry, and runs `dbt parse` to confirm the
project still compiles (`parse_ok`). It does not build the model; `run_transform` does that, running
the model together with its tests. (Output and per-node results trimmed.)

```
> create_model(model_name="fct_daily_revenue", layer="marts", description="Revenue and order count per day", sql="…", columns=[{"name": "order_date", "description": "Day the order was placed", "data_tests": ["not_null", "unique"]}])
{
  "model_name": "fct_daily_revenue",
  "layer": "marts",
  "status": "created",
  "path": "dbt/models/marts/fct_daily_revenue.sql",
  "files_changed": [
    "dbt/models/marts/fct_daily_revenue.sql",
    "dbt/models/marts/schema.yml"
  ],
  "warnings": [],
  "refs": [
    "stg_orders_csv__orders_csv"
  ],
  "sources": [],
  "downstream": [],
  "table_existed": false,
  "dropped_table": false,
  "parse_ok": true,
  "monitors_removed": []
}
```

```
> run_transform(select="fct_daily_revenue")
{
  "status": "completed",
  "output": "…",
  "results": {
    "elapsed_seconds": 0.2822239398956299,
    "counts": {
      "success": 3,
      "pass": 2,
      "error": 0,
      "fail": 0,
      "warn": 0,
      "skipped": 0
    },
    "nodes": "…",
    "failed": []
  },
  "post_build": {
    "model_status": "updated",
    "schema_sync": "updated",
    "metabase": "not_running",
    "metabase_schema_synced": false
  }
}
```

Finally the agent reads the numbers with `query`. (The `pii_masking` note is trimmed; see
[the limits](#what-the-agent-cant-do-limits).)

```
> query(sql="select * from marts.fct_daily_revenue order by order_date")
{
  "columns": [
    "order_date",
    "revenue",
    "orders"
  ],
  "rows": [
    [
      "2026-09-01",
      169.9,
      2
    ],
    [
      "2026-09-02",
      35.5,
      1
    ],
    [
      "2026-09-03",
      89.99,
      1
    ]
  ],
  "row_count": 3,
  "truncated": false,
  "pii_masking": {
    "enabled": true,
    "masked_columns": [],
    "note": "…"
  }
}
```

### "Connect Stripe"

Stripe needs an API key, and no tool accepts one. `create_source` configures everything else and
returns what's missing in `credentials_required` and `next_steps`. It also adds an empty
`STRIPE_PAYMENTS_API_KEY=` line to your `.env` for you to fill in (the variable name is derived from
the source name):

```
> create_source(source_type="stripe", source_name="stripe_payments", config={"endpoints": ["Charge", "Customer"], "start_date": "2026-07-01"})
{
  "status": "created",
  "source_name": "stripe_payments",
  "source_type": "stripe",
  "source_config": {
    "name": "stripe_payments",
    "type": "stripe",
    "enabled": true,
    "description": "Stripe - added via wizard",
    "stripe": {
      "stripe_secret_key_env": "STRIPE_PAYMENTS_API_KEY",
      "endpoints": [
        "Charge",
        "Customer"
      ],
      "start_date": "2026-07-01"
    },
    "empty_sync_policy": "block"
  },
  "files_changed": [
    ".env",
    ".dango/sources.yml"
  ],
  "credentials_required": [
    {
      "kind": "env_var",
      "detail": "Set STRIPE_PAYMENTS_API_KEY in .env (Find in Stripe Dashboard > Developers > API Keys)",
      "name": "STRIPE_PAYMENTS_API_KEY",
      "command": null
    }
  ],
  "warnings": [],
  "validation_errors": [],
  "next_steps": [
    "Ask the user to set STRIPE_PAYMENTS_API_KEY in .env",
    "Then call validate_source('stripe_payments') and run_sync(source_name='stripe_payments')"
  ]
}
```

`validate_source` confirms the source isn't ready yet:

```
> validate_source("stripe_payments")
{
  "source_name": "stripe_payments",
  "type": "stripe",
  "enabled": true,
  "ready": false,
  "issues": [
    "Set STRIPE_PAYMENTS_API_KEY in .env"
  ],
  "files_found": null
}
```

The agent then tells you to put the key in `.env` (you edit the file; no Dango tool accepts or
returns the value, but an agent with its own file-reading tool could read `.env`, so restrict that
if it matters to you):

```
STRIPE_PAYMENTS_API_KEY=sk_test_dummy
```

Once you have, the same check passes. (Without `check_connectivity=True`, `validate_source` only
checks that the variable is set; it makes no network call.)

```
> validate_source("stripe_payments")
{
  "source_name": "stripe_payments",
  "type": "stripe",
  "enabled": true,
  "ready": true,
  "issues": [],
  "files_found": null
}
```

The agent can now call `run_sync(source_name="stripe_payments")`.

### "Why did last night's sync fail?"

To reproduce a failure, the scratch project's `refunds_csv` source had its uploads folder deleted
after the first successful sync. The next `run_sync` reports it:

```
> run_sync(source_name="refunds_csv")
{
  "success_count": 0,
  "failed_count": 1,
  "skipped_count": 0,
  "success_sources": [],
  "failed_sources": [
    {
      "name": "refunds_csv",
      "error": "CSV directory not found: …/data/uploads/refunds_csv",
      "error_type": null
    }
  ],
  "skipped_sources": [],
  "results": [
    {
      "status": "failed",
      "source": "refunds_csv",
      "error": "CSV directory not found: …/data/uploads/refunds_csv",
      "rows_loaded": 0
    }
  ],
  "oauth_warnings": [],
  "transform_status": "skipped",
  "transform_error": null,
  "hooks_status": "success",
  "hooks_failed": [],
  "status": "failed",
  "warnings": []
}
```

The agent checks the history and the activity log (trimmed to the last two entries) for the cause
and when it started:

```
> get_sync_history(source_name="refunds_csv", limit=5)
[
  {
    "timestamp": "2026-10-01T10:21:06.453102+00:00",
    "status": "failed",
    "duration_seconds": 0.03,
    "rows_processed": 0,
    "full_refresh": true,
    "error_message": "CSV directory not found: …/data/uploads/refunds_csv",
    "source": "refunds_csv"
  },
  {
    "timestamp": "2026-10-01T10:20:54.517362+00:00",
    "status": "success",
    "duration_seconds": 0.4,
    "rows_processed": 4,
    "total_row_count": null,
    "full_refresh": true,
    "error_message": null,
    "start_date": null,
    "source": "refunds_csv"
  }
]
```

```
> get_logs(log="activity", lines=5, source="refunds_csv")
{
  "log": "activity",
  "path": ".dango/logs/activity.jsonl",
  "entries": [
    "…",
    {
      "timestamp": "2026-10-01T10:21:06.470970+00:00",
      "level": "info",
      "source": "refunds_csv",
      "message": "Starting sync",
      "category": "…",
      "dango_version": "…"
    },
    {
      "timestamp": "2026-10-01T10:21:06.481433+00:00",
      "level": "error",
      "source": "refunds_csv",
      "message": "Sync failed: CSV directory not found: …/data/uploads/refunds_csv",
      "category": "…",
      "dango_version": "…"
    }
  ],
  "truncated": false
}
```

`error_message` names the problem, so a configuration or file problem like this one needs no further
digging. `validate_source` confirms it from the other side:

```
> validate_source("refunds_csv")
{
  "source_name": "refunds_csv",
  "type": "local_files",
  "enabled": true,
  "ready": false,
  "issues": [
    "No files matching '*' in data/uploads/refunds_csv"
  ],
  "files_found": 0
}
```

`run_doctor` checks *credentials*, not files, so it correctly reports no problem here. It is the
tool for credential-shaped failures such as an expired OAuth token or a missing API key:

```
> run_doctor()
[
  {
    "source": "orders_csv",
    "type": "local_files",
    "auth_type": "none",
    "status": "ok",
    "detail": ""
  },
  {
    "source": "stripe_payments",
    "type": "stripe",
    "auth_type": "api_key",
    "status": "ok",
    "detail": ""
  },
  {
    "source": "refunds_csv",
    "type": "local_files",
    "auth_type": "none",
    "status": "ok",
    "detail": ""
  }
]
```

---

## What the agent can't do (limits)

Some of these limits are enforced by the tools themselves (secrets, PII overrides that can only
tighten, git guardrails on remote pushes). Others (`dry_run` first, `confirm`, `force`) are guard
rails the agent is told to follow, but the agent supplies those arguments itself, so review a dry
run before you approve anything.

### Secrets are never accepted

No tool accepts a secret value. If an agent passes one in `config`, the call fails with an error
telling it to leave the field out. Instead, `create_source` and `update_source` return `credentials_required`
and `next_steps` for anything still missing (and `validate_source` reports what is still unset): you
add the value to `.env` yourself (or to `.dlt/secrets.toml` where `next_steps` says so), or run
`dango oauth <source_type>` for OAuth sources. If a source's stored
`*_env` setting holds something that isn't a valid environment-variable name (for example a key
pasted in by hand), results show a placeholder instead of the value. Logs returned by `get_logs` and
`remote_logs` have secret-looking values masked.

### PII masking is a guardrail, not a security boundary

`query` (and `remote_query`) mask result columns whose **output name** matches a column flagged as
PII in a raw table, by a scan or by an override. The result's `pii_masking` field lists what was
masked and carries this note, verbatim from the tool:

> Masking matches output column names (case-insensitive) against columns flagged as PII in raw
> tables, so an aliased column (email AS contact) or an expression-derived name (upper(email)) is NOT
> masked. Filtering on a masked column (WHERE email LIKE 'a%') and aggregates over it can still
> reveal information. This is a guardrail against accidental exposure, not a security boundary.
> Disable with api.mcp_mask_pii: false in project.yml.

It exists to keep values from being sent to your LLM provider by accident. It does not stop a
determined or confused agent. Specifically, these are **not** covered:

- **Aliases and expressions**: `email AS contact`, `upper(email)`
- **Whole-row and struct selects**: `SELECT t FROM raw_orders t` returns every column of the row
  as one value
- **`to_json`** (and similar functions) over a row or column
- **Filter probing**: `WHERE email = '<guess>'` or `LIKE 'a%'` confirms a value without returning it
- **Aggregates** over a masked column

Here it is with a real run: `customer_id` marked as PII in the scratch project is masked when
selected by name, and not when aliased. (`pii_masking` notes trimmed.)

```
> query(sql="select order_id, customer_id from raw_orders_csv.orders_csv order by order_id limit 2")
{"columns": ["order_id", "customer_id"], "rows": [[1001, "[PII masked]"], [1002, "[PII masked]"]], "row_count": 2, "truncated": false, "pii_masking": {"enabled": true, "masked_columns": ["customer_id"]}}

> query(sql="select order_id, customer_id as contact from raw_orders_csv.orders_csv order by order_id limit 2")
{"columns": ["order_id", "contact"], "rows": [[1001, 201], [1002, 202]], "row_count": 2, "truncated": false, "pii_masking": {"enabled": true, "masked_columns": []}}
```

Treat anything the agent can query as readable by the agent and your LLM provider. To keep a column
out of reach, don't load it into the warehouse. Masking is on by default; turn it off
with `api.mcp_mask_pii: false` in `.dango/project.yml`. Agents can add `pii` overrides
(`set_pii_override`) but can never remove one or mark a column `not_pii`; that takes you, through
the CLI or web UI.

### One writer at a time

DuckDB allows one writer. Tools that write to the warehouse or run dbt (`run_sync`, `run_transform`,
`generate_docs`, and `remove_model` when it drops a table) take the same lock the CLI uses. If a
sync or dbt run already holds it, the tool waits and then returns an error saying another sync or dbt
run holds the lock. The wait is up to 5 minutes for `run_transform` (which can exceed your client's
tool timeout) and 30 seconds for `remove_model` and `generate_docs`; `run_sync` reports the lock
failure in its own summary. The agent should wait and retry. `get_platform_status`
shows who currently holds the lock.

### Remote tools

- `remote_push` defaults to `dry_run=True`, which only lists what would change. A real push needs
  both `dry_run=False` **and** `confirm=True`, and an agent should only attempt it after showing you
  the dry-run result and getting your approval. Without `confirm=True`, the call is rejected.
- Git guardrails (you must be on the deploy branch, with a clean working tree) can't be overridden
  from MCP, and a held deploy lock is never forced.
- Rollback is CLI-only: `dango remote rollback`.
- `remote_sync` runs the configuration last pushed to the server, so push first if you've added
  sources or models.

The remote tools are covered by automated tests but have not yet been verified against a live deployed server in this release.

### Git warnings on write tools

These tools check your git state and, when something looks risky, add a `git_warning` key (a list of
strings) to their result: `create_source`, `update_source`,
`set_source_enabled`, `remove_source`, `create_model`, `update_model`, `remove_model`,
`add_schedule`, `update_schedule`, `set_schedule_enabled`, `remove_schedule`, `accept_schema_drift`
and `update_source_table_docs`. A dry run, or a call that changes nothing, adds none. Because each write leaves uncommitted changes,
later writes in the same session will carry the "uncommitted changes" warning too. See
[Safety](#safety) for what triggers it.

---

## Safety

Mutation tools are not a separate, less-validated path. They go through the same service layers
the CLI uses (shared modules, and in several cases the identical function):

- **`create_source`** validates the settings and writes the source through a source-setup service
  module shared with the `dango source add` wizard, so the same validation rules apply;
  **`update_source`** and **`set_source_enabled`** go through the shared source lifecycle service
  (the CLI has no direct equivalent), and **`remove_source`** uses the same removal function as
  `dango source remove`. `remove_source` refuses to remove a
  source that models depend on unless `force=True`, and leaves warehouse data and `.env` alone. None
  of them create credentials; see [Secrets are never accepted](#secrets-are-never-accepted).
- **`create_model`**, **`update_model`** and **`remove_model`** go through Dango's model service,
  the same one `dango model add` and `dango model remove` use. They write SQL and `schema.yml`,
  check refs, lineage and naming before writing, and run `dbt parse` to roll back a change that
  breaks the project. They don't build anything; that's `run_transform`.
- **`run_sync`** calls `dango.ingestion.run_sync`, the identical function `dango sync` uses,
  including its internal `DbtLock` acquisition around the data load and the dbt step after it.
  Concurrent syncs and dbt runs are serialized the same way regardless of whether they were
  triggered from the CLI or from an agent.
- **`run_transform`** acquires the same `DbtLock` as `dango run` before calling dbt, and runs the
  same follow-up steps afterwards (recording model status, syncing `schema.yml`, refreshing
  Metabase). If the lock is already held, it returns a clean `{"status": "failed", "error": ...}`
  rather than risking the warehouse. See the [dbt Workflows](../workflows/dbt-workflows.md) page for
  more on the `DbtLock` model.
- **`run_doctor`** calls the identical credential-health function `dango doctor` uses, and
  **`validate_project`** the one `dango validate` uses.
- **Schedule tools** edit the same schedule configuration the CLI and web UI use, then reload the
  scheduler of *this project's* running server (never another project's). If Dango isn't running,
  the change is saved and applied on the next `dango start`; see `activation` in
  [Schedules](#schedules).
- **Git warnings.** The write tools listed under
  [Git warnings on write tools](#git-warnings-on-write-tools) check your project's git state before
  returning. If your project is a git repo and you're on `main`/`master`, in a detached HEAD, the
  working tree has uncommitted changes, or its status can't be determined, the response includes a `git_warning` key (a list of warning
  strings) alongside the normal result. For example, on `main` with a clean tree you'd see something
  like `"On branch 'main' — this change will be written directly to that branch. Consider creating
  a feature branch first."` This is advisory only: the tool still writes the file and reports
  success, it just gives the agent (and you) a heads-up so an LLM-driven session doesn't silently
  commit changes straight to your default branch. Non-git projects and clean feature branches get no
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

The remote tools are the exception to "local only": they connect over SSH to the server recorded by `dango deploy`, using your existing SSH credentials, so an agent with them can act on that server as you. Tools that call out to other services (`scan_pii` may download a language model, `validate_source` with `check_connectivity=True` calls the provider's API) need network access too.

---

## Next Steps

- [dlt Workflows](../workflows/dlt-workflows.md) - Source configuration and sync internals
- [dbt Workflows](../workflows/dbt-workflows.md) - Direct dbt access and the `DbtLock` model
- [Troubleshooting](../workflows/troubleshooting.md) - General troubleshooting guide
