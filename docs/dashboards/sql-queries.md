# SQL Queries

Writing SQL queries in Metabase with DuckDB syntax and best practices.

---

## Overview

Metabase's SQL editor provides direct access to your DuckDB warehouse. This guide covers DuckDB SQL syntax, how to query Dango's data layers, and common query patterns for analytics.

**What you'll learn**:

- DuckDB SQL syntax essentials
- Accessing raw, staging, and marts schemas
- Query variables for interactive filters
- Common analytics patterns
- Query optimization tips
- Troubleshooting SQL errors

---

## Quick Start

### Open SQL Editor

1. Navigate to http://localhost:3000
2. Click **"+ New"** → **"SQL query"**
3. Select **"DuckDB"** database
4. Write SQL in the editor
5. Click **"Get Answer"** to execute

### Your First Query

```sql
-- View all marts tables
SHOW TABLES FROM marts;
```

**Result**: List of all tables in the marts schema

```sql
-- Query a marts table
SELECT *
FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10;
```

**Result**: Top 10 customers by lifetime value

---

## DuckDB SQL Basics

### Schema-Qualified Names

Always use schema prefix:

```sql
-- Correct: Schema.table
SELECT * FROM marts.revenue_by_month

-- Also works: Database.schema.table
SELECT * FROM duckdb.marts.revenue_by_month

-- Avoid: Unqualified (may fail or be ambiguous)
SELECT * FROM revenue_by_month
```

### Available Schemas in Dango

| Schema | Purpose | Example Tables |
|--------|---------|----------------|
| `raw` | Single-table sources from dlt | `raw.csv_uploads` |
| `raw_*` | Multi-table sources | `raw_stripe.charges`, `raw_stripe.customers` |
| `staging` | Auto-generated staging models | `staging.stg_stripe_charges` |
| `intermediate` | Custom business logic | `intermediate.int_customer_orders` |
| `marts` | Analytics-ready tables | `marts.customer_metrics`, `marts.revenue_by_month` |

### List All Tables

```sql
-- All tables across all schemas
SHOW TABLES;

-- Tables in specific schema
SHOW TABLES FROM marts;

-- With schema prefix
SELECT * FROM information_schema.tables
WHERE table_schema = 'marts';
```

### Describe Table Structure

```sql
-- Show columns and types
DESCRIBE marts.customer_metrics;

-- Alternative
PRAGMA table_info('marts.customer_metrics');

-- Full metadata
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'marts'
  AND table_name = 'customer_metrics';
```

---

## DuckDB SQL Syntax

### Data Types

Common types in Dango:

| Type | Description | Example |
|------|-------------|---------|
| `INTEGER` | Whole numbers | `42` |
| `DOUBLE` | Decimals | `3.14` |
| `VARCHAR` | Text | `'hello'` |
| `DATE` | Dates | `DATE '2024-12-09'` |
| `TIMESTAMP` | Date + time | `TIMESTAMP '2024-12-09 14:30:00'` |
| `BOOLEAN` | True/false | `true` |
| `JSON` | JSON objects | `'{"key": "value"}'::JSON` |

### Casting

Convert between types:

```sql
-- String to integer
SELECT CAST('123' AS INTEGER)
SELECT '123'::INTEGER  -- DuckDB shorthand

-- Integer to string
SELECT CAST(123 AS VARCHAR)

-- String to date
SELECT CAST('2024-12-09' AS DATE)
SELECT DATE '2024-12-09'  -- Literal syntax

-- Handle Stripe amounts (cents to dollars)
SELECT
    id,
    amount / 100.0 as amount_usd,
    CAST(amount AS DOUBLE) / 100.0 as amount_usd_explicit
FROM raw_stripe.charges
```

### Date Functions

Essential for time-series analysis:

#### Current Date/Time

```sql
SELECT CURRENT_DATE                 -- 2024-12-09
SELECT CURRENT_TIMESTAMP            -- 2024-12-09 14:30:00.123
SELECT NOW()                        -- Same as CURRENT_TIMESTAMP
```

#### Date Truncation

```sql
-- Truncate to period
SELECT DATE_TRUNC('day', created) as day
SELECT DATE_TRUNC('week', created) as week
SELECT DATE_TRUNC('month', created) as month
SELECT DATE_TRUNC('year', created) as year

-- Example: Monthly aggregation
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as customer_count
FROM marts.customer_metrics
GROUP BY month
ORDER BY month DESC
```

#### Date Arithmetic

