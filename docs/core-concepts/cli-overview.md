# CLI Overview

Master the Dango command-line interface.

---

## Command Categories

Dango CLI commands are organized into logical groups:

| Category | Commands | Purpose |
|----------|----------|---------|
| **Project** | `init`, `info`, `status`, `validate`, `rename` | Project lifecycle |
| **Data** | `sync`, `source`, `run` | Data ingestion & transformation |
| **Platform** | `start`, `stop`, `restart` | Service management |
| **Database** | `db status`, `db clean` | Database operations |
| **Auth** | `auth list`, `auth refresh`, `auth <provider>` | OAuth management |
| **Configuration** | `config validate`, `config show` | Config management |
| **Documentation** | `docs` | Generate dbt documentation |

---

## Project Lifecycle

### `dango init`

Initialize a new Dango project.

**Usage**:
```bash
# Interactive wizard (recommended)
dango init my-project

# Skip wizard (blank project)
dango init . --skip-wizard

# Reinitialize existing project
dango init my-project --force
```

**What it creates**:
```
my-project/
├── .dango/
│   ├── project.yml
│   └── sources.yml
├── data/
├── dbt/
├── custom_sources/
├── docker-compose.yml
└── .gitignore
```

**Interactive prompts**:
```
What's your project name? my-analytics
Who are you? alice@acme.com
What's the purpose of this project? Track customer behavior
Would you like to add a stakeholder? (Y/n)
```

---

### `dango info`

Display project metadata and configuration.

**Usage**:
```bash
dango info
```

**Output**:
```
Project: my-analytics
Organization: Acme Corp
Created: 2024-11-15 by alice@acme.com
Purpose: Track customer behavior

Stakeholders:
  - Bob Chen (CEO) - bob@acme.com
  - Sarah Lee (Analyst) - sarah@acme.com

SLA: Daily by 9am UTC
Limitations: Stripe data has 24h delay

Database: data/warehouse.duckdb (42.3 MB)
dbt Project: dbt/
```

---

### `dango status`

Check if platform services are running.

**Usage**:
```bash
dango status
```

**Output**:
```
Project: my-analytics (Port: 8800)
Status: ● Running

Services:
  FastAPI Web UI     ● Running (http://localhost:8800)
  File Watcher       ● Running (auto-sync enabled)
  Metabase          ● Running (http://localhost:3000)
  dbt-docs          ● Running (http://localhost:8081)

Database: data/warehouse.duckdb (42.3 MB)
```

---

### `dango validate`

Verify project configuration and directory structure.

**Usage**:
```bash
dango validate
```

**What it checks**:
- `.dango/project.yml` is valid YAML
- `.dango/sources.yml` has correct schema
- `dbt/` directory exists
- `data/` directory exists
- DuckDB database is accessible
- Docker is installed (for Metabase)

**Output**:
```
✓ Project configuration valid
✓ Sources configuration valid
✓ dbt project configured
✓ DuckDB database accessible
✗ Docker not running (Metabase won't start)

1 issue found. Run 'docker start' to resolve.
```

---

### `dango rename`

Rename project and update domain routing.

**Usage**:
```bash
dango rename new-project-name
```

Updates:
- `.dango/project.yml` → `project.name`
- `.dango/routing.json` → domain mappings
- Docker container labels

---

## Data Ingestion

### `dango sync`

Sync data from configured sources using dlt.

**Usage**:
```bash
# Sync all enabled sources
dango sync

# Sync specific source only
dango sync --source stripe_payments

# Full refresh (drop and reload)
dango sync --full-refresh

# Preview what would be synced (no changes)
dango sync --dry-run

# Override incremental start date
dango sync --start-date 2024-01-01
```

**Example**:
```bash
$ dango sync --source stripe_payments

[12:34:56] Starting sync for stripe_payments
[12:34:57] Connecting to Stripe API
[12:34:58] Fetching charges (incremental from 2024-11-01)
[12:35:12] Loaded 1,523 charges
[12:35:13] Fetching customers (full refresh)
[12:35:20] Loaded 342 customers
[12:35:21] Writing to raw_stripe_payments.charges
[12:35:24] Writing to raw_stripe_payments.customers
[12:35:25] Generating staging models...
[12:35:26] ✓ Sync complete (1,865 rows in 30.1s)
```

Note: `dango sync` automatically generates staging models for the synced source.

**WebSocket real-time logs**:

Open `http://localhost:8800` during sync to see live progress in the Web UI.

---

### `dango source`

Manage data sources.

#### `dango source add`

Add a new data source interactively.

**Usage**:
```bash
dango source add
```

**Interactive wizard**:
```
Select source type:
  1. CSV files
  2. Stripe
  3. Google Sheets
  4. Google Analytics (GA4)
  5. HubSpot
  6. Salesforce
  ...
  30. REST API
  31. Custom (dlt_native)

Choice: 2

Source name: stripe_payments
Stripe API Key (env var name): STRIPE_API_KEY
Start date (YYYY-MM-DD): 2024-01-01

✓ Source added to .dango/sources.yml
Run 'dango sync --source stripe_payments' to load data.
```

