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

## Quick Start

### Via Web UI (Recommended)

1. Start the Dango platform:
   ```bash
   dango start
   ```

2. Open Web UI at `http://localhost:8800`

3. Click **"Add Source"** → **"CSV"**

4. Upload your CSV file or enter the file path

5. Configure options (delimiter, header row, etc.)

6. Click **"Save"**

7. Run `dango sync` to load the data

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
      file_path: data/sales.csv
      delimiter: ","
      header: true
      watch: true
```

Then sync:

```bash
dango sync --source sales_data
```

---

## Configuration Options

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Unique identifier for this source | `sales_data` |
| `type` | Must be `csv` | `csv` |
| `csv.file_path` | Path to CSV file (absolute or relative to project root) | `data/sales.csv` |

### Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `true` | Whether this source is active |
| `description` | `""` | Human-readable description |
| `csv.delimiter` | `","` | Field separator (`,`, `\t`, `|`, etc.) |
| `csv.header` | `true` | First row contains column names |
| `csv.watch` | `false` | Auto-sync when file changes |
| `csv.encoding` | `"utf-8"` | File encoding |

---

## Complete Example

### sources.yml

```yaml
version: '1.0'
sources:
  # Standard CSV with auto-sync
  - name: customer_data
    type: csv
    enabled: true
    description: Customer master data
    csv:
      file_path: data/customers.csv
      delimiter: ","
      header: true
      watch: true

  # Tab-delimited file
  - name: product_catalog
    type: csv
    enabled: true
    description: Product SKU catalog
    csv:
      file_path: data/products.tsv
      delimiter: "\t"
      header: true
      watch: false

  # Pipe-delimited file without headers
  - name: legacy_transactions
    type: csv
    enabled: true
    description: Legacy transaction log
    csv:
      file_path: data/legacy.psv
      delimiter: "|"
      header: false
      watch: false
```

### File Structure

```
my-dango-project/
├── .dango/
│   └── sources.yml
├── data/
│   ├── customers.csv       # File path references start from here
│   ├── products.tsv
│   └── legacy.psv
└── dbt/
```

---

## File Watcher (Auto-Sync)

When `watch: true` is enabled, Dango monitors the CSV file and automatically triggers a sync when changes are detected.

### Enable File Watcher

In `.dango/config.toml`:

```toml
[pipeline]
auto_sync = true
```

Or when starting the platform:

```bash
dango start --auto-sync
```

### How It Works

1. File watcher monitors CSV files with `watch: true`
2. When file is modified, triggers `dango sync --source <name>`
3. New data is loaded into DuckDB
4. dbt transformations run automatically (if configured)

### Use Cases

- **Live data feeds**: CSV files updated by external scripts
- **Development**: Edit CSV files and see results immediately in Metabase
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

Data is loaded into the `raw` schema:

```
raw.<source_name>
```

Example:
```sql
-- source name: sales_data
-- target table: raw.sales_data
SELECT * FROM raw.sales_data LIMIT 10;
```

---

## Common Patterns

### Monthly Data Updates

```yaml
- name: monthly_financials
  type: csv
  enabled: true
  description: Monthly P&L data
  csv:
    file_path: data/financials/2024-12.csv
    delimiter: ","
    header: true
    watch: false
```

Update workflow:
```bash
# Replace CSV file with new month
cp financials-2025-01.csv data/financials/2024-12.csv

# Sync to reload
dango sync --source monthly_financials
```

### Multiple Related Files

```yaml
# Option 1: Separate sources (separate tables)
- name: sales_north
  type: csv
  csv:
    file_path: data/regions/north.csv

- name: sales_south
  type: csv
  csv:
    file_path: data/regions/south.csv

# Option 2: Combine in dbt intermediate layer
# See Transformations section for union patterns
```

### Excel Exports

Export Excel to CSV first:

```bash
# Using pandas (install first: pip install pandas openpyxl)
python << EOF
import pandas as pd
df = pd.read_excel('data/report.xlsx', sheet_name='Sales')
df.to_csv('data/sales.csv', index=False)
EOF

# Then configure as CSV source
dango sync --source sales
```

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

**Solution**: Specify encoding in sources.yml:

```yaml
csv:
  file_path: data/latin1.csv
  encoding: "latin-1"  # or "iso-8859-1", "cp1252", etc.
```

### File Not Found

**Problem**: `FileNotFoundError: data/sales.csv`

**Solution**: File paths are relative to project root (where `.dango/` is). Use:

```bash
ls data/sales.csv  # Verify file exists
```

Or use absolute path:

```yaml
csv:
  file_path: /Users/yourname/data/sales.csv
```

### File Watcher Not Triggering

**Problem**: File changes but sync doesn't run

**Solution**: Check that:

1. `auto_sync: true` in `.dango/config.toml`
2. `watch: true` in source configuration
3. Platform is running (`dango start`)
4. File path is correct

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
# Good
file_path: data/sales.csv

# Avoid
file_path: /Users/john/Desktop/sales.csv
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