```sql
-- Add/subtract intervals
SELECT CURRENT_DATE - INTERVAL 7 DAY        -- 7 days ago
SELECT CURRENT_DATE - INTERVAL 1 MONTH      -- 1 month ago
SELECT CURRENT_DATE + INTERVAL 1 YEAR       -- 1 year from now

-- Date filters
SELECT *
FROM marts.customer_metrics
WHERE created >= CURRENT_DATE - INTERVAL 30 DAY
  AND created < CURRENT_DATE
```

#### Date Parts

```sql
-- Extract parts
SELECT EXTRACT(YEAR FROM created) as year
SELECT EXTRACT(MONTH FROM created) as month
SELECT EXTRACT(DAY FROM created) as day
SELECT EXTRACT(QUARTER FROM created) as quarter
SELECT EXTRACT(DOW FROM created) as day_of_week  -- 0=Sunday, 6=Saturday

-- Example: Group by day of week
SELECT
    EXTRACT(DOW FROM created) as day_of_week,
    CASE EXTRACT(DOW FROM created)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(*) as orders
FROM marts.customer_metrics
GROUP BY day_of_week, day_name
ORDER BY day_of_week
```

### String Functions

```sql
-- Concatenation
SELECT first_name || ' ' || last_name as full_name

-- Case conversion
SELECT UPPER(email), LOWER(email)

-- Substring
SELECT SUBSTRING(email, 1, 10)  -- First 10 chars

-- Pattern matching
SELECT * FROM staging.stg_stripe_customers
WHERE email LIKE '%@gmail.com'

-- Regular expressions
SELECT * FROM staging.stg_stripe_customers
WHERE REGEXP_MATCHES(email, '^[a-z]+@gmail\.com$')

-- Replace
SELECT REPLACE(phone, '-', '') as phone_clean

-- Trim whitespace
SELECT TRIM(name), LTRIM(name), RTRIM(name)
```

### Aggregation Functions

```sql
-- Basic aggregations
SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(amount) as total_amount,
    AVG(amount) as avg_amount,
    MIN(amount) as min_amount,
    MAX(amount) as max_amount
FROM raw_stripe.charges

-- With filtering
SELECT
    COUNT(*) FILTER (WHERE status = 'succeeded') as successful_count,
    SUM(amount) FILTER (WHERE status = 'succeeded') as successful_amount
FROM raw_stripe.charges

-- Percentiles
SELECT
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) as median,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) as p25,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY amount) as p75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY amount) as p95
FROM raw_stripe.charges
```

### Window Functions

Powerful for rankings and running calculations:

#### Row Numbers and Rankings

```sql
-- Row number
SELECT
    customer_id,
    email,
    lifetime_value,
    ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) as rank
FROM marts.customer_metrics

-- Rank (with ties)
SELECT
    customer_id,
    lifetime_value,
    RANK() OVER (ORDER BY lifetime_value DESC) as rank,
    DENSE_RANK() OVER (ORDER BY lifetime_value DESC) as dense_rank
FROM marts.customer_metrics
```

#### Partition By

```sql
-- Rank within groups
SELECT
    region,
    customer_id,
    lifetime_value,
    RANK() OVER (
        PARTITION BY region
        ORDER BY lifetime_value DESC
    ) as rank_in_region
FROM marts.customer_metrics

-- Top customer per region
SELECT * FROM (
    SELECT
        region,
        customer_id,
        lifetime_value,
        ROW_NUMBER() OVER (
            PARTITION BY region
            ORDER BY lifetime_value DESC
        ) as rn
    FROM marts.customer_metrics
)
WHERE rn = 1
```

#### Running Totals

```sql
-- Cumulative sum
SELECT
    month,
    revenue,
    SUM(revenue) OVER (
        ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as cumulative_revenue
FROM marts.revenue_by_month
ORDER BY month

-- Moving average
SELECT
    day,
    sales,
    AVG(sales) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7day
FROM daily_sales
```

---

## Querying Dango Data Layers

### Raw Data (dlt Source)

Query unprocessed data from dlt:

```sql
-- Single-table source (e.g., CSV)
SELECT * FROM raw.customer_uploads
LIMIT 100;

-- Multi-table source (e.g., Stripe)
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

**Use cases**:
- Debugging source data issues
- Auditing data lineage
- Comparing raw vs. transformed data

### Staging Data (Auto-Generated)

Query cleaned, deduplicated data:

```sql
-- Generated staging model
SELECT
    id,
    customer_id,
    amount / 100.0 as amount_usd,
    status,
    created
FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
  AND created >= CURRENT_DATE - INTERVAL 90 DAY
