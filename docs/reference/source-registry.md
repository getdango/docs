# Source Registry

Complete reference for all data source types supported by Dango.

---

## Overview

Dango supports **33 data sources** across **10 categories**, using **5 authentication types**. Sources are added via `dango source add` (wizard-enabled) or manual YAML configuration in `.dango/sources.yml`.

- **25 wizard-enabled** sources can be configured interactively
- **8 wizard-disabled** sources require manual YAML configuration or the `dlt_native` bypass
- Sources without a dedicated Pydantic config model use `generic_config: dict` in YAML

---

## Source Summary

| Source | Type Key | Category | Auth | Wizard | Incremental |
|--------|----------|----------|------|:------:|:-----------:|
| File Import (CSV, JSON, Parquet) | `local_files` | Local & Custom | None | :white_check_mark: | :white_check_mark: |
| REST API (Generic) | `rest_api` | Local & Custom | API Key | :white_check_mark: | :white_check_mark: |
| dlt Native Source (Advanced) | `dlt_native` | Local & Custom | None | :white_check_mark: | |
| CSV Files | `csv` | Local & Custom | None | | :white_check_mark: |
| Files & Cloud Storage | `filesystem` | Local & Custom | None | | |
| Google Sheets | `google_sheets` | Marketing & Analytics | OAuth | :white_check_mark: | |
| Facebook Ads | `facebook_ads` | Marketing & Analytics | OAuth | :white_check_mark: | :white_check_mark: |
| Google Analytics (GA4) | `google_analytics` | Marketing & Analytics | OAuth | :white_check_mark: | :white_check_mark: |
| Google Ads | `google_ads` | Marketing & Analytics | OAuth | :white_check_mark: | |
| Mux | `mux` | Marketing & Analytics | API Key | :white_check_mark: | |
| Airtable | `airtable` | Marketing & Analytics | API Key | :white_check_mark: | |
| Matomo Analytics | `matomo` | Marketing & Analytics | API Key | | :white_check_mark: |
| HubSpot | `hubspot` | Business & CRM | API Key | :white_check_mark: | :white_check_mark: |
| Salesforce | `salesforce` | Business & CRM | Service Account | :white_check_mark: | :white_check_mark: |
| Zendesk | `zendesk` | Business & CRM | Basic | :white_check_mark: | :white_check_mark: |
| Pipedrive | `pipedrive` | Business & CRM | API Key | :white_check_mark: | :white_check_mark: |
| Freshdesk | `freshdesk` | Business & CRM | API Key | :white_check_mark: | :white_check_mark: |
| Workable | `workable` | Business & CRM | API Key | :white_check_mark: | :white_check_mark: |
| Jira | `jira` | Business & CRM | Basic | | |
| Asana | `asana` | Business & CRM | API Key | | :white_check_mark: |
| Stripe | `stripe` | E-commerce & Payment | API Key | :white_check_mark: | :white_check_mark: |
| Shopify | `shopify` | E-commerce & Payment | OAuth | | :white_check_mark: |
| Notion | `notion` | Files & Storage | API Key | :white_check_mark: | |
| Email Inbox (IMAP) | `inbox` | Files & Storage | Basic | :white_check_mark: | :white_check_mark: |
| MongoDB | `mongodb` | Databases | Basic | :white_check_mark: | :white_check_mark: |
| PostgreSQL | `postgres` | Databases | Basic | :white_check_mark: | :white_check_mark: |
| GitHub | `github` | Development | API Key | :white_check_mark: | :white_check_mark: |
| Slack | `slack` | Communication | API Key | :white_check_mark: | :white_check_mark: |
| Apache Kafka | `kafka` | Streaming | None | :white_check_mark: | :white_check_mark: |
| Amazon Kinesis | `kinesis` | Streaming | Service Account | :white_check_mark: | :white_check_mark: |
| Chess.com | `chess` | Other | None | :white_check_mark: | |
| Strapi | `strapi` | Other | API Key | | |
| Personio | `personio` | Other | API Key | | :white_check_mark: |

