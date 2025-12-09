# Monitoring

Real-time sync status, logs, and health checks via the Web UI.

---

## Overview

The Dango Web UI provides comprehensive monitoring capabilities to track your data platform's health and activity. Watch syncs happen in real-time, troubleshoot errors, and ensure your pipelines are running smoothly.

**Monitoring Features**:

- **Real-time log streaming** - WebSocket-powered live updates
- **Sync progress tracking** - Row counts, durations, status
- **Error detection** - Immediate alerts with stack traces
- **System health checks** - Database, services, connections
- **Activity history** - Audit log of all operations
- **Performance metrics** - Sync times, data freshness, throughput

---

## Logs Panel

### Accessing Logs

Navigate to the Logs view:

```
Web UI → Logs
http://localhost:8800/logs
```

The Logs panel shows all system activity with real-time updates.

### Log Levels

**Filter logs by severity**:

| Level | Color | Icon | When Used |
|-------|-------|------|-----------|
| **DEBUG** | Gray | 🔍 | Detailed diagnostic info |
| **INFO** | Blue | ℹ️ | Normal operations, progress updates |
| **SUCCESS** | Green | ✓ | Successful completions |
| **WARNING** | Yellow | ⚠ | Non-critical issues, deprecations |
| **ERROR** | Red | ✗ | Failed operations, exceptions |

**Filter buttons**:

```
[All] [DEBUG] [INFO] [SUCCESS] [WARNING] [ERROR]
```

Click to show only logs of that level.

### Real-Time Log Streaming

**WebSocket connection** provides live updates:

**During a sync**:

```
[12:34:56] INFO    Starting sync for stripe_payments
[12:34:57] INFO    Connecting to Stripe API
[12:34:58] INFO    Fetching charges (incremental from 2024-11-01)
[12:35:05] DEBUG   Fetched page 1: 100 records
[12:35:08] DEBUG   Fetched page 2: 100 records
[12:35:11] DEBUG   Fetched page 3: 100 records
[12:35:12] INFO    Loaded 1,523 charges
[12:35:13] INFO    Fetching customers (full refresh)
[12:35:20] INFO    Loaded 342 customers
[12:35:21] INFO    Writing to raw_stripe.charges
[12:35:24] SUCCESS Sync complete (1,865 rows in 29.2s)
```

**Connection indicator**:

```
● Connected - Real-time updates enabled
○ Disconnected - Reconnecting...
⚡ Buffering - Updates paused (click to resume)
```

### Log Search and Filtering

**Search box**:

```
🔍 Search logs...
```

**Search examples**:

```
stripe_payments     → All logs for this source
ERROR              → All error-level logs
Sync complete      → All completion messages
Writing to raw     → Database write operations
```

**Advanced filters**:

- **Source**: Filter by specific source name
- **Time range**: Last hour, today, this week, custom
- **Log level**: Show only selected levels
- **Text search**: Keywords in log messages

**Combined filtering**:

```
Source: stripe_payments
Level: ERROR
Time: Last 24 hours
Search: "authentication"

Result: All authentication errors for stripe_payments in last 24 hours
```

### Log Details

Click any log entry to expand details:

**Basic log**:

```
[12:35:24] INFO Sync complete (1,865 rows in 29.2s)
```

**Expanded view**:

```
Timestamp: 2024-12-09 12:35:24.123 UTC
Level: INFO
Message: Sync complete (1,865 rows in 29.2s)
Source: stripe_payments
Module: dango.sync.runner
Function: run_sync()
Thread: MainThread

Context:
  rows_synced: 1865
  duration_ms: 29200
  tables_updated: ["raw_stripe.charges", "raw_stripe.customers"]
  sync_type: incremental
```

**Error log with stack trace**:

```
[12:40:15] ERROR Sync failed for old_hubspot

Timestamp: 2024-12-09 12:40:15.456 UTC
Level: ERROR
Message: Sync failed for old_hubspot
Source: old_hubspot
Exception: AuthenticationError

Stack Trace:
  File "dango/sync/runner.py", line 142, in run_sync
    source.sync()
  File "dlt/sources/hubspot.py", line 89, in sync
    raise AuthenticationError("Invalid API key")
  AuthenticationError: Invalid API key

Fix Suggestion:
  → Verify HUBSPOT_API_KEY in .env file
  → Check API key has required permissions
  → API key may be expired - generate new key
```

### Download Logs

**Export logs for offline analysis**:

