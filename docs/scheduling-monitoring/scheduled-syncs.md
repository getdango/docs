# Scheduled Syncs

Automate data syncs with cron schedules so your warehouse stays fresh without manual intervention.

---

!!! note "Prerequisites"
    - At least one data source configured (`dango source add`)
    - `dango start` running (local) or cloud deployment active

## Quick Start

1. **Add a schedule:**

    ```bash
    dango schedule add
    ```

2. **Verify it's registered:**

    ```bash
    dango schedule list
    ```

3. **Check the next run time:**

    ```bash
    dango schedule status daily_sync
    ```

That's it — your sources will sync automatically on the cron schedule you chose.

## Detailed Steps

### The Schedule Wizard (`dango schedule add`)

The interactive wizard walks you through creating a schedule:

```
$ dango schedule add

📅 Schedule Setup
─────────────────

Schedule name (lowercase, letters/numbers/underscores): daily_sync
Schedule type:
  1. sync       — Sync sources + run dbt (recommended)
  2. sync_only  — Sync sources only, skip dbt
  3. dbt        — Run dbt only (no source sync)
Choice [1]: 1

Select sources to sync:
  [1] stripe
  [2] google_sheets
  [3] hubspot
Enter source numbers (comma-separated, or 'all'): all

Frequency:
  1. Every 15 minutes    (*/15 * * * *)
  2. Every hour           (0 * * * *)
  3. Every 6 hours        (0 */6 * * *)
  4. Daily at 6 AM        (0 6 * * *)
  5. Weekly (Monday 6 AM) (0 6 * * 1)
  6. Custom cron expression
Choice [4]: 4

Timezone (leave blank for UTC): America/New_York

✅ Schedule 'daily_sync' created
   Next run: 2026-05-16 06:00:00 EDT
```

### Schedule Types

| Type | What It Does | When to Use |
|------|-------------|-------------|
| `sync` | Syncs selected sources, then runs `dbt run` + `dbt test` | **Recommended** for most workflows. Keeps models up to date after every sync. |
| `sync_only` | Syncs selected sources only — skips dbt entirely | When you want to decouple ingestion from transformation, or run dbt on a separate schedule. |
| `dbt` | Runs a dbt command only — no source sync | For dbt-only schedules (e.g., hourly `dbt run` on models that depend on external tables). |

!!! tip "When to use `sync_only`"
    If you have 10 sources syncing hourly, each `sync` schedule runs a full `dbt run` after every source sync — that's 10 dbt runs per hour. Use `sync_only` for individual sources and a separate `dbt` schedule to run transformations once.

### Frequency Options

Dango provides built-in presets, or you can write a custom cron expression:

| Preset | Cron Expression | Description |
|--------|----------------|-------------|
| Every 15 minutes | `*/15 * * * *` | High-frequency syncs for real-time data |
| Every hour | `0 * * * *` | Standard hourly sync |
| Every 6 hours | `0 */6 * * *` | Four times daily |
| Daily at 6 AM | `0 6 * * *` | Once per day (default) |
| Weekly (Monday 6 AM) | `0 6 * * 1` | Weekly sync |
| Custom | *you define it* | Any valid 5-field cron expression |

### Timezone Handling

Schedules default to **UTC** if no timezone is specified. To use a local timezone:

```yaml
schedules:
  - name: daily_sync
    cron: "0 6 * * *"
    timezone: "America/New_York"
```

!!! warning "Daylight Saving Time"
    When using timezones with DST, schedule times shift with the clock. A 6 AM schedule runs at 6 AM local time year-round, which means the UTC time changes when clocks spring forward or fall back.

### dbt Selectors (for `type: dbt` schedules)

When using `type: dbt`, specify a dbt command with selectors:

```yaml
schedules:
  - name: hourly_marts
    type: dbt
    cron: "0 * * * *"
    dbt_command: "run --select tag:hourly"
```

Common dbt selector patterns:

