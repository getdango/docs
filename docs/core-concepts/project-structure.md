# Project Structure

Understanding the directory layout and configuration files.

---

## Overview

A Dango project has a standard directory structure created by `dango init`:

```
my-analytics/
├── .dango/                    # Project configuration
├── .dlt/                      # dlt configuration
├── data/                      # Database and uploads
├── dbt/                       # dbt project
├── custom_sources/            # Custom dlt sources
├── dashboards/                # Metabase exports (optional)
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Metabase DuckDB driver
├── .gitignore                 # Git ignore patterns
├── .env                       # Environment variables
└── README.md                  # Auto-generated docs
```

---

## .dango/ - Project Configuration

The `.dango/` directory contains all Dango-specific configuration.

### Directory Contents

```
.dango/
├── project.yml       # Project metadata and platform settings
├── sources.yml       # Data source definitions
├── routing.json      # Multi-project domain routing (auto-generated)
└── metabase.yml      # Metabase credentials (auto-generated)
```

**What to commit**: `project.yml`, `sources.yml`
**What to ignore**: `routing.json`, `metabase.yml`

---

### project.yml

Project metadata and platform configuration.

**Location**: `.dango/project.yml`

**Example**:
```yaml
project:
  name: my-analytics
  organization: Acme Corp
  created: 2024-11-15
  created_by: alice@acme.com
  purpose: Track daily sales and customer behavior
  dango_version: 0.0.5

  stakeholders:
    - name: Bob Chen
      role: CEO - Executive view
      contact: bob@acme.com
    - name: Sarah Lee
      role: Analyst - Power user
      contact: sarah@acme.com

  sla: "Daily by 9am UTC"
  limitations: "Stripe data has 24h delay. GA4 takes 48h to backfill."
  getting_started: |
    1. Run: dango sync
    2. Open: http://localhost:8800

platform:
  port: 8800                     # Web UI port
  metabase_port: 3000           # Metabase BI port
  dbt_docs_port: 8081           # dbt docs port

  auto_sync: true               # Enable file watcher
  auto_dbt: true                # Auto-run dbt after sync
  debounce_seconds: 600         # Wait 10 min before triggering

  watch_patterns:
    - "*.csv"
    - "*.xlsx"
  watch_directories:
    - "data/uploads"

  duckdb_path: "./data/warehouse.duckdb"
  dbt_project_dir: "./dbt"
  data_dir: "./data"
```

**Key sections**:

- **project** - Human-readable metadata
- **stakeholders** - Who uses this project
- **sla** - Data freshness expectations
- **limitations** - Known data delays or gaps
- **platform** - Technical configuration

---

### sources.yml

Data source definitions.

**Location**: `.dango/sources.yml`

**Example**:
```yaml
version: "1.0"
sources:
  # CSV source
  - name: orders
    type: csv
    enabled: true
    csv:
      directory: ./data/uploads
      file_pattern: "orders_*.csv"
      deduplication_strategy: latest_only
      primary_key: order_id
      timestamp_column: created_at
      timestamp_sort: desc

  # Stripe API source
  - name: stripe_payments
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      start_date: 2024-01-01

  # Google Sheets source (OAuth)
  - name: forecast
    type: google_sheets
    enabled: true
    google_sheets:
      spreadsheet_url_or_id: "1a2b3c4d5e6f..."
      range_names: [Sheet1, Q4_Planning]

  # Custom dlt_native source
  - name: internal_api
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: my_custom_source
      source_function: internal_api_source
      function_kwargs:
        api_url: "https://api.internal.com"
        api_key_env: INTERNAL_API_KEY

  # Disabled source
  - name: old_hubspot
    type: hubspot
    enabled: false
```

**Common fields**:

- `name` - Unique identifier (used in table names)
- `type` - Source type (csv, stripe, hubspot, etc.)
- `enabled` - Whether to sync this source
- `<type>` - Type-specific configuration

---

## .dlt/ - dlt Configuration

The `.dlt/` directory contains dlt pipeline configuration.

### Directory Contents

```
.dlt/
├── config.toml       # Pipeline settings (destination, etc.)
└── secrets.toml      # API keys, OAuth tokens (git-ignored)
```

**What to commit**: `config.toml`
**What to ignore**: `secrets.toml`

