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
    curl -sSL https://getdango.dev/install.sh | bash
    ```

=== "Windows"

    ```powershell
    irm https://getdango.dev/install.ps1 | iex
    ```

The installer will:

- Create a project directory
- Set up an isolated virtual environment
- Install Dango from PyPI
- Run `dango init` to configure your project

During `dango init`, you set an admin password for the Web UI. This configures authentication automatically — no extra setup needed.

!!! info "Authentication is always on"
    Dango enables authentication by default. During `dango init`, you set an admin password that protects the Web UI and Metabase. For local development, sessions last 365 days so you rarely need to re-authenticate. See [Authentication](../security/authentication.md) for details.

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

Let's add your first data source. Dango supports 35 data sources including file imports, APIs, databases, and OAuth-based services.

### Option A: File Import (Simplest)

```bash
dango source add
```

Follow the prompts:

1. Select **File Import (CSV, JSON, Parquet)** as the source type
2. Provide a path to your data file (CSV, JSON, or Parquet)
3. Give it a descriptive name (e.g., `sales_data`)

**Example:**

```bash
$ dango source add
? Select source type: File Import (CSV, JSON, Parquet)
? File path: /path/to/your/data.csv
? Source name: sales_data
✓ Source 'sales_data' added successfully
```

Your `sources.yml` will look like this:

```yaml
# .dango/sources.yml
sources:
  - name: sales_data
    type: local_files
    local_files:
      file_path: /path/to/your/data.csv
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

!!! tip "Managing OAuth credentials"
    Check the status of your OAuth tokens with `dango oauth status`. Re-authenticate anytime with the source-specific command (e.g., `dango oauth google_sheets`, `dango oauth facebook_ads`). See [OAuth Guide](../security/oauth.md) for details.

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

- **Web UI** — `http://localhost:8800`
- **Metabase** — Accessible through the Web UI (SSO bridge)
- **dbt docs** — Accessible through the Web UI

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

Your browser should open automatically. If it doesn't, visit `http://localhost:8800` manually. Log in with the admin password you set during `dango init`.

!!! tip "Explore the Web UI"
    After logging in, you'll see the **Dashboard** page with system health and recent activity. Use the top navigation to explore:

    - **Sources** — view your data sources, trigger syncs, upload CSVs
    - **Models** — browse and run dbt transformation models
    - **Schedules** — set up automated sync schedules
    - **Catalog** — explore your data warehouse tables and columns
    - **Notebooks** — launch Python notebooks for ad-hoc analysis
    - **Monitoring** — track data quality and freshness metrics

    See the [Platform Tour](platform-tour.md) for a full walkthrough of each page.

!!! note "Metabase cold start"
    The first time Metabase starts, it takes 2–3 minutes to initialize its database. Subsequent starts are much faster. You can check progress with `docker ps`.

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

- **Pipeline Status** — See all your data sources and their sync status
- **Data Sources** — Add, edit, and manage sources
- **Transformations** — View and manage dbt models
- **Metabase** — Access dashboards (SSO bridge, no separate login needed)
- **dbt docs** — Explore your data models
- **Monitoring** — Schema drift alerts, sync history, health checks

### Metabase Dashboards

1. Click **"Open Metabase"** in the Web UI sidebar
2. Metabase is auto-configured with your DuckDB database
3. Start exploring your data with SQL or the visual query builder

!!! tip "Build a full dashboard"
    See **[Your First Dashboard](first-dashboard.md)** for a step-by-step guide to creating questions, building dashboards, and saving your configuration.

### Query Your Data with SQL

You can query DuckDB directly using Metabase's SQL editor (via the Web UI) or from the command line. Open an interactive DuckDB session:

```bash
duckdb data/warehouse.duckdb
```

```sql
D SELECT * FROM staging.stg_sales_data LIMIT 10;
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

## Step 7: Automate with Scheduling

Set up automatic syncing on a schedule:

**1. Enable in configuration:**

Edit `.dango/project.yml`:

```yaml
platform:
  auto_sync: true
  debounce_seconds: 600  # Wait 10 minutes after last change
```

**2. Add a schedule:**

```bash
dango schedule add
```

The interactive wizard will prompt you for the source name and schedule (e.g., "every day at 8am", custom cron expressions).

**3. Start the platform:**

```bash
dango start
```

The scheduler runs automatically while the platform is running.

Learn more in [Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md) and [Configuring Schedules](../scheduling-monitoring/configuring.md).

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
dango sync stripe_payments
```

---

## Verify Everything Works

Let's make sure your setup is complete:

```bash
# Check Dango is installed
which dango

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

1. **[Your First Dashboard](first-dashboard.md)** — Build a Metabase dashboard step by step
2. **[Core Concepts](../core-concepts/index.md)** — Understand Dango's architecture
3. **[Data Sources](../data-sources/index.md)** — Connect more data sources
4. **[Transformations](../transformations/index.md)** — Write advanced dbt models
5. **[Dashboards](../dashboards/index.md)** — Advanced Metabase features
6. **[Scheduling & Monitoring](../scheduling-monitoring/index.md)** — Automate your pipelines
7. **[Security](../security/index.md)** — Authentication, OAuth, credentials
8. **[Deployment](../deployment/index.md)** — Deploy to the cloud
9. **[CLI Reference](../cli/cli-reference.md)** — Explore all 50+ commands
10. **[Notebooks](../notebooks/index.md)** — Interactive data exploration

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

If you just installed Dango, clear the shell's command cache:

```bash
hash -r
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

- ✅ Initialized a Dango project (with authentication)
- ✅ Added a data source
- ✅ Synced data to DuckDB
- ✅ Started the Web UI and Metabase
- ✅ Explored your data

**Keep learning:**

- Explore the **[CLI Reference](../cli/cli-reference.md)** for all 50+ commands
- Learn about **[Data Sources](../data-sources/index.md)**
- Master **[dbt Transformations](../transformations/index.md)**
- Set up **[Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md)**