---

## Sources by Category

### Local & Custom

#### File Import (`local_files`) :white_check_mark:{ title="Wizard enabled" }

Load CSV, JSON, JSONL, or Parquet files from a directory. All matching files are combined into a single raw table. On re-sync, new/modified files are loaded, deleted files are removed.

```yaml
sources:
  - name: sales_data
    type: local_files
    local_files:
      directory: data/uploads/sales
      file_pattern: "*.csv"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `directory` | path | -- | Directory containing files (required) |
| `file_pattern` | string | `"*"` | Glob pattern for files to load |
| `notes` | string | -- | Notes about how to regenerate files |

#### REST API (`rest_api`) :white_check_mark:{ title="Wizard enabled" }

Connect to any REST API with configurable authentication (bearer, API key, basic, OAuth2 client credentials, custom header).

```yaml
sources:
  - name: custom_api
    type: rest_api
    rest_api:
      base_url: https://api.example.com/v1
      auth_type: bearer
      auth_token_env: API_TOKEN
      endpoints:
        - path: /users
        - path: /orders
          params:
            limit: 100
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | string | -- | Base URL for API (required) |
| `endpoints` | list[dict] | -- | Endpoint definitions (required) |
| `auth_type` | string | `"bearer"` | Auth type: `bearer`, `api_key`, `basic`, `oauth2_client_credentials`, `custom_header`, `none` |
| `auth_token_env` | string | -- | Env var with auth token/key |
| `api_key_name` | string | -- | Header or query param name for API key auth |
| `api_key_location` | string | -- | Where to send API key: `"header"` or `"query"` |
| `basic_username_env` | string | -- | Env var for HTTP Basic username |
| `basic_password_env` | string | -- | Env var for HTTP Basic password |
| `access_token_url` | string | -- | OAuth2 token endpoint URL |
| `client_id_env` | string | -- | Env var for OAuth2 client ID |
| `client_secret_env` | string | -- | Env var for OAuth2 client secret |
| `auth_header_name` | string | -- | Custom auth header name (e.g., `X-Shopify-Access-Token`) |
| `headers` | dict | -- | Additional request headers |

#### dlt Native Source (`dlt_native`) :white_check_mark:{ title="Wizard enabled" }

Use any dlt verified source or custom source not in Dango's registry. For advanced users.

```yaml
sources:
  - name: hubspot_crm
    type: dlt_native
    dlt_native:
      source_module: hubspot
      source_function: hubspot
      function_kwargs:
        api_key: "env:HUBSPOT_API_KEY"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source_module` | string | -- | Python module name (required) |
| `source_function` | string | -- | Function name to call (required) |
| `function_kwargs` | dict | `{}` | Arguments passed to the source function |
| `pipeline_name` | string | source name | Custom pipeline name |
| `dataset_name` | string | source name | Custom dataset name |

#### CSV Files (`csv`)

!!! note "Hidden source"
    The `csv` type is hidden in the wizard. Use `local_files` instead, which supports CSV plus JSON, JSONL, and Parquet formats.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `directory` | path | -- | Directory containing CSV files (required) |
| `file_pattern` | string | `"*.csv"` | Glob pattern for files |
| `notes` | string | -- | Regeneration notes |

#### Files & Cloud Storage (`filesystem`)

!!! note "Hidden source"
    The `filesystem` type is hidden in the wizard. Use `local_files` for local files or `filesystem` with manual YAML for cloud storage (S3, GCS, Azure).

---

### Marketing & Analytics

#### Google Sheets (`google_sheets`) :white_check_mark:{ title="Wizard enabled" }

Load data from Google Sheets (one or more tabs). Requires OAuth setup via `dango oauth google`.

