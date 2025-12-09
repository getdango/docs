# Sync & Run

Data syncing and running transformations via CLI.

---

## Overview

Master the core workflow of loading data (`dango sync`) and transforming it (`dango run`, `dango generate`). These commands form the foundation of your data pipeline.

**What you'll learn**:

- Sync data from sources to warehouse
- Generate staging models automatically
- Run dbt transformations
- Incremental vs full-refresh strategies
- Optimize sync performance
- Troubleshoot sync failures

---

## Data Syncing

### Basic Sync

Sync all enabled sources:

```bash
dango sync
```

**What happens**:

1. Reads `.dango/sources.yml` for enabled sources
2. For each source:
   - Connects to source (API, database, file)
   - Fetches data (full or incremental)
   - Writes to DuckDB raw layer
   - Updates metadata (`_dlt_loads` table)
3. Logs progress and results

**Example output**:

```
[12:34:56] Starting sync for 3 sources...

[12:34:57] Syncing stripe_payments (1/3)
[12:34:57] Connecting to Stripe API
[12:34:58] Fetching charges (incremental from 2024-11-01)
[12:35:12] Loaded 1,523 charges
[12:35:13] Fetching customers (full refresh)
[12:35:20] Loaded 342 customers
[12:35:21] Writing to raw_stripe.charges
[12:35:24] Writing to raw_stripe.customers
[12:35:25] ✓ Sync complete (1,865 rows in 29.2s)

[12:35:26] Syncing google_sheets (2/3)
[12:35:27] Connecting to Google Sheets API
[12:35:28] Fetching spreadsheet: Marketing Budget 2024
[12:35:32] Loaded 234 rows from 2 sheets
[12:35:33] Writing to raw.google_sheets
[12:35:34] ✓ Sync complete (234 rows in 8.1s)

[12:35:35] Syncing sales_data (3/3)
[12:35:36] Reading CSV: data/sales.csv
[12:35:37] Loaded 5,432 rows
[12:35:38] Writing to raw.sales_data
[12:35:40] ✓ Sync complete (5,432 rows in 5.2s)

──────────────────────────────────────────────
✓ All syncs complete!

Total rows: 7,531
Total duration: 42.5s
Success: 3/3 sources
Failed: 0/3 sources
──────────────────────────────────────────────
```

### Sync Specific Source

Sync only one source:

```bash
dango sync --source stripe_payments
```

**Use when**:

- Testing new source configuration
- One source updated more frequently
- Debugging specific source issues
- Faster iteration during development

**Output**:

```
[12:34:56] Starting sync for stripe_payments
[12:34:57] Connecting to Stripe API
[12:34:58] Fetching charges (incremental from 2024-11-01)
[12:35:12] Loaded 1,523 charges
[12:35:25] ✓ Sync complete (1,865 rows in 29.2s)
```

### Sync Multiple Specific Sources

```bash
dango sync --source stripe_payments --source google_sheets
```

**Or comma-separated**:

```bash
dango sync --source "stripe_payments,google_sheets"
```

### Full Refresh

Drop and reload all data:

```bash
dango sync --full-refresh
```

**What changes**:

- **Normal sync**: Incremental updates (append new data)
- **Full refresh**: Drop tables, reload from scratch

**Use when**:

- Source schema changed
- Data quality issues (need clean slate)
- Deduplication problems
- Testing pipeline from scratch

**Warning**: Can be slow for large datasets!

**Example**:

```bash
# Full refresh specific source
dango sync --source stripe_payments --full-refresh
```

**Output**:

```
⚠ Full refresh mode enabled
This will DROP and RELOAD all data for selected sources.

Sources to refresh:
  - stripe_payments (28,351 rows will be deleted)

Proceed? (y/N): y

[12:34:56] Dropping raw_stripe.charges
[12:34:57] Dropping raw_stripe.customers
[12:34:58] Starting fresh sync...
[12:35:25] ✓ Sync complete (fresh data loaded)
```

---

## Advanced Sync Options

### Override Start Date

For incremental sources, override the start date:

