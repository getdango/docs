# Catalog Page

Browse the data catalog with search, profiling, lineage, and impact analysis.

---

## Overview

The Catalog page (`/catalog`) is a searchable data catalog that lets you explore all sources and dbt models in your project. View column profiles, PII annotations, schema drift, dependency lineage, and downstream impact — all from the browser.

Navigate to **Catalog** in the top navigation bar.

The Catalog has three views: **List** (default), **Detail**, and **Lineage**. Your position is reflected in the URL, so you can bookmark or share specific views.

## Summary Cards

At the top of the list view, four cards show high-level counts:

| Card | Description |
|------|-------------|
| **Sources** | Number of data sources |
| **Tables** | Total table count across all sources |
| **Models** | Number of dbt models |
| **Sources Fresh** | Count of fresh sources vs. total (green if all fresh, amber if some stale) |

## Source Breakdown

Below the summary cards, a grid of per-source cards shows each source with:

- **Source name** and table count
- **Estimated row count**
- **Freshness badge** — "fresh" (green), "stale" (amber), or "unknown" (gray)

Click a source card to filter the table below to only that source's tables. Click **Show X more** to reveal additional sources beyond the initial 6.

## Type Filter Tabs

Filter the model/source list by type:

| Tab | Shows |
|-----|-------|
| **All** | Everything |
| **Sources** | Raw source tables (dlt-ingested data) |
| **Staging** | `stg_` staging models |
| **Intermediate** | `int_` intermediate models |
| **Marts** | Final analytics models |

Each tab shows a count of matching items. When a source filter is active, a "Showing tables from source: X" indicator appears with a **Show all** link to clear the filter.

## Search

The search bar (top of the list view) searches across model names, column names, and descriptions with a 300ms debounce. Results show:

| Column | Description |
|--------|-------------|
| **Name** | Model or source name (clickable to open detail) |
| **Type** | Type badge (source, staging, intermediate, marts) |
| **Match** | What matched — "name", "description", or "column" with the matched column name |
| **Description** | Truncated model description |

Click **Clear** next to the results header to return to the filtered list.

## Model / Source List

The main table displays all items matching the current tab and source filters:

| Column | Description |
|--------|-------------|
| **Name** | Model or source name (clickable to open detail view) |
| **Type** | Color-coded type badge |
| **Description** | Truncated model description |
| **Tests** | Pass/fail count (e.g., "3 pass / 1 fail") |
| **Documented** | Column documentation ratio (e.g., "5/8") |
| **Tags** | Up to 3 tag badges, with "+N" for additional tags |

Click any row to open the [Detail View](#detail-view).

## Detail View

Clicking a model or source opens the detail view with a breadcrumb ("Catalog / model_name") and three sub-tabs.

### Header

- **Model name** and type badge
- **Description** (if available)
- **Metadata row**: materialization type, row count, and profiling timestamp ("Profiled 5m ago")
- **Refresh Profile** button (source tables only) — re-runs column profiling

### Columns Tab

A table of all columns in the model:

| Column | Description |
|--------|-------------|
| **Column Name** | Column name with optional PII and drift badges (see below) |
| **Type** | Data type (e.g., `VARCHAR`, `INTEGER`, `TIMESTAMP`) |
| **Description** | Column description from dbt schema YAML |
| **Nullable** | Yes/No |
| **Tests** | Test badges — green "&#10003;" for passing, red "&#10007;" for failing |
| **Null %** | Percentage of null values |
| **Distinct Count** | Number of distinct values |
| **Min** | Minimum value |
| **Max** | Maximum value |

#### PII Badges

Columns detected as containing personally identifiable information show badges:

- **PII &#9873;** (amber) — auto-detected PII, with entity type in tooltip
- **PII &#10003;** (green) — confirmed PII annotation

#### Schema Drift Badges

Columns with detected schema drift show an orange badge with the drift type (e.g., "type_changed", "column_added").

### Code Tab

Shows the model's SQL (not available for source tables):

- **Raw SQL (with Jinja)** — the source `.sql` file content
- **Compiled SQL** — the rendered SQL after Jinja processing

SQL is syntax-highlighted for readability.

### Info Tab

Additional model metadata:

- **Description** — full model description
- **Schema**, **Materialization**, **Type** — key properties
- **Tags** — tag badges
- **Tests** — list of tests with status dots (green/red/gray)
- **Upstream Dependencies** — clickable links to models this one depends on
- **Downstream Dependents** — clickable links to models that depend on this one
- **View in Lineage** button — opens the lineage view focused on this model

## Lineage Visualization

Click the **Lineage** toggle button (top-right of the list view) to switch to the DAG (directed acyclic graph) view showing data flow from sources through staging, intermediate, and marts models.

### Navigation

- **Zoom in/out** — use the `+` and `−` buttons, or scroll
- **Fit all** — click the `↔` button to fit the entire graph in view
- **Pan** — click and drag the background
- **Click a node** — opens the node detail sidebar

### Focus Mode

From the detail view, click **View in Lineage** to focus the graph on that model. In focus mode:

- A **Depth selector** dropdown controls how many hops to show: 1, 2, 3, or 5
- A **Show Full DAG** button returns to the complete graph
- The URL updates to reflect the focused node

### Node Detail Sidebar

Clicking a node in the graph opens a sidebar with:

- **Type** and **Materialization**
- **Description**
- **Tests** count
- **Doc Coverage** — documented columns vs. total

Actions:

- **View Details** — opens the full detail view for this model
- **Show Downstream** — highlights all downstream dependents in the graph
- After highlighting, a count shows "X downstream model(s)" with a **Clear Highlight** button

??? info "How it works"
    - **List models:** `GET /api/catalog/models` returns all models and sources with overview counts, freshness data, and per-source detail.
    - **Model detail:** `GET /api/catalog/models/{name}` returns columns with profiling stats, tests, raw/compiled SQL, dependencies, and dependents.
    - **Refresh profile:** `POST /api/catalog/{source}/{table}/profile` re-runs column profiling for a source table.
    - **Search:** `GET /api/catalog/search?q={query}` searches across model names, descriptions, and column names (2-100 character queries).
    - **Lineage:** `GET /api/catalog/lineage` returns nodes and edges for the full DAG.
    - **Impact analysis:** `GET /api/catalog/impact/{model_name}` returns the downstream dependency tree with total count.
    - **PII and drift data** are fetched in parallel on page load and merged onto column data in the detail view.
    - **URL state:** The page encodes view, model, tab, focus, source filter, and type filter into URL parameters for bookmarkability and browser back/forward support.

## Troubleshooting

**"No models found" message**
:   dbt has not been run yet. Run `dbt run` from the CLI to materialize models and generate the manifest, or trigger a sync which runs dbt automatically.

**Column profiling stats show "—"**
:   Profiling has not been run for this table. Click **Refresh Profile** (available on source tables) or wait for the next scheduled sync which includes profiling.

**Lineage graph is empty**
:   The lineage graph requires a dbt manifest with dependency information. Run `dbt run` or `dbt compile` to generate the manifest.

## Related Pages

- [Models Page](models.md) — run individual dbt models
- [Monitoring Page](monitoring-page.md) — metric monitors and dbt test results
- [Sources Page](sources.md) — view source sync status
