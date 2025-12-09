# Metabase Overview

Introduction to Metabase in Dango with auto-configuration and basic features.

---

## Overview

Metabase is the built-in business intelligence tool in Dango, providing a powerful web-based interface for creating dashboards, writing SQL queries, and visualizing data from your DuckDB warehouse.

**What Metabase provides**:

- Visual query builder (no SQL required)
- SQL editor for advanced queries
- Interactive dashboards with filters
- Chart and visualization library
- Shareable reports and embeds
- User management and permissions

**What Dango automates**:

- Metabase installation and configuration
- DuckDB connection setup
- Database schema sync
- Container orchestration
- Port management

---

## Quick Start

### Access Metabase

After starting Dango:

```bash
dango start
```

Metabase is available at: **http://localhost:3000**

!!! tip "First-Time Setup"
    On first launch, Metabase will prompt you to create an admin account. This is a one-time setup.

### Initial Admin Setup

1. **Open Metabase**: Navigate to http://localhost:3000

2. **Create Admin Account**:
   - Email: your@email.com
   - Password: (choose a secure password)
   - First name / Last name

3. **Skip "Add your data"** - Dango has already configured the DuckDB connection

4. **Complete setup** - Click "Take me to Metabase"

You're now ready to query your data!

---

## Auto-Configuration

Dango automatically configures Metabase on `dango start`:

### DuckDB Connection

Pre-configured database connection:

- **Database Name**: DuckDB
- **Connection Type**: DuckDB (via custom driver)
- **Database File**: Shared volume mount to `data/warehouse.duckdb`
- **Read-Only**: No (allows creating models in Metabase)

### Available Schemas

All Dango data layers are accessible:

| Schema | Description | Tables |
|--------|-------------|--------|
| `raw` | Source of truth from dlt | Single-table sources |
| `raw_*` | Multi-table sources | Stripe, database exports, etc. |
| `staging` | Auto-generated staging models | `stg_*` tables |
| `intermediate` | Custom business logic | Your intermediate models |
| `marts` | Analytics-ready tables | Your marts models |

### Database Sync

Metabase automatically syncs schema metadata:

- **On startup**: Full schema scan
- **Daily**: Automatic re-sync (default)
- **Manual**: Admin → Databases → DuckDB → "Sync database schema now"

---

## Metabase Interface

### Home Screen

After login, you'll see:

- **Our analytics** - Saved questions and dashboards
- **Databases** - Available data sources (DuckDB)
- **Collections** - Organized folders for content
- **Search** - Find questions, dashboards, tables

### Navigation

**Top Navigation Bar**:

- **Home** - Dashboard overview
- **+** - Create new question or dashboard
- **Browse data** - Explore tables by schema
- **SQL** - Open SQL editor

**Settings (Gear Icon)**:

- Admin settings
- Account settings
- About Metabase

---

## Key Features

### 1. Browse Data

**Access**: Home → Browse data → DuckDB

Explore your warehouse:

```
DuckDB
├── raw
│   └── csv_uploads
├── raw_stripe
│   ├── charges
│   ├── customers
│   └── subscriptions
├── staging
│   ├── stg_stripe_charges
│   ├── stg_stripe_customers
│   └── stg_stripe_subscriptions
├── intermediate
│   └── int_customer_orders
└── marts
    ├── customer_metrics
    └── revenue_by_month
```

Click any table to:
- Preview first 2000 rows
- See column types
- View sample values
- Create questions

### 2. Ask a Question

**Visual Query Builder** - No SQL required:

1. Click **"+ New"** → **"Question"**
2. Select **DuckDB database**
3. Choose a table (e.g., `marts.customer_metrics`)
4. Add filters, aggregations, grouping
5. Visualize results
6. Save question

**Example**: Top 10 customers by revenue:
- Table: `marts.customer_metrics`
- Sort by: `lifetime_value` descending
- Limit: 10
- Visualization: Table or Bar chart

### 3. SQL Editor

**Access**: Home → SQL

Write custom SQL queries:

```sql
SELECT
    DATE_TRUNC('month', created) as month,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_revenue
FROM marts.customer_metrics
GROUP BY month
ORDER BY month DESC
LIMIT 12
```

**Features**:
- Auto-completion for tables and columns
- Schema browser (left sidebar)
- Query variables for filters
- Save and organize queries
- Export results (CSV, JSON, XLSX)

### 4. Visualizations

Available chart types:

