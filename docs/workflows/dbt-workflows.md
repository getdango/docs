# dbt Workflows

Using dbt directly for transformation development and debugging.

---

## Overview

Dango uses [dbt](https://getdbt.com/) for data transformations. While `dango run` handles typical workflows, direct dbt access is useful for:

- Developing and debugging specific models
- Running tests
- Generating documentation
- Advanced selector patterns

---

## dbt Project Structure

Dango creates and manages a dbt project in the `dbt/` directory:

```
dbt/
├── dbt_project.yml          # Project configuration
├── profiles.yml             # Connection profiles (auto-generated)
├── models/
│   ├── staging/             # Auto-generated from sources
│   │   ├── sources.yml      # Source definitions
│   │   └── stg_*.sql        # Staging models
│   ├── intermediate/        # Your business logic
│   └── marts/               # Final tables
├── macros/                  # Reusable SQL
├── tests/                   # Custom tests
└── seeds/                   # Static data
```

---

## Running dbt Commands

### Navigate to dbt Directory

```bash
# All dbt commands must run from the dbt directory
cd dbt

# Or use --project-dir flag
dbt run --project-dir ./dbt
```

### Common Commands

```bash
# Run all models
dbt run

# Run specific model
dbt run --select my_model

# Run model and its downstream dependencies
dbt run --select my_model+

# Run model and its upstream dependencies
dbt run --select +my_model

# Run entire lineage
dbt run --select +my_model+
```

---

## Development Workflow

### 1. Create a New Model

```sql
-- dbt/models/marts/fct_daily_revenue.sql
{{ config(materialized='table') }}

select
    date_trunc('day', order_date) as day,
    sum(amount) as total_revenue,
    count(distinct order_id) as order_count
from {{ ref('stg_orders') }}
group by 1
```

### 2. Compile to Check SQL

```bash
# Compile without running (validates SQL)
dbt compile --select fct_daily_revenue

# View compiled SQL
cat target/compiled/my_project/models/marts/fct_daily_revenue.sql
```

### 3. Run the Model

```bash
# Run single model
dbt run --select fct_daily_revenue

# Run with full refresh (rebuild table)
dbt run --select fct_daily_revenue --full-refresh
```

### 4. Test the Model

```bash
# Run all tests
dbt test

# Run tests for specific model
dbt test --select fct_daily_revenue
```

---

## Selector Patterns

dbt selectors let you target specific models:

| Pattern | Description | Example |
|---------|-------------|---------|
| `model_name` | Single model | `dbt run --select fct_revenue` |
| `+model_name` | Model + upstream | `dbt run --select +fct_revenue` |
| `model_name+` | Model + downstream | `dbt run --select fct_revenue+` |
| `path/to/models` | All models in path | `dbt run --select marts/` |
| `tag:my_tag` | Models with tag | `dbt run --select tag:daily` |
| `source:name` | Source-related models | `dbt run --select source:stripe+` |

### Exclude Patterns

```bash
# Run everything except staging
dbt run --exclude staging/

# Run marts except one model
dbt run --select marts/ --exclude fct_large_table
```

---

## Testing

### Built-in Tests

Add tests in schema YAML files:

```yaml
# dbt/models/marts/schema.yml
version: 2

models:
  - name: fct_daily_revenue
    description: Daily revenue aggregations
    columns:
      - name: day
        description: Date of revenue
        tests:
          - not_null
          - unique
      - name: total_revenue
        tests:
          - not_null
```

### Custom Tests

```sql
-- dbt/tests/assert_positive_revenue.sql
select *
from {{ ref('fct_daily_revenue') }}
where total_revenue < 0
```

### Run Tests

```bash
# All tests
dbt test

# Tests for specific model
dbt test --select fct_daily_revenue

# Only schema tests
dbt test --select test_type:schema

# Only data tests
dbt test --select test_type:data
```

---

## Documentation

### Generate Docs

```bash
# Generate documentation
dbt docs generate

# Serve documentation locally
dbt docs serve --port 8081
```

### Access via Dango

```bash
# Dango also serves dbt docs
dango docs

# Or access directly
open http://localhost:8081
```

### Add Descriptions

```yaml
# dbt/models/marts/schema.yml
version: 2

models:
  - name: fct_daily_revenue
    description: |
      Daily revenue metrics aggregated from orders.

      **Grain**: One row per day
      **Update frequency**: After each sync

    columns:
      - name: day
        description: Calendar date (truncated to day)
      - name: total_revenue
        description: Sum of all order amounts for the day
```

---

## Debugging

### View Compiled SQL

```bash
# Compile model to see actual SQL
dbt compile --select my_model

# Output is in target/compiled/
cat target/compiled/*/models/**/my_model.sql
```

### Debug Configuration

```bash
# Show dbt configuration
dbt debug

# Example output:
# profiles.yml found at ./profiles.yml
# dbt_project.yml found at ./dbt_project.yml
# Connection test: OK
```

### Log Verbosity

```bash
# Run with debug logging
dbt run --select my_model --debug

# Or set log level
dbt run --select my_model --log-level debug
```

---

## Materializations

### Configure Materialization

```sql
-- View (default for staging)
{{ config(materialized='view') }}

-- Table (for marts)
{{ config(materialized='table') }}

-- Incremental (for large tables)
{{ config(
    materialized='incremental',
    unique_key='id'
) }}
```

### Incremental Models

```sql
-- dbt/models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

select
    order_id,
    customer_id,
    amount,
    created_at
from {{ ref('stg_orders') }}

{% if is_incremental() %}
    where created_at > (select max(created_at) from {{ this }})
{% endif %}
```

---

## Working with Profiles

### Profile Location

Dango auto-generates `profiles.yml`:

```yaml
# dbt/profiles.yml
my_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/warehouse.duckdb
      schema: main
```

### Multiple Environments

```yaml
# dbt/profiles.yml
my_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/warehouse.duckdb
    prod:
      type: duckdb
      path: /var/data/warehouse.duckdb
```

```bash
# Run against specific target
dbt run --target prod
```

---

## Useful Commands Reference

| Command | Description |
|---------|-------------|
| `dbt run` | Run all models |
| `dbt run --select model` | Run specific model |
| `dbt test` | Run all tests |
| `dbt compile` | Compile SQL without running |
| `dbt docs generate` | Generate documentation |
| `dbt docs serve` | Serve docs locally |
| `dbt debug` | Test configuration |
| `dbt deps` | Install packages |
| `dbt clean` | Remove compiled files |
| `dbt seed` | Load seed data |

---

## Next Steps

- [Staging Models](../transformations/staging-models.md) - Auto-generated models
- [Custom Models](../transformations/custom-models.md) - Building transformations
- [Testing](../transformations/testing.md) - Data quality tests
