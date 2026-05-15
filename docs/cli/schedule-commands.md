# Schedule Commands

Configure scheduled syncs and webhook notifications from the command line.

---

## Overview

The `dango schedule` commands automate data syncing on a recurring schedule. Configure when sources sync, enable/disable schedules, and set up webhook notifications for sync events.

**Schedule commands (7):**

| Command | Description |
|---------|-------------|
| `schedule add` | Add a schedule via interactive wizard |
| `schedule list` | List all schedules |
| `schedule remove` | Remove a schedule |
| `schedule status` | Show scheduler overview or single schedule detail |
| `schedule enable` | Enable a disabled schedule |
| `schedule disable` | Disable an active schedule |

**Webhook commands (4):**

| Command | Description |
|---------|-------------|
| `schedule webhook add` | Add a webhook via interactive prompts |
| `schedule webhook list` | List configured webhooks |
| `schedule webhook remove` | Remove a webhook |
| `schedule webhook test` | Send a test payload |

---

## Managing Schedules

### dango schedule add

Add a new schedule via interactive wizard.

```bash
dango schedule add
```

The wizard prompts for:

1. Source(s) to schedule
2. Schedule frequency (cron expression or preset)
3. Whether to run dbt transformations after sync
4. Schedule name

---

### dango schedule list

List all configured schedules with their status, frequency, and next run time.

```bash
dango schedule list
```

---

### dango schedule remove

Remove a schedule by name.

```bash
dango schedule remove NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

```bash
dango schedule remove daily_sync
dango schedule remove daily_sync --yes
```

---

### dango schedule status

Show scheduler status overview, or details for a single schedule.

```bash
dango schedule status [NAME]
```

| Parameter | Description |
|-----------|-------------|
| `NAME` | Optional — show details for this specific schedule |

```bash
dango schedule status                # Overview of all schedules
dango schedule status daily_sync     # Details for one schedule
```

---

### dango schedule enable

Enable a disabled schedule.

```bash
dango schedule enable NAME
```

```bash
dango schedule enable daily_sync
```

---

### dango schedule disable

Disable an active schedule. The schedule configuration is preserved but no longer runs.

```bash
dango schedule disable NAME
```

```bash
dango schedule disable daily_sync
```

---

## Webhooks

Webhook notifications fire on schedule events (success, failure, stale data). Useful for Slack, Teams, email, or custom integrations.

!!! info
    Webhook event toggles (`on_success`, `on_failure`, `on_stale`) are global — they affect all configured webhooks. Per-webhook event filtering is not currently supported.

### dango schedule webhook add

Add a webhook via interactive prompts.

```bash
dango schedule webhook add
```

The wizard prompts for:

1. Webhook name
2. URL endpoint
3. Event types to trigger on

---

### dango schedule webhook list

List configured webhooks.

```bash
dango schedule webhook list
```

---

### dango schedule webhook remove

Remove a webhook by name.

```bash
dango schedule webhook remove NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

```bash
dango schedule webhook remove slack_alerts
```

---

### dango schedule webhook test

Send a test payload to a webhook to verify connectivity.

```bash
dango schedule webhook test NAME
```

```bash
dango schedule webhook test slack_alerts
```

---

## Common Workflows

### Set Up Daily Sync

```bash
# Create a schedule
dango schedule add

# Verify it's active
dango schedule list

# Add Slack notification
dango schedule webhook add
dango schedule webhook test slack_alerts
```

### Pause and Resume

```bash
# Temporarily pause
dango schedule disable daily_sync

# Resume later
dango schedule enable daily_sync
```

---

## Troubleshooting

??? info "Schedule not running"
    Check `dango schedule status <name>` for the next run time and last run status. Ensure the platform is running with `dango status`. Schedules only execute while `dango start` is active.

??? info "Missed scheduled sync"
    If the platform was stopped during a scheduled sync time, the missed sync runs once when the platform restarts (coalesce behavior). Check `dango schedule status` to confirm.

??? info "Webhook not firing"
    Run `dango schedule webhook test <name>` to verify the endpoint is reachable. Check that the webhook URL is correct and the receiving service is running.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [Source & Sync](source-sync.md) — Manual sync operations
- [Deploy & Remote](deploy-remote.md) — Remote server management
