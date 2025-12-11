# Architecture Overview

Understanding how Dango's components work together.

---

## System Architecture

Dango integrates four production-grade open-source tools into a unified platform:

```
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                    │
│  APIs (Stripe, HubSpot, GA4) • CSV Files • Databases       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    dlt (Data Load Tool)                     │
│  • 30+ sources (60+ via dlt_native)  • OAuth  • Incremental │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DuckDB (Database)                        │
│  raw_{source}.*  →  staging.*  →  intermediate.*  →  marts.*│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   dbt (Transformations)                     │
│  • Auto-generated staging  • Custom SQL models             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Visualization & Management Layer               │
│  Metabase (BI) • Web UI (Monitoring) • dbt-docs            │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Overview

### dlt - Data Ingestion

**Purpose**: Load data from external sources into DuckDB

**Key Features**:
- 30+ sources with wizard support (Stripe, HubSpot, Google Analytics, Salesforce, etc.)
- Access to 60+ dlt sources via `dlt_native` for advanced users
- CSV file ingestion with auto-detection
- Custom REST API sources
- OAuth 2.0 authentication handling
- Incremental loading (only new/changed data)
- Automatic schema evolution (for dlt sources)

**What it does**:
```bash
dango sync
# → dlt connects to Stripe API
# → Fetches charges, customers, subscriptions
# → Writes to raw_stripe.* tables in DuckDB
# → Auto-generates staging models in dbt/models/staging/
# → Tracks metadata (_dlt_load_id, _dlt_extracted_at)
```

**Learn more**: [Data Sources section](../data-sources/index.md)

---

### DuckDB - Analytics Database

**Purpose**: Store and query data with SQL

**Why DuckDB?**:
- Embedded (no server to manage)
- OLAP-optimized (fast analytics queries)
- Efficient storage (columnar format)
- Full SQL support (window functions, CTEs, etc.)
- Handles datasets up to ~100GB comfortably on a modern laptop

!!! note "For larger datasets"
    DuckDB is optimized for single-machine analytical workloads. For enterprise-scale needs (petabytes), consider cloud data warehouses like Snowflake or BigQuery.

**Database file**: `data/warehouse.duckdb`

**Schema organization**:
```
warehouse.duckdb
├── raw_{source_name}   # Raw ingested data (e.g., raw_stripe, raw_hubspot)
├── staging             # Cleaned data (tables, not views)
├── intermediate        # Reusable business logic
└── marts               # Final metrics for BI
```

Each data source gets its own `raw_{source_name}` schema (e.g., `raw_stripe`, `raw_csv_orders`).

**Learn more**: [Data Layers](data-layers.md)

---

### dbt - SQL Transformations

**Purpose**: Transform raw data into analytics-ready tables

**What Dango automates**:
- Auto-generates staging models during `dango sync`
- Creates data lineage documentation
- Generates dbt-docs website (documentation and lineage visualization)

**What you control**:
- Custom transformations in `dbt/models/`
- Business logic in SQL
- Data tests and documentation

**Example workflow**:
```bash
dango sync              # Load raw data + auto-generate staging models
# Edit dbt/models/marts/customer_metrics.sql
dango run               # Run dbt transformations
dango docs              # Generate documentation
```

**Learn more**: [Transformations section](../transformations/index.md)

---

### Metabase - Business Intelligence

**Purpose**: Visualize data and create dashboards

**Auto-configured on `dango start`**:
- DuckDB connection established
- Admin account auto-provisioned (local development only)
- All tables and schemas discovered
- Sample collections set up

**Access**: Run `dango start` first, then access via:
- Web UI at `http://localhost:8800` (recommended - includes navigation to all services)
- Direct Metabase at `http://localhost:3000`

**What you can do**:
- Write SQL queries with autocomplete
- Create visualizations (charts, tables, maps)
- Build dashboards
- Set up alerts and notifications
- Schedule email reports
- Share with stakeholders

**Learn more**: [Dashboards section](../dashboards/index.md)

---

### Web UI - Monitoring & Management

**Purpose**: Monitor pipelines and manage sources

**Built with**: FastAPI (Python backend)

**Access**: `http://localhost:8800`

**Features**:
- Real-time sync status (WebSocket updates)
- Source management (add, remove, configure)
- CSV file uploads
- Validation reports
- Activity logs
- Links to Metabase and dbt-docs

**Learn more**: [Web UI section](../web-ui/index.md)

---

## Data Flow Example

Let's walk through what happens when you add a Stripe source:

### 1. Configuration

**Option A: Interactive wizard (recommended)**
```bash
dango source add
# Select "Stripe" from the list
# Follow the prompts
```

**Option B: Manual configuration** in `.dango/sources.yml`:
```yaml
sources:
  - name: stripe_payments
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      start_date: 2024-01-01
```

You can also add sources via the Web UI at `http://localhost:8800`.

### 2. Ingestion + Staging Generation

When you run `dango sync`:

```bash
dango sync
# Or trigger from Web UI at http://localhost:8800
```

