# Web UI

Monitor and manage your data platform through a modern web interface.

---

## Overview

The Dango Web UI provides a visual interface for managing your data platform. Access real-time sync monitoring, source management, data exploration, and system health checks through your browser at **http://localhost:8800**.

**Key Features**:

- **Real-time monitoring** with WebSocket updates
- **Source management** with sync triggers and CSV file uploads
- **Data catalog** with column profiling, lineage, and impact analysis
- **Health dashboards** for system status, disk usage, and OAuth tokens
- **Notebook management** for Marimo data exploration notebooks
- **Authentication** with role-based access, 2FA, and API keys

---

## Getting Started

### Launch Web UI

Start your Dango platform:

```bash
dango start
```

Open your browser:

**http://localhost:8800**

Log in with the admin credentials you set during `dango init`. On cloud deployments, use your server's domain (e.g., `https://data.example.com`).

### First Steps

1. **Check the dashboard** — view service status and platform health
2. **Browse your sources** — see configured data sources and sync status
3. **Trigger a sync** — click Sync Now on a source to load data
4. **Upload a CSV file** — add files through the source detail modal
5. **Explore the catalog** — browse tables, columns, and lineage

---

## Web UI Guides

<div class="grid cards" markdown>

-   :material-view-dashboard: **Web UI Overview**

    ---

    Introduction to the Web UI with features, navigation, and capabilities.

    - Dashboard and navigation
    - Real-time monitoring features
    - WebSocket integration
    - Authentication and roles
    - External links (Metabase, dbt Docs)

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

-   :material-view-dashboard-variant: **Dashboard Page**

    ---

    Health widgets, service cards, and activity log.

    [:octicons-arrow-right-24: Dashboard Page](dashboard.md)

-   :material-database-outline: **Sources Page**

    ---

    View and manage data sources, trigger syncs, inspect details.

    [:octicons-arrow-right-24: Sources Page](sources.md)

-   :material-file-tree: **Models Page**

    ---

    Browse and run dbt models from the web interface.

    [:octicons-arrow-right-24: Models Page](models.md)

-   :material-heart-pulse: **Health & Logs**

    ---

    DuckDB capacity, service status, and activity logs.

    [:octicons-arrow-right-24: Health & Logs](health-logs.md)

-   :material-book-search: **Catalog Page**

    ---

    Model browser, lineage, profiling, and impact analysis.

    [:octicons-arrow-right-24: Catalog Page](catalog.md)

-   :material-chart-line: **Monitoring Page**

    ---

    Metric results, trends, and dbt test outcomes.

    [:octicons-arrow-right-24: Monitoring Page](monitoring-page.md)

-   :material-clock-outline: **Schedules Page**

    ---

    Schedule configurations and execution history.

    [:octicons-arrow-right-24: Schedules Page](schedules.md)

-   :material-notebook: **Notebooks Page**

    ---

    Create, open, and manage Marimo notebooks.

    [:octicons-arrow-right-24: Notebooks Page](notebooks.md)

-   :material-shield-key: **Secrets & Admin**

    ---

    Environment variables, OAuth credentials, and user administration.

    [:octicons-arrow-right-24: Secrets & Admin](secrets-admin.md)

</div>

---

## Quick Actions

Common tasks via the Web UI:

### Sync a Source

1. Go to the [Sources page](sources.md)
2. Find the source in the table
3. Click the **Sync Now** button
4. Watch the status badge update in real time

### Upload a CSV File

1. Go to the [Sources page](sources.md)
2. Click on a CSV or local_files source
3. Use the file upload form in the modal to select files
4. Click **Upload File**, then **Sync Now** to process

### Monitor Sync Progress

1. Watch toast notifications for sync start/complete events
2. Check the [Dashboard](dashboard.md) for recent activity
3. Go to [Logs](health-logs.md#logs-page) for detailed event history
4. Filter by source or log level to find specific events

### Check System Health

1. Go to the [Health page](health-logs.md) from the gear menu
2. Review the status banner and metric cards
3. Check for sync or dbt failures in Recent Issues
4. Review OAuth token health for expiring credentials

---

## Web UI vs CLI

The Web UI and CLI provide complementary interfaces to your Dango platform.

| Feature | Web UI | CLI |
|---------|--------|-----|
| **Sync sources** | Click "Sync Now" button | `dango sync` |
| **Upload CSV** | File upload in source modal | Copy to source directory |
| **Run models** | Click "Run" on model row | `dbt run --select model` |
| **Monitor progress** | Real-time WebSocket updates | Terminal output |
| **View health** | Health page with metrics | `dango status` |
| **Add sources** | Not available (CLI only) | `dango source add` |
| **Configure schedules** | View only | `dango schedule add` |
| **Manage users** | View only | `dango auth add-user` |

**When to use Web UI**:

- Visual monitoring and health dashboards
- Uploading CSV files via browser
- Exploring data catalog and lineage
- Quick ad-hoc sync triggers
- Managing notebooks

**When to use CLI**:

- Adding and configuring sources
- Managing schedules and users
- Automation and scripting
- CI/CD pipelines
- SSH access to remote servers

**Use both together**: Keep the Web UI open in a browser tab for monitoring while running CLI commands for configuration and automation.

---

## Common Workflows

### Morning Data Check

1. Open the [Dashboard](dashboard.md) — check the health widget status
2. Review [Recent Activity](dashboard.md#recent-activity) for overnight sync results
3. Go to [Health](health-logs.md) if any warnings — check disk, OAuth tokens
4. Browse [Sources](sources.md) — verify all sources synced successfully

### Investigate a Sync Failure

1. Go to [Sources](sources.md) — find the source with red status
2. Click the source to open the detail modal
3. Read the error message in the red alert box
4. Check [Logs](health-logs.md#logs-page) — filter by Error level and source name
5. Fix the issue (credentials, network, etc.) and click **Sync Now**

### Explore Your Data

1. Open the [Catalog](catalog.md) — browse models and source tables
2. Use the search bar to find specific tables or columns
3. Click a model to view column profiles, tests, and SQL
4. Switch to the Lineage view to understand data flow
5. Click **Query** in the nav to open Metabase for SQL queries

---

## Security

Authentication is enabled by default on both local and cloud deployments.

- **Local**: 365-day sessions, 24-hour idle timeout
- **Cloud**: 30-day sessions, 60-minute idle timeout, HTTPS via Caddy

Set up [two-factor authentication](secrets-admin.md#two-factor-authentication-2fa) for additional security, especially on cloud deployments. Create [API keys](secrets-admin.md#api-keys) for programmatic access.

---

## Next Steps

<div class="grid cards" markdown>

-   :material-view-dashboard: **Web UI Overview**

    ---

    Explore all Web UI features and capabilities.

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

-   :material-database-outline: **Sources Page**

    ---

    Learn how to view and manage data sources.

    [:octicons-arrow-right-24: Sources Page](sources.md)

-   :material-book-search: **Catalog Page**

    ---

    Browse your data catalog with lineage and profiling.

    [:octicons-arrow-right-24: Catalog Page](catalog.md)

-   :material-console: **CLI Alternative**

    ---

    Explore CLI commands for the same functionality.

    [:octicons-arrow-right-24: CLI Reference](../cli/cli-reference.md)

</div>
