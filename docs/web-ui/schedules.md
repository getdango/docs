# Schedules Page

View schedule configurations, execution history, and notification settings.

---

## Overview

The Schedules page (`/schedules`) shows all configured sync and dbt schedules with their execution status and history. You can view status, browse history, and manually trigger runs, but schedule configuration (adding, editing, removing schedules) is managed via the CLI.

Navigate to **Schedules** in the top navigation bar.

!!! info "CLI-managed"
    Schedules are configured with `dango schedule add` and stored in `.dango/schedules.yml`. The web UI displays schedule status and history but does not modify the schedule configuration. See the [Scheduling guide](../scheduling-monitoring/scheduled-syncs.md) for setup instructions.

## Schedules Table

The main table lists all configured schedules:

| Column | Description |
|--------|-------------|
| **Name** | Schedule name (clickable — expands execution history). |
| **Type** | Schedule type badge — blue for `sync` schedules, purple for `dbt` schedules. |
| **Sources** | Comma-separated list of sources included in the schedule. |
| **Cron** | Human-readable schedule frequency (e.g., "Every hour", "Daily 6 AM", "Weekly Mon midnight"). Raw cron expression shown if no friendly mapping exists. |
| **Next Run** | Relative time until the next scheduled execution (e.g., "in 5 min", "in 2h"). |
| **Status** | Last run status badge (see below) or "running" with pulsing animation. |
| **Enabled** | "Yes" (green) or "No" (gray). |
| **Actions** | **Trigger** button (editor/admin only) to manually run the schedule. |

### Status Badges

| Status | Badge Color | Meaning |
|--------|-------------|---------|
| **success** / **completed** | Green | Last run completed without errors |
| **failed** | Red | Last run encountered an error |
| **running** | Blue (pulsing) | Schedule is currently executing |
| **cancelled** | Yellow | Last run was cancelled |
| **timeout** | Gray | Last run timed out |

## Execution History

Click a **schedule name** in the table to expand its execution history. The expandable row shows:

**Recent Executions** — a table of past runs:

| Column | Description |
|--------|-------------|
| **Started** | Relative time (e.g., "5 min ago", "2h ago") |
| **Duration** | Run duration (e.g., "45s", "3m 15s") |
| **Status** | Color-coded status badge |
| **Error** | Error message (truncated) for failed runs |
| **Actions** | **Re-run** button on failed runs (editor/admin only) |

Click the schedule name again to collapse the history.

## Unscheduled Sources

A collapsible section below the main table shows sources that have no schedule configured. Click the header to expand.

- A yellow badge shows the count of unscheduled sources
- Each source has a **Sync Now** button for manual one-off syncs

When all sources are scheduled, the section shows "All sources are scheduled."

## Notifications

The Notifications section shows webhook configuration for schedule events:

### Not Configured

If no webhooks are set up:

> Not configured. Add webhooks in `.dango/schedules.yml`.

### Configured Webhooks

When webhooks are configured, each webhook displays:

- **Name** and format (e.g., "slack", "custom")
- **URL** (truncated for long URLs)

### Notification Toggles

Three event toggles show which events trigger notifications:

- **Failures** — On/Off (green/gray indicator)
- **Success** — On/Off
- **Stale** — On/Off

!!! note "Global toggles"
    These settings apply to all webhooks. Per-webhook event filtering is not currently supported.

### Test Notification

Click **Test Notification** (editor/admin only) to send a test message to all configured webhooks. This verifies your webhook URLs and formatting are correct.

## Trigger Modal

Click **Trigger** on a schedule row (or **Re-run** on a failed history entry) to open the trigger modal:

- **Full refresh** checkbox — run all sources from scratch instead of incrementally
- **Start Date** (optional) — restrict sync to data after this date
- **End Date** (optional) — restrict sync to data before this date

Click **Trigger Now** to start the schedule immediately. A success message confirms the schedule was triggered.

??? info "How it works"
    - **List schedules:** `GET /api/schedules` returns all schedules with name, type, cron, sources, enabled status, next run time, and last run result.
    - **Schedule detail:** `GET /api/schedules/{name}` returns full schedule config with the last 10 execution records.
    - **Execution history:** `GET /api/schedules/{name}/history?limit=30` returns paginated execution records with optional status, date range, and offset filters.
    - **Trigger:** `POST /api/schedules/{name}/trigger` triggers the schedule immediately with optional full_refresh, start_date, and end_date parameters.
    - **Unscheduled sources:** `GET /api/sources/unscheduled` returns source names not assigned to any schedule.
    - **Notifications config:** `GET /api/notifications/config` returns webhook list and event toggle settings.
    - **Test notification:** `POST /api/notifications/test` sends a test payload to all configured webhooks.
    - **WebSocket events:** `sync_started`, `sync_completed`, `sync_failed`, `dbt_started`, `dbt_completed`, `dbt_failed` events update the running status in real time.

## Troubleshooting

**Schedule shows "No" for Enabled**
:   The schedule is disabled in `.dango/schedules.yml`. Enable it with `dango schedule enable <name>` or edit the YAML file directly.

**Next Run shows "—"**
:   The scheduler may not be running, or the schedule is disabled. Check that Dango is running with `dango status`.

**Triggered schedule doesn't start**
:   The scheduler service must be running. If the scheduler is unavailable, the trigger returns a "Scheduler is not available" error. Restart Dango with `dango start`.

## Related Pages

- [Sources Page](sources.md) — view source sync status and trigger individual syncs
- [Health & Logs](health-logs.md) — view sync and dbt execution logs
- [Dashboard Page](dashboard.md) — quick health overview
