# Source Management

CLI commands for managing data sources.

---

## Overview

Manage data sources entirely from the command line. Add, list, edit, and remove sources using the `dango source` command family.

**What you'll learn**:

- Add sources interactively or non-interactively
- List and inspect configured sources
- Edit source configuration
- Remove sources safely
- Manage OAuth credentials
- Import/export source configurations

---

## Adding Sources

### Interactive Source Wizard

Launch the interactive wizard:

```bash
dango source add
```

**Wizard flow**:

```
Welcome to Dango Source Wizard

Select source type:
  1. CSV files
  2. dlt Native (advanced - for manual source configuration)
  3. REST API
  4. Google Sheets
  5. Facebook Ads
  6. Google Analytics 4 (GA4)
  7. Stripe
  8. Google Ads

For other sources (HubSpot, Notion, Asana, etc.), select "dlt Native"
and configure manually. See: https://docs.getdango.dev/data-sources/custom-sources/

Choice: 7

──────────────────────────────────────
Stripe Source Configuration
──────────────────────────────────────

Source name (unique identifier): stripe_payments

API Key:
  Where is your Stripe API key stored?
  1. Environment variable (recommended)
  2. .dlt/secrets.toml

Choice: 1
Environment variable name: STRIPE_API_KEY

Start date (YYYY-MM-DD) [2024-01-01]: 2024-06-01

Resources to sync:
  [x] charges
  [x] customers
  [x] subscriptions
  [ ] invoices
  [ ] payment_intents
  [ ] refunds

Enable source now? [Y/n]: y

Testing connection...
✓ API key valid
✓ Connected to Stripe API
✓ Fetched sample data (10 records)

Save configuration? [Y/n]: y

✓ Source added to .dango/sources.yml
✓ Credentials stored in .env

Next steps:
  dango sync --source stripe_payments   # Load data
  dango generate --source stripe_payments  # Create staging models
```

### Non-Interactive Add

Specify source type directly:

```bash
dango source add stripe
```

**Prompts for configuration** without full wizard:

```
Source name: stripe_payments
API Key (env var): STRIPE_API_KEY
Start date [2024-01-01]: 2024-06-01
✓ Source added
```

### Add from Configuration File

Create a YAML file with source configuration:

```yaml
# stripe-prod.yml
name: stripe_production
type: stripe
enabled: true
stripe:
  stripe_secret_key_env: STRIPE_PROD_API_KEY
  start_date: 2024-01-01
  resources:
    - charges
    - customers
    - subscriptions
```

**Add from file**:

```bash
dango source add --config stripe-prod.yml
```

**Output**:

```
Loading configuration from stripe-prod.yml...
✓ Configuration valid
✓ Source 'stripe_production' added
```

### Add with Name

Specify name upfront:

```bash
dango source add stripe --name stripe_production
```

**Wizard skips name prompt**:

```
Source name: stripe_production (provided)
API Key (env var): STRIPE_PROD_API_KEY
...
```

### Skip Connection Test

Add source without testing connection:

```bash
dango source add --skip-test
```

**Use when**:

- Credentials not yet available
- Testing configuration syntax
- Offline setup

**Warning**: Source may fail during sync if credentials invalid.

---

## Listing Sources

### List All Sources

```bash
dango source list
```

**Output**:

```
Configured Sources:

  ● stripe_payments (stripe) - Enabled
      Last synced: 2024-12-09 12:34:56
      Rows: 1,865
      Tables: charges, customers, subscriptions
      Status: Healthy

  ● google_sheets (google_sheets) - Enabled
      Last synced: 2024-12-09 08:15:23
      Rows: 234
      Tables: marketing_budget
      Status: OAuth expires in 6 days

  ● orders_csv (csv) - Enabled
      Last synced: 2024-12-08 18:45:12
      Rows: 5,432
      File: data/orders.csv
      Status: Healthy

  ○ old_hubspot (hubspot) - Disabled
      Last synced: 2024-12-04 14:22:10 (5 days ago)
      Rows: 2,341
      Status: Disabled in config

  ✗ legacy_database (dlt_native) - Enabled
      Last synced: Never
      Status: Connection failed
```

### Filter by Status

**Enabled sources only**:

```bash
dango source list --enabled-only
```

### Source Details

The `source list` command shows comprehensive information:

**Output**:

```
stripe_payments (stripe)
  Status: Enabled
  Type: stripe
  Last sync: 2024-12-09 12:34:56
  Sync frequency: Every 1 hour
  Next sync: 2024-12-09 13:34:56

  Configuration:
    API Key: STRIPE_API_KEY (from environment)
    Start date: 2024-06-01
    Resources: charges, customers, subscriptions
    Incremental: Yes (cursor: created)

  Data:
    Tables: 3
    Total rows: 1,865
    Last row: 2024-12-09 12:30:00
    Data freshness: 5 minutes

  Health:
    Status: Healthy
    Last error: None
    Success rate: 98.5% (last 30 syncs)

────────────────────────────────────────
```

