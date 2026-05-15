# Health & Logs

Monitor platform health metrics, disk usage, and browse activity logs.

---

## Health Page

The Health page (`/health`) provides a comprehensive view of your platform's operational status. Access it from the **gear menu** in the navigation bar.

The page auto-refreshes every 30 seconds. Click the **Refresh** button in the footer to update manually.

### Status Banner

A color-coded banner at the top summarizes overall platform status:

- **Healthy** (green) — all systems operating normally
- **Warnings** (yellow) — non-critical issues detected (e.g., disk usage above 80%, expiring OAuth tokens)
- **Critical** (red) — immediate attention required (e.g., sync failures, database errors)

The banner lists specific issues when warnings or critical problems are detected.

### Key Metrics

A responsive grid of metric cards shows at-a-glance health data:

| Card | What it shows |
|------|---------------|
| **Database** | Database size (GB), table count, status badge. Expand for breakdown by schema (raw, staging, marts) and total size in MB. |
| **Disk Space** | Free space (GB), usage percentage. Expand for total/used/free breakdown. |
| **Syncs (24h)** | "All Pass" or count of failed syncs in the last 24 hours, plus number of enabled sources. |
| **Transformations** | "All Pass" or count of dbt failures. |

**Cloud-only cards** appear when running on a deployed server:

| Card | What it shows |
|------|---------------|
| **CPU** | CPU usage percentage. Status: Normal (<70%), High (70-90%), Critical (>90%). |
| **Memory** | RAM usage percentage and MB breakdown (used/total). |
| **Deployment** | Last deploy commit hash, branch, deployer, and timestamp. |
| **Backup** | Backup status (OK/Stale/None) and last backup timestamp. |

### DuckDB Capacity Gauge

When capacity data is available, the Database card includes a progress bar showing DuckDB usage as a percentage of the recommended maximum size. The bar is color-coded:

- **Green** — under 50% of recommended capacity
- **Yellow** — 50-75%
- **Red** — over 75% (consider archiving data)

### Recent Issues

The **Recent Issues (Last 24h)** section lists sync and dbt failures from the past day. Each issue shows the source name, error count, and error message. When there are no issues, a green "No issues in the last 24 hours" message displays.

### Disk Usage Breakdown

On cloud deployments, a detailed breakdown shows disk consumption by component:

- **DuckDB Database** — file size with per-schema breakdown
- **Metabase Database** — Metabase's internal database size
- **CSV Uploads** — total size with per-source breakdown
- **dbt Artifacts** — compiled SQL and manifest files
- **dlt Pipeline State** — pipeline state and staging files
- **Local Backups** — backup file size

### OAuth Token Health

If any data sources use OAuth authentication, this section shows each source's token status:

- **Expired** (red) — token has expired, source cannot sync
- **Expires in Xd** (yellow) — token expires within 7 days
- **No expiry** (green) — token is valid with no upcoming expiry

A link to [Secrets & Credentials](/settings/secrets) lets you reconnect expired tokens.

??? info "How it works"
    - **Health data:** `GET /api/health/platform` returns a comprehensive status object including database stats, disk usage, sync/dbt failures, scheduler state, cloud resources, backup health, and OAuth token status.
    - **Service status:** `GET /api/status` returns service-level health (API, DuckDB, Metabase, dbt Docs) with uptime info.
    - **Auto-refresh:** JavaScript polls the health endpoint every 30 seconds and updates all cards and banners.

---

## Logs Page

The Logs page (`/logs`) provides a searchable, filterable view of platform activity. Access it from the **gear menu** in the navigation bar.

### Filters

The filter bar at the top provides four controls:

| Filter | Options |
|--------|---------|
| **Level** | All Levels, Info, Success, Warning, Error |
| **Source** | All Sources, or a specific source name (populated dynamically) |
| **Time Range** | All Time, Last Hour, Last 24 Hours, Last 7 Days, Last 30 Days |
| **Search** | Free-text search across log messages |

Click **Apply Filters** to update the table. Click **Clear Filters** to reset all filters. The entry count updates to show how many logs match the current filters.

### Logs Table

| Column | Description | Sortable |
|--------|-------------|----------|
| **Timestamp** | When the event occurred | Yes (click header) |
| **Level** | Log level — Info, Success, Warning, or Error | Yes (click header) |
| **Source** | Which component generated the log | No |
| **Message** | Log message content | No |

### Pagination

The table paginates results with **Previous** and **Next** buttons. The current page number and total range ("Showing X to Y of Z") display between the buttons.

??? info "How it works"
    - **Fetch logs:** `GET /api/logs?limit=1000` returns log entries with timestamp, level, source, and message fields.
    - **Source-specific logs:** `GET /api/sources/{source_name}/logs?limit=100` returns logs from a specific source's sync log file.
    - **Client-side filtering:** Filters and sorting are applied in the browser against the fetched data set.

## Troubleshooting

**Health page shows "Loading..."**
:   The platform health endpoint may be slow on first load while it gathers database stats. Wait a few seconds for data to populate.

**Disk usage not showing breakdown**
:   The detailed disk breakdown only appears on cloud deployments. Local installs show total disk stats only.

**Logs table is empty**
:   Check that your filters aren't too restrictive. Click **Clear Filters** to reset. If still empty, no activity has been logged yet — try running a sync.

**OAuth token shows "Expired" but source still syncs**
:   Some OAuth providers (like Google) auto-refresh tokens. The displayed expiry may lag behind the actual token state. Reconnecting from Secrets & Credentials forces a fresh token.

## Related Pages

- [Dashboard Page](dashboard.md) — quick health summary and service status
- [Sources Page](sources.md) — view source sync status and trigger syncs
- [Secrets & Admin](secrets-admin.md) — manage OAuth credentials
