# Custom Models

Build intermediate layers and data marts for analytics.

---

## Overview

Custom models are where you implement business logic, create reusable transformations, and build final analytics tables. Unlike staging models (which are auto-generated templates), custom models are written by you.

**Two Types**:

1. **Intermediate Models** - Reusable business logic and joins
2. **Marts Models** - Final tables optimized for BI and reporting

**Key Features**:

- Full SQL and dbt functionality
- Version controlled with Git
- Tested and documented
- **Materialized as tables** (required for Metabase compatibility)
- Build on top of staging models

**Creating Custom Models**:

Use `dango model add` to create new models via an interactive wizard:

```bash
dango model add
# Select "intermediate" or "marts"
# Enter model name
# Add optional description
```

This creates a template file you can edit with your SQL logic.

---

## Quick Start

### Create Your First Mart

**Step 1: Create the model file**

```bash
dango model add
# Select "marts"
# Enter name: customer_metrics
# Add description (optional)
```

**Step 2: Edit the generated template**

Open `dbt/models/marts/customer_metrics.sql` and replace with your SQL:

```sql
-- dbt/models/marts/customer_metrics.sql
{{ config(materialized='table') }}

WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) as order_count,
        SUM(amount / 100.0) as total_spent,
        MIN(created) as first_order_date,
        MAX(created) as last_order_date
    FROM {{ ref('stg_stripe_charges') }}
    WHERE status = 'succeeded'
    GROUP BY customer_id
),

customers AS (
    SELECT
        id,
        email,
        created as customer_since
    FROM {{ ref('stg_stripe_customers') }}
)

SELECT
    c.id as customer_id,
    c.email,
    c.customer_since,
    COALESCE(co.order_count, 0) as lifetime_orders,
    COALESCE(co.total_spent, 0) as lifetime_value,
    co.first_order_date,
    co.last_order_date,
    DATEDIFF('day', co.first_order_date, co.last_order_date) as customer_lifespan_days
FROM customers c
LEFT JOIN customer_orders co ON c.id = co.customer_id
```

**Step 3: Run the model**

```bash
dango run
```

Query in Metabase or DuckDB:

```sql
SELECT * FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10;
```

---

## Project Structure

### Directory Layout

```
dbt/models/
├── staging/              # Auto-generated (don't modify)
│   └── stg_*.sql
├── intermediate/         # Your reusable logic
│   ├── int_customer_orders.sql
│   ├── int_product_performance.sql
│   └── schema.yml
└── marts/               # Your final analytics tables
    ├── finance/
    │   ├── revenue_by_month.sql
    │   ├── mrr_analysis.sql
    │   └── schema.yml
    ├── marketing/
    │   ├── campaign_performance.sql
    │   ├── customer_acquisition.sql
    │   └── schema.yml
    └── operations/
        ├── fulfillment_metrics.sql
        └── schema.yml
```

### Naming Conventions

| Layer | Prefix | Example | Materialization |
|-------|--------|---------|-----------------|
| Staging | `stg_` | `stg_stripe_charges` | table |
| Intermediate | `int_` | `int_customer_orders` | table |
| Marts | (any) | `customer_metrics`, `revenue_by_month` | table |

!!! note "Materialization"
    All models use `table` materialization in Dango for Metabase compatibility.
    The `int_` prefix is auto-added when you create intermediate models via `dango model add`.

---

## Intermediate Models

### Purpose

Intermediate models encapsulate reusable business logic that:

- Joins multiple staging tables
- Applies business rules consistently
- Creates reusable building blocks
- Reduces code duplication

**Materialization**: `table` (required for Metabase compatibility)

**Creating intermediate models**:

```bash
dango model add
# Select "intermediate"
# The name will be auto-prefixed with "int_"
```

### Example: Customer Orders

