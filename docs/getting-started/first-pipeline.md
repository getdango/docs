# Your First Pipeline

A step-by-step walkthrough from empty project to scheduled dashboard — using Google Sheets as an example.

---

## What You'll Build

By the end of this tutorial, you'll have:

- A Dango project connected to a Google Sheets data source
- Data synced into DuckDB
- A dbt model transforming your data
- A Metabase dashboard visualizing results
- A scheduled sync keeping everything up to date

**Time:** ~20 minutes (mostly waiting for OAuth setup in Google Cloud Console)

---

## Prerequisites

- [x] Python 3.10+ installed (3.11 recommended)
- [x] Docker Desktop running
- [x] A Google account with a Google Sheet containing data

!!! tip "Don't have a Google Sheet handy?"
    Create one with sample data — any spreadsheet with headers in row 1 works. For example, a sales tracker with columns: `date`, `product`, `quantity`, `revenue`.

---

## Step 0: Set Up Your Project Directory

Create a fresh directory, set up a virtual environment, and install Dango:

```bash
mkdir my-analytics && cd my-analytics
python3.11 -m venv venv && source venv/bin/activate
pip install --pre getdango
```

!!! note "Python version"
    Dango requires Python 3.10 or higher (but below 3.13). We recommend `python3.11`. On macOS, the system `python3` may be too old — use `python3.11` or `python3.12` explicitly.

---

## Step 1: Initialize Your Project

```bash
dango init
```

The wizard prompts for an **admin email**, then auto-generates an admin password for the Web UI and Metabase. The password is displayed in the terminal output — save it somewhere.

Your project structure:

```
my-analytics/
├── .dango/           # Configuration
├── .dlt/             # dlt credentials (gitignored)
├── dbt/              # Transformation models
└── data/             # DuckDB warehouse
```

---

## Step 2: Add a Google Sheets Source

```bash
dango source add
```

The interactive wizard walks you through setup. For Google Sheets, the key prompts are:

1. **Select source type** → choose **Google Sheets**
2. **Source name** → give it a name (e.g., `sales_data`)
3. **OAuth setup** → the wizard opens your browser for Google login
4. **Spreadsheet URL** → paste the URL of your Google Sheet

See [Adding Sources](../data-sources/adding-sources.md) for the full wizard reference.

### OAuth: What to Expect

The wizard needs OAuth credentials to access your Google account. If you haven't set them up before:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Google Sheets API**
4. Configure the **OAuth consent screen** (External type, Testing mode is fine)
5. Create **OAuth client ID** credentials (Desktop app)
6. Enter the Client ID and Client Secret when the wizard asks

!!! note "\"App not verified\" warning"
    When authorizing, Google shows a warning because your app is in testing mode. Click **Advanced** → **Go to [your app]** to continue. This is expected and safe for your own data.

See the [OAuth Troubleshooting Guide](../guides/oauth-troubleshooting.md) if you hit issues.

---

## Step 3: Sync Your Data

```bash
dango sync sales_data
```

Dango will:

1. Fetch data from your Google Sheet via the Sheets API
2. Load it into DuckDB (table: `raw_sales_data.*`)
3. Auto-generate dbt staging models
4. Run dbt transformations

You'll see progress output as each step completes. After sync:

```bash
# Check what was loaded
dango db status
```

---

## Step 4: Start the Platform

```bash
dango start
```

This boots the full stack:

- **Metabase** dashboard server (via Docker)
- **FastAPI** web server (monitoring UI at `http://localhost:8800`)

!!! info "Background process"
    On macOS, `dango start` runs in the background. Closing the terminal does **not** stop Dango — the process continues running. Run `dango start` again at any time to check status or restart if needed.

Wait for the "Platform is ready" message before continuing.

---

## Step 5: Explore in Metabase

Open the Web UI:

```
http://localhost:8800
```

Click **Open Metabase** (or go directly to `http://localhost:3000`). Log in with the admin credentials Dango set up automatically.

In Metabase:

1. Click **New** → **Question**
2. Pick your table (under the schema matching your source name)
3. Build a visualization — try a bar chart of revenue by product

### Create a Dashboard

1. Click **New** → **Dashboard**
2. Give it a name (e.g., "Sales Overview")
3. Click **+** to add your question(s)
4. Arrange and resize cards
5. Click **Save**

### Save Dashboard Config

Export your dashboard to version-controllable YAML:

```bash
dango metabase save
```

This creates files in `metabase/` that you can commit to Git.

---

## Step 6: Add a dbt Model

Create a custom model to transform your data:

```bash
dango model add
```

The wizard asks:

1. **Model name** → e.g., `monthly_revenue`
2. **Source** → select your `sales_data` source
3. **Layer** → choose **marts** (for business-level aggregations)

This creates a SQL file at `dbt/models/marts/monthly_revenue.sql`. Edit it:

```sql
-- dbt/models/marts/monthly_revenue.sql
SELECT
    DATE_TRUNC('month', date) AS month,
    product,
    SUM(quantity) AS total_quantity,
    SUM(revenue) AS total_revenue
FROM {{ ref('stg_sales_data__sheet1') }}
GROUP BY 1, 2
ORDER BY 1 DESC
```

Run the model:

```bash
dango run
```

Your new `monthly_revenue` table now appears in Metabase for dashboarding.

---

## Step 7: Schedule Automatic Syncs

Keep your data fresh with a scheduled sync:

```bash
dango schedule add
```

The wizard asks:

1. **Source** → select `sales_data`
2. **Frequency** → e.g., daily at 8:00 AM
3. **Include dbt?** → Yes (runs transformations after sync)

Verify the schedule:

```bash
dango schedule status
```

Your pipeline is now fully automated — data syncs daily, transformations run, and Metabase dashboards update automatically.

---

## What You've Built

```
Google Sheets → dlt sync → DuckDB → dbt models → Metabase dashboards
                  ↑
           Scheduled daily
```

| Component | What it does |
|-----------|-------------|
| **dlt** | Extracts data from Google Sheets into DuckDB |
| **DuckDB** | Stores all your data locally (single file) |
| **dbt** | Transforms raw data into analysis-ready models |
| **Metabase** | Visualizes data as interactive dashboards |
| **APScheduler** | Runs syncs on a cron schedule |

---

## Next Steps

- **Add more sources** — run `dango source add` to connect Stripe, HubSpot, CSV files, APIs, and [30+ more](../data-sources/source-catalog.md)
- **Write custom models** — see [Custom Models](../transformations/custom-models.md) for intermediate and marts patterns
- **Deploy to cloud** — see [Deployment](../deployment/index.md) to run 24/7 on a server
- **Monitor data quality** — set up [Schema Drift](../scheduling-monitoring/schema-drift.md) and [PII Scanning](../scheduling-monitoring/pii-scanning.md)
- **Set up webhooks** — get notified on sync failures via [Webhook Notifications](../scheduling-monitoring/webhooks.md)
