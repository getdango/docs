# Sync Modes

Understand how Dango loads data from your sources — incremental by default, with full refresh and date range options when you need them.

---

## Overview

Dango supports three sync modes that control how data is fetched from sources and loaded into DuckDB:

| Mode | Command | Behavior | Use Case |
|------|---------|----------|----------|
| **Incremental** | `dango sync` | Load only new/changed data since last sync | Daily operations (default) |
| **Full Refresh** | `dango sync --full-refresh` | Drop existing data, reload everything | Schema changes, data corruption |
| **Date Range** | `dango sync --since 2026-01-01` | Load data within a specific time window | Backfills, gap filling |

---

## Incremental Sync

Incremental sync is the default mode. It loads only data that has changed since the last successful sync, keeping sync times short and API usage low.

### How It Works

dlt tracks sync state automatically — each pipeline remembers its last cursor position (e.g., the most recent `updated_at` timestamp or page offset). On the next sync, dlt resumes from where it left off.

```bash
# First sync: loads all historical data
dango sync stripe_prod

# Subsequent syncs: loads only new/changed records
dango sync stripe_prod
```

### Lookback Window

Some sources support a **lookback window** that re-fetches recent data to catch late-arriving records. For example, Google Ads attribution data can update for up to 30 days after the initial event.

When a source has `lookback_days` configured in the registry, incremental syncs automatically extend the fetch window back by that many days. This is handled transparently — no configuration needed.

### Local File Incremental

For `local_files` sources, incremental sync uses **file metadata tracking** instead of API cursors:

1. Dango maintains a `_dango_file_metadata` table tracking every loaded file
2. On each sync, files are classified as **new**, **updated**, **unchanged**, or **deleted**
3. Only new and updated files are loaded
4. Deleted files are soft-deleted (marked with `_dango_deleted = true`)

See [Local Files](local-files/index.md) for details.

---

## Full Refresh

Full refresh drops all existing data for a source and reloads everything from scratch. Use this when incremental state becomes invalid.

```bash
# Full refresh with confirmation prompt
dango sync sales_data --full-refresh

# Skip confirmation
dango sync sales_data --full-refresh --yes
```

### Safety Guard Rails

Full refresh includes several protections:

1. **Confirmation prompt** — requires explicit confirmation before proceeding (bypass with `--yes`)
2. **State backup** — dlt pipeline state is backed up before the refresh starts
3. **Row count anomaly detection** — if the refreshed data has significantly fewer rows than before, Dango warns you and keeps the state backup for recovery
4. **Automatic restore on failure** — if the sync fails mid-refresh, the backed-up state is restored so subsequent incremental syncs work correctly

!!! warning "Full refresh reloads all data"
    For large sources (e.g., Stripe with years of transaction history), a full refresh may take significantly longer than an incremental sync and consume more API quota. Use `--dry-run` first to see what would happen.

### Write Disposition

Some dlt sources always use `replace` write disposition internally — meaning every sync is effectively a full refresh regardless of the `--full-refresh` flag. Dango detects this automatically and notes it in the sync output.

Sources known to use `replace` mode include Stripe, Jira, Asana, Airtable, Notion, and GitHub. For these sources, incremental behavior comes from dlt's state tracking (fetching only new pages), not from the write disposition.

---

## Date Range Sync

Date range sync lets you load data for a specific time period. This is useful for backfills, gap filling, and testing.

### Flags

| Flag | Format | Description |
|------|--------|-------------|
| `--since` | `YYYY-MM-DD` | Start date (inclusive) |
| `--until` | `YYYY-MM-DD` | End date (inclusive) |
| `--backfill` | `Nd`, `Nw`, `Nm` | Relative duration from today |

```bash
# Load data from a specific date forward
dango sync ga4_data --since 2026-01-01

# Load a specific date range
dango sync ga4_data --since 2026-01-01 --until 2026-03-31

# Backfill last 30 days
dango sync ga4_data --backfill 30d

# Backfill last 2 weeks
dango sync ga4_data --backfill 2w
```

