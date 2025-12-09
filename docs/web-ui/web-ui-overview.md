# Web UI Overview

Monitor and manage your data platform through a modern web interface.

---

## Overview

The Dango Web UI is a FastAPI-powered web application that provides real-time monitoring, source management, and validation reporting for your data platform. Access it at **http://localhost:8800** when your Dango platform is running.

**Key Features**:

- **Real-time monitoring** - Live sync progress with WebSocket updates
- **Source management** - Add, edit, and remove data sources
- **File uploads** - Drag-and-drop CSV file management
- **Validation reports** - Configuration health checks
- **Quick actions** - One-click sync, generate, and run operations
- **System status** - Database stats, service health, recent activity

**Technology**:

- **FastAPI** - Modern Python web framework
- **WebSockets** - Real-time log streaming
- **Responsive UI** - Works on desktop and mobile
- **RESTful API** - All features accessible via HTTP endpoints

---

## Quick Start

### Access the Web UI

Start your Dango platform:

```bash
dango start
```

Open your browser to:

**http://localhost:8800**

The Web UI launches automatically and is ready to use immediately—no login required for local development.

### Dashboard Overview

The main dashboard shows:

**Header**:
- Project name and status indicator
- Navigation menu (Dashboard, Sources, Logs, Settings)
- Quick action buttons (Sync, Generate, Run)

**Main Panels**:
1. **System Status** - Service health, database size, last sync time
2. **Recent Activity** - Latest syncs, transformations, errors
3. **Source Summary** - Enabled sources with status indicators
4. **Quick Stats** - Row counts, schema stats, data freshness

---

## Navigation

### Main Menu

<div class="grid cards" markdown>

-   :material-view-dashboard: **Dashboard**

    ---

    Overview of system health, recent activity, and quick stats.

    - Service status indicators
    - Recent sync history
    - Database statistics
    - Quick action buttons

    Default landing page at http://localhost:8800

-   :material-database-outline: **Sources**

    ---

    Manage all data sources in one place.

    - View all configured sources
    - Add new sources with wizard
    - Edit source configuration
    - Enable/disable sources
    - Upload CSV files

    [:octicons-arrow-right-24: Managing Sources Guide](managing-sources.md)

-   :material-text-box-outline: **Logs**

    ---

    Real-time log streaming and history.

    - Live sync progress with WebSocket
    - Filter by log level (INFO, WARNING, ERROR)
    - Search log messages
    - Download log files
    - Clear log history

    [:octicons-arrow-right-24: Monitoring Guide](monitoring.md)

-   :material-cog-outline: **Settings**

    ---

    Configure platform settings and preferences.

    - Port configuration
    - Auto-sync settings
    - File watcher configuration
    - Metabase integration
    - dbt-docs settings

-   :material-check-circle-outline: **Validation**

    ---

    Project health and validation reports.

    - Configuration validation
    - Source connection tests
    - Database health checks
    - Dependency verification
    - Troubleshooting hints

</div>

---

## Key Features

### Real-Time Sync Monitoring

Watch data syncs happen live:

**Before sync**:
```
Status: Ready
Sources: 3 enabled
Last sync: 2 hours ago
```

**During sync** (WebSocket updates):
```
[12:34:56] Starting sync for stripe_payments
[12:34:57] Connecting to Stripe API
[12:34:58] Fetching charges (incremental from 2024-11-01)
[12:35:12] Loaded 1,523 charges
[12:35:13] Fetching customers (full refresh)
[12:35:20] Loaded 342 customers
[12:35:21] Writing to raw_stripe.charges
[12:35:24] Writing to raw_stripe.customers
[12:35:25] ✓ Sync complete (1,865 rows in 29.2s)
```

**After sync**:
```
Status: Success
Duration: 29.2s
Rows synced: 1,865
Next sync: In 10 minutes (auto-sync enabled)
```

### Source Management Interface

**Add New Source**:

1. Click "Add Source" button
2. Choose source type from dropdown
3. Fill in configuration form
4. Test connection
5. Save and enable

**Edit Existing Source**:

1. Click source card
2. Modify configuration fields
3. Re-test connection
4. Save changes
5. Sync immediately or later

**Visual Status Indicators**:

- 🟢 **Green** - Source healthy, syncing normally
- 🟡 **Yellow** - Warning (credentials expiring, slow sync)
- 🔴 **Red** - Error (auth failed, connection timeout)
- ⚪ **Gray** - Disabled

