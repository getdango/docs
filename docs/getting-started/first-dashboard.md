# Your First Dashboard

Build your first Metabase dashboard after running the [Quick Start](quick-start.md).

!!! note "Prerequisites"
    Before starting, make sure you have:

    - Completed the [Quick Start](quick-start.md) (at least through Step 4)
    - The platform running (`dango start`)
    - At least one data source synced (`dango sync`)

---

## Step 1: Open Metabase

The easiest way to access Metabase is through the Dango Web UI, which handles authentication automatically.

1. Open `http://localhost:8800` in your browser
2. Log in with your admin password (set during `dango init`)
3. Click **"Open Metabase"** in the sidebar

The Web UI uses an SSO bridge to log you into Metabase automatically — no separate Metabase credentials needed.

??? info "Direct Metabase access (alternative)"
    You can also access Metabase directly at `http://localhost:3000`. Use the bootstrap credentials:

    - **Email:** `admin@dango.local`
    - **Password:** `dangolocal123`

    The SSO bridge approach (via the Web UI) is recommended because it keeps authentication centralized.

!!! note "First-time startup"
    Metabase takes 2–3 minutes to initialize on its first launch. If you see a loading screen, wait for it to complete. Check progress with `docker ps` — the container health will show as "healthy" when ready.

---

## Step 2: Explore Your Data

Once Metabase loads, you'll see the home screen. Your DuckDB database is already connected.

### Browse Your Schemas

Click the **Browse** icon (grid icon) in the left sidebar or navigate to **Browse → Tables** to see your data organized by schema:

| Schema | Contents | Description |
|--------|----------|-------------|
| `raw_*` | Source data as-is | Immutable copy from dlt, one schema per source |
| `staging` | Clean data | Deduplicated, renamed columns, type-cast |
| `intermediate` | Business logic | Joins and calculations across sources |
| `marts` | Final metrics | Ready for dashboards and reporting |

Start by exploring the **staging** schema — it contains clean, well-named tables ready for querying.

Learn more about data layers in [Data Layers](../core-concepts/data-layers.md).

---

## Step 3: Create a Question

In Metabase, a "question" is a saved query. You can create one using the visual builder or SQL.

### Visual Query Builder (No SQL Required)

1. Click **+ New** in the top-right corner
2. Select **Question**
3. Pick your database (DuckDB) and a table (e.g., `staging > stg_sales_data`)
4. Add filters, groupings, or summaries using the visual builder
5. Click **Visualize** to see results
6. Click **Save** to keep the question

### Custom SQL Query

For more control, write SQL directly:

1. Click **+ New** → **SQL query**
2. Make sure **DuckDB** is selected as the database
3. Write your query:

```sql
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue
FROM staging.stg_sales_data
WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY 1
ORDER BY 1 DESC
```

4. Click **Run** (or press Ctrl+Enter) to execute
5. Switch visualization types using the **Visualization** button (bar chart, line chart, table, etc.)
6. Click **Save** to keep the question

!!! tip "Autocomplete"
    Metabase's SQL editor provides autocomplete for table names, column names, and SQL keywords. Press Tab to accept suggestions.

---

## Step 4: Build a Dashboard

Now combine multiple questions into a dashboard.

1. Click **+ New** → **Dashboard**
2. Give it a name (e.g., "Sales Overview")
3. Click **Save**

### Add Questions to the Dashboard

1. Click the **pencil icon** (edit mode) in the top-right
2. Click **+ Add** → **Saved question**
3. Select the questions you created in Step 3
4. Drag and resize cards to arrange your layout
5. Click **Save**

### Add a Date Filter

Filters let viewers change the time range without editing queries:

1. In edit mode, click **Filter** in the top bar
2. Select **Date picker**
3. Connect it to the date column in each card (Metabase will suggest matches)
4. Click **Save**

Now anyone viewing the dashboard can filter by date range.

---

## Step 5: Save Your Configuration

Export your Metabase dashboards and questions so you can restore them later or share with teammates:

```bash
# Save all dashboards, questions, and collections
dango metabase save

# Save specific collections only
dango metabase save --collections "Sales,Marketing"

# Save everything including personal collections
dango metabase save --all
```

This exports to the `metabase/` directory in your project. To restore on another machine or after a reset:

```bash
dango metabase load
```

Learn more in [Save & Load](../dashboards/save-load.md).

---

## Refreshing Data

### After a Sync

When you run `dango sync`, your data in DuckDB is updated. Metabase picks up data changes automatically the next time you run a question or refresh a dashboard.

### After Schema Changes

If you add new sources or dbt models, Metabase needs to discover the new tables:

```bash
dango metabase refresh
```

This tells Metabase to re-scan the DuckDB schema and make new tables available for querying.

---

## Instant Pipeline Dashboard

Want a pre-built dashboard without creating questions manually? Use the provisioning command:

```bash
dango dashboard provision
```

This creates a **Data Pipeline Health** dashboard in Metabase with:

- Sync status and history for all sources
- Row counts and freshness metrics
- Error tracking and alerts

Learn more in [Dashboard Provisioning](../dashboards/provisioning.md).

---

## Troubleshooting

### Metabase shows a loading screen

Metabase takes 2–3 minutes to start on first launch. Check container status:

```bash
docker ps
```

Look for the Metabase container — when health shows "healthy", it's ready.

### No tables visible in Metabase

Make sure you've synced at least one source:

```bash
dango sync
dango metabase refresh
```

### SQL query returns an error

- Check that you're querying the correct schema (`staging.*`, `marts.*`, not `raw_*` directly)
- Verify column names by browsing the table in Metabase first
- Use `SHOW TABLES` in Metabase's SQL editor to list all available tables

### Dashboard shows "No results"

- Verify the date filter range includes your data
- Check that the underlying questions return data when run individually
- Re-sync your source if the data is stale: `dango sync --source <name>`

### Can't access Metabase through Web UI

Make sure the platform is running:

```bash
dango status
```

If Metabase isn't responding, restart:

```bash
dango stop
dango start
```

---

## Next Steps

<div class="grid cards" markdown>

- :material-view-dashboard:{ .lg .middle } **[Creating Dashboards](../dashboards/creating-dashboards.md)**

    ---

    Advanced dashboard techniques, filters, and layouts

- :material-database-search:{ .lg .middle } **[SQL Queries](../dashboards/sql-queries.md)**

    ---

    Write powerful SQL queries in Metabase

- :material-content-save:{ .lg .middle } **[Save & Load](../dashboards/save-load.md)**

    ---

    Export and restore your Metabase configuration

- :material-layers:{ .lg .middle } **[Data Layers](../core-concepts/data-layers.md)**

    ---

    Understand raw, staging, intermediate, and marts schemas

</div>