### JSON Output

For scripting:

```bash
dango source list --json
```

**Response**:

```json
{
  "sources": [
    {
      "name": "stripe_payments",
      "type": "stripe",
      "enabled": true,
      "last_sync": "2024-12-09T12:34:56Z",
      "rows": 1865,
      "tables": ["charges", "customers", "subscriptions"],
      "status": "healthy",
      "config": {
        "stripe_secret_key_env": "STRIPE_API_KEY",
        "start_date": "2024-06-01"
      }
    }
  ]
}
```

---

## Editing Sources

!!! note "No Edit Command"
    Dango does not have a `source edit` command. Edit sources manually:

### Edit Configuration

**Edit sources.yml directly**:

```bash
vim .dango/sources.yml
```

**Find your source**:

```yaml
sources:
  - name: stripe_payments
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      start_date: 2024-06-01
      resources:
        - charges
        - customers
        - subscriptions
```

**Make changes**, save, and validate:

```bash
dango validate
```

### Enable/Disable Source

!!! note "No Enable/Disable Commands"
    Dango does not have `source enable` or `source disable` commands. Edit sources.yml manually:

**Disable source** (edit `.dango/sources.yml`):

```yaml
sources:
  - name: stripe_payments
    enabled: false  # Change from true to false
```

**Enable source** (edit `.dango/sources.yml`):

```yaml
sources:
  - name: stripe_payments
    enabled: true  # Change from false to true
```

**Effect**:

- Disabled sources skipped during `dango sync`
- Data remains in database
- Can re-enable anytime

### Update Credentials

**Method 1: Environment variables**

```bash
# Edit .env
vim .env

# Add or update
STRIPE_API_KEY=sk_live_NEW_KEY

# Test
dango sync --source stripe_payments --dry-run
```

**Method 2: dlt secrets file**

```bash
# Edit .dlt/secrets.toml
vim .dlt/secrets.toml

# Add or update
[sources.stripe]
stripe_secret_key = "sk_live_NEW_KEY"

# Test
dango sync --source stripe_payments --dry-run
```

**Method 3: Re-run wizard**

```bash
dango source add stripe --name stripe_payments
```

**Prompts**:

```
Source 'stripe_payments' already exists.
Update configuration? (y/N): y

API Key (env var) [STRIPE_API_KEY]: STRIPE_NEW_API_KEY
Start date [2024-06-01]: 2024-06-01
...

✓ Source updated
```

### Clone Source

!!! note "No Clone Command"
    Dango does not have a `source clone` command. To duplicate a source:

    1. Manually copy the source configuration in `.dango/sources.yml`
    2. Change the `name` field to a new name
    3. Update credentials in `.dlt/secrets.toml` if needed

**Example** (manually copying in `.dango/sources.yml`):

```yaml
sources:
  # Original source
  - name: stripe_payments
    type: stripe
    enabled: true

  # Manually cloned source with new name
  - name: stripe_staging
    type: stripe
    enabled: true
```

---

## Removing Sources

### Remove Source

```bash
dango source remove stripe_payments
```

**Interactive confirmation**:

```
Remove source 'stripe_payments'?

This will:
  ✓ Remove from .dango/sources.yml
  ✓ Keep data in database (raw_stripe.*)

This will NOT:
  ✗ Delete data from database
  ✗ Remove staging models

To also delete data:
  dango source remove stripe_payments --delete-data

Proceed? (y/N): y

✓ Source removed from configuration
Data remains in raw_stripe schema.
Run 'dango db clean' to remove orphaned data.
```

### Remove and Delete Data

```bash
dango source remove stripe_payments --delete-data
```

**Confirmation**:

```
Remove source 'stripe_payments' and DELETE DATA?

This will:
  ✗ Remove from .dango/sources.yml
  ✗ DROP database tables (raw_stripe.*)
  ✗ Remove staging models (stg_stripe_*)

⚠ THIS CANNOT BE UNDONE!

Tables to delete:
  - raw_stripe.charges (28,351 rows, 12.3 MB)
  - raw_stripe.customers (1,234 rows, 0.5 MB)
  - raw_stripe.subscriptions (5,678 rows, 2.1 MB)

Total: 35,263 rows, 14.9 MB will be deleted

Type source name to confirm: stripe_payments

✓ Source removed
✓ Database tables dropped
✓ Staging models removed
```

### Force Remove