```bash
dango sync --source stripe_payments --start-date 2024-01-01
```

**Use when**:

- Backfilling historical data
- Testing with specific date range
- Recovering from sync gap

**Example**:

```
[12:34:58] Fetching charges (incremental from 2024-01-01)
           Overriding default: 2024-11-01
[12:35:45] Loaded 15,234 charges (10 months of data)
```

### Sync Specific Table/Resource

For multi-table sources, sync only specific tables:

```bash
dango sync --source stripe_payments --select charges
```

**Multiple tables**:

```bash
dango sync --source stripe_payments --select charges,customers
```

**Use when**:

- One table needs urgent update
- Testing specific table
- Other tables too slow

### Parallel Workers

Increase parallelism for faster syncs:

```bash
dango sync --workers 8
```

**Default**: 4 workers

**Considerations**:

- **More workers**: Faster, but higher CPU/memory
- **Fewer workers**: Slower, but lighter resource usage
- **API rate limits**: May need fewer workers to avoid limits

**Example**:

```bash
# Single-threaded (sequential)
dango sync --workers 1

# Highly parallel
dango sync --workers 16
```

### Dry Run

Preview what would be synced without actually syncing:

```bash
dango sync --dry-run
```

**Output**:

```
DRY RUN MODE - No data will be modified

Would sync 3 sources:

1. stripe_payments
   - charges: ~1,500 new rows (since 2024-11-01)
   - customers: ~300 rows (full refresh)
   - subscriptions: ~500 new rows (since 2024-11-01)
   Estimated: 2,300 rows, ~30s

2. google_sheets
   - Marketing Budget 2024: 234 rows (full refresh)
   Estimated: 234 rows, ~8s

3. sales_data
   - data/sales.csv: 5,432 rows (full refresh)
   Estimated: 5,432 rows, ~5s

Total estimated: 7,966 rows, ~43s

No data was modified.
```

**Use when**:

- Testing new source configuration
- Estimating sync time
- Verifying what will be synced

---

## Auto-Generated Staging

### Generate Staging Models

Create dbt staging models from raw tables:

```bash
dango generate
```

**What it does**:

1. Introspects raw layer schemas
2. For each raw table:
   - Creates `stg_<source>_<table>.sql`
   - Adds deduplication logic
   - Generates column selection
   - Creates schema YAML files
3. Writes to `dbt/models/staging/`

**Output**:

```
Generating staging models...
Introspecting raw layer...

Found sources:
  - stripe (3 tables: charges, customers, subscriptions)
  - google_sheets (1 table: marketing_budget)
  - sales_data (1 table: sales_data)

Generating models...

✓ Generated stg_stripe_charges.sql (12 columns, latest_only)
✓ Generated stg_stripe_customers.sql (8 columns, latest_only)
✓ Generated stg_stripe_subscriptions.sql (15 columns, scd_type2)
✓ Generated stg_google_sheets_marketing_budget.sql (6 columns, latest_only)
✓ Generated stg_sales_data.sql (10 columns, latest_only)

✓ Generated _stg_stripe__sources.yml
✓ Generated _stg_google_sheets__sources.yml
✓ Generated _stg_sales_data__sources.yml

✓ Generated _stg_stripe__schema.yml
✓ Generated _stg_google_sheets__schema.yml
✓ Generated _stg_sales_data__schema.yml

5 models created in dbt/models/staging/

Next step:
  dango run  # Materialize staging models
```

### Generate for Specific Source

```bash
dango generate --source stripe_payments
```

**Output**:

```
Generating staging models for stripe_payments...
Introspecting raw_stripe.* tables...

✓ Generated stg_stripe_charges.sql
✓ Generated stg_stripe_customers.sql
✓ Generated stg_stripe_subscriptions.sql
✓ Generated _stg_stripe__sources.yml
✓ Generated _stg_stripe__schema.yml

3 models created.
```

### Regenerate (Force Overwrite)

Overwrite existing staging models:

```bash
dango generate --force
```

**Warning**:

```
⚠ Force mode enabled
This will OVERWRITE existing staging models:
  - dbt/models/staging/stg_stripe_charges.sql
  - dbt/models/staging/stg_stripe_customers.sql
  - dbt/models/staging/stg_stripe_subscriptions.sql

Manual edits to these files will be lost!

Proceed? (y/N): y
```

**Use when**:

- Source schema changed (new columns)
- Want to update deduplication logic
- Starting fresh with staging

**Best practice**: Don't manually edit generated files. They should be regenerated as sources change.

### Custom Deduplication Strategy

Override default deduplication:

```bash
dango generate --dedup-strategy scd_type2
```

**Strategies**:

- **latest_only** (default): Keep only latest version of each record
- **scd_type2**: Keep all versions with validity periods
- **none**: No deduplication (keep all raw data)

**Example `latest_only`**:

```sql
-- stg_stripe_charges.sql
{{ config(materialized='view') }}

WITH deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY _dlt_extracted_at DESC
        ) as _rn
    FROM {{ source('stripe', 'charges') }}
)

SELECT
    id,
    customer,
    amount,
    status,
    created,
    _dlt_load_id,
    _dlt_extracted_at
FROM deduplicated
WHERE _rn = 1
```

**Example `scd_type2`**:

```sql
-- stg_stripe_subscriptions.sql (slowly changing dimension)
{{ config(materialized='view') }}

SELECT
    id,
    customer,
    status,
    plan_id,
    created,
    _dlt_extracted_at as _valid_from,
    LEAD(_dlt_extracted_at) OVER (
        PARTITION BY id ORDER BY _dlt_extracted_at
    ) as _valid_to,
    CASE
        WHEN LEAD(_dlt_extracted_at) OVER (
            PARTITION BY id ORDER BY _dlt_extracted_at
        ) IS NULL THEN TRUE
        ELSE FALSE
    END as _is_current
FROM {{ source('stripe', 'subscriptions') }}
```

---

## Running Transformations

### Run All dbt Models

Execute all dbt transformations:

```bash
dango run
```

**What happens**:

1. dbt compiles SQL models
2. Executes in dependency order
3. Materializes views and tables
4. Logs results

**Output**:

```
Running dbt...
12:45:01  Running with dbt=1.7.4
12:45:02  Found 15 models, 8 tests, 0 snapshots
12:45:03  Concurrency: 4 threads
12:45:04
12:45:04  1 of 15 START sql view model staging.stg_stripe_charges ........ [RUN]
12:45:05  1 of 15 OK created sql view model staging.stg_stripe_charges ... [SUCCESS in 0.8s]
12:45:05  2 of 15 START sql view model staging.stg_stripe_customers ..... [RUN]
12:45:06  2 of 15 OK created sql view model staging.stg_stripe_customers  [SUCCESS in 0.6s]
...
12:45:10  10 of 15 START sql table model marts.customer_metrics .......... [RUN]
12:45:12  10 of 15 OK created sql table model marts.customer_metrics ..... [SUCCESS in 2.1s]
...
12:45:15  Finished running 8 views, 7 tables in 12.3s.
12:45:15
12:45:15  Completed successfully
12:45:15
12:45:15  Done. PASS=15 WARN=0 ERROR=0 SKIP=0 TOTAL=15
```

### Run Specific Model

```bash
dango run --select customer_metrics
```

**Output**:

```
Running dbt...
12:45:01  Running with dbt=1.7.4
12:45:02  Found 1 model
12:45:03
12:45:03  1 of 1 START sql table model marts.customer_metrics ............ [RUN]
12:45:05  1 of 1 OK created sql table model marts.customer_metrics ....... [SUCCESS in 2.1s]
12:45:05
12:45:05  Completed successfully
```

### Run Model and Dependencies

**Downstream dependencies** (model + everything that depends on it):

```bash
dango run --select customer_metrics+
```

**Upstream dependencies** (model + everything it depends on):

```bash
dango run --select +customer_metrics
```

**Both directions**:

```bash
dango run --select +customer_metrics+
```

**Example**:

```
# customer_metrics depends on stg_stripe_charges, stg_stripe_customers
# revenue_dashboard depends on customer_metrics

# Run only customer_metrics
dango run --select customer_metrics

# Run customer_metrics + staging models it needs
dango run --select +customer_metrics

# Run customer_metrics + revenue_dashboard that uses it
dango run --select customer_metrics+

# Run entire lineage
dango run --select +customer_metrics+
```

### Run by Path

Run all models in directory:

```bash
# All marts
dango run --select marts.*

# Specific subdirectory
dango run --select marts.finance.*

# Multiple paths
dango run --select marts.finance.*,marts.marketing.*
```

### Run by Tag

Tag models in dbt:

```sql
-- dbt/models/marts/customer_metrics.sql
{{ config(
    materialized='table',
    tags=['customer', 'daily']
) }}

SELECT ...
```

Run tagged models:

```bash
# Run all customer models
dango run --select tag:customer

# Run all daily models
dango run --select tag:daily
```

### Exclude Models

```bash
# Run all except slow models
dango run --exclude tag:slow

# Run all marts except finance
dango run --select marts.* --exclude marts.finance.*
```

### Full Refresh dbt

Rebuild incremental models from scratch:

```bash
dango run --full-refresh
```

**For incremental model**:

```sql
-- Normal run: Append only new data
-- Full refresh: Drop and rebuild entire table
{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

SELECT * FROM {{ ref('stg_events') }}
{% if is_incremental() %}
  WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

### Pass dbt Variables

```bash
# Set year variable
dango run --vars '{"year": 2024}'

# Multiple variables
dango run --vars '{"year": 2024, "region": "US"}'
```

**Use in model**:

```sql
-- dbt/models/marts/annual_revenue.sql
SELECT
    DATE_TRUNC('year', created) as year,
    SUM(amount) as revenue
FROM {{ ref('stg_stripe_charges') }}
WHERE YEAR(created) = {{ var('year') }}
GROUP BY year
```

### Custom Threads

```bash
# Single-threaded (sequential)
dango run --threads 1

# High parallelism
dango run --threads 8
```

**Default**: 4 threads

### Fail Fast

Stop on first error:

```bash
dango run --fail-fast
```

**Default behavior**: Continue running other models even if one fails.

**Fail fast**: Stop immediately on first failure.

---

## Common Workflows

### Daily Update Workflow

```bash
#!/bin/bash
# daily-update.sh

# Sync new data
dango sync

# Regenerate staging if schema changed
dango generate

# Run transformations
dango run

# Run tests
dbt test --profiles-dir .dango --project-dir dbt

# Success notification
echo "Daily update complete at $(date)"
```

**Schedule with cron**:

```bash
# Run daily at 6am
0 6 * * * cd /path/to/project && ./daily-update.sh
```

### Development Iteration

```bash
# 1. Sync test data
dango sync --source stripe_payments --start-date 2024-12-01

# 2. Generate staging
dango generate

# 3. Write custom model: dbt/models/marts/my_metric.sql

# 4. Run just your model
dango run --select my_metric

# 5. Check results
duckdb data/warehouse.duckdb "SELECT * FROM marts.my_metric LIMIT 10"

# 6. Iterate: edit model, re-run
dango run --select my_metric
```

### Schema Change Workflow

```bash
# 1. Source adds new column

# 2. Sync to get new column in raw layer
dango sync --source stripe_payments

# 3. Regenerate staging to pick up new column
dango generate --source stripe_payments --force

# 4. Update custom models if needed
vim dbt/models/marts/customer_metrics.sql

# 5. Run transformations
dango run

# 6. Test
dbt test --profiles-dir .dango --project-dir dbt
```

### Backfill Historical Data

```bash
# 1. Sync historical data
dango sync --source stripe_payments --start-date 2023-01-01

# 2. Full refresh transformations
dango run --full-refresh

# 3. Verify data
duckdb data/warehouse.duckdb "
  SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as row_count
  FROM marts.customer_metrics
  GROUP BY month
  ORDER BY month
