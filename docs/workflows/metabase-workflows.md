# Metabase Workflows

Dashboard management, exports, and advanced Metabase usage.

---

## Overview

Dango includes Metabase for visualization. This guide covers advanced workflows beyond basic dashboard creation:

- Exporting and importing dashboards
- Organizing collections
- Using the Metabase API
- Backup strategies

---

## Accessing Metabase

### Via Dango

```bash
# Open Metabase in browser
dango web
# Then click "Metabase" in the navigation

# Or directly
open http://localhost:3000
```

### Default Credentials

After `dango start`, Metabase is provisioned with:

- **Email**: `admin@dango.local`
- **Password**: `dango123!`

!!! warning "Change Default Password"
    For any shared or production environment, change the default password immediately.

---

## Dashboard Export & Import

### Using Dango CLI

```bash
# Save all dashboards to JSON
dango metabase save

# Output: metabase_export.json

# Load dashboards from JSON
dango metabase load --file metabase_export.json
```

### Export Location

Exports are saved to:
```
my-project/
└── metabase_export.json
```

### What's Exported

The export includes:
- Dashboard definitions
- Questions (saved queries)
- Collections structure
- Visualization settings

!!! note "Credentials Not Exported"
    Database connections and credentials are NOT exported for security.

---

## Organizing Collections

### Collection Structure

Organize dashboards into collections for clarity:

```
📁 Our Analytics
├── 📁 Revenue
│   ├── 📊 Daily Revenue Dashboard
│   └── 📊 Monthly Trends
├── 📁 Customers
│   ├── 📊 Customer Overview
│   └── 📊 Cohort Analysis
└── 📁 Operations
    └── 📊 Sync Status
```

### Creating Collections

1. Click **+ New** in Metabase
2. Select **Collection**
3. Name it and choose parent location
4. Move dashboards by editing them and changing collection

---

## Using the Metabase API

### API Basics

Metabase has a REST API for automation:

```bash
# Base URL
http://localhost:3000/api/

# Authentication
# First, get a session token
curl -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d '{"username": "admin@dango.local", "password": "dango123!"}'
```

### Common API Operations

**List Dashboards**:
```bash
curl http://localhost:3000/api/dashboard \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

**Get Dashboard Details**:
```bash
curl http://localhost:3000/api/dashboard/1 \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN"
```

**Export Dashboard**:
```bash
curl http://localhost:3000/api/dashboard/1 \
  -H "X-Metabase-Session: YOUR_SESSION_TOKEN" \
  -o dashboard_1.json
```

### Python Example

```python
import requests

# Login
session = requests.Session()
response = session.post(
    "http://localhost:3000/api/session",
    json={
        "username": "admin@dango.local",
        "password": "dango123!"
    }
)
token = response.json()["id"]

# List dashboards
headers = {"X-Metabase-Session": token}
dashboards = session.get(
    "http://localhost:3000/api/dashboard",
    headers=headers
).json()

for d in dashboards:
    print(f"{d['id']}: {d['name']}")
```

---

## Dashboard Versioning

### Git Workflow for Dashboards

```bash
# 1. Export dashboards
dango metabase save

# 2. Commit to version control
git add metabase_export.json
git commit -m "Update dashboard: added revenue chart"

# 3. On another machine, restore
dango metabase load --file metabase_export.json
```

### Tracking Changes

The JSON export is diff-friendly:

```bash
# See what changed
git diff metabase_export.json
```

---

## Refreshing Data Connections

### When to Refresh

Refresh the database connection after:
- DuckDB schema changes
- Adding new dbt models
- Syncing new data sources

### Refresh Methods

**Via CLI**:
```bash
dango metabase refresh
```

**Via UI**:
1. Go to **Admin** → **Databases**
2. Select the DuckDB database
3. Click **Sync database schema now**

---

## Creating Effective Dashboards

### Best Practices

1. **One dashboard per topic** - Don't overcrowd
2. **Put key metrics at top** - Most important KPIs first
3. **Use consistent colors** - Establish a color scheme
4. **Add text cards** - Explain context and definitions
5. **Filter at dashboard level** - Add date/category filters

### Dashboard Layout

```
┌─────────────────────────────────────────┐
│  📊 Revenue Dashboard                    │
├──────────────┬──────────────┬───────────┤
│  Total Rev   │  Orders      │  Avg Order │
│  $125,000    │  1,234       │  $101      │
├──────────────┴──────────────┴───────────┤
│                                         │
│  📈 Revenue Over Time (Line Chart)      │
│                                         │
├───────────────────┬─────────────────────┤
│  Revenue by       │  Top Products       │
│  Category (Pie)   │  (Table)            │
└───────────────────┴─────────────────────┘
```

---

## Scheduling & Alerts

### Dashboard Subscriptions

Set up email notifications:

1. Open a dashboard
2. Click **Subscriptions** (bell icon)
3. Configure:
   - Recipients
   - Frequency (daily, weekly)
   - Time of day

### Alerts

Set alerts on questions:

1. Open a saved question
2. Click **Alert** (bell icon)
3. Configure trigger:
   - When results exist
   - When value is above/below threshold

!!! note "Email Configuration Required"
    Subscriptions and alerts require SMTP configuration in Metabase admin settings.

---

## Embedding Dashboards

### Public Links

For sharing without login:

1. Go to **Admin** → **Settings** → **Public Sharing**
2. Enable public sharing
3. On a dashboard, click **Sharing** → **Public link**

### Iframe Embedding

```html
<iframe
    src="http://localhost:3000/public/dashboard/abc123"
    frameborder="0"
    width="100%"
    height="600"
    allowtransparency
></iframe>
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Database connection failed" | Restart Metabase: `dango stop && dango start` |
| Tables not showing | Run `dango metabase refresh` |
| Slow queries | Check DuckDB [performance](performance.md) |
| Export fails | Ensure Metabase is running and accessible |

### Reset Metabase

If Metabase gets into a bad state:

```bash
# Stop services
dango stop

# Remove Metabase data (WARNING: loses all dashboards!)
rm -rf metabase-data/

# Restart and re-provision
dango start
dango dashboard provision
```

---

## Next Steps

- [Creating Dashboards](../dashboards/creating-dashboards.md) - Dashboard basics
- [SQL Queries](../dashboards/sql-queries.md) - Custom SQL in Metabase
- [Backup & Restore](backup-restore.md) - Complete backup strategy