Skip confirmation:

```bash
dango source remove stripe_payments --force
```

**Use in scripts**:

```bash
#!/bin/bash
# Remove old sources
dango source remove old_hubspot --force
dango source remove legacy_database --force
```

---

## OAuth Source Management

### Authenticate OAuth Source

For OAuth sources (Google, Facebook, etc.):

```bash
dango auth google_sheets
```

**Flow**:

```
Opening browser for Google OAuth...
✓ Browser opened at: https://accounts.google.com/...

Please authorize Dango to access:
  - Google Sheets (read-only)

Waiting for callback...
✓ Authorization successful
✓ Credentials stored in .dlt/secrets.toml

You can now add Google Sheets sources:
  dango source add google_sheets
```

### Add OAuth Source

After authentication:

```bash
dango source add google_sheets
```

**Wizard**:

```
Source name: company_budget
Spreadsheet URL or ID: https://docs.google.com/spreadsheets/d/ABC123.../edit
Sheet names (comma-separated) [all]: Sheet1, Budget 2024

Testing connection...
✓ Connected to Google Sheets
✓ Found 2 sheets
✓ Fetched sample data

✓ Source added
```

### List OAuth Credentials

```bash
dango auth list
```

**Output**:

```
OAuth Credentials:

  ✓ google_sheets_source
      Provider: Google OAuth
      Scopes: spreadsheets.readonly
      Expires: 2024-12-15 (6 days)
      Status: Valid

  ✗ facebook_ads_source
      Provider: Facebook OAuth
      Scopes: ads_read
      Expires: 2024-11-20 (EXPIRED 19 days ago)
      Status: Expired - Re-authenticate required

  ✓ google_analytics_source
      Provider: Google OAuth
      Scopes: analytics.readonly
      Expires: 2025-01-15 (37 days)
      Status: Valid
```

### Refresh OAuth Credentials

When credentials expire:

```bash
dango auth refresh facebook_ads_source
```

**Flow**:

```
Opening browser for Facebook OAuth...
✓ Browser opened

Waiting for authorization...
✓ Authorization successful
✓ Credentials refreshed

New expiry: 2025-01-15 (60 days)
```

### Check OAuth Status

```bash
dango auth status
```

**Output**:

```
OAuth Status:

Expired:
  - facebook_ads_source (expired 19 days ago)
    Action: dango auth refresh facebook_ads_source

Expiring Soon (< 7 days):
  - google_sheets_source (expires in 6 days)
    Action: dango auth refresh google_sheets_source

Healthy:
  - google_analytics_source (expires in 37 days)
```

---

## CSV File Sources

### Add CSV Source

```bash
dango source add csv
```

**Wizard**:

```
Source name: sales_data
CSV file path: data/sales.csv

Auto-detect settings? [Y/n]: y

Analyzing data/sales.csv...
✓ Detected delimiter: , (comma)
✓ Detected header: Yes (row 1)
✓ Detected encoding: UTF-8
✓ Detected 10 columns

Preview (first 5 rows):
┌────────────┬──────────┬────────┬─────────┐
│ order_id   │ customer │ amount │ date    │
├────────────┼──────────┼────────┼─────────┤
│ ORD-00001  │ C-1234   │ 129.99 │ 2024-01-15 │
│ ORD-00002  │ C-5678   │  49.99 │ 2024-01-16 │
...

Settings look correct? [Y/n]: y

✓ Source added
Run 'dango sync --source sales_data' to load data.
```

### Manual CSV Configuration

```yaml
# .dango/sources.yml
sources:
  - name: sales_data
    type: csv
    enabled: true
    csv:
      file_path: data/sales.csv
      delimiter: ","
      header: true
      encoding: utf-8
      date_format: "%Y-%m-%d"
```

### CSV with Auto-Sync

Enable file watcher:

```yaml
sources:
  - name: sales_data
    type: csv
    enabled: true
    csv:
      file_path: data/sales.csv
      auto_sync: true  # Watch for file changes
```

**Or platform-wide** in `.dango/project.yml`:

```yaml
platform:
  file_watcher:
    enabled: true
    patterns:
      - "*.csv"
    debounce_seconds: 600
```

**Behavior**:

1. You edit `data/sales.csv`
2. File watcher detects change
3. Waits 600 seconds (10 minutes)
4. Automatically runs `dango sync --source sales_data`

---

## Database Sources

### Add PostgreSQL Source

```bash
dango source add postgres
```

**Wizard**:

```
Source name: production_db

Connection:
  Host: db.acme.com
  Port [5432]: 5432
  Database: analytics
  Username: readonly_user
  Password: ****************

  SSL Mode:
    1. disable
    2. allow
    3. prefer
    4. require
  Choice [4]: 4

Schema [public]: public

Tables (comma-separated, or 'all') [all]: customers,orders,products

Incremental sync?
  1. Full refresh (reload all data each sync)
  2. Incremental (sync only new/updated rows)
Choice [2]: 2

  Cursor column (e.g., updated_at): updated_at
  Initial value (YYYY-MM-DD) [2024-01-01]: 2024-01-01

Testing connection...
✓ Connected to PostgreSQL
✓ Database 'analytics' accessible
✓ Schema 'public' found
✓ Found 3 tables: customers, orders, products
✓ Cursor column 'updated_at' exists

Store credentials in:
  1. Environment variable (recommended)
  2. .dlt/secrets.toml
Choice [1]: 1

Environment variable name: POSTGRES_CREDENTIALS

✓ Source added

Next steps:
  Add to .env:
    POSTGRES_CREDENTIALS="postgresql://readonly_user:PASSWORD@db.acme.com:5432/analytics"

  Then sync:
    dango sync --source production_db
```

### Database Configuration

**Environment variable**:

```bash
# .env
POSTGRES_CREDENTIALS="postgresql://user:pass@host:5432/db"
MYSQL_CREDENTIALS="mysql://user:pass@host:3306/db"
SNOWFLAKE_CREDENTIALS="snowflake://user:pass@account/db/schema"
```

**Or dlt secrets**:

```toml
# .dlt/secrets.toml
[sources.sql_database]
credentials = "postgresql://user:pass@host:5432/db"

[sources.mysql_database]
credentials = "mysql://user:pass@host:3306/db"
```

**Source configuration**:

```yaml
# .dango/sources.yml
sources:
  - name: production_db
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: sql_database
      source_function: sql_database
      function_kwargs:
        credentials: "${POSTGRES_CREDENTIALS}"
        schema: "public"
        tables:
          - customers
          - orders
          - products
        incremental:
          cursor_column: "updated_at"
          initial_value: "2024-01-01"
```

!!! note "No Import/Export Commands"
    Dango does not have `source export` or `source import` commands. To share or backup source configurations:

    **Manual Export/Import**:

    1. Copy `.dango/sources.yml` to share source configurations
    2. Copy `.dlt/secrets.toml` separately (contains credentials - **never commit to Git**)
    3. On destination machine, place files in the same locations

    **Example**:
    ```bash
    # Backup source configurations
    cp .dango/sources.yml ~/backups/sources.yml

    # Restore source configurations
    cp ~/backups/sources.yml .dango/sources.yml

    # Validate after restore
    dango validate
    ```

---

## Best Practices

### 1. Use Environment Variables for Credentials

**Good**:

```yaml
# .dango/sources.yml
sources:
  - name: stripe_payments
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY

# .env (gitignored)
STRIPE_API_KEY=sk_live_abc123...
```

**Avoid**:

```yaml
# .dango/sources.yml (committed to git)
sources:
  - name: stripe_payments
    stripe:
      stripe_secret_key: sk_live_abc123...  # ✗ Credential in git!
```

### 2. Use Descriptive Names

**Good**:

```
stripe_production_payments
marketing_facebook_ads_2024
finance_google_sheets_budget
crm_postgres_customers
```

**Avoid**:

```
source1
data
my_source
stripe
```

### 3. Document Sources

```yaml
sources:
  - name: crm_export
    description: |
      Weekly CRM export from sales team.
      Updated every Monday at 9am.
      Contact: sales@acme.com for issues.
    type: csv
    csv:
      file_path: data/crm/weekly_export.csv
```

### 4. Test Before Committing

```bash
# Add source
dango source add stripe

# Test connection
dango sync --source stripe_payments --dry-run

# Sync small sample
dango sync --source stripe_payments --start-date 2024-12-01

# Verify data
duckdb data/warehouse.duckdb "SELECT * FROM raw_stripe.charges LIMIT 10"

# Commit when working
git add .dango/sources.yml
git commit -m "Add Stripe payments source"
```

### 5. Version Control Source Configuration

```bash
# Track source configuration
git add .dango/sources.yml

# Don't track credentials
git status .env
# .env should be in .gitignore

# Commit
git commit -m "Add production database source"
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-sync: **Sync & Run**

    ---

    Learn how to sync sources and run transformations.

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-check-circle-outline: **Validation**

    ---

    Validate source configuration and troubleshoot.

    [:octicons-arrow-right-24: Validation Guide](validation.md)

-   :material-database-outline: **Data Sources**

    ---

    Deep dive into specific source types.

    [:octicons-arrow-right-24: Data Sources](../data-sources/index.md)

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete CLI command reference.

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

</div>