### Backfill Durations

The `--backfill` flag accepts these suffixes:

| Suffix | Meaning | Example |
|--------|---------|---------|
| `d` | Days | `30d` = last 30 days |
| `w` | Weeks | `2w` = last 14 days |
| `m` | Months | `1m` = last 30 days |

!!! note "Mutual exclusivity"
    `--backfill` cannot be combined with `--since` or `--until`. Use one approach or the other.

### Gap Fill Detection

When you provide a `--since` date earlier than the earliest data in your warehouse, Dango logs a notice indicating a gap fill operation. This helps you track when historical data is being loaded.

---

## CLI Flags Reference

All flags available on `dango sync`:

| Flag | Type | Description |
|------|------|-------------|
| `SOURCE_NAME` | Positional | Sync a specific source (e.g., `dango sync stripe_prod`) |
| `--full-refresh` | Flag | Drop existing data and reload from scratch |
| `--since YYYY-MM-DD` | Option | Start date for date range sync |
| `--until YYYY-MM-DD` | Option | End date for date range sync |
| `--backfill Nd\|Nw\|Nm` | Option | Relative backfill duration |
| `--dry-run` | Flag | Preview what would be synced without executing |
| `--allow-schema-changes` | Flag | Allow schema evolution for file sources (add columns, treat missing as NULL) |
| `--limit N` | Option | Limit rows per source (for development/testing) |
| `--yes` / `-y` | Flag | Skip confirmation prompts |

### Dry Run

Use `--dry-run` to preview a sync without making changes:

```bash
dango sync --dry-run
```

This shows:

- Which sources would be synced
- Sync options (full refresh, date range, row limit)
- Any warnings (disabled sources, missing credentials)

No data is fetched or written.

---

## Single-Writer Lock

DuckDB supports only one writer process at a time. Dango enforces this with a lock file at `.dango/state/dbt.lock`.

When a sync is running:

- Other `dango sync` commands wait up to 5 minutes for the lock (queued)
- The lock is released when the sync completes (success or failure)
- If the process crashes, the stale lock is detected and cleaned up on the next sync

```
$ dango sync orders
⏳ Another sync is running. Waiting for lock (up to 5 minutes)...
✓ Lock acquired. Starting sync.
```

!!! tip "Parallel source syncs"
    Sources within a single `dango sync` run are synced **sequentially** (one at a time) due to the single-writer constraint. To sync faster, sync individual sources in separate terminal sessions — they'll queue automatically.

---

## Troubleshooting

### "Lock file exists" or sync appears stuck

Another sync process holds the lock. Wait for it to complete, or check for a stale lock:

```bash
# Check if a sync is actually running
ps aux | grep "dango sync"

# If no sync is running, the lock is stale — the next sync will clean it up
dango sync my_source
```

### Full refresh loaded fewer rows

Dango detected a potential data loss anomaly. The state backup is preserved at `~/.dlt/pipelines/<pipeline_name>_backup_<timestamp>/`. If the refresh was intentional (e.g., the source API now has less data), no action is needed. If unexpected, investigate the source.

### Date range flags ignored

Not all sources support date range filtering. If a source doesn't accept `start_date`/`end_date` parameters, Dango warns you and proceeds with a normal incremental sync.

### Sync takes much longer than expected

- Check if the source uses `replace` write disposition (every sync reloads all data)
- Use `--limit N` during development to cap row counts
- For API sources, check rate limits in the provider's dashboard

---

## Related Pages

- [Adding Sources](adding-sources.md) — set up a new source and run your first sync
- [Deduplication](deduplication.md) — how duplicate records are handled across strategies
- [Local Files](local-files/index.md) — file-specific sync behavior and metadata tracking
- [DuckDB & Single-Writer](../core-concepts/duckdb.md) — why only one write process is allowed