**Basic Charts**:
- Table
- Number (single metric)
- Trend (time series line)
- Bar chart
- Line chart
- Area chart
- Pie chart

**Advanced Charts**:
- Funnel
- Map (with lat/long data)
- Scatter plot
- Waterfall
- Gauge
- Progress bar

**Customization**:
- Colors and formatting
- Axis labels and ranges
- Goal lines
- Multi-series charts

### 5. Dashboards

Combine multiple visualizations:

1. Create dashboard: **"+ New"** → **"Dashboard"**
2. Add saved questions as cards
3. Arrange cards in grid layout
4. Add text cards for context
5. Add filters (apply across cards)
6. Save and share

**Dashboard Features**:
- Auto-refresh
- Full-screen mode
- Public sharing links
- PDF/PNG export
- Time-based filters
- Parameter drill-down

---

## Common Workflows

### View Raw Source Data

```
Home → Browse data → DuckDB → raw_stripe → charges
```

Preview Stripe charges directly from dlt ingestion.

### Query Staging Tables

```
Home → SQL
```

```sql
SELECT * FROM staging.stg_stripe_charges
WHERE status = 'succeeded'
  AND created >= CURRENT_DATE - INTERVAL 7 DAY
ORDER BY created DESC
```

### Create Business Metrics

```
Home → + New → Question → marts.revenue_by_month
```

Build visualizations from your dbt marts.

### Build Executive Dashboard

1. Create monthly revenue trend (line chart)
2. Create customer count (number)
3. Create top products (bar chart)
4. Combine in dashboard
5. Add date filter
6. Share with team

---

## Data Refresh

### When Data Updates in DuckDB

Metabase queries live data:

```bash
# 1. Sync new source data
dango sync --source stripe_payments

# 2. Run dbt transformations
dango run

# 3. Refresh Metabase dashboard
# (Just reload the page - no action needed!)
```

### Schema Changes

When you add new tables or columns:

**Automatic**: Daily sync at 2 AM (default)

**Manual Sync**:
1. Admin → Databases → DuckDB
2. Click **"Sync database schema now"**
3. Wait 30-60 seconds
4. New tables/columns appear

**After running `dango generate`**:
```bash
dango generate  # Creates new staging models
dango run       # Materializes them
# → Sync Metabase manually or wait for daily sync
```

---

## User Management

### Create Additional Users

Admin → People → Add someone

**User Roles**:

| Role | Permissions |
|------|-------------|
| **Admin** | Full access, manage users, settings |
| **Editor** | Create/edit questions and dashboards |
| **Viewer** | View and filter, cannot edit |

### Collections & Permissions

Organize content:

- **Collections** - Folders for dashboards and questions
- **Permissions** - Control database/schema access per group
- **Sharing** - Public links, email subscriptions

---

## Configuration

### Metabase Settings

Access via: Admin → Settings

**Recommended Settings**:

| Setting | Recommendation | Why |
|---------|----------------|-----|
| Email | Configure SMTP | For subscriptions and alerts |
| Slack | Optional | Dashboard notifications |
| Query Caching | Enabled (default) | Faster repeat queries |
| Auto-refresh | 1-5 minutes | Live dashboard updates |
| Timezone | Match your team | Correct date display |

### Database Settings

Admin → Databases → DuckDB → Settings

**Available Options**:

- **Display name**: Customize (default: "DuckDB")
- **Rerun queries for simple exploration**: Enabled (recommended)
- **Synchronization frequency**: Daily (default) or hourly
- **Refingerprinting frequency**: Weekly (default)

!!! warning "Do Not Modify Connection"
    Dango manages the DuckDB connection. Changing connection settings may break integration.

---

## Performance Tips

### 1. Use Marts for Dashboards

```sql
-- Good: Query pre-aggregated marts
SELECT * FROM marts.revenue_by_month

-- Avoid: Aggregating in Metabase on large raw tables
SELECT DATE_TRUNC('month', created), SUM(amount)
FROM raw_stripe.charges
GROUP BY 1
```

Create aggregations in dbt, not Metabase queries.

### 2. Enable Query Caching

Admin → Settings → Caching

- Caches query results for faster repeat views
- Configurable TTL (time to live)
- Automatic invalidation on schema changes

### 3. Limit Dashboard Cards

- Aim for 6-12 cards per dashboard
- Split large dashboards into multiple themed dashboards
- Use tabs for related content

### 4. Use Filters Wisely

Add dashboard filters to reduce query load:

```
Date filter: Last 30 days (default)
Status filter: Active only
```