ORDER BY created DESC;
```

**Characteristics**:
- Deduplicated (latest record per ID)
- Column naming standardized
- No business logic (just cleaning)

**When to use**:
- Building custom analytics
- Joining multiple source tables
- Exploring cleaned data

### Marts Data (Analytics-Ready)

Query business-ready tables:

```sql
-- Pre-aggregated metrics
SELECT
    month,
    customer_count,
    revenue_usd,
    avg_order_value
FROM marts.monthly_metrics
ORDER BY month DESC
LIMIT 12;

-- Customer lifetime value
SELECT
    customer_id,
    email,
    lifetime_value,
    lifetime_orders,
    first_order_date,
    last_order_date
FROM marts.customer_metrics
WHERE lifetime_value > 1000
ORDER BY lifetime_value DESC;
```

**Best practice**: Always prefer marts for dashboards (faster, more meaningful).

---

## Query Variables (Filters)

Make queries interactive with user inputs:

### Text Variable

```sql
SELECT *
FROM marts.customer_metrics
WHERE email = {{email_address}}
```

**Variable setup**:
- Type: Text
- Default: `user@example.com`
- Label: "Customer Email"

### Number Variable

```sql
SELECT *
FROM marts.customer_metrics
WHERE lifetime_value > {{min_ltv}}
ORDER BY lifetime_value DESC
```

**Variable setup**:
- Type: Number
- Default: `100`
- Label: "Minimum LTV"

### Date Variable

```sql
SELECT *
FROM marts.customer_metrics
WHERE created >= {{start_date}}
  AND created < {{end_date}}
```

**Variable setup**:
- Type: Date
- Default: `2024-01-01` and `2024-12-31`
- Label: "Start Date" and "End Date"

### Optional Filters

Use `[[double brackets]]` for optional clauses:

```sql
SELECT
    customer_id,
    email,
    lifetime_value
FROM marts.customer_metrics
WHERE 1=1
  [[AND region = {{region}}]]
  [[AND created >= {{start_date}}]]
ORDER BY lifetime_value DESC
```

**Behavior**:
- If variable is empty/null, clause is omitted
- If variable has value, clause is included

### Dropdown Variable

```sql
SELECT *
FROM marts.customer_metrics
WHERE status = {{status}}
```

**Variable setup**:
- Type: Field Filter
- Field: `customer_metrics.status`
- Widget: Dropdown
- Shows distinct values from column

---

## Common Query Patterns

### Time-Series Analysis

#### Daily/Monthly Trends

```sql
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(DISTINCT customer_id) as new_customers,
    SUM(amount / 100.0) as revenue
FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
GROUP BY month
ORDER BY month;
```

#### Year-over-Year Growth

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
    (revenue - LAG(revenue, 12) OVER (ORDER BY month)) / LAG(revenue, 12) OVER (ORDER BY month) * 100 as yoy_growth_pct
FROM monthly_revenue
ORDER BY month DESC;
```

#### Period Comparisons

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
  AND created < DATE_TRUNC('month', CURRENT_DATE)

UNION ALL

SELECT
    'This Year' as period,
    COUNT(*) as customers,
    SUM(lifetime_value) as total_ltv
FROM marts.customer_metrics
WHERE created >= DATE_TRUNC('year', CURRENT_DATE);
```

### Cohort Analysis

#### Monthly Cohorts

```sql
WITH cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', MIN(created)) as cohort_month
    FROM staging.stg_stripe_charges
    WHERE status = 'succeeded'
    GROUP BY customer_id
),

cohort_metrics AS (
    SELECT
        c.cohort_month,
        COUNT(DISTINCT c.customer_id) as cohort_size,
        SUM(ch.amount / 100.0) as total_revenue
    FROM cohorts c
    JOIN staging.stg_stripe_charges ch
        ON c.customer_id = ch.customer_id
    WHERE ch.status = 'succeeded'
    GROUP BY c.cohort_month
)

SELECT
    cohort_month,
    cohort_size,
    total_revenue,
    total_revenue / cohort_size as avg_revenue_per_customer
FROM cohort_metrics
ORDER BY cohort_month DESC;
```

### Customer Segmentation

#### RFM Segmentation

```sql
WITH customer_rfm AS (
    SELECT
        customer_id,
        MAX(created) as last_purchase,
        COUNT(*) as frequency,
        SUM(amount / 100.0) as monetary
    FROM staging.stg_stripe_charges
    WHERE status = 'succeeded'
    GROUP BY customer_id
),