```sql
-- dbt/models/intermediate/int_customer_orders.sql
{{ config(
    materialized='table',
    schema='intermediate'
) }}

WITH customers AS (
    SELECT
        id,
        email,
        created as customer_since
    FROM {{ ref('stg_stripe_customers') }}
),

charges AS (
    SELECT
        id as charge_id,
        customer,
        amount / 100.0 as amount_usd,
        currency,
        status,
        created as charge_date
    FROM {{ ref('stg_stripe_charges') }}
    WHERE status = 'succeeded'
),

joined AS (
    SELECT
        c.id as customer_id,
        c.email,
        c.customer_since,
        ch.charge_id,
        ch.amount_usd,
        ch.currency,
        ch.charge_date
    FROM customers c
    INNER JOIN charges ch ON c.id = ch.customer
)

SELECT * FROM joined
```

### Example: Product Performance

```sql
-- dbt/models/intermediate/int_product_performance.sql
{{ config(materialized='table', schema='intermediate') }}

WITH products AS (
    SELECT
        id as product_id,
        name,
        category,
        price / 100.0 as price_usd
    FROM {{ ref('stg_shopify_products') }}
),

order_items AS (
    SELECT
        product_id,
        quantity,
        price / 100.0 as item_price_usd,
        order_date
    FROM {{ ref('stg_shopify_order_items') }}
),

aggregated AS (
    SELECT
        oi.product_id,
        p.name,
        p.category,
        p.price_usd,
        COUNT(DISTINCT oi.order_date) as days_with_sales,
        SUM(oi.quantity) as total_units_sold,
        SUM(oi.item_price_usd) as total_revenue
    FROM order_items oi
    INNER JOIN products p ON oi.product_id = p.product_id
    GROUP BY 1, 2, 3, 4
)

SELECT
    *,
    total_revenue / NULLIF(total_units_sold, 0) as avg_sale_price
FROM aggregated
```

### When to Use Intermediate

Use intermediate models when:

- ✅ Logic is reused in multiple marts
- ✅ Complex joins need to be standardized
- ✅ Business rules apply across domains
- ✅ You want to simplify downstream models

Don't use intermediate when:

- ❌ Logic is only used once (put it in the mart)
- ❌ Model is simple enough for a CTE
- ❌ Performance requires materialization (use mart instead)

---

## Marts Models

### Purpose

Marts are the final analytics tables designed for:

- Business intelligence tools (Metabase, Tableau, etc.)
- SQL queries by analysts
- Reporting and dashboards
- Data exports

**Materialization**: `table` (required for Metabase compatibility)

**Creating marts models**:

```bash
dango model add
# Select "marts"
# Enter the model name
```

### Fact Tables

**Fact tables** store measurable events or transactions.

```sql
-- dbt/models/marts/finance/fct_revenue.sql
{{ config(
    materialized='table',
    schema='marts'
) }}

WITH daily_revenue AS (
    SELECT
        DATE_TRUNC('day', charge_date) as date,
        currency,
        COUNT(*) as transaction_count,
        SUM(amount_usd) as revenue_usd,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM {{ ref('int_customer_orders') }}
    GROUP BY 1, 2
)

SELECT
    date,
    currency,
    transaction_count,
    revenue_usd,
    unique_customers,
    revenue_usd / NULLIF(transaction_count, 0) as avg_transaction_value
FROM daily_revenue
ORDER BY date DESC
```

### Dimension Tables

**Dimension tables** store attributes about entities.

```sql
-- dbt/models/marts/operations/dim_customers.sql
{{ config(
    materialized='table',
    schema='marts'
) }}

WITH customer_base AS (
    SELECT
        customer_id,
        email,
        customer_since,
        lifetime_orders,
        lifetime_value,
        first_order_date,
        last_order_date
    FROM {{ ref('int_customer_orders') }}
),

customer_segments AS (
    SELECT
        *,
        CASE
            WHEN lifetime_value >= 10000 THEN 'vip'
            WHEN lifetime_value >= 1000 THEN 'high_value'
            WHEN lifetime_value >= 100 THEN 'medium_value'
            ELSE 'low_value'
        END as customer_segment,

        CASE
            WHEN lifetime_orders = 1 THEN 'one_time'
            WHEN lifetime_orders <= 5 THEN 'occasional'
            WHEN lifetime_orders <= 20 THEN 'regular'
            ELSE 'power_user'
        END as customer_type
    FROM customer_base
)

SELECT * FROM customer_segments
```

