# Configuration Reference

Complete reference for all Dango configuration files and schemas.

---

## Overview

Dango uses several configuration files to manage your project:

| File | Purpose | Sensitive |
|------|---------|-----------|
| `.dango/project.yml` | Project metadata and platform settings | No |
| `.dango/sources.yml` | Data source definitions | No |
| `.dlt/secrets.toml` | API keys and credentials | **Yes** (gitignored) |
| `.dlt/config.toml` | Non-sensitive dlt parameters | No |

---

## project.yml

Project metadata, stakeholder information, and platform settings.

**Location**: `.dango/project.yml`

### Project Section

```yaml
project:
  name: my-analytics              # Required: Project name
  organization: Acme Corp         # Optional: Organization name
  dango_version: 0.0.5            # Optional: Dango version used
  created: '2025-12-07T00:21:56'  # Required: Creation timestamp
  created_by: user@example.com    # Required: Creator email
  purpose: Track sales metrics    # Required: Project purpose

  stakeholders:                   # Optional: List of stakeholders
    - name: Sarah Chen
      role: CMO - Dashboard user
      contact: sarah@company.com

  sla: Daily by 9am UTC           # Optional: Data freshness SLA
  limitations: 24h data delay     # Optional: Known limitations
  getting_started: |              # Optional: Quick start guide
    1. Run 'dango sync'
    2. Open http://localhost:8800
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name |
| `organization` | string | No | Organization name |
| `dango_version` | string | No | Dango version |
| `created` | datetime | Yes | Creation timestamp |
| `created_by` | string | Yes | Creator email/name |
| `purpose` | string | Yes | Why this project exists |
| `stakeholders` | list | No | Project stakeholders |
| `sla` | string | No | Data freshness SLA |
| `limitations` | string | No | Known limitations |
| `getting_started` | string | No | Quick start guide |

### Platform Section

```yaml
platform:
  duckdb_path: ./data/warehouse.duckdb  # Path to DuckDB database
  dbt_project_dir: ./dbt                # Path to dbt project
  data_dir: ./data                      # Path to data directory
  port: 8800                            # Web UI port
  metabase_port: 3000                   # Metabase port
  dbt_docs_port: 8081                   # dbt docs port
  auto_sync: true                       # Auto-sync on file changes
  auto_dbt: true                        # Auto-run dbt on sync
  debounce_seconds: 600                 # Debounce period (10 min)
  watch_patterns:                       # File patterns to watch
    - '*.csv'
  watch_directories:                    # Directories to watch
    - data/uploads
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `duckdb_path` | string | `./data/warehouse.duckdb` | Path to DuckDB database |
| `dbt_project_dir` | string | `./dbt` | Path to dbt project |
| `data_dir` | string | `./data` | Path to data directory |
| `port` | integer | `8800` | Web UI port |
| `metabase_port` | integer | `3000` | Metabase port |
| `dbt_docs_port` | integer | `8081` | dbt docs port |
| `auto_sync` | boolean | `true` | Auto-sync on file changes |
| `auto_dbt` | boolean | `true` | Auto-run dbt after sync |
| `debounce_seconds` | integer | `600` | Debounce period in seconds |
| `watch_patterns` | list | `['*.csv']` | Glob patterns to watch |
| `watch_directories` | list | `['data/uploads']` | Directories to watch |

### Complete Example

```yaml
project:
  name: Acme Analytics
  organization: Acme Corp
  dango_version: 0.0.5
  created: '2025-12-07T00:21:56.325092'
  created_by: data-team@acme.com
  purpose: Track sales performance and customer behavior
  stakeholders:
    - name: Sarah Chen
      role: CMO - Primary dashboard user
      contact: sarah@acme.com
    - name: David Kim
      role: Data analyst
      contact: david@acme.com
  sla: Daily by 9am UTC
  limitations: |
    - Stripe data has 24h delay
    - Google Sheets updated manually on Mondays
  getting_started: |
    1. Run 'dango sync' to refresh data
    2. Open http://localhost:8800 for Web UI
    3. Open http://localhost:3000 for Metabase dashboards

platform:
  duckdb_path: ./data/warehouse.duckdb
  dbt_project_dir: ./dbt
  data_dir: ./data
  port: 8800
  metabase_port: 3000
  dbt_docs_port: 8081
  auto_sync: true
  auto_dbt: true
  debounce_seconds: 600
  watch_patterns:
    - '*.csv'
  watch_directories:
    - data/uploads
```

---

## sources.yml

Data source definitions and configuration.

**Location**: `.dango/sources.yml`

### Structure

```yaml
version: '1.0'
sources:
  - name: source_name
    type: source_type
    enabled: true
    description: Human-readable description
    tags: [tag1, tag2]
    # Type-specific configuration block
    source_type:
      # Configuration fields
```

### Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique source identifier |
| `type` | string | Yes | Source type (see below) |
| `enabled` | boolean | No | Whether to sync (default: `true`) |
| `description` | string | No | Human-readable description |
| `tags` | list | No | Tags for organization |

### Source Types

**Wizard-Supported** (via `dango source add`):

- `csv` - CSV files
- `stripe` - Stripe payments
- `google_sheets` - Google Sheets
- `google_analytics` - Google Analytics 4
- `facebook_ads` - Facebook Ads
- `google_ads` - Google Ads
- `rest_api` - Custom REST APIs
- `dlt_native` - Advanced dlt sources

**Manual Configuration** (via `dlt_native`):

- `hubspot`, `salesforce`, `pipedrive` - CRM
- `shopify`, `woocommerce` - E-commerce
- `notion`, `asana`, `jira` - Productivity
- `github`, `slack` - Development
- `postgres`, `mysql`, `mongodb` - Databases
- See [Built-in Sources](../data-sources/built-in-sources.md) for full list

---

### CSV Source

```yaml
- name: sales_data
  type: csv
  enabled: true
  csv:
    directory: data/uploads/sales       # Required: Directory path
    file_pattern: '*.csv'               # Default: *.csv
    deduplication_strategy: latest_only # none, latest_only, append_only, scd_type2
    primary_key: order_id               # Required for deduplication
    timestamp_column: updated_at        # Required for latest_only/scd_type2
    timestamp_sort: desc                # desc (default) or asc
    notes: Export from Shopify daily    # Optional: How to regenerate
  description: Daily sales transactions
  tags: [ecommerce, daily]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `directory` | path | - | Directory containing CSV files |
| `file_pattern` | string | `*.csv` | Glob pattern for files |
| `deduplication_strategy` | enum | `latest_only` | Dedup strategy |
| `primary_key` | string | - | Column for unique records |
| `timestamp_column` | string | - | Column for determining latest |
| `timestamp_sort` | string | `desc` | Sort order (desc/asc) |
| `notes` | string | - | Regeneration notes |

**Deduplication Strategies**:

| Strategy | Description |
|----------|-------------|
| `none` | Keep all records |
| `latest_only` | Keep only most recent version per primary key |
| `append_only` | Add new records, never update |
| `scd_type2` | Track history with valid_from/valid_to |

---

### Stripe Source

```yaml
- name: stripe_payments
  type: stripe
  enabled: true
  stripe:
    stripe_secret_key_env: STRIPE_API_KEY  # Env var name (not the actual key)
    endpoints:                              # Optional: specific endpoints
      - charges
      - customers
      - invoices
      - subscriptions
    start_date: 2024-01-01                 # Optional: initial load date
    end_date: 2024-12-31                   # Optional: end date
  description: Stripe payment data
  tags: [payments]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `stripe_secret_key_env` | string | `STRIPE_API_KEY` | Env var containing API key |
| `endpoints` | list | all | Specific endpoints to sync |
| `start_date` | date | - | Start date (YYYY-MM-DD) |
| `end_date` | date | - | End date (YYYY-MM-DD) |

---

### Google Sheets Source

```yaml
- name: budgets
  type: google_sheets
  enabled: true
  google_sheets:
    spreadsheet_url_or_id: https://docs.google.com/spreadsheets/d/1abc...
    range_names:                    # Sheet/tab names to load
      - Monthly Budget
      - Quarterly Forecast
    deduplication: latest_only      # none, latest_only, append_only, scd_type2
  description: Financial planning documents
  tags: [finance]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `spreadsheet_url_or_id` | string | - | Spreadsheet URL or ID |
| `range_names` | list | - | Sheet names to load |
| `deduplication` | enum | `latest_only` | Dedup strategy |

---

### Google Analytics Source

```yaml
- name: website_analytics
  type: google_analytics
  enabled: true
  google_analytics:
    property_id: "123456789"          # GA4 property ID
    credentials_env: GOOGLE_CREDENTIALS
    start_date: 2024-01-01
  description: Website analytics
  tags: [marketing, web]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `property_id` | string | - | GA4 property ID |
| `credentials_env` | string | `GOOGLE_CREDENTIALS` | Env var for credentials |
| `start_date` | date | - | Start date |

---

### Facebook Ads Source

```yaml
- name: facebook_marketing
  type: facebook_ads
  enabled: true
  facebook_ads:
    account_id: act_123456789        # Include 'act_' prefix
    access_token_env: FB_ACCESS_TOKEN
    start_date: 2024-01-01
  description: Facebook ad performance
  tags: [marketing, ads]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `account_id` | string | - | Facebook Ads Account ID (with `act_` prefix) |
| `access_token_env` | string | `FB_ACCESS_TOKEN` | Env var for access token |
| `start_date` | date | - | Start date |

---

### REST API Source

```yaml
- name: custom_api
  type: rest_api
  enabled: true
  rest_api:
    base_url: https://api.example.com/v1
    auth_type: bearer                # bearer, api_key, basic, none
    auth_token_env: API_TOKEN
    endpoints:
      - path: /users
      - path: /orders
        params:
          limit: 100
    headers:
      Accept: application/json
  description: Custom REST API
  tags: [custom]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | string | - | Base URL for API |