---

### config.toml

dlt pipeline configuration.

**Location**: `.dlt/config.toml`

**Auto-generated content**:
```toml
[destination.duckdb]
credentials = "./data/warehouse.duckdb"

[runtime]
log_level = "INFO"
```

**You rarely need to edit this** - Dango manages it automatically.

---

### secrets.toml

Sensitive credentials (API keys, OAuth tokens).

**Location**: `.dlt/secrets.toml`

**Example**:
```toml
[sources.stripe]
stripe_secret_key = "sk_live_abc123..."

[sources.google_analytics]
credentials = """
{
  "type": "service_account",
  "project_id": "my-ga-project",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "service@my-ga-project.iam.gserviceaccount.com"
}
"""

[sources.facebook_ads]
access_token = "EAABwzLix..."
account_id = "act_123456789"
```

**Security**:
- **Never commit this file** (included in `.gitignore`)
- Use `.env` or environment variables as alternative
- dlt reads credentials in this priority order:
  1. `.dlt/secrets.toml`
  2. `.env`
  3. Environment variables

---

## data/ - Database and Uploads

The `data/` directory stores the DuckDB database and CSV uploads.

### Directory Contents

```
data/
├── warehouse.duckdb          # Main analytics database
├── warehouse.duckdb.wal      # Write-ahead log (temporary)
├── uploads/                  # Default CSV upload location
│   ├── orders_2024-12-01.csv
│   ├── orders_2024-12-02.csv
│   └── customers.csv
└── warehouse/                # Legacy data location (ignored)
```

**What to commit**: Nothing (all ignored by default)
**What to backup**: `warehouse.duckdb`, `uploads/`

---

### warehouse.duckdb

The DuckDB analytics database file.

**Location**: `data/warehouse.duckdb`

**Size**: Typically 10-500 MB for small projects

**Contents**:
- All raw data ingested by dlt
- Staging models (views)
- Intermediate models (tables)
- Marts models (tables)
- dlt metadata tables

**Direct access**:
```bash
# Open DuckDB CLI
duckdb data/warehouse.duckdb

# Run queries
SELECT * FROM marts.customer_metrics LIMIT 10;
```

**Backup**:
```bash
# Copy database file
cp data/warehouse.duckdb backups/warehouse-2024-12-01.duckdb

# Or export specific tables
duckdb data/warehouse.duckdb -c "EXPORT DATABASE 'export_dir'"
```

---

### uploads/

Default location for CSV file uploads.

**Location**: `data/uploads/`

**How it's used**:
1. You drop CSV files here
2. File watcher detects changes (if `auto_sync: true`)
3. Dango auto-syncs after debounce period
4. Data lands in `raw.*` tables

**File naming patterns**:
```yaml
# Match specific pattern
file_pattern: "orders_*.csv"
# → orders_2024-12-01.csv ✓
# → orders_2024-12-02.csv ✓
# → customers.csv ✗

# Match all CSVs
file_pattern: "*.csv"
# → Any .csv file ✓
```

---

## dbt/ - dbt Project

The `dbt/` directory contains all SQL transformation logic.

### Directory Contents

```
dbt/
├── dbt_project.yml           # dbt project configuration
├── profiles.yml              # DuckDB connection profile
├── models/
│   ├── staging/              # Auto-generated staging models
│   │   ├── stg_stripe_charges.sql
│   │   ├── stg_stripe_customers.sql
│   │   ├── _stg_stripe__sources.yml
│   │   └── _stg_stripe__schema.yml
│   ├── intermediate/         # User-created business logic
│   │   ├── int_customer_ltv.sql
│   │   └── int_customer_segments.sql
│   └── marts/                # User-created final metrics
│       ├── customer_metrics.sql
│       ├── daily_sales.sql
│       └── schema.yml
├── macros/                   # Reusable SQL macros
├── tests/                    # Data tests
├── snapshots/                # SCD Type 2 snapshots
└── target/                   # Build artifacts (git-ignored)
```

**What to commit**: Everything except `target/`, `logs/`, `dbt_packages/`

---

### dbt_project.yml

dbt project configuration.

**Location**: `dbt/dbt_project.yml`