```yaml
# Run a specific model and its upstream dependencies
dbt_command: "run --select +fct_orders"

# Run all models in a directory
dbt_command: "run --select marts.*"

# Run models tagged for hourly refresh
dbt_command: "run --select tag:hourly"

# Run tests after a specific model
dbt_command: "test --select fct_orders"
```

## Configuration Reference

### `schedules.yml` Format

Schedules are stored in `.dango/schedules.yml`. The wizard writes this file automatically, but you can also edit it directly.

```yaml
# .dango/schedules.yml

schedules:
  - name: daily_sync
    type: sync                  # sync | sync_only | dbt
    cron: "0 6 * * *"          # 5-field cron expression
    sources:                    # Sources to sync (ignored for type: dbt)
      - stripe
      - google_sheets
    enabled: true               # Toggle without removing
    timezone: "America/New_York"
    notify_on:                  # Per-schedule notification override
      - failure
      - stale

  - name: hourly_marts
    type: dbt
    cron: "0 * * * *"
    dbt_command: "run --select tag:hourly"
    timeout_minutes: 30         # Override default 60-min timeout

# Notification config (see Webhook Notifications for details)
notifications:
  webhooks:
    - name: slack_alerts
      url: "https://hooks.slack.com/services/T.../B.../xxx"
      format: slack
  on_failure: true
  on_success: true
  on_stale: true
  on_governance: true
  on_analysis: true
  stale_threshold_hours: 24
```

### Schedule Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | yes | — | Unique identifier. Lowercase alphanumeric + underscores. |
| `type` | string | no | `sync` | Schedule type: `sync`, `sync_only`, or `dbt`. |
| `cron` | string | yes | — | 5-field cron expression (minute hour day month weekday). |
| `sources` | list | no | `[]` | Source names to sync. Required for `sync` / `sync_only`. |
| `enabled` | bool | no | `true` | Set to `false` to pause without deleting. |
| `timezone` | string | no | UTC | IANA timezone (e.g., `America/New_York`). |
| `start_date` | datetime | no | — | Don't run before this date. |
| `misfire_grace_time` | int | no | — | Seconds after scheduled time to still run a missed job. `null` = always run. |
| `timeout_minutes` | int | no | `60` | Maximum execution time before the job is killed. |
| `notify_on` | list | no | `[]` | Per-schedule notification override: `failure`, `success`, `stale`. |
| `dbt_command` | string | no | — | dbt command for `type: dbt` schedules (e.g., `run --select marts.*`). |

### Cron Expressions

