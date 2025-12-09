# Local Development

Project organization and development workflows for Dango.

---

## Project Structure

A typical Dango project has the following structure:

```
my-analytics/
├── .dango/                  # Dango state (auto-generated)
│   ├── sources.yml          # Source configurations
│   ├── project.yml          # Project settings
│   └── logs/                # Sync logs
├── .dlt/                    # dlt configuration
│   ├── config.toml          # dlt settings
│   └── secrets.toml         # Credentials (DO NOT COMMIT)
├── data/                    # Data files
│   ├── uploads/             # CSV upload directory
│   └── warehouse.duckdb     # DuckDB database
├── dbt/                     # dbt project
│   ├── models/
│   │   ├── staging/         # Auto-generated staging models
│   │   ├── intermediate/    # Your intermediate models
│   │   └── marts/           # Your mart models
│   ├── macros/
│   ├── tests/
│   └── dbt_project.yml
└── metabase-data/           # Metabase state (if using Docker)
```

---

## Directory Organization

### Data Directory

The `data/` directory contains all raw data files:

```bash
data/
├── uploads/                 # CSV files organized by source
│   ├── sales/              # Sales data CSVs
│   │   ├── orders_2024.csv
│   │   └── orders_2025.csv
│   └── inventory/          # Inventory data CSVs
│       └── products.csv
└── warehouse.duckdb        # DuckDB database file
```

!!! tip "Organizing CSV Files"
    Create subdirectories in `data/uploads/` for each CSV source. This keeps files organized and makes source configuration clearer.

### dbt Directory

The `dbt/` directory contains your transformation logic:

```bash
dbt/
├── models/
│   ├── staging/            # Auto-generated, don't edit
│   │   ├── stg_orders.sql
│   │   └── stg_products.sql
│   ├── intermediate/       # Your business logic
│   │   └── int_order_items.sql
│   └── marts/              # Final tables for dashboards
│       ├── fct_daily_sales.sql
│       └── dim_products.sql
├── macros/                 # Reusable SQL snippets
├── tests/                  # Data quality tests
├── seeds/                  # Static lookup data
└── dbt_project.yml
```

---

## Development Workflow

### 1. Initial Setup

```bash
# Create project
dango init my-analytics
cd my-analytics

# Start services
dango start
```

### 2. Add Data Sources

```bash
# Add CSV source
dango source add csv

# Add OAuth source (e.g., Google Sheets)
dango source add google_sheets
dango auth google_sheets
```

### 3. Sync Data

```bash
# Sync all sources
dango sync

# Sync specific source
dango sync --source my_csv_data
```

### 4. Develop Transformations

```bash
# After sync, staging models are auto-generated
# Edit or add models in dbt/models/

# Run transformations
dango run

# Or run specific model during development
cd dbt && dbt run --select my_model
```

### 5. Build Dashboards

```bash
# Access Metabase
open http://localhost:3000

# Or use dango web
dango web
```

---

## Iterative Development

### Hot Reload for CSV Sources

When the file watcher is enabled, CSV changes are automatically detected:

```bash
# Check watcher status
dango status

# The watcher will:
# 1. Detect file changes in data/uploads/
# 2. Wait for debounce period (default: 10 minutes)
# 3. Auto-sync changed sources
# 4. Auto-run dbt transformations
```

### Manual Iteration

For faster development cycles:

```bash
# 1. Make changes to CSV or source config
# 2. Sync immediately (skip watcher debounce)
dango sync --source my_source

# 3. Run only affected models
cd dbt && dbt run --select my_model+
```

---

## Environment Management

### Development vs Production

Create separate configurations for different environments:

=== "Development"

    ```yaml
    # .dango/project.yml (development)
    name: my-analytics-dev
    version: "0.0.5"

    # Use local data
    web_port: 8800
    ```

=== "Production"

    ```yaml
    # .dango/project.yml (production)
    name: my-analytics-prod
    version: "0.0.5"

    # Different port to avoid conflicts
    web_port: 8801
    ```

### Using Environment Variables

Store sensitive values in environment variables:

```bash
# .env file (DO NOT COMMIT)
STRIPE_API_KEY=sk_live_xxx
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/creds.json
```

Reference in secrets.toml:

```toml
# .dlt/secrets.toml
[sources.stripe]
api_key = "${STRIPE_API_KEY}"
```

---

## Testing Your Setup

### Validate Configuration

```bash
# Check all configurations
dango validate

# Check specific source
dango validate --source my_source
```

### Test Sync

```bash
# Dry run to see what would be synced
dango sync --dry-run

# Sync with debug logging
RUNTIME__LOG_LEVEL=DEBUG dango sync
```

### Test Transformations

```bash
# Compile SQL without running
cd dbt && dbt compile

# Run tests
cd dbt && dbt test
```

---

## Cleaning Up

### Reset Data

```bash
# Remove all data and start fresh
dango db clean

# This removes:
# - DuckDB database
# - dlt state
# - Keeps configuration files
```

### Stop Services

```bash
# Stop all running services
dango stop

# Check what's still running
dango status
```

---

## Next Steps

- [dbt Workflows](dbt-workflows.md) - Advanced transformation development
- [Git Workflows](git-workflows.md) - Version control best practices
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