#### `dango source list`

List all configured sources.

**Usage**:
```bash
dango source list
```

**Output**:
```
Configured Sources:

  ● stripe_payments (stripe) - Enabled
      Last synced: 2024-12-01 12:34:56
      Rows: 1,865

  ● orders_csv (csv) - Enabled
      Last synced: 2024-12-01 08:15:23
      Rows: 5,432

  ○ old_hubspot (hubspot) - Disabled
      Never synced
```

#### `dango source remove`

Remove a source from configuration.

**Usage**:
```bash
dango source remove orders_csv
```

**Confirmation**:
```
Remove 'orders_csv' source?
This will:
  - Remove from .dango/sources.yml
  - Keep data in database (use 'dango db clean' to remove)

Proceed? (y/N): y

✓ Source removed from configuration
```

---

## Transformations

### `dango run`

Run dbt transformations.

**Usage**:
```bash
# Run all models
dango run

# Run specific model
dango run --select customer_metrics

# Run all models in marts/
dango run --select marts.*

# Pass any dbt arguments
dango run --full-refresh --vars '{"year": 2024}'
```

**What it does**:
- Executes `dbt run` in the `dbt/` directory
- Applies transformations defined in `dbt/models/`
- Materializes staging tables, intermediate tables, and marts

**Example**:
```bash
$ dango run --select marts.customer_metrics

Running dbt...
12:45:01  Running with dbt=1.7.0
12:45:02  Found 15 models, 8 tests, 3 snapshots
12:45:03
12:45:03  Concurrency: 4 threads
12:45:03
12:45:04  1 of 1 START sql table model marts.customer_metrics ........... [RUN]
12:45:06  1 of 1 OK created sql table model marts.customer_metrics ...... [SUCCESS in 2.1s]
12:45:06
12:45:06  Finished running 1 table model in 3.2s.
```

---

### `dango docs`

Generate dbt documentation website.

**Usage**:
```bash
dango docs
```

**What it does**:
- Runs `dbt docs generate`
- Creates data lineage graphs
- Documents all models, columns, tests
- Serves docs at `http://localhost:8081`

**Access**: Open `http://localhost:8081` or click "dbt Docs" in Web UI.

---

## Platform Management

### `dango start`

Start all platform services.

**Usage**:
```bash
dango start
```

**What starts**:
1. FastAPI Web UI (port 8800)
2. File Watcher (if `auto_sync: true`)
3. Docker containers:
   - Metabase (port 3000)
   - dbt-docs (port 8081)

**Output**:
```
Starting Dango platform...
✓ FastAPI Web UI started (http://localhost:8800)
✓ File Watcher started (auto-sync enabled)
✓ Metabase started (http://localhost:3000)
✓ dbt-docs started (http://localhost:8081)

Platform running. Press Ctrl+C to stop.
```

**Logs**:
```bash
dango logs
# or
dango logs --follow
```

---

### `dango stop`

Stop all services.

**Usage**:
```bash
# Stop current project
dango stop

# Stop all Dango projects on machine
dango stop --all
```

**Output**:
```
Stopping Dango platform...
✓ File Watcher stopped
✓ FastAPI Web UI stopped
✓ Docker containers stopped

Platform stopped.
```

---

### `dango restart`

Restart platform (equivalent to `stop` + `start`).

**Usage**:
```bash
dango restart
```

---

## Database Operations

### `dango db status`

Show database schema and table summary.

**Usage**:
```bash
dango db status
```

**Output**:
```
Database: data/warehouse.duckdb (42.3 MB)

Schemas:
  raw_orders         3 tables, 12,435 rows
  raw_stripe_payments 5 tables, 8,921 rows
  staging            8 tables
  intermediate       3 tables, 5,234 rows
  marts              4 tables, 2,103 rows

Total: 23 tables, 28,693 rows
```

---

### `dango db clean`

Remove orphaned tables (sources no longer in config).

**Usage**:
```bash
dango db clean
```

**What it does**:
1. Compares database tables to `.dango/sources.yml`
2. Identifies tables for removed sources
3. Prompts for confirmation
4. Drops orphaned tables

**Example**:
```bash
$ dango db clean

Found orphaned tables:
  - raw_old_hubspot.contacts (1,234 rows)
  - raw_old_hubspot.companies (567 rows)

These sources are no longer in .dango/sources.yml.

Drop these tables? (y/N): y

✓ Dropped raw_old_hubspot.contacts
✓ Dropped raw_old_hubspot.companies

Cleaned 1,801 rows (2.1 MB freed).
```

---

## OAuth Authentication

### `dango auth list`

List stored OAuth credentials.

**Usage**:
```bash
dango auth list
```