1. Click "Download Logs" button
2. Select format:
   - **Text** (.txt) - Plain text format
   - **JSON** (.json) - Structured data
   - **CSV** (.csv) - Import to Excel
3. Optional: Apply filters before download
4. File downloads to browser

**Example downloaded JSON**:

```json
[
  {
    "timestamp": "2024-12-09T12:35:24.123Z",
    "level": "INFO",
    "message": "Sync complete (1,865 rows in 29.2s)",
    "source": "stripe_payments",
    "context": {
      "rows": 1865,
      "duration_ms": 29200
    }
  }
]
```

### Clear Logs

**Remove old logs**:

1. Click "Clear Logs" button
2. Choose scope:
   - **Clear all logs** - Delete everything
   - **Clear old logs** - Keep last 1000 entries
   - **Clear by date** - Delete before specific date
3. Confirm action
4. Logs cleared (operation cannot be undone)

**Note**: Clearing logs in UI only clears display. Logs on disk (if file logging enabled) are not affected.

---

## Real-Time Sync Monitoring

### Sync Progress Indicator

**During active sync**:

```
┌──────────────────────────────────┐
│ Syncing: stripe_payments         │
│ ████████████░░░░░░░░ 60%        │
│                                  │
│ Current: Fetching customers      │
│ Progress: 342 / ~570 rows       │
│ Elapsed: 15.3s                   │
│ ETA: ~10s remaining              │
└──────────────────────────────────┘
```

**Multiple syncs in parallel**:

```
stripe_payments  ████████████████ 100% Complete
google_sheets    ████████░░░░░░░░  50% Fetching
facebook_ads     ██░░░░░░░░░░░░░░  10% Connecting
```

### Sync Status Updates

**Real-time status changes**:

```
Queued → Connecting → Fetching → Writing → Complete
```

**Each stage shows**:

1. **Queued**:
   ```
   [12:34:55] Sync queued: stripe_payments
   Position: 1 of 3
   Waiting for: google_sheets to complete
   ```

2. **Connecting**:
   ```
   [12:34:56] Connecting to Stripe API
   Testing authentication...
   ✓ Connected successfully
   ```

3. **Fetching**:
   ```
   [12:34:58] Fetching charges (incremental)
   Rate limit: 95% available
   Fetched: 1,523 records
   ```

4. **Writing**:
   ```
   [12:35:21] Writing to raw_stripe.charges
   Batch size: 500 rows per insert
   Progress: 1,523 / 1,523 rows
   ```

5. **Complete**:
   ```
   [12:35:24] ✓ Sync complete
   Total rows: 1,865
   Duration: 29.2s
   Next sync: In 1 hour (auto-sync)
   ```

### Row Count Tracking

**Watch row counts update in real-time**:

**Before sync**:

```
raw_stripe.charges: 26,828 rows
```

**During sync**:

```
raw_stripe.charges: 26,828 → 27,351 rows (+523)
Updating...
```

**After sync**:

```
raw_stripe.charges: 28,351 rows (+1,523)
Last updated: Just now
```

---

## System Health Checks

### Health Dashboard

Navigate to Dashboard → System Health:

```
http://localhost:8800/health
```

**Health indicators**:

<div class="grid cards" markdown>

-   :material-check-circle: **Platform Services**

    ---

    Status of all Dango services.

    - ✓ Web UI (running)
    - ✓ File Watcher (running)
    - ✓ Metabase (running)
    - ✓ dbt-docs (running)

-   :material-database-check: **Database Health**

    ---

    DuckDB warehouse status.

    - ✓ Database accessible
    - ✓ 42.3 MB (healthy size)
    - ✓ All schemas present
    - ✓ No corruption detected

-   :material-source-branch: **Source Connections**

    ---

    Data source connectivity.

    - ✓ 4 sources healthy
    - ⚠ 1 OAuth expiring soon
    - ✗ 1 authentication failed
    - Next check: In 5 minutes

-   :material-package-variant: **Dependencies**

    ---

    External service dependencies.

    - ✓ Docker running
    - ✓ Python 3.9+ installed
    - ✓ dbt 1.7+ available
    - ✓ dlt 0.4+ available

</div>

### Automated Health Checks

**Periodic checks** run every 5 minutes:

**What's checked**:

1. **Platform**:
   - Web UI responding
   - File watcher active
   - Docker containers running
   - Ports accessible

2. **Database**:
   - DuckDB file exists
   - Database not corrupted
   - Disk space sufficient (> 1 GB free)
   - Schemas intact

3. **Sources**:
   - OAuth tokens valid
   - API keys not expired
   - Database connections active
   - Rate limits not exceeded