### File Upload System

Drag-and-drop CSV file management:

**Upload Flow**:

1. Navigate to Sources → CSV Files
2. Drag CSV file into upload zone
3. Preview first 10 rows
4. Auto-detect:
   - Delimiter (comma, tab, pipe)
   - Header row presence
   - Column types
5. Confirm and upload
6. File auto-syncs to database

**File Management**:

- View all uploaded files
- Replace existing files
- Download originals
- Delete unused files
- See sync status per file

**Auto-Sync**:

When `auto_sync: true` in config, file changes trigger automatic re-sync:

```
File detected: sales.csv (modified)
Debouncing for 600 seconds...
Syncing sales_data source...
✓ Sync complete
```

### Quick Actions

One-click operations from the dashboard:

**Sync All**:
```
Button: Sync All Sources
Action: dango sync
Shows: Real-time progress in log panel
```

**Generate Staging**:
```
Button: Generate Staging
Action: dango generate
Shows: Model generation progress
Result: "3 models created" notification
```

**Run Transformations**:
```
Button: Run dbt
Action: dango run
Shows: dbt run output
Result: Model execution summary
```

**Validate Configuration**:
```
Button: Validate
Action: dango validate
Shows: Validation report with issues
Result: Pass/fail with fix suggestions
```

---

## Dashboard Panels

### System Status Panel

**Displays**:

- **Platform Status**: Running / Stopped
- **Web UI**: http://localhost:8800 (active)
- **Metabase**: http://localhost:3000 (active)
- **dbt-docs**: http://localhost:8081 (active)
- **Database**: data/warehouse.duckdb (42.3 MB)
- **File Watcher**: Active (auto-sync enabled)

**Quick Links**:

- Open Metabase
- Open dbt Docs
- Query Database (opens SQL editor)

### Recent Activity Panel

**Shows last 20 events**:

```
12:35:25  ✓ Sync completed (stripe_payments) - 1,865 rows
12:30:15  ✓ dbt run completed - 15 models
12:15:42  ✓ Generated staging models (stripe)
11:45:00  ⚠ OAuth token expires in 7 days (google_sheets)
11:30:21  ✗ Sync failed (old_hubspot) - Auth expired
```

**Event Types**:

- Sync started / completed / failed
- Transformations run
- Models generated
- Validation checks
- Configuration changes
- Errors and warnings

### Source Summary Panel

**Grid view of all sources**:

Each card shows:

- Source name
- Source type (icon + label)
- Status indicator
- Last sync time
- Row count
- Quick actions (Sync, Edit, Disable)

**Example**:

```
┌─────────────────────────────┐
│ 🟢 stripe_payments         │
│ Type: Stripe               │
│ Last sync: 2 hours ago     │
│ Rows: 1,865                │
│ [Sync Now] [Edit] [...]    │
└─────────────────────────────┘
```

### Quick Stats Panel

**Real-time metrics**:

- **Total Sources**: 5 (4 enabled, 1 disabled)
- **Database Size**: 42.3 MB
- **Total Rows**: 28,693
- **Schemas**: 5 (raw, raw_stripe, staging, intermediate, marts)
- **dbt Models**: 15 (12 tables, 3 views)
- **Last Activity**: 2 minutes ago

---

## Port Configuration

### Default Ports

Dango uses these ports by default:

| Service | Default Port | Configurable | Config Location |
|---------|-------------|--------------|-----------------|
| Web UI | 8800 | Yes | `.dango/project.yml` |
| Metabase | 3000 | Yes | `docker-compose.yml` |
| dbt-docs | 8081 | Yes | `.dango/project.yml` |

### Change Web UI Port

**Edit `.dango/project.yml`**:

```yaml
platform:
  port: 8888  # Change from default 8800
```

**Restart platform**:

```bash
dango restart
```

**Access at new URL**:

```
http://localhost:8888
```

### Port Conflicts

If you see "Address already in use" error:

**Find conflicting process**:

```bash
lsof -i :8800
```

**Kill process**:

```bash
kill -9 <PID>
```

**Or change Dango port** as shown above.

---

## Multi-Project Support

Run multiple Dango projects simultaneously on different ports:

**Project 1** (port 8800):
```bash
cd ~/projects/analytics
dango start
# Web UI: http://localhost:8800
```