```yaml
sources:
  - name: budgets
    type: google_sheets
    google_sheets:
      spreadsheet_url_or_id: https://docs.google.com/spreadsheets/d/1abc...
      range_names:
        - Monthly Budget
        - Quarterly Forecast
      deduplication: latest_only
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `spreadsheet_url_or_id` | string | -- | Spreadsheet URL or ID (required) |
| `range_names` | list[string] | -- | Sheet/tab names to load (required) |
| `deduplication` | enum | `latest_only` | Dedup strategy: `none`, `latest_only`, `append_only`, `scd_type2` |

#### Facebook Ads (`facebook_ads`) :white_check_mark:{ title="Wizard enabled" }

Load ad campaigns, ads, creatives, leads, and daily performance metrics.

```yaml
sources:
  - name: facebook_marketing
    type: facebook_ads
    facebook_ads:
      account_id: act_123456789
      access_token_env: FB_ACCESS_TOKEN
      initial_load_past_days: 30
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `account_id` | string | -- | Facebook Ads Account ID with `act_` prefix (required) |
| `access_token_env` | string | `FB_ACCESS_TOKEN` | Env var with access token |
| `initial_load_past_days` | integer | `30` | Historical days to load on first sync |
| `start_date` | date | -- | Start date (YYYY-MM-DD) |
| `resources` | list[string] | all | Resources to sync |

**Default resources:** `campaigns`, `ads`, `ad_sets`, `facebook_insights`

**Available resources:** `campaigns`, `ads`, `ad_sets`, `ad_creatives`, `leads`, `facebook_insights`

#### Google Analytics (`google_analytics`) :white_check_mark:{ title="Wizard enabled" }

Load website analytics data from Google Analytics 4. Supports custom report queries.

```yaml
sources:
  - name: website_analytics
    type: google_analytics
    google_analytics:
      property_id: "123456789"
      credentials_env: GOOGLE_CREDENTIALS
      start_date: "2024-01-01"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `property_id` | string | -- | GA4 property ID (required) |
| `credentials_env` | string | `GOOGLE_CREDENTIALS` | Env var with credentials |
| `start_date` | string | -- | Start date (YYYY-MM-DD or relative like `90daysAgo`) |

#### Google Ads (`google_ads`) :white_check_mark:{ title="Wizard enabled" }

Load daily performance metrics from Google Ads via GAQL queries. Includes 5 default queries (campaign stats, ad group stats, keyword stats, ad stats, search term stats).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `property_id` | string | -- | Google Ads customer ID (required) |
| `credentials_env` | string | `GOOGLE_CREDENTIALS` | Env var with credentials |

#### Mux (`mux`) :white_check_mark:{ title="Wizard enabled" }

Load video analytics data from Mux.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Airtable (`airtable`) :white_check_mark:{ title="Wizard enabled" }

Load tables from Airtable bases.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Matomo Analytics (`matomo`)

!!! note "Wizard disabled"
    Disabled because Matomo passes the auth token via GET parameter, which is a security risk. Configure manually with `dlt_native`.

---

### Business & CRM

#### HubSpot (`hubspot`) :white_check_mark:{ title="Wizard enabled" }

Load contacts, companies, deals, and tickets from HubSpot CRM.

```yaml
sources:
  - name: hubspot_crm
    type: hubspot
    hubspot:
      api_key_env: HUBSPOT_API_KEY
      resources:
        - contacts
        - companies
        - deals
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `api_key_env` | string | `HUBSPOT_API_KEY` | Env var with API key |
| `resources` | list[string] | `["contacts", "companies", "deals", "tickets"]` | Resources to sync |

**Available resources:** `contacts`, `companies`, `deals`, `tickets`, `products`, `quotes`, `owners`, `properties`, `pipelines_deal`, `pipelines_ticket`

#### Salesforce (`salesforce`) :white_check_mark:{ title="Wizard enabled" }

Load data from Salesforce CRM using service account authentication.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `resources` | list[string] | all | Resources to sync |

