# Other Commands

Configuration, database, governance, notebooks, monitoring, and utility commands.

---

## Overview

This page covers CLI commands not covered by the dedicated group pages. These include project utilities, database management, data governance, notebook management, and more.

---

## Configuration

### dango config validate

Validate all configuration files: `.dango/sources.yml`, `.dango/project.yml`, and dbt source documentation.

```bash
dango config validate
```

**Checks performed:**

- YAML syntax validity
- Required fields present
- Source configuration correctness
- dbt source documentation consistency

---

### dango config show

Show current configuration values.

```bash
dango config show
```

---

### dango config do-token clear

Remove the stored DigitalOcean API token.

```bash
dango config do-token clear
```

---

## Database

### dango db status

Show database status including orphaned tables. Orphaned tables exist in DuckDB but have no corresponding source in `.dango/sources.yml`.

```bash
dango db status
```

---

### dango db clean

Remove orphaned tables from DuckDB.

```bash
dango db clean [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

!!! warning
    This permanently removes tables from DuckDB. Run `dango db status` first to review what will be deleted.

```bash
dango db clean
dango db clean --yes
```

---

## Local Backup

### dango backup

List local backup archives stored in `.dango/backups/`.

```bash
dango backup
```

Displays all archived backups newest-first with file size and modification time. Archives are created automatically by `dango backup restore` as safety backups before restoring from an archive.

```
.dango/backups/pre-restore-20260820_143022.tar.gz     (245 MB, 2026-08-20 14:30:22)
.dango/backups/pre-restore-20260819_091500.tar.gz     (243 MB, 2026-08-19 09:15:00)
```

---

### dango backup restore

Restore a project from a backup archive. Overwrites local project data and creates a safety backup first.

```bash
dango backup restore /path/to/archive.tar.gz
```

**Workflow:**

1. Specify the path to a `.tar.gz` archive in `.dango/backups/` or elsewhere.
2. A `pre-restore-{TIMESTAMP}.tar.gz` safety backup is created automatically.
3. The archive is extracted, restoring all project files and database state.
4. Restart services manually with `dango start`.

```bash
dango backup restore .dango/backups/pre-restore-20260819_091500.tar.gz
```

!!! warning "Destructive Operation"
    Restore overwrites your current project data. The safety backup created before restore can be used to undo if needed.

!!! note "Local vs. Cloud Backups"
    `dango backup` manages local archives in `.dango/backups/`. For cloud backups to DigitalOcean Spaces, use `dango remote backup` — see [Cloud Backup & Recovery](../deployment/backup-and-recovery.md).

---

## Validation

### dango validate

Validate project configuration and setup. Comprehensive health check that verifies:

- Project directory structure
- Configuration files (`project.yml`, `sources.yml`)
- Data source configurations
- dbt setup (`dbt_project.yml`, `profiles.yml`, models)
- Database connectivity (DuckDB)
- Required dependencies (dlt, dbt, duckdb, etc.)
- File permissions

```bash
dango validate
```

Run before syncing or deploying to catch configuration issues early.

```
Validating project configuration...

