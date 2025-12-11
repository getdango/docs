# CSV Files

Upload and sync CSV files into your data warehouse.

---

## Overview

CSV sources in Dango provide a simple way to load flat files into DuckDB with automatic schema detection and file watching capabilities.

**Key Features**:

- Automatic schema detection
- File watcher with auto-sync on changes
- Manual and scheduled sync
- Support for multiple delimiters
- Header row handling

---

## How CSV Loading Works

**Core behavior**: All files matching your `file_pattern` in the directory are **combined (UNION)** into a single table. This happens on every sync.

This simple design supports two common workflows:

### Workflow 1: Accumulate Data Over Time

Add new files to the directory and all rows combine automatically.

```
data/uploads/sales/
├── sales_2024_01.csv    # 1,000 rows
├── sales_2024_02.csv    # 1,200 rows
└── sales_2024_03.csv    # 1,100 rows
                         # ─────────────
                         # Table: 3,300 rows (all combined)
```

**Use cases**: Monthly exports, daily transaction logs, regional data files

### Workflow 2: Replace with Latest Data

Keep only one file in the directory. Replace it when you have new data.

```
data/uploads/inventory/
└── current_inventory.csv    # Latest snapshot only
```

To update: delete the old file, copy in the new one, sync.

**Use cases**: Product catalogs, price lists, reference data, point-in-time snapshots

!!! tip "Choose your workflow"
    - **Growing data?** → Add files, let them accumulate
    - **Reference data?** → Replace the single file each time

---

## Quick Start

### Via Wizard (Recommended)

```bash
dango source add
# Select "CSV Files"
# Enter source name (e.g., "sales_data")
# Confirm directory (default: data/uploads/sales_data)
# Confirm file pattern (default: *.csv)
```

The wizard creates the directory and configuration for you.

### Via Web UI

1. Start the platform: `dango start`
2. Open Web UI at `http://localhost:8800`
3. Click **"Add Source"** → **"CSV"**
4. Follow the prompts
5. Upload files via the Web UI

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: sales_data
    type: csv
    enabled: true
    description: Monthly sales transactions
    csv:
      directory: data/uploads/sales_data
      file_pattern: "*.csv"
```

Then copy files and sync:

```bash
# Create directory if needed
mkdir -p data/uploads/sales_data

# Copy your CSV files
cp my_sales.csv data/uploads/sales_data/

# Sync
dango sync --source sales_data
```

---

## Configuration Options

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Unique identifier for this source | `sales_data` |
| `type` | Must be `csv` | `csv` |
| `csv.directory` | Directory containing CSV files | `data/uploads/sales_data` |
| `csv.file_pattern` | Glob pattern for files to load | `*.csv`, `orders_*.csv` |

### Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Whether this source is active |
| `description` | `""` | Human-readable description |
| `csv.notes` | `null` | Notes on how to refresh this data |

!!! note "Auto-detected settings"
    The following are NOT configurable - they are auto-detected by DuckDB:

    - **Delimiter** - Auto-detected (comma, tab, pipe, etc.)
    - **Header** - Assumed true (first row = column names)
    - **Encoding** - Assumed UTF-8
    - **Data types** - Inferred from first ~1000 rows

---

## Complete Example

### sources.yml

```yaml
version: '1.0'
sources:
  # Sales data - multiple CSV files in one directory
  - name: sales_data
    type: csv
    enabled: true
    description: Monthly sales transactions
    csv:
      directory: data/uploads/sales_data
      file_pattern: "*.csv"
      notes: "Export from POS system monthly"

  # Customer data - specific file pattern
  - name: customers
    type: csv
    enabled: true
    description: Customer master data
    csv:
      directory: data/uploads/customers
      file_pattern: "customer_*.csv"

  # Product catalog
  - name: products
    type: csv
    enabled: true
    description: Product SKU catalog
    csv:
      directory: data/uploads/products
      file_pattern: "*.csv"