**Default resources:** `account`, `contact`, `lead`, `opportunity`, `campaign`

**Available resources:** `account`, `contact`, `lead`, `opportunity`, `campaign`, `task`, `event`, `sf_user`, `user_role`, `product_2`

#### Zendesk (`zendesk`) :white_check_mark:{ title="Wizard enabled" }

Load support tickets, users, and chat data from Zendesk Support.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

**Default resources:** `tickets`, `ticket_fields`

**Available resources:** `tickets`, `ticket_fields`, `ticket_events`, `ticket_metric_events`

#### Pipedrive (`pipedrive`) :white_check_mark:{ title="Wizard enabled" }

Load deals, contacts, and activities from Pipedrive CRM.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Freshdesk (`freshdesk`) :white_check_mark:{ title="Wizard enabled" }

Load support tickets, agents, and companies from Freshdesk.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Workable (`workable`) :white_check_mark:{ title="Wizard enabled" }

Load candidates, jobs, and events from Workable ATS.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Jira (`jira`)

!!! note "Wizard disabled"
    Disabled due to endpoint issues in the dlt source. Configure manually with `dlt_native`.

#### Asana (`asana`)

!!! note "Wizard disabled"
    Disabled because the Asana SDK was removed from the dlt source. Configure manually with `dlt_native`.

---

### E-commerce & Payment

#### Stripe (`stripe`) :white_check_mark:{ title="Wizard enabled" }

Load payment data from Stripe (charges, customers, subscriptions, etc.).

```yaml
sources:
  - name: stripe_payments
    type: stripe
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      endpoints:
        - charges
        - customers
        - invoices
      start_date: "2024-01-01"
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `stripe_secret_key_env` | string | `STRIPE_API_KEY` | Env var with Stripe secret key |
| `endpoints` | list[string] | all | Specific endpoints to sync |
| `start_date` | date | -- | Start date (YYYY-MM-DD) |
| `end_date` | date | -- | End date (YYYY-MM-DD) |

#### Shopify (`shopify`)

!!! note "Wizard disabled"
    Disabled because Shopify requires Authorization Code Grant OAuth 2.0, which needs a dedicated `dango oauth shopify` provider (not yet implemented).

---

### Files & Storage

#### Notion (`notion`) :white_check_mark:{ title="Wizard enabled" }

Load pages and databases from Notion.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Email Inbox (`inbox`) :white_check_mark:{ title="Wizard enabled" }

Read messages and attachments from email inbox via IMAP.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

---

### Databases

#### MongoDB (`mongodb`) :white_check_mark:{ title="Wizard enabled" }

Load collections from MongoDB databases with incremental support.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### PostgreSQL (`postgres`) :white_check_mark:{ title="Wizard enabled" }

Load tables from PostgreSQL databases with schema filtering.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

---

### Streaming

#### Apache Kafka (`kafka`) :white_check_mark:{ title="Wizard enabled" }

Extract messages from Kafka topics.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

#### Amazon Kinesis (`kinesis`) :white_check_mark:{ title="Wizard enabled" }

Read messages from Kinesis streams.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `generic_config` | dict | -- | See [generic_config](#generic_config) |

---

### Development

#### GitHub (`github`) :white_check_mark:{ title="Wizard enabled" }

Load repository data, issues, pull requests, and commits from GitHub.

```yaml
sources:
  - name: my_repo
    type: github
    github:
      access_token_env: GITHUB_ACCESS_TOKEN
      owner: my-org
      name: my-repo
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `access_token_env` | string | `GITHUB_ACCESS_TOKEN` | Env var with personal access token |
| `owner` | string | -- | GitHub username or organization (required) |
| `name` | string | -- | Repository name (required) |

---

### Communication

#### Slack (`slack`) :white_check_mark:{ title="Wizard enabled" }

Load messages, channels, and user data from Slack.

