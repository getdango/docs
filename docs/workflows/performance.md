# Performance Optimization

Strategies for optimizing Dango performance with large datasets.

---

## Overview

As your data grows, you may need to optimize:
- Sync performance (data loading)
- Query performance (DuckDB)
- dbt model execution
- Memory usage

---

## DuckDB Optimization

### Understanding DuckDB

DuckDB is optimized for analytical workloads:
- Columnar storage for fast aggregations
- Automatic parallelization
- In-memory processing with disk spillover

### Version Alignment

DuckDB requires that the Python library and the Metabase JDBC driver share the same major.minor version. Dango handles this automatically — the driver version (`1.5.1.0`) is pinned to match the Python DuckDB dependency (`1.5.x`).

If you upgrade DuckDB manually, the Metabase driver must also be updated. Dango checks version alignment on startup and warns if there is a mismatch.

??? info "Why Version Alignment Matters"
    DuckDB's read-only mode cannot open database files created by a different major.minor version. If the Python library is 1.5.x but the Metabase JDBC driver bundles 1.4.x, Metabase cannot read the database. Dango's startup check and pre-commit hook prevent this drift.

### Memory Configuration

```sql
-- Check current memory limit
SELECT current_setting('memory_limit');

-- Increase memory for large datasets (run in DuckDB CLI)
SET memory_limit = '8GB';
SET threads = 4;
```

Configure in dbt:
```yaml
# dbt/profiles.yml
my_project:
  outputs:
    dev:
      type: duckdb
      path: ../data/warehouse.duckdb
      config:
        memory_limit: '8GB'
        threads: 4
```

### Query Optimization

**Use EXPLAIN to analyze queries**:
```sql
EXPLAIN ANALYZE
SELECT date_trunc('day', order_date), SUM(amount)
FROM raw_orders.orders
GROUP BY 1;
```

**Common optimizations**:

```sql
-- BAD: Full table scan for filter
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- GOOD: Range filter
SELECT * FROM orders
WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';

-- BAD: SELECT *
SELECT * FROM orders JOIN customers USING (customer_id);

-- GOOD: Select only needed columns
SELECT o.order_id, o.amount, c.name
FROM orders o JOIN customers c USING (customer_id);
```

---

## Sync Performance

### Sync Subprocess Model

Syncs run in isolated subprocesses, keeping the web UI responsive. The web server never blocks on a long-running sync — it monitors progress via status files at `.dango/state/sync_status_{id}.json` and broadcasts updates over WebSocket.

This means you can continue using the dashboard, viewing data, and managing sources while a sync runs in the background.

### Single-Writer Constraint

DuckDB allows only one writer process at a time. Dango enforces this with `DbtLock` — a file lock at `.dango/state/dbt.lock`.

**Do not run syncs in parallel.** DuckDB's single-writer constraint means parallel syncs will fail:

```bash
# WRONG: parallel syncs will fail on the second one
dango sync --source source1 &
dango sync --source source2 &

# CORRECT: sync sources sequentially
dango sync --source source1
dango sync --source source2

# CORRECT: sync all sources (Dango handles ordering)
dango sync
```

When a sync is triggered from the web UI while another is running, it waits up to 5 minutes for the lock before failing. The CLI fails immediately.

See [DuckDB Single-Writer](../core-concepts/duckdb.md) for details.

### Reduce Sync Scope

**Select specific endpoints**:
```yaml
sources:
  - name: stripe
    type: stripe
    stripe:
      endpoints:
        - charges      # Only what you need
        - customers
        # Skip: products, plans, etc.
```

**Date range limits**:
```yaml
sources:
  - name: google_analytics
    type: google_analytics
    google_analytics:
      start_date: "2024-01-01"  # Don't fetch all history
```

### Full Refresh Scheduling

```bash
# Regular syncs: incremental
dango sync

# Weekly: full refresh for data quality
dango sync --full-refresh  # Run on weekends
```

---

## Large Dataset Handling

### Sync Strategies

**Incremental Syncs**:
```yaml
# .dango/sources.yml
sources:
  - name: large_source
    type: stripe
    stripe:
      # Only sync recent data after initial load
      start_date: "2024-01-01"
```

**Source Timeouts**:
```yaml
# For slow sources, increase timeout
sources:
  - name: slow_api
    type: rest_api
    rest_api:
      timeout: 600  # 10 minutes
```

### Data Volume Guidelines

| Data Size | Recommendation |
|-----------|---------------|
| < 100 MB | Default settings work well |
| 100 MB - 1 GB | Consider incremental syncs |
| 1 GB - 10 GB | Use materialized tables, indexes |
| > 10 GB | Consider partitioning, external tables |

---

