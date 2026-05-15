# Save & Load (YAML)

Export Metabase dashboards and questions as YAML files for version control. Load them back to restore or share dashboard configurations across environments.

---

## Overview

The save/load workflow lets you:

- **Version control** dashboards alongside your dbt models
- **Share** dashboard configurations across team members
- **Promote** dashboards between environments (dev → staging → production)
- **Restore** dashboards after accidental changes

```
Metabase UI  ──save──►  metabase/*.yml  ──git──►  Repository
Metabase UI  ◄──load──  metabase/*.yml  ◄──git──  Repository
```

---

## Quick Start

```bash
# 1. Save dashboards from Metabase to YAML
dango metabase save

# 2. Commit to version control
git add metabase/
git commit -m "Save dashboard configurations"

# 3. On another machine or after changes, load back
dango metabase load
```

---

## Saving Dashboards

### Basic Save

```bash
dango metabase save
```

By default, exports only the **Shared** collection:

```
✅ Exported 5 item(s) to metabase/

Dashboards:
  ✓ Data Pipeline Health (6 cards) - Shared
  ✓ Sales Overview (4 cards) - Shared

Questions:
  ✓ Revenue by Month (bar) - Shared
  ✓ Customer Count (scalar) - Shared
  ✓ Order Volume (line) - Shared
```

### Export Specific Collections

```bash
# Export a specific collection
dango metabase save --collections "Our analytics"

# Export multiple collections
dango metabase save --collections "Shared,Marketing,Finance"
```

### Export Directory Structure

Saved files are organized by type in the `metabase/` directory:

```
metabase/
├── dashboards/
│   ├── data_pipeline_health.yml
│   └── sales_overview.yml
├── questions/
│   ├── revenue_by_month.yml
│   └── customer_count.yml
├── models/
│   └── customer_360.yml
├── metrics/
│   └── total_revenue.yml
├── timelines/
│   └── product_launches.yml
└── collections.yml
```

### YAML Format

#### Dashboard

```yaml
name: "Sales Overview"
description: "Monthly sales metrics and trends"
collection: "Shared"
created_at: "2026-05-15T14:30:00.000000"
updated_at: "2026-05-15T15:45:00.000000"
cards:
  - name: "Revenue by Month"
    description: "Total monthly revenue"
    type: "bar"
    dataset_query:
      type: native
      native:
        query: |
          SELECT DATE_TRUNC('month', order_date) AS month,
                 SUM(total) AS revenue
          FROM staging.stg_shopify__orders
          GROUP BY 1
          ORDER BY 1
      database: 2
    visualization_settings: {}
    position:
      row: 0
      col: 0
      size_x: 9
      size_y: 6
```

#### Question

```yaml
name: "Revenue by Month"
description: "Total monthly revenue"
type: "question"
collection: "Shared"
collection_id: 5
created_at: "2026-05-15T14:30:00.000000"
updated_at: "2026-05-15T15:45:00.000000"
display: "bar"
dataset_query:
  type: native
  native:
    query: |
      SELECT DATE_TRUNC('month', order_date) AS month,
             SUM(total) AS revenue
      FROM staging.stg_shopify__orders
      GROUP BY 1
      ORDER BY 1
  database: 2
visualization_settings: {}
```

---

## Loading Dashboards

### Safe Load (Default)

```bash
dango metabase load
```

By default, items that already exist in Metabase are **skipped**:

```
Imported 3 item(s)
  ✓ Sales Overview (4 cards)
  ✓ Revenue by Month
  ✓ Customer Count

Skipped 2 item(s) (already exist):
  ⏭ Data Pipeline Health — Already exists (use --overwrite to replace)
  ⏭ Order Volume — Already exists (use --overwrite to replace)
```

### Dry Run

Preview what would be imported without making changes:

```bash
dango metabase load --dry-run
```

```
Preview (dry-run mode):
  ? Sales Overview (4 cards) — would import
  ? Revenue by Month — would import
  ? Data Pipeline Health — would skip (already exists)
```

