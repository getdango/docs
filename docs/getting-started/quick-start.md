# Quick Start

Get your first data pipeline running in under 10 minutes.

## Prerequisites

Before starting, make sure you have:

- [x] Installed Dango ([Installation Guide](installation.md))
- [x] Python 3.10+ and Docker Desktop running
- [x] Virtual environment activated (if using venv)

---

## Step 1: Install and Initialize

Run the install script to set up your project:

=== "macOS / Linux"

    ```bash
    curl -sSL https://raw.githubusercontent.com/getdango/dango/main/install.sh | bash
    ```

=== "Windows"

    ```powershell
    irm https://raw.githubusercontent.com/getdango/dango/main/install.ps1 | iex
    ```

The installer will:

- Create a project directory
- Set up an isolated virtual environment
- Install Dango from PyPI
- Run `dango init` to configure your project

!!! tip "Already installed?"
    If you've already run the installer, activate your environment and skip to Step 2:

    === "macOS / Linux"

        ```bash
        cd my-analytics
        source venv/bin/activate
        ```

    === "Windows"

        ```powershell
        cd my-analytics
        .\venv\Scripts\Activate.ps1
        ```

---

## Step 2: Add a Data Source

Let's add your first data source. Dango supports CSV files and 29+ verified dlt sources.

### Option A: CSV File (Simplest)

```bash
dango source add
```

Follow the prompts:

1. Select **CSV** as the source type
2. Provide a path to your CSV file
3. Give it a descriptive name (e.g., `sales_data`)

**Example:**

```bash
$ dango source add
? Select source type: CSV
? CSV file path: /path/to/your/data.csv
? Source name: sales_data
✓ CSV source 'sales_data' added successfully
```

### Option B: Stripe (API Integration)

For a more advanced example, try Stripe:

```bash
dango source add
```

Follow the prompts:

