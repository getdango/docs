# Financial Reporting Tutorial

Create financial dashboards with Stripe revenue data and dbt transformations.

---

## What You'll Build

By the end of this tutorial, you'll have:

- Stripe payment data synced to DuckDB
- Financial dbt models (MRR, revenue by period)
- A financial dashboard with key metrics

**Duration**: ~20 minutes

---

## Prerequisites

- Dango project initialized
- Stripe account with API access (test mode works)
- Basic SQL knowledge

---

## Step 1: Configure Stripe Source

### Get API Key

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret key** (starts with `sk_test_` or `sk_live_`)

### Add Source

```bash
dango source add stripe
```

When prompted:
- **Source name**: `stripe_payments`
- **API Key**: Your Stripe secret key

Or configure manually in `.dango/sources.yml`:

```yaml
sources:
  - name: stripe_payments
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      endpoints:
        - charges
        - customers
        - subscriptions
        - invoices
```

Add credentials to `.dlt/secrets.toml`:

```toml
[sources.stripe]
stripe_secret_key = "sk_test_xxx"
```

!!! warning "Protect Your API Key"
    Never commit your Stripe API key. Use environment variables in production.

---

## Step 2: Sync Data

```bash
# Sync Stripe data
dango sync --source stripe_payments

# Check what was loaded
dango db status
```

Expected tables:
- `raw_stripe.charges`
- `raw_stripe.customers`
- `raw_stripe.subscriptions`
- `raw_stripe.invoices`

---

## Step 3: Create Financial Models

### Monthly Revenue

Create `dbt/models/marts/fct_monthly_revenue.sql`:

```sql
{{ config(materialized='table') }}

with charges as (
    select * from {{ ref('stg_stripe_payments_charges') }}
    where status = 'succeeded'
),

monthly as (
    select
        date_trunc('month', created::timestamp) as month,
        count(*) as transaction_count,
        sum(amount / 100.0) as gross_revenue,
        sum(case when refunded then amount / 100.0 else 0 end) as refunds,
        sum(case when refunded then 0 else amount / 100.0 end) as net_revenue,
        avg(amount / 100.0) as avg_transaction_value
    from charges
    group by 1
)

select
    month,
    transaction_count,
    gross_revenue,
    refunds,
    net_revenue,
    avg_transaction_value,
    -- Month-over-month growth
    net_revenue - lag(net_revenue) over (order by month) as revenue_change,
    (net_revenue - lag(net_revenue) over (order by month))
        / nullif(lag(net_revenue) over (order by month), 0) * 100 as growth_pct
from monthly
order by month
```

### Revenue by Customer

Create `dbt/models/marts/fct_customer_revenue.sql`:

```sql
{{ config(materialized='table') }}

with charges as (
    select * from {{ ref('stg_stripe_payments_charges') }}
    where status = 'succeeded'
    and not refunded
),

customers as (
    select * from {{ ref('stg_stripe_payments_customers') }}
),

customer_revenue as (
    select
        customer as customer_id,
        count(*) as total_transactions,
        sum(amount / 100.0) as lifetime_revenue,
        min(created) as first_charge_date,
        max(created) as last_charge_date,
        avg(amount / 100.0) as avg_transaction
    from charges
    where customer is not null
    group by 1
)

select
    cr.customer_id,
    c.email,
    c.name,
    cr.total_transactions,
    cr.lifetime_revenue,
    cr.first_charge_date,
    cr.last_charge_date,
    cr.avg_transaction,
    -- Days since first charge
    current_date - cr.first_charge_date::date as customer_age_days
from customer_revenue cr
left join customers c on cr.customer_id = c.id
order by cr.lifetime_revenue desc
```

### Daily Metrics

Create `dbt/models/marts/fct_daily_metrics.sql`:

```sql
{{ config(materialized='table') }}

with charges as (
    select * from {{ ref('stg_stripe_payments_charges') }}
),

daily as (
    select
        date_trunc('day', created::timestamp) as day,
        count(*) as total_charges,
        count(case when status = 'succeeded' then 1 end) as successful_charges,
        count(case when status = 'failed' then 1 end) as failed_charges,
        sum(case when status = 'succeeded' then amount / 100.0 else 0 end) as revenue,
        count(distinct customer) as unique_customers
    from charges
    group by 1
)

select
    day,
    total_charges,
    successful_charges,
    failed_charges,
    successful_charges::float / nullif(total_charges, 0) * 100 as success_rate,
    revenue,
    unique_customers,
    revenue / nullif(successful_charges, 0) as avg_charge_amount
from daily
order by day
```

---

## Step 4: Add Schema Documentation

Create `dbt/models/marts/schema.yml`:

```yaml
version: 2

models:
  - name: fct_monthly_revenue
    description: Monthly revenue metrics from Stripe charges
    columns:
      - name: month
        description: First day of the month
        tests:
          - unique
          - not_null
      - name: net_revenue
        description: Revenue after refunds (in dollars)
      - name: growth_pct
        description: Month-over-month growth percentage

  - name: fct_customer_revenue
    description: Lifetime revenue metrics by customer
    columns:
      - name: customer_id
        description: Stripe customer ID
        tests:
          - unique
          - not_null
      - name: lifetime_revenue
        description: Total revenue from customer (in dollars)

  - name: fct_daily_metrics
    description: Daily charge and revenue metrics
    columns:
      - name: day
        description: Date
        tests:
          - unique
          - not_null
```

