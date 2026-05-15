# Webhook Notifications

Get notified when syncs complete, fail, go stale, or when governance events are detected — via Slack or any HTTP endpoint.

---

!!! note "Prerequisites"
    - A webhook URL (Slack incoming webhook or custom HTTP endpoint)
    - At least one [schedule configured](scheduled-syncs.md)

## Quick Start

1. **Add a webhook:**

    ```bash
    dango schedule webhook add
    ```

2. **Choose a format** (Slack or generic JSON) and paste your webhook URL.

3. **Test it:**

    ```bash
    dango schedule webhook test slack_alerts
    ```

    You should see a test notification arrive at your endpoint.

## Detailed Steps

### Adding a Webhook

The interactive wizard configures webhook delivery:

```
$ dango schedule webhook add

🔔 Webhook Setup
─────────────────

Webhook name: slack_alerts
Webhook URL: https://hooks.slack.com/services/T.../B.../xxx
Format:
  1. slack   — Slack Block Kit (colored sidebar, structured fields)
  2. generic — Plain JSON payload
Choice [1]: 1

✅ Webhook 'slack_alerts' added to schedules.yml
```

### Event Types

Dango sends notifications for 7 event types:

| Event Type | Description | Category |
|------------|-------------|----------|
| `sync_completed` | A scheduled sync finished successfully | success |
| `sync_failed` | A sync failed after all retry attempts | failure |
| `sync_stale` | No sync has run within the stale threshold | stale |
| `sync_retrying` | A sync failed and is being retried | failure |
| `schema_drift_detected` | Breaking schema change detected in a source | governance |
| `pii_detected` | PII found in synced data | governance |
| `metric_alert` | A monitoring metric exceeded its alert threshold | analysis |

### Event Categories

Events are grouped into 5 categories that control which notifications are sent:

| Category | Events | Default |
|----------|--------|---------|
| `success` | `sync_completed` | Enabled |
| `failure` | `sync_failed`, `sync_retrying` | Enabled |
| `stale` | `sync_stale` | Enabled |
| `governance` | `schema_drift_detected`, `pii_detected` | Enabled |
| `analysis` | `metric_alert` | Enabled |

### Global Event Toggles

Control which event categories trigger notifications for all webhooks:

```yaml
# .dango/schedules.yml
notifications:
  webhooks:
    - name: slack_alerts
      url: "https://hooks.slack.com/services/T.../B.../xxx"
      format: slack

  # Global toggles — apply to ALL webhooks
  on_success: true        # sync_completed events
  on_failure: true        # sync_failed, sync_retrying events
  on_stale: true          # sync_stale events
  on_governance: true     # schema_drift_detected, pii_detected events
  on_analysis: true       # metric_alert events
  stale_threshold_hours: 24  # Hours without a sync before "stale" fires
```

!!! tip "Reducing noise"
    Set `on_success: false` if you only want alerts on problems. Success notifications can be noisy when syncs run frequently.

### Per-Schedule Overrides

Override global toggles for individual schedules using the `notify_on` field:

```yaml
schedules:
  - name: critical_sync
    type: sync
    cron: "*/15 * * * *"
    sources: [stripe]
    notify_on:          # Only notify on these events for this schedule
      - failure
      - stale

  - name: hourly_marts
    type: dbt
    cron: "0 * * * *"
    notify_on: []       # Disable all notifications for this schedule
```

## Configuration Reference

### `notifications` Block in `schedules.yml`

```yaml
notifications:
  # Webhook endpoints
  webhooks:
    - name: slack_alerts                              # Unique name
      url: "https://hooks.slack.com/services/..."     # Webhook URL (must start with http:// or https://)
      format: slack                                   # "slack" or "generic"
    - name: pagerduty
      url: "https://events.pagerduty.com/integration/..."
      format: generic

  # Global event category toggles
  on_success: true          # Send notifications for successful syncs
  on_failure: true          # Send notifications for failed syncs and retries
  on_stale: true            # Send notifications when syncs go stale
  on_governance: true       # Send notifications for schema drift and PII
  on_analysis: true         # Send notifications for metric alerts
  stale_threshold_hours: 24 # Hours without a sync before a source is considered stale
```

### Slack Integration

