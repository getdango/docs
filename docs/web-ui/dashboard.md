# Dashboard Page

The landing page showing platform health, services, and recent activity.

---

## Overview

The Dashboard (`/`) is the first page you see after logging in. It provides a quick summary of your platform's health, service availability, and recent activity. The page receives real-time updates via WebSocket, so status changes appear without refreshing.

## Initial Sync Progress

On first deployment, a progress banner appears at the top of the dashboard showing the initial sync status. The banner tracks each source as it syncs, runs dbt docs, and sets up Metabase.

The banner shows:

- **Current phase** — syncing sources, building dbt docs, or configuring Metabase
- **Progress bar** — percentage complete with "Source X/Y: source_name" label
- **Completed sources** — listed as they finish
- **Failed sources** — shown with error messages in amber text

Two action buttons are available during the initial sync:

- **Skip** (yellow) — skip the current source and move to the next one
- **Cancel** (red) — cancel the entire initial sync process

The banner turns green on completion, red on failure, and yellow if cancelled. Click the **X** button to dismiss it once done.

## OAuth Expiry Warning

If any OAuth tokens are expiring soon, a yellow banner appears below the header:

> **OAuth tokens expiring soon** — Manage credentials ->

Click the link to navigate to [Secrets & Credentials](secrets-admin.md) to reconnect expiring sources.

## Platform Health Widget

A card on the left side shows overall platform health status. The left border color indicates the state:

- **Green** — platform healthy
- **Yellow** — warnings detected
- **Red** — critical issues

Click the card to navigate to the [Health page](health-logs.md) for full details.

## Service Status Cards

A 4-column grid shows the status of core services:

| Card | Service | Link |
|------|---------|------|
| **dbt Docs** | Data documentation server | Opens `/dbt-docs` in a new tab |
| **DuckDB** | Data warehouse database | (no link — status only) |
| **Metabase** | Dashboarding and query tool | Opens `/metabase` in a new tab |
| **Activity Logs** | Platform event log | Opens the [Logs page](health-logs.md#logs-page) |

Each card shows a colored status dot:

- **Green** — service is running
- **Red** — service is down or unreachable
- **Gray** — status unknown or loading

## Recent Activity

A table at the bottom of the dashboard shows the last 10 platform events:

| Column | Description |
|--------|-------------|
| **Level** | Event severity (Info, Success, Warning, Error) |
| **Source** | Component that generated the event |
| **Time** | When the event occurred |
| **Message** | Event description |

Click **View Full Logs** in the header to open the [Logs page](health-logs.md#logs-page) with the complete event history.

??? info "How it works"
    - **Dashboard page:** `GET /` renders the dashboard template with version and cloud detection context.
    - **Health data:** The platform health widget fetches from `GET /api/health/platform`.
    - **Service status:** The service cards check `GET /api/status` for API, DuckDB, Metabase, and dbt Docs availability.
    - **Initial sync:** Status comes from `GET /api/initial-sync/status` on load, then via WebSocket `initial_sync_progress` events. Skip and cancel actions use `POST /api/initial-sync/skip-source` and `POST /api/initial-sync/cancel`.
    - **WebSocket:** The dashboard connects to `/ws` for real-time event streaming. A connection indicator in the header shows connectivity status.

## Troubleshooting

**Dashboard shows no data**
:   The platform may still be starting up. Services take a few seconds to initialize after `dango start`. Refresh the page after 5-10 seconds.

**Service cards show gray dots**
:   The status check is still loading or the service hasn't started yet. DuckDB and Metabase may take longer to initialize on first run.

**Initial sync banner won't dismiss**
:   Click the **X** button in the top-right corner of the banner. If the banner shows a failed state, you can still dismiss it and re-run failed syncs individually from the [Sources page](sources.md).

**WebSocket disconnected**
:   The connection indicator in the header shows "Connecting..." when the WebSocket is not connected. The page automatically attempts to reconnect. If it persists, check that the Dango server is still running.

## Related Pages

- [Health & Logs](health-logs.md) — detailed health metrics and activity logs
- [Sources Page](sources.md) — manage and sync data sources
- [Web UI Overview](web-ui-overview.md) — navigation and feature summary