4. **Configuration**:
   - YAML files valid
   - Required fields present
   - No duplicate source names
   - File paths exist

**Health check results**:

```
[12:45:00] Running health checks...
[12:45:01] ✓ Platform services healthy
[12:45:02] ✓ Database accessible
[12:45:03] ⚠ OAuth token expires in 6 days (google_sheets)
[12:45:04] ✗ Authentication failed (old_hubspot)
[12:45:05] Health check complete (2 issues found)
```

### Health Alerts

**Automatic notifications** for issues:

**Warning alert**:

```
⚠ OAuth Token Expiring Soon
Source: google_sheets_source
Expires: Dec 15 (6 days)
Action: Re-authenticate before expiration
[Re-authenticate Now] [Remind Me Later]
```

**Error alert**:

```
✗ Sync Failed
Source: old_hubspot
Error: Invalid API key
Last successful sync: 5 days ago
Action: Update API key in source configuration
[Fix Now] [Disable Source]
```

**Critical alert**:

```
⛔ Database Error
Issue: DuckDB file corrupted
Impact: All syncs and queries will fail
Action: Restore from backup immediately
[View Backup Guide] [Contact Support]
```

### Manual Health Check

**Run on-demand health check**:

1. Dashboard → System Health
2. Click "Run Health Check Now"
3. Wait for checks to complete (~10 seconds)
4. Review results
5. Fix any issues found

**Detailed health report**:

```
Health Check Report - Dec 9, 2024 12:45 PM

✓ PASSED (8/10 checks)

Platform Services:
  ✓ Web UI accessible on port 8800
  ✓ File watcher process running
  ✓ Metabase container running
  ✓ dbt-docs container running

Database:
  ✓ DuckDB file exists (42.3 MB)
  ✓ All schemas present
  ✓ No corruption detected

Sources:
  ✓ stripe_payments - Healthy
  ⚠ google_sheets - OAuth expires in 6 days
  ✗ old_hubspot - Authentication failed

Dependencies:
  ✓ Docker version 24.0.6
  ✓ Python 3.9.18
  ✓ dbt 1.7.4
  ✓ dlt 0.4.2

Recommendations:
  1. Re-authenticate google_sheets before Dec 15
  2. Fix or disable old_hubspot source
  3. Consider upgrading to dbt 1.8 (optional)
```

---

## Activity History

### Recent Activity Panel

**Dashboard shows last 20 events**:

```
Recent Activity

12:35:24  ✓ Sync completed: stripe_payments (1,865 rows)
12:30:15  ✓ dbt run completed (15 models)
12:15:42  ✓ Generated staging models (stripe)
11:45:00  ⚠ OAuth token expires in 7 days (google_sheets)
11:30:21  ✗ Sync failed: old_hubspot (Auth expired)
10:15:33  ✓ File uploaded: sales.csv (1.2 MB)
09:45:12  ✓ Source added: facebook_ads_campaign
09:30:00  ✓ Auto-sync triggered: sales_data
08:15:55  ✓ Configuration validated (no issues)
```

**Event types**:

- ✓ **Success** - Operations completed successfully
- ⚠ **Warning** - Non-critical issues
- ✗ **Error** - Failed operations
- ℹ️ **Info** - General activity

### Full Activity Log

**View complete history**:

```
Dashboard → Activity → View All
```

**Filterable table**:

| Time | Event | Source | Status | Details |
|------|-------|--------|--------|---------|
| 12:35:24 | Sync | stripe_payments | Success | 1,865 rows in 29.2s |
| 12:30:15 | dbt run | - | Success | 15 models |
| 11:30:21 | Sync | old_hubspot | Error | Auth failed |
| 10:15:33 | Upload | sales_data | Success | sales.csv (1.2 MB) |

**Filters**:

- Time range (last hour, today, this week, custom)
- Event type (sync, dbt run, upload, etc.)
- Source name
- Status (success, warning, error)

### Activity Metrics

**Statistics from activity log**:

```
Last 24 Hours:
  Total Events: 156
  Successful: 142 (91%)
  Warnings: 8 (5%)
  Errors: 6 (4%)

Most Active Sources:
  1. stripe_payments (24 syncs)
  2. google_sheets (12 syncs)
  3. sales_data (8 syncs)

Average Sync Duration: 18.3 seconds
Total Rows Synced: 45,321
Data Volume: 12.4 MB
```

---

## Performance Monitoring

### Sync Performance Metrics

**Track sync efficiency over time**:

