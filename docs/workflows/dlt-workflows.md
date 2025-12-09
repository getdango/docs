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

## dlt Pipeline Basics

### How Dango Uses dlt

When you run `dango sync`, Dango:

1. Reads source configuration from `sources.yml`
2. Creates a dlt pipeline targeting DuckDB
3. Runs the appropriate dlt source
4. Stores state in `.dlt/` directory

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
dango sync --source my_source --full-refresh
```

---

## Debugging Sync Issues

### Enable Verbose Logging

```bash
# Set environment variable for detailed logs
export RUNTIME__LOG_LEVEL=DEBUG
dango sync --source problematic_source
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