rfm_scores AS (
    SELECT
        customer_id,
        last_purchase,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY last_purchase DESC) as recency_score,
        NTILE(5) OVER (ORDER BY frequency) as frequency_score,
        NTILE(5) OVER (ORDER BY monetary) as monetary_score
    FROM customer_rfm
)

SELECT
    customer_id,
    last_purchase,
    frequency,
    monetary,
    recency_score,
    frequency_score,
    monetary_score,
    CASE
        WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
        WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal Customers'
        WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'Recent Customers'
        WHEN recency_score <= 2 AND frequency_score >= 4 THEN 'At Risk'
        ELSE 'Other'
    END as segment
FROM rfm_scores
ORDER BY monetary DESC;
```

### Funnel Analysis

```sql
WITH funnel AS (
    SELECT
        COUNT(DISTINCT visitor_id) as visitors,
        COUNT(DISTINCT CASE WHEN signed_up THEN visitor_id END) as signups,
        COUNT(DISTINCT CASE WHEN made_purchase THEN visitor_id END) as customers
    FROM marts.user_journey
)

SELECT
    visitors,
    signups,
    customers,
    ROUND(signups::DOUBLE / visitors * 100, 1) as signup_rate,
    ROUND(customers::DOUBLE / signups * 100, 1) as conversion_rate,
    ROUND(customers::DOUBLE / visitors * 100, 1) as overall_rate
FROM funnel;
```

### Top N with Others

```sql
WITH ranked_products AS (
    SELECT
        product,
        SUM(amount / 100.0) as revenue,
        RANK() OVER (ORDER BY SUM(amount / 100.0) DESC) as rank
    FROM staging.stg_stripe_charges
    WHERE status = 'succeeded'
    GROUP BY product
)

SELECT
    CASE WHEN rank <= 10 THEN product ELSE 'Other' END as product_group,
    SUM(revenue) as total_revenue
FROM ranked_products
GROUP BY product_group
ORDER BY total_revenue DESC;
```

---

## Query Optimization

### Use Appropriate Schemas

```sql
-- Bad: Aggregating raw data every time
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as orders,
    SUM(amount) as revenue
FROM raw_stripe.charges
WHERE status = 'succeeded'
GROUP BY month;

-- Good: Query pre-aggregated mart
SELECT
    month,
    order_count,
    total_revenue
FROM marts.revenue_by_month;
```

**Rule**: Create mart in dbt for repeated aggregations.

### Limit Result Sets

```sql
-- Always use LIMIT for exploration
SELECT * FROM staging.stg_stripe_charges
LIMIT 100;

-- Use TOP N patterns
SELECT *
FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 50;
```

### Filter Early

```sql
-- Bad: Filter after joins
SELECT c.*, o.*
FROM staging.stg_customers c
JOIN staging.stg_orders o ON c.id = o.customer_id
WHERE o.created >= CURRENT_DATE - INTERVAL 30 DAY;

-- Good: Filter before joins
SELECT c.*, o.*
FROM staging.stg_customers c
JOIN (
    SELECT *
    FROM staging.stg_orders
    WHERE created >= CURRENT_DATE - INTERVAL 30 DAY
) o ON c.id = o.customer_id;
```

### Use CTEs for Readability

```sql
-- Complex logic broken into steps
WITH active_customers AS (
    SELECT customer_id
    FROM staging.stg_stripe_charges
    WHERE created >= CURRENT_DATE - INTERVAL 90 DAY
    GROUP BY customer_id
),

customer_metrics AS (
    SELECT
        c.customer_id,
        c.email,
        COUNT(o.id) as order_count,
        SUM(o.amount / 100.0) as total_spent
    FROM staging.stg_customers c
    JOIN staging.stg_orders o ON c.id = o.customer_id
    WHERE c.id IN (SELECT customer_id FROM active_customers)
    GROUP BY c.customer_id, c.email
)

SELECT *
FROM customer_metrics
ORDER BY total_spent DESC;
```

---

## Troubleshooting

### Common Errors

#### Table Not Found

```
Error: Table "revenue_by_month" not found
```

**Solution**: Add schema prefix:
```sql
SELECT * FROM marts.revenue_by_month
```

#### Column Not Found

```
Error: Column "custmer_id" not found
```

**Solution**: Check spelling, use `DESCRIBE` to see columns:
```sql
DESCRIBE marts.customer_metrics;
```

#### Type Mismatch

```
Error: Cannot compare INTEGER with VARCHAR
```

**Solution**: Cast to matching type:
```sql
-- Wrong
WHERE customer_id = '123'

