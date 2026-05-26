# Creating Dashboards

Build your first dashboard with Dango data in Metabase.

---

## Overview

Dashboards in Metabase combine visualizations from your Dango data into interactive views. This guide covers the Dango-specific workflow.

!!! info "Learn More About Metabase Dashboards"
    For detailed dashboard features (sharing, parameters, subscriptions), see the [official Metabase documentation](https://www.metabase.com/docs/latest/dashboards/introduction).

---

## Quick Start: First Dashboard

Create a revenue dashboard in 5 minutes.

### Step 1: Create a Question

1. Open the Web UI at `http://localhost:8800` and click **Open Metabase** in the sidebar (SSO bridge handles login automatically)

    Alternatively, access Metabase directly at `http://localhost:3000`. Check `.dango/metabase.yml` for credentials.

2. Click **"+ New"** → **"Question"**
3. Select **"DuckDB"** database
4. Choose table: `marts.customer_metrics` (or any marts table)
5. Summarize: **Sum of** `lifetime_value`
6. Group by: `created` → **by Month**
7. Visualization: **Line chart**
8. Click **"Save"** → Name: "Monthly Revenue"

### Step 2: Create Dashboard

1. Click **"+ New"** → **"Dashboard"**
2. Name: "Revenue Dashboard"
3. Click **"Create"**

### Step 3: Add Question to Dashboard

1. Click **"Add a saved question"**
2. Select "Monthly Revenue"
3. Resize and position
4. Click **"Save"**

Done! Your first dashboard is ready.

---

## Querying Dango Data

### Use Marts Tables

For dashboards, query pre-aggregated marts instead of raw data:

```sql
-- Good: Query marts (fast, clean)
SELECT * FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10

-- Avoid: Query raw tables (slow, may have duplicates)
SELECT * FROM raw_stripe.customers
```

Marts are designed for business intelligence - use them.

### Example Questions

**Monthly Revenue Trend** (Line chart):

```sql
SELECT
    DATE_TRUNC('month', created_at) as month,
    SUM(lifetime_value) as revenue
FROM marts.customer_metrics
GROUP BY month
ORDER BY month
```

**Top 10 Customers** (Table):

```sql
SELECT
    email,
    lifetime_value,
    lifetime_orders
FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10
```

**Customer Count** (Number):

```sql
SELECT COUNT(*) as total_customers
FROM marts.customer_metrics
```

### Working with dlt Metadata

Query raw data with dlt timestamp columns:

```sql
SELECT *
FROM raw_stripe.charges
WHERE _dlt_extracted_at > CURRENT_DATE - INTERVAL 1 DAY
ORDER BY _dlt_extracted_at DESC
```

---

## Dashboard Layout

### Recommended Structure

**Executive Dashboard**:

```
[  KPI 1  ] [  KPI 2  ] [  KPI 3  ]
[        Trend Chart (Line)       ]
[ Bar Chart ] [ Table/Details ]
```

**Key principles**:

- Most important metric at top-left
- Trends over time below KPIs
- Details at bottom

### Adding Filters

1. Click **"Add a filter"** (top-right)
2. Choose **Time** → Select date field
3. Connect to cards with date columns
4. Set default: "Last 30 days"

Date filters work across all cards automatically.

---

## Data Refresh

Dashboards show live data from DuckDB:

```bash
# 1. Sync new data
dango sync

# 2. Run transformations
dango run

# 3. Reload dashboard (data updates automatically)
```

No additional steps needed - Metabase queries live data.

!!! tip "Instant Monitoring Dashboard"
    Run `dango dashboard provision` to auto-create a "Data Pipeline Health" dashboard with sync status, test results, data freshness, and row count trends. See [Dashboard Provisioning](provisioning.md).

---

## Best Practices

### 1. Pre-aggregate in dbt

Create dbt marts for dashboard queries:

```sql
-- dbt/models/marts/revenue_by_month.sql
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC('month', created) as month,
    SUM(amount) as revenue,
    COUNT(*) as order_count
FROM {{ ref('stg_stripe_charges') }}
WHERE status = 'succeeded'
GROUP BY month
```

Then query the mart in Metabase - much faster.

### 2. Keep Dashboards Focused

- One dashboard = one purpose
- 6-12 cards maximum
- Use filters instead of multiple similar dashboards

### 3. Name Questions Clearly

Good: "Monthly Revenue by Product Category"
Bad: "Analysis 1" or "test query"

### 4. Version-Control Your Dashboards

Build dashboards locally, not directly on your cloud Metabase instance:

1. **Build locally** &mdash; create and iterate on dashboards at `http://localhost:3000`
2. **Export** &mdash; run `dango metabase save` to export dashboards as YAML to your project repo
3. **Commit** &mdash; `git add` the saved YAML files and commit. Dashboards are now version-controlled
4. **Deploy** &mdash; `dango remote push` syncs saved dashboards to the cloud server
5. **Restore** &mdash; `dango metabase load` on cloud restores dashboards from the repo

**Why this matters:**

- A cloud server crash or rebuild loses all Metabase state (saved questions, dashboards, collections)
- Backups cover Metabase, but the git repo is the authoritative source of truth
- Treat dashboards like code &mdash; review changes, track history, roll back if needed

**If you must build directly on cloud:**

- Run `dango metabase save` immediately after making changes on the cloud instance
- Pull the saved YAML files back to your local repo and commit them

See [Save & Load](save-load.md) for full details on the export/import workflow.

---

## Troubleshooting

### Dashboard Not Loading

Check if dbt models ran successfully:

```bash
dango run
duckdb data/warehouse.duckdb "SELECT COUNT(*) FROM marts.customer_metrics"
```

### Missing Tables in Metabase

Sync the database schema:

1. Admin → Databases → DuckDB
2. Click "Sync database schema now"

### Slow Dashboards

1. Query marts instead of raw tables
2. Add date filters to limit data
3. Create more specific dbt models

---

## Next Steps

<div class="grid cards" markdown>

-   :material-code-tags: **SQL Queries**

    ---

    DuckDB SQL syntax and patterns.

    [:octicons-arrow-right-24: SQL Queries Guide](sql-queries.md)

-   :material-chart-box: **Dashboard Provisioning**

    ---

    Auto-create a pipeline health dashboard.

    [:octicons-arrow-right-24: Provisioning](provisioning.md)

-   :material-content-save: **Save & Load**

    ---

    Version-control dashboards as YAML.

    [:octicons-arrow-right-24: Save & Load](save-load.md)

-   :material-chart-box-outline: **Metabase Overview**

    ---

    Metabase configuration in Dango.

    [:octicons-arrow-right-24: Metabase Overview](metabase-overview.md)

</div>