**Current sync**:

```
Source: stripe_payments
Duration: 29.2s
Rows/second: 63.9
API calls: 16
Rate limit: 95% available
```

**Historical trend**:

```
stripe_payments - Last 7 days

Duration (avg):    29.2s  ← (was 31.5s, 7% faster)
Rows/sync (avg):   1,865  ← (was 1,723, 8% more data)
Success rate:      98.5%  ← (1 failed sync)
Slowest sync:      45.2s  (Dec 7, 10:30 AM)
Fastest sync:      21.1s  (Dec 9, 6:15 AM)
```

**Performance chart**:

```
Sync Duration (last 30 syncs)
50s │                    ●
40s │              ●     ●
30s │  ● ● ●   ● ●   ● ●   ● ● ●
20s │ ●     ● ●         ●       ●
10s │
    └──────────────────────────────
     Nov 15              Dec 9
```

### Database Growth Tracking

**Monitor warehouse size over time**:

```
Database Size History

Current: 42.3 MB
Yesterday: 39.1 MB (+3.2 MB, +8.2%)
Last week: 31.5 MB (+10.8 MB, +34.3%)
Last month: 18.2 MB (+24.1 MB, +132%)

Growth Rate: ~0.8 MB/day
Projected (30 days): 66.3 MB
Disk space available: 245 GB (healthy)
```

**Size by schema**:

```
raw          12.3 MB (29%)
raw_stripe   18.5 MB (44%)
staging      0.1 MB (0%, views)
intermediate 5.2 MB (12%)
marts        6.2 MB (15%)
```

### Source Freshness

**Track data recency**:

```
Source Freshness Dashboard

stripe_payments
  Last sync: 2 hours ago
  Last new data: 5 minutes ago (API)
  Status: ✓ Fresh (< 1 hour)

google_sheets
  Last sync: 6 hours ago
  Last updated: 2 days ago (spreadsheet)
  Status: ⚠ Stale (> 4 hours since sync)

sales_data (CSV)
  Last sync: 12 hours ago
  File modified: 10 hours ago
  Status: ⚠ Out of sync (sync needed)
```

**Freshness alerts**:

Set thresholds for staleness warnings:

```
Alert if source not synced in:
  Critical sources: 1 hour
  Standard sources: 4 hours
  Low priority: 24 hours
```

---

## Error Monitoring

### Error Dashboard

**Dedicated error view**:

```
Dashboard → Errors
```

**Error summary**:

```
Errors (Last 7 Days)

Total Errors: 12
By Source:
  old_hubspot: 8 errors (67%)
  facebook_ads: 3 errors (25%)
  stripe_payments: 1 error (8%)

By Type:
  Authentication: 8 errors (67%)
  Connection timeout: 3 errors (25%)
  Rate limit: 1 error (8%)

Trend: ↓ Down 25% from previous week
```

### Error Details

**Click error for full details**:

```
Error #12
Timestamp: Dec 9, 2024 11:30:21 AM
Source: old_hubspot
Type: AuthenticationError

Message:
Invalid API key

Stack Trace:
File "dango/sync/runner.py", line 142, in run_sync
  source.sync()
File "dlt/sources/hubspot.py", line 89, in sync
  raise AuthenticationError("Invalid API key")

Context:
  source_type: hubspot
  last_successful_sync: Dec 4, 2024 2:15 PM (5 days ago)
  api_endpoint: https://api.hubapi.com/crm/v3/objects/contacts
  http_status: 401 Unauthorized

Suggested Fixes:
  1. Verify HUBSPOT_API_KEY in .env file
  2. Check API key has required permissions (crm.objects.contacts.read)
  3. API key may be expired - generate new key at hubspot.com/settings/api
  4. Ensure API key is for correct HubSpot account

Actions:
  [Update API Key] [Test Connection] [Disable Source] [View Logs]
```

### Error Notifications

**Desktop notifications** (if enabled):

```
🔔 Dango - Sync Error
Source: old_hubspot failed to sync
Reason: Authentication error
[View Details]
```

**Email notifications** (if configured):

```
Subject: [Dango] Sync Error - old_hubspot

Source old_hubspot failed to sync at 11:30 AM.

Error: Invalid API key
Impact: Data is 5 days old
Action Required: Update API key

View details: http://localhost:8800/errors/12
```

---

## Troubleshooting with Web UI

### Debug Mode

**Enable verbose logging**:

```
Settings → Debug Mode: [x] Enabled
```

**Debug mode shows**:

- Full API requests and responses
- SQL queries executed
- File system operations
- Internal dlt processing steps
- Timing for each operation

**Example debug output**:

```
[12:34:56] INFO    Starting sync for stripe_payments
[12:34:56] DEBUG   Loading source configuration from .dango/sources.yml
[12:34:56] DEBUG   Source type: stripe
[12:34:57] DEBUG   Initializing dlt pipeline
[12:34:57] DEBUG   Pipeline destination: duckdb
[12:34:57] DEBUG   Destination path: data/warehouse.duckdb
[12:34:57] DEBUG   Reading API key from STRIPE_API_KEY
[12:34:57] DEBUG   API key: sk_live_***...***abc (masked)
[12:34:57] DEBUG   Making request to https://api.stripe.com/v1/charges
[12:34:57] DEBUG   Request headers: {"Authorization": "Bearer sk_***"}
[12:34:58] DEBUG   Response status: 200 OK
[12:34:58] DEBUG   Response time: 1.2s
[12:34:58] DEBUG   Received 100 records (page 1)
```

### Network Inspector

**Monitor API calls**:

```
Monitoring → Network
```

**Shows all external requests**:

| Time | Method | URL | Status | Duration | Size |
|------|--------|-----|--------|----------|------|
| 12:34:57 | GET | https://api.stripe.com/v1/charges | 200 | 1.2s | 45 KB |
| 12:34:59 | GET | https://api.stripe.com/v1/charges?starting_after=... | 200 | 1.1s | 43 KB |
| 12:35:01 | GET | https://api.stripe.com/v1/customers | 200 | 1.8s | 12 KB |

**Network stats**:

```
Total requests: 16
Successful (2xx): 16 (100%)
Failed (4xx, 5xx): 0 (0%)
Average latency: 1.3s
Total data: 512 KB
```

### SQL Query Log

**View all database operations**:

```
Monitoring → SQL Queries
```

**Recent queries**:

```
[12:35:21] INSERT INTO raw_stripe.charges (...) VALUES (...)
           Rows affected: 500
           Duration: 0.3s

[12:35:22] INSERT INTO raw_stripe.charges (...) VALUES (...)
           Rows affected: 500
           Duration: 0.2s

[12:35:23] INSERT INTO raw_stripe.charges (...) VALUES (...)
           Rows affected: 523
           Duration: 0.2s

[12:35:24] SELECT COUNT(*) FROM raw_stripe.charges
           Result: 28,351
           Duration: 0.01s
```

**Slow query detection**:

```
⚠ Slow Query Detected
Duration: 5.2s (threshold: 1.0s)
Query: SELECT * FROM marts.customer_metrics ORDER BY lifetime_value DESC
Suggestion: Add index on lifetime_value column
```

---

## Best Practices

### 1. Keep Logs Panel Open During Syncs

Monitor in real-time:

- Catch errors immediately
- Verify expected behavior
- Track progress of long syncs

### 2. Set Up Health Check Alerts

Configure notifications for:

- OAuth tokens expiring in < 7 days
- Sync failures
- Database errors
- Disk space low (< 5 GB)

### 3. Review Activity History Daily

Check for:

- Unexpected errors
- Performance degradation
- Missing scheduled syncs
- Configuration changes

### 4. Monitor Source Freshness

Ensure data is up-to-date:

- Set freshness thresholds per source
- Get alerted when data goes stale
- Fix auto-sync issues quickly

### 5. Use Filters to Focus

Don't get overwhelmed by logs:

- Filter by source when debugging
- Show only ERROR level for issues
- Search for specific messages
- Download logs for deep analysis

### 6. Enable Debug Mode Only When Needed

Debug mode is verbose:

- Use only for troubleshooting
- Disable after fixing issue
- Logs can grow large quickly

---

## Next Steps

<div class="grid cards" markdown>

-   :material-view-dashboard: **Web UI Overview**

    ---

    Explore other Web UI features and capabilities.

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

-   :material-database-outline: **Managing Sources**

    ---

    Learn how to configure and manage data sources.

    [:octicons-arrow-right-24: Managing Sources](managing-sources.md)

-   :material-console: **CLI Validation**

    ---

    Use CLI commands for validation and troubleshooting.

    [:octicons-arrow-right-24: Validation CLI](../cli/validation.md)

-   :material-help-circle: **Troubleshooting Guide**

    ---

    Comprehensive troubleshooting for common issues.

    [:octicons-arrow-right-24: Troubleshooting](../getting-started/troubleshooting.md)

</div>
