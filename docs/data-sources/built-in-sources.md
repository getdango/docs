# Built-in Sources

Overview of dlt verified sources available in Dango.

---

## Overview

Dango leverages dlt's ecosystem of verified sources - production-tested integrations for popular SaaS platforms and APIs. These sources are maintained by the dlt community and require minimal configuration.

**Key Benefits**:

- Pre-built, tested integrations
- Automatic schema evolution
- Incremental loading support
- OAuth handling (where applicable)
- Regular updates from dlt community

---

## Tested Sources in Dango

The following sources have been tested and validated with Dango:

### Stripe

**What it loads**: Charges, customers, subscriptions, invoices, products, payment intents

```yaml
- name: stripe_payments
  type: stripe
  enabled: true
  stripe:
    stripe_secret_key_env: STRIPE_API_KEY
    start_date: "2024-01-01"
```

**Setup**:
```bash
export STRIPE_API_KEY="sk_test_..."
dango sync --source stripe_payments
```

**Tables loaded**: `raw_stripe.charges`, `raw_stripe.customers`, `raw_stripe.subscriptions`, etc.

---

### Google Sheets

**What it loads**: Spreadsheet data as tables (one table per sheet)

```yaml
- name: my_sheets
  type: google_sheets
  enabled: true
  google_sheets:
    spreadsheet_url: "https://docs.google.com/spreadsheets/d/1ABC..."
    get_sheets:
      - "Sheet1"
      - "Sales Data"
```

**Setup**:
```bash
dango source add
# Select "Google Sheets" from the list
# Follow OAuth flow in browser
```

**Tables loaded**: `raw_my_sheets.sheet1`, `raw_my_sheets.sales_data`

---

### Google Analytics 4 (GA4)

**What it loads**: Website analytics data with custom dimensions and metrics

```yaml
- name: website_analytics
  type: google_analytics
  enabled: true
  google_analytics:
    property_id: "123456789"
    start_date: "2024-01-01"
    dimensions:
      - date
      - country
      - deviceCategory
    metrics:
      - sessions
      - pageviews
      - conversions
```

**Setup**:
```bash
dango source add
# Select "Google Analytics 4" from the list
# Follow OAuth flow
# Enter GA4 property ID when prompted
```

---

### Facebook Ads

**What it loads**: Campaigns, ad sets, ads, insights

```yaml
- name: facebook_campaigns
  type: facebook_ads
  enabled: true
  facebook_ads:
    account_id: "act_123456789"
    start_date: "2024-01-01"
    include_deleted: false
```

**Setup**:
```bash
dango source add
# Select "Facebook Ads" from the list
# Follow OAuth flow
# Select ad account when prompted
```

---

### CSV Files

**What it loads**: Flat CSV files with automatic schema detection

```yaml
- name: sales_data
  type: csv
  enabled: true
  csv:
    directory: data/uploads/sales_data
    file_pattern: "*.csv"
```

**Setup**: See [CSV Files](csv-files.md) for details

---

## Available Sources (dlt Verified)

The following sources are available through dlt and can be configured in Dango. **Note**: Not all sources have been tested with Dango v0.0.5.

### Marketing & Advertising

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| **Google Analytics 4** | `google_analytics` | OAuth | ✅ Tested |
| **Facebook Ads** | `facebook_ads` | OAuth | ✅ Tested |
| **Google Ads** | `google_ads` | OAuth | 🔄 Wizard-supported (testing in progress) |
| Matomo | `matomo` | API token | ⚠️ Available via dlt_native (untested) |

### CRM & Sales

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| **Stripe** | `stripe` | API key | ✅ Tested |
| HubSpot | `hubspot` | OAuth | ⚠️ Available via dlt_native (untested) |
| Salesforce | `salesforce` | OAuth | ⚠️ Available via dlt_native (untested) |
| Pipedrive | `pipedrive` | API token | ⚠️ Available via dlt_native (untested) |

### Productivity & Collaboration

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| **Google Sheets** | `google_sheets` | OAuth | ✅ Tested |
| Notion | `notion` | OAuth | ⚠️ Available via dlt_native (untested) |
| Asana | `asana` | OAuth | ⚠️ Available via dlt_native (untested) |
| Slack | `slack` | OAuth | ⚠️ Available via dlt_native (untested) |
| Airtable | `airtable` | API key | ⚠️ Available via dlt_native (untested) |

### Databases

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| PostgreSQL | `sql_database` | Connection string | ⚠️ Experimental (uses dlt sql_database) |
| MySQL | `sql_database` | Connection string | ⚠️ Experimental (uses dlt sql_database) |
| SQL Server | `sql_database` | Connection string | ⚠️ Available via dlt_native (untested) |
| MongoDB | `mongodb` | Connection string | ⚠️ Available via dlt_native (untested) |

### Data Warehouses

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| Snowflake | `sql_database` | Connection string | ⚠️ Available via dlt_native (untested) |
| BigQuery | `sql_database` | Service account | ⚠️ Available via dlt_native (untested) |
| Redshift | `sql_database` | Connection string | ⚠️ Available via dlt_native (untested) |

### E-commerce

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| Shopify | `shopify` | OAuth | 🔄 Deferred (awaiting dlt auth update) |
| WooCommerce | `woocommerce` | API key | ⚠️ Available via dlt_native (untested) |

### Other

| Source | Type | Authentication | Status |
|--------|------|---------------|--------|
| GitHub | `github` | Personal token | ⚠️ Available via dlt_native (untested) |
| Jira | `jira` | API token | ⚠️ Available via dlt_native (untested) |
| Zendesk | `zendesk` | API token | ⚠️ Available via dlt_native (untested) |
| Intercom | `intercom` | API token | ⚠️ Available via dlt_native (untested) |

