# dlt Workflows

Using dlt directly for advanced data loading scenarios.

---

## Overview

Dango uses [dlt (data load tool)](https://dlthub.com/) under the hood for data ingestion. While `dango sync` handles most cases, direct dlt access is useful for:

- Debugging pipeline issues
- Custom source development
- Accessing pipeline state and metadata
- Advanced incremental loading configurations

---

## How Syncs Work

### Sync Subprocess Model

Every sync runs in an isolated subprocess, whether triggered from the CLI, web UI, or scheduler. This keeps the web server responsive and prevents a failing sync from crashing other services.

```
dango sync ──► subprocess ──► dlt load ──► post-sync hooks ──► done
                  │
                  ├── Acquires DbtLock
                  ├── Writes progress to .dango/state/sync_status_{id}.json
                  └── Releases DbtLock on completion
```

The status file at `.dango/state/sync_status_{id}.json` tracks progress through phases: `starting` → `lock_waiting` → `data_load` → `dbt_started` → `completed` (or `failed`).

### Sync Queuing

DuckDB is a single-writer database — only one process can write at a time. Dango enforces this with `DbtLock`:

| Trigger | Behavior when lock is held |
|---------|---------------------------|
| CLI (`dango sync`) | Fails immediately with lock error |
| Web UI (Sync Now button) | Waits up to 5 minutes for lock, then fails |
| Scheduler | Waits up to 5 minutes for lock, then fails |

There is no queue. If a sync cannot acquire the lock within the timeout, it fails and must be retried.

See [DuckDB Single-Writer](../core-concepts/duckdb.md) for details on the locking model.

---

## dlt Pipeline Basics

### Pipeline State Location

```
.dlt/
├── config.toml          # dlt configuration
├── secrets.toml         # Credentials
└── pipelines/           # Pipeline state (auto-created)
    └── my_source/
        └── state/
```

---

## Direct dlt Commands

### View Pipeline Information

```bash
# List all pipelines
dlt pipeline list

# Get info about a specific pipeline
dlt pipeline my_source info

# Show pipeline state
dlt pipeline my_source show
```

### Check Pipeline State

```bash
# View what's been synced
dlt pipeline my_source sync-state

# Example output:
# resource: orders
#   last_value: 2025-01-15T10:30:00
#   rows_synced: 15234
```

### Reset Pipeline

```bash
# Reset a pipeline to re-sync from scratch
dlt pipeline my_source drop

# Then sync again
dango sync my_source --full-refresh
```

---

## Schema Drift Interaction

After each sync, Dango runs a post-sync hook that detects schema drift — columns removed or column types changed in your source data.

**Additive changes** (new columns) are recorded but don't block anything.

**Breaking changes** (columns removed or types changed) block dbt from running until you accept them:

```bash
# Check which sources have unresolved drift
dango governance drift-report

# Accept current schema as new baseline
dango governance accept my_source
```

Until you accept breaking drift, dbt transformations are skipped for that source after each sync.

For full details, see [Schema Drift](../scheduling-monitoring/schema-drift.md).

---

## OAuth Pre-Sync Validation

For OAuth-authenticated sources (Google Sheets, Google Analytics, etc.), Dango validates the token before starting a sync.

```bash
# Check OAuth token status for all sources
dango oauth check
```

| Provider | Token refresh | Action needed |
|----------|--------------|---------------|
| Google | Automatic (dlt handles refresh) | None — tokens auto-renew |
| Facebook | Manual every 60 days | Run `dango oauth setup facebook_ads` to re-authenticate |

Tokens expiring within 7 days show a warning but don't block syncs. Expired tokens fail the sync with a clear error message.

For full details, see [OAuth](../security/oauth.md).

---

## Debugging Sync Issues

### Enable Verbose Logging

```bash
# Set environment variable for detailed logs
export RUNTIME__LOG_LEVEL=DEBUG
dango sync problematic_source
```

### Check dlt Logs

```bash
# dlt logs are in the pipeline directory
cat .dlt/pipelines/my_source/runtime.log
```

### Inspect Last Load

```python
# Python script to inspect load info
import dlt

pipeline = dlt.pipeline(
    pipeline_name="my_source",
    destination="duckdb",
    dataset_name="raw_my_source"
)

# Get load info
load_info = pipeline.last_trace.last_normalize_info
print(load_info)
```

---

## Custom Source Development

### Creating a Custom dlt Source

For APIs not supported by built-in sources:

```python
# custom_sources/my_api.py
import dlt
from dlt.sources.helpers import requests

@dlt.source
def my_api_source(api_key: str = dlt.secrets.value):
    """Custom source for My API."""

    @dlt.resource(write_disposition="merge", primary_key="id")
    def items():
        """Load items from API."""
        url = "https://api.example.com/items"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        yield response.json()["items"]

    return items
```

### Register Custom Source in Dango

```yaml
# .dango/sources.yml
sources:
  - name: my_custom_api
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: "custom_sources.my_api"
      source_name: "my_api_source"
```

### Configure Credentials

```toml
# .dlt/secrets.toml
[sources.my_api_source]
api_key = "your-api-key-here"
```

---

## Incremental Loading

### Understanding Incremental State

dlt tracks incremental loading state automatically:

```python
@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def orders(
    updated_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "updated_at",
        initial_value="2024-01-01T00:00:00Z"
    )
):
    """Load orders incrementally."""
    # Only fetch records after last_value
    params = {"updated_after": updated_at.last_value}
    # ... fetch and yield data
```

### View Incremental State

```bash
# Check what the last synced value was
dlt pipeline my_source sync-state
```

### Reset Incremental State

```bash
# Reset to re-sync all data
dlt pipeline my_source drop

# Or in Python:
pipeline.sync_destination()
```

---

## Advanced Configurations

### Schema Evolution

dlt handles schema changes automatically. Configure behavior:

```toml
# .dlt/config.toml
[schema]
# Allow new columns
allow_new_columns = true
# Don't allow column removal
allow_column_removal = false
```

### Parallelization

```toml
# .dlt/config.toml
[runtime]
# Number of parallel workers
workers = 4
```

### Retry Configuration

```toml
# .dlt/config.toml
[runtime]
# Retry failed requests
request_max_attempts = 3
request_backoff_factor = 1
```

---

## Working with dlt Python API

### Running a Pipeline Directly

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name="test_pipeline",
    destination="duckdb",
    dataset_name="raw_test"
)

