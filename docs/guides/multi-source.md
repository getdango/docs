# Multi-Source Integration

Combine data from multiple sources into unified analytics.

---

## What You'll Build

By the end of this tutorial, you'll have:

- Multiple data sources connected (CSV + API)
- Unified data models joining sources
- Cross-source analytics dashboards

**Duration**: ~25 minutes

---

## Prerequisites

- Dango project with at least one source configured
- Understanding of dbt refs and joins
- Basic data modeling knowledge

---

## Step 1: Plan Your Sources

Before integrating sources, plan how they'll connect:

```
┌─────────────────┐     ┌─────────────────┐
│  CSV Orders     │     │  Stripe         │
│  - order_id     │     │  - customer_id  │
│  - customer_id  │──┬──│  - email        │
│  - product_id   │  │  │  - charges      │
└─────────────────┘  │  └─────────────────┘
                     │
                     │  ┌─────────────────┐
                     │  │  Google Sheets  │
                     └──│  - customer_id  │
                        │  - segment      │
                        └─────────────────┘
```

**Key questions**:
- What fields connect the sources?
- Which source is the "truth" for each entity?
- How to handle mismatches?

---

## Step 2: Configure Multiple Sources

### Example: CSV + Google Sheets

```yaml
# .dango/sources.yml
sources:
  # Order data from CSV
  - name: order_data
    type: csv
    enabled: true
    csv:
      base_path: data/uploads/orders
      file_pattern: "*.csv"

  # Customer enrichment from Google Sheets
  - name: customer_segments
    type: google_sheets
    enabled: true
    google_sheets:
      spreadsheet_url_or_id: "1ABC..."
      credentials_path: "~/.config/gcloud/credentials.json"
```

### Authenticate and Sync

```bash
# OAuth for Google Sheets
dango auth google_sheets

# Sync all sources
dango sync
```

---

## Step 3: Understand the Raw Data

After syncing, explore what you have:

```bash
# List all tables
duckdb data/warehouse.duckdb "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema LIKE 'raw_%'"
```

Expected:
```
raw_order_data.orders
raw_order_data.products
raw_customer_segments.sheet1
```

Check schemas:
```sql
-- Orders schema
DESCRIBE raw_order_data.orders;

-- Customer segments schema
DESCRIBE raw_customer_segments.sheet1;
```

---

## Step 4: Create Integration Models

### Customer Master

Combine customer data from multiple sources:

```sql
-- dbt/models/intermediate/int_customers_unified.sql
{{ config(materialized='table') }}

with order_customers as (
    -- Customers from order data
    select distinct
        customer_id,
        customer_email as email,
        customer_name as name,
        'orders' as source
    from {{ ref('stg_order_data_orders') }}
    where customer_id is not null
),

sheet_customers as (
    -- Customer enrichment from Google Sheets
    select
        customer_id,
        email,
        name,
        segment,
        acquisition_channel,
        'sheets' as source
    from {{ ref('stg_customer_segments_sheet1') }}
),

-- Combine with preference for enriched data
unified as (
    select
        coalesce(s.customer_id, o.customer_id) as customer_id,
        coalesce(s.email, o.email) as email,
        coalesce(s.name, o.name) as name,
        s.segment,
        s.acquisition_channel,
        o.customer_id is not null as has_orders,
        s.customer_id is not null as has_enrichment
    from order_customers o
    full outer join sheet_customers s
        on o.customer_id = s.customer_id
)

select * from unified
```

### Orders with Customer Context

```sql
-- dbt/models/marts/fct_orders_enriched.sql
{{ config(materialized='table') }}

with orders as (
    select * from {{ ref('stg_order_data_orders') }}
),

customers as (
    select * from {{ ref('int_customers_unified') }}
)

select
    o.order_id,
    o.order_date,
    o.product_id,
    o.quantity,
    o.amount,
    o.customer_id,
    c.name as customer_name,
    c.email as customer_email,
    c.segment as customer_segment,
    c.acquisition_channel
from orders o
left join customers c using (customer_id)
```

---

## Step 5: Handle Data Quality

### Check for Orphans

```sql
-- dbt/tests/orphan_customers.sql
-- Find orders with no matching customer
select order_id, customer_id
from {{ ref('stg_order_data_orders') }}
where customer_id not in (
    select customer_id from {{ ref('int_customers_unified') }}
)
```

### Add Tests

```yaml
# dbt/models/intermediate/schema.yml
version: 2

models:
  - name: int_customers_unified
    tests:
      - unique:
          column_name: customer_id
    columns:
      - name: customer_id
        tests:
          - not_null
      - name: email
        tests:
          - not_null
```

Run tests:
```bash
cd dbt && dbt test
```

---

## Step 6: Build Cross-Source Analytics

### Revenue by Segment

