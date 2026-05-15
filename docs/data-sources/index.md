# Data Sources

Connect to APIs, databases, and local files through Dango's unified data ingestion layer.

---

## Overview

Dango supports **33 data sources** through [dlt (data load tool)](https://dlthub.com/docs). Whether you're working with local CSV files, cloud APIs, or existing databases, Dango provides a unified configuration interface.

!!! info "Wizard vs Manual Sources"
    **Wizard-enabled sources** (25 sources): Add via `dango source add` interactive wizard — handles authentication, configuration, and validation automatically.

    **Manual sources**: Configure directly in `sources.yml` using `dlt_native` for any [dlt verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/).

    See the [Source Catalog](source-catalog.md) for the complete list of all 33 sources.

**Source categories at a glance:**

- **Local Files** — CSV, JSON, JSONL, Parquet from your filesystem
- **OAuth Sources** — Google Sheets, GA4, Google Ads, Facebook Ads (browser-based auth)
- **API Key Sources** — Stripe, HubSpot, Salesforce, GitHub, Slack, and more
- **Database Sources** — PostgreSQL, MongoDB, and others via dlt
- **REST API** — Connect to any API with JSON responses
- **Custom Sources** — Build integrations with Python and dlt

---

## For dlt Users

If you're already familiar with [dlt (data load tool)](https://dlthub.com/docs), here's how Dango relates:

**Dango wraps dlt** with:

- YAML configuration instead of Python scripts
- Automatic dbt staging model generation
- Unified CLI (`dango sync`) for all sources
- Web UI for monitoring and management

**What stays the same**:

- Credentials in `.dlt/secrets.toml` (same format)
- All dlt verified sources available via `dlt_native`
- Standard dlt decorators (`@dlt.source`, `@dlt.resource`)

**When to use what**:

| Scenario | Use |
|----------|-----|
| Standard sources (Stripe, Google Sheets, etc.) | Dango wizard or YAML config |
| Custom API with simple logic | Dango `dlt_native` + Python file |
| Complex pipelines, custom destinations | Pure dlt (Dango not needed) |

**Learn more**:

- [Custom Sources](custom-sources.md) — "dlt vs. Dango Workflow" comparison
- [Database Sources](database-sources.md) — "How This Differs from Standard dlt" table
- [dlt Documentation](https://dlthub.com/docs) — Official dlt docs for advanced topics

---

## Quick Start

### Add Your First Source

Choose your source type and follow the guide:

=== "Local Files"

    ```bash
    # Recommended: Use the wizard
    dango source add
    # Select "File Import (CSV, JSON, Parquet)" and follow prompts
    ```

    Or configure manually in `.dango/sources.yml`:

    ```yaml
    sources:
      - name: sales_data
        type: local_files
        enabled: true
        local_files:
          directory: data/uploads/sales_data
          file_pattern: "*.csv"
    ```

    Then copy files and sync:

    ```bash
    cp my_sales.csv data/uploads/sales_data/
    dango sync sales_data
    ```

    [Learn more →](local-files/index.md)

=== "OAuth (Google Sheets)"

    ```bash
    # Interactive setup
    dango source add
    # Select "Google Sheets" from the list
    # Follow OAuth flow in browser

    # Sync
    dango sync my_sheets
    ```

    [Learn more →](oauth-sources.md)

=== "Database"

    ```bash
    # Configure .dlt/secrets.toml
    [sources.sql_database]
    credentials = "postgresql://user:pass@host:5432/db"

    # Edit .dango/sources.yml
    sources:
      - name: my_postgres
        type: dlt_native
        dlt_native:
          source_module: sql_database
          source_function: sql_database
          function_kwargs:
            schema: "public"

    # Sync
    dango sync my_postgres
    ```

    [Learn more →](database-sources.md)

=== "Custom API"

    ```python
    # custom_sources/my_api.py
    import dlt
    import requests

    @dlt.source
    def my_api():
        @dlt.resource(name="data")
        def get_data():
            return requests.get("https://api.example.com/data").json()
        return [get_data()]
    ```

    ```yaml
    # .dango/sources.yml
    sources:
      - name: my_api
        type: dlt_native
        dlt_native:
          source_module: my_api
          source_function: my_api
    ```

    [Learn more →](custom-sources.md)

---

## Source Type Guides

<div class="grid cards" markdown>

-   :material-file-delimited-outline: **Local Files**

    ---

    Load CSV, JSON, JSONL, and Parquet files with automatic schema detection and incremental sync.

    - 5 supported formats
    - File change tracking
    - Schema evolution support

    [:octicons-arrow-right-24: Local Files Guide](local-files/index.md)

-   :material-cloud-lock-outline: **OAuth Sources**

    ---

    Connect to cloud services using OAuth 2.0 authentication.

    - Google Sheets, GA4, Google Ads, Facebook Ads
    - Automatic token management
    - Browser-based authentication

    [:octicons-arrow-right-24: OAuth Sources Guide](oauth-sources.md)

-   :material-database-outline: **Database Sources**

    ---

    Connect to PostgreSQL, MySQL, SQL Server via dlt.

    - Full table or incremental loading
    - SSL/TLS support

    [:octicons-arrow-right-24: Database Sources Guide](database-sources.md)

-   :material-api: **Custom Sources**

    ---

    Build custom integrations using Python and dlt.

    - REST APIs
    - Web scraping
    - Custom data formats

    [:octicons-arrow-right-24: Custom Sources Guide](custom-sources.md)

-   :material-store-outline: **Source Catalog**

    ---

    Complete catalog of all 33 supported data sources.

    - Source types and auth methods
    - Configuration examples
    - Sync behavior details

    [:octicons-arrow-right-24: Source Catalog](source-catalog.md)

-   :material-plus-circle-outline: **Adding Sources**

    ---

    Step-by-step wizard walkthrough and manual YAML configuration.

    [:octicons-arrow-right-24: Adding Sources](adding-sources.md)

-   :material-sync-circle: **Sync Modes**

    ---

    Incremental loading, full refresh, and date range syncs.

    [:octicons-arrow-right-24: Sync Modes](sync-modes.md)

-   :material-content-duplicate: **Deduplication**

    ---

    Four strategies for handling duplicate records in your data.

    [:octicons-arrow-right-24: Deduplication](deduplication.md)

</div>

---

## Common Workflows

### Adding a New Source

1. **Choose source type** based on your data
2. **Run the wizard** with `dango source add` (or edit `sources.yml` manually)
3. **Configure credentials** (OAuth flow, API key in `.env`, or connection string)
4. **Sync** with `dango sync <name>`
5. **Verify** in Metabase or with `dango db query`

### Managing Multiple Sources

```yaml
# .dango/sources.yml
version: '1.0'
sources:
  # Production Stripe data
  - name: stripe_prod
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_PROD_API_KEY

  # Google Sheets for manual data
  - name: manual_overrides
    type: google_sheets
    enabled: true

  # PostgreSQL analytics database
  - name: analytics_db
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: sql_database
      source_function: sql_database

  # Local CSV exports
  - name: finance_reports
    type: local_files
    enabled: true
    local_files:
      directory: data/uploads/finance_reports
      file_pattern: "*.csv"
```

### Sync All Sources

```bash
# Sync all enabled sources
dango sync

# Sync specific source
dango sync stripe_prod

# List all sources
dango source list
```

---

## Data Flow

Understanding how data flows from sources to your warehouse:

```mermaid
graph LR
    A[Data Source] --> B[dlt]
    B --> C[Raw Layer]
    C --> D[DuckDB]
    D --> E[dbt Staging]
    E --> F[dbt Marts]
    F --> G[Metabase]

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#f3e5f5
    style D fill:#e8f5e9
    style E fill:#fff9c4
    style F fill:#ffebee
    style G fill:#e0f2f1
```

1. **Source** — External API, database, or file
2. **dlt** — Fetches and normalizes data
3. **Raw Layer** — Source data as-loaded in DuckDB
4. **Staging** — Clean starting point (auto-generated by Dango)
5. **Marts** — Business logic (custom SQL models you write)
6. **Metabase** — Dashboards and queries

[Learn more about data layers →](../core-concepts/data-layers.md)

---

## Source Configuration

### sources.yml Structure

```yaml
version: '1.0'
sources:
  - name: unique_source_name      # Identifier (lowercase, underscores)
    type: local_files              # Source type
    enabled: true                  # Toggle sync
    description: "Optional description"
    local_files:                   # Type-specific config
      directory: data/uploads/unique_source_name
      file_pattern: "*.csv"
```

### Common Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier for this source |
| `type` | Yes | Source type from the [catalog](source-catalog.md) |
| `enabled` | No | Whether to include in sync (default: `true`) |
| `description` | No | Human-readable description |
| `deduplication` | No | Strategy: `none`, `latest_only`, `append_only`, `scd_type2` |

### Credentials Management

**Never commit credentials!** Use one of these methods:

**Recommended: .env file** (persists across sessions)
```bash
# Create or edit .env file (gitignored by default)
echo 'MY_API_KEY=your-key-here' >> .env
```

**Or .dlt/secrets.toml** (gitignored credential storage)
```toml
[sources.stripe]
api_key = "sk_live_..."
```

**Or environment variables** (current session only)
```bash
export MY_API_KEY="your-key-here"
```

---

## Testing Status

| Source Type | Status | Notes |
|-------------|--------|-------|
| Local Files | :white_check_mark: Production-ready | CSV, JSON, JSONL, Parquet |
| Stripe | :white_check_mark: Production-ready | All resources supported |
| Google Sheets | :white_check_mark: Production-ready | OAuth flow verified |
| Google Analytics 4 | :white_check_mark: Production-ready | OAuth flow verified |
| Facebook Ads | :white_check_mark: Production-ready | OAuth flow verified |
| Google Ads | :white_check_mark: Production-ready | OAuth flow verified |
| HubSpot | :white_check_mark: Production-ready | Contacts, companies, deals, tickets |
| GitHub | :white_check_mark: Production-ready | Issues, PRs, commits |
| Salesforce | :white_check_mark: Tested | Service account auth |
| Slack | :white_check_mark: Tested | Channels, messages, users |
| PostgreSQL | :white_check_mark: Tested | Full table and incremental |
| MongoDB | :white_check_mark: Tested | Collections with filtering |
| REST API | :white_check_mark: Tested | Generic API connector |
| dlt_native | :white_check_mark: Tested | Registry bypass for any dlt source |
| Coming Soon sources | :material-clock-outline: Pending | Shopify, Matomo, Jira, Asana, Strapi, Personio |

---

## Best Practices

### 1. Use Descriptive Names

```yaml
# Good
- name: stripe_production_payments
- name: marketing_facebook_ads
- name: finance_google_sheets

# Avoid
- name: source1
- name: data
```

### 2. Enable Only What You Need

Disable unused sources to speed up sync:

```yaml
- name: old_source
  enabled: false  # Keeps config but skips sync
```

### 3. Document Your Sources

```yaml
- name: crm_export
  type: local_files
  description: "Weekly CRM export from sales team, updated every Monday"
  local_files:
    directory: data/uploads/crm_export
    file_pattern: "*.csv"
```

### 4. Use Incremental When Possible

Incremental sync is the default — it loads only new and changed data. See [Sync Modes](sync-modes.md) for details on when to use full refresh instead.

### 5. Monitor Source Health

```bash
# Validate all sources
dango validate

# Check specific source
dango source list
```

---

## Troubleshooting

### Source Not Syncing

1. Check `enabled: true` in sources.yml
2. Verify credentials in `.env` or `.dlt/secrets.toml`
3. Run `dango validate` to see errors
4. Check network connectivity

### Authentication Failures

- **API keys**: Verify not expired, check permissions
- **OAuth**: Re-authenticate with `dango oauth refresh <source_type>`
- **Database**: Test connection outside Dango

### Schema Mismatches

When APIs change:
1. Run `dango sync` (schema auto-updates for API sources, staging models regenerated)
2. Update custom dbt models if needed

!!! note "File schema changes"
    For local file sources, schema is fixed on first load. Use `--allow-schema-changes` to add new columns, or `--full-refresh` to reload with a new schema. See [Local Files](local-files/index.md).

### Performance Issues

- Use incremental loading for large datasets (default behavior)
- Sync sources individually rather than all at once
- Check API rate limits
- Use `--limit N` during development to cap row counts

---

## Next Steps

<div class="grid cards" markdown>

-   :material-plus-circle-outline: **Adding Sources**

    ---

    Step-by-step wizard walkthrough for your first source.

    [:octicons-arrow-right-24: Adding Sources](adding-sources.md)

-   :material-store-outline: **Source Catalog**

    ---

    Explore all 33 supported data source types.

    [:octicons-arrow-right-24: Source Catalog](source-catalog.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Transform your loaded data with dbt.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

</div>
