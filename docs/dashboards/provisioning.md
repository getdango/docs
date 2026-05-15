# Dashboard Provisioning

Provision a pre-built monitoring dashboard in Metabase with a single command. The "Data Pipeline Health" dashboard gives you instant visibility into sync status, data freshness, test results, and row count trends.

---

## Overview

`dango dashboard provision` creates a Metabase dashboard with 6 visualizations covering pipeline health. It authenticates with Metabase, creates individual cards (questions), assembles them into a dashboard with a grid layout, and returns the dashboard URL.

---

## Quick Start

=== "Local"

    ```bash
    dango dashboard provision
    ```

    Uses `http://localhost:3000` by default.

=== "Cloud"

    ```bash
    dango dashboard provision --url https://your-domain.com
    ```

    Provide the public URL of your Metabase instance.

You'll be prompted for the admin password:

```
Password: ********

✓ Dashboard provisioned successfully!

  Dashboard: Data Pipeline Health
  URL: http://localhost:3000/dashboard/1
  Cards created:
    • Pipeline Health Score
    • dbt Test Results
    • Data Sources Overview
    • Sync History (Last 7 Days)
    • Row Counts Over Time
    • Data Freshness by Source
```

---

## Command Options

```bash
dango dashboard provision [--url URL] [--username EMAIL] [--password PASSWORD]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | `http://localhost:3000` | Metabase instance URL |
| `--username` | Auto-detected | Metabase admin email |
| `--password` | Prompted | Metabase admin password (entered interactively) |

### Username Resolution

The admin username is resolved in this order:

1. Explicit `--username` flag
2. `DANGO_ADMIN_EMAIL` environment variable
3. Active admin user from the auth database
4. Fallback: `admin@example.com`

---

## Dashboard Contents

The provisioned dashboard contains 6 cards arranged in a grid:

### Layout

```
┌──────────────────┬──────────────────┬──────────────────┐
│ Pipeline Health  │ dbt Test Results │ Data Sources     │
│ Score (gauge)    │ (scalar)         │ Overview (table) │
│ 6×4              │ 6×4              │ 6×4              │
├────────────────────────────┬────────────────────────────┤
│ Sync History 7 Days       │ Row Counts Over Time       │
│ (line chart) 9×6          │ (area chart) 9×6           │
├────────────────────────────┴────────────────────────────┤
│ Data Freshness by Source (table) 18×4 — full width     │
└─────────────────────────────────────────────────────────┘
```

### Cards

| Card | Visualization | Position | Description |
|------|--------------|----------|-------------|
| Pipeline Health Score | Gauge | Row 0, Col 0 (6×4) | Overall health score 0-100 |
| dbt Test Results | Scalar | Row 0, Col 6 (6×4) | Count of failed tests vs total |
| Data Sources Overview | Table | Row 0, Col 12 (6×4) | Source name, type, enabled status |
| Sync History (Last 7 Days) | Line chart | Row 4, Col 0 (9×6) | Sync activity per day |
| Row Counts Over Time | Area chart | Row 4, Col 9 (9×6) | Data growth trend over 30 days |
| Data Freshness by Source | Table | Row 10, Col 0 (18×4) | Row count and last update per source |

Each card executes a native SQL query against the DuckDB database connected to Metabase.

---

## Customizing the Dashboard

After provisioning, the dashboard is a standard Metabase dashboard. You can:

- **Edit the layout** — drag and resize cards in Metabase
- **Add cards** — create new questions and add them to the dashboard
- **Modify queries** — click any card to edit its underlying SQL
- **Add filters** — add interactive filter widgets to the dashboard
- **Change visualizations** — switch chart types (e.g., line to bar)

!!! tip "Save Your Customizations"
    After customizing the dashboard in Metabase, run `dango metabase save` to export it as YAML. This lets you version-control your changes and restore them later. See [Save & Load](save-load.md).

---

## Re-Provisioning

Running `dango dashboard provision` again creates a new dashboard — it does not update the existing one. If you want a fresh dashboard:

1. Delete the old dashboard in Metabase
2. Run `dango dashboard provision` again

For updating an existing dashboard, edit it directly in the Metabase UI instead.

---

## Troubleshooting

### Authentication Failed

```
Error: Authentication failed. Check your credentials.
```

Verify your Metabase admin email and password. The Metabase admin password was auto-generated during `dango start` and stored in `.dango/metabase.yml`. This is separate from the Dango admin password set during `dango init`.

=== "Local"

    ```bash
    # Check which admin email is configured
    dango user list
    ```

=== "Cloud"

    ```bash
    dango user list
    # Or check the environment variable
    echo $DANGO_ADMIN_EMAIL
    ```

### DuckDB Database Not Found

```
Error: No DuckDB database configured in Metabase.
```

Metabase needs a DuckDB connection configured during setup. This is normally done automatically by `dango start`. If the connection is missing:

1. Verify Metabase is running: `dango status`
2. Check if DuckDB is connected in the Metabase admin panel under **Admin > Databases**
3. Re-run setup if needed: `dango start`

### Empty Dashboard

The dashboard cards show "No results" if there's no data in DuckDB yet:

1. Run `dango sync` to load data
2. Run `dango run` to build dbt models
3. Run `dango metabase refresh` to sync the schema
4. Open the dashboard — cards should now show data

---

## Next Steps

<div class="grid cards" markdown>

-   **[Save & Load](save-load.md)**

    Export dashboard customizations as YAML for version control.

-   **[Creating Dashboards](creating-dashboards.md)**

    Build custom dashboards from scratch in Metabase.

-   **[SQL Queries](sql-queries.md)**

    Write native SQL queries against DuckDB in Metabase.

-   **[Metabase Overview](metabase-overview.md)**

    Learn how Dango integrates with Metabase.

</div>
