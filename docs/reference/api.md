# API Reference

REST API reference for the Dango Web UI.

---

## Overview

The Dango Web UI exposes a REST API for programmatic access to all platform features.

**Base URL**: `http://localhost:8800/api`

**Documentation**:
- Swagger UI: `http://localhost:8800/api/docs`
- ReDoc: `http://localhost:8800/api/redoc`

---

## Health & Status

### GET /api/status

Get service health status.

**Response**:
```json
{
  "status": "healthy",
  "dango_version": "0.0.5",
  "services": {
    "api": "running",
    "duckdb": "healthy",
    "metabase": "healthy",
    "dbt_docs": "healthy"
  },
  "uptime": "N/A"
}
```

---

### GET /api/health/platform

Get comprehensive platform health.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-09T10:30:00Z",
  "database": {
    "size_mb": 42.3,
    "tables": 15,
    "status": "small",
    "raw_tables": 5,
    "staging_tables": 5,
    "marts_tables": 5
  },
  "disk": {
    "status": "ok",
    "free_gb": 245,
    "total_gb": 500
  },
  "sync_failures": [],
  "dbt_failures": [],
  "total_sources": 5,
  "enabled_sources": 4,
  "critical_issues": [],
  "warnings": []
}
```

---

### GET /api/watcher/status

Get file watcher status.

**Response**:
```json
{
  "running": true,
  "pid": 12345,
  "auto_sync_enabled": true,
  "auto_dbt_enabled": true,
  "debounce_seconds": 600,
  "watch_patterns": ["*.csv"],
  "watch_directories": ["data/uploads"]
}
```

---

## Configuration

### GET /api/config

Get Dango configuration and service URLs.

**Response**:
```json
{
  "web_port": 8800,
  "web_url": "http://localhost:8800",
  "metabase_url": "http://localhost:3000",
  "dbt_docs_url": "http://localhost:8081",
  "api_url": "http://localhost:8800/api",
  "project_name": "my-analytics",
  "organization": "Acme Corp"
}
```

---

### GET /api/metabase-config

Get Metabase configuration.

**Response**:
```json
{
  "database_id": 2,
  "configured": true
}
```

---

## Sources

### GET /api/sources

List all configured data sources.

**Response**:
```json
[
  {
    "name": "stripe_payments",
    "type": "stripe",
    "enabled": true,
    "last_sync": "2025-12-09T08:00:00Z",
    "row_count": 1523,
    "status": "synced",
    "freshness": {
      "last_update": "2025-12-09T08:00:00Z",
      "days_old": 0
    },
    "tables": [
      {"name": "charges", "row_count": 1000, "schema": "raw_stripe"},
      {"name": "customers", "row_count": 523, "schema": "raw_stripe"}
    ]
  }
]
```

**Status values**: `synced`, `syncing`, `failed`, `empty`, `not_synced`, `unknown`

---

### GET /api/sources/{source_name}/details

Get detailed information about a source.

**Path Parameters**:
- `source_name` - Name of the source

**Response**:
```json
{
  "name": "stripe_payments",
  "config": {
    "name": "stripe_payments",
    "type": "stripe",
    "enabled": true,
    "stripe": {
      "stripe_secret_key_env": "STRIPE_API_KEY",
      "endpoints": ["charges", "customers"]
    }
  },
  "history": [
    {
      "timestamp": "2025-12-09T08:00:00Z",
      "status": "success",
      "duration_seconds": 45,
      "rows_processed": 1523,
      "full_refresh": false
    }
  ],
  "row_count": 1523,
  "tables": [...]
}
```

---

### POST /api/sources/{source_name}/sync

Trigger a data sync for a source.

**Path Parameters**:
- `source_name` - Name of the source

**Request Body**:
```json
{
  "full_refresh": false,
  "start_date": "2024-01-01",
  "end_date": null
}
```

**Response**:
```json
{
  "success": true,
  "message": "Sync started for stripe_payments",
  "source_name": "stripe_payments",
  "started_at": "2025-12-09T10:30:00Z"
}
```

---

### GET /api/sources/{source_name}/logs

Get sync logs for a source.

**Path Parameters**:
- `source_name` - Name of the source

**Query Parameters**:
- `limit` (optional) - Maximum entries (default: 100)

**Response**:
```json
[
  {
    "timestamp": "2025-12-09T08:00:00Z",
    "level": "INFO",
    "message": "Starting sync for stripe_payments"
  },
  {
    "timestamp": "2025-12-09T08:00:45Z",
    "level": "SUCCESS",
    "message": "Sync completed: 1523 rows"
  }
]
```

---

## CSV Operations

### POST /api/sources/{source_name}/upload-csv

Upload a CSV file to a source.

**Path Parameters**:
- `source_name` - Name of the CSV source

**Query Parameters**:
- `trigger_sync` (optional) - Trigger sync after upload (default: false)

**Request**: Multipart form with `file` field

**Response**:
```json
{
  "success": true,
  "message": "CSV uploaded successfully: sales_2024.csv",
  "source_name": "sales_data",
  "file_path": "/data/uploads/sales/sales_2024.csv",
  "file_name": "sales_2024.csv",
  "auto_sync": true
}
```

---

### GET /api/sources/{source_name}/csv-files

List CSV files for a source.

**Response**:
```json
{
  "source_name": "sales_data",
  "directory": "data/uploads/sales",
  "file_pattern": "*.csv",
  "files": [
    {
      "filename": "sales_2024.csv",
      "path": "/data/uploads/sales/sales_2024.csv",
      "size": 102400,
      "modified": "2025-12-09T08:00:00Z",
      "on_disk": true,
      "loaded": true,
      "rows_loaded": 5432,
      "status": "success"
    }
  ],
  "total_files": 1,
  "files_on_disk": 1,
  "files_loaded": 1
}
```

---

### DELETE /api/sources/{source_name}/csv-files

Delete a CSV file.

**Query Parameters**:
- `file_path` - Full path to file to delete

**Response**:
```json
{
  "success": true,
  "message": "File deleted: sales_2024.csv",
  "file_path": "/data/uploads/sales/sales_2024.csv",
  "source_name": "sales_data",
  "background_sync": true
}
```

---

## dbt Operations

### GET /api/dbt/models

List all dbt models.

**Response**:
```json
{
  "models": [
    {
      "name": "stg_stripe_charges",
      "description": "Staging model for Stripe charges",
      "database": "warehouse",
      "schema": "staging",
      "depends_on": [],
      "materialization": "view",
      "status": "success"
    },
    {
      "name": "customer_metrics",
      "description": "Customer-level aggregations",
      "database": "warehouse",
      "schema": "marts",
      "depends_on": ["stg_stripe_charges", "stg_stripe_customers"],
      "materialization": "table",
      "status": "success"
    }
  ]
}
```

---

### POST /api/dbt/models/{model_name}/run

Run a specific dbt model.

**Path Parameters**:
- `model_name` - Name of the model

**Query Parameters**:
- `cascade` (optional) - Run downstream models (default: true)

**Response**:
```json
{
  "success": true,
  "message": "dbt model 'customer_metrics' run started",
  "model_name": "customer_metrics",
  "started_at": "2025-12-09T10:30:00Z"
}
```

---

## Logs

### GET /api/logs

Get all activity logs.

**Query Parameters**:
- `limit` (optional) - Maximum entries (default: 1000)

**Response**:
```json
[
  {
    "timestamp": "2025-12-09T10:30:00Z",
    "level": "INFO",
    "message": "Platform started"
  },
  {
    "timestamp": "2025-12-09T10:31:00Z",
    "level": "SUCCESS",
    "message": "Sync completed for stripe_payments"
  }
]
```

**Log levels**: `INFO`, `WARNING`, `ERROR`, `SUCCESS`

---

## WebSocket

### WS /ws

Real-time updates for platform events.

**Connection**: `ws://localhost:8800/ws`