Dango executes:
1. Reads Stripe API credentials from environment
2. Authenticates with Stripe via dlt
3. Fetches data (charges, customers, subscriptions)
4. Writes to DuckDB:
   - `raw_stripe.charges`
   - `raw_stripe.customers`
   - `raw_stripe.subscriptions`
5. Tracks load metadata (`_dlt_load_id`, `_dlt_extracted_at`)
6. Auto-generates staging models

### 3. Generated Staging Models

After sync, Dango creates:
```
dbt/models/staging/
├── stg_stripe_charges.sql
├── stg_stripe_customers.sql
├── stg_stripe_subscriptions.sql
├── _stg_stripe__sources.yml
└── _stg_stripe__schema.yml
```

### 4. Transformations (dbt)

Create custom business logic in `dbt/models/marts/`:

```sql
-- dbt/models/marts/customer_metrics.sql
{{ config(materialized='table') }}

WITH charges AS (
    SELECT
        customer_id,
        SUM(amount) as total_spent,
        COUNT(*) as order_count
    FROM {{ ref('stg_stripe_charges') }}
    GROUP BY customer_id
),

customers AS (
    SELECT
        id,
        email,
        created
    FROM {{ ref('stg_stripe_customers') }}
)

SELECT
    c.id,
    c.email,
    COALESCE(ch.total_spent, 0) as lifetime_value,
    COALESCE(ch.order_count, 0) as total_orders
FROM customers c
LEFT JOIN charges ch ON c.id = ch.customer_id
```

Run transformations:
```bash
dango run
```

### 5. Visualization (Metabase)

Start the platform if not already running:
```bash
dango start
```

Open the Web UI (`http://localhost:8800`) and navigate to Metabase, or go directly to `http://localhost:3000`. Query your `marts` tables:

```sql
SELECT * FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10
```

Create charts, dashboards, and share with your team.

---

## Tech Stack Details

### Core Tools (as of Dango v0.0.5)

| Tool | Version | Purpose | Language |
|------|---------|---------|----------|
| **dlt** | 0.4.x | Data ingestion | Python |
| **dbt** | 1.7.x | SQL transformations | Python + SQL |
| **DuckDB** | 0.10.x | Analytics database | C++ |
| **Metabase** | 0.49.x | Business intelligence | Java/Clojure |

### Dango Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Web Backend** | FastAPI | REST API + WebSockets |
| **Service Orchestration** | Docker Compose | Metabase + dbt-docs containers |
| **File Watcher** | watchdog (Python) | Auto-sync on file changes |
| **CLI** | Click (Python) | Command-line interface |
| **Config Management** | YAML + TOML | Sources, project settings |

---

## Service Management

When you run `dango start`, the following services are launched:

### Local Services
- **FastAPI Web UI** - Port 8800
- **File Watcher** - Background process (if `auto_sync: true`)

### Docker Containers
- **Metabase** - Port 3000
- **dbt-docs** - Port 8081

Check service status:
```bash
dango status
```

Output:
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

Stop all services:
```bash
dango stop
```

---

## Local vs. Cloud Architecture

### Current (Local)

```
┌─────────────────────────────────────┐
│        Your Laptop                  │
│  ┌──────────────────────────────┐  │
│  │  DuckDB (data/warehouse.db)  │  │
│  │  FastAPI (port 8800)         │  │
│  │  Docker (Metabase, dbt-docs) │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Future (Cloud)

```
┌─────────────────────────────────────┐
│        Cloud Infrastructure         │
│  ┌──────────────────────────────┐  │
│  │  DuckDB or Snowflake/BigQuery│  │
│  │  FastAPI (Cloud Run/Fargate) │  │
│  │  Metabase (managed instance) │  │
│  │  Orchestrator (Airflow/Prefect)│
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

The same `.dango/` configuration files work in both environments.

---

## Design Principles

### 1. Minimal Setup

Get started without complex infrastructure:
- DuckDB is embedded (single file database)
- Metabase runs in Docker
- Web UI is a lightweight Python process

### 2. Configuration Over Code

Define sources in YAML, not Python:
```yaml
# This...
sources:
  - name: stripe
    type: stripe
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY

# ...instead of this (raw dlt code)
import dlt
pipeline = dlt.pipeline(...)
data = stripe_source(api_key=os.getenv("STRIPE_API_KEY"))
pipeline.run(data)
```

### 3. Auto-Generated Boilerplate

Dango generates the repetitive dbt staging models automatically during sync:
```bash
dango sync
# → Loads data from sources
# → Auto-generates staging models
# → You focus on business logic in marts/
```

### 4. Batteries Included

Set up a complete analytics stack with one command:

```bash
curl -sSL https://raw.githubusercontent.com/getdango/dango/main/install.sh | bash
```

This gives you dlt, dbt, DuckDB, and Metabase—ready to go.

Then build your data pipeline:
```bash
dango source add      # Add data sources
dango sync           # Load data + generate staging
dango start          # Launch platform
```

---

## Next Steps

- **[Data Layers](data-layers.md)** - Learn how data is organized across schemas
- **[CLI Overview](cli-overview.md)** - Master the command-line interface
- **[Project Structure](project-structure.md)** - Understand the directory layout
