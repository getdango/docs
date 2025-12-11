# SQL Queries

DuckDB SQL patterns for querying Dango data in Metabase.

---

## Overview

Metabase's SQL editor provides direct access to your DuckDB warehouse. This guide covers Dango-specific patterns and DuckDB syntax essentials.

!!! info "Full DuckDB Reference"
    For complete SQL syntax and functions, see the [DuckDB documentation](https://duckdb.org/docs/sql/introduction).

---

## Quick Start

### Open SQL Editor

1. Navigate to http://localhost:3000
2. Click **"+ New"** → **"SQL query"**
3. Select **"DuckDB"** database
4. Write SQL and click **"Get Answer"**

### First Queries

```sql
-- List all marts tables
SHOW TABLES FROM marts;

-- Query a marts table
SELECT *
FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10;
```

---

## Dango Data Schemas

### Available Schemas

| Schema | Purpose | Example Tables |
|--------|---------|----------------|
| `raw` | Single-table sources (CSV) | `raw.csv_uploads` |
| `raw_*` | Multi-table sources (APIs) | `raw_stripe.charges`, `raw_stripe.customers` |
| `staging` | Auto-generated staging models | `staging.stg_stripe_charges` |
| `intermediate` | Custom business logic | `intermediate.int_customer_orders` |
| `marts` | Analytics-ready tables | `marts.customer_metrics` |

### Schema-Qualified Names

Always use schema prefix:

```sql
-- Correct: Schema.table
SELECT * FROM marts.revenue_by_month

-- Avoid: Unqualified (may fail)
SELECT * FROM revenue_by_month
```

### Explore Tables

```sql
-- Tables in specific schema
SHOW TABLES FROM marts;

-- Show columns and types
DESCRIBE marts.customer_metrics;
```

---

## Querying Dango Data Layers

### Raw Data (dlt Source)

Query unprocessed data from dlt:

```sql
SELECT
    id,
    customer,
    amount / 100.0 as amount_usd,
    status,
    created,
    _dlt_load_id,
    _dlt_extracted_at
FROM raw_stripe.charges
WHERE created >= CURRENT_DATE - INTERVAL 30 DAY;
```

**dlt Metadata Columns**:

| Column | Description |
|--------|-------------|
| `_dlt_load_id` | Unique ID for each dlt sync run |
| `_dlt_extracted_at` | Timestamp when data was extracted |
| `_dlt_id` | Unique row identifier |

**Use cases**: Debugging source data, auditing data lineage, comparing raw vs. transformed.

### Staging Data (Auto-Generated)

Query cleaned, deduplicated data:

```sql
SELECT
    id,
    customer_id,
    amount / 100.0 as amount_usd,
    status,
    created
FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
ORDER BY created DESC;
```

**Characteristics**: Deduplicated, standardized column names, no business logic.

### Marts Data (Analytics-Ready)

Query business-ready tables:

```sql
SELECT
    customer_id,
    email,
    lifetime_value,
    lifetime_orders
FROM marts.customer_metrics
WHERE lifetime_value > 1000
ORDER BY lifetime_value DESC;
```

**Best practice**: Always prefer marts for dashboards—faster and more meaningful.

---

## DuckDB SQL Essentials

### Date Functions

Essential for time-series analysis:

```sql
-- Current date/time
SELECT CURRENT_DATE                    -- 2024-12-09
SELECT CURRENT_TIMESTAMP               -- 2024-12-09 14:30:00

-- Date truncation (for grouping)
SELECT DATE_TRUNC('month', created) as month

-- Date arithmetic
SELECT CURRENT_DATE - INTERVAL 7 DAY   -- 7 days ago
SELECT CURRENT_DATE - INTERVAL 1 MONTH -- 1 month ago

-- Extract parts
SELECT EXTRACT(YEAR FROM created) as year
SELECT EXTRACT(MONTH FROM created) as month
```

### Common Patterns

**Monthly aggregation**:

```sql
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_ltv
FROM marts.customer_metrics
GROUP BY month
ORDER BY month DESC
```

**Date filtering**:

```sql
SELECT *
FROM marts.customer_metrics
WHERE created >= CURRENT_DATE - INTERVAL 30 DAY
  AND created < CURRENT_DATE
```

### Stripe Amount Conversion

Stripe stores amounts in cents:

```sql
SELECT
    id,
    amount / 100.0 as amount_usd
FROM raw_stripe.charges
```

### Type Casting

```sql
-- String to integer
SELECT '123'::INTEGER

-- String to date
SELECT DATE '2024-12-09'
```

---

## Query Variables (Filters)

Make queries interactive with Metabase variables:

### Basic Variable

```sql
SELECT *
FROM marts.customer_metrics
WHERE email = {{email_address}}
```

### Date Range

```sql
SELECT *
FROM marts.customer_metrics
WHERE created >= {{start_date}}
  AND created < {{end_date}}
```

### Optional Filters

Use `[[double brackets]]` for optional clauses:

```sql
SELECT *
FROM marts.customer_metrics
WHERE 1=1
  [[AND region = {{region}}]]
  [[AND created >= {{start_date}}]]
ORDER BY lifetime_value DESC
```

If variable is empty, clause is omitted.

!!! info "Query Variables Reference"
    For detailed variable configuration, see [Metabase SQL Parameters](https://www.metabase.com/docs/latest/questions/native-editor/sql-parameters).

---

## Common Analytics Queries

### Monthly Revenue Trend

```sql
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(DISTINCT customer_id) as customers,
    SUM(amount / 100.0) as revenue
FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
GROUP BY month
ORDER BY month;
```

### Top Customers

```sql
SELECT
    customer_id,
    email,
    lifetime_value,
    lifetime_orders
FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10;
```

### Period Comparison

```sql
SELECT
    'This Month' as period,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_ltv
FROM marts.customer_metrics
WHERE created >= DATE_TRUNC('month', CURRENT_DATE)

UNION ALL

SELECT
    'Last Month' as period,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_ltv
FROM marts.customer_metrics
WHERE created >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL 1 MONTH)
  AND created < DATE_TRUNC('month', CURRENT_DATE);
```

### Year-over-Year Growth

```sql
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', created) as month,
        SUM(amount / 100.0) as revenue
    FROM staging.stg_stripe_charges
    WHERE status = 'succeeded'
    GROUP BY month
)

SELECT
    month,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY month) as revenue_last_year,
    (revenue - LAG(revenue, 12) OVER (ORDER BY month)) /
        LAG(revenue, 12) OVER (ORDER BY month) * 100 as yoy_growth_pct
FROM monthly_revenue
ORDER BY month DESC;
```

---

## Query Optimization

### Use Marts Instead of Raw

```sql
-- Bad: Aggregating raw data every time
SELECT DATE_TRUNC('month', created) as month, SUM(amount) as revenue
FROM raw_stripe.charges
GROUP BY month;

-- Good: Query pre-aggregated mart
SELECT month, total_revenue
FROM marts.revenue_by_month;
```

**Rule**: Create a dbt mart for repeated aggregations.

### Limit Result Sets

```sql
-- Always use LIMIT for exploration
SELECT * FROM staging.stg_stripe_charges LIMIT 100;
```

### Filter Early in Joins

```sql
-- Good: Filter before join
SELECT c.*, o.*
FROM staging.stg_customers c
JOIN (
    SELECT * FROM staging.stg_orders
    WHERE created >= CURRENT_DATE - INTERVAL 30 DAY
) o ON c.id = o.customer_id;
```

---

## Troubleshooting

### Table Not Found

```
Error: Table "revenue_by_month" not found
```

**Solution**: Add schema prefix:
```sql
SELECT * FROM marts.revenue_by_month
```

### Column Not Found

**Solution**: Check spelling with `DESCRIBE`:
```sql
DESCRIBE marts.customer_metrics;
```

### Type Mismatch

```
Error: Cannot compare INTEGER with VARCHAR
```

**Solution**: Cast to matching type:
```sql
WHERE customer_id = 123           -- Not '123'
WHERE customer_id = '123'::INTEGER
```

### Division by Zero

```sql
SELECT
    revenue,
    CASE WHEN order_count > 0 THEN revenue / order_count ELSE 0 END as avg_order_value
FROM marts.revenue_by_month;
```

---

## Best Practices

1. **Always qualify table names**: `marts.customer_metrics` not `customer_metrics`
2. **Use meaningful aliases**: `c` for customers, `o` for orders, not `a`, `b`
3. **Handle NULLs explicitly**: `COALESCE(region, 'Unknown')`
4. **Comment complex logic**: Explain business rules in SQL comments
5. **Format for readability**: One clause per line, consistent indentation

---

## Next Steps

<div class="grid cards" markdown>

-   :material-plus-box: **Creating Dashboards**

    ---

    Build interactive dashboards using your SQL queries.

    [:octicons-arrow-right-24: Creating Dashboards](creating-dashboards.md)

-   :material-table-sync: **Transformations**

    ---

    Create marts tables with dbt for better query performance.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **DuckDB Documentation**

    ---

    Complete SQL reference: window functions, JSON, regex, arrays.

    [:octicons-arrow-right-24: DuckDB Docs](https://duckdb.org/docs/sql/introduction)

-   :material-book-open-outline: **Metabase SQL Guide**

    ---

    SQL editor features, variables, and native queries.

    [:octicons-arrow-right-24: Metabase Docs](https://www.metabase.com/docs/latest/questions/native-editor/writing-sql)

</div>
