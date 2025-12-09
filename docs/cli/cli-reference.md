# CLI Reference

Complete command reference for all dango commands.

---

## Overview

The Dango CLI provides a comprehensive set of commands for managing your data platform. This reference covers every command, option, and flag available.

**Command Categories**:

- [Project Management](#project-management) - init, info, status, validate, rename
- [Data Operations](#data-operations) - sync, generate, run
- [Source Management](#source-management) - source add/list/remove
- [Platform Control](#platform-control) - start, stop
- [Database](#database-operations) - db status, db clean
- [Authentication](#authentication) - auth list/refresh/status/check/setup
- [Metabase](#metabase-operations) - metabase save/load/refresh
- [Dashboard](#dashboard-operations) - dashboard provision
- [Documentation](#documentation) - docs
- [Configuration](#configuration) - config validate/show

---

## Global Options

Available for all commands:

```bash
dango [COMMAND] [OPTIONS]
```

### Common Flags

| Flag | Description |
|------|-------------|
| `--help`, `-h` | Show help message and exit |
| `--version`, `-v` | Show Dango version |
| `--verbose` | Enable verbose output |
| `--quiet`, `-q` | Suppress non-error output |
| `--no-color` | Disable colored output |
| `--project-dir PATH` | Run command in specific project directory |

**Examples**:

```bash
# Show help for any command
dango sync --help

# Check version
dango --version
# Output: dango version 0.0.5

# Verbose output
dango sync --verbose

# Quiet mode (errors only)
dango sync --quiet

# Run in different project
dango --project-dir ~/other-project status
```

---

## Project Management

### dango init

Initialize a new Dango project.

**Syntax**:

```bash
dango init [PROJECT_NAME] [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `PROJECT_NAME` | No | Name for the project directory (defaults to current directory) |

**Options**:

| Option | Description |
|--------|-------------|
| `--skip-wizard` | Skip interactive setup wizard |
| `--force`, `-f` | Overwrite existing project |

**Examples**:

```bash
# Interactive initialization
dango init my-analytics

# Blank project (no wizard)
dango init . --skip-wizard

# Force reinitialize
dango init my-project --force
```

**What it creates**:

```
my-analytics/
├── .dango/
│   ├── project.yml
│   └── sources.yml
├── .dlt/
│   ├── config.toml
│   └── secrets.toml
├── data/
│   └── .gitkeep
├── dbt/
│   ├── dbt_project.yml
│   ├── models/
│   └── tests/
├── custom_sources/
│   └── __init__.py
├── docker-compose.yml
├── .gitignore
└── .env.example
```

---

### dango info

Display project metadata and configuration.

**Syntax**:

```bash
dango info [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--json` | Output in JSON format |
| `--yaml` | Output in YAML format |

**Examples**:

```bash
# Human-readable output
dango info

# JSON format
dango info --json

# YAML format
dango info --yaml
```

**Output**:

```
Project: my-analytics
Organization: Acme Corp
Created: 2024-11-15 by alice@acme.com
Dango Version: 0.0.5

Purpose:
  Track customer behavior and revenue metrics

Stakeholders:
  - Bob Chen (CEO) - bob@acme.com
  - Sarah Lee (Analyst) - sarah@acme.com

Data SLA:
  Daily updates by 9am UTC

Known Limitations:
  - Stripe data has 24h delay
  - Google Sheets updated manually

Configuration:
  Database: data/warehouse.duckdb (42.3 MB)
  dbt Project: dbt/
  Port: 8800
  Auto-sync: Enabled (600s debounce)
```

---

### dango status

Check platform and service status.

**Syntax**:

```bash
dango status [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--json` | Output in JSON format |
| `--check` | Exit with error code if not running |

**Examples**:

```bash
# Check status
dango status

# JSON output
dango status --json

# Exit code check (for scripts)
dango status --check && echo "Running" || echo "Stopped"
```

**Output**:

```
Project: my-analytics (Port: 8800)
Status: ● Running

Services:
  FastAPI Web UI     ● Running (http://localhost:8800)
  File Watcher       ● Running (auto-sync enabled)
  Metabase          ● Running (http://localhost:3000)
  dbt-docs          ○ Stopped

Database: data/warehouse.duckdb (42.3 MB)
Sources: 5 configured (4 enabled)
Last activity: 2 minutes ago
```

**Exit codes**:

- `0` - Platform running
- `1` - Platform stopped or error

---

### dango validate

Validate project configuration and health.

**Syntax**:

```bash
dango validate [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--fix` | Attempt to auto-fix issues |
| `--strict` | Fail on warnings (not just errors) |
| `--check TYPE` | Run specific check: config, sources, database, deps |

**Examples**:

```bash
# Validate everything
dango validate

# Auto-fix issues
dango validate --fix

# Strict mode
dango validate --strict

# Validate sources only
dango validate --check sources
```

**Output**:

```
Validating project configuration...

✓ Project configuration (.dango/project.yml)
✓ Sources configuration (.dango/sources.yml)
✓ dbt project (dbt/dbt_project.yml)
✓ DuckDB database accessible
✗ Docker not running (Metabase won't start)
⚠ OAuth token expires in 6 days (google_sheets)

Validation complete: 1 error, 1 warning

Errors:
  1. Docker daemon not running
     → Start Docker: docker start
     → Or disable Metabase in docker-compose.yml

Warnings:
  1. OAuth credentials expire soon
     → Run: dango auth refresh google_sheets
```

**Exit codes**:

- `0` - No errors (warnings OK unless --strict)
- `1` - Validation errors found

---

### dango rename

Rename project.

**Syntax**:

```bash
dango rename NEW_NAME [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `NEW_NAME` | Yes | New project name |

**Options**:

| Option | Description |
|--------|-------------|
| `--force`, `-f` | Skip confirmation prompt |

**Examples**:

```bash
# Rename project
dango rename new-analytics

# Force rename
dango rename new-analytics --force
```

**What it updates**:

- `.dango/project.yml` → `project.name`
- `.dango/routing.json` → Domain mappings
- Docker container labels
- dbt project name

---

## Data Operations

### dango sync

Sync data from configured sources.

**Syntax**:

```bash
dango sync [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--source NAME` | Sync specific source only |
| `--full-refresh` | Drop and reload all data |
| `--dry-run` | Preview without syncing |
| `--start-date DATE` | Override incremental start date (YYYY-MM-DD) |
| `--workers N` | Number of parallel workers (default: 4) |
| `--select TABLE` | Sync specific table/resource only |

**Examples**:

```bash
# Sync all enabled sources
dango sync

# Sync specific source
dango sync --source stripe_payments

# Full refresh
dango sync --full-refresh

# Dry run
dango sync --dry-run

# Override start date
dango sync --source stripe_payments --start-date 2024-01-01

# Parallel workers
dango sync --workers 8

# Specific table only
dango sync --source stripe_payments --select charges
```

**Output**:

```
[12:34:56] Starting sync for stripe_payments
[12:34:57] Connecting to Stripe API
[12:34:58] Fetching charges (incremental from 2024-11-01)
[12:35:12] Loaded 1,523 charges
[12:35:13] Fetching customers (full refresh)
[12:35:20] Loaded 342 customers
[12:35:21] Writing to raw_stripe.charges
[12:35:24] Writing to raw_stripe.customers
[12:35:25] ✓ Sync complete (1,865 rows in 29.2s)
```

**Exit codes**:

- `0` - Sync successful
- `1` - Sync failed

---

### dango generate

Auto-generate dbt staging models from raw tables.

**Syntax**:

```bash
dango generate [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--source NAME` | Generate for specific source only |
| `--models LAYER` | Generate specific layer: staging, all |
| `--force`, `-f` | Overwrite existing models |
| `--dedup-strategy STRATEGY` | Deduplication: latest_only, scd_type2, none |

**Examples**:

```bash
# Generate all staging models
dango generate

# Generate for specific source
dango generate --source stripe_payments

# Force overwrite
dango generate --force

# Custom dedup strategy
dango generate --dedup-strategy scd_type2
```

**Output**:

```
Generating staging models...
Introspecting raw_stripe.* tables...

✓ Generated stg_stripe_charges.sql (12 columns)
✓ Generated stg_stripe_customers.sql (8 columns)
✓ Generated stg_stripe_subscriptions.sql (15 columns)
✓ Generated _stg_stripe__sources.yml
✓ Generated _stg_stripe__schema.yml

3 models created in dbt/models/staging/
Run 'dango run' to materialize.
```

**Exit codes**:

- `0` - Generation successful
- `1` - Generation failed

---

### dango run

Run dbt transformations.

**Syntax**:

```bash
dango run [OPTIONS] [DBT_ARGS...]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--select MODEL` | Run specific model(s) |
| `--exclude MODEL` | Exclude model(s) |
| `--full-refresh` | Full rebuild of incremental models |
| `--threads N` | Number of threads (default: 4) |

**Additional dbt arguments**:

Any dbt run argument can be passed through:

- `--vars` - Set dbt variables
- `--target` - Use specific target
- `--models` - Alternative to --select
- `--fail-fast` - Stop on first error

**Examples**:

```bash
# Run all models
dango run

# Run specific model
dango run --select customer_metrics

# Run model and downstream
dango run --select customer_metrics+

# Run model and upstream
dango run --select +customer_metrics

# Run all marts
dango run --select marts.*

# Full refresh
dango run --full-refresh

# Set variables
dango run --vars '{"year": 2024}'

# Custom threads
dango run --threads 8

# Fail fast
dango run --fail-fast
```

**Output**:

```
Running dbt...
12:45:01  Running with dbt=1.7.4
12:45:02  Found 15 models, 8 tests, 0 snapshots
12:45:03  Concurrency: 4 threads
12:45:04
12:45:04  1 of 15 START sql view model staging.stg_stripe_charges ........ [RUN]
12:45:05  1 of 15 OK created sql view model staging.stg_stripe_charges ... [SUCCESS in 0.8s]
12:45:05  2 of 15 START sql table model marts.customer_metrics ........... [RUN]
12:45:07  2 of 15 OK created sql table model marts.customer_metrics ...... [SUCCESS in 2.1s]
...
12:45:15  Finished running 15 models in 12.3s.
12:45:15
12:45:15  Completed successfully
```

**Exit codes**:

- `0` - All models successful
- `1` - One or more models failed

---

## Source Management

### dango source add

Add a new data source interactively.

**Syntax**:

```bash
dango source add [SOURCE_TYPE] [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `SOURCE_TYPE` | No | Source type (launches wizard if omitted) |

**Options**:

| Option | Description |
|--------|-------------|
| `--name NAME` | Source name |
| `--config FILE` | Load config from YAML file |
| `--skip-test` | Skip connection test |

**Examples**:

```bash
# Interactive wizard
dango source add

# Specify source type
dango source add stripe

# Non-interactive with config file
dango source add --config stripe-config.yml

# Skip connection test
dango source add --skip-test
```

**Interactive flow**:

```
Select source type:
  1. CSV files
  2. Stripe
  3. Google Sheets
  ...
  30. Custom (dlt_native)

Choice: 2

Source name: stripe_payments
Stripe API Key (env var name): STRIPE_API_KEY
Start date (YYYY-MM-DD): 2024-01-01

Testing connection...
✓ Connection successful
✓ API key valid
✓ Fetched sample data

Save source? (Y/n): y

✓ Source added to .dango/sources.yml
Run 'dango sync --source stripe_payments' to load data.
```

---

### dango source list

List all configured sources.

**Syntax**:

```bash
dango source list [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--enabled` | Show only enabled sources |
| `--disabled` | Show only disabled sources |
| `--json` | Output in JSON format |
| `--verbose`, `-v` | Show detailed configuration |

**Examples**:

```bash
# List all sources
dango source list

# Enabled sources only
dango source list --enabled

# Disabled sources only
dango source list --disabled

# JSON output
dango source list --json

# Detailed info
dango source list --verbose
```

**Output**:

```
Configured Sources:

  ● stripe_payments (stripe) - Enabled
      Last synced: 2024-12-01 12:34:56
      Rows: 1,865
      Tables: charges, customers, subscriptions

  ● orders_csv (csv) - Enabled
      Last synced: 2024-12-01 08:15:23
      Rows: 5,432
      File: data/orders.csv

  ○ old_hubspot (hubspot) - Disabled
      Never synced
      Reason: Deprecated source
```

---

### dango source remove

Remove a source from configuration.

**Syntax**:

```bash
dango source remove SOURCE_NAME [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `SOURCE_NAME` | Yes | Name of source to remove |

**Options**:

| Option | Description |
|--------|-------------|
| `--force`, `-f` | Skip confirmation prompt |
| `--delete-data` | Also delete data from database |

**Examples**:

```bash
# Remove source (with confirmation)
dango source remove old_hubspot

# Force remove
dango source remove old_hubspot --force

# Remove and delete data
dango source remove old_hubspot --delete-data
```

**Output**:

```
Remove 'old_hubspot' source?
This will:
  - Remove from .dango/sources.yml
  - Keep data in database (use --delete-data to remove)

Proceed? (y/N): y

✓ Source removed from configuration
Data remains in raw_old_hubspot schema
Run 'dango db clean' to remove orphaned data
```

---

## Platform Control

### dango start

Start the Dango platform and all services.

**Syntax**:

```bash
dango start
```

!!! note "No Options Available"
    The `start` command has no command-line options. All configuration is done via `.dango/project.yml`.

**Example**:

```bash
# Start all services (Web UI, Metabase, dbt docs)
dango start
```

**Configuration** (via `.dango/project.yml`):

```yaml
platform:
  web_ui:
    port: 8800  # Configure Web UI port here
  auto_sync: true  # Enable file watcher
```

**Output**:

```
Starting Dango platform...
✓ FastAPI Web UI started (http://localhost:8800)
✓ File Watcher started (auto-sync enabled)
✓ Metabase starting... (this may take 30s)
✓ Metabase started (http://localhost:3000)
✓ dbt-docs started (http://localhost:8081)

Platform running. Press Ctrl+C to stop.
Open http://localhost:8800 in your browser.
```

---

### dango stop

Stop the Dango platform and all services.

**Syntax**:

```bash
dango stop [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--all` | Stop all Dango projects on machine |
| `--force`, `-f` | Force kill processes |

**Examples**:

```bash
# Stop current project
dango stop

# Stop all Dango projects
dango stop --all

# Force stop
dango stop --force
```

**Output**:

```
Stopping Dango platform...
✓ File Watcher stopped
✓ FastAPI Web UI stopped
✓ Metabase stopped
✓ dbt-docs stopped

Platform stopped.
```

!!! note "Restarting the Platform"
    There is no `dango restart` command. To restart the platform:

    ```bash
    dango stop && dango start
    ```

---

## Database Operations

### dango db status

Show database status and statistics.

**Syntax**:

```bash
dango db status [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--detailed` | Show table-level details |
| `--json` | Output in JSON format |

**Examples**:

```bash
# Database summary
dango db status

# Detailed table info
dango db status --detailed

# JSON output
dango db status --json
```

**Output**:

```
Database: data/warehouse.duckdb (42.3 MB)

Schemas:
  raw                3 tables, 12,435 rows
  raw_stripe         5 tables, 8,921 rows
  staging           8 views
  intermediate      3 tables, 5,234 rows
  marts             4 tables, 2,103 rows

Total: 23 objects, 28,693 rows
Disk usage: 42.3 MB
Available space: 245 GB
Last vacuum: 2024-12-08 10:30:15
```

---

### dango db clean

Remove orphaned tables from disabled sources.

**Syntax**:

```bash
dango db clean [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview without deleting |
| `--force`, `-f` | Skip confirmation |
| `--source NAME` | Clean specific source only |

**Examples**:

```bash
# Interactive clean
dango db clean

# Dry run
dango db clean --dry-run

# Force clean
dango db clean --force

# Clean specific source
dango db clean --source old_hubspot
```

**Output**:

```
Found orphaned tables:
  - raw_old_hubspot.contacts (1,234 rows, 0.5 MB)
  - raw_old_hubspot.companies (567 rows, 0.2 MB)

These sources are no longer in .dango/sources.yml.

Drop these tables? (y/N): y

✓ Dropped raw_old_hubspot.contacts
✓ Dropped raw_old_hubspot.companies

Cleaned 1,801 rows (0.7 MB freed).
```

---

## Authentication

### dango auth list

List stored OAuth credentials.

**Syntax**:

```bash
dango auth list [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--expired` | Show only expired credentials |
| `--expiring DAYS` | Show credentials expiring within N days |
| `--json` | Output in JSON format |

**Examples**:

```bash
# List all credentials
dango auth list

# Show expired only
dango auth list --expired

# Expiring within 7 days
dango auth list --expiring 7
```

**Output**:

```
OAuth Credentials:

  ✓ google_sheets_source
      Provider: Google OAuth
      Scopes: spreadsheets.readonly
      Expires: 2024-12-15 (6 days)

  ✗ facebook_ads_source
      Provider: Facebook OAuth
      Expires: 2024-11-20 (EXPIRED 19 days ago)

  ✓ google_analytics_source
      Provider: Google OAuth
      Expires: 2024-12-08 (7 days)
```

---

### dango auth refresh

Re-authenticate OAuth source.

**Syntax**:

```bash
dango auth refresh SOURCE_NAME [OPTIONS]
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `SOURCE_NAME` | Yes | Name of OAuth source |

**Options**:

| Option | Description |
|--------|-------------|
| `--no-browser` | Don't auto-open browser |

**Examples**:

```bash
# Refresh credentials
dango auth refresh facebook_ads_source

# Manual browser
dango auth refresh google_sheets --no-browser
```

**Output**:

```
Opening browser for Facebook OAuth...
✓ Browser opened at: https://www.facebook.com/...

Waiting for authorization...
✓ Authorization successful
✓ Credentials refreshed

New expiry: 2025-01-15 (60 days)
```

---

### dango auth status

Show OAuth credential expiration status.

**Syntax**:

```bash
dango auth status [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--source NAME` | Check specific source |

**Examples**:

```bash
# Check all sources
dango auth status

# Specific source
dango auth status --source google_sheets
```

**Output**:

```
OAuth Status:

Expired:
  - facebook_ads_source (expired 19 days ago)

Expiring soon (< 7 days):
  - google_sheets_source (expires in 6 days)
  - google_analytics_source (expires in 7 days)

Healthy:
  - stripe_oauth_source (expires in 45 days)

Run 'dango auth refresh <source>' to re-authenticate.
```

---

### dango auth check

Validate OAuth configuration and credential status.

**Syntax**:

```bash
dango auth check
```

**What it validates**:

1. **OAuth Client Credentials** (.env file):
   - Google: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
   - Facebook: `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET`

2. **Saved OAuth Tokens** (.dlt/secrets.toml):
   - Token presence and validity
   - Expiration status (expired, expiring soon, active)

3. **Summary**:
   - Overall configuration state
   - Recommended next steps

**Example**:

```bash
dango auth check
```

**Output**:

```
OAuth Configuration Check

1. OAuth Client Credentials (.env)
  ✓ Google
    ✓ GOOGLE_CLIENT_ID: 1234...5678.apps.googleusercontent.com
    ✓ GOOGLE_CLIENT_SECRET: ********
    → Ready to authenticate

  ✗ Facebook
    ✗ FACEBOOK_APP_ID: Missing
    ✗ FACEBOOK_APP_SECRET: Missing
    → Run: dango auth setup facebook

2. Saved OAuth Tokens (.dlt/secrets.toml)
  ✓ my_sheets (user@example.com)
    Provider: google_sheets | Source: my_sheets
    Active

  ⚠ my_analytics (user@example.com)
    Provider: google_analytics | Source: my_analytics
    Expires in 5d
    → Run: dango auth refresh my_analytics

3. Summary
  Google credentials configured and authenticated.
  Facebook credentials missing.
  → Run: dango auth setup facebook
```

**Status indicators**:

| Symbol | Meaning |
|--------|---------|
| `✓` (green) | Configured/Active |
| `✗` (red) | Missing/Expired |
| `⚠` (yellow) | Warning (expiring soon) |

---

### dango auth setup

Interactive OAuth setup wizard for creating provider credentials.

**Syntax**:

```bash
dango auth setup PROVIDER
```

**Arguments**:

| Argument | Required | Description |
|----------|----------|-------------|
| `PROVIDER` | Yes | OAuth provider: `google` or `facebook` |

**Supported Providers**:

| Provider | Services | Required Credentials |
|----------|----------|---------------------|
| `google` | Google Sheets, GA4, Google Ads | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| `facebook` | Facebook Ads | `FACEBOOK_APP_ID`, `FACEBOOK_APP_SECRET` |

**Examples**:

```bash
# Setup Google OAuth
dango auth setup google

# Setup Facebook OAuth
dango auth setup facebook
```

**Interactive flow**:

```
OAuth Setup: Google

Why create your own OAuth app?
────────────────────────────────
Your data flows directly from Google → Your machine → Local database.
Dango never touches your data. You control access and can revoke anytime.

Current Configuration
────────────────────────────────
GOOGLE_CLIENT_ID: Not configured
GOOGLE_CLIENT_SECRET: Not configured

Setup Steps
────────────────────────────────
1. Go to Google Cloud Console → APIs & Services → Credentials
   https://console.cloud.google.com/apis/credentials

2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'

3. Application type: 'Web application'
   Name: 'Dango Local'

4. Authorized redirect URIs:
   Add: http://localhost:8080/callback

5. Click 'Create' and copy credentials

Enter Google Client ID: [paste here]
Enter Google Client Secret: [paste here]

✓ Credentials saved to .env

Next steps:
  dango auth google_sheets   # Authenticate Google Sheets
  dango auth google_analytics # Authenticate GA4
  dango auth google_ads      # Authenticate Google Ads
```

**After setup**:

```bash
# Authenticate with the provider
dango auth google_sheets
dango auth google_analytics
dango auth facebook_ads

# Then add a source
dango source add
```

---

## Metabase Operations

### dango metabase save

Save Metabase dashboards and questions to JSON files.

**Syntax**:

```bash
dango metabase save [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--output DIR` | Output directory (default: `.dango/metabase/`) |

**Example**:

```bash
dango metabase save
```

---

### dango metabase load

Load Metabase dashboards and questions from JSON files.

**Syntax**:

```bash
dango metabase load [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--input DIR` | Input directory (default: `.dango/metabase/`) |

**Example**:

```bash
dango metabase load
```

---

### dango metabase refresh

Refresh Metabase database connection to discover new schemas.

**Syntax**:

```bash
dango metabase refresh
```

**When to use**:

- After creating new marts (analytics models)
- When new schemas are added to the warehouse
- After dbt transformations that create new tables
- When Metabase doesn't show recently created tables

**Prerequisites**:

- Metabase must be running (`dango start`)
- Metabase must be configured (`.dango/metabase.yml` exists)

**Example**:

```bash
dango metabase refresh
```

**Output**:

```
Step 1: Logging in to Metabase...
✓ Logged in successfully

Step 2: Removing old database connection...
✓ Old connection removed

Step 3: Creating new database connection...
✓ New connection created

Step 4: Updating configuration...
✓ Configuration updated

Step 5: Waiting for schema sync...
✓ Schema sync complete

Discovered schemas: raw, raw_stripe, staging, marts
Total tables: 15

  raw: csv_uploads
  raw_stripe: charges, customers, subscriptions
  staging: stg_stripe_charges, stg_stripe_customers, ...
  marts: customer_metrics, revenue_by_month

✨ Metabase connection refreshed successfully!
```

**Troubleshooting**:

| Error | Solution |
|-------|----------|
| "Metabase is not running" | Run `dango start` first |
| "Metabase not configured" | Run `dango start` to initialize Metabase |
| "Cannot connect to Metabase" | Check Docker is running, try `dango stop && dango start` |

---

## Dashboard Operations

### dango dashboard provision

Provision pre-built dashboards in Metabase.

**Syntax**:

```bash
dango dashboard provision [OPTIONS]
```

**Options**:

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | `http://localhost:3001` | Metabase URL |
| `--username` | `admin@example.com` | Metabase admin username |
| `--password` | (prompted) | Metabase admin password |

!!! warning "Port Mismatch"
    The CLI defaults to port 3001, but Metabase runs on port 3000 by default.
    Always specify `--url http://localhost:3000` when using this command.

!!! note "Use Auto-Created Credentials"
    If Metabase was auto-configured by `dango start`, use the auto-created credentials:

    - **Email**: `admin@dango.local`
    - **Password**: `dangolocal123`

**Example**:

```bash
# With auto-created Metabase credentials (correct port and username)
dango dashboard provision --url http://localhost:3000 --username admin@dango.local
```

**What it creates**:

- Data Pipeline Health dashboard with:
  - Source sync status overview
  - Recent sync failures
  - Data freshness metrics
  - Row count trends

---

## Documentation

### dango docs

Generate and serve dbt documentation.

**Syntax**:

```bash
dango docs [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--port PORT` | Custom port (default: 8081) |
| `--no-serve` | Generate only, don't serve |
| `--open`, `-o` | Auto-open browser |

**Examples**:

```bash
# Generate and serve
dango docs

# Custom port
dango docs --port 8082

# Generate only
dango docs --no-serve

# Auto-open browser
dango docs --open
```

**Output**:

```
Generating dbt documentation...
12:50:01  Running with dbt=1.7.4
12:50:02  Building catalog
12:50:05  Catalog written to target/catalog.json
12:50:05  Building docs
12:50:06  Docs written to target/index.html

Starting documentation server...
✓ dbt-docs running at http://localhost:8081

Press Ctrl+C to stop.
```

---

## Configuration

### dango config validate

Validate all configuration files.

**Syntax**:

```bash
dango config validate [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--fix` | Auto-fix issues |
| `--file FILE` | Validate specific file |

**Examples**:

```bash
# Validate all config
dango config validate

# Auto-fix
dango config validate --fix

# Specific file
dango config validate --file .dango/sources.yml
```

**Output**:

```
Validating configuration...

✓ .dango/project.yml - OK
✓ .dango/sources.yml - OK
✓ dbt/dbt_project.yml - OK
✗ .dlt/secrets.toml - Missing STRIPE_API_KEY

1 issue found.
Add STRIPE_API_KEY to .env or .dlt/secrets.toml.
```

---

### dango config show

Display current configuration.

**Syntax**:

```bash
dango config show [OPTIONS]
```

**Options**:

| Option | Description |
|--------|-------------|
| `--format FORMAT` | Output format: yaml, json, toml |
| `--section SECTION` | Show specific section: project, platform, sources |

**Examples**:

```bash
# Show all config
dango config show

# JSON format
dango config show --format json

# Show project section only
dango config show --section project
```

---

## Exit Codes

All commands follow standard exit code conventions:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (validation failed, command failed) |
| `2` | Invalid usage (wrong arguments) |
| `130` | Interrupted (Ctrl+C) |

**Use in scripts**:

```bash
#!/bin/bash
dango validate
if [ $? -eq 0 ]; then
  dango sync
  dango run
else
  echo "Validation failed"
  exit 1
fi
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch: **Init & Start**

    ---

    Learn project initialization and starting services.

    [:octicons-arrow-right-24: Init & Start Guide](init-start.md)

-   :material-sync: **Sync & Run**

    ---

    Master data syncing and running transformations.

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-database-outline: **Source Management**

    ---

    CLI commands for managing data sources.

    [:octicons-arrow-right-24: Source Management](source-management.md)

-   :material-check-circle-outline: **Validation**

    ---

    Validate configuration and troubleshoot issues.

    [:octicons-arrow-right-24: Validation Guide](validation.md)

</div>