-- Right
WHERE customer_id = 123
-- OR
WHERE customer_id = CAST('123' AS INTEGER)
```

#### Division by Zero

```sql
-- Protect against division by zero
SELECT
    revenue,
    CASE
        WHEN order_count > 0 THEN revenue / order_count
        ELSE 0
    END as avg_order_value
FROM marts.revenue_by_month;
```

### Debugging Queries

#### View Query Execution Plan

```sql
EXPLAIN SELECT * FROM marts.customer_metrics
WHERE lifetime_value > 1000;
```

#### Check Row Counts

```sql
-- Verify data exists
SELECT COUNT(*) FROM marts.revenue_by_month;

-- Check date ranges
SELECT MIN(month), MAX(month) FROM marts.revenue_by_month;
```

#### Sample Data

```sql
-- Random sample
SELECT * FROM marts.customer_metrics
USING SAMPLE 100 ROWS;

-- Stratified sample
SELECT * FROM marts.customer_metrics
USING SAMPLE 10 PERCENT;
```

---

## Advanced DuckDB Features

### JSON Queries

If source data includes JSON:

```sql
-- Extract JSON field
SELECT
    id,
    metadata->>'plan' as plan_name,
    CAST(metadata->>'price' AS INTEGER) as price
FROM staging.stg_stripe_subscriptions
WHERE metadata IS NOT NULL;

-- Array aggregation to JSON
SELECT
    customer_id,
    LIST(order_id) as order_ids,
    TO_JSON(LIST(order_id)) as order_ids_json
FROM staging.stg_orders
GROUP BY customer_id;
```

### Regular Expressions

```sql
-- Pattern matching
SELECT email
FROM staging.stg_customers
WHERE REGEXP_MATCHES(email, '^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$');

-- Extract patterns
SELECT
    email,
    REGEXP_EXTRACT(email, '@(.+)$', 1) as domain
FROM staging.stg_customers;
```

### Arrays and Lists

```sql
-- Create array
SELECT LIST(product_id) as products
FROM staging.stg_orders
WHERE customer_id = 123;

-- Array aggregation
SELECT
    customer_id,
    LIST(DISTINCT product_id) as purchased_products,
    LEN(LIST(DISTINCT product_id)) as unique_product_count
FROM staging.stg_orders
GROUP BY customer_id;
```

---

## Best Practices

### 1. Always Qualify Table Names

```sql
-- Good
SELECT * FROM marts.customer_metrics

-- Avoid
SELECT * FROM customer_metrics
```

### 2. Use Meaningful Aliases

```sql
-- Good
SELECT
    c.customer_id,
    c.email,
    o.order_count
FROM marts.customer_metrics c
JOIN marts.order_summary o ON c.customer_id = o.customer_id

-- Avoid
SELECT
    a.customer_id,
    a.email,
    b.order_count
FROM marts.customer_metrics a
JOIN marts.order_summary b ON a.customer_id = b.customer_id
```

### 3. Comment Complex Logic

```sql
-- Calculate customer lifetime value with 3-month active window
-- Excludes refunds and failed payments
SELECT
    customer_id,
    SUM(amount / 100.0) as lifetime_value
FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
  AND created >= CURRENT_DATE - INTERVAL 90 DAY
GROUP BY customer_id;
```

### 4. Handle NULLs Explicitly

```sql
SELECT
    customer_id,
    COALESCE(region, 'Unknown') as region,
    COALESCE(lifetime_value, 0) as lifetime_value
FROM marts.customer_metrics;
```

### 5. Format for Readability

```sql
-- Good formatting
SELECT
    customer_id,
    email,
    lifetime_value,
    lifetime_orders
FROM marts.customer_metrics
WHERE lifetime_value > 1000
  AND created >= CURRENT_DATE - INTERVAL 1 YEAR
ORDER BY lifetime_value DESC
LIMIT 100;
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-plus-box: **Creating Dashboards**

    ---

    Build interactive dashboards using your SQL queries.

    [:octicons-arrow-right-24: Creating Dashboards](creating-dashboards.md)

-   :material-chart-box-outline: **Metabase Overview**

    ---

    Learn about Metabase features and configuration.

    [:octicons-arrow-right-24: Metabase Overview](metabase-overview.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Create marts tables with dbt for better query performance.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **DuckDB Documentation**

    ---

    Explore official DuckDB SQL reference.

    [:octicons-arrow-right-24: DuckDB Docs](https://duckdb.org/docs/sql/introduction)

</div>
