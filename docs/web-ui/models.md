# Models Page

Browse and run dbt models from the web interface.

---

## Overview

The Models page (`/models`) displays all dbt models in your project with their current status. Use it to check which models have run successfully and to trigger individual model runs from the browser.

Navigate to **Models** in the top navigation bar.

## Models Table

The table shows all models from your dbt project:

| Column | Description |
|--------|-------------|
| **Model** | Model name (e.g., `stg_customers`, `fct_orders`) |
| **Schema** | Database schema the model materializes into (e.g., `raw`, `staging`, `marts`) |
| **Type** | Materialization type — `table`, `view`, or `incremental` |
| **Rows** | Number of rows in the materialized model |
| **Status** | Current run status (see [Status Indicators](#status-indicators) below) |
| **Last Run** | Timestamp of the most recent dbt run for this model |
| **Actions** | Run button to trigger a dbt run for the model |

### Status Indicators

- **Success** (green) — model ran successfully on its last execution
- **Error** (red) — model failed on its last run
- **Running** (yellow, pulsing) — model is currently being executed via the UI
- **Skipped** (gray) — model was skipped in the last run
- **Not Run** (gray) — model has not been run yet

## Running a Model

1. Find the model in the table.
2. Click the **Run** action button in its row.
3. A toast notification confirms the run has started.
4. The status updates in real time via WebSocket as the run progresses.

The table provides two run actions:

- **Run** — runs just the selected model (`dbt run --select model_name`)
- **Run+** — runs the model and all its downstream dependents (`dbt run --select model_name+`), keeping dependent models in sync

!!! info "DuckDB write lock"
    dbt runs acquire the DuckDB write lock. If a sync is already running, the model run waits for the lock to be released. Only one write operation can run at a time.

## Refresh

Click the **refresh icon** (top-right of the table header) to reload the models list from the dbt manifest. This picks up changes to your dbt project without a full page refresh.

??? info "How it works"
    - **List models:** `GET /api/dbt/models` returns all models from the dbt manifest with status metadata.
    - **Run a model:** `POST /api/dbt/models/{model_name}/run` starts a background task that acquires a dbt lock, runs the model via subprocess, and refreshes the Metabase connection on success. Runs have a 5-minute timeout.
    - **WebSocket events:** The page receives `dbt_run_started`, `dbt_run_progress`, `dbt_run_completed`, and `dbt_run_failed` events for real-time updates and toast notifications.

## Troubleshooting

**Models table shows "Loading dbt models..."**
:   dbt has not been run yet or the manifest file is missing. Run `dbt run` from the CLI to generate the manifest, or trigger a sync (which runs dbt automatically).

**Model run fails with lock error**
:   Another write operation (sync or dbt run) is in progress. Wait for it to complete and try again. The toast notification shows which operation holds the lock.

**Model run times out**
:   Model runs have a 5-minute timeout. For large models, run from the CLI with `dbt run --select model_name` which has no timeout limit.

## Related Pages

- [Catalog Page](catalog.md) — browse model columns, lineage, and profiling stats
- [Schedules Page](schedules.md) — automated dbt runs on a schedule
- [Dashboard Page](dashboard.md) — service status and recent activity