Dango formats Slack messages using [Block Kit](https://api.slack.com/block-kit) with colored sidebars:

| Event | Color | Hex |
|-------|-------|-----|
| Sync Completed | Green | `#2eb886` |
| Sync Failed | Red | `#e01e5a` |
| Sync Stale | Amber | `#ecb22e` |
| Sync Retrying | Gray | `#aaaaaa` |
| Schema Drift Detected | Dark amber | `#e0a514` |
| PII Detected | Red | `#e01e5a` |
| Metric Alert | Dark amber | `#e0a514` |

**Setting up a Slack webhook:**

1. Go to your Slack workspace and create a new app (or use an existing one)
2. Enable **Incoming Webhooks** in your app settings
3. Click **Add New Webhook to Workspace** and select a channel
4. Copy the webhook URL (starts with `https://hooks.slack.com/services/`)
5. Use `dango schedule webhook add` and paste the URL with format `slack`

### Generic Webhooks

For non-Slack endpoints, use `format: generic`. The payload is a JSON object:

```json
{
  "event_type": "sync_completed",
  "schedule_name": "daily_sync",
  "sources": ["stripe", "google_sheets"],
  "duration_seconds": 145.2,
  "rows_loaded": 12500,
  "occurred_at": "2026-05-15T06:02:30+00:00",
  "dashboard_url": "https://your-domain.com/",
  "error": null,
  "stale_hours": null,
  "attempt_number": null,
  "next_retry_at": null,
  "metadata": null
}
```

| Field | Type | Present When |
|-------|------|-------------|
| `event_type` | string | Always |
| `schedule_name` | string | Always |
| `sources` | list | Always (may be empty for `dbt` schedules) |
| `duration_seconds` | float | `sync_completed` |
| `rows_loaded` | int | `sync_completed` |
| `error` | string | `sync_failed`, `schema_drift_detected`, `pii_detected` |
| `stale_hours` | float | `sync_stale` |
| `attempt_number` | int | `sync_retrying` |
| `next_retry_at` | datetime | `sync_retrying` |
| `occurred_at` | datetime | Always |
| `dashboard_url` | string | When configured |
| `metadata` | object | `metric_alert` (contains `summary`, `flagged_count`, `total_count`) |

### Retry Logic

Webhook delivery retries on transient failures:

| Attempt | Delay After Failure | Retried On |
|---------|-------------------|------------|
| 1 | — | First delivery attempt |
| 2 | 5 seconds | 5xx status, timeout, connection error |
| 3 | 15 seconds | 5xx status, timeout, connection error |
| *(give up)* | 45 seconds | Final attempt before discarding |

- **HTTP timeout:** 10 seconds per request
- **Retryable errors:** 5xx server errors, connection errors, DNS failures, timeouts
- **Non-retryable:** 4xx client errors (bad URL, invalid token) — no retry, discarded immediately
- **Never blocks:** Webhook failures never block the sync pipeline. Delivery is fire-and-forget.

## Verification

After adding a webhook, test it:

```bash
# Send a test notification to a specific webhook
dango schedule webhook test slack_alerts
```

Check that:

- The test notification appears at your endpoint
- The format is correct (Slack Block Kit or JSON)
- The channel/destination is right

!!! tip "Debugging delivery"
    If webhooks aren't arriving, check the Dango logs for `webhook_delivery_failed` entries. Common causes: expired Slack webhook URL, firewall blocking outbound HTTPS, or incorrect URL.

## Troubleshooting

**Webhook not receiving notifications**

- Run `dango schedule webhook test <name>` — does the test message arrive?
- Verify the URL is correct in `.dango/schedules.yml`
- Check that the relevant event category is enabled (e.g., `on_success: true`)
- Ensure `dango start` is running

**Slack formatting issues**

- Verify `format: slack` is set in the webhook config
- Slack incoming webhooks only support their own Block Kit format — don't use `format: generic` for Slack

**Timeout errors**

- Dango waits 10 seconds for a webhook response. If your endpoint is slow, webhook delivery will fail
- Check your endpoint's response time — it should respond within a few seconds

**Event not triggering**

- Check global toggles (`on_success`, `on_failure`, etc.) in the `notifications` block
- Check per-schedule `notify_on` overrides — an empty list disables all notifications for that schedule
- `sync_stale` only fires when no sync has run within `stale_threshold_hours` (default: 24)

## Next Steps

- [Scheduled Syncs](scheduled-syncs.md) — set up the schedules that trigger these notifications
- [Schema Drift](schema-drift.md) — understand `schema_drift_detected` events
- [PII Scanning](pii-scanning.md) — understand `pii_detected` events
- [Monitoring Metrics](metrics.md) — understand `metric_alert` events