### Aggregate Tables

**Aggregate tables** pre-compute metrics for performance.

```sql
-- dbt/models/marts/marketing/monthly_cohort_retention.sql
{{ config(materialized='table') }}

WITH customer_cohorts AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', customer_since) as cohort_month,
        DATE_TRUNC('month', charge_date) as activity_month
    FROM {{ ref('int_customer_orders') }}
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) as cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
),

cohort_activity AS (
    SELECT
        c.cohort_month,
        c.activity_month,
        COUNT(DISTINCT c.customer_id) as active_customers
    FROM customer_cohorts c
    GROUP BY 1, 2
)

SELECT
    ca.cohort_month,
    ca.activity_month,
    cs.cohort_size,
    ca.active_customers,
    ca.active_customers::FLOAT / cs.cohort_size as retention_rate,
    DATEDIFF('month', ca.cohort_month, ca.activity_month) as months_since_cohort
FROM cohort_activity ca
INNER JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
ORDER BY ca.cohort_month, ca.activity_month
```

---

## Common Patterns

### Time Series Analysis

```sql
-- dbt/models/marts/finance/revenue_by_month.sql
{{ config(materialized='table') }}

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', charge_date) as month,
        SUM(amount_usd) as revenue,
        COUNT(DISTINCT customer_id) as customers,
        COUNT(*) as transactions
    FROM {{ ref('int_customer_orders') }}
    GROUP BY 1
),

with_previous AS (
    SELECT
        month,
        revenue,
        customers,
        transactions,
        LAG(revenue) OVER (ORDER BY month) as prev_month_revenue
    FROM monthly_revenue
)

SELECT
    month,
    revenue,
    customers,
    transactions,
    prev_month_revenue,
    revenue - prev_month_revenue as revenue_change,
    (revenue - prev_month_revenue) / NULLIF(prev_month_revenue, 0) * 100 as revenue_growth_pct
FROM with_previous
ORDER BY month DESC
```

### Funnel Analysis

```sql
-- dbt/models/marts/marketing/conversion_funnel.sql
{{ config(materialized='table') }}

WITH funnel_events AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as viewed,
        MAX(CASE WHEN event_type = 'signup' THEN 1 ELSE 0 END) as signed_up,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchased
    FROM {{ ref('stg_analytics_events') }}
    WHERE event_date >= CURRENT_DATE - INTERVAL 30 DAY
    GROUP BY user_id
)

SELECT
    COUNT(*) as total_users,
    SUM(viewed) as step_1_viewed,
    SUM(signed_up) as step_2_signed_up,
    SUM(purchased) as step_3_purchased,
    SUM(signed_up)::FLOAT / NULLIF(SUM(viewed), 0) * 100 as conversion_rate_1_to_2,
    SUM(purchased)::FLOAT / NULLIF(SUM(signed_up), 0) * 100 as conversion_rate_2_to_3,
    SUM(purchased)::FLOAT / NULLIF(SUM(viewed), 0) * 100 as overall_conversion_rate
FROM funnel_events
```

### Slowly Changing Dimensions (SCD Type 2)

```sql
-- dbt/models/marts/operations/dim_products_scd.sql
{{ config(materialized='table') }}

WITH product_changes AS (
    SELECT
        id,
        name,
        price,
        _dlt_extracted_at as valid_from,
        LEAD(_dlt_extracted_at) OVER (PARTITION BY id ORDER BY _dlt_extracted_at) as valid_to,
        CASE
            WHEN LEAD(_dlt_extracted_at) OVER (PARTITION BY id ORDER BY _dlt_extracted_at) IS NULL
            THEN TRUE
            ELSE FALSE
        END as is_current
    FROM {{ ref('stg_shopify_products') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['id', 'valid_from']) }} as product_key,
    id as product_id,
    name,
    price,
    valid_from,
    COALESCE(valid_to, '9999-12-31'::TIMESTAMP) as valid_to,
    is_current
FROM product_changes
```

