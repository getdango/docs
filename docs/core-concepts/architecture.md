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
│  • 30+ verified sources  • OAuth handling  • Incremental   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DuckDB (Database)                        │
│  raw.*  →  staging.*  →  intermediate.*  →  marts.*        │
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
- 30+ verified sources (Stripe, HubSpot, Google Analytics, Salesforce, etc.)
- CSV file ingestion with auto-detection
- Custom REST API sources
- OAuth 2.0 authentication handling
- Incremental loading (only new/changed data)
- Automatic schema evolution
- Deduplication strategies

**What it does**:
```bash
dango sync
# → dlt connects to Stripe API
# → Fetches charges, customers, subscriptions
# → Writes to raw_stripe.* tables in DuckDB
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
- Works on laptop or production servers

**Database file**: `data/warehouse.duckdb`

**Schema organization**:
```
warehouse.duckdb
├── raw                  # Raw ingested data (immutable)
├── raw_stripe          # Multi-table sources
├── staging             # Cleaned, deduplicated data
├── intermediate        # Reusable business logic
└── marts               # Final metrics for BI
```

**Learn more**: [Data Layers](data-layers.md)

---

### dbt - SQL Transformations

**Purpose**: Transform raw data into analytics-ready tables

**What Dango automates**:
- Auto-generates staging models from raw tables
- Applies deduplication logic based on source config
- Creates data lineage documentation
- Generates dbt-docs website

**What you control**:
- Custom transformations in `dbt/models/`
- Business logic in SQL
- Data tests and documentation

**Example workflow**:
```bash
dango sync              # Load raw data with dlt
dango generate          # Auto-generate staging models
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
- Admin account created
- All tables and schemas discovered
- Sample collections set up

**Access**: `http://localhost:3000`

**What you can do**:
- Write SQL queries
- Create visualizations (charts, tables, maps)
- Build dashboards
- Share with stakeholders
- Schedule email reports

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

You define the source in `.dango/sources.yml`:

```yaml
sources:
  - name: stripe_payments
    type: stripe
    enabled: true
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      start_date: 2024-01-01
```

### 2. Ingestion (dlt)

When you run `dango sync`:

```bash
dango sync
```

dlt executes:
1. Reads Stripe API credentials from environment
2. Authenticates with Stripe
3. Fetches data (charges, customers, subscriptions)
4. Writes to DuckDB:
   - `raw_stripe.charges`
   - `raw_stripe.customers`
   - `raw_stripe.subscriptions`
5. Tracks load metadata (`_dlt_load_id`, `_dlt_extracted_at`)

### 3. Staging Generation

Run `dango generate` to create staging models:

```bash
dango generate
```

Dango creates:
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

Open Metabase (`http://localhost:3000`), navigate to the `marts` schema, and query `customer_metrics`:

```sql
SELECT * FROM marts.customer_metrics
ORDER BY lifetime_value DESC
LIMIT 10
```

Create charts, dashboards, and share with your team.

---

## Tech Stack Details

### Core Tools

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

### 1. Zero Infrastructure

No servers to configure. Everything runs on your laptop:
- DuckDB is embedded (single file database)
- Metabase runs in Docker
- Web UI is a simple Python process

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

Dango generates the repetitive dbt staging models:
```bash
dango generate
# → Creates 30+ staging models for Stripe
# → You focus on business logic in marts/
```

### 4. Batteries Included

Get a complete stack with one command:
```bash
dango init my-project
dango source add      # Add Stripe
dango sync           # Load data
dango start          # Open Metabase
```

---

## Next Steps

- **[Data Layers](data-layers.md)** - Learn how data is organized across schemas
- **[CLI Overview](cli-overview.md)** - Master the command-line interface
- **[Project Structure](project-structure.md)** - Understand the directory layout
