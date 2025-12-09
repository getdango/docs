# E-commerce Analytics Tutorial

Build a complete e-commerce analytics pipeline with CSV orders and optional Stripe integration.

---

## What You'll Build

By the end of this tutorial, you'll have:

- CSV order data loaded into DuckDB
- Auto-generated staging models
- Custom dbt models for revenue analysis
- A dashboard showing key e-commerce metrics

**Duration**: ~30 minutes

---

## Prerequisites

- Dango installed (`pip install getdango`)
- Docker running
- Sample data or your own CSV files

---

## Step 1: Create Project

```bash
# Create new Dango project
dango init ecommerce-analytics
cd ecommerce-analytics

# Start services
dango start
```

Verify services are running:
```bash
dango status
```

---

## Step 2: Prepare Sample Data

Create sample order data (or use your own):

```bash
mkdir -p data/uploads/orders
```

Create `data/uploads/orders/orders.csv`:

```csv
order_id,customer_id,order_date,status,total_amount,discount,shipping
ORD001,CUST001,2024-01-15,completed,125.99,0,10.00
ORD002,CUST002,2024-01-15,completed,89.50,5.00,10.00
ORD003,CUST001,2024-01-16,completed,245.00,20.00,0
ORD004,CUST003,2024-01-17,pending,67.25,0,10.00
ORD005,CUST002,2024-01-18,completed,199.99,15.00,10.00
ORD006,CUST004,2024-01-19,cancelled,150.00,0,10.00
ORD007,CUST001,2024-01-20,completed,312.50,25.00,0
ORD008,CUST005,2024-01-21,completed,78.99,0,10.00
ORD009,CUST003,2024-01-22,completed,425.00,50.00,0
ORD010,CUST002,2024-01-23,completed,156.75,10.00,10.00
```

Create `data/uploads/orders/customers.csv`:

```csv
customer_id,name,email,signup_date,country
CUST001,Alice Johnson,alice@example.com,2023-06-15,US
CUST002,Bob Smith,bob@example.com,2023-08-20,US
CUST003,Carol Williams,carol@example.com,2023-10-01,UK
CUST004,David Brown,david@example.com,2023-11-15,CA
CUST005,Eve Davis,eve@example.com,2024-01-10,US
```

---

## Step 3: Add CSV Source

```bash
# Add CSV source via wizard
dango source add csv
```

When prompted:
- **Source name**: `ecommerce_orders`
- **Directory**: `data/uploads/orders`
- **File pattern**: `*.csv`

Or manually edit `.dango/sources.yml`:

```yaml
sources:
  - name: ecommerce_orders
    type: csv
    enabled: true
    csv:
      base_path: data/uploads/orders
      file_pattern: "*.csv"
```

---

## Step 4: Sync Data

```bash
# Sync CSV files to DuckDB
dango sync
```

Expected output:
```
Syncing source: ecommerce_orders
  Loading: orders.csv (10 rows)
  Loading: customers.csv (5 rows)
Sync complete: 2 tables, 15 total rows
Generating dbt staging models...
```

Verify data loaded:
```bash
dango db status
```

---

## Step 5: Explore Staging Models

Dango auto-generates staging models in `dbt/models/staging/`:

```bash
ls dbt/models/staging/
# stg_ecommerce_orders_orders.sql
# stg_ecommerce_orders_customers.sql
# sources.yml
```

View generated model:
```bash
cat dbt/models/staging/stg_ecommerce_orders_orders.sql
```

---

## Step 6: Create Custom Models

### Revenue by Day

Create `dbt/models/marts/fct_daily_revenue.sql`:

```sql
{{ config(materialized='table') }}

with orders as (
    select * from {{ ref('stg_ecommerce_orders_orders') }}
    where status = 'completed'
),

daily_metrics as (
    select
        date_trunc('day', order_date::date) as day,
        count(distinct order_id) as order_count,
        count(distinct customer_id) as unique_customers,
        sum(total_amount) as gross_revenue,
        sum(discount) as total_discounts,
        sum(shipping) as total_shipping,
        sum(total_amount - discount + shipping) as net_revenue
    from orders
    group by 1
)

select * from daily_metrics
order by day
```

### Customer Summary

Create `dbt/models/marts/dim_customers.sql`:

```sql
{{ config(materialized='table') }}

with customers as (
    select * from {{ ref('stg_ecommerce_orders_customers') }}
),

orders as (
    select * from {{ ref('stg_ecommerce_orders_orders') }}
    where status = 'completed'
),

customer_orders as (
    select
        customer_id,
        count(distinct order_id) as total_orders,
        sum(total_amount) as lifetime_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from orders
    group by 1
)

select
    c.customer_id,
    c.name,
    c.email,
    c.country,
    c.signup_date,
    coalesce(co.total_orders, 0) as total_orders,
    coalesce(co.lifetime_value, 0) as lifetime_value,
    co.first_order_date,
    co.last_order_date
from customers c
left join customer_orders co using (customer_id)
```

---

## Step 7: Run Transformations

```bash
# Run all dbt models
dango run
```

Verify marts created:
```bash
duckdb data/warehouse.duckdb "SELECT * FROM main.fct_daily_revenue"
```

---

## Step 8: Create Dashboard

Open Metabase:
```bash
open http://localhost:3000
```

Login with:
- Email: `admin@dango.local`
- Password: `dango123!`

### Create Questions

**1. Daily Revenue Chart**:
- Click **+ New** → **Question**
- Select **Native query**
- Run:
```sql
SELECT day, net_revenue, order_count
FROM fct_daily_revenue
ORDER BY day
```
- Visualization: Line chart
- Save as "Daily Revenue"

**2. Top Customers**:
- New question, native query:
```sql
SELECT name, country, total_orders, lifetime_value
FROM dim_customers
ORDER BY lifetime_value DESC
LIMIT 10
```
- Visualization: Table
- Save as "Top Customers"

**3. Revenue KPIs**:
- New question:
```sql
SELECT
    sum(net_revenue) as total_revenue,
    sum(order_count) as total_orders,
    avg(net_revenue / order_count) as avg_order_value
FROM fct_daily_revenue
```
- Save as "Revenue KPIs"

### Build Dashboard

1. Click **+ New** → **Dashboard**
2. Name it "E-commerce Overview"
3. Add your saved questions
4. Arrange layout:

```
┌─────────────────────────────────────────┐
│  Revenue KPIs (Scalar cards)            │
├─────────────────────────────────────────┤
│  Daily Revenue (Line chart)             │
├───────────────────┬─────────────────────┤
│  Top Customers    │  Revenue by Country │
│  (Table)          │  (Pie/Bar chart)    │
└───────────────────┴─────────────────────┘
```

---

## Step 9: Add More Data (Optional)

### Add Stripe Payments

If you have Stripe access:

```bash
# Add Stripe source
dango source add stripe
```

Configure with your API key, then:

```bash
# Sync Stripe data
dango sync --source stripe

# Run to include new staging models
dango run
```

### Create Combined Model

`dbt/models/marts/fct_revenue_combined.sql`:

```sql
{{ config(materialized='table') }}

-- Combine CSV orders with Stripe charges
with csv_revenue as (
    select
        order_date as date,
        'csv' as source,
        sum(total_amount) as revenue
    from {{ ref('stg_ecommerce_orders_orders') }}
    where status = 'completed'
    group by 1
),

{% if ref('stg_stripe_charges') %}
stripe_revenue as (
    select
        date_trunc('day', created) as date,
        'stripe' as source,
        sum(amount / 100.0) as revenue
    from {{ ref('stg_stripe_charges') }}
    where status = 'succeeded'
    group by 1
)
{% endif %}

select * from csv_revenue
{% if ref('stg_stripe_charges') %}
union all
select * from stripe_revenue
{% endif %}
```

---

## Step 10: Export Dashboard

Save your work:

```bash
# Export Metabase dashboard
dango metabase save

# Commit to git
git add .
git commit -m "feat: e-commerce analytics pipeline"
```

---

## Summary

You've built a complete e-commerce analytics pipeline:

- [x] CSV data ingestion
- [x] Auto-generated staging models
- [x] Custom fact and dimension tables
- [x] Interactive dashboard

### Files Created

```
ecommerce-analytics/
├── .dango/sources.yml           # Source config
├── data/uploads/orders/         # CSV files
├── dbt/models/
│   ├── staging/                 # Auto-generated
│   └── marts/
│       ├── fct_daily_revenue.sql
│       └── dim_customers.sql
└── metabase_export.json         # Dashboard export
```

---

## Next Steps

- [Financial Reporting](financial-reporting.md) - More advanced dbt patterns
- [Multi-Source Integration](multi-source.md) - Combine multiple sources
- [Performance](../workflows/performance.md) - Scale to larger datasets