1. Select **Stripe** as the source type
2. Enter your Stripe API key (get it from [Stripe Dashboard](https://dashboard.stripe.com/apikeys))
3. Give it a descriptive name (e.g., `stripe_payments`)

### Option C: Google Sheets (OAuth)

```bash
dango source add
```

Follow the prompts:

1. Select **Google Sheets** as the source type
2. Complete OAuth authentication in your browser
3. Provide the Google Sheet URL
4. Give it a descriptive name (e.g., `marketing_data`)

---

## Step 3: Sync Your Data

Now let's pull data from your source into DuckDB:

```bash
dango sync
```

**What happens during sync:**

1. dlt connects to your data source
2. Data is loaded into the `raw` schema in DuckDB
3. dbt generates staging models automatically
4. Transformations run to create clean, deduplicated data

**Example output:**

```bash
$ dango sync
[18:30:45] Starting sync for all sources...
[18:30:46] → sales_data: Extracting data...
[18:30:47] → sales_data: Loading to DuckDB...
[18:30:48] → sales_data: 1,234 rows loaded
[18:30:49] Running dbt transformations...
[18:30:51] ✓ 3 models completed successfully
[18:30:51] ✓ Sync completed in 6.2s
```

### Dry Run (Preview Without Executing)

To preview what will happen without executing:

```bash
dango sync --dry-run
```

---

## Step 4: Start the Platform

Start the Web UI, Metabase, and dbt docs server:

```bash
dango start
```

**What starts:**

- **Web UI** - `http://localhost:8800`
- **Metabase** - Accessible through Web UI
- **dbt docs** - Accessible through Web UI

**Example output:**

```bash
$ dango start
[18:31:00] Starting Dango platform...
[18:31:02] ✓ Docker containers started
[18:31:05] ✓ Metabase ready
[18:31:06] ✓ Web UI ready at http://localhost:8800
[18:31:06] ✓ Platform started successfully
[18:31:06] Opening http://localhost:8800 in your browser...
```

Your browser should open automatically. If it doesn't, visit `http://localhost:8800` manually.

### Open the Dashboard

=== "macOS / Linux"

    ```bash
    open http://localhost:8800
    ```

=== "Windows"

    ```powershell
    Start-Process http://localhost:8800
    ```

Or simply visit `http://localhost:8800` in your browser.

---

## Step 5: Explore Your Data

### Web UI (http://localhost:8800)

The Web UI provides:

- **Pipeline Status** - See all your data sources and their sync status
- **Data Sources** - Add, edit, and manage sources
- **Transformations** - View and manage dbt models
- **Metabase** - Access dashboards (link in Web UI)
- **dbt docs** - Explore your data models (link in Web UI)

### Metabase Dashboards

1. Click **"Open Metabase"** in the Web UI
2. Metabase is auto-configured with your DuckDB database
3. Start exploring your data with SQL or visual query builder

**First time setup:**

- No login required (auto-configured)
- All tables are already connected
- Start creating dashboards immediately

### Query Your Data with SQL

You can also query DuckDB directly using the DuckDB CLI:

```bash
# Install DuckDB CLI if not already installed
# brew install duckdb  # macOS
# apt-get install duckdb  # Linux

# Query your data
duckdb data/warehouse.duckdb "SELECT * FROM marts.dim_customers LIMIT 10"
```

Or open an interactive SQL session:

```bash
duckdb data/warehouse.duckdb

D SELECT * FROM marts.dim_customers LIMIT 10;
D .exit
```

**Recommended**: Use Metabase's SQL editor (accessible via the Web UI at `http://localhost:8800`) for a better query experience with autocomplete and visualization.

---

## Step 6: Add Transformations

Dango auto-generates staging models, but you can add your own transformations:

### Create a New dbt Model

1. Navigate to your dbt models directory:
   ```bash
   cd dbt_project/models/
   ```

2. Create a new model file (e.g., `marts/revenue_summary.sql`):
   ```sql
   {{ config(materialized='table') }}

   SELECT
       DATE_TRUNC('month', order_date) AS month,
       SUM(amount) AS total_revenue,
       COUNT(DISTINCT customer_id) AS unique_customers
   FROM {{ ref('stg_sales_data') }}
   GROUP BY 1
   ORDER BY 1 DESC
   ```

3. Run dbt to materialize your model:
   ```bash
   dango sync
   ```

Your new model is now available in DuckDB and Metabase!

---

## Step 7: Automate with File Watcher

Enable automatic syncing when CSV files change by configuring auto-sync:

**1. Enable in configuration:**

Edit `.dango/project.yml`:

```yaml
platform:
  auto_sync: true
  debounce_seconds: 600  # Wait 10 minutes after last change
```

**2. Start platform with auto-sync:**

```bash
dango start
```

**What it does:**

- Monitors CSV files configured with `watch: true` in sources.yml
- Automatically runs `dango sync` when changes detected
- Debounces changes to avoid excessive syncing
- Keeps your data up-to-date automatically

**Configure which sources to watch:**

```yaml
# .dango/sources.yml
sources:
  - name: sales_data
    type: csv
    csv:
      file_path: data/sales.csv
      watch: true  # Enable auto-sync for this file
```

Auto-sync runs in the background while `dango start` is running.

---

## Common Workflows

### Daily Data Pipeline

```bash
# Morning routine
source venv/bin/activate
dango sync                    # Pull fresh data
dango start                   # Start dashboards
```

### Development Workflow

```bash
# Make changes to dbt models
cd dbt_project/models/

# Test your changes
dango sync --dry-run          # Preview changes
dango sync                    # Apply changes

# View results in Metabase
open http://localhost:8800
```

### Adding More Sources

```bash
# Add another source
dango source add

# Sync all sources
dango sync

# Sync specific source only
dango sync --source stripe_payments
```

---

## Verify Everything Works

Let's make sure your setup is complete:

```bash
# Check Dango version
dango --version

# Validate installation
dango validate

# Check sync status
dango status

# List all sources
dango source list
```

---

## Next Steps

Now that you have a working pipeline:

1. **[Core Concepts](../core-concepts/index.md)** - Understand Dango's architecture
2. **[Data Sources](../data-sources/index.md)** - Connect more data sources
3. **[Transformations](../transformations/index.md)** - Write advanced dbt models
4. **[Dashboards](../dashboards/index.md)** - Build Metabase dashboards
5. **[Web UI & CLI](../reference/index.md)** - Explore all commands

---

## Troubleshooting

### "dango: command not found"

Make sure your virtual environment is activated:

=== "macOS / Linux"

    ```bash
    source venv/bin/activate
    ```

=== "Windows"

    ```powershell
    .\venv\Scripts\Activate.ps1
    ```

### "Docker not running"

Start Docker Desktop and verify:

```bash
docker --version
```

### "Port 8800 already in use"

Stop any running Dango instances:

```bash
dango stop
```

Or kill the process using the port:

```bash
lsof -ti:8800 | xargs kill -9
```

### More Issues?

Check the full **[Troubleshooting Guide](troubleshooting.md)** or [open an issue](https://github.com/getdango/dango/issues).

---

## Summary

You've successfully:

- ✅ Initialized a Dango project
- ✅ Added a data source
- ✅ Synced data to DuckDB
- ✅ Started the Web UI and Metabase
- ✅ Explored your data

**Keep learning:**

- Explore the **[CLI Reference](../reference/index.md)** for all commands
- Learn about **[Data Sources](../data-sources/index.md)**
- Master **[dbt Transformations](../transformations/index.md)**
