# Dev Workflow

Run dbt against a copy of your production database. The dev workflow lets you test model changes, add new models, and inspect results without modifying production data.

---

## Overview

The `dango dev` command:

1. Copies `data/warehouse.duckdb` to `.dango/dev/warehouse_dev.duckdb`
2. Generates a dev `profiles.yml` pointing at the copy
3. Runs `dbt run` against the dev database
4. Shows results with optional row-count comparison

Your production database is never modified.

---

## Quick Start

```bash
# Run all models against a dev copy
dango dev

# Inspect results, then clean up
dango dev clean
```

---

## Running Dev Builds

```bash
dango dev
```

Output:

```
Copying production database (45.2 MB)...
✓ Dev environment ready at .dango/dev

Running: dbt run --project-dir dbt --profiles-dir .dango/dev

...dbt output...

┌──────────────────────────┬─────────┬──────────┐
│ Model                    │ Status  │ Time (s) │
├──────────────────────────┼─────────┼──────────┤
│ stg_shopify__orders      │ success │     0.42 │
│ stg_shopify__customers   │ success │     0.38 │
│ int_order_items          │ success │     0.51 │
│ mart_revenue             │ success │     0.67 │
└──────────────────────────┴─────────┴──────────┘

  4 passed

✓ Dev run completed successfully.

Dev database: .dango/dev/warehouse_dev.duckdb
Run 'dango dev clean' to remove dev artifacts.
```

### Dev Profile Configuration

The generated `profiles.yml` uses these settings:

```yaml
your_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: /absolute/path/to/.dango/dev/warehouse_dev.duckdb
      schema: main
      threads: 4
      extensions:
        - httpfs
        - parquet
      settings:
        memory_limit: 4GB
        threads: 4
```

!!! info "Absolute Path"
    The dev profile uses an absolute path to the dev database to avoid dbt-duckdb path resolution ambiguity.

---

## Selective Runs

Use `--select` (or `-s`) to run specific models:

```bash
# Run a single model
dango dev --select stg_orders

# Run all models matching a pattern
dango dev --select "stg_shopify_*"

# Run a model and its downstream dependencies
dango dev -s "stg_orders+"

# Run all marts models
dango dev -s "marts.*"
```

The `--select` flag passes directly to `dbt run --select`, so all [dbt node selection](https://docs.getdbt.com/reference/node-selection/syntax) syntax works.

!!! tip "Use --select for Large Projects"
    The dev run has a 5-minute timeout. If your full dbt project takes longer, use `--select` to run a subset of models.

---

## Comparing Results

Use `--diff` to see row-count differences between production and dev:

```bash
dango dev --diff
```

After the dbt run completes, a comparison table shows row counts across `staging`, `intermediate`, and `marts` schemas:

```
┌──────────────────────────────┬────────────┬────────┬────────┐
│ Table                        │ Production │ Dev    │ Diff   │
├──────────────────────────────┼────────────┼────────┼────────┤
│ staging.stg_shopify__orders  │     12,450 │ 12,450 │      0 │
│ staging.stg_shopify__items   │     34,200 │ 34,200 │      0 │
│ intermediate.int_order_items │     34,200 │ 35,100 │   +900 │
│ marts.mart_revenue           │        365 │    366 │     +1 │
└──────────────────────────────┴────────────┴────────┴────────┘
```

Color coding:

- **Green (+N)** — dev has more rows than production
- **Red (-N)** — dev has fewer rows than production
- **Dim (0)** — row counts match

This is useful for validating that model changes produce expected results — for example, a new filter should reduce row counts, while a new join might increase them.

---

## Inspecting the Dev Database

The dev database persists after the run at `.dango/dev/warehouse_dev.duckdb`. You can query it directly:

```bash
# Open the dev database in DuckDB CLI
duckdb .dango/dev/warehouse_dev.duckdb

# Run ad-hoc queries
duckdb .dango/dev/warehouse_dev.duckdb -c "
  SELECT COUNT(*) FROM staging.stg_shopify__orders
"
```

The dev database contains both the original raw data (copied from production) and all model outputs from the dev run.

---

## Cleaning Up

```bash
dango dev clean
```

Output:

```
Removing dev artifacts (45.2 MB)...
✓ Cleaned up dev environment.
```

This deletes the entire `.dango/dev/` directory, including the copied database and generated profiles.

If there are no dev artifacts:

```
Nothing to clean — no dev artifacts found.
```

---

## Workflow Patterns

### New Model Development

Build and test a new model iteratively:

```bash
# 1. Create your model file
# dbt/models/intermediate/int_order_items.sql

# 2. Run just that model
dango dev -s int_order_items

# 3. Check results
duckdb .dango/dev/warehouse_dev.duckdb -c "
  SELECT * FROM intermediate.int_order_items LIMIT 10
"

# 4. Iterate until satisfied, then run against production
dango run
```

### Testing Changes to Existing Models

Compare before and after:

```bash
# 1. Run with --diff to see current state
dango dev --diff

# 2. Edit your model
# dbt/models/staging/stg_shopify__orders.sql

# 3. Run again with --diff to see impact
dango dev --diff

# 4. Compare the two diff outputs
```

### Git Branch Workflow

Use `dango dev` alongside git branches for safe experimentation:

```bash
# 1. Create a branch for your changes
git checkout -b feature/new-revenue-model

# 2. Make changes to dbt models
# Edit dbt/models/marts/mart_revenue.sql

# 3. Test with dango dev
dango dev -s mart_revenue --diff

# 4. If satisfied, commit and merge
git add dbt/models/marts/mart_revenue.sql
git commit -m "Add quarterly breakdown to revenue mart"

# 5. Clean up dev artifacts
dango dev clean
```

---

## Troubleshooting

### Timeout Error

```
dbt run timed out after 5 minutes.
Try running a subset: dango dev --select model_name
```

The dev run has a 300-second (5-minute) timeout. Use `--select` to run fewer models:

```bash
# Run only the models you're working on
dango dev -s "my_model"

# Run a model and its immediate parents
dango dev -s "+my_model"
```

### Database Not Found

```
Production database not found at data/warehouse.duckdb.
Run 'dango sync' first to load data.
```

You need synced data before running dev builds. Run `dango sync` to load data into DuckDB first.

### Large Dev Database

The dev database is a full copy of production. For large warehouses:

1. Use `--select` to limit which models run (reduces execution time, not DB size)
2. Run `dango dev clean` after each session to free disk space
3. The copy includes WAL files if present, so actual disk usage may be larger than the database file

### dbt Directory Not Found

```
Error: dbt directory not found.
```

The dbt project hasn't been initialized yet. Run `dango generate` to create the dbt project structure, or `dango sync` to load data and auto-generate models.

---

## Next Steps

<div class="grid cards" markdown>

-   **[Snapshots](snapshots.md)**

    Track historical changes to source data using SCD Type 2 snapshots.

-   **[Testing](testing.md)**

    Add dbt tests to validate data quality in your models.

-   **[Custom Models](custom-models.md)**

    Build intermediate and marts models for business logic.

-   **[dbt Basics](dbt-basics.md)**

    Learn the fundamentals of dbt in Dango.

</div>
