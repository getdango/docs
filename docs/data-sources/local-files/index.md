# Local Files

Load CSV, JSON, JSONL, NDJSON, and Parquet files from your local filesystem into DuckDB.

---

## Quick Start

```bash
# 1. Add a file import source via the wizard
dango source add
# Select "File Import (CSV, JSON, Parquet)" and follow prompts

# 2. Copy your files into the source directory
cp customers.csv data/uploads/my_files/

# 3. Sync
dango sync my_files
```

That's it. Dango detects new files, infers the schema, and loads them into DuckDB.

---

## Supported Formats

| Extension | Format | DuckDB Reader |
|-----------|--------|---------------|
| `.csv` | Comma-separated values | `read_csv_auto` |
| `.json` | JSON (array of objects) | `read_json_auto` |
| `.jsonl` | JSON Lines (one object per line) | `read_json_auto` |
| `.ndjson` | Newline-delimited JSON | `read_json_auto` |
| `.parquet` | Apache Parquet (columnar) | `read_parquet` |

DuckDB's `auto` readers handle delimiter detection, type inference, and header detection automatically. No format configuration needed in most cases.

!!! tip "Mixed formats"
    A single source can contain files of different formats. Dango reads each file with the appropriate reader based on its extension. All files load into the same source schema.

---

## Directory Setup

When you add a `local_files` source, Dango creates a directory for your files:

```
your-project/
├── data/
│   └── uploads/
│       └── my_source/        ← Drop files here
│           ├── customers.csv
│           ├── orders.json
│           └── products.parquet
├── .dango/
│   └── sources.yml
└── warehouse.duckdb
```

The default directory is `data/uploads/{source_name}/`. You can specify a custom path during wizard setup or in `sources.yml`:

```yaml
sources:
  - name: external_data
    type: local_files
    local_files:
      directory: /path/to/shared/drive/exports
      file_pattern: "*.csv"
```

---

## File Pattern Matching

Control which files are loaded using glob patterns:

| Pattern | Matches |
|---------|---------|
| `*` | All supported files (default) |
| `*.csv` | Only CSV files |
| `*.json` | Only JSON files |
| `sales_*.csv` | CSV files starting with "sales_" |
| `2026-*.parquet` | Parquet files starting with "2026-" |

```yaml
sources:
  - name: sales_reports
    type: local_files
    local_files:
      directory: data/uploads/sales_reports
      file_pattern: "sales_*.csv"
```

Files that don't match the pattern are ignored during sync.

---

## How Loading Works

### File Classification

On each sync, Dango compares the current files in the directory against its metadata table and classifies each file:

| Classification | Condition | Action |
|---------------|-----------|--------|
| **New** | File not seen before | Load into DuckDB |
| **Updated** | File modification time changed | Reload (replace previous data) |
| **Unchanged** | File modification time matches | Skip (no action) |
| **Deleted** | File was loaded but no longer on disk | Soft-delete (mark `_dango_deleted = true`) |

This classification makes incremental syncs fast — only new and updated files are processed.

### Metadata Tracking

Dango maintains a `_dango_file_metadata` table in DuckDB that tracks every loaded file:

| Column | Type | Description |
|--------|------|-------------|
| `source_name` | VARCHAR | Source identifier |
| `file_path` | VARCHAR | Full path to the file |
| `file_size` | BIGINT | File size in bytes |
| `file_mtime` | TIMESTAMP | File modification timestamp |
| `rows_loaded` | BIGINT | Number of rows loaded |
| `status` | VARCHAR | `loaded`, `updated`, or `deleted` |
| `loaded_at` | TIMESTAMP | When the file was processed |
| `error_message` | VARCHAR | Error description (if load failed) |

Query the metadata table to see what files have been loaded:

```sql
SELECT file_path, rows_loaded, status, loaded_at
FROM _dango_file_metadata
WHERE source_name = 'my_files'
ORDER BY loaded_at DESC;
```

### Metadata Columns

Every loaded record gets four tracking columns appended:

| Column | Type | Description |
|--------|------|-------------|
| `_dango_filename` | VARCHAR | Name of the source file (e.g., `customers.csv`) |
| `_dango_file_mtime` | TIMESTAMP | File modification time when loaded |
| `_dango_loaded_at` | TIMESTAMP | When the record was loaded into DuckDB |
| `_dango_deleted` | BOOLEAN | `true` if the source file was deleted from disk |

These columns let you trace any record back to its source file and know when it was loaded.

---

## Schema Handling

### Default: Strict Mode

By default, the schema is fixed on first load. If a subsequent file has different columns (new columns, missing columns, or type changes), the sync fails with a schema mismatch error. This prevents accidental data corruption from malformed files.

### Schema Evolution

Use the `--allow-schema-changes` flag to allow column additions:

```bash
dango sync my_files --allow-schema-changes
```

When enabled:

- **New columns** are added to the table (existing rows get NULL for the new column)
- **Missing columns** in new files are loaded as NULL
- **Type changes** still cause an error (e.g., a column changing from INTEGER to VARCHAR)

!!! warning "Schema evolution is per-sync"
    The `--allow-schema-changes` flag applies to the current sync only. Each sync that might encounter new columns needs the flag. This is intentional — schema changes should be a conscious decision.

---

## Configuration Reference

Full `sources.yml` configuration for a `local_files` source:

```yaml
sources:
  - name: my_files                    # Required: unique source name
    type: local_files                 # Required: source type
    enabled: true                     # Optional: toggle sync (default: true)
    description: "Monthly CSV exports from finance team"  # Optional

    local_files:
      directory: data/uploads/my_files  # Required: path to files
      file_pattern: "*"                 # Optional: glob pattern (default: "*")

    deduplication: none               # Optional: none | latest_only | append_only | scd_type2
```

### Key Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `directory` | Yes | `data/uploads/{name}` | Directory containing files to load |
| `file_pattern` | No | `*` | Glob pattern to filter files |
| `deduplication` | No | `none` | Deduplication strategy (see [Deduplication](../deduplication.md)) |

---

## Full Refresh

To reload all files from scratch (ignoring metadata state):

```bash
dango sync my_files --full-refresh
```

This clears the metadata table for the source and reloads every file in the directory. Use this when:

- You've manually edited files that were already loaded
- The metadata table is out of sync with actual file state
- You want to recompute `_dango_loaded_at` timestamps

---

## Verification

After syncing, verify your data loaded correctly:

```bash
# Check source status
dango source list

# Query the loaded data
dango db query "SELECT count(*) FROM raw_my_files.customers"

# Check file metadata
dango db query "SELECT * FROM _dango_file_metadata WHERE source_name = 'my_files'"
```

Or open Metabase and browse the `raw_my_files` schema.

---

## Troubleshooting

### "Unsupported file format: .xlsx"

Dango supports `.csv`, `.json`, `.jsonl`, `.ndjson`, and `.parquet` only. Export Excel files to CSV first:

- In Excel: File > Save As > CSV UTF-8
- Or use a command-line tool: `xlsx2csv input.xlsx output.csv`

### "Schema mismatch" error

A file has different columns than previously loaded files. Options:

1. **Fix the file** — ensure all files have consistent columns
2. **Allow schema changes** — `dango sync my_files --allow-schema-changes`
3. **Full refresh** — `dango sync my_files --full-refresh` to reload with the new schema

### "No files found matching pattern"

- Check that the directory path in `sources.yml` is correct
- Verify files exist: `ls data/uploads/my_source/`
- Check the `file_pattern` — `*.csv` won't match `.json` files
- Ensure files have a supported extension

### Files not loading on re-sync

If you copied files but they're classified as "unchanged":

- Dango uses file modification time (`mtime`) to detect changes
- Simply copying a file may preserve the original `mtime`
- Touch the file to update its timestamp: `touch data/uploads/my_source/file.csv`
- Or use `--full-refresh` to reload everything

---

## Related Pages

- [Adding Sources](../adding-sources.md) — wizard walkthrough for all source types
- [Source Catalog](../source-catalog.md) — complete list of all 33 sources
- [Sync Modes](../sync-modes.md) — incremental, full refresh, and date range options
- [Deduplication](../deduplication.md) — strategies for handling duplicate records