# Configure source
source = rest_api_source(
    "https://api.example.com",
    {
        "resources": [
            {"name": "users", "endpoint": "/users"},
            {"name": "orders", "endpoint": "/orders"}
        ]
    }
)

# Run
load_info = pipeline.run(source)
print(load_info)
```

### Accessing Load Metadata

```python
# Get detailed load info
for package in load_info.load_packages:
    for table in package.tables:
        print(f"Table: {table.name}")
        print(f"  Rows: {table.row_count}")
        print(f"  File: {table.file_path}")
```

---

## Troubleshooting dlt

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Pipeline not found" | Pipeline hasn't run yet | Run `dango sync` first |
| "Invalid credentials" | Secrets not configured | Check `.dlt/secrets.toml` |
| "Schema mismatch" | Source schema changed | Run with `--full-refresh` |
| "Rate limit exceeded" | API throttling | Add retry configuration |
| "Database is locked" | Another sync is running | Wait for it to finish or check [DuckDB Locks](troubleshooting.md#duckdb-locks) |
| "OAuth token expired" | Token needs refresh | Run `dango oauth setup <source>` — see [OAuth Expiry](troubleshooting.md#oauth-token-expiry) |

### Getting Help

```bash
# dlt CLI help
dlt --help
dlt pipeline --help

# dlt documentation
open https://dlthub.com/docs
```

---

## Next Steps

- [Custom Sources](../data-sources/custom-sources.md) - Build custom data sources
- [dbt Workflows](dbt-workflows.md) - Transform loaded data
- [Troubleshooting](troubleshooting.md) - More debugging tips
