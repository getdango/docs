# Platform Tour

What you get when you run `dango start` — a quick tour of the web interface.

---

## Starting Dango

After [installation](installation.md) and [initialization](quick-start.md), start the platform:

```bash
dango start
```

Open **http://localhost:8800** in your browser. Log in with the admin credentials you set during `dango init`.

## Web UI Pages

The top navigation bar gives you access to all platform features:

### Dashboard (Overview)

**Route:** `/`

The landing page shows system health at a glance — service status for DuckDB, Metabase, and the scheduler, recent sync activity, and quick stats on sources, models, and schedules. This is your starting point for monitoring the platform.

:material-arrow-right: [Dashboard page details](../web-ui/dashboard.md)

### Sources

**Route:** `/sources`

Manage all your data sources. View sync status, trigger manual syncs with **Sync Now**, upload CSV files, and see detailed per-source history. Each source shows its last sync time, row counts, and current state.

:material-arrow-right: [Sources page details](../web-ui/sources.md)

### Models

**Route:** `/models`

Browse your dbt transformation models. See which models are available, their status, and run individual models on demand. This is the web equivalent of `dango run`.

:material-arrow-right: [Models page details](../web-ui/models.md)

### Schedules

**Route:** `/schedules`

View automated sync schedules. See which sources have schedules, their cron expressions, next run times, and execution history. Manually trigger runs from the UI. Schedule configuration (adding, editing, removing) is managed via the CLI.

:material-arrow-right: [Schedules page details](../web-ui/schedules.md)

### Catalog

**Route:** `/catalog`

Explore your data warehouse. Browse tables and columns, view data profiling statistics, and trace data lineage from source to dashboard. The catalog auto-updates after each sync.

:material-arrow-right: [Catalog page details](../web-ui/catalog.md)

### Notebooks

**Route:** `/notebooks`

Launch and manage [Marimo](https://marimo.io/) notebooks for Python-based data analysis. Create notebooks from templates, open them in the browser, and work directly with your DuckDB warehouse data.

:material-arrow-right: [Notebooks page details](../web-ui/notebooks.md)

### Monitoring

**Route:** `/monitoring`

Track data quality metrics and dbt test results. View freshness scores, schema drift alerts, and PII scan results across all sources.

:material-arrow-right: [Monitoring page details](../web-ui/monitoring-page.md)

### Metabase (Dashboards & Query)

The **Dashboards** and **Query** nav items open [Metabase](https://www.metabase.com/) in a new tab — Dango's embedded BI tool for creating dashboards and running SQL queries. Metabase connects directly to your DuckDB warehouse.

:material-arrow-right: [Dashboards overview](../dashboards/index.md)

### Settings & Admin

Click the **gear icon** (top-right) to access:

- **Account Settings** — change your password, enable two-factor auth
- **User Management** (admin only) — create users, assign roles
- **Secrets & Credentials** (admin only) — manage API keys and OAuth tokens
- **Activity Logs** — audit trail of all platform actions
- **Health** — detailed service health and system info

:material-arrow-right: [Secrets & Admin details](../web-ui/secrets-admin.md) | [Health & Logs details](../web-ui/health-logs.md)

## What's Next?

- **[Quick Start](quick-start.md)** — add your first source and sync data
- **[Your First Dashboard](first-dashboard.md)** — build a dashboard from your data
- **[Web UI Reference](../web-ui/index.md)** — detailed docs for every page