**Project 2** (port 8801):
```bash
cd ~/projects/marketing
# Edit .dango/project.yml → port: 8801
dango start
# Web UI: http://localhost:8801
```

**Switch between projects**:

- Each project has its own Web UI instance
- Each has separate Metabase and dbt-docs ports
- Projects share nothing—fully isolated

**Routing** (automatic):

Dango maintains a routing registry:

```json
{
  "analytics": {
    "port": 8800,
    "path": "/Users/you/projects/analytics"
  },
  "marketing": {
    "port": 8801,
    "path": "/Users/you/projects/marketing"
  }
}
```

Access any project by port or navigate via browser bookmarks.

---

## API Endpoints

The Web UI is built on a RESTful API. All features are accessible programmatically:

### Core Endpoints

**GET `/api/status`**

Get system status.

```bash
curl http://localhost:8800/api/status
```

Response:
```json
{
  "platform_running": true,
  "database_size": "42.3 MB",
  "services": {
    "web_ui": "running",
    "metabase": "running",
    "dbt_docs": "running",
    "file_watcher": "running"
  }
}
```

**POST `/api/sync`**

Trigger data sync.

```bash
curl -X POST http://localhost:8800/api/sync \
  -H "Content-Type: application/json" \
  -d '{"source": "stripe_payments"}'
```

**POST `/api/generate`**

Generate staging models.

```bash
curl -X POST http://localhost:8800/api/generate
```

**POST `/api/run`**

Run dbt transformations.

```bash
curl -X POST http://localhost:8800/api/run \
  -H "Content-Type: application/json" \
  -d '{"select": "marts.customer_metrics"}'
```

### Source Management

**GET `/api/sources`**

List all sources.

```bash
curl http://localhost:8800/api/sources
```

**POST `/api/sources`**

Add new source.

```bash
curl -X POST http://localhost:8800/api/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_csv",
    "type": "csv",
    "enabled": true,
    "csv": {
      "file_path": "data/sales.csv"
    }
  }'
```

**PUT `/api/sources/{name}`**

Update source configuration.

**DELETE `/api/sources/{name}`**

Remove source.

### File Uploads

**POST `/api/upload`**

Upload CSV file.

```bash
curl -X POST http://localhost:8800/api/upload \
  -F "file=@sales.csv" \
  -F "source_name=sales_data"
```

### Logs

**GET `/api/logs`**

Get recent logs.

```bash
curl http://localhost:8800/api/logs?limit=100
```

**WebSocket `/ws/logs`**

Stream real-time logs:

```javascript
const ws = new WebSocket('ws://localhost:8800/ws/logs');
ws.onmessage = (event) => {
  console.log(event.data);
};
```

---

## WebSocket Integration

### Real-Time Updates

The Web UI uses WebSockets for live updates during:

- Data syncs (progress, row counts, status)
- dbt runs (model execution, tests)
- File watcher events (file changes detected)
- Validation checks
- Error notifications

### Connection

**JavaScript example**:

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8800/ws/logs');

// Handle messages
ws.onmessage = (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.timestamp}] ${log.level}: ${log.message}`);
};

// Handle connection
ws.onopen = () => console.log('Connected to Dango logs');
ws.onerror = (error) => console.error('WebSocket error:', error);
ws.onclose = () => console.log('Disconnected from Dango logs');
```

**Message format**:

```json
{
  "timestamp": "2024-12-09T12:34:56",
  "level": "INFO",
  "message": "Loaded 1,523 charges",
  "source": "stripe_payments",
  "context": {
    "rows": 1523,
    "duration_ms": 12400
  }
}
```

### Auto-Reconnect

The Web UI automatically reconnects if WebSocket disconnects:

- Retry with exponential backoff
- Show "Reconnecting..." indicator
- Resume log streaming on reconnect

---

## UI Customization

### Branding

**Logo and favicon** (`.dango/project.yml`):

```yaml
branding:
  logo: "assets/logo.svg"
  favicon: "assets/favicon.ico"
  primary_color: "#009688"  # Teal
  accent_color: "#3F51B5"   # Indigo
```

### Dashboard Layout

**Reorder panels** (drag and drop in UI):

1. Click "Edit Layout" button
2. Drag panels to reorder
3. Save layout preferences
4. Reset to default if needed

**Hide/show panels**:

- Toggle panel visibility
- Customize dashboard for your workflow
- Settings persist per browser

---

## Keyboard Shortcuts

Speed up your workflow with keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Sync all sources |
| `Ctrl + G` | Generate staging models |
| `Ctrl + R` | Run dbt transformations |
| `Ctrl + V` | Validate configuration |
| `Ctrl + L` | Focus log search |
| `Ctrl + /` | Show keyboard shortcuts |
| `Esc` | Close modal/dialog |

---

## Best Practices

### 1. Keep the Web UI Open

Run it in a dedicated browser tab:

- Monitor syncs in real-time
- Catch errors immediately
- See auto-sync activity
- Quick access to actions

### 2. Use Auto-Sync for Development

Enable file watcher during development:

```yaml
# .dango/project.yml
platform:
  auto_sync: true
  debounce_seconds: 600  # 10 minute delay
```

Save CSV file → automatic sync after 10 minutes.

### 3. Check Validation Regularly

Click "Validate" before important syncs:

- Verify all credentials valid
- Check OAuth tokens not expired
- Ensure database accessible
- Confirm dbt project configured

### 4. Monitor Resource Usage

Keep an eye on:

- Database size (in System Status panel)
- Row counts growing as expected
- Sync durations (should be consistent)
- Error rates (should be zero)

### 5. Use Logs for Debugging

When something fails:

1. Open Logs panel
2. Filter by ERROR level
3. Search for source name
4. Read full error stack trace
5. Download logs if needed

---

## Troubleshooting

### Web UI Won't Start

**Error**: "Address already in use"

**Solution**:
```bash
# Check what's using port 8800
lsof -i :8800

# Kill the process or change Dango port
# Edit .dango/project.yml → port: 8801
dango restart
```

### Cannot Connect to WebSocket

**Symptom**: Logs don't update in real-time

**Solutions**:

1. **Check firewall**: Allow WebSocket connections
2. **Check proxy**: Some proxies block WebSockets
3. **Refresh page**: Sometimes connection drops
4. **Check browser console**: Look for WebSocket errors

### Blank Page / 404 Errors

**Solutions**:

1. **Verify Dango is running**:
   ```bash
   dango status
   ```

2. **Check correct port**:
   ```bash
   # In .dango/project.yml
   platform:
     port: 8800  # Confirm this matches your URL
   ```

3. **Clear browser cache**:
   - Hard refresh: `Ctrl + Shift + R`

### Slow Performance

**If Web UI is slow**:

1. **Large database**: Consider cleaning old data
   ```bash
   dango db clean
   ```

2. **Too many logs**: Clear log history
   - Logs panel → Clear logs button

3. **Many sources**: Disable unused sources
   - Sources panel → Disable unused sources

---

## Security Considerations

### Local Development

The Web UI is designed for **local development** only:

- No authentication by default
- Listens on `localhost` only
- Not exposed to network

**Never expose to internet** without adding:

- Authentication (OAuth, API keys)
- HTTPS/TLS encryption
- Rate limiting
- Input validation

### Production Deployment

For production use:

1. **Add authentication**:
   - OAuth 2.0 integration
   - API key middleware
   - Session management

2. **Enable HTTPS**:
   - Use reverse proxy (nginx)
   - SSL certificates
   - HSTS headers

3. **Restrict access**:
   - VPN or IP allowlist
   - Role-based permissions
   - Audit logging

4. **Harden configuration**:
   - Disable debug mode
   - Set secure cookies
   - CORS restrictions

---

## Next Steps

<div class="grid cards" markdown>

-   :material-database-outline: **Managing Sources**

    ---

    Learn how to add, edit, and manage data sources via the Web UI.

    [:octicons-arrow-right-24: Managing Sources Guide](managing-sources.md)

-   :material-chart-line: **Monitoring**

    ---

    Master real-time monitoring, logs, and health checks.

    [:octicons-arrow-right-24: Monitoring Guide](monitoring.md)

-   :material-console: **CLI Reference**

    ---

    Explore command-line alternatives to Web UI features.

    [:octicons-arrow-right-24: CLI Reference](../cli/cli-reference.md)

-   :material-cog-outline: **Configuration**

    ---

    Customize Web UI settings and platform configuration.

    [:octicons-arrow-right-24: Project Structure](../core-concepts/project-structure.md)

</div>