---

## Advanced Techniques

### Using dbt Macros

Create reusable SQL snippets:

```sql
-- dbt/macros/currency_conversion.sql
{% macro convert_to_usd(amount_column, currency_column) %}
    CASE {{ currency_column }}
        WHEN 'usd' THEN {{ amount_column }}
        WHEN 'eur' THEN {{ amount_column }} * 1.10
        WHEN 'gbp' THEN {{ amount_column }} * 1.27
        ELSE {{ amount_column }}
    END
{% endmacro %}
```

Use in models:

```sql
SELECT
    id,
    amount,
    currency,
    {{ convert_to_usd('amount', 'currency') }} as amount_usd
FROM {{ ref('stg_stripe_charges') }}
```

### Incremental Models

For large, append-only datasets:

```sql
-- dbt/models/marts/events/fct_user_events.sql
{{ config(
    materialized='incremental',
    unique_key='event_id',
    on_schema_change='append_new_columns'
) }}

SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    properties
FROM {{ ref('stg_analytics_events') }}

{% if is_incremental() %}
WHERE event_timestamp > (SELECT MAX(event_timestamp) FROM {{ this }})
{% endif %}
```

### Dynamic SQL with Jinja

```sql
-- dbt/models/marts/finance/revenue_by_product_line.sql
{{ config(materialized='table') }}

{% set product_lines = ['electronics', 'clothing', 'home_goods'] %}

SELECT
    date,
    {% for line in product_lines %}
    SUM(CASE WHEN product_line = '{{ line }}' THEN revenue ELSE 0 END) as {{ line }}_revenue,
    {% endfor %}
    SUM(revenue) as total_revenue
FROM {{ ref('int_product_performance') }}
GROUP BY date
```

### Using dbt Packages

Install dbt_utils:

```yaml
# dbt/packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.0
```

```bash
dbt deps --profiles-dir dbt --project-dir dbt
```

Use in models:

```sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['customer_id', 'order_id']) }} as unique_key,
    customer_id,
    order_id
FROM {{ ref('int_customer_orders') }}
```

---

## Materialization Strategies

### Tables (Default in Dango)

```sql
{{ config(materialized='table') }}
```

All Dango models use `table` materialization by default for Metabase compatibility.

!!! info "Why tables?"
    Metabase requires tables for reliable schema discovery. Views can work in some
    cases but may have inconsistent behavior with Metabase features.

### Incremental (For Large Tables)

```sql
{{ config(
    materialized='incremental',
    unique_key='id'
) }}
```

**Use for**:

- Large event logs (millions of rows)
- Append-only data
- Historical archives

**Pros**: Efficient updates, handles scale
**Cons**: More complex logic, harder to debug

### Ephemeral (Advanced)

```sql
{{ config(materialized='ephemeral') }}
```

**Use for**:

- Helper CTEs that shouldn't create tables
- Small utility models
- Reducing table clutter

**Pros**: No tables created, clean namespace
**Cons**: Can't query directly in Metabase

---

## Documentation

### Schema YAML

Document all custom models:

```yaml
# dbt/models/marts/finance/schema.yml
version: 2

models:
  - name: fct_revenue
    description: |
      Daily revenue metrics aggregated from successful Stripe charges.
      Updates daily via `dango sync && dango run`.

    columns:
      - name: date
        description: Revenue date (UTC timezone)
        tests:
          - not_null
          - unique

      - name: revenue_usd
        description: Total revenue in USD (converted from cents)
        tests:
          - not_null

      - name: transaction_count
        description: Number of successful transactions
        tests:
          - not_null

      - name: unique_customers
        description: Count of distinct customers who made purchases
```

### Inline Documentation