```

### File Structure

Each CSV source has its own directory:

```
my-dango-project/
├── .dango/
│   └── sources.yml
├── data/
│   └── uploads/
│       ├── sales_data/           # Source: sales_data
│       │   ├── sales_2024_01.csv
│       │   ├── sales_2024_02.csv
│       │   └── sales_2024_03.csv
│       ├── customers/            # Source: customers
│       │   └── customer_list.csv
│       └── products/             # Source: products
│           └── catalog.csv
└── dbt/
```

All files matching the `file_pattern` in a source's directory are combined into one table.

---

## File Watcher (Auto-Sync)

When auto-sync is enabled in your project configuration, Dango monitors CSV directories and automatically triggers sync when files change.

### Enable Auto-Sync

In `.dango/project.yml`:

```yaml
platform:
  auto_sync: true
  debounce_seconds: 600  # Wait 10 min before triggering
```

!!! note
    Auto-sync is a platform configuration setting, not a CLI flag or per-source setting.

### How It Works

1. Start platform: `dango start`
2. File watcher monitors all CSV source directories
3. When files are added or modified, sync triggers after debounce period
4. Data is loaded into DuckDB
5. Staging models are regenerated

### Use Cases

- **Live data feeds**: CSV files updated by external scripts
- **Development**: Edit CSV files and see results in Metabase
- **Manual exports**: Drop in new CSV files and have them auto-load

---

## Data Loading Behavior

### Schema Detection

Dango uses DuckDB's automatic CSV parsing:

- **Column names**: From header row (if `header: true`)
- **Data types**: Inferred from first 1000 rows
- **Null handling**: Empty values treated as NULL

### Write Disposition

CSV sources use **replace** disposition by default:

- Full table refresh on each sync
- Previous data is dropped
- Suitable for master data files (customers, products, etc.)

For append-only behavior (logs, events), use a custom dlt source instead.

### Target Schema

Data is loaded into a source-specific schema:

```
raw_{source_name}.{source_name}
```

Example:
```sql
-- source name: sales_data
-- target table: raw_sales_data.sales_data
SELECT * FROM raw_sales_data.sales_data LIMIT 10;
```

!!! note
    All files matching the `file_pattern` are combined into a single table named after the source.

### Schema Detection

CSV schema (column names and types) is **fixed on first load**:

- **First sync**: DuckDB analyzes file headers and infers types from first ~1000 rows
- **Subsequent syncs**: Schema must match the original

**If your CSV schema changes** (columns added/removed/renamed):

1. Sync will fail with a schema mismatch error
2. To fix: Remove and re-add the source

```bash
# Remove old source
dango source remove sales_data

# Re-add with same name (schema will be re-detected)
dango source add
# Select "CSV Files", use same name
```

!!! warning
    Schema changes require re-creating the source. Plan your CSV structure before initial load.

---

## Common Patterns

### Accumulating Monthly Data (Workflow 1)

Keep adding files each month - all data combines automatically:

```yaml
- name: monthly_sales
  type: csv
  enabled: true
  description: Monthly sales exports - all months combined
  csv:
    directory: data/uploads/monthly_sales
    file_pattern: "*.csv"
    notes: "Add new monthly export file, keep previous months"
```

```
data/uploads/monthly_sales/
├── sales_2024_01.csv    # January data
├── sales_2024_02.csv    # February data
├── sales_2024_03.csv    # March data
└── sales_2024_04.csv    # April data (just added)
```

**Workflow**: Each month, export your data and copy the new file into the directory:
```bash
# Add new month's file (don't delete old ones)
cp sales_2024_05.csv data/uploads/monthly_sales/

# Sync - table now contains Jan through May
dango sync --source monthly_sales
```

The table `raw_monthly_sales.monthly_sales` contains all rows from all months.

### Reference Data Replacement (Workflow 2)

Keep only the latest version - replace the file each time:

```yaml
- name: product_catalog
  type: csv
  enabled: true
  description: Current product catalog
  csv:
    directory: data/uploads/product_catalog
    file_pattern: "*.csv"
    notes: "Replace with latest export from inventory system"
```

```
data/uploads/product_catalog/
└── products.csv    # Current catalog only
```

**Workflow**: Replace the file when you have updated data:
```bash
# Remove old file, add new one
rm data/uploads/product_catalog/products.csv
cp new_products_export.csv data/uploads/product_catalog/products.csv

# Sync - table reflects only the new file
dango sync --source product_catalog
```

### Regional/Category Files (Combined)

Multiple files representing different segments, all combined:

```yaml
- name: regional_sales
  type: csv
  csv:
    directory: data/uploads/regional_sales
    file_pattern: "*.csv"
