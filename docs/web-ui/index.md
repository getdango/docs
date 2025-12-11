# Web UI

Monitor and manage your data platform through a modern web interface.

---

## Overview

The Dango Web UI provides a visual interface for managing your data platform. Access real-time sync monitoring, source management, and system health checks through your browser at **http://localhost:8800**.

**Key Features**:

- **Real-time monitoring** with WebSocket updates
- **Source management** with drag-and-drop file uploads
- **Live log streaming** for debugging
- **Health dashboards** for system status
- **One-click operations** for common tasks

---

## Getting Started

### Launch Web UI

Start your Dango platform:

```bash
dango start
```

Open your browser:

**http://localhost:8800**

The Web UI is ready immediately—no configuration or login required for local development.

### First Steps

1. **Check system status** - View running services
2. **Add a data source** - Use the source wizard
3. **Upload a CSV file** - Drag and drop to get started
4. **Monitor a sync** - Watch data load in real-time
5. **Validate configuration** - Run health checks

---

## Web UI Guides

<div class="grid cards" markdown>

-   :material-view-dashboard: **Web UI Overview**

    ---

    Introduction to the Web UI with features, navigation, and capabilities.

    - Dashboard and navigation
    - Real-time monitoring features
    - WebSocket integration
    - API endpoints
    - Multi-project support
    - Security considerations

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

-   :material-database-outline: **Managing Sources**

    ---

    Add, edit, and manage data sources through the Web UI.

    - Interactive source wizard
    - CSV file upload and management
    - OAuth source authentication
    - Database source configuration
    - Source status indicators
    - Bulk operations

    [:octicons-arrow-right-24: Managing Sources Guide](managing-sources.md)

-   :material-chart-line: **Monitoring**

    ---

    Real-time sync status, logs, and health checks.

    - Real-time log streaming
    - Sync progress tracking
    - System health checks
    - Activity history
    - Performance metrics
    - Error monitoring

    [:octicons-arrow-right-24: Monitoring Guide](monitoring.md)

</div>

---

## Quick Actions

Common tasks via the Web UI:

### Sync Data

1. Navigate to Dashboard
2. Click "Sync All" button
3. Watch real-time progress in logs panel
4. View completion notification

**Or sync specific source**:

1. Go to Sources page
2. Click source card
3. Click "Sync Now" button

### Upload CSV File

1. Navigate to Sources → CSV Files
2. Drag CSV file into upload zone
3. Preview data and confirm settings
4. File syncs automatically

### Monitor Sync Progress

1. Click "Logs" in navigation
2. Real-time WebSocket updates appear
3. Filter by source or log level
4. Download logs if needed

### Check System Health

1. Navigate to Dashboard → System Health
2. View service status indicators
3. Click "Run Health Check" for detailed report
4. Fix any issues identified

---

## Web UI vs CLI

The Web UI and CLI are **equal interfaces** to the same Dango functionality. Neither is "better"—they serve different workflows and preferences.

| Feature | Web UI | CLI |
|---------|--------|-----|
| **Add sources** | Interactive wizard | `dango source add` |
| **Sync data** | Click "Sync" button | `dango sync` |
| **Monitor progress** | Real-time logs panel | Terminal output |
| **Validate config** | Health check dashboard | `dango validate` |
| **Upload CSV** | Drag-and-drop | Copy to data/ folder |
| **View status** | Dashboard panels | `dango status` |

**When to use Web UI**:

- Visual monitoring and dashboards
- Uploading files via browser
- Exploring data interactively
- Sharing screens with stakeholders
- Quick ad-hoc operations

**When to use CLI**:

- Automation and scripting
- CI/CD pipelines
- SSH remote access
- Precise command control
- Advanced options and flags

**Use both together**: Many users keep the Web UI open in a browser tab for monitoring while running CLI commands in a terminal for precise control.

---

## Web UI Features

### Real-Time Updates

WebSocket-powered live updates for:

- Sync progress (rows synced, duration, status)
- Log streaming (INFO, WARNING, ERROR)
- File watcher events (CSV changes detected)
- Health check results
- Error notifications

### Visual Source Management

- Grid view of all configured sources
- Color-coded status indicators (green/yellow/red)
- Quick actions (sync, edit, disable)
- OAuth credential expiration warnings
- Connection test results

### Interactive Dashboards

- System status panel (services, database, uptime)
- Recent activity log (last 20 events)
- Source summary cards (status, last sync, rows)
- Quick stats (total sources, database size, data freshness)

### File Upload System

- Drag-and-drop CSV uploads
- Auto-detection (delimiter, headers, encoding)
- File preview (first 10 rows)
- Replace existing files
- Download original files

---

## Common Workflows

### Morning Data Refresh

```
1. Open http://localhost:8800
2. Check System Status (all green?)
3. Click "Sync All Sources"
4. Monitor Logs panel for progress
5. Verify completion notifications
```

### Add New Data Source

```
1. Sources → Add Source
2. Select source type from wizard
3. Fill in configuration form
4. Test connection
5. Save and sync immediately
```

### Debug Sync Failure

```
1. Logs → Filter by ERROR level
2. Search for source name
3. Read error message and stack trace
4. Click error to see suggested fixes
5. Fix issue and retry sync
```

### Upload Updated CSV

```
1. Sources → Find CSV source card
2. Click "Replace File"
3. Upload new CSV
4. Preview changes
5. Confirm - auto-sync triggered
```

---

## Accessing the Web UI

### Default URL

```
http://localhost:8800
```

### Custom Port

**Change in `.dango/project.yml`**:

```yaml
platform:
  port: 8888
```

**Access at**:

```
http://localhost:8888
```

### Multiple Projects

Run multiple Dango projects on different ports:

**Project 1**:
```
http://localhost:8800
```

**Project 2**:
```
http://localhost:8801
```

**Project 3**:
```
http://localhost:8802
```

---

## Browser Compatibility

Tested browsers:

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Requirements**:

- JavaScript enabled
- WebSocket support
- Cookies enabled (for session)

---

## Next Steps

<div class="grid cards" markdown>

-   :material-view-dashboard: **Web UI Overview**

    ---

    Explore all Web UI features and capabilities.

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

-   :material-database-outline: **Managing Sources**

    ---

    Learn how to add and manage data sources.

    [:octicons-arrow-right-24: Managing Sources](managing-sources.md)

-   :material-chart-line: **Monitoring**

    ---

    Master real-time monitoring and health checks.

    [:octicons-arrow-right-24: Monitoring](monitoring.md)

-   :material-console: **CLI Alternative**

    ---

    Explore CLI commands for the same functionality.

    [:octicons-arrow-right-24: CLI Reference](../cli/cli-reference.md)

</div>
