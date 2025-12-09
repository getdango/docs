# Data Sources

Connect to CSV files, APIs, databases, and 30+ verified dlt sources.

---

## Overview

Dango supports multiple types of data sources through dlt (data load tool). Whether you're working with local CSV files, cloud APIs, or existing databases, Dango provides a unified configuration interface.

!!! info "Wizard vs Manual Sources"
    **Wizard-supported sources** (8 sources): Can be added via `dango source add` interactive wizard:

    - CSV, dlt Native, REST API, Google Sheets, Facebook Ads, Google Analytics 4, Stripe, Google Ads

    **Manual sources** (25+ sources): Require dlt_native configuration in sources.yml:

    - HubSpot, Notion, Asana, Shopify, PostgreSQL, MySQL, and all other dlt verified sources
    - See [Custom Sources](custom-sources.md) for manual setup guide

**Available Source Types**:

- **CSV Files** - Upload and auto-sync flat files
- **OAuth Sources** - Google Sheets, Facebook Ads, GA4, Google Ads (wizard-supported)
- **Built-in dlt Sources** - 30+ verified integrations (requires manual dlt_native config)
- **Database Sources** - PostgreSQL, MySQL, SQL Server, Snowflake (requires manual config)
- **Custom Sources** - Build your own Python-based integrations

---

## Quick Start

### Add Your First Source

Choose your source type and follow the guide:

=== "CSV File"

    ```bash
    # Edit .dango/sources.yml
    sources:
      - name: sales_data
        type: csv
        enabled: true
        csv:
          file_path: data/sales.csv
          delimiter: ","
          header: true

    # Sync
    dango sync --source sales_data
    ```

    [Learn more →](csv-files.md)

=== "OAuth (Google Sheets)"

    ```bash
    # Interactive setup
    dango source add google_sheets
    # Follow OAuth flow in browser

    # Sync
    dango sync --source my_sheets
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
    dango sync --source my_postgres
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

-   :material-file-delimited-outline: **CSV Files**

    ---

    Upload and sync CSV files with automatic schema detection and file watching.

    - Simple file-based data loading
    - Auto-sync on file changes
    - Multiple delimiters supported

    [:octicons-arrow-right-24: CSV Files Guide](csv-files.md)

-   :material-cloud-lock-outline: **OAuth Sources**

    ---

    Connect to cloud services using OAuth 2.0 authentication.

    - Google Sheets, GA4, Facebook Ads
    - Automatic token management
    - Browser-based authentication

    [:octicons-arrow-right-24: OAuth Sources Guide](oauth-sources.md)

-   :material-database-outline: **Database Sources**

    ---

    Connect to PostgreSQL, MySQL, SQL Server, and 30+ databases.

    - Full table or incremental loading
    - SSL/TLS support
    - Read-only access recommended

    [:octicons-arrow-right-24: Database Sources Guide](database-sources.md)

-   :material-api: **Custom Sources**

    ---

    Build custom integrations using Python and dlt.

    - REST APIs
    - Web scraping
    - Custom data formats

    [:octicons-arrow-right-24: Custom Sources Guide](custom-sources.md)

-   :material-store-outline: **Built-in Sources**

    ---

    Explore 30+ verified dlt sources for popular SaaS platforms.

    - Stripe, HubSpot, Salesforce
    - Production-tested integrations
    - Regular community updates

    [:octicons-arrow-right-24: Built-in Sources Catalog](built-in-sources.md)

</div>

---

## Common Workflows

### Adding a New Source

1. **Choose source type** based on your data
2. **Configure credentials** (if needed)
3. **Add to sources.yml** or use `dango source add`
4. **Sync** with `dango sync --source <name>`
5. **Verify** in Metabase or with SQL

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
      stripe_secret_key_env: STRIPE_PROD_KEY

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

  # Custom internal API
  - name: internal_api
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: internal_api
      source_function: internal_api
```

### Sync All Sources

```bash
# Sync all enabled sources
dango sync

# Sync specific source
dango sync --source stripe_prod

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

1. **Source** - External API, database, or file
2. **dlt** - Fetches and normalizes data
3. **Raw Layer** - Immutable source of truth in DuckDB
4. **Staging** - Cleaned, deduplicated (auto-generated by Dango)
5. **Marts** - Business logic (custom SQL models)
6. **Metabase** - Dashboards and queries

[Learn more about data layers →](../core-concepts/data-layers.md)

---

## Source Configuration

### sources.yml Structure

```yaml
version: '1.0'
sources:
  - name: unique_source_name      # Identifier
    type: csv                      # Source type
    enabled: true                  # Toggle sync
    description: "Optional description"
    csv:                           # Type-specific config
      file_path: data/file.csv
      delimiter: ","
```

### Common Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier for this source |
| `type` | Yes | Source type: `csv`, `stripe`, `dlt_native`, etc. |
| `enabled` | No | Whether to include in sync (default: `true`) |
| `description` | No | Human-readable description |

### Credentials Management

**Never commit credentials!** Use:

- **Environment variables**: `export MY_API_KEY="..."`
- **.dlt/secrets.toml**: Gitignored credential storage
- **.env files**: Gitignored environment configs

```bash
# .gitignore (automatically created by Dango)
.dlt/secrets.toml
.dlt/config.toml
.env
*.env
```

---

## Testing Status

| Source Type | Status | Notes |
|-------------|--------|-------|
| CSV | ✅ Tested | Production-ready |
| Stripe | ✅ Tested | All resources supported |
| Google Sheets | ✅ Tested | OAuth flow verified |
| Google Analytics 4 | ✅ Tested | Custom dimensions/metrics |
| Facebook Ads | ✅ Tested | Campaign insights |
| PostgreSQL | ✅ Tested | Full table + incremental |
| MySQL | ✅ Tested | Full table + incremental |
| Custom (dlt_native) | ✅ Tested | Verified with multiple APIs |
| Google Ads | 🔄 Planned | v0.1.0 milestone |
| Other dlt sources | 🔄 Available | See [Built-in Sources](built-in-sources.md) |

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
  type: csv
  description: "Weekly CRM export from sales team, updated every Monday"
  csv:
    file_path: data/crm/weekly_export.csv
```

### 4. Use Incremental When Possible

For large datasets, configure incremental loading:

```yaml
- name: large_table
  type: dlt_native
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      incremental:
        cursor_column: "updated_at"
        initial_value: "2024-01-01"
```

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
2. Verify credentials in `.dlt/secrets.toml` or environment
3. Run `dango validate` to see errors
4. Check network connectivity

### Authentication Failures

- **API keys**: Verify not expired, check permissions
- **OAuth**: Re-authenticate with `dango source add`
- **Database**: Test connection outside Dango

### Schema Mismatches

When APIs change:
1. Run `dango sync` (schema auto-updates)
2. Run `dango generate` to update staging models
3. Update custom dbt models if needed

### Performance Issues

- Use incremental loading for large tables
- Sync sources individually rather than all at once
- Check API rate limits
- Consider upgrading to paid API tiers

---

## Next Steps

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **Core Concepts**

    ---

    Understand how data flows through Dango's layered architecture.

    [:octicons-arrow-right-24: Core Concepts](../core-concepts/index.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Learn how to transform raw source data with dbt.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

-   :material-chart-line: **Dashboards**

    ---

    Visualize your source data in Metabase dashboards.

    [:octicons-arrow-right-24: Dashboards](../dashboards/index.md)

</div>