Cron expressions use 5 fields:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7, Sun=0 or 7)
│ │ │ │ │
* * * * *
```

| Symbol | Meaning | Example |
|--------|---------|---------|
| `*` | Every value | `* * * * *` = every minute |
| `*/N` | Every N | `*/15 * * * *` = every 15 minutes |
| `N` | Specific value | `0 6 * * *` = at 6:00 |
| `N,M` | Multiple values | `0 6,18 * * *` = at 6:00 and 18:00 |
| `N-M` | Range | `0 9-17 * * *` = every hour 9 AM–5 PM |

## Execution History

### Viewing History

=== "CLI"

    ```bash
    # Status of a specific schedule
    dango schedule status daily_sync

    # List all schedules with last run info
    dango schedule list
    ```

=== "Web UI"

    Navigate to the **Schedules** page to see execution history for each schedule, including start time, duration, status, and error details.

=== "API"

    ```
    GET /api/schedules/{name}/history
    GET /api/schedules/recent-history
    ```

### Status Values

| Status | Meaning |
|--------|---------|
| `running` | Job is currently executing |
| `success` | Job completed without errors |
| `failed` | Job encountered an error (after all retries) |
| `timeout` | Job exceeded its `timeout_minutes` limit |
| `cancelled` | Job was stopped by the user or during server shutdown |

History records are retained for **30 days**, after which they are automatically cleaned up. Running records older than 24 hours are automatically marked as failed (stale detection).

## Resilience & Recovery

Scheduled jobs have built-in retry and timeout handling:

### Retry Behavior

| Attempt | Delay Before Retry | What Happens |
|---------|-------------------|--------------|
| 1 | — | First attempt runs immediately at the scheduled time |
| 2 | 30 seconds | Retry after transient failure |
| 3 | 2 minutes | Second retry |
| *(failure)* | 5 minutes | Final retry before marking as failed |

After 3 failed attempts, the job is marked as `failed` and a `sync_failed` webhook notification is sent (if configured).

### Timeout

Jobs are killed after **60 minutes** by default (configurable per-schedule via `timeout_minutes`). Timed-out jobs are marked with `timeout` status and do not retry.

### Missed Run Recovery

If Dango was offline when a schedule was supposed to fire (e.g., laptop was asleep, server was rebooting), the missed run executes immediately on startup. This is controlled by `misfire_grace_time=None` (unlimited) and `coalesce=True` — multiple missed runs collapse into a single execution.

??? info "APScheduler internals"
    Dango uses [APScheduler](https://apscheduler.readthedocs.io/) 3.x with `AsyncIOScheduler` for job scheduling. Key configuration:

    - **Job store:** SQLite database at `.dango/scheduler.db` — jobs persist across restarts
    - **Executor:** ThreadPoolExecutor — sync jobs run in threads without blocking the event loop
    - **`coalesce=True`:** Multiple missed runs collapse into one execution
    - **`misfire_grace_time=None`:** Missed jobs always run (no expiration window)
    - **`max_instances=1`:** Only one instance of a job can run at a time — prevents overlapping syncs

=== "Local"

    Schedules run while `dango start` is active. If you close the terminal or your laptop sleeps, schedules pause. Missed runs fire on next startup.

=== "Cloud"

    Schedules run 24/7 via the systemd service. They survive server reboots automatically (systemd restart + APScheduler job persistence).

## Verification

After creating a schedule, verify it's working:

```bash
# List all schedules with their status
dango schedule list

# Check a specific schedule's details and next run time
dango schedule status daily_sync

# Watch the execution history for the next scheduled run
dango schedule status daily_sync --watch
```

Expected output from `dango schedule list`:

```
Schedules
─────────
Name          Type   Cron          Enabled  Next Run
daily_sync    sync   0 6 * * *     ✓        2026-05-16 06:00 EDT
hourly_marts  dbt    0 * * * *     ✓        2026-05-15 15:00 EDT
```

## Troubleshooting

**Schedule not firing**

- Verify `dango start` is running (local) or the server is online (cloud)
- Check `dango schedule list` — is the schedule `enabled`?
- Verify the cron expression: `dango schedule status <name>` shows the next run time

**Overlapping syncs**

- APScheduler's `max_instances=1` prevents overlapping runs of the same schedule
- If a sync is still running when the next one is due, the new run waits until the current one finishes (with `coalesce=True`, backed-up runs collapse into one)

**Timezone confusion**

- Schedules default to UTC. Check `dango schedule status <name>` to see the next run in your local time
- Use a valid IANA timezone string (e.g., `America/New_York`, not `EST`)

**Cron syntax errors**

- Cron must be exactly 5 fields separated by spaces
- The wizard validates syntax before saving — if editing `schedules.yml` manually, run `dango config validate` to check

**Stale "running" status**

- If a schedule shows `running` for more than 24 hours, it was likely killed without cleanup (e.g., `kill -9`)
- Stale running records are automatically marked as `failed` during the next cleanup cycle
- Restart `dango start` to clear the state

## Next Steps

- [Webhook Notifications](webhooks.md) — get alerts on sync success, failure, or staleness
- [Configuring Monitors](configuring.md) — set up automated metric tracking after syncs
- [Schema Drift](schema-drift.md) — detect source schema changes between syncs
- [CLI Schedule Commands](../cli/schedule-commands.md) — full CLI reference for schedule management
