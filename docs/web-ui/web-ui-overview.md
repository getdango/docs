# Web UI Overview

A tour of the Dango web interface — navigation, pages, and key features.

---

## Overview

The Dango Web UI is a FastAPI-powered web application with an [Alpine.js](https://alpinejs.dev/) and [Tailwind CSS](https://tailwindcss.com/) frontend. It provides real-time monitoring, source management, data exploration, and administration for your data platform.

**Access the Web UI** at `http://localhost:8800` after starting Dango:

```bash
dango start
```

Authentication is enabled by default. Log in with the admin credentials set during `dango init`.

## Navigation

### Top Navigation Bar

The main nav bar has 9 items plus external links:

| Nav Item | Route | Description |
|----------|-------|-------------|
| **Overview** | `/` | [Dashboard](dashboard.md) — health, services, activity |
| **Sources** | `/sources` | [Sources](sources.md) — data source management and sync |
| **Models** | `/models` | [Models](models.md) — dbt models list and execution |
| **Schedules** | `/schedules` | [Schedules](schedules.md) — schedule status and history |
| **Catalog** | `/catalog` | [Catalog](catalog.md) — data catalog, profiling, lineage |
| **Query** | `/query` | Opens Metabase query editor (new tab) |
| **Dashboards** | `/metabase` | Opens Metabase dashboards (new tab) |
| **Notebooks** | `/notebooks` | [Notebooks](notebooks.md) — Marimo notebook management |
| **Monitoring** | `/monitoring` | [Monitoring](monitoring-page.md) — metrics and dbt tests |

### Gear Menu

The gear icon (top-right) opens a dropdown with settings and utility pages:

| Item | Route | Access |
|------|-------|--------|
| **Account Settings** | `/settings/account` | All users |
| **User Management** | `/settings/users` | Admin only |
| **Secrets & Credentials** | `/settings/secrets` | Admin only |
| **Activity Logs** | `/logs` | All users |
| **Health** | `/health` | All users |
| **Logout** | (POST) | All users |

### Mobile

On small screens, the navigation collapses into a hamburger menu with all nav items, user info, and settings links.

## Pages at a Glance

| Page | Route | Purpose |
|------|-------|---------|
| [Dashboard](dashboard.md) | `/` | Health summary, service status, recent activity |
| [Sources](sources.md) | `/sources` | Source table, sync actions, CSV upload, details |
| [Models](models.md) | `/models` | dbt model list, run individual models |
| [Schedules](schedules.md) | `/schedules` | Schedule status, history, trigger, notifications |
| [Catalog](catalog.md) | `/catalog` | Data catalog, column profiling, lineage DAG |
| [Monitoring](monitoring-page.md) | `/monitoring` | Metric monitors, drill-downs, dbt test results |
| [Notebooks](notebooks.md) | `/notebooks` | Create and manage Marimo notebooks |
| [Health](health-logs.md) | `/health` | Platform health metrics, disk, capacity, OAuth |
| [Logs](health-logs.md#logs-page) | `/logs` | Searchable activity logs with filters |
| [Secrets](secrets-admin.md) | `/settings/secrets` | Environment variables, OAuth credentials |
| [Users](secrets-admin.md#user-management) | `/settings/users` | User accounts and roles (admin) |
| [Account](secrets-admin.md#account-settings) | `/settings/account` | Profile, password, sessions, API keys, 2FA |
| [Login](secrets-admin.md#login) | `/login` | Email/password + optional TOTP |
| [Invite](secrets-admin.md#accept-invite) | `/invite/{token}` | New user password setup |
| Query | `/query` | Metabase SQL editor (external link) |
| Dashboards | `/metabase` | Metabase dashboards (external link) |
| dbt Docs | `/dbt-docs` | dbt documentation (external link) |

## Getting Started

### Starting the Web UI

```bash
dango start
```

Open your browser to **http://localhost:8800**. On cloud deployments, use your server's domain (e.g., `https://data.example.com`).

### First Deploy Banner

On first startup after initial configuration, the [Dashboard](dashboard.md) shows an **Initial Sync Progress** banner that tracks each source as it syncs for the first time, builds dbt docs, and configures Metabase.

### Cloud Login

On cloud deployments, the login page appears immediately. Enter the admin email and password configured during setup. If 2FA is enabled, a second step prompts for the authenticator code.

## Access & Authentication

Authentication is enabled by default for both local and cloud deployments.

**Local defaults:**

- 365-day session duration
- 24-hour idle timeout
- Login required for all pages

**Cloud defaults:**

- 30-day session duration
- 60-minute idle timeout
- HTTPS required (via Caddy auto-TLS)
- 2FA recommended (a yellow banner appears on every page until enabled)

### Roles

| Role | Access |
|------|--------|
| **Admin** | Full access — manage users, secrets, all features |
| **Editor** | Create/edit sources, run models, manage notebooks |
| **Viewer** | Read-only access to all data pages |

### API Keys

For programmatic access, create API keys from [Account Settings](secrets-admin.md#api-keys). Pass the key in the `Authorization` header:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8800/api/sources
```

## Real-Time Updates

The Web UI connects to a WebSocket at `/ws` for real-time event streaming. Events include:

- **Sync progress** — sync started, completed, failed
- **dbt runs** — model execution progress and results
- **File uploads** — CSV upload notifications
- **Lock events** — notebook lock revocations
- **Initial sync** — first-deploy progress updates

A connection indicator in the page header shows WebSocket status. The UI automatically reconnects if the connection drops.

## External Links

Three nav items link to external services running alongside Dango:

- **Query** → Metabase SQL editor for ad-hoc queries against your DuckDB warehouse
- **Dashboards** → Metabase dashboard builder for charts and reports
- **dbt Docs** → auto-generated dbt documentation site (served at `/dbt-docs`)

These open in new browser tabs and use session bridging for seamless authentication with Metabase.

## Troubleshooting

**Web UI won't load**
:   Check that Dango is running with `dango status`. Verify the port (default 8800) isn't in use by another process. Try `lsof -i :8800` to check.

**Redirected to login but credentials don't work**
:   On first setup, the admin password is set during `dango init`. If you've forgotten it, reset with `dango auth reset-password`.

**WebSocket shows "Connecting..." and never connects**
:   Check that nothing is blocking WebSocket connections (some corporate proxies strip WebSocket upgrades). The UI still works without WebSocket — it just won't show real-time updates.

**Pages load slowly**
:   Large databases (many tables/models) can slow the catalog and health pages. The initial load fetches all metadata; subsequent navigation uses cached data.

## Next Steps

<div class="grid cards" markdown>

-   :material-view-dashboard-variant: **Dashboard**

    ---

    Health widgets, service cards, and activity log.

    [:octicons-arrow-right-24: Dashboard Page](dashboard.md)

-   :material-database-outline: **Sources**

    ---

    Manage data sources, trigger syncs, upload files.

    [:octicons-arrow-right-24: Sources Page](sources.md)

-   :material-book-search: **Catalog**

    ---

    Browse models, columns, lineage, and profiling.

    [:octicons-arrow-right-24: Catalog Page](catalog.md)

-   :material-shield-key: **Secrets & Admin**

    ---

    Environment variables, OAuth, users, and 2FA.

    [:octicons-arrow-right-24: Secrets & Admin](secrets-admin.md)

</div>
