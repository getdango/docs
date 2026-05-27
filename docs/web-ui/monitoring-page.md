# Monitoring Page

View metric results, trends, drill-downs, and dbt test outcomes.

---

## Overview

The Monitoring page (`/monitoring`) displays configured metric monitors and data quality check results. Use it to track key metrics over time, investigate anomalies with drill-downs, and review dbt test pass/fail status.

Navigate to **Monitoring** in the top navigation bar.

The page header shows a summary: "**X monitors**, **Y flagged**" (the flagged count only appears if there are flagged metrics).

## Running Analysis

Click the **Run Analysis** button (top-right) to execute a fresh analysis across all configured monitors. The button shows a spinner and "Running..." text while the analysis is in progress. Results update automatically when the analysis completes.

!!! tip "First time?"
    If no monitors are configured, the page shows: "No monitors configured or no data available. Configure monitors in `.dango/monitors.yml`."

## Metric Cards

Each configured metric displays as a card with:

### Card Header

- **Status badge** — color-coded by state:
    - **Normal** (green) — metric within expected range
    - **Trending** (yellow) — metric trending toward a threshold
    - **Flagged** (red) — metric exceeds threshold or has anomalous change
    - **Error** (gray) — metric computation failed
- **Metric name** — the monitor identifier
- **Current value** — displayed in monospace font. Freshness metrics show as dates.
- **Change percentage** — red for increases (positive), green for decreases (negative)
- **Trend direction** — arrow or indicator (hidden on mobile)

### Card Metadata

Below the header, additional context includes:

- **Source** — linked to the [Catalog page](catalog.md) if available
- **Comparison type** — e.g., "day over day", "week over week"
- **Error message** — shown in red if the metric computation failed

### Drill-Down View

If a metric has drill-down data, a **Drill-down** link appears. Click it to expand a breakdown by dimension:

- Each dimension shows its name as a heading
- The top 5 contributors display with their change percentage
- Change values are color-coded: red for increases, green for decreases
- Null dimension values display as "(null)"

Click **Hide** to collapse the drill-down.

### History View

Click **History** on a metric card to expand a 30-day history table:

| Column | Description |
|--------|-------------|
| **Recorded** | Timestamp with relative time (e.g., "Jan 15, 2:30 PM (3h ago)") |
| **Value** | Metric value at that point in time |

The history header shows the comparison type and baseline value when available. Click **Hide history** to collapse.

## Data Quality Checks

Below the metric cards, the **Data Quality Checks** section shows dbt test results grouped by model.

### Summary Counts

The header shows aggregated test counts:

- "**X passing**" (always shown)
- "**Y failing**" (red, only if failures exist)
- "**Z not run**" (gray, only if unexecuted tests exist)

### Grouped by Model

Tests are organized into collapsible groups by model name. Each group header shows:

- Model name
- Per-model counts: "X pass", "Y fail", "Z not run"

Groups with failing tests are **auto-expanded** on page load so failures are immediately visible.

Click a group header to expand or collapse it. Each test row shows:

- **Test name** — in monospace font (e.g., `not_null_orders_id`, `unique_customers_email`)
- **Status badge**:
    - **pass** (green)
    - **fail** or **error** (red)
    - **not run** (gray)

??? info "How it works"
    - **Load cached results:** `GET /api/monitoring` returns the most recent metric results and dbt test outcomes from the SQLite cache.
    - **Run analysis:** `POST /api/monitoring/run` executes a fresh analysis, stores results, and returns updated metrics and test data. Optionally filter by source with the `?source=` parameter.
    - **Metric history:** `GET /api/monitoring/history?metric=X&days=30` returns up to 1,000 data points for a specific metric over the requested time window (1-365 days).
    - The page uses legacy-compatible redirect support: `/api/insights` redirects to `/api/monitoring`.

## Troubleshooting

**"No monitors configured" message**
:   Create a monitors configuration file at `.dango/monitors.yml`. See the monitoring configuration guide for setup instructions.

**Metric shows "Error" status**
:   The metric computation failed. Check the error message on the card for details. Common causes: missing table (run a sync first), invalid SQL in the monitor definition, or DuckDB connection issues.

**Data Quality Checks section doesn't appear**
:   dbt tests must be run before results appear. Run `dbt test` from the CLI, or trigger a schedule that includes dbt tests. The section only renders when test results exist.

## Related Pages

- [Catalog Page](catalog.md) — browse the tables and models referenced by monitors
- [Health & Logs](health-logs.md) — platform health and error logs
- [Schedules Page](schedules.md) — scheduled analysis runs
