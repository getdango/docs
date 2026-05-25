# Configuration Reference

Complete reference for all Dango configuration files and schemas.

---

## Overview

Dango uses several configuration files organized across three directories:

| File | Purpose | Sensitive | User-Edited |
|------|---------|:---------:|:-----------:|
| [`.dango/project.yml`](#project-yml) | Project metadata, platform settings, auth config | No | Yes |
| [`.dango/sources.yml`](#sources-yml) | Data source definitions | No | Yes |
| [`.dango/schedules.yml`](#schedules-yml) | Scheduled sync/dbt jobs and notifications | No | Yes |
| [`.dango/monitors.yml`](#monitors-yml) | Metric monitoring and alert definitions | No | Yes |
| [`.dango/cloud.yml`](#cloud-yml) | Cloud deployment state | No | Rarely |
| [`.dango/pii-overrides.yml`](#pii-overrides-yml) | PII column override decisions | No | Yes |
| [`.dango/metabase.yml`](#metabase-yml) | Metabase admin credentials and database ID | **Yes** | No |
| [`.env`](#env) | Environment variables | **Yes** | Yes |
| [`.dlt/secrets.toml`](#secrets-toml) | Source API keys and OAuth tokens | **Yes** | Yes |
| [`.dlt/config.toml`](#config-toml) | Non-sensitive dlt parameters | No | Rarely |
| [`dbt/profiles.yml`](#dbt-profiles-yml) | DuckDB connection config for dbt | No | No |
| [`dbt/dbt_project.yml`](#dbt-project-yml) | dbt project config | No | Rarely |
| [`docker-compose.yml`](#docker-compose-yml) | Metabase container config | No | No |

---

## `.dango/project.yml` { #project-yml }

Project metadata, platform settings, and authentication configuration. Created by `dango init`.

### `project` Section

```yaml
project:
  name: my-analytics
  organization: Acme Corp
  dango_version: 1.0.0b1
  created: '2026-01-15T10:30:00'
  created_by: data-team@acme.com
  purpose: Track sales performance and customer behavior
  stakeholders:
    - name: Sarah Chen
      role: CMO - Dashboard user
      contact: sarah@acme.com
  sla: Daily by 9am UTC
  limitations: Stripe data has 24h delay
  getting_started: |
    1. Run 'dango sync'
    2. Open http://localhost:8800
```

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `name` | string | Yes | Project name |
| `organization` | string | No | Organization name |
| `dango_version` | string | No | Dango version used to create the project |
| `created` | datetime | Yes | Creation timestamp (auto-populated) |
| `created_by` | string | Yes | Creator email or name |
| `purpose` | string | Yes | Why this project exists |
| `stakeholders` | list | No | Project stakeholders (each with `name`, `role`, `contact`) |
| `sla` | string | No | Data freshness SLA |
| `limitations` | string | No | Known limitations or caveats |
| `getting_started` | string | No | Quick start guide for new team members |

### `platform` Section

```yaml
platform:
  duckdb_path: ./data/warehouse.duckdb
  dbt_project_dir: ./dbt
  data_dir: ./data
  port: 8800
  metabase_port: 3000
  dbt_docs_port: 8081
  marimo_port: 7805
  auto_sync: true
  auto_dbt: true
  debounce_seconds: 600
  dbt_coalesce_seconds: 10
  workers: null
  watch_patterns:
    - '*.csv'
    - '*.json'
    - '*.jsonl'
    - '*.ndjson'
    - '*.parquet'
  watch_directories:
    - data/uploads
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `duckdb_path` | string | `./data/warehouse.duckdb` | Path to DuckDB database |
| `dbt_project_dir` | string | `./dbt` | Path to dbt project |
| `data_dir` | string | `./data` | Data directory path |
| `port` | integer | `8800` | Web UI and API port |
| `metabase_port` | integer | `3000` | Metabase dashboard port |
| `dbt_docs_port` | integer | `8081` | dbt documentation port |
| `marimo_port` | integer | `7805` | Marimo notebooks port |
| `auto_sync` | boolean | `true` | Auto-sync when watched files change |
| `auto_dbt` | boolean | `true` | Auto-run dbt after sync completes |
| `debounce_seconds` | integer | `600` | Seconds to wait before triggering auto-sync (10 min) |
| `dbt_coalesce_seconds` | integer | `10` | Seconds to wait before dbt run (coalesces multiple syncs) |
| `workers` | integer | `null` | Uvicorn worker count (`null` = 1 local, auto-detect cloud vCPUs) |
| `watch_patterns` | list[string] | `["*.csv", "*.json", "*.jsonl", "*.ndjson", "*.parquet"]` | Glob patterns for file watch |
| `watch_directories` | list[string] | `["data/uploads"]` | Directories to watch (relative to project root) |

### `auth` Section

```yaml
auth:
  enabled: true
  idle_timeout_minutes: 1440   # 24 hours
  session_max_days: 365        # 1 year
  password_max_age_days: 0     # disabled (0 = no forced rotation)
  require_2fa: false
  rate_limit:
    enabled: true
    login:
      requests: 10
      window_seconds: 60
    api:
      requests: 200
      window_seconds: 60
    trusted_proxies: []
  lockout:
    max_attempts: 5
    lockout_minutes: 15
  oauth_providers: {}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable authentication |
| `idle_timeout_minutes` | integer | `1440` (24h) | Session idle timeout in minutes |
| `session_max_days` | integer | `365` (1 year) | Maximum session lifetime in days |
| `password_max_age_days` | integer | `0` (disabled) | Force password change after this many days. `0` disables rotation. When expired, user is redirected to the change-password page on next login. OAuth login bypasses rotation. |
| `require_2fa` | boolean | `false` | Require all users to set up TOTP 2FA |
| `rate_limit.enabled` | boolean | `true` | Enable rate limiting |
| `rate_limit.login.requests` | integer | `10` | Max login attempts per window |
| `rate_limit.login.window_seconds` | integer | `60` | Login rate limit window |
| `rate_limit.api.requests` | integer | `200` | Max API requests per window |
| `rate_limit.api.window_seconds` | integer | `60` | API rate limit window |
| `rate_limit.trusted_proxies` | list[string] | `[]` | IPs of trusted reverse proxies |
| `lockout.max_attempts` | integer | `5` | Failed attempts before lockout |
| `lockout.lockout_minutes` | integer | `15` | Lockout duration in minutes |
| `oauth_providers` | dict | `{}` | OAuth login providers (keyed by `google`, `github`) with `client_id` and `client_secret` |

!!! info "Cloud deployment defaults differ"
    During `dango deploy`, the auth section is configured with shorter timeouts for security: `idle_timeout_minutes: 60` and `session_max_days: 30`.

### `api` Section { #api-section }

```yaml
api:
  query_max_rows: 10000
  query_timeout_seconds: 30
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `query_max_rows` | integer | `10000` | Maximum rows returned by `POST /api/query`. Increase for scheduled reporting scripts pulling large datasets. |
| `query_timeout_seconds` | integer | `30` | Query timeout in seconds. Increase for complex analytical queries. |

---

## `.dango/sources.yml` { #sources-yml }

Data source definitions and configuration. Managed via `dango source add` or manual editing.

### Structure

```yaml
version: '1.0'
sources:
  - name: source_name
    type: source_type
    enabled: true
    description: Human-readable description
    tags: [tag1, tag2]
    lookback_days: 7
    # Type-specific config block (one of the options below)
```

### Common Fields

| Field | Type | Required | Default | Description |
|-------|------|:--------:|---------|-------------|
| `name` | string | Yes | -- | Unique source name (lowercase alphanumeric + underscore) |
| `type` | SourceType | Yes | -- | Source type (see [Source Registry](source-registry.md)) |
| `enabled` | boolean | No | `true` | Whether to include in syncs |
| `description` | string | No | -- | Human-readable description |
| `tags` | list[string] | No | `[]` | Metadata tags |
| `lookback_days` | integer | No | -- | Re-load this many days on incremental sync |

### Type-Specific Configuration

Each source type has its own configuration block. Sources with a dedicated Pydantic model use a typed config key (e.g., `stripe:`, `hubspot:`). Sources without a dedicated model use `generic_config:`.

**Typed config examples:**

```yaml
# Stripe
- name: stripe_payments
  type: stripe
  stripe:
    stripe_secret_key_env: STRIPE_API_KEY
    endpoints: [charges, customers, invoices]
    start_date: '2024-01-01'

# HubSpot
- name: hubspot_crm
  type: hubspot
  hubspot:
    api_key_env: HUBSPOT_API_KEY
    resources: [contacts, companies, deals]

# GitHub
- name: my_repo
  type: github
  github:
    access_token_env: GITHUB_ACCESS_TOKEN
    owner: my-org
    name: my-repo

# Slack
- name: slack_data
  type: slack
  slack:
    access_token_env: SLACK_ACCESS_TOKEN
    selected_channels: [C01234ABCDE]
```

**`generic_config` example (21+ source types):**

```yaml
# Zendesk (uses generic_config)
- name: zendesk_support
  type: zendesk
  generic_config:
    subdomain: mycompany
    email: support@mycompany.com
```

For the complete list of source types, typed config fields, and which sources use `generic_config`, see the [Source Registry](source-registry.md).

---

## `.dango/schedules.yml` { #schedules-yml }

Scheduled sync and dbt jobs with notification configuration. Managed via `dango schedule add` or manual editing.

### Structure

```yaml
schedules:
  - name: hourly_sync
    type: sync
    cron: every_hour
    sources: [stripe_payments, hubspot_crm]
    enabled: true
    timezone: America/New_York
    notify_on: [failure, stale]

  - name: daily_transforms
    type: dbt
    cron: daily
    dbt_command: dbt run
    enabled: true

notifications:
  webhooks:
    - name: slack_alerts
      url: https://hooks.slack.com/services/T.../B.../xxx
      format: slack
    - name: generic_webhook
      url: https://api.example.com/webhook
      format: generic
  on_failure: true
  on_success: true
  on_stale: true
  on_governance: true
  on_analysis: true
  stale_threshold_hours: 24
```

### Schedule Fields

| Field | Type | Required | Default | Description |
|-------|------|:--------:|---------|-------------|
| `name` | string | Yes | -- | Schedule name (lowercase alphanumeric + underscore, starts with letter) |
| `type` | ScheduleType | No | `sync` | Schedule type: `sync`, `sync_only`, `dbt` |
| `cron` | string | Yes | -- | Cron expression or preset name |
| `sources` | list[string] | Yes* | -- | Source names to sync (*required for `sync`/`sync_only` types) |
| `enabled` | boolean | No | `true` | Enable this schedule |
| `timezone` | string | No | server TZ | Timezone for cron evaluation |
| `start_date` | datetime | No | -- | First execution date |
| `misfire_grace_time` | integer | No | -- | Seconds to wait before skipping missed execution |
| `timeout_minutes` | integer | No | -- | Execution timeout |
| `notify_on` | list[string] | No | `[]` | Override notification triggers: `failure`, `success`, `stale` |
| `dbt_command` | string | No* | -- | dbt command to run (*required for `dbt` type) |

### Schedule Types

| Type | Behavior |
|------|----------|
| `sync` | Sync selected sources, then run dbt (recommended) |
| `sync_only` | Sync selected sources without running dbt afterward |
| `dbt` | Run a dbt command only (no sync) |

### Cron Presets

| Preset | Cron Expression | Description |
|--------|----------------|-------------|
| `every_15m` | `*/15 * * * *` | Every 15 minutes |
| `every_hour` | `0 * * * *` | Top of every hour |
| `every_6h` | `0 */6 * * *` | Every 6 hours |
| `daily` | `0 6 * * *` | Daily at 6 AM |
| `weekly` | `0 6 * * 1` | Monday at 6 AM |

You can also use standard 5-field cron expressions (e.g., `30 2 * * *` for 2:30 AM daily).

### CLI Frequency Choices

The `dango schedule add` wizard offers these frequencies:

| Label | Code |
|-------|------|
| Every hour | `1h` |
| Every 2 hours | `2h` |
| Every 3 hours | `3h` |
| Every 4 hours | `4h` |
| Every 6 hours | `6h` |
| Every 8 hours | `8h` |
| Every 12 hours | `12h` |
| Daily | `daily` |
| Weekly | `weekly` |
| Custom cron | `custom` |

### Notification Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `webhooks` | list | `[]` | Webhook endpoints |
| `webhooks[].name` | string | -- | Webhook name |
| `webhooks[].url` | string | -- | Webhook URL (must start with `http://` or `https://`) |
| `webhooks[].format` | string | `generic` | Message format: `generic` or `slack` |
| `on_failure` | boolean | `true` | Notify on sync failure |
| `on_success` | boolean | `true` | Notify on sync completion |
| `on_stale` | boolean | `true` | Notify on stale data |
| `on_governance` | boolean | `true` | Notify on governance events (schema drift, PII) |
| `on_analysis` | boolean | `true` | Notify on metric alerts |
| `stale_threshold_hours` | integer | `24` | Hours before data is considered stale |

### Webhook Payload (Wire Format)

The generic webhook sends JSON with these fields:

```json
{
  "event": "sync_completed",
  "schedule": "hourly_sync",
  "sources": ["stripe_payments"],
  "error": null,
  "duration_seconds": 45.2,
  "timestamp": "2026-05-17T12:34:56+00:00",
  "dashboard_url": "http://localhost:8800",
  "rows_loaded": 1523,
  "stale_hours": null,
  "attempt_number": null,
  "next_retry_at": null,
  "metadata": null
}
```

!!! note "Wire format field mapping"
    The webhook payload uses different field names than the internal Pydantic model:
    `event_type` becomes `event`, `schedule_name` becomes `schedule`, `occurred_at` becomes `timestamp`.

**Event types:** `sync_completed`, `sync_failed`, `sync_stale`, `sync_retrying`, `schema_drift_detected`, `pii_detected`, `metric_alert`

---

## `.dango/monitors.yml` { #monitors-yml }

Metric monitoring and alert definitions. Managed via manual editing.

### Structure

```yaml
enabled: true
monitors:
  - name: daily_revenue
    source_table: raw_stripe.charges
    value_expression: "SUM(amount) / 100.0"
    filter: "status = 'succeeded'"
    compare: week_over_week
    alert_threshold: 20.0
    drill_down: [currency]

  - name: new_customers
    source_table: raw_hubspot.contacts
    value_expression: "COUNT(*)"
    compare: rolling_7day_avg
    alert_threshold: 30.0
```

### Monitor Fields

| Field | Type | Required | Default | Description |
|-------|------|:--------:|---------|-------------|
| `name` | string | Yes | -- | Monitor name (lowercase alphanumeric + underscore) |
| `source_table` | string | Yes | -- | Schema-qualified table (`schema.table`) |
| `value_expression` | string | Yes | -- | SQL expression for metric value |
| `filter` | string | No | -- | SQL `WHERE` clause filter |
| `compare` | ComparisonType | No | `week_over_week` | Comparison strategy |
| `alert_threshold` | float | No | -- | Percentage change threshold for alerts |
| `drill_down` | list[string] | No | `[]` | Columns for drill-down (`GROUP BY`) |

### Top-Level Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable metric monitoring |

### Comparison Types

| Type | Description |
|------|-------------|
| `week_over_week` | Compare current value to same day last week |
| `rolling_7day_avg` | Compare to 7-day rolling average |
| `rolling_30day_avg` | Compare to 30-day rolling average |
| `prior_period` | Compare to the previous period |

!!! note "Backward compatibility"
    The file can also be named `.dango/metrics.yml`. The `monitors` key accepts `metrics` as an alias, and `alert_threshold` accepts `warn_threshold`.

---

## `.dango/cloud.yml` { #cloud-yml }

Cloud deployment state. Created by `dango deploy` and updated by deployment operations. Generally not edited manually.

### Structure

```yaml
provider: digitalocean
droplet_id: 123456789
droplet_ip: 203.0.113.10
firewall_id: abcdef-1234-5678
region: nyc1
size: s-2vcpu-4gb
domain: analytics.example.com
ssh_key_path: .dango/cloud_key
ssh_key_id: 12345678
deploy_branch: main
spaces:
  bucket: my-backups
  region: nyc3
  access_key_env: SPACES_ACCESS_KEY
  secret_key_env: SPACES_SECRET_KEY
dbt_overrides:
  threads: 2
  memory_limit: 1GB
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `provider` | string | `digitalocean` | Deployment provider: `digitalocean` or `byos` |
| `droplet_id` | integer | -- | DigitalOcean droplet ID (set after provisioning) |
| `droplet_ip` | string | -- | Public IP address (set after provisioning) |
| `firewall_id` | string | -- | DigitalOcean firewall ID |
| `region` | string | `nyc1` | DigitalOcean region |
| `size` | string | `s-2vcpu-4gb` | Droplet size slug |
| `domain` | string | -- | Custom domain name |
| `ssh_key_path` | string | `.dango/cloud_key` | Path to SSH private key |
| `ssh_key_id` | integer | -- | DigitalOcean SSH key ID |
| `deploy_branch` | string | `main` | Expected git branch for deployments |
| `spaces.bucket` | string | -- | Spaces bucket name (required if spaces configured) |
| `spaces.region` | string | droplet region | Spaces region |
| `spaces.access_key_env` | string | `SPACES_ACCESS_KEY` | Env var for Spaces access key |
| `spaces.secret_key_env` | string | `SPACES_SECRET_KEY` | Env var for Spaces secret key |
| `dbt_overrides.threads` | integer | vCPU count | Override dbt threads |
| `dbt_overrides.memory_limit` | string | 25% of RAM | Override DuckDB memory limit |

---

## `.dango/pii-overrides.yml` { #pii-overrides-yml }

Override PII detection results for specific columns. When automatic PII scanning produces false positives or misses sensitive data, add overrides here.

### Structure

```yaml
overrides:
  - source: stripe_payments
    table: charges
    column: customer_email
    status: pii
    set_by: admin@company.com
    reason: Contains customer email addresses
    updated_at: '2026-05-17T12:34:56'

  - source: hubspot_crm
    table: companies
    column: company_name
    status: not_pii
    set_by: admin@company.com
    reason: Public company names, not personally identifiable
    updated_at: '2026-05-17T12:35:00'
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Source name |
| `table` | string | Table name |
| `column` | string | Column name |
| `status` | string | PII status: `pii` or `not_pii` |
| `set_by` | string | User who set the override |
| `reason` | string | Human-readable reason |
| `updated_at` | datetime | ISO-8601 timestamp |

---

## `.dango/metabase.yml` { #metabase-yml }

Metabase admin credentials and database reference. Auto-generated during Metabase setup. **Contains sensitive credentials.**

!!! warning "Sensitive file"
    This file contains the Metabase admin password. It is gitignored by default. Do not commit it to version control.

### Structure

```yaml
admin:
  email: admin@localhost
  password: <auto-generated>
database:
  id: 2
```

| Field | Type | Description |
|-------|------|-------------|
| `admin.email` | string | Metabase admin email |
| `admin.password` | string | Metabase admin password (auto-generated) |
| `database.id` | integer | DuckDB database ID in Metabase |

---

## `.env` { #env }

Environment variables for the project. Loaded automatically by Dango.

See the [Environment Variables Reference](environment-variables.md) for the complete list of supported variables.

---

## `.dlt/secrets.toml` { #secrets-toml }

Sensitive credentials for dlt sources. Auto-populated by `dango source add` and `dango oauth` flows.

!!! warning "Security"
    This file is automatically gitignored. Never commit credentials to version control.

### Structure

```toml
[sources.{source_name}]
api_key = "your-api-key"

[sources.{source_name}.credentials]
client_id = "..."
client_secret = "..."
refresh_token = "..."
```

### Common Patterns

```toml
# Stripe
[sources.stripe_payments]
api_key = "sk_live_51ABCdef..."

# Google Sheets (OAuth)
[sources.budgets]
[sources.budgets.credentials]
client_id = "123456789.apps.googleusercontent.com"
client_secret = "GOCSPX-abc123..."
refresh_token = "1//0abc123..."

# Facebook Ads
[sources.facebook_marketing]
access_token = "EAAB123..."
account_id = "123456789"

# HubSpot
[sources.hubspot_crm]
api_key = "pat-na1-xxxxxxxxxxxxx"

# PostgreSQL
[sources.postgres_prod]
connection_string = "postgresql://user:pass@db.example.com:5432/production"

# GitHub
[sources.my_repo]
access_token = "ghp_xxxxxxxxxxxxx"
```

---

## `.dlt/config.toml` { #config-toml }

Non-sensitive dlt configuration. Safe to commit to version control.

### Structure

```toml
[load]
truncate_staging_dataset = true

[sources.{source_name}]
start_date = "2024-01-01"
```

---

## `dbt/profiles.yml` { #dbt-profiles-yml }

Standard dbt connection profile for DuckDB. Auto-generated by `dango init`.

```yaml
dango:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/warehouse.duckdb
      threads: 4
```

!!! note "Auto-generated"
    This file is managed by Dango. Manual edits may be overwritten by `dango init` or cloud deployment.

---

## `dbt/dbt_project.yml` { #dbt-project-yml }

Standard dbt project configuration. Auto-generated by `dango init`.

```yaml
name: dango
version: '1.0.0'
config-version: 2
profile: dango

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]
```

!!! note "Auto-generated"
    This file is managed by Dango. Custom dbt models are placed in `dbt/models/`.

---

## `docker-compose.yml` { #docker-compose-yml }

Metabase container configuration. Generated from a template during `dango start`.

!!! note "Auto-generated"
    This file is generated from a Jinja2 template and should not be edited manually. It is regenerated on each `dango start`.

---

## Validation

Validate your configuration files:

```bash
# Validate all config files
dango validate

# Validate specific config
dango config validate

# Show current configuration
dango config show
```

---

## Related Pages

- [Environment Variables](environment-variables.md) --- Complete variable reference
- [Permissions Matrix](permissions.md) --- Role-based access control
- [Source Registry](source-registry.md) --- All source types and their config fields
- [CLI Reference](../cli/cli-reference.md) --- Config management commands