✓ Project configuration (.dango/project.yml)
✓ Sources configuration (.dango/sources.yml)
✓ dbt project (dbt/dbt_project.yml)
✓ DuckDB database accessible
✓ Dependencies installed
✗ Docker not running (Metabase won't start)

Validation complete: 1 error, 0 warnings
```

---

## Governance

### dango governance drift-report

Show schema drift events — changes in source table schemas detected during sync.

```bash
dango governance drift-report [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source TEXT` | Filter by source name |
| `--table TEXT` | Filter by table name |
| `--limit INTEGER` | Max events to show |

```bash
dango governance drift-report
dango governance drift-report --source stripe --limit 10
```

---

### dango governance accept

Accept schema drift for a source and resume dbt. Use after reviewing drift events to acknowledge the schema change.

```bash
dango governance accept SOURCE
```

```bash
dango governance accept stripe
```

---

### dango governance pii-report

Show PII (Personally Identifiable Information) findings detected by automated scanning.

```bash
dango governance pii-report [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source TEXT` | Filter by source name |
| `--table TEXT` | Filter by table name |
| `--limit INTEGER` | Max findings to show |

```bash
dango governance pii-report
dango governance pii-report --source my_source --table users
```

---

### dango governance pii-set

Set a PII override for a column. Mark a column as confirmed PII or confirmed not-PII.

```bash
dango governance pii-set SOURCE TABLE COLUMN [OPTIONS]
```

| Option | Required | Description |
|--------|----------|-------------|
| `--status [pii\|not_pii]` | Yes | PII status to set |
| `--reason TEXT` | No | Reason for the override |

```bash
dango governance pii-set my_source users email --status pii --reason "User email addresses"
dango governance pii-set my_source orders order_id --status not_pii
```

---

### dango governance pii-list

List PII overrides.

```bash
dango governance pii-list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source TEXT` | Filter by source name |

---

## Notebooks

### dango notebook new

Create a new Marimo notebook from a starter template.

```bash
dango notebook new [OPTIONS]
```

| Option | Required | Description |
|--------|----------|-------------|
| `-t`, `--template [explore\|quality\|blank]` | No | Starter template |
| `-n`, `--name TEXT` | Yes | Notebook name (no extension) |

**Templates:**

| Template | Description |
|----------|-------------|
| `explore` | Data exploration with DuckDB queries |
| `quality` | Data quality analysis |
| `blank` | Empty notebook |

```bash
dango notebook new -n my_analysis -t explore
dango notebook new -n data_quality -t quality
dango notebook new -n scratch -t blank
```

---

### dango notebook open

Open a notebook in Marimo. Acquires a DuckDB lock, creates a read-only snapshot, and starts the Marimo server. Press Ctrl+C to release the lock and exit.

```bash
dango notebook open NAME
```

```bash
dango notebook open my_analysis
```

!!! info
    Notebooks use a DuckDB snapshot to avoid blocking write operations. The snapshot is created automatically when you open the notebook.

---

## Monitoring

### dango monitor run

Run monitor analysis and display data quality results.

```bash
dango monitor run [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source TEXT` | Filter by source name |

```bash
dango monitor run
dango monitor run --source stripe
```

### dango analyze

Alias for `dango monitor run`.

```bash
dango analyze [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--source TEXT` | Filter by source name |

---

## Metabase

### dango metabase save

Export Metabase dashboards and questions to YAML files in the `metabase/` directory.

```bash
dango metabase save [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--all` | Include personal collections (default: "Shared" only) |
| `--collections TEXT` | Specific collections to export (comma-separated) |

```bash
dango metabase save
dango metabase save --collections "Shared,Marketing"
```

**Workflow:** Make changes in Metabase UI, then run `dango metabase save` to export. Optionally commit to git for version control.

---

### dango metabase load

Import Metabase dashboards and questions from files.

```bash
dango metabase load [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--overwrite` | Replace existing dashboards/questions |
| `--dry-run` | Preview what would be imported |

!!! warning
    `--overwrite` replaces existing items in Metabase. Uncommitted Metabase changes will be lost.

```bash
dango metabase load
dango metabase load --dry-run
dango metabase load --overwrite
```

---

### dango metabase refresh

Refresh Metabase schema to discover new tables and schemas. Use after creating new dbt models or schemas.

```bash
dango metabase refresh
```

---

## Dashboard

### dango dashboard provision

Provision the Data Pipeline Health dashboard in Metabase with pre-built cards for pipeline health score, source sync status, data freshness, row count trends, and dbt test results.

```bash
dango dashboard provision [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--url TEXT` | Metabase URL |
| `--username TEXT` | Metabase admin username (auto-detected from auth DB) |
| `--password TEXT` | Metabase admin password |

```bash
dango dashboard provision
dango dashboard provision --url http://metabase.local
```

---

## Migrations

### dango migrate status

Show migration status for all databases.

```bash
dango migrate status
```

---

### dango migrate run

Apply pending migrations.

```bash
dango migrate run [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--db TEXT` | Apply to a specific database only |

```bash
dango migrate run
dango migrate run --db auth
```

---

## Utilities

### dango info

Show project information: name, purpose, stakeholders, data refresh schedule, last sync time.

```bash
dango info
```

---

### dango rename

Rename the project and update its local domain routing (config, nginx, `/etc/hosts`).

```bash
dango rename NEW_NAME
```

```bash
dango rename my-new-analytics
```

---

### dango cleanup

Remove old log archives, dbt artifacts, and Python cache.

```bash
dango cleanup [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be deleted |
| `-y`, `--yes` | Skip confirmation |
| `--logs-only` | Only clean log archives |
| `--docker` | Also prune dangling Docker volumes |

```bash
dango cleanup --dry-run
dango cleanup --yes
dango cleanup --logs-only
dango cleanup --docker
```

---

### dango upgrade

Upgrade Dango to the latest version, then run pending migrations.

```bash
dango upgrade [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--version TEXT` | Specific version (e.g. `1.2.3`) |
| `-y`, `--yes` | Skip confirmation |

```bash
dango upgrade
dango upgrade --version 1.2.3 -y
```

Restart services with `dango start` after upgrading.

---

### dango serve

Run Dango in production server mode (foreground). Intended for systemd on cloud servers.

```bash
dango serve [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host TEXT` | `0.0.0.0` | Bind address |
| `--port INTEGER` | config or 8800 | Port |
| `--workers INTEGER` | 1 | Number of uvicorn workers |

---

### dango web

Start the Web UI backend server only (without Metabase, file watcher, or dbt-docs). Primarily used for development.

```bash
dango web [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--host TEXT` | Host to bind to |
| `--port INTEGER` | Port to bind to |
| `--reload` | Enable auto-reload (development) |

```bash
dango web                   # Start on default port
dango web --port 3001       # Custom port
dango web --reload          # Auto-reload on code changes
```

!!! info
    Most users should use `dango start` (starts all services) or `dango serve` (production mode). `dango web` is for running the API server in isolation.

---

## Troubleshooting

??? info "Validate shows Docker not running"
    Metabase requires Docker. Start Docker Desktop or the Docker daemon. If you don't need Metabase, the rest of Dango works without Docker.

??? info "Notebook fails to open"
    Another process may hold a DuckDB lock. Wait for active syncs to complete, or check `dango status` for running operations.

??? info "Metabase load skips everything"
    By default, `dango metabase load` skips existing items. Use `--overwrite` to replace them, or `--dry-run` to preview.

??? info "Migration fails"
    Run `dango migrate status` to see which migrations are pending. If a specific database migration fails, check the error output and try `dango migrate run --db <name>`.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [Source & Sync](source-sync.md) — Data source management
- [Transform & Model](transform-model.md) — dbt transformation commands
- [Auth Commands](auth-commands.md) — User authentication
- [Deploy & Remote](deploy-remote.md) — Cloud deployment
