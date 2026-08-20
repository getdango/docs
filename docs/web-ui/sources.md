# Sources Page

View and manage data sources, trigger syncs, and inspect details.

---

## Overview

The Sources page (`/sources`) is the central hub for managing your data sources. It shows every configured source with its sync status, row count, and schedule. From here you can trigger syncs, upload CSV files, inspect source details, and view sync history.

Navigate to **Sources** in the top navigation bar.

## Sources Table

The main table lists all configured sources:

| Column | Description |
|--------|-------------|
| **Source** | Source name (e.g., `stripe_payments`, `sales_csv`) |
| **Type** | Source type (e.g., `csv`, `postgres`, `google_sheets`, `stripe`) |
| **Status** | Current sync status with color-coded badge |
| **Rows** | Total row count in the database |
| **Last Sync** | Timestamp of the most recent sync |
| **Schedule** | Human-readable schedule (e.g., "Daily at midnight", "Every 2 hours") or "Not scheduled" |
| **Actions** | Sync button and detail actions |

Click the **refresh icon** in the table header to reload the sources list.

### Status Badges

Status badges reflect the source's freshness state:

- **Synced** (green) — last sync completed successfully
- **Stale** (yellow) — last sync succeeded, but data is older than 2× the source's schedule interval. Only shown for scheduled sources. Unscheduled sources always show Synced with an age label.
- **Syncing...** (blue, pulsing) — sync currently in progress
- **Processing...** (purple, pulsing) — file operation in progress (upload or delete)
- **Failed** (red) — last sync failed with an error
- **No Data** (yellow) — sync succeeded but loaded no rows
- **Never Synced** (gray) — source has not been synced yet

## Schema Drift Attention

When a source has **breaking schema drift** (columns removed or types changed), an attention banner appears at the top of the page alerting you to the affected source.

## Syncing a Source

1. Click the **Sync Now** button (or refresh icon) in the source's row.
2. A toast notification confirms the sync has started.
3. The status badge changes to "Running" with a pulsing animation.
4. On completion, the status updates and row count refreshes.

!!! info "Queue wait"
    If another sync is already running, your sync request waits up to 5 minutes for the DuckDB write lock. Only one sync can write to the database at a time. The toast notification indicates the queued state.

## Source Detail Modal

Click a source name or the detail action to open the **Source Detail Modal**. It shows:

### Stats Overview

Three summary cards at the top:

- **Total Rows** — current row count in the database
- **Sync Count** — number of syncs run for this source
- **Sync Mode** — "incremental" or "full_refresh"

### Data Freshness

A freshness indicator shows how recently data was synced, with a link to view the source in the [Catalog](catalog.md).

### Last Sync Error

If the most recent sync failed, a red alert box shows the error message with the "Last Sync Failed" heading.

### Configuration

The source's configuration displayed in a scrollable code block. Sensitive values (passwords, tokens, API keys) are masked with `***`.

### Sync History

A table of the last 20 syncs with:

| Column | Description |
|--------|-------------|
| **Timestamp** | When the sync ran |
| **Status** | Success or Failed |
| **Duration** | How long the sync took (seconds) |
| **Sync Mode** | Incremental or Full Refresh |

## CSV / File Upload

For CSV and local file sources, clicking the source opens a dedicated modal with additional features:

### Source Configuration

Read-only display of the source's directory, file pattern, and any deduplication notes.

### Existing Files

A list of files associated with the source, showing:

- **Filename** and file size
- **Modified date**
- **Rows loaded** and when they were loaded
- **Status** — `on_disk` (file exists), `loaded` (imported to database), or `file_deleted` (file was removed but data remains)

### File Upload

1. Click the file input or drag files into it.
2. Select one or more files:
    - CSV sources accept `.csv` files
    - Local file sources accept `.csv`, `.json`, `.jsonl`, `.ndjson`, and `.parquet`
3. Review the selected files list.
4. Click **Upload File** to upload.
5. A progress indicator shows during upload.

Files are saved to the source's configured directory. Maximum file size is **100 MB**. Duplicate filenames are rejected — delete the existing file first if you need to replace it.

!!! info "Auto-sync after upload"
    After uploading, click **Sync Now** in the modal to immediately process the new files into the database.

## Date Range Sync

For sources that support date-based backfills, the **Custom Date Range Sync** modal lets you sync a specific time period:

1. Open the date range modal from the source actions.
2. Set a **Start Date** (required).
3. Optionally set an **End Date**.
4. Click **Start Sync**.

This triggers a sync that only processes data within the specified date range, useful for backfilling historical data or re-syncing a specific period.

??? info "How it works"
    - **List sources:** `GET /api/sources` returns all sources with status, row count, schedule display, freshness, and attention flags.
    - **Source details:** `GET /api/sources/{name}/details` returns masked config, sync history (last 20), row count, freshness, and sync mode.
    - **Sync:** `POST /api/sources/{name}/sync` starts a sync subprocess. Accepts optional `full_refresh`, `start_date`, and `end_date` parameters.
    - **Upload:** `POST /api/sources/{name}/upload-csv` uploads a file to the source directory. Max 100 MB. Set `trigger_sync=true` to auto-sync after upload.
    - **File list:** `GET /api/sources/{name}/csv-files` returns files on disk merged with database load metadata.
    - **Delete file:** `DELETE /api/sources/{name}/csv-files?file_path=...` removes the file, cleans up database rows, and triggers a background dbt refresh.
    - **WebSocket events:** `sync_started`, `sync_failed`, `file_uploaded`, `csv_deleted` events provide real-time feedback via toast notifications.

## Troubleshooting

**Source shows "Failed" status**
:   Open the Source Detail Modal to see the error message from the last sync. Common causes: expired OAuth credentials, network errors, or API rate limits. Fix the underlying issue and click **Sync Now** to retry.

**CSV upload rejected with "file already exists"**
:   A file with the same name already exists in the source directory. Delete the existing file from the Existing Files list in the modal, then upload again.

**Sync appears stuck (running for a long time)**
:   The sync may be waiting for the DuckDB write lock. Check if another sync or dbt run is in progress. Syncs wait up to 5 minutes for the lock before timing out.

**Row count shows 0 after sync**
:   The sync may have succeeded but loaded no data (e.g., incremental sync with no new records). Check the sync history for confirmation. For first syncs, verify the source configuration is correct.

## Related Pages

- [Schedules Page](schedules.md) — configure automated sync schedules
- [Catalog Page](catalog.md) — browse synced tables and columns
- [Health & Logs](health-logs.md) — view sync logs and platform health
- [Secrets & Admin](secrets-admin.md) — manage OAuth credentials for sources
