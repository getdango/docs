# Data Sources

Connect to CSV files, APIs, and databases through Dango's unified configuration.

---

## Overview

Dango supports multiple types of data sources through dlt (data load tool). Whether you're working with local CSV files, cloud APIs, or existing databases, Dango provides a unified configuration interface.

!!! info "Wizard vs Manual Sources"
    **Wizard-supported sources** (7 sources): Can be added via `dango source add` interactive wizard:

    - CSV, Stripe, Google Sheets, Facebook Ads, Google Analytics 4, Google Ads, dlt Native (advanced)

    **Manual sources**: Require dlt_native configuration in sources.yml:

    - HubSpot, Notion, Asana, databases, and other dlt sources
    - See [Custom Sources](custom-sources.md) for manual setup guide

    **60+ additional sources** available via dlt_native for advanced users.

**Available Source Types**:

- **CSV Files** - Upload and auto-sync flat files (wizard-supported)
- **OAuth Sources** - Google Sheets, Facebook Ads, GA4, Google Ads (wizard-supported)
- **Stripe** - Payment data (wizard-supported)
- **Database Sources** - PostgreSQL, MySQL, etc. via dlt_native (experimental)
- **Custom Sources** - Build your own or use any dlt verified source via dlt_native

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

- [Custom Sources](custom-sources.md) - "dlt vs. Dango Workflow" comparison
- [Database Sources](database-sources.md) - "How This Differs from Standard dlt" table
- [dlt Documentation](https://dlthub.com/docs) - Official dlt docs for advanced topics

---

## Quick Start

### Add Your First Source

Choose your source type and follow the guide:

=== "CSV File"

    ```bash
    # Recommended: Use the wizard
    dango source add
    # Select "CSV Files" and follow prompts
    ```

    Or configure manually in `.dango/sources.yml`:

    ```yaml
    sources:
      - name: sales_data
        type: csv
        enabled: true
        csv:
          directory: data/uploads/sales_data
          file_pattern: "*.csv"
    ```

    Then copy files and sync:

    ```bash
    cp my_sales.csv data/uploads/sales_data/
    dango sync --source sales_data
    ```

    [Learn more →](csv-files.md)

=== "OAuth (Google Sheets)"

    ```bash
    # Interactive setup
    dango source add
    # Select "Google Sheets" from the list
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

    Connect to PostgreSQL, MySQL, SQL Server via dlt_native.

    - Full table or incremental loading
    - SSL/TLS support
    - Experimental (not fully tested)

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

    Explore wizard-supported sources and dlt_native options.

    - 7 wizard-supported sources
    - 60+ available via dlt_native
    - Community-maintained dlt sources

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
3. **Raw Layer** - Source data as-loaded in DuckDB
4. **Staging** - Clean starting point (auto-generated by Dango)
5. **Marts** - Business logic (custom SQL models you write)
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
      directory: data/uploads/unique_source_name
      file_pattern: "*.csv"
```

### Common Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier for this source |
| `type` | Yes | Source type: `csv`, `stripe`, `dlt_native`, etc. |
| `enabled` | No | Whether to include in sync (default: `true`) |
| `description` | No | Human-readable description |

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
| CSV | ✅ Tested | Production-ready |
| Stripe | ✅ Tested | All resources supported |
| Google Sheets | ✅ Tested | OAuth flow verified |
| Google Analytics 4 | ✅ Tested | OAuth flow verified |
| Facebook Ads | ✅ Tested | OAuth flow verified |
| Google Ads | 🔄 In Progress | Wizard-supported, testing ongoing |
| dlt_native | ✅ Works | Registry bypass verified |
| Database sources | ⚠️ Experimental | Uses dlt sql_database, not fully tested |
| Other dlt sources | ⚠️ Experimental | Available via dlt_native, see [Built-in Sources](built-in-sources.md) |

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
    directory: data/uploads/crm_export
    file_pattern: "*.csv"
    notes: "Export from Salesforce > Reports > Weekly CRM"
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
1. Run `dango sync` (schema auto-updates for API sources, staging models regenerated)
2. Update custom dbt models if needed

!!! note "CSV schema changes"
    For CSV sources, schema is fixed on first load. If your CSV schema changes, remove and re-add the source.

### Performance Issues

- Use incremental loading for large tables
- Sync sources individually rather than all at once
- Check API rate limits
- Consider upgrading to paid API tiers

---

## Next Steps

<div class="grid cards" markdown>

-   :material-file-delimited-outline: **CSV Files**

    ---

    Start with the simplest source type - local CSV files.

    [:octicons-arrow-right-24: CSV Files Guide](csv-files.md)

-   :material-store-outline: **Built-in Sources**

    ---

    Explore wizard-supported and dlt_native sources.

    [:octicons-arrow-right-24: Built-in Sources](built-in-sources.md)

-   :material-application-braces-outline: **Transformations**

    ---

    Transform your loaded data with dbt.

    [:octicons-arrow-right-24: Transformations](../transformations/index.md)

</div>
