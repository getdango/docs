# Source & Sync

Add, manage, and sync data sources from the command line.

---

## Overview

The `dango source` commands manage your data source configurations, while `dango sync` loads data from those sources into your DuckDB warehouse.

**Commands covered on this page:**

- `dango source add` — Add a data source (interactive wizard)
- `dango source list` — List configured sources
- `dango source remove` — Remove a source
- `dango source edit` — Open config in editor
- `dango sync` — Load data from sources

---

## Adding Sources

### dango source add

Launch the interactive source wizard.

```bash
dango source add
```

The wizard supports 27+ sources across 9 categories:

| Category | Sources |
|----------|---------|
| Marketing & Analytics | Facebook Ads, Google Ads, Google Sheets, Google Analytics, and more |
| Business & CRM | HubSpot, Salesforce, Zendesk, Jira, and more |
| E-commerce & Payment | Stripe |
| Files & Storage | Notion, Email Inbox |
| Databases | MongoDB |
| Streaming | Kafka, Kinesis |
| Development | GitHub |
| Communication | Slack |
| Local & Custom | CSV, REST API |

**Wizard flow:**

1. Select source type from the categorized list
2. Provide a unique source name
3. Configure credentials (environment variable or secrets file)
4. Select resources/tables to sync
5. Set start date for incremental loading
6. Test connection (automatic)
7. Save configuration

```
Select source type:
  1. CSV files
  2. dlt Native (advanced)
  3. REST API
  4. Google Sheets
  ...

Source name (unique identifier): stripe_payments
API Key stored in environment variable: STRIPE_API_KEY
Start date (YYYY-MM-DD) [2024-01-01]: 2024-06-01

Testing connection...
✓ Connected to Stripe API
✓ Source added to .dango/sources.yml
```

!!! tip
    After adding a source, run `dango sync <source_name>` to load data, then `dango generate` to create staging models.

---

## Listing Sources

### dango source list

List all configured data sources with their status and last sync time.

```bash
dango source list [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--enabled-only` | Show only enabled sources |

**Example:**

```bash
dango source list
```

```
Configured Sources:

  ● stripe_payments (stripe) - Enabled
      Last synced: 2024-12-09 12:34:56
      Tables: charges, customers, subscriptions

  ● orders_csv (csv) - Enabled
      Last synced: 2024-12-08 18:45:12
      File: data/orders.csv

  ○ old_hubspot (hubspot) - Disabled
      Last synced: 2024-12-04 14:22:10
```

**Filter to enabled only:**

```bash
dango source list --enabled-only
```

---

## Removing Sources

### dango source remove

Remove a data source from configuration.

```bash
dango source remove SOURCE_NAME [OPTIONS]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `SOURCE_NAME` | positional, required | Name of source to remove |
| `-y`, `--yes` | flag | Skip confirmation prompt |

```bash
dango source remove my_csv
dango source remove my_csv --yes
```

!!! warning
    This removes the source from `.dango/sources.yml`. It does **not** delete data already loaded into DuckDB. Use `dango db clean` to remove orphaned tables.

---

## Editing Sources

### dango source edit

Open `sources.yml` in your default editor (`$EDITOR`).

```bash
dango source edit [NAME]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `NAME` | positional, optional | Hints at the section to focus on |

```bash
dango source edit              # Edit full sources.yml
dango source edit chess         # Edit with focus hint
```

!!! tip
    Set the `EDITOR` environment variable to your preferred editor: `export EDITOR=vim`

---

## Syncing Data

!!! tip "Web UI alternative"
    You can also trigger syncs from the **Sources** page in the Web UI. Navigate to `http://localhost:8800/sources` and click **Sync Now** on any source. See [Web UI — Sources](../web-ui/sources.md).

### dango sync

Load data from all sources (or a specific source) into DuckDB.

```bash
dango sync [SOURCE_NAME] [OPTIONS]
```

**Arguments:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `SOURCE_NAME` | positional, optional | Sync only this source |

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--source TEXT` | deprecated | Use positional `SOURCE_NAME` instead |
| `--since TEXT` | date | Start date for incremental loading (YYYY-MM-DD) |
| `--until TEXT` | date | End date for incremental loading (YYYY-MM-DD) |
| `--backfill TEXT` | duration | Backfill duration (e.g. `7d`, `2w`, `1m`) |
| `--limit INTEGER` | number | Limit rows per source (dev testing) |
| `--full-refresh` | flag | Drop existing data and reload from scratch |
| `--dry-run` | flag | Show what would be synced without executing |
| `--allow-schema-changes` | flag | Allow CSV schema changes (add columns, NULL for missing) |
| `-y`, `--yes` | flag | Skip confirmation prompts |

**What happens during sync:**

1. Reads `.dango/sources.yml` for enabled sources
2. For each source: connects, fetches data (incremental or full), writes to DuckDB raw layer
3. Updates metadata (`_dlt_loads` table)
4. Logs progress and results

### Sync All Sources

```bash
dango sync
```

### Sync Specific Source

```bash
dango sync stripe_payments
```

### Incremental Loading

By default, syncs use incremental loading — only fetching new data since the last sync. Override the start date:

```bash
dango sync --since 2024-01-01
dango sync --until 2024-06-30
dango sync --since 2024-01-01 --until 2024-06-30
```

### Backfill

Backfill a relative time range:

```bash
dango sync --backfill 7d      # Last 7 days
dango sync --backfill 2w      # Last 2 weeks
dango sync --backfill 1m      # Last 1 month
```

### Full Refresh

Drop all existing data for the source and reload from scratch:

```bash
dango sync --full-refresh
```

!!! warning
    Full refresh deletes existing data before reloading. For large sources, this can take significant time and API quota.

### Dev Mode

Limit rows per source for quick testing:

```bash
dango sync --limit 1000
```

### Dry Run

Preview what would be synced without executing:

```bash
dango sync --dry-run
```

### CSV Schema Changes

Allow schema changes when syncing CSV files (new columns added, missing columns treated as NULL):

```bash
dango sync --allow-schema-changes
```

---

## Common Workflows

### Initial Setup

```bash
# Add a source
dango source add

# Sync data
dango sync stripe_payments

# Generate staging models
dango generate --all

# Run transformations
dango run
```

### Daily Operations

```bash
# Sync all sources and run transformations
dango sync && dango run

# Sync with backfill for missed data
dango sync --backfill 3d && dango run
```

### Schema Changes

When a source adds new columns:

```bash
# For CSV: allow new columns
dango sync my_csv --allow-schema-changes

# Regenerate staging models to pick up new columns
dango generate --all
```

---

## Troubleshooting

??? info "Sync fails with connection error"
    Check that credentials are correctly set in your environment or `.dlt/secrets.toml`. Run `dango oauth check` for OAuth sources or verify API keys are exported.

??? info "Sync is slow"
    Use `--limit` for development. For production, ensure incremental loading is configured (check `start_date` in source config). Avoid `--full-refresh` unless necessary.

??? info "Orphaned tables after removing a source"
    Run `dango db status` to see orphaned tables, then `dango db clean` to remove them.

??? info "CSV schema changed"
    Use `--allow-schema-changes` to handle added/removed columns. New columns get NULL for historical rows; removed columns keep existing data.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [Transform & Model](transform-model.md) — dbt transformations after syncing
- [Schedule Commands](schedule-commands.md) — Automate sync schedules
- [OAuth Commands](oauth-commands.md) — Set up OAuth for Google/Facebook sources
