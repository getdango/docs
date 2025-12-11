# Dashboards

Build interactive dashboards and visualizations with Metabase.

---

## Overview

Dango includes Metabase, a business intelligence tool that runs automatically when you start your data platform. Query your DuckDB warehouse, build dashboards, and share insights—all through a web interface.

**What Dango automates**:

- Metabase installation and setup
- DuckDB connection configuration
- Admin user creation
- Schema synchronization

**What Metabase provides**:

- Visual query builder (no SQL required)
- SQL editor for advanced analytics
- Interactive dashboards with filters
- Sharing and collaboration features

!!! info "Learn More About Metabase"
    For detailed Metabase features (visualizations, sharing, user management), see the [official Metabase documentation](https://www.metabase.com/docs/latest/).

---

## Quick Start

### Access Metabase

Start the Dango platform:

```bash
dango start
```

Open Metabase: **http://localhost:3000**

**Auto-created credentials**:

- Email: `admin@dango.local`
- Password: `dangolocal123`

### Your First Dashboard

Create a dashboard in 5 minutes:

**1. Create a Question**:

1. Click **"+ New"** → **"Question"**
2. Select **"DuckDB"** database
3. Choose table: `marts.customer_metrics`
4. Summarize: **Sum of** `lifetime_value`
5. Group by: `created` → **by Month**
6. Visualization: **Line chart**
7. Click **"Save"** → Name: "Monthly Revenue"

**2. Create Dashboard**:

1. Click **"+ New"** → **"Dashboard"**
2. Name: "Revenue Dashboard"
3. Click **"Add a saved question"**
4. Select "Monthly Revenue"
5. Click **"Save"**

Done! Your first dashboard is ready.

---

## Dashboard Guides

<div class="grid cards" markdown>

-   :material-chart-box-outline: **Metabase Overview**

    ---

    How Dango auto-configures Metabase for your DuckDB warehouse.

    - Auto-created admin credentials
    - DuckDB connection setup
    - Available data schemas
    - Data refresh workflow

    [:octicons-arrow-right-24: Metabase Overview](metabase-overview.md)

-   :material-plus-box: **Creating Dashboards**

    ---

    Build your first dashboard with Dango data.

    - Quick start tutorial
    - Querying marts vs raw data
    - Dashboard layout tips
    - Best practices

    [:octicons-arrow-right-24: Creating Dashboards](creating-dashboards.md)

-   :material-code-tags: **SQL Queries**

    ---

    DuckDB SQL patterns for querying Dango data.

    - Schema-qualified names
    - dlt metadata columns
    - Date functions and patterns
    - Query optimization

    [:octicons-arrow-right-24: SQL Queries Guide](sql-queries.md)

</div>

---

## Available Data Schemas

Metabase has access to all Dango data layers:

| Schema | Description | When to Query |
|--------|-------------|---------------|
| `raw` | Single-table sources (CSV) | Debug source data |
| `raw_*` | Multi-table sources (e.g., `raw_stripe`) | Explore raw API data |
| `staging` | Auto-generated staging models | Build custom analytics |
| `intermediate` | Reusable business logic | Advanced analysis |
| `marts` | Analytics-ready tables | **Dashboards (recommended)** |

**Best practice**: Always prefer marts for dashboards—pre-aggregated, tested, and optimized.

---

## Data Refresh

Metabase queries live data from DuckDB:

```bash
# 1. Sync new source data
dango sync

# 2. Run dbt transformations
dango run

# 3. Reload dashboard (data updates automatically)
```

No additional steps needed—Metabase shows updated data immediately.

### Schema Changes

When you add new dbt models:

1. Run `dango run` to create the table
2. Sync Metabase schema: Admin → Databases → DuckDB → "Sync database schema now"

Or wait for the daily automatic sync (2 AM default).

---

## Common Workflows

### Explore Source Data

After syncing a data source:

```bash
dango sync --source stripe_payments
```

View raw data in Metabase:

```
Browse data → DuckDB → raw_stripe → charges
```

### Query Staging Tables

Use auto-generated staging models:

```sql
SELECT * FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
  AND created >= CURRENT_DATE - INTERVAL 7 DAY
ORDER BY created DESC
```

### Build Business Dashboards

Query marts created in dbt:

```sql
SELECT month, customer_count, revenue_usd
FROM marts.monthly_metrics
ORDER BY month DESC
LIMIT 12
```

---

## Best Practices

### 1. Query Marts, Not Raw

```sql
-- Good: Pre-aggregated mart
SELECT * FROM marts.revenue_by_month

-- Avoid: Aggregating raw data in Metabase
SELECT DATE_TRUNC('month', created), SUM(amount)
FROM raw_stripe.charges
GROUP BY 1
```

### 2. Use Meaningful Names

- Questions: "Monthly Revenue Trend" (not "Query 1")
- Dashboards: "Executive Overview" (not "Dashboard")

### 3. Keep Dashboards Focused

- One dashboard = One purpose
- 6-12 cards maximum
- Use filters instead of multiple similar dashboards

### 4. Add Date Filters

Make dashboards interactive with date range filters. Set sensible defaults (last 30 days).

---

## Troubleshooting

### Cannot Access Metabase

```bash
# Check if running
docker ps | grep metabase

# Restart
dango stop && dango start
```

### Table Not Found

1. Add schema prefix: `marts.revenue_by_month`
2. Verify table exists:
   ```bash
   duckdb data/warehouse.duckdb "SHOW TABLES FROM marts;"
   ```
3. Sync Metabase schema (Admin → Databases → Sync)

### Slow Dashboards

1. Query marts instead of raw tables
2. Add date filters to limit data
3. Create more specific dbt models

---

## Metabase vs dbt Docs

| Feature | Metabase | dbt Docs |
|---------|----------|----------|
| **Purpose** | Business intelligence | Technical documentation |
| **Audience** | Business users, analysts | Data engineers |
| **URL** | http://localhost:3000 | http://localhost:8800/dbt-docs |
| **Features** | Dashboards, visualizations | Lineage, SQL code |

**Use both**: dbt Docs for understanding transformations, Metabase for dashboards.

---

## Next Steps

<div class="grid cards" markdown>

-   :material-chart-box-outline: **Metabase Overview**

    ---

    Learn about Metabase auto-configuration in Dango.

    [:octicons-arrow-right-24: Metabase Overview](metabase-overview.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Create marts tables with dbt for optimal dashboard performance.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **Metabase Documentation**

    ---

    Full Metabase features: visualizations, sharing, embedding.

    [:octicons-arrow-right-24: Metabase Docs](https://www.metabase.com/docs/latest/)

</div>