### Overwrite Existing

!!! danger "Destructive Operation"
    `--overwrite` replaces existing dashboards and questions in Metabase with versions from the YAML files. Uncommitted Metabase changes will be lost.

```bash
dango metabase load --overwrite
```

The overwrite process:

1. Backs up existing items before replacing
2. Imports new versions from YAML files
3. On failure, **automatically rolls back** — deletes partially imported items and restores backups

```
Imported 5 item(s)
  ✓ Data Pipeline Health (6 cards) — overwrote existing
  ✓ Sales Overview (4 cards) — overwrote existing
  ✓ Revenue by Month — overwrote existing
  ✓ Customer Count — new
  ✓ Order Volume — new
```

---

## Refreshing Schema

After adding new dbt models or running `dango run`, Metabase needs to discover the new tables:

```bash
dango metabase refresh
```

This triggers a Metabase schema sync and updates table metadata:

| Schema | Visibility | Description |
|--------|-----------|-------------|
| `raw_*` | Hidden | Raw source data — not for dashboards |
| `staging` | Visible | Clean, typed data ready for analysis |
| `intermediate` | Visible | Reusable business logic building blocks |
| `marts` | Visible | Pre-built metrics optimized for dashboards |

!!! tip "When to Refresh"
    Run `dango metabase refresh` after:

    - Adding new dbt models
    - Running `dango run` (which creates new tables/schemas)
    - Adding a new data source with `dango sync`

Raw schemas (`raw_*`) are hidden from the Metabase browse UI but remain accessible via SQL queries. This keeps the schema browser clean while preserving full access for advanced users.

---

## Version Control Workflow

### Team Workflow

```bash
# Developer A: makes dashboard changes
dango metabase save
git add metabase/
git commit -m "Add revenue breakdown dashboard"
git push

# Developer B: gets the changes
git pull
dango metabase load
```

### Environment Promotion

Move dashboards from development to production:

```bash
# On dev environment
dango metabase save
git add metabase/
git commit -m "Dashboard ready for production"
git push

# On production environment
git pull
dango metabase load --overwrite
```

!!! note "Database IDs"
    YAML files reference Metabase database IDs (e.g., `database: 2`). If your production Metabase has a different database ID than development, you may need to update these references in the YAML files before loading.

### Restoring Dashboards

If someone accidentally modifies a dashboard in Metabase:

```bash
# Restore from the last saved version
dango metabase load --overwrite
```

Or restore from a specific git commit:

```bash
git checkout abc123 -- metabase/
dango metabase load --overwrite
```

---

## Troubleshooting

### No Shared Collection

```
No items found in collection "Shared".
```

The Shared collection is created automatically during `dango start`. If it's missing:

1. Open Metabase admin: **Admin > Collections**
2. Create a collection named "Shared"
3. Move your dashboards into it
4. Re-run `dango metabase save`

### Missing metabase/ Directory

```
Error: No metabase/ directory found.
```

No dashboards have been saved yet. Run `dango metabase save` first to create the export directory.

### Validation Failures on Load

```
Error: Validation failed for dashboards/sales_overview.yml
```

The YAML file may be malformed or reference invalid data. Check:

- YAML syntax is valid
- Required fields (`name`, `dataset_query`) are present
- Database IDs match your Metabase instance

### Metabase Not Running

```
Error: Could not connect to Metabase at http://localhost:3000
```

Start Metabase first:

```bash
dango start
```

Then wait for Metabase to become healthy before running save/load commands.

---

## Next Steps

<div class="grid cards" markdown>

-   **[Dashboard Provisioning](provisioning.md)**

    Auto-create a pipeline health dashboard with one command.

-   **[Creating Dashboards](creating-dashboards.md)**

    Build custom dashboards from scratch in Metabase.

-   **[Metabase Overview](metabase-overview.md)**

    Understand how Dango integrates with Metabase.

-   **[SQL Queries](sql-queries.md)**

    Write native SQL queries against DuckDB in Metabase.

</div>