```yaml
sources:
  - name: slack_data
    type: slack
    slack:
      access_token_env: SLACK_ACCESS_TOKEN
      selected_channels:
        - C01234ABCDE
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `access_token_env` | string | `SLACK_ACCESS_TOKEN` | Env var with Slack bot token |
| `selected_channels` | list[string] | all | Channel IDs to sync |
| `start_date` | date | -- | Start date for message history |

---

### Other

#### Chess.com (`chess`) :white_check_mark:{ title="Wizard enabled" }

Load player profiles and games from Chess.com API. No authentication required.

#### Strapi (`strapi`)

!!! note "Wizard disabled"
    Untested, requires a Docker Strapi instance.

#### Personio (`personio`)

!!! note "Wizard disabled"
    Enterprise-only API.

---

## `generic_config` { #generic_config }

Sources without a dedicated Pydantic configuration model use the `generic_config` field. This applies to **21+ sources** including Zendesk, Pipedrive, Freshdesk, Workable, Airtable, Mux, Notion, Inbox, MongoDB, PostgreSQL, Kafka, Kinesis, and others.

The `generic_config` field accepts any key-value pairs that the underlying dlt source function expects:

```yaml
sources:
  - name: my_zendesk
    type: zendesk
    generic_config:
      subdomain: mycompany
      email: support@mycompany.com
```

Refer to the [dlt documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/) for source-specific parameters.

---

## Capabilities Matrix

| Capability | Description | Sources |
|------------|-------------|---------|
| **Performance Metrics** | Source provides built-in analytics/metrics | Facebook Ads, Google Analytics, Google Ads, Matomo, Mux |
| **Date Range** | Supports `start_date`/`end_date` filtering | Stripe, Shopify, Google Analytics, Google Ads, Zendesk, Workable, Slack, Mux |
| **Incremental** | Supports incremental loading (only new/changed data) | CSV, Local Files, REST API, Facebook Ads, Google Analytics, HubSpot, Salesforce, Zendesk, Pipedrive, Freshdesk, Workable, Stripe, Shopify, Slack, GitHub, Inbox, MongoDB, PostgreSQL, Kafka, Kinesis, Asana, Matomo, Chess, Personio |
| **Custom Queries** | Supports user-defined queries or report definitions | dlt Native, REST API, Google Analytics, Google Ads, Matomo |

---

## Authentication Types

| Auth Type | Description | Sources |
|-----------|-------------|---------|
| **None** | No authentication required | CSV, Local Files, dlt Native, Filesystem, Kafka, Chess |
| **API Key** | API key passed via environment variable | REST API, Stripe, HubSpot, GitHub, Slack, Pipedrive, Freshdesk, Workable, Airtable, Mux, Matomo, Notion, Asana, Strapi, Personio |
| **OAuth** | OAuth 2.0 flow via `dango oauth <provider>` | Google Sheets, Facebook Ads, Google Analytics, Google Ads, Shopify |
| **Basic** | Username/password or token authentication | Zendesk, Jira, Inbox, MongoDB, PostgreSQL |
| **Service Account** | Service account credentials (JSON key file) | Salesforce, Kinesis |

---

## Common Source Fields

These fields are available on every source regardless of type:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | -- | Unique source name (required, lowercase alphanumeric + underscore) |
| `type` | SourceType | -- | Source type key (required) |
| `enabled` | boolean | `true` | Whether to include in syncs |
| `description` | string | -- | Human-readable description |
| `tags` | list[string] | `[]` | Metadata tags for organization |
| `lookback_days` | integer | -- | Re-load this many days on incremental sync (ignored on full refresh) |

---

## Related Pages

- [Source Catalog](../data-sources/source-catalog.md) — User-friendly guide to choosing sources
- [Adding Sources](../data-sources/adding-sources.md) — Step-by-step source configuration
- [Configuration Reference](configuration.md) — Full `sources.yml` schema