```sql
-- dbt/models/marts/fct_revenue_by_segment.sql
{{ config(materialized='table') }}

with orders as (
    select * from {{ ref('fct_orders_enriched') }}
)

select
    customer_segment,
    acquisition_channel,
    date_trunc('month', order_date::date) as month,
    count(distinct order_id) as order_count,
    count(distinct customer_id) as customer_count,
    sum(amount) as total_revenue,
    avg(amount) as avg_order_value
from orders
group by 1, 2, 3
```

### Customer Cohort Analysis

```sql
-- dbt/models/marts/fct_cohort_analysis.sql
{{ config(materialized='table') }}

with customer_first_order as (
    select
        customer_id,
        min(order_date) as first_order_date
    from {{ ref('fct_orders_enriched') }}
    group by 1
),

orders_with_cohort as (
    select
        o.*,
        date_trunc('month', c.first_order_date::date) as cohort_month,
        datediff('month', c.first_order_date::date, o.order_date::date) as months_since_first
    from {{ ref('fct_orders_enriched') }} o
    join customer_first_order c using (customer_id)
)

select
    cohort_month,
    months_since_first,
    count(distinct customer_id) as customers,
    sum(amount) as revenue
from orders_with_cohort
group by 1, 2
order by 1, 2
```

---

## Step 7: Run All Models

```bash
# Run full pipeline
dango run

# Check lineage
dango docs
# Open http://localhost:8081 and view the DAG
```

---

## Step 8: Create Unified Dashboard

### Cross-Source Questions

**Revenue by Segment** (Bar chart):
```sql
SELECT
    customer_segment,
    sum(total_revenue) as revenue
FROM fct_revenue_by_segment
GROUP BY 1
ORDER BY 2 DESC
```

**Acquisition Channel Performance** (Table):
```sql
SELECT
    acquisition_channel,
    count(distinct customer_id) as customers,
    sum(total_revenue) as revenue,
    sum(total_revenue) / count(distinct customer_id) as revenue_per_customer
FROM fct_revenue_by_segment
GROUP BY 1
ORDER BY revenue DESC
```

**Cohort Retention** (Heatmap):
```sql
SELECT
    cohort_month,
    months_since_first,
    customers
FROM fct_cohort_analysis
WHERE months_since_first <= 12
ORDER BY cohort_month, months_since_first
```

### Dashboard Layout

```
┌─────────────────────────────────────────┐
│  Total Revenue  │  Customers  │  AOV    │
├─────────────────────────────────────────┤
│  Revenue by Segment (Bar chart)         │
├───────────────────┬─────────────────────┤
│  Channel          │  Cohort             │
│  Performance      │  Retention          │
└───────────────────┴─────────────────────┘
```

---

## Step 9: Maintain Data Quality

### Add Freshness Tests

```yaml
# dbt/models/staging/sources.yml
version: 2

sources:
  - name: order_data
    freshness:
      warn_after: {count: 24, period: hour}
      error_after: {count: 48, period: hour}
    tables:
      - name: orders
        loaded_at_field: _dlt_load_time

  - name: customer_segments
    freshness:
      warn_after: {count: 7, period: day}
    tables:
      - name: sheet1
        loaded_at_field: _dlt_load_time
```

Check freshness:
```bash
cd dbt && dbt source freshness
```

---

## Step 10: Document the Integration

### Update README

```markdown
# Multi-Source Analytics

## Data Sources

| Source | Type | Update Frequency | Key Fields |
|--------|------|------------------|------------|
| order_data | CSV | Daily | customer_id, order_id |
| customer_segments | Google Sheets | Weekly | customer_id, segment |

## Integration Keys

- **customer_id**: Primary link between sources
- Email used as fallback match

## Known Issues

- ~5% of orders have no customer segment (default to "Unknown")
```

---

## Common Integration Patterns

### Pattern 1: Lookup Enrichment

```sql
-- Enrich facts with dimension lookup
select
    f.*,
    d.attribute
from facts f
left join dimension d using (key)
```

### Pattern 2: Slowly Changing Dimensions

```sql
-- Track changes over time
select
    entity_id,
    attribute,
    valid_from,
    valid_to
from dimension_history
where current_date between valid_from and coalesce(valid_to, '9999-12-31')
```

### Pattern 3: Fuzzy Matching

```sql
-- When IDs don't match exactly
select
    a.*,
    b.enrichment
from source_a a
left join source_b b
    on lower(trim(a.email)) = lower(trim(b.email))
```

---

## Summary

You've built a multi-source analytics system:

- [x] Multiple sources configured
- [x] Unified customer model
- [x] Cross-source metrics
- [x] Data quality tests

### Key Takeaways

1. **Plan integration points** before building
2. **Create intermediate models** for unified entities
3. **Test data quality** at integration points
4. **Document assumptions** about data relationships

---

## Next Steps

- [Custom API Integration](custom-api.md) - Add custom sources
- [dbt Workflows](../workflows/dbt-workflows.md) - Advanced modeling
- [Performance](../workflows/performance.md) - Optimize joins