**Auto-generated content**:
```yaml
name: my_analytics
version: 1.0.0

profile: duckdb
model-paths: [models]
test-paths: [tests]
data-paths: [data]
macro-paths: [macros]
snapshot-paths: [snapshots]

target-path: target
clean-targets: [target, dbt_packages]

models:
  my_analytics:
    staging:
      materialized: view      # Fast, always fresh
      tags: [staging]
    intermediate:
      materialized: table     # Pre-computed for reuse
      tags: [intermediate]
    marts:
      materialized: table     # Optimized for BI queries
      tags: [marts]
```

---

### profiles.yml

dbt DuckDB connection configuration.

**Location**: `dbt/profiles.yml`

**Auto-generated content**:
```yaml
duckdb:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/warehouse.duckdb
      threads: 4
```

**Connects dbt to**: `data/warehouse.duckdb`

---

### models/ Structure

#### staging/

Auto-generated by `dango generate`.

**Do not edit manually** - regenerate with `dango generate`.

**Contents**:
- `stg_<source>_<table>.sql` - Deduplication logic
- `_stg_<source>__sources.yml` - Documents raw tables
- `_stg_<source>__schema.yml` - Column descriptions

#### intermediate/

User-created reusable business logic.

**You create these files**.

**Examples**:
```sql
-- int_customer_ltv.sql
-- Reusable customer lifetime value calculation

-- int_customer_segments.sql
-- Customer segmentation logic
```

#### marts/

User-created final metrics for BI tools.

**You create these files**.

**Examples**:
```sql
-- customer_metrics.sql
-- Wide table with all customer KPIs

-- daily_sales.sql
-- Daily aggregated sales metrics
```

---

## custom_sources/ - Custom dlt Sources

Write custom dlt sources without modifying Dango code.

### Directory Contents

```
custom_sources/
├── my_api_source.py
├── internal_crm.py
└── legacy_system.py
```

**What to commit**: All `.py` files

---

### Example Custom Source

**File**: `custom_sources/my_api_source.py`

```python
import dlt
from typing import Iterator, Dict, Any

@dlt.resource
def my_api_source(api_key: str, endpoint: str) -> Iterator[Dict[str, Any]]:
    """
    Custom dlt source for internal API.
    """
    import requests

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()

    for item in response.json():
        yield item
```

**Configuration in sources.yml**:
```yaml
- name: my_api_data
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: my_api_source        # Filename (without .py)
    source_function: my_api_source      # Function name
    function_kwargs:
      api_key_env: MY_API_KEY          # From .env or secrets.toml
      endpoint: "https://api.internal.com/data"
```

**Learn more**: [Custom Sources guide](../data-sources/custom-sources.md)

---

## Docker Configuration

Docker Compose orchestrates Metabase and dbt-docs containers.

### docker-compose.yml

Service definitions.

**Location**: `docker-compose.yml`

**Auto-generated content**:
```yaml
version: '3.8'

services:
  metabase:
    image: metabase/metabase:latest
    container_name: dango-metabase-my-analytics
    ports:
      - "3000:3000"
    volumes:
      - ./data/warehouse.duckdb:/duckdb/warehouse.duckdb
      - ./metabase-plugins:/plugins
    environment:
      MB_DB_FILE: /metabase-data/metabase.db
      MB_PLUGINS_DIR: /plugins

  dbt-docs:
    image: fishtownanalytics/dbt:latest
    container_name: dango-dbt-docs-my-analytics
    ports:
      - "8081:8080"
    volumes:
      - ./dbt/target:/usr/app/target
    command: docs serve --port 8080
```

---

### Dockerfile

Metabase with DuckDB driver.

**Location**: `Dockerfile`

**Auto-generated content**:
```dockerfile
FROM metabase/metabase:latest

# Install DuckDB driver
COPY metabase-plugins/duckdb.metabase-driver.jar /plugins/

ENV MB_PLUGINS_DIR=/plugins
```

---

## .gitignore

Git ignore patterns to protect secrets and large files.

**Location**: `.gitignore`

**Auto-generated content**:
```gitignore
# Secrets
.env
.dlt/secrets.toml
*.key
*.pem

# Data (large files)
data/
*.duckdb
*.duckdb.wal

# dbt artifacts
dbt/target/
dbt/logs/
dbt/dbt_packages/

# Python
__pycache__/
*.pyc
.venv/
venv/

# System
.DS_Store
```