```sql
-- dbt/models/marts/customer_metrics.sql
{{ config(materialized='table') }}

/*
Customer Lifetime Value Calculation
====================================
This model calculates key metrics for each customer:
- Total orders and revenue
- Average order value
- Customer lifespan

Updated: Daily
Owner: Analytics Team
*/

WITH customer_orders AS (
    -- Aggregate all successful charges per customer
    SELECT ...
```

---

## Testing Custom Models

### Schema Tests

```yaml
# dbt/models/marts/schema.yml
models:
  - name: customer_metrics
    tests:
      # Model-level tests
      - dbt_utils.expression_is_true:
          expression: "lifetime_value >= 0"

    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
          - relationships:
              to: ref('stg_stripe_customers')
              field: id

      - name: lifetime_orders
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### Custom SQL Tests

```sql
-- dbt/tests/assert_revenue_matches_charges.sql
WITH revenue_from_mart AS (
    SELECT SUM(revenue_usd) as total
    FROM {{ ref('fct_revenue') }}
),

revenue_from_source AS (
    SELECT SUM(amount / 100.0) as total
    FROM {{ ref('stg_stripe_charges') }}
    WHERE status = 'succeeded'
)

SELECT *
FROM revenue_from_mart
CROSS JOIN revenue_from_source
WHERE ABS(revenue_from_mart.total - revenue_from_source.total) > 0.01
```

Run tests:

```bash
dbt test --profiles-dir dbt --project-dir dbt --select marts.*
```

---

## Performance Optimization

### Optimize Query Performance

```sql
-- Bad: Multiple scans of same table
SELECT
    customer_id,
    (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) as order_count,
    (SELECT SUM(amount) FROM orders WHERE customer_id = c.id) as total
FROM customers c

-- Good: Single scan with aggregation
WITH order_stats AS (
    SELECT
        customer_id,
        COUNT(*) as order_count,
        SUM(amount) as total
    FROM orders
    GROUP BY customer_id
)

SELECT
    c.customer_id,
    COALESCE(o.order_count, 0) as order_count,
    COALESCE(o.total, 0) as total
FROM customers c
LEFT JOIN order_stats o ON c.id = o.customer_id
```

### Use Indexes (if supported)

```sql
{{ config(
    materialized='table',
    post_hook=[
        "CREATE INDEX IF NOT EXISTS idx_customer_email ON {{ this }} (email)",
        "CREATE INDEX IF NOT EXISTS idx_customer_segment ON {{ this }} (customer_segment)"
    ]
) }}
```

### Partition Large Tables

```sql
{{ config(
    materialized='incremental',
    partition_by={
        "field": "date",
        "data_type": "date",
        "granularity": "month"
    }
) }}
```

---

## Best Practices

### 1. Use CTEs for Readability

```sql
-- Good
WITH base AS (...),
     filtered AS (...),
     aggregated AS (...)
SELECT * FROM aggregated

-- Avoid
SELECT ... FROM (...) JOIN (...) WHERE ...
```

### 2. Layer Your Logic

```
Staging → Intermediate → Marts
  ↓           ↓            ↓
Simple     Reusable    Complex
Tables      Tables      Tables
```

### 3. Document Business Rules

```yaml
- name: customer_segment
  description: |
    Customer segmentation based on lifetime value:
    - vip: >= $10,000
    - high_value: >= $1,000
    - medium_value: >= $100
    - low_value: < $100
```

### 4. Test Assumptions

```yaml
tests:
  - dbt_utils.expression_is_true:
      expression: "first_order_date <= last_order_date"
```

### 5. Keep Models Focused

One model = one business concept

```
✅ customer_metrics.sql
✅ revenue_by_month.sql
❌ everything_analytics.sql
```

---

## Next Steps

- **[Testing](testing.md)** - Comprehensive data quality testing guide
- **[dbt Basics](dbt-basics.md)** - Learn dbt fundamentals
- **[Staging Models](staging-models.md)** - Understand the foundation
- **[dbt Documentation](https://docs.getdbt.com/)** - Official dbt resources
