# API Reference

REST API reference for the Dango Web UI.

---

## Overview

**Base URL:** `http://localhost:8800` (configurable via `platform.port` in `project.yml`)

**Authentication methods:**

- **Cookie session** --- login via `POST /api/auth/login`, session cookie set automatically
- **API key** --- `Authorization: Bearer dango_ak_...` header (see [API Key Auth](permissions.md#api-key-authentication))

**Interactive documentation:**

- Swagger UI: `http://localhost:8800/api/docs`
- ReDoc: `http://localhost:8800/api/redoc`

---

## Endpoint Summary

### Health & Status

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/status` | None | Service health status |
| GET | `/api/watcher/status` | None | File watcher status |
| GET | `/api/health/platform` | None | Comprehensive platform health |
| GET | `/api/deployments/history` | `platform.manage` | Deployment history (cloud only) |

### Configuration

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/config` | None | Project config and service URLs |
| GET | `/api/metabase-config` | None | Metabase database ID |

### Authentication

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/auth/login` | None (public) | Authenticate with credentials |
| POST | `/api/auth/logout` | Authenticated | Invalidate session |
| GET | `/api/auth/me` | None (public) | Current user or auth-disabled indicator |
| POST | `/api/auth/change-password` | Authenticated | Change password |
| GET | `/api/auth/sessions` | Authenticated | List active sessions |
| DELETE | `/api/auth/sessions/{session_id}` | Authenticated | Revoke a session |
| POST | `/api/auth/api-keys` | Authenticated | Create API key |
| GET | `/api/auth/api-keys` | Authenticated | List API keys |
| DELETE | `/api/auth/api-keys/{key_id}` | Authenticated | Revoke API key |
| POST | `/api/auth/accept-invite` | None (public) | Accept invite and set password |
| GET | `/api/auth/oauth/{provider}/login` | None (public) | Redirect to OAuth provider |
| GET | `/api/auth/oauth/{provider}/callback` | None (public) | Handle OAuth callback |

### Two-Factor Authentication

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/auth/2fa/setup` | Authenticated | Begin 2FA setup (generate secret) |
| POST | `/api/auth/2fa/verify-setup` | Authenticated | Complete 2FA setup with TOTP code |
| POST | `/api/auth/2fa/verify` | Partial session | Verify TOTP/recovery code |
| POST | `/api/auth/2fa/disable` | Authenticated | Disable 2FA |
| POST | `/api/auth/2fa/regenerate-recovery` | Authenticated | Regenerate recovery codes |

### User Management

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/admin/users` | `users.manage` | List all users |
| POST | `/api/admin/users` | `users.manage` | Create user |
| POST | `/api/admin/users/{id}/reinvite` | `users.manage` | Resend invite |
| PUT | `/api/admin/users/{id}/role` | `users.manage` | Change user role |
| POST | `/api/admin/users/{id}/reset-password` | `users.manage` | Reset password |
| POST | `/api/admin/users/{id}/deactivate` | `users.manage` | Deactivate user |
| POST | `/api/admin/users/{id}/reactivate` | `users.manage` | Reactivate user |
| DELETE | `/api/admin/users/{id}` | `users.manage` | Delete user |
| POST | `/api/admin/users/{id}/unlock` | `users.manage` | Unlock locked account |
| POST | `/api/admin/users/{id}/revoke-sessions` | `users.manage` | Revoke all user sessions |

### Sources

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/sources` | None | List sources with status |
| GET | `/api/sources/{name}/details` | None | Source details, config, history |

### Sync

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/sources/{name}/sync` | `source.sync` | Trigger source sync |
| POST | `/api/sync/trigger` | `source.sync` | Trigger multi-source sync |
| GET | `/api/sync/status/{record_id}` | `source.sync` | Poll sync job status |

### CSV Operations

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/sources/{name}/upload-csv` | `csv.upload` | Upload CSV/JSON/Parquet file |
| GET | `/api/sources/{name}/csv-files` | None | List files for source |
| DELETE | `/api/sources/{name}/csv-files` | `csv.delete` | Delete a file |

### dbt Operations

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/dbt/models` | None | List dbt models |
| POST | `/api/dbt/models/{name}/run` | `dbt.run` | Run specific dbt model |

### Logs

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/sources/{name}/logs` | None | Source sync logs |
| GET | `/api/logs` | None | All activity logs |

### Secrets & OAuth

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/secrets` | `config.manage` | List env vars (masked) |
| POST | `/api/secrets` | `config.manage` | Add/update env var |
| DELETE | `/api/secrets/{key}` | `config.manage` | Delete env var |
| GET | `/api/secrets/oauth` | `config.manage` | OAuth credential status |
| DELETE | `/api/secrets/oauth/{source_type}` | `config.manage` | Disconnect OAuth |
| GET | `/oauth/connect/{source_type}` | `config.manage` | Initiate OAuth flow |
| GET | `/oauth/callback/{source_type}` | `config.manage` | OAuth callback |

### Data Catalog

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/catalog/{source}/{table}/columns` | `governance.view` | Column schema + profiling |
| POST | `/api/catalog/{source}/{table}/profile` | `governance.view` | Compute fresh profiling |
| GET | `/api/catalog/models` | `governance.view` | List models + sources |
| GET | `/api/catalog/models/{model_name}` | `governance.view` | Model details + lineage |
| GET | `/api/catalog/search` | `governance.view` | Search models/sources |
| GET | `/api/catalog/lineage` | `governance.view` | Full lineage DAG |
| GET | `/api/catalog/impact/{model_name}` | `governance.view` | Downstream impact |

### Governance

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/governance/schema-drift` | `governance.view` | Schema drift events |
| GET | `/api/governance/pii` | `governance.view` | PII findings |
| GET | `/api/governance/pii/overrides` | `governance.view` | PII overrides |
| POST | `/api/governance/drift/{source}/accept` | `governance.manage` | Accept schema drift |
| GET | `/api/governance/attention` | `governance.view` | Sources needing attention |

### Monitoring

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/monitoring` | `governance.view` | Cached analysis results |
| POST | `/api/monitoring/run` | `governance.view` | Execute fresh analysis |
| GET | `/api/monitoring/history` | `governance.view` | Metric value history |

### Schedules

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/schedules` | `scheduler.view` | List all schedules |
| GET | `/api/schedules/{name}` | `scheduler.view` | Schedule details |
| GET | `/api/schedules/{name}/history` | `scheduler.view` | Execution history |
| GET | `/api/schedules/history/recent` | `scheduler.view` | Recent executions |
| POST | `/api/schedules/{name}/trigger` | `source.sync` | Manually trigger schedule |
| POST | `/api/schedules/reload` | `scheduler.manage` | Reload from YAML |
| POST | `/api/schedules/jobs/{job_id}/cancel` | `scheduler.manage` | Cancel running job |
| GET | `/api/sources/unscheduled` | `scheduler.view` | Unscheduled sources |
| GET | `/api/notifications/config` | `scheduler.view` | Notification config |
| POST | `/api/notifications/test` | `scheduler.manage` | Send test notification |

### Notebooks

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/notebooks` | `notebooks.view` | List notebooks |
| POST | `/api/notebooks` | `notebooks.execute` | Create notebook |
| DELETE | `/api/notebooks/{name}` | `notebooks.execute` | Delete notebook |
| POST | `/api/notebooks/{name}/lock` | `notebooks.execute` | Acquire editing lock |
| POST | `/api/notebooks/{name}/heartbeat` | `notebooks.execute` | Refresh lock |
| POST | `/api/notebooks/{name}/release` | `notebooks.execute` | Release lock |
| DELETE | `/api/notebooks/{name}/lock` | `notebooks.manage` | Force-release lock |
| POST | `/api/notebooks/{name}/copy` | `notebooks.execute` | Copy notebook |

### Query

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/query` | `query.execute` | Execute ad-hoc SELECT query |

### AI / Agent

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/api/catalog/summary` | `source.view` | Machine-readable catalog summary |
| GET | `/api/tools` | `source.view` | Available API tools for agents |

### Initial Sync (Deploy)

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| POST | `/api/initial-sync/start` | Deploy token / Admin | Start initial sync |
| GET | `/api/initial-sync/status` | Deploy token / Admin | Sync progress |
| POST | `/api/initial-sync/skip-source` | Admin | Skip current source |
| POST | `/api/initial-sync/cancel` | Admin | Cancel initial sync |

### WebSocket

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| WS | `/ws` | Authenticated | Real-time platform events |

---

## Endpoint Details

### Health & Status

#### GET /api/status

Get service health status for DuckDB, Metabase, and dbt docs.

**Permission:** None (public)

??? example "Response"
    ```json
    {
      "status": "healthy",
      "dango_version": "1.0.0b1",
      "services": {
        "api": "running",
        "duckdb": "healthy",
        "metabase": "healthy",
        "dbt_docs": "healthy"
      },
      "uptime": "N/A"
    }
    ```

#### GET /api/watcher/status

Get file watcher status and configuration.

**Permission:** None (public)

??? example "Response"
    ```json
    {
      "running": true,
      "pid": 12345,
      "auto_sync_enabled": true,
      "auto_dbt_enabled": true,
      "debounce_seconds": 600,
      "watch_patterns": ["*.csv", "*.json", "*.jsonl", "*.ndjson", "*.parquet"],
      "watch_directories": ["data/uploads"]
    }
    ```

#### GET /api/health/platform

Comprehensive platform health including database size, disk space, sync failures, cloud resource metrics, backup health, and OAuth token health.

**Permission:** None (public)

??? example "Response"
    ```json
    {
      "status": "healthy",
      "timestamp": "2026-05-17T10:30:00Z",
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

#### GET /api/deployments/history

Deployment history from the deploy journal. Cloud deployments only.

**Permission:** `platform.manage`

---

### Configuration

#### GET /api/config

Get Dango configuration including service URLs.

**Permission:** None (public)

??? example "Response"
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

#### GET /api/metabase-config

Get Metabase configuration including database ID.

**Permission:** None (public)

??? example "Response"
    ```json
    {
      "database_id": 2,
      "configured": true
    }
    ```

---

### Authentication

#### POST /api/auth/login

Authenticate with email and password. Sets a session cookie on success.

**Permission:** None (public)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `email` | body | string | Yes | User email |
| `password` | body | string | Yes | User password |

??? example "Response"
    ```json
    {
      "status": "ok",
      "user": {
        "id": "...",
        "email": "admin@localhost",
        "role": "admin",
        "display_name": "Admin"
      }
    }
    ```

If the user has 2FA enabled, a partial session is returned and `POST /api/auth/2fa/verify` must be called next.

#### POST /api/auth/logout

Invalidate the current session.

**Permission:** Authenticated

#### GET /api/auth/me

Get the current user. Returns auth-disabled indicator if authentication is turned off.

**Permission:** None (public)

#### POST /api/auth/change-password

Change the current user's password.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `current_password` | body | string | Yes | Current password |
| `new_password` | body | string | Yes | New password |

#### GET /api/auth/sessions

List active sessions for the current user.

**Permission:** Authenticated

#### DELETE /api/auth/sessions/{session_id}

Revoke a specific session.

**Permission:** Authenticated

#### POST /api/auth/api-keys

Create a new API key.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `name` | body | string | Yes | Key name |
| `expires_at` | body | datetime | No | Optional expiry date |

??? example "Response"
    ```json
    {
      "key": "dango_ak_...",
      "id": "...",
      "name": "my-key",
      "key_prefix": "dango_ak_XYZ"
    }
    ```

!!! warning
    The full key is only returned once at creation time. Store it securely.

#### GET /api/auth/api-keys

List API keys (prefix and metadata only, not full keys).

**Permission:** Authenticated

#### DELETE /api/auth/api-keys/{key_id}

Revoke an API key.

**Permission:** Authenticated

#### POST /api/auth/accept-invite

Accept an invitation and set a password.

**Permission:** None (public, requires valid invite token)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `token` | body | string | Yes | Invite token |
| `password` | body | string | Yes | New password |
| `display_name` | body | string | No | Display name |

#### GET /api/auth/oauth/{provider_name}/login

Redirect to an OAuth provider (Google, GitHub) for login.

**Permission:** None (public)

#### GET /api/auth/oauth/{provider_name}/callback

Handle OAuth provider callback after authorization.

**Permission:** None (public)

---

### Two-Factor Authentication

#### POST /api/auth/2fa/setup

Begin 2FA setup. Verifies password, generates TOTP secret and recovery codes.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `password` | body | string | Yes | Current password (verification) |

??? example "Response"
    ```json
    {
      "secret": "JBSWY3DPEHPK3PXP",
      "provisioning_uri": "otpauth://totp/Dango:admin@localhost?...",
      "recovery_codes": ["ABCD-1234", "EFGH-5678", "..."]
    }
    ```

#### POST /api/auth/2fa/verify-setup

Complete 2FA setup by verifying a TOTP code from the authenticator app.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `code` | body | string | Yes | 6-digit TOTP code |

#### POST /api/auth/2fa/verify

Verify a TOTP code or recovery code to upgrade a partial session to a full session. Called after login when 2FA is enabled.

**Permission:** Partial session (public with valid partial session cookie)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `code` | body | string | Yes | TOTP code or recovery code |

#### POST /api/auth/2fa/disable

Disable 2FA for the current user.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `password` | body | string | Yes | Current password (verification) |

#### POST /api/auth/2fa/regenerate-recovery

Regenerate recovery codes. Requires both password and TOTP verification.

**Permission:** Authenticated

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `password` | body | string | Yes | Current password |
| `code` | body | string | Yes | Current TOTP code |

---

### User Management

All user management endpoints require `users.manage` permission (admin only).

#### GET /api/admin/users

List all users with roles, status, and last login.

#### POST /api/admin/users

Create a new user.

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `email` | body | string | Yes | User email |
| `role` | body | string | Yes | Role: `admin`, `editor`, `viewer` |
| `display_name` | body | string | No | Display name |

#### POST /api/admin/users/{user_id}/reinvite

Resend an invite link to a user who hasn't accepted yet.

#### PUT /api/admin/users/{user_id}/role

Change a user's role.

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `role` | body | string | Yes | New role: `admin`, `editor`, `viewer` |

#### POST /api/admin/users/{user_id}/reset-password

Generate a password reset link for a user.

#### POST /api/admin/users/{user_id}/deactivate

Deactivate a user (preserves account, revokes access).

#### POST /api/admin/users/{user_id}/reactivate

Reactivate a previously deactivated user.

#### DELETE /api/admin/users/{user_id}

Permanently delete a user.

#### POST /api/admin/users/{user_id}/unlock

Unlock an account that was locked due to too many failed login attempts.

#### POST /api/admin/users/{user_id}/revoke-sessions

Revoke all active sessions for a user (forces re-login).

---

### Sources

#### GET /api/sources

List all configured sources with sync status, row counts, freshness, schedule info, and attention flags.

**Permission:** None (public)

??? example "Response"
    ```json
    [
      {
        "name": "stripe_payments",
        "type": "stripe",
        "enabled": true,
        "last_sync": "2026-05-17T08:00:00Z",
        "row_count": 1523,
        "status": "synced",
        "freshness": {
          "last_update": "2026-05-17T08:00:00Z",
          "days_old": 0
        },
        "tables": [
          {"name": "charges", "row_count": 1000, "schema": "raw_stripe"},
          {"name": "customers", "row_count": 523, "schema": "raw_stripe"}
        ]
      }
    ]
    ```

**Status values:** `synced`, `syncing`, `failed`, `empty`, `not_synced`, `unknown`

#### GET /api/sources/{source_name}/details

Get detailed source information including masked config, sync history, freshness, tables, and sync mode.

**Permission:** None (public)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source_name` | path | string | Yes | Source name |

---

### Sync

#### POST /api/sources/{source_name}/sync

Trigger a data sync for a single source.

**Permission:** `source.sync`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source_name` | path | string | Yes | Source name |
| `full_refresh` | body | boolean | No | Force full refresh (default: false) |
| `start_date` | body | string | No | Start date (YYYY-MM-DD) |
| `end_date` | body | string | No | End date (YYYY-MM-DD) |

??? example "Response"
    ```json
    {
      "success": true,
      "message": "Sync started for stripe_payments",
      "source_name": "stripe_payments",
      "started_at": "2026-05-17T10:30:00Z"
    }
    ```

#### POST /api/sync/trigger

Trigger a manual sync for multiple sources with execution tracking.

**Permission:** `source.sync`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `sources` | body | list[string] | Yes | Source names to sync |
| `full_refresh` | body | boolean | No | Force full refresh |

#### GET /api/sync/status/{record_id}

Poll execution status for a manual sync job.

**Permission:** `source.sync`

---

### CSV Operations

#### POST /api/sources/{source_name}/upload-csv

Upload a CSV, JSON, or Parquet file to a source.

**Permission:** `csv.upload`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source_name` | path | string | Yes | Source name |
| `file` | body (multipart) | file | Yes | File to upload |
| `trigger_sync` | query | boolean | No | Trigger sync after upload (default: false) |

#### GET /api/sources/{source_name}/csv-files

List files for a source (on disk and loaded in database).

**Permission:** None (public)

#### DELETE /api/sources/{source_name}/csv-files

Delete a file from the filesystem.

**Permission:** `csv.delete`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `file_path` | query | string | Yes | Full path to file |

---

### dbt Operations

#### GET /api/dbt/models

List all dbt models with metadata.

**Permission:** None (public)

#### POST /api/dbt/models/{model_name}/run

Run a specific dbt model.

**Permission:** `dbt.run`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `model_name` | path | string | Yes | Model name |
| `cascade` | query | boolean | No | Run downstream models (default: true) |

---

### Logs

#### GET /api/sources/{source_name}/logs

Get sync logs for a specific source.

**Permission:** None (public)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source_name` | path | string | Yes | Source name |
| `limit` | query | integer | No | Maximum entries (default: 100) |

#### GET /api/logs

Get all activity logs.

**Permission:** None (public)

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `limit` | query | integer | No | Maximum entries (default: 1000) |

---

### Secrets & OAuth

All secrets endpoints require `config.manage` permission (admin only).

#### GET /api/secrets

List environment variables and OAuth credentials (values masked).

#### POST /api/secrets

Add or update an environment variable.

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `key` | body | string | Yes | Variable name |
| `value` | body | string | Yes | Variable value |

#### DELETE /api/secrets/{key}

Delete an environment variable.

#### GET /api/secrets/oauth

List OAuth credential status for all providers.

#### DELETE /api/secrets/oauth/{source_type}

Disconnect OAuth credentials for a source type.

#### GET /oauth/connect/{source_type}

Initiate OAuth flow for a source. Cloud deployments only.

#### GET /oauth/callback/{source_type}

Handle OAuth provider callback.

---

### Data Catalog

All catalog endpoints require `governance.view` permission.

#### GET /api/catalog/{source}/{table}/columns

Get column schema and cached profiling statistics for a table.

#### POST /api/catalog/{source}/{table}/profile

Compute fresh profiling statistics for a table.

#### GET /api/catalog/models

List all dbt models and sources with overview summary from the dbt manifest.

#### GET /api/catalog/models/{model_name}

Get model or source details: columns, SQL code, tests, dependencies, and lineage.

#### GET /api/catalog/search

Search models and sources by name, description, or column names.

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `q` | query | string | Yes | Search query |

#### GET /api/catalog/lineage

Get the full lineage DAG (nodes and edges) across all models.

#### GET /api/catalog/impact/{model_name}

Get the downstream impact tree for a specific model.

---

### Governance

#### GET /api/governance/schema-drift

Query schema drift events with optional source/table filters.

**Permission:** `governance.view`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source` | query | string | No | Filter by source |
| `table` | query | string | No | Filter by table |

#### GET /api/governance/pii

Query PII findings with optional filters.

**Permission:** `governance.view`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source` | query | string | No | Filter by source |
| `table` | query | string | No | Filter by table |

#### GET /api/governance/pii/overrides

List PII column overrides.

**Permission:** `governance.view`

#### POST /api/governance/drift/{source}/accept

Accept schema drift for a source and clear the attention flag.

**Permission:** `governance.manage`

#### GET /api/governance/attention

Get sources that need attention (schema drift, PII detected, sync failures).

**Permission:** `governance.view`

---

### Monitoring

#### GET /api/monitoring

Read cached metric analysis results.

**Permission:** `governance.view`

#### POST /api/monitoring/run

Execute a fresh metric analysis run.

**Permission:** `governance.view`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `source` | query | string | No | Filter to a specific source |

#### GET /api/monitoring/history

Get historical metric values.

**Permission:** `governance.view`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `days` | query | integer | No | Number of days of history |

---

### Schedules

#### GET /api/schedules

List all schedules with runtime status (next run, last run, active jobs).

**Permission:** `scheduler.view`

#### GET /api/schedules/{name}

Get detailed schedule information.

**Permission:** `scheduler.view`

#### GET /api/schedules/{name}/history

Get paginated execution history for a schedule.

**Permission:** `scheduler.view`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `limit` | query | integer | No | Max entries |
| `offset` | query | integer | No | Pagination offset |

#### GET /api/schedules/history/recent

Get recent executions across all schedules.

**Permission:** `scheduler.view`

#### POST /api/schedules/{name}/trigger

Manually trigger a schedule execution.

**Permission:** `source.sync`

#### POST /api/schedules/reload

Reload schedules from the YAML configuration file.

**Permission:** `scheduler.manage`

#### POST /api/schedules/jobs/{job_id}/cancel

Cancel a currently running scheduled job.

**Permission:** `scheduler.manage`

#### GET /api/sources/unscheduled

List sources that don't have any schedule assigned.

**Permission:** `scheduler.view`

#### GET /api/notifications/config

Get the current notification configuration.

**Permission:** `scheduler.view`

#### POST /api/notifications/test

Send a test notification to all configured webhooks.

**Permission:** `scheduler.manage`

---

### Notebooks

#### GET /api/notebooks

List notebooks with metadata and lock status.

**Permission:** `notebooks.view`

#### POST /api/notebooks

Create a notebook from a template.

**Permission:** `notebooks.execute`

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `name` | body | string | Yes | Notebook name |
| `template` | body | string | No | Template: `blank`, `explore`, `quality` |

#### DELETE /api/notebooks/{name}

Delete a notebook.

**Permission:** `notebooks.execute`

#### POST /api/notebooks/{name}/lock

Acquire an editing lock and start the Marimo server.

**Permission:** `notebooks.execute`

#### POST /api/notebooks/{name}/heartbeat

Refresh the lock expiry (keep the editing session alive).

**Permission:** `notebooks.execute`

#### POST /api/notebooks/{name}/release

Release the editing lock.

**Permission:** `notebooks.execute`

#### DELETE /api/notebooks/{name}/lock

Force-release another user's lock (admin operation).

**Permission:** `notebooks.manage`

#### POST /api/notebooks/{name}/copy

Copy a locked notebook.

**Permission:** `notebooks.execute`

---

### Query

#### POST /api/query

Execute an ad-hoc read-only SQL query against DuckDB.

**Permission:** `query.execute`

**Security layers:**

1. SQL parsed by `sqlglot` to validate syntax
2. AST walked to reject write statements (INSERT, UPDATE, DELETE, DROP)
3. DuckDB connection opened in `read_only` mode
4. Result limited to 10,000 rows
5. SQL input limited to 100 KB
6. 30-second query timeout

| Parameter | In | Type | Required | Description |
|-----------|:--:|------|:--------:|-------------|
| `sql` | body | string | Yes | SQL SELECT query |

??? example "Response"
    ```json
    {
      "columns": ["id", "amount", "currency"],
      "rows": [
        [1, 2500, "usd"],
        [2, 1000, "eur"]
      ],
      "row_count": 2,
      "truncated": false
    }
    ```

---

### AI / Agent

#### GET /api/catalog/summary

Machine-readable catalog summary for LLM/agent consumption. Includes table schemas, freshness, and quality signals.

**Permission:** `source.view` (full data requires `governance.view`)

#### GET /api/tools

Descriptions of all available API tools for agent use.

**Permission:** `source.view`

---

### Initial Sync

These endpoints are used during the first cloud deployment to sync data. They accept either a deploy token (one-time use) or an admin session.

#### POST /api/initial-sync/start

Start the initial data sync.

#### GET /api/initial-sync/status

Get current sync progress.

#### POST /api/initial-sync/skip-source

Skip the currently syncing source.

**Permission:** Admin only

#### POST /api/initial-sync/cancel

Cancel the entire initial sync.

**Permission:** Admin only

---

### WebSocket

#### WS /ws

Real-time updates for platform events. Requires an authenticated session.

**Connection:** `ws://localhost:8800/ws`

**Event types:**

```json
{"type": "sync_started", "source": "stripe_payments", "timestamp": "..."}
{"type": "sync_completed", "source": "stripe_payments", "rows": 1523, "timestamp": "..."}
{"type": "sync_failed", "source": "stripe_payments", "error": "...", "timestamp": "..."}
{"type": "dbt_run_started", "model": "customer_metrics", "timestamp": "..."}
{"type": "dbt_run_completed", "model": "customer_metrics", "timestamp": "..."}
{"type": "csv_uploaded", "source": "sales_data", "file": "sales.csv", "timestamp": "..."}
{"type": "freshness_update", "source": "stripe_payments", "timestamp": "..."}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (not authenticated) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Resource not found |
| 409 | Conflict (e.g., sync already in progress) |
| 422 | Validation error |
| 429 | Rate limited |
| 500 | Internal server error |
| 502 | Bad gateway (upstream service unavailable) |

**Error response format:**

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
| `/metabase/*` | `localhost:3000` | Metabase dashboard (with SSO session bridging) |
| `/dbt-docs/*` | `localhost:8081` | dbt documentation |
| `/manifest.json` | `localhost:8081` | dbt manifest |
| `/catalog.json` | `localhost:8081` | dbt catalog |
| `/app/*` | `localhost:3000` | Metabase app assets |
| `/public/*` | `localhost:3000` | Metabase public assets |
| `/styles.css` | `localhost:3000` | Metabase stylesheets |

---

## Page Routes

These routes return HTML pages (not JSON APIs):

| Path | Description |
|------|-------------|
| `/` | Dashboard |
| `/sources` | Sources page |
| `/models` | dbt models page |
| `/health` | Platform health |
| `/logs` | Activity logs |
| `/catalog` | Data catalog |
| `/schedules` | Schedule management |
| `/notebooks` | Notebook management |
| `/login` | Login page |
| `/setup` | First-login password change |
| `/invite/{token}` | Invite acceptance |
| `/settings/users` | Admin user management |
| `/settings/account` | User account settings |
| `/settings/secrets` | Admin secrets management |
| `/query` | Redirect to Metabase query |

---

## Usage Examples

### curl

```bash
# Authenticate and save session cookie
curl -c cookies.txt -X POST http://localhost:8800/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@localhost", "password": "your-password"}'

# Use session cookie for subsequent requests
curl -b cookies.txt http://localhost:8800/api/sources

# Or use API key
curl -H "Authorization: Bearer dango_ak_..." http://localhost:8800/api/sources

# Trigger sync
curl -b cookies.txt -X POST http://localhost:8800/api/sources/stripe_payments/sync \
  -H "Content-Type: application/json" \
  -d '{"full_refresh": false}'

# Upload CSV
curl -b cookies.txt -X POST http://localhost:8800/api/sources/sales_data/upload-csv \
  -F "file=@sales.csv"

# Execute query
curl -b cookies.txt -X POST http://localhost:8800/api/query \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM raw_stripe.charges LIMIT 10"}'
```

### Python

```python
import requests

base = "http://localhost:8800"

# Login
session = requests.Session()
session.post(f"{base}/api/auth/login", json={
    "email": "admin@localhost",
    "password": "your-password"
})

# List sources
sources = session.get(f"{base}/api/sources").json()

# Trigger sync
session.post(f"{base}/api/sources/stripe_payments/sync",
             json={"full_refresh": False})

# Or use API key
headers = {"Authorization": "Bearer dango_ak_..."}
sources = requests.get(f"{base}/api/sources", headers=headers).json()
```

### JavaScript

```javascript
// WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8800/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.type, data);
};

// REST API with fetch
const response = await fetch('/api/sources', {
  credentials: 'include'  // include session cookie
});
const sources = await response.json();
```

---

## Related Pages

- [Permissions Matrix](permissions.md) --- Role and permission reference
- [Configuration Reference](configuration.md) --- Config file schemas
- [CLI Reference](../cli/cli-reference.md) --- Command-line interface