**Events**:

```json
// Sync events
{"type": "sync_started", "source": "stripe_payments", "timestamp": "..."}
{"type": "sync_completed", "source": "stripe_payments", "rows": 1523, "timestamp": "..."}
{"type": "sync_failed", "source": "stripe_payments", "error": "...", "timestamp": "..."}

// dbt events
{"type": "dbt_run_started", "model": "customer_metrics", "timestamp": "..."}
{"type": "dbt_run_completed", "model": "customer_metrics", "timestamp": "..."}
{"type": "dbt_run_failed", "model": "customer_metrics", "error": "...", "timestamp": "..."}

// CSV events
{"type": "csv_uploaded", "source": "sales_data", "file": "sales.csv", "timestamp": "..."}
{"type": "csv_deleted", "source": "sales_data", "file": "sales.csv", "timestamp": "..."}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
| 409 | Conflict (e.g., sync already in progress) |
| 500 | Internal server error |
| 502 | Bad gateway (upstream service unavailable) |

**Error Response Format**:
```json
{
  "detail": "Error message describing the problem"
}
```

---

## Proxy Endpoints

The Web UI proxies requests to other services:

| Path Pattern | Proxied To | Description |
|--------------|------------|-------------|
| `/metabase/*` | `localhost:3000` | Metabase dashboard |
| `/dbt-docs/*` | `localhost:8081` | dbt documentation |
| `/manifest.json` | `localhost:8081` | dbt manifest |
| `/catalog.json` | `localhost:8081` | dbt catalog |

---

## Usage Examples

### Python

```python
import requests

# Get all sources
response = requests.get("http://localhost:8800/api/sources")
sources = response.json()

# Trigger sync
response = requests.post(
    "http://localhost:8800/api/sources/stripe_payments/sync",
    json={"full_refresh": False}
)
print(response.json())
```

### curl

```bash
# Get platform status
curl http://localhost:8800/api/status

# List sources
curl http://localhost:8800/api/sources

# Trigger sync
curl -X POST http://localhost:8800/api/sources/stripe_payments/sync \
  -H "Content-Type: application/json" \
  -d '{"full_refresh": false}'

# Upload CSV
curl -X POST http://localhost:8800/api/sources/sales_data/upload-csv \
  -F "file=@sales.csv"
```

### JavaScript

```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8800/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type, data);
};

// REST API
const sources = await fetch('http://localhost:8800/api/sources')
  .then(r => r.json());
```

---

## Next Steps

- [Web UI Overview](../web-ui/web-ui-overview.md) - Using the dashboard
- [CLI Reference](../cli/cli-reference.md) - Command-line interface
- [Configuration Reference](configuration.md) - Config file schemas