```

```
data/uploads/regional_sales/
├── north.csv
├── south.csv
├── east.csv
└── west.csv
```

All four files are loaded into `raw_regional_sales.regional_sales`. Add a new region by adding a file.

### Separate Tables per Category

If you need separate tables instead of combined, use separate sources:

```yaml
- name: sales_north
  type: csv
  csv:
    directory: data/uploads/sales_north
    file_pattern: "*.csv"

- name: sales_south
  type: csv
  csv:
    directory: data/uploads/sales_south
    file_pattern: "*.csv"
```

Then combine in dbt if needed (see Transformations section).

### Excel Files

Dango does not currently support Excel files (.xlsx) directly.

**Workaround**: Export to CSV from Excel:

1. Open your Excel file
2. File → Save As → CSV (Comma delimited)
3. Save to your source's directory

```bash
# Example: save to sales_data directory
# Then sync
dango sync --source sales_data
```

!!! tip "Future support"
    Native Excel support may be added in a future version.

---

## Troubleshooting

### Schema Detection Errors

**Problem**: Incorrect data types inferred

**Solution**: Check first 1000 rows. DuckDB infers types from this sample. If later rows have different types, you may need to:

1. Clean the CSV file
2. Create a dbt staging model with explicit casting
3. Use a custom dlt source for complex parsing

### Encoding Issues

**Problem**: Special characters display incorrectly

**Solution**: DuckDB auto-detects encoding but assumes UTF-8 by default. If special characters display incorrectly:

1. Convert your CSV file to UTF-8 before uploading
2. Use a text editor or command-line tool:

```bash
# Convert from latin-1 to UTF-8
iconv -f ISO-8859-1 -t UTF-8 original.csv > converted.csv
```

3. Move the converted file to your source directory

### Directory Not Found

**Problem**: `FileNotFoundError` or no files synced

**Solution**: Directory paths are relative to project root (where `.dango/` is). Verify:

```bash
# Check directory exists
ls data/uploads/sales_data/

# Check files match pattern
ls data/uploads/sales_data/*.csv
```

Ensure your `sources.yml` directory matches the actual location:

```yaml
csv:
  directory: data/uploads/sales_data  # Must exist
  file_pattern: "*.csv"               # Must match files
```

### File Watcher Not Triggering

**Problem**: File changes but sync doesn't run

**Solution**: Check that:

1. `auto_sync: true` in `.dango/project.yml` under `platform:`
2. Platform is running (`dango start`)
3. Directory path is correct and accessible
4. Files match the `file_pattern` glob

Note: Auto-sync has a debounce period (default 10 minutes) to avoid rapid repeated syncs.

---

## Best Practices

### 1. Use Consistent Delimiters

Stick to standard formats:
- **CSV**: Comma-delimited (`.csv`)
- **TSV**: Tab-delimited (`.tsv`)
- **PSV**: Pipe-delimited (`.psv`)

### 2. Always Include Headers

Makes data self-documenting and easier to work with in dbt/Metabase.

### 3. Validate Data Before Uploading

Check for:
- Consistent column counts
- Proper escaping of quotes
- No binary data in text fields

### 4. Use Relative Paths

Keeps configuration portable across environments:

```yaml
# Good - relative to project root
csv:
  directory: data/uploads/sales_data

# Avoid - absolute paths break portability
csv:
  directory: /Users/john/Desktop/sales_data
```

### 5. Version Your CSV Files

For important data, use Git LFS or date-based naming:

```
data/
├── customers-2024-12-01.csv
├── customers-2024-12-08.csv
└── customers.csv  -> symlink to latest
```

---

## Comparison: CSV vs. Other Sources

| Feature | CSV | Built-in dlt | Custom dlt |
|---------|-----|--------------|------------|
| Setup complexity | Lowest | Low | Medium |
| Real-time data | No (file-based) | Yes (API) | Yes (API) |
| Schema evolution | Manual | Automatic | Automatic |
| Incremental loading | No | Yes | Yes |
| Best for | Static data, exports | SaaS APIs | Custom APIs |

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - Connect to cloud services
- **[Custom Sources](custom-sources.md)** - Build your own integrations
- **[Transformations](../transformations/index.md)** - Clean and model your CSV data
- **[Dashboards](../dashboards/index.md)** - Visualize CSV data in Metabase