"
```

---

## Performance Optimization

### Optimize Sync Speed

**1. Use incremental loading**:

```yaml
# .dango/sources.yml
sources:
  - name: large_database
    type: dlt_native
    dlt_native:
      source_module: sql_database
      source_function: sql_database
      function_kwargs:
        incremental:
          cursor_column: updated_at
          initial_value: "2024-01-01"
```

**2. Increase workers**:

```bash
dango sync --workers 8
```

**3. Sync specific tables**:

```bash
# Only urgent tables
dango sync --source large_database --select critical_table
```

**4. Schedule wisely**:

- Sync large sources during off-hours
- More frequent syncs for small, critical sources

### Optimize dbt Performance

**1. Materialize strategically**:

```sql
-- Staging: views (lightweight)
{{ config(materialized='view') }}

-- Marts: tables (fast queries)
{{ config(materialized='table') }}

-- Large marts: incremental (efficient updates)
{{ config(materialized='incremental') }}
```

**2. Increase threads**:

```bash
dango run --threads 8
```

**3. Run selectively during development**:

```bash
# Don't run everything every time
dango run --select +my_model  # Only what you need
```

**4. Use incremental models for large datasets**:

```sql
{{ config(
    materialized='incremental',
    unique_key='event_id'
) }}

SELECT * FROM {{ ref('stg_events') }}
{% if is_incremental() %}
  WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

---

## Troubleshooting

### Sync Fails with Authentication Error

**Error**:

```
✗ Sync failed for stripe_payments
AuthenticationError: Invalid API key
```

**Solution**:

1. **Check API key**:
   ```bash
   # View current config (keys are masked)
   dango source list --verbose

   # Verify in .env
   cat .env | grep STRIPE_API_KEY

   # Test key manually
   curl https://api.stripe.com/v1/charges \
     -u "sk_test_YOUR_KEY:"
   ```

2. **Update API key**:
   ```bash
   # Edit .env
   vim .env
   # Update STRIPE_API_KEY=sk_live_NEW_KEY

   # Retry sync
   dango sync --source stripe_payments
   ```

### Sync Fails with Rate Limit

**Error**:

```
✗ Sync failed for stripe_payments
RateLimitError: Too many requests
```

**Solution**:

1. **Reduce workers**:
   ```bash
   dango sync --source stripe_payments --workers 1
   ```

2. **Add delays** (in source config):
   ```yaml
   sources:
     - name: stripe_payments
       type: stripe
       stripe:
         rate_limit_delay: 1.0  # seconds between requests
   ```

3. **Sync less frequently**:
   - Change from hourly to daily
   - Use incremental instead of full refresh

### dbt Model Fails

**Error**:

```
1 of 15 START sql table model marts.customer_metrics ................ [RUN]
1 of 15 ERROR creating sql table model marts.customer_metrics ....... [ERROR in 0.5s]

Syntax Error: SELECT ...
```

**Solution**:

1. **Check compiled SQL**:
   ```bash
   dbt compile --select customer_metrics --profiles-dir .dango --project-dir dbt
   cat dbt/target/compiled/my_project/models/marts/customer_metrics.sql
   ```

2. **Test SQL directly**:
   ```bash
   duckdb data/warehouse.duckdb < dbt/target/compiled/.../customer_metrics.sql
   ```

3. **Fix model and retry**:
   ```bash
   vim dbt/models/marts/customer_metrics.sql
   dango run --select customer_metrics
   ```

### Staging Models Out of Sync

**Symptom**: New columns in raw data not appearing in staging.

**Solution**:

```bash
# Regenerate staging models
dango generate --force

# Run to materialize
dango run
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-database-outline: **Source Management**

    ---

    Learn how to add and configure sources via CLI.

    [:octicons-arrow-right-24: Source Management](source-management.md)

-   :material-check-circle-outline: **Validation**

    ---

    Validate configuration and troubleshoot issues.

    [:octicons-arrow-right-24: Validation Guide](validation.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Deep dive into dbt transformations and best practices.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete reference for all CLI commands and options.

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

</div>
