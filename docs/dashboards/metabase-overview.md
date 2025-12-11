# Metabase Overview

How Dango auto-configures Metabase for your DuckDB warehouse.

---

## Overview

Metabase is the built-in BI tool in Dango, providing dashboards, SQL queries, and visualizations for your data.

**What Dango automates**:

- Metabase installation via Docker
- DuckDB connection setup
- Admin user creation
- Database schema sync

**What Metabase provides**:

- Visual query builder
- SQL editor
- Interactive dashboards
- Chart visualizations

!!! info "Learn More About Metabase"
    For detailed Metabase features (visualizations, sharing, user management), see the [official Metabase documentation](https://www.metabase.com/docs/latest/).

---

## Quick Start

### Access Metabase

Start your Dango platform:

```bash
dango start
```

Metabase is available at: **http://localhost:3000**

### Auto-Created Credentials

Dango automatically creates an admin user:

- **Email**: `admin@dango.local`
- **Password**: `dangolocal123`

!!! tip "Change Password"
    For production use, change the default password in Account Settings after first login.

### First Login

1. Open http://localhost:3000
2. Login with credentials above
3. Start querying - DuckDB connection is pre-configured

---

## Auto-Configuration

### DuckDB Connection

Dango pre-configures the database connection:

- **Database Name**: DuckDB
- **Database File**: `data/warehouse.duckdb` (shared volume)
- **Connection**: Automatic (no setup required)

!!! warning "Do Not Modify Connection"
    Dango manages the DuckDB connection settings. Modifying them may break integration.

### Available Schemas

All Dango data layers are accessible in Metabase:

| Schema | Description | Example Tables |
|--------|-------------|----------------|
| `raw_*` | Source data from dlt | `raw_stripe.charges`, `raw_stripe.customers` |
| `staging` | Auto-generated staging models | `stg_stripe_charges`, `stg_stripe_customers` |
| `intermediate` | Your business logic models | `int_customer_orders` |
| `marts` | Analytics-ready tables | `customer_metrics`, `revenue_by_month` |

**Browse in Metabase**: Home → Browse data → DuckDB

### Database Sync

Metabase syncs schema metadata:

- **On startup**: Full schema scan
- **Daily**: Automatic re-sync (2 AM default)
- **Manual**: Admin → Databases → DuckDB → "Sync database schema now"

---

## Querying Dango Data

### Browse Tables

Navigate to: **Home → Browse data → DuckDB**

```
DuckDB
├── raw_stripe
│   ├── charges
│   ├── customers
│   └── subscriptions
├── staging
│   └── stg_stripe_charges
└── marts
    └── customer_metrics
```

Click any table to preview data and create questions.

### SQL Queries

Open the SQL editor: **Home → SQL**

**Example - Query marts table**:

```sql
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_revenue
FROM marts.customer_metrics
GROUP BY month
ORDER BY month DESC
```

**Example - Query with dlt metadata**:

```sql
SELECT *
FROM raw_stripe.charges
WHERE _dlt_extracted_at > CURRENT_DATE - INTERVAL 1 DAY
ORDER BY _dlt_extracted_at DESC
```

!!! info "DuckDB SQL Syntax"
    For DuckDB-specific SQL functions, see the [DuckDB documentation](https://duckdb.org/docs/sql/introduction).

### Best Practice: Query Marts

For dashboards, query pre-aggregated marts instead of raw tables:

```sql
-- Good: Query marts (fast)
SELECT * FROM marts.revenue_by_month

-- Avoid: Aggregate raw data in Metabase (slow)
SELECT DATE_TRUNC('month', created), SUM(amount)
FROM raw_stripe.charges
GROUP BY 1
```

Create aggregations in dbt, not Metabase.

---

## Data Refresh Workflow

### Update Data in Metabase

Metabase queries live DuckDB data. To refresh:

```bash
# 1. Sync new source data
dango sync

# 2. Run dbt transformations
dango run

# 3. Reload Metabase dashboard (no action needed!)
```

Metabase shows updated data immediately after `dango run` completes.

### Schema Changes

When you add new dbt models:

```bash
# 1. Create model
dango model add

# 2. Run transformations
dango run

# 3. Sync Metabase schema
# Admin → Databases → DuckDB → "Sync database schema now"
```

Or wait for the daily automatic sync.

---

## Metabase vs dbt Docs

| Feature | Metabase | dbt Docs |
|---------|----------|----------|
| **Audience** | Business users, analysts | Data engineers |
| **Purpose** | Dashboards, reporting | Documentation, lineage |
| **Access** | http://localhost:3000 | http://localhost:8800/dbt-docs |
| **Query Interface** | Visual + SQL | View only |
| **Best For** | End-user analytics | Developer reference |

**Use both**:

- **dbt Docs**: Understand data lineage and transformations
- **Metabase**: Build dashboards and share insights

---

## Troubleshooting

### Cannot Connect to Metabase

**Check if running**:

```bash
docker ps | grep metabase
```

**Restart**:

```bash
dango stop
dango start
```

### Schema Not Updating

**Trigger manual sync**:

1. Admin → Databases → DuckDB
2. Click "Sync database schema now"

### Missing Tables

**Verify table exists**:

```bash
duckdb data/warehouse.duckdb "SHOW TABLES FROM marts;"
```

If the table exists but doesn't appear in Metabase, trigger a manual sync.

### Query Timeout

For complex queries:

1. Create a dbt mart with pre-aggregated data
2. Query the mart instead of raw tables
3. Optionally increase timeout: Admin → Databases → DuckDB → Advanced options

---

## Next Steps

<div class="grid cards" markdown>

-   :material-plus-box: **Creating Dashboards**

    ---

    Build your first dashboard with Dango data.

    [:octicons-arrow-right-24: Creating Dashboards](creating-dashboards.md)

-   :material-code-tags: **SQL Queries**

    ---

    DuckDB SQL syntax and patterns for Dango data.

    [:octicons-arrow-right-24: SQL Queries Guide](sql-queries.md)

-   :material-table-sync: **Transformations**

    ---

    Create analytics-ready tables with dbt.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **Metabase Documentation**

    ---

    Full Metabase features: visualizations, sharing, users.

    [:octicons-arrow-right-24: Metabase Docs](https://www.metabase.com/docs/latest/)

</div>