Reduces rows scanned on each query.

---

## Troubleshooting

### Cannot Connect to Metabase

**Check if running**:
```bash
docker ps | grep metabase
```

**Restart if needed**:
```bash
dango stop
dango start
```

**Check port availability**:
```bash
lsof -i :3000
```

### Schema Not Updating

**Trigger manual sync**:
1. Admin → Databases → DuckDB
2. "Sync database schema now"

**Check for errors**:
1. Admin → Databases → DuckDB
2. View "Connection details" and "Sync status"

### Query Timeout

For long-running queries:

1. Optimize in dbt first (create aggregated marts)
2. Admin → Databases → DuckDB → Advanced options
3. Increase "Query timeout" (default: 30 seconds)

### Missing Tables

**Verify table exists in DuckDB**:
```bash
duckdb data/warehouse.duckdb "SHOW TABLES FROM marts;"
```

**If exists, sync Metabase**:
- Admin → Databases → DuckDB → "Sync database schema now"

---

## Metabase vs dbt Docs

Both provide data exploration, with different purposes:

| Feature | Metabase | dbt Docs |
|---------|----------|----------|
| **Audience** | Business users, analysts | Data engineers |
| **Purpose** | BI, dashboards, reporting | Technical documentation, lineage |
| **Access** | http://localhost:3000 | http://localhost:8081 (via `dango docs`) |
| **Query Interface** | Visual + SQL | View only |
| **Visualizations** | Full chart library | Sample data preview |
| **Best For** | End-user analytics | Developer reference |

**Use both**:
- dbt Docs: Understand data lineage and transformations
- Metabase: Build dashboards and share insights

---

## Data Security

### Access Control

**Production deployments**:

1. Enable authentication
2. Create user groups
3. Restrict database access by group
4. Use read-only credentials for DuckDB (if possible)

### Audit Logging

Track query activity:

- Admin → Troubleshooting → Logs
- View query history
- Monitor user activity

### Public Sharing

**Be cautious**:
- Public links expose data without authentication
- Use signed embeds for controlled sharing
- Set expiration dates on public shares

---

## Backup and Recovery

### Metabase Application Database

Metabase stores dashboards, questions, and users in its own database (H2 by default):

**Location** (in Docker): `/metabase.db/`

**Backup**:
```bash
# Metabase data persists in Docker volume
docker volume ls | grep metabase

# Backup volume (advanced)
docker run --rm -v metabase_data:/data -v $(pwd):/backup ubuntu tar czf /backup/metabase-backup.tar.gz /data
```

### DuckDB Warehouse

Your actual data is in DuckDB:

```bash
# Backup warehouse
cp data/warehouse.duckdb data/warehouse-backup-$(date +%Y%m%d).duckdb
```

**Restore**:
```bash
cp data/warehouse-backup-20241209.duckdb data/warehouse.duckdb
dango start
```

---

## Advanced Features

### SQL Snippets

Reusable SQL fragments:

1. Admin → SQL Snippets
2. Create snippet: `{{snippet: active_customers}}`
3. Use in queries:
   ```sql
   SELECT * FROM {{ snippet: active_customers }}
   WHERE created > CURRENT_DATE - 30
   ```

### Alerts and Subscriptions

**Email Alerts**:
- Set thresholds on metrics
- Daily/weekly email delivery
- Requires SMTP configuration

**Slack Integration**:
- Post dashboards to Slack channels
- Scheduled or on-demand

### Metabase Models

Create logical layers in Metabase:

1. Admin → Models
2. Save complex SQL as a Model
3. Business users query Models (not raw tables)

Similar to dbt models, but defined in Metabase UI.

---

## Next Steps

<div class="grid cards" markdown>

-   :material-plus-box: **Creating Dashboards**

    ---

    Step-by-step guide to building interactive dashboards in Metabase.

    [:octicons-arrow-right-24: Creating Dashboards](creating-dashboards.md)

-   :material-code-tags: **SQL Queries**

    ---

    Learn to write SQL queries for DuckDB in Metabase.

    [:octicons-arrow-right-24: SQL Queries Guide](sql-queries.md)

-   :material-table-sync: **Transformations**

    ---

    Create analytics-ready tables with dbt for Metabase.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-book-open-outline: **Metabase Documentation**

    ---

    Explore official Metabase resources and advanced features.

    [:octicons-arrow-right-24: Metabase Docs](https://www.metabase.com/docs/latest/)

</div>