## dbt Performance

### Materialization Strategy

Dango uses `table` materialization for all models to ensure Metabase compatibility:

| Type | Use When | Performance |
|------|----------|-------------|
| `table` | Default for all models | Best query performance, reliable Metabase support |
| `incremental` | Very large, append-only data | Fast to build, fast to query |

!!! note "Why Tables Only"
    Dango auto-generates staging models as tables (not views) for reliable Metabase compatibility. While views rebuild faster, they can cause query issues in Metabase.

```sql
-- Staging: tables (auto-generated by Dango)
{{ config(materialized='table') }}

-- Intermediate: tables
{{ config(materialized='table') }}

-- Marts: tables (query performance matters)
{{ config(materialized='table') }}

-- Large fact tables: incremental
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge'
) }}
```

### Incremental Models

For large fact tables:

```sql
-- dbt/models/marts/fct_events.sql
{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

SELECT
    event_id,
    user_id,
    event_type,
    created_at
FROM {{ ref('stg_events') }}

{% if is_incremental() %}
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Run Specific Models

```bash
# Don't rebuild everything
cd dbt

# Run only what changed
dbt run --select state:modified+

# Run specific model and downstream
dbt run --select my_model+
```

### Parallel Execution

```bash
# Run models in parallel (default is 1)
dbt run --threads 4
```

---

## Multi-Worker Considerations

When running Dango with multiple uvicorn workers (cloud deployments use this by default), be aware of these characteristics:

- **`app.state` is not shared across workers** — each worker has its own instance of in-memory state
- **Scheduler runs in one worker only** — the lifespan context starts the scheduler, but only the first worker's scheduler is active
- **WebSocket connections are per-worker** — a client connected to worker A won't receive broadcasts from worker B

Dango handles this automatically with a file-based sync status watcher that runs in every worker. Each worker monitors `.dango/state/sync_status_*.json` files for changes and broadcasts updates to its own WebSocket clients.

??? info "How Multi-Worker Sync Broadcasting Works"
    Each worker runs a background `sync_status_watcher()` task that polls status files by mtime. When a status file changes, the worker broadcasts the update to its connected WebSocket clients. A `_locally_polled` set prevents duplicate broadcasts for syncs that the worker itself launched.

---

## Memory Management

### Monitor Memory Usage

```bash
# Check DuckDB memory
duckdb data/warehouse.duckdb "SELECT * FROM duckdb_memory()"

# Check system memory during sync
top -pid $(pgrep -f dango)
```

### Reduce Memory Pressure

**Close unused connections**:
```bash
# Stop services when not needed
dango stop
```

**Process in batches**:
```python
# Custom source with batching
@dlt.resource
def large_api():
    for page in range(100):
        batch = fetch_page(page, size=1000)
        yield batch  # Yield batches, not all at once
```

---

## Database Maintenance

### Vacuum and Analyze

```sql
-- Run periodically in DuckDB CLI
VACUUM;
ANALYZE;
```

### Check Table Sizes

```sql
-- Find large tables
SELECT
    table_name,
    estimated_size
FROM duckdb_tables()
ORDER BY estimated_size DESC;
```

### Remove Unused Data

```bash
# Clean up old dlt state
dango db clean

# This removes:
# - DuckDB database
# - dlt pipeline state
# Fresh sync required after
```

---

## Monitoring Performance

### Sync Duration

```bash
# Time a sync
time dango sync --source my_source

# Check sync logs
cat .dango/logs/activity.jsonl | tail -20
```

### Query Performance

```sql
-- Enable profiling
PRAGMA enable_profiling;
PRAGMA profile_output='query_profile.json';

-- Run your query
SELECT ...;

-- Check profile
.read query_profile.json
```

### dbt Timing

```bash
# dbt shows timing by default
dbt run --select my_model

# Detailed timing
dbt run --select my_model --log-level debug
```

---

## Performance Checklist

### Before Scaling

- [ ] Use incremental syncs where possible
- [ ] Materialize slow models as tables
- [ ] Limit sync scope to needed endpoints
- [ ] Set appropriate date ranges

### For Large Datasets

- [ ] Increase DuckDB memory limit
- [ ] Use incremental dbt models
- [ ] Run dbt with multiple threads
- [ ] Schedule full refreshes off-peak

### Troubleshooting Slow Queries

1. Check with `EXPLAIN ANALYZE`
2. Verify indexes exist on join columns
3. Review model materializations
4. Check for unnecessary `SELECT *`

---

## Next Steps

- [dbt Workflows](dbt-workflows.md) - Model optimization
- [Troubleshooting](troubleshooting.md) - Debug slow syncs
- [Backup & Restore](backup-restore.md) - Large database backups