---

## Step 5: Run Transformations

```bash
# Run all models
dango run

# Or run specific models
cd dbt && dbt run --select fct_monthly_revenue fct_customer_revenue fct_daily_metrics
```

Verify:
```bash
duckdb data/warehouse.duckdb "SELECT * FROM main.fct_monthly_revenue ORDER BY month DESC LIMIT 5"
```

---

## Step 6: Create Financial Dashboard

Open Metabase:
```bash
open http://localhost:3000
```

### Key Metrics Cards

**Total Revenue (Current Month)**:
```sql
SELECT net_revenue as "Revenue This Month"
FROM fct_monthly_revenue
WHERE month = date_trunc('month', current_date)
```

**Month-over-Month Growth**:
```sql
SELECT growth_pct as "MoM Growth %"
FROM fct_monthly_revenue
WHERE month = date_trunc('month', current_date)
```

**Total Customers**:
```sql
SELECT count(*) as "Total Customers"
FROM fct_customer_revenue
```

### Charts

**Revenue Trend** (Line chart):
```sql
SELECT
    month,
    net_revenue,
    gross_revenue
FROM fct_monthly_revenue
ORDER BY month
```

**Daily Revenue** (Area chart):
```sql
SELECT day, revenue
FROM fct_daily_metrics
WHERE day >= current_date - interval '30 days'
ORDER BY day
```

**Top Customers** (Table):
```sql
SELECT
    name,
    email,
    lifetime_revenue,
    total_transactions
FROM fct_customer_revenue
ORDER BY lifetime_revenue DESC
LIMIT 10
```

**Success Rate Trend** (Line chart):
```sql
SELECT
    day,
    success_rate
FROM fct_daily_metrics
WHERE day >= current_date - interval '30 days'
ORDER BY day
```

---

## Step 7: Dashboard Layout

Arrange your dashboard:

```
┌─────────────────────────────────────────────────────┐
│  Revenue This    │  MoM Growth %  │  Total          │
│  Month: $XX,XXX  │  +12.5%        │  Customers: XXX │
├─────────────────────────────────────────────────────┤
│                                                     │
│            Monthly Revenue Trend                    │
│                                                     │
├───────────────────────┬─────────────────────────────┤
│  Daily Revenue        │  Top Customers              │
│  (Last 30 days)       │  (Table)                    │
├───────────────────────┴─────────────────────────────┤
│                                                     │
│           Payment Success Rate                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Step 8: Add Date Filters

Make your dashboard interactive:

1. Edit dashboard
2. Click **Add a filter** → **Time**
3. Configure:
   - Filter type: Date range
   - Wire to: fct_daily_metrics.day, fct_monthly_revenue.month
4. Set default to "Last 3 months"

---

## Step 9: Schedule Updates

### Auto-Sync

Ensure Stripe syncs regularly:

```bash
# File watcher handles this automatically
dango status
```

### Dashboard Subscriptions

In Metabase:
1. Open dashboard
2. Click bell icon (Subscriptions)
3. Configure weekly email reports to stakeholders

---

## Step 10: Export and Save

```bash
# Export dashboard
dango metabase save

# Commit work
git add .
git commit -m "feat: financial reporting dashboard"
```

---

## Advanced: MRR Calculations

For subscription businesses, add MRR tracking:

```sql
-- dbt/models/marts/fct_mrr.sql
{{ config(materialized='table') }}

with subscriptions as (
    select * from {{ ref('stg_stripe_payments_subscriptions') }}
),

mrr_by_month as (
    select
        date_trunc('month', created::timestamp) as month,
        sum(
            case status
                when 'active' then plan_amount / 100.0
                when 'trialing' then 0
                else 0
            end
        ) as mrr
    from subscriptions
    group by 1
)

select
    month,
    mrr,
    mrr - lag(mrr) over (order by month) as mrr_change,
    (mrr - lag(mrr) over (order by month))
        / nullif(lag(mrr) over (order by month), 0) * 100 as mrr_growth_pct
from mrr_by_month
order by month
```

---

## Summary

You've built a financial reporting system:

- [x] Stripe data ingestion
- [x] Revenue analysis models
- [x] Customer lifetime value tracking
- [x] Interactive financial dashboard

### Models Created

| Model | Purpose |
|-------|---------|
| `fct_monthly_revenue` | Monthly revenue with growth |
| `fct_customer_revenue` | Customer LTV analysis |
| `fct_daily_metrics` | Daily operational metrics |

---

## Next Steps

- [Multi-Source Integration](multi-source.md) - Add more data sources
- [Performance](../workflows/performance.md) - Optimize for large datasets
- [dbt Workflows](../workflows/dbt-workflows.md) - Advanced modeling