| `auth_type` | enum | `bearer` | Auth type |
| `auth_token_env` | string | - | Env var for auth token |
| `endpoints` | list | - | Endpoints to sync |
| `headers` | dict | - | Additional headers |

---

### dlt_native Source (Advanced)

For dlt sources not in Dango's wizard, or for full control:

```yaml
- name: hubspot_crm
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: hubspot           # dlt source module name
    source_function: hubspot         # Function to call
    function_kwargs:                 # Arguments to pass
      api_key: env:HUBSPOT_API_KEY
  description: HubSpot CRM data
  tags: [crm]
```

**Example - PostgreSQL Database**:

```yaml
- name: postgres_prod
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: public
      table_names:
        - customers
        - orders
  description: PostgreSQL database
  tags: [database]
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_module` | string | - | dlt source module name |
| `source_function` | string | - | Function to call |
| `function_kwargs` | dict | `{}` | Arguments for the function |
| `pipeline_name` | string | source name | Custom pipeline name |
| `dataset_name` | string | source name | Custom dataset name |

---

## secrets.toml

Sensitive credentials for dlt sources.

**Location**: `.dlt/secrets.toml`

!!! warning "Security"
    This file is automatically gitignored. Never commit credentials to version control.

### Structure

```toml
[sources.{source_name}]
api_key = "your-api-key"

[sources.{source_name}.credentials]
# Nested credentials for OAuth
client_id = "..."
client_secret = "..."
refresh_token = "..."
```

### Common Patterns

**Stripe**:
```toml
[sources.stripe_payments]
api_key = "sk_live_xxxxxxxxxxxxx"
```

**Google OAuth** (Sheets, Analytics, Ads):
```toml
[sources.my_sheets]
[sources.my_sheets.credentials]
client_id = "xxxxx.apps.googleusercontent.com"
client_secret = "xxxxx"
refresh_token = "xxxxx"
```

**Facebook Ads**:
```toml
[sources.facebook_ads]
access_token = "EAAB1234567890..."
account_id = "act_123456789"
```

**HubSpot**:
```toml
[sources.hubspot]
api_key = "pat-na1-xxxxxxxxxxxxx"
```

**PostgreSQL**:
```toml
[sources.postgres]
connection_string = "postgresql://user:password@localhost:5432/database"
```

**GitHub**:
```toml
[sources.github]
access_token = "ghp_xxxxxxxxxxxxx"
```

### Complete Example

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
account_id = "act_123456789"

# PostgreSQL
[sources.postgres_prod]
connection_string = "postgresql://dango:secret@db.example.com:5432/production"
```

---

## config.toml

Non-sensitive dlt configuration.

**Location**: `.dlt/config.toml`

This file can be safely committed to version control.

### Structure

```toml
[load]
truncate_staging_dataset = true

[sources.{source_name}]
# Non-sensitive source parameters
start_date = "2024-01-01"
```

### Example

```toml
[load]
truncate_staging_dataset = true

[sources.stripe_payments]
start_date = "2024-01-01"

[sources.facebook_marketing]
start_date = "2024-01-01"
```

---

## Environment Variables

Dango reads credentials from multiple sources in this order:

1. `.dlt/secrets.toml` (highest priority)
2. `.env` file
3. System environment variables

### .env File

```bash
# API Keys
STRIPE_API_KEY=sk_live_xxxxx
HUBSPOT_API_KEY=pat-na1-xxxxx

# Google OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Facebook OAuth
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=xxxxx

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db
```

### Common Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `STRIPE_API_KEY` | Stripe | Stripe secret key |
| `GOOGLE_CLIENT_ID` | Google OAuth | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth | Google OAuth client secret |
| `FACEBOOK_APP_ID` | Facebook OAuth | Facebook app ID |
| `FACEBOOK_APP_SECRET` | Facebook OAuth | Facebook app secret |
| `FB_ACCESS_TOKEN` | Facebook Ads | Facebook access token |
| `HUBSPOT_API_KEY` | HubSpot | HubSpot private app key |
| `GITHUB_ACCESS_TOKEN` | GitHub | GitHub personal access token |

---

## Validation

Validate your configuration:

```bash
# Validate all config files
dango validate

# Validate specific config
dango config validate --file .dango/sources.yml

# Show current configuration
dango config show

# Check OAuth credentials
dango auth check
```

---

## Next Steps

- [CLI Reference](../cli/cli-reference.md) - Complete command documentation
- [Data Sources](../data-sources/index.md) - Source-specific guides
- [Custom Sources](../data-sources/custom-sources.md) - Build your own integrations