**What gets committed**:
- `.dango/project.yml`
- `.dango/sources.yml`
- `dbt/models/` (your SQL)
- `custom_sources/` (your Python)
- `docker-compose.yml`
- `README.md`

**What stays local**:
- `data/warehouse.duckdb` (database)
- `.env` (secrets)
- `.dlt/secrets.toml` (API keys)

---

## .env - Environment Variables

Store secrets and environment-specific configuration.

**Location**: `.env`

**Example**:
```bash
# Stripe
STRIPE_API_KEY=sk_live_abc123...

# Google Analytics
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# HubSpot
HUBSPOT_API_KEY=pat-na1-xyz...

# Custom sources
MY_API_KEY=internal-api-key-here
INTERNAL_API_URL=https://api.internal.com
```

**Security**:
- **Never commit** (in `.gitignore`)
- Use for local development
- For production, use proper secrets management

**Precedence**:
1. `.dlt/secrets.toml` (highest)
2. `.env`
3. System environment variables (lowest)

---

## dashboards/ - Metabase Exports (Optional)

Store exported Metabase dashboard definitions.

**Location**: `dashboards/`

**Example**:
```
dashboards/
├── customer-overview.yml
├── daily-sales.yml
└── churn-analysis.yml
```

**How to use**:
1. Export dashboard from Metabase UI
2. Save YAML to `dashboards/`
3. Commit to Git
4. Teammates import into their Metabase

**Learn more**: [Metabase Workflows](../workflows/metabase-workflows.md)

---

## README.md

Auto-generated project documentation.

**Location**: `README.md`

**Auto-generated on `dango init`**:
````markdown
# my-analytics

Track daily sales and customer behavior

## Quick Start

```bash
dango sync
dango start
```

Open: http://localhost:8800

## Stakeholders

- Bob Chen (CEO) - bob@acme.com
- Sarah Lee (Analyst) - sarah@acme.com

## SLA

Daily by 9am UTC

## Limitations

Stripe data has 24h delay. GA4 takes 48h to backfill.
````

---

## File Size Reference

Typical file sizes for a small project:

| File/Directory | Size | Notes |
|----------------|------|-------|
| `data/warehouse.duckdb` | 10-500 MB | Grows with data volume |
| `.dango/sources.yml` | 1-5 KB | Depends on source count |
| `dbt/models/` | 10-100 KB | Depends on model count |
| `docker-compose.yml` | 1 KB | Static |
| Total project | 50-1000 MB | Mostly database |

---

## Backup Strategy

**What to backup**:
1. **Database**: `data/warehouse.duckdb`
2. **Configuration**: `.dango/`, `dbt/models/`
3. **Custom code**: `custom_sources/`
4. **Secrets**: `.env`, `.dlt/secrets.toml` (separately!)

**What NOT to backup**:
- `dbt/target/` (regenerated)
- Docker images (re-downloadable)
- `metabase-plugins/` (re-downloadable)

**Learn more**: [Backup & Restore guide](../workflows/backup-restore.md)

---

## Multi-Project Setup

Running multiple Dango projects on the same machine:

```
~/analytics/
├── project-a/
│   ├── .dango/project.yml       # port: 8800
│   ├── data/warehouse.duckdb
│   └── dbt/
├── project-b/
│   ├── .dango/project.yml       # port: 8801
│   ├── data/warehouse.duckdb
│   └── dbt/
└── project-c/
    ├── .dango/project.yml       # port: 8802
    ├── data/warehouse.duckdb
    └── dbt/
```

**Each project gets unique ports**:
- Project A: Web UI 8800, Metabase 3000, dbt-docs 8081
- Project B: Web UI 8801, Metabase 3001, dbt-docs 8082
- Project C: Web UI 8802, Metabase 3002, dbt-docs 8083

**Manage all projects**:
```bash
# Check all running projects
dango status --all

# Stop all projects
dango stop --all
```

---

## Next Steps

- **[Architecture](architecture.md)** - See how files relate to components
- **[Data Layers](data-layers.md)** - Understand where data lives in DuckDB
- **[CLI Overview](cli-overview.md)** - Commands that operate on this structure
- **[Quick Start](../getting-started/quick-start.md)** - Create your first project