**Full list**: See [dlt Verified Sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources) for complete catalog.

---

## Configuration Patterns

### API Key Authentication

```yaml
- name: my_source
  type: <source_type>
  enabled: true
  <source_type>:
    api_key_env: MY_API_KEY
```

Set environment variable:
```bash
export MY_API_KEY="your-key-here"
```

### OAuth Authentication

```yaml
- name: my_oauth_source
  type: <source_type>
  enabled: true
  <source_type>:
    # OAuth credentials stored in .dlt/secrets.toml
```

Authenticate:
```bash
dango source add
# Select OAuth source from the list
# Follow browser OAuth flow
```

### Connection String (Databases)

```yaml
- name: my_database
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "public"
```

Credentials in `.dlt/secrets.toml`:
```toml
[sources.sql_database]
credentials = "postgresql://user:pass@host:5432/db"
```

---

## Testing Untested Sources

Want to try a dlt source that hasn't been tested with Dango? Here's how:

### Step 1: Check dlt Documentation

Visit [dlt Verified Sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources) and find your source.

### Step 2: Install Dependencies

Most sources require extras:

```bash
pip install "dlt[<source_name>]"

# Example
pip install "dlt[hubspot]"
```

### Step 3: Configure as dlt_native

Add to `.dango/sources.yml`:

```yaml
- name: my_hubspot
  type: dlt_native
  enabled: true
  description: HubSpot CRM data
  dlt_native:
    source_module: hubspot
    source_function: hubspot
    function_kwargs: {}
```

### Step 4: Set Up Credentials

Follow dlt documentation for credential format. Add to `.dlt/secrets.toml`:

```toml
[sources.hubspot]
api_key = "your-api-key"
```

### Step 5: Test

```bash
dango sync --source my_hubspot
```

### Step 6: Share Results

If it works, please share on [GitHub Discussions](https://github.com/getdango/dango/discussions) to help the community!

---

## Incremental Loading

Many dlt sources support incremental loading - fetching only new/changed data since the last sync.

### How It Works

```yaml
- name: stripe_incremental
  type: stripe
  enabled: true
  stripe:
    stripe_secret_key_env: STRIPE_API_KEY
    start_date: "2024-01-01"  # Initial load
    # On subsequent syncs: only data after last sync
```

**First sync**:
- Loads all data since `start_date`
- Stores latest timestamp in `_dlt_loads` table

**Subsequent syncs**:
- Only loads data newer than last sync
- Much faster for large datasets

### Supported Sources

Most API sources support incremental:
- ✅ Stripe (charges, customers, etc.)
- ✅ Google Analytics 4 (date-based)
- ✅ Facebook Ads (insights)
- ✅ HubSpot (contacts, deals)
- ✅ Database sources (with cursor column)

---

## Schema Evolution

dlt sources automatically handle schema changes:

### What Happens When API Changes

1. **New fields added**: Automatically added to DuckDB table
2. **Fields removed**: Existing columns remain (populated with NULL)
3. **Data types changed**: dlt attempts coercion or creates new variant column

### Re-generating dbt Models

When schema changes, staging models are automatically regenerated during sync. To manually trigger regeneration:

```bash
dango sync --source <source_name>
```

This updates:
- Column lists in staging models
- Data type casts
- Documentation in schema.yml

---

## Best Practices

### 1. Start with Tested Sources

Use tested sources (Stripe, Google Sheets, GA4, Facebook Ads, CSV) for production data pipelines.

### 2. Read dlt Documentation

For untested sources, consult [dlt docs](https://dlthub.com/docs) for:
- Required credentials format
- Available configuration options
- Known limitations

### 3. Use Incremental When Possible

For large datasets:
- Set `start_date` for initial historical load
- Use incremental for subsequent syncs
- Reduces API calls and sync time

### 4. Monitor Rate Limits

APIs have rate limits:
- Stripe: 100 requests/second
- Facebook Ads: Varies by tier
- Google Analytics 4: 10 concurrent requests

Dango respects these automatically via dlt.

### 5. Secure Your Credentials

- Use environment variables for API keys
- Never commit `.dlt/secrets.toml`
- Rotate keys regularly
- Use read-only permissions where possible

---

## Troubleshooting

### Source Not Found

**Problem**: `Could not import source module: <source_name>`

**Solution**: Install dlt extras:
```bash
pip install "dlt[<source_name>]"
```

### Authentication Failed

**Problem**: `401 Unauthorized` or `403 Forbidden`

**Solution**:
1. Verify API key/token is correct
2. Check token hasn't expired
3. Ensure sufficient permissions
4. For OAuth: re-authenticate with `dango source add`

### No Data Loaded

**Problem**: Sync completes but no tables created

**Solution**:
1. Check `start_date` isn't in the future
2. Verify account has data in source system
3. Check dlt documentation for required parameters
4. Look for errors in sync output

### Rate Limit Errors

**Problem**: `429 Too Many Requests`

**Solution**:
1. Wait before retrying (dlt handles backoff automatically)
2. Reduce sync frequency
3. Contact provider to increase limits

---

## Source Request

Missing a source you need? We prioritize based on community demand.

**Request a source**:
1. Check if it exists in [dlt verified sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources)
2. If yes: Open [GitHub Discussion](https://github.com/getdango/dango/discussions) requesting Dango testing
3. If no: Consider creating a [custom source](custom-sources.md)

**Most requested**:
- Google Ads (wizard-supported, testing in progress)
- Salesforce (available via dlt_native)
- HubSpot (available via dlt_native)

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - Set up OAuth authentication
- **[Custom Sources](custom-sources.md)** - Build your own integrations
- **[Database Sources](database-sources.md)** - Connect to SQL databases
- **[dlt Verified Sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources)** - Full dlt catalog