**Output**:
```
OAuth Credentials:

  ✓ google_sheets_source
      Provider: Google OAuth
      Scopes: https://www.googleapis.com/auth/spreadsheets.readonly
      Expires: 2024-12-15 (14 days)

  ✗ facebook_ads_source
      Provider: Facebook OAuth
      Expires: 2024-11-20 (EXPIRED)

  ✓ google_analytics_source
      Provider: Google OAuth
      Expires: 2024-12-08 (7 days)
```

---

### `dango auth status`

Show expiring or expired credentials.

**Usage**:
```bash
dango auth status
```

**Output**:
```
OAuth Status:

Expired:
  - facebook_ads_source (expired 11 days ago)

Expiring soon (< 7 days):
  - google_analytics_source (expires in 7 days)

Run 'dango auth refresh <source>' to re-authenticate.
```

---

### `dango auth refresh`

Re-authenticate OAuth source.

**Usage**:
```bash
dango auth refresh facebook_ads_source
```

**Flow**:
```
Opening browser for Facebook OAuth...
✓ Browser opened at: https://www.facebook.com/v18.0/dialog/oauth?...

Waiting for authorization...
✓ Authorization successful
✓ Credentials refreshed

New expiry: 2025-01-15 (60 days)
```

---

### `dango auth <provider>`

Authenticate a new OAuth source (interactive).

**Example**:
```bash
dango auth google_sheets
```

**Flow**:
```
Opening browser for Google OAuth...
✓ Browser opened

Please authorize Dango to access:
  - Google Sheets (read-only)

Waiting for callback...
✓ Authorization successful
✓ Credentials stored securely

You can now add Google Sheets sources:
  dango source add
```

---

## Configuration Management

### `dango config validate`

Validate all configuration files.

**Usage**:
```bash
dango config validate
```

**What it checks**:
- `.dango/project.yml` - Valid YAML, required fields
- `.dango/sources.yml` - Valid schema, source types exist
- `dbt/dbt_project.yml` - Valid dbt config
- `.dlt/config.toml` - Valid TOML syntax

**Output**:
```
Validating configuration...

✓ .dango/project.yml - OK
✓ .dango/sources.yml - OK
✓ dbt/dbt_project.yml - OK
✗ .dlt/secrets.toml - Missing STRIPE_API_KEY

1 issue found. Add STRIPE_API_KEY to .env or .dlt/secrets.toml.
```

---

### `dango config show`

Display current configuration.

**Usage**:
```bash
dango config show
```

**Output**:
```yaml
project:
  name: my-analytics
  organization: Acme Corp
  dango_version: 0.0.5

platform:
  port: 8800
  metabase_port: 3000
  dbt_docs_port: 8081
  auto_sync: true
  debounce_seconds: 600

sources:
  - stripe_payments (enabled)
  - orders_csv (enabled)
```

---

## Common Workflows

### Workflow 1: New Project Setup

```bash
# Initialize project
dango init my-analytics
cd my-analytics

# Add a CSV source
dango source add  # Choose CSV

# Sync data (also generates staging models)
dango sync

# Start platform
dango start

# Open Web UI: http://localhost:8800
# Open Metabase: http://localhost:3000
```

---

### Workflow 2: Adding an API Source

```bash
# Add source
dango source add  # Choose Stripe

# Set API key in .env
echo "STRIPE_API_KEY=sk_live_abc123" >> .env

# Test with dry run
dango sync --source stripe_payments --dry-run

# Sync for real (also generates staging models)
dango sync --source stripe_payments

# Run dbt transformations
dango run
```

---

### Workflow 3: Build Custom Metrics

```bash
# Sync raw data (generates staging models automatically)
dango sync

# Create custom model: dbt/models/marts/daily_sales.sql
# (write SQL)

# Run transformation
dango run --select daily_sales

# Generate docs
dango docs

# View in Metabase or dbt-docs
```

---

### Workflow 4: OAuth Source

```bash
# Authenticate with Google
dango auth google_sheets

# Add Google Sheets source
dango source add  # Choose Google Sheets

# Sync
dango sync

# Check credentials status
dango auth list
```

---

## Global Options

Available for all commands:

```bash
# Show help
dango --help
dango sync --help

# Show version
dango --version

# Debug output (via environment variable)
RUNTIME__LOG_LEVEL=DEBUG dango sync
```

---

## Version Control Tips

When using Dango with git, consider these practices:

**Track in version control**:
- `.dango/project.yml` - Project configuration
- `.dango/sources.yml` - Source definitions
- `dbt/` - All transformation logic
- `custom_sources/` - Custom dlt sources

**Do NOT track**:
- `data/` - Database file (add to `.gitignore`)
- `.dlt/secrets.toml` - API keys (add to `.gitignore`)
- `.env` - Environment variables (add to `.gitignore`)

The `dango init` command creates a `.gitignore` file with recommended exclusions.

---

## Next Steps

- **[Project Structure](project-structure.md)** - See where CLI commands operate
- **[Data Sources](../data-sources/index.md)** - Deep dive into `dango source` and `dango sync`
- **[Transformations](../transformations/index.md)** - Learn more about `dango run` and dbt models
