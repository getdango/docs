# Validation

Validating configuration and troubleshooting via CLI.

---

## Overview

The `dango validate` command performs comprehensive health checks on your project. Catch configuration errors, missing credentials, and platform issues before they cause sync failures.

**What you'll learn**:

- Validate project configuration
- Check source configurations
- Verify database health
- Test source connections
- Troubleshoot common issues
- Auto-fix problems

---

## Basic Validation

### Validate Everything

Run comprehensive validation:

```bash
dango validate
```

**Checks performed**:

1. **Project configuration** (`.dango/project.yml`)
2. **Source configuration** (`.dango/sources.yml`)
3. **dbt configuration** (`dbt/dbt_project.yml`)
4. **Database accessibility** (`data/warehouse.duckdb`)
5. **Dependencies** (Docker, Python, dbt, dlt)
6. **OAuth credentials** (expiration status)
7. **File paths** (CSV files exist)
8. **Network connectivity** (API endpoints reachable)

**Example output**:

```
Validating Dango project...

[1/8] Project Configuration
      ✓ .dango/project.yml exists
      ✓ Valid YAML syntax
      ✓ Required fields present
      ✓ Port 8800 available

[2/8] Source Configuration
      ✓ .dango/sources.yml exists
      ✓ Valid YAML syntax
      ✓ 5 sources configured
      ✓ No duplicate source names
      ⚠ 1 source disabled (old_hubspot)

[3/8] dbt Configuration
      ✓ dbt/dbt_project.yml exists
      ✓ Valid dbt project
      ✓ DuckDB profile configured
      ✓ 15 models found

[4/8] Database
      ✓ data/warehouse.duckdb exists
      ✓ Database accessible
      ✓ All schemas present (raw, staging, marts)
      ✓ No corruption detected
      ✓ Disk space: 245 GB available

[5/8] Dependencies
      ✓ Python 3.9.18 installed
      ✓ dbt 1.7.4 installed
      ✓ dlt 0.4.2 installed
      ✗ Docker not running (Metabase won't start)

[6/8] OAuth Credentials
      ✓ google_sheets_source valid (expires in 37 days)
      ⚠ google_analytics_source expires in 6 days
      ✗ facebook_ads_source expired 19 days ago

[7/8] File Paths
      ✓ data/sales.csv exists (5,432 rows)
      ✓ data/orders.csv exists (2,341 rows)

[8/8] Network Connectivity
      ✓ Stripe API reachable (125 ms)
      ✓ Google Sheets API reachable (89 ms)
      ⚠ Facebook Ads API slow (1,234 ms)

──────────────────────────────────────────────
Validation complete: 2 errors, 3 warnings

Errors:
  1. Docker daemon not running
     → Start Docker: docker start
     → Or run: dango start --no-metabase

  2. OAuth credentials expired (facebook_ads_source)
     → Re-authenticate: dango auth refresh facebook_ads_source
     → Or disable source: dango source disable facebook_ads_source

Warnings:
  1. OAuth credentials expiring soon (google_analytics_source)
     → Refresh before Dec 15: dango auth refresh google_analytics_source

  2. old_hubspot source disabled
     → Remove if no longer needed: dango source remove old_hubspot

  3. Facebook Ads API responding slowly
     → May indicate rate limiting
     → Consider reducing sync frequency
```

**Exit codes**:

- `0` - No errors (warnings OK)
- `1` - One or more errors found

### Strict Mode

Fail on warnings:

```bash
dango validate --strict
```

**Effect**:

- Warnings treated as errors
- Exit code 1 if any warnings
- Use in CI/CD pipelines

**Example**:

```
Validation complete: 0 errors, 3 warnings

In strict mode, warnings are treated as errors.
Exit code: 1
```

---

## Specific Validations

### Validate Configuration Files

**Project configuration only**:

```bash
dango validate --check config
```

**Output**:

```
Validating configuration files...

✓ .dango/project.yml
  - Valid YAML syntax
  - Required fields: name, created_by
  - Port 8800 available
  - File watcher configured

✓ .dango/sources.yml
  - Valid YAML syntax
  - 5 sources configured
  - No duplicate names
  - All source types valid

✓ dbt/dbt_project.yml
  - Valid dbt project
  - Name: my_analytics
  - Profile: dango
  - Models configured

✓ .dlt/config.toml
  - Valid TOML syntax
  - Runtime settings configured

✓ .dlt/secrets.toml
  - Valid TOML syntax
  - Credentials present for 3 sources
  ⚠ Missing FACEBOOK_ADS_ACCESS_TOKEN

All configuration files valid (1 warning)
```

### Validate Sources

**Source configuration and connections**:

```bash
dango validate --check sources
```

**Output**:

```
Validating data sources...

stripe_payments (stripe)
  ✓ Configuration valid
  ✓ API key present (STRIPE_API_KEY)
  ✓ Start date valid: 2024-06-01
  ✓ Connection test: PASSED (125 ms)
  ✓ Sample data fetched: 10 records

google_sheets (google_sheets)
  ✓ Configuration valid
  ✓ OAuth credentials valid (expires in 37 days)
  ✓ Connection test: PASSED (89 ms)
  ✓ Spreadsheet accessible

sales_data (csv)
  ✓ Configuration valid
  ✓ File exists: data/sales.csv
  ✓ File readable: 5,432 rows
  ✓ Schema detected: 10 columns

facebook_ads_source (facebook_ads)
  ✓ Configuration valid
  ✗ OAuth credentials expired (19 days ago)
  ✗ Connection test: FAILED
  → Re-authenticate: dango auth refresh facebook_ads_source

old_hubspot (hubspot)
  ⚠ Source disabled in config
  - Last synced: 5 days ago
  → Remove if no longer needed

Validation complete: 1 error, 1 warning
```

### Validate Database

**Database health and integrity**:

```bash
dango validate --check database
```

**Output**:

```
Validating database...

File:
  ✓ data/warehouse.duckdb exists
  ✓ Size: 42.3 MB
  ✓ Readable and writable

Connection:
  ✓ Can connect to database
  ✓ DuckDB version: 0.10.0
  ✓ No file locks detected

Schemas:
  ✓ raw (3 tables)
  ✓ raw_stripe (5 tables)
  ✓ staging (8 views)
  ✓ intermediate (3 tables)
  ✓ marts (4 tables)

Integrity:
  ✓ No corrupted tables
  ✓ All tables readable
  ✓ Metadata tables present (_dlt_loads, _dlt_version)

Disk Space:
  ✓ Available: 245 GB
  ✓ Database size: 42.3 MB (0.02% used)

Performance:
  ✓ Query response time: 12 ms (healthy)
  ✓ No blocking locks

Database health: PASSED
```

### Validate Dependencies

**Check required software**:

```bash
dango validate --check deps
```

**Output**:

```
Validating dependencies...

Python:
  ✓ Version: 3.9.18
  ✓ Minimum required: 3.8+
  ✓ Virtual environment: active
  ✓ Packages installed: 42

dbt:
  ✓ Version: 1.7.4
  ✓ Minimum required: 1.5+
  ✓ Installed via: pip
  ✓ Adapter: duckdb 1.7.1

dlt:
  ✓ Version: 0.4.2
  ✓ Minimum required: 0.3+
  ✓ Verified sources: 8 available

Docker:
  ✗ Docker daemon not running
  - Required for: Metabase, dbt-docs
  → Start Docker Desktop
  → Or run with: dango start --no-metabase --no-docs

Git:
  ✓ Version: 2.42.0
  ✓ Repository initialized
  ✓ Remote: origin (github.com/acme/my-analytics)

Optional:
  ⚠ dbt packages not installed
  → Run: dbt deps --profiles-dir .dango --project-dir dbt

Dependencies: 1 error, 1 warning
```

---

## Auto-Fix Issues

### Automatic Fixes

Attempt to fix issues automatically:

```bash
dango validate --fix
```

**What can be auto-fixed**:

1. **Missing directories**:
   - Creates `data/`, `dbt/models/`, etc.

2. **Invalid YAML**:
   - Corrects indentation
   - Adds missing required fields

3. **Missing dbt packages**:
   - Runs `dbt deps`

4. **Orphaned tables**:
   - Optionally cleans up

5. **File permissions**:
   - Makes files readable/writable

**Example output**:

```
Validating project...

[Issue 1] Directory missing: dbt/models/marts
  Fixing: Creating directory...
  ✓ Fixed

[Issue 2] Invalid YAML indentation in .dango/sources.yml
  Fixing: Correcting indentation...
  ✓ Fixed

[Issue 3] dbt packages not installed
  Fixing: Running dbt deps...
  ✓ Fixed (installed dbt_utils 1.1.0)

[Issue 4] Orphaned table: raw_old_source.data
  Action required: Cannot auto-fix (data deletion)
  → Run: dango db clean

3 issues fixed, 1 requires manual action

Re-run validation to verify:
  dango validate
```

### Selective Fixes

Fix only specific types:

```bash
# Fix configuration issues only
dango validate --fix --check config

# Fix missing directories only
dango validate --fix-dirs

# Fix YAML syntax only
dango validate --fix-yaml
```

---

## Detailed Issue Reporting

### Verbose Output

Get detailed diagnostics:

```bash
dango validate --verbose
```

**Additional information**:

- Full stack traces for errors
- Detailed configuration values
- Network diagnostics
- File system details
- Timing information

**Example**:

```
[2/8] Source Configuration

  Checking .dango/sources.yml...
    File path: /Users/alice/projects/my-analytics/.dango/sources.yml
    File size: 1,234 bytes
    Last modified: 2024-12-09 12:34:56
    Readable: Yes
    Writable: Yes

  Parsing YAML...
    Parser: PyYAML 6.0
    Encoding: UTF-8
    Parse time: 3 ms
    ✓ Valid YAML

  Validating schema...
    Sources found: 5
    Checking source 1/5: stripe_payments
      Type: stripe
      Enabled: true
      Required fields: stripe_secret_key_env, start_date
      Optional fields: resources
      ✓ All required fields present

    Checking source 2/5: google_sheets
      Type: google_sheets
      Enabled: true
      Testing OAuth...
        Provider: Google
        Token path: .dlt/.google_sheets_oauth_token
        Token expiry: 2025-01-15T10:30:00Z
        Days until expiry: 37
        ✓ OAuth valid
```

### JSON Output

Machine-readable validation results:

```bash
dango validate --json
```

**Response**:

```json
{
  "timestamp": "2024-12-09T12:45:00Z",
  "project": "my-analytics",
  "status": "failed",
  "errors": 2,
  "warnings": 3,
  "checks": {
    "config": {
      "status": "passed",
      "duration_ms": 45,
      "details": {
        "project_yml": "valid",
        "sources_yml": "valid",
        "dbt_project_yml": "valid"
      }
    },
    "sources": {
      "status": "failed",
      "duration_ms": 1234,
      "sources": [
        {
          "name": "stripe_payments",
          "status": "passed",
          "connection_time_ms": 125
        },
        {
          "name": "facebook_ads_source",
          "status": "failed",
          "error": "OAuth credentials expired",
          "fix": "dango auth refresh facebook_ads_source"
        }
      ]
    },
    "database": {
      "status": "passed",
      "duration_ms": 67,
      "size_mb": 42.3,
      "tables": 23
    },
    "dependencies": {
      "status": "failed",
      "duration_ms": 89,
      "issues": [
        {
          "component": "docker",
          "status": "not_running",
          "fix": "docker start"
        }
      ]
    }
  },
  "fixes": [
    "docker start",
    "dango auth refresh facebook_ads_source"
  ]
}
```

**Use in CI/CD**:

```bash
#!/bin/bash
# ci-validate.sh

result=$(dango validate --json)
status=$(echo "$result" | jq -r '.status')

if [ "$status" != "passed" ]; then
  echo "Validation failed!"
  echo "$result" | jq '.fixes[]'
  exit 1
fi

echo "Validation passed"
exit 0
```

---

## Common Issues and Fixes

### Issue: Port Already in Use

**Error**:

```
✗ Port 8800 already in use
```

**Fix**:

```bash
# Find process using port
lsof -i :8800

# Kill process
kill <PID>

# Or change port in .dango/project.yml
vim .dango/project.yml
# port: 8888

# Validate
dango validate
```

### Issue: Docker Not Running

**Error**:

```
✗ Docker daemon not running
Metabase and dbt-docs won't start
```

**Fix 1: Start Docker**:

```bash
# macOS/Windows
open -a Docker

# Linux
sudo systemctl start docker

# Validate
dango validate
```

**Fix 2: Skip Docker**:

```bash
# Run without Metabase/dbt-docs
dango start --no-metabase --no-docs
```

### Issue: OAuth Expired

**Error**:

```
✗ OAuth credentials expired (facebook_ads_source)
Last synced: 19 days ago
```

**Fix**:

```bash
# Re-authenticate
dango auth refresh facebook_ads_source

# Validate
dango validate --check sources
```

### Issue: Missing Credentials

**Error**:

```
✗ STRIPE_API_KEY not found
Required by: stripe_payments
```

**Fix**:

```bash
# Add to .env
echo "STRIPE_API_KEY=sk_live_abc123..." >> .env

# Or add to .dlt/secrets.toml
cat >> .dlt/secrets.toml << EOF
[sources.stripe]
stripe_secret_key = "sk_live_abc123..."
EOF

# Validate
dango validate --check sources
```

### Issue: Invalid YAML

**Error**:

```
✗ .dango/sources.yml invalid YAML
Line 15: unexpected indentation
```

**Fix 1: Auto-fix**:

```bash
dango validate --fix
```

**Fix 2: Manual edit**:

```bash
vim .dango/sources.yml
# Fix indentation at line 15

# Validate
dango validate --check config
```

### Issue: Database Corrupted

**Error**:

```
✗ Database file corrupted
Cannot read tables
```

**Fix 1: Restore from backup**:

```bash
# If you have backups
cp data/warehouse-backup-20241208.duckdb data/warehouse.duckdb

# Validate
dango validate --check database
```

**Fix 2: Rebuild database**:

```bash
# Remove corrupted database
mv data/warehouse.duckdb data/warehouse-corrupted.duckdb

# Re-sync all data
dango sync --full-refresh

# Regenerate staging
dango generate

# Run transformations
dango run

# Validate
dango validate
```

### Issue: CSV File Not Found

**Error**:

```
✗ File not found: data/sales.csv
Required by: sales_data source
```

**Fix 1: Add file**:

```bash
# Add missing file
cp ~/Downloads/sales.csv data/

# Validate
dango validate --check sources
```

**Fix 2: Update path**:

```bash
# Edit source configuration
vim .dango/sources.yml
# Change file_path to correct location

# Validate
dango validate
```

### Issue: dbt Packages Missing

**Error**:

```
⚠ dbt packages not installed
dbt_utils referenced but not installed
```

**Fix**:

```bash
# Install dbt packages
dbt deps --profiles-dir .dango --project-dir dbt

# Validate
dango validate --check deps
```

---

## CI/CD Integration

### Validation in CI Pipeline

**GitHub Actions** (`.github/workflows/validate.yml`):

```yaml
name: Validate Dango Project

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dango
        run: |
          pip install getdango
          dango --version

      - name: Validate Configuration
        run: |
          dango validate --strict --check config
        env:
          STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}

      - name: Validate Sources
        run: |
          dango validate --check sources --dry-run
        env:
          STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}
          GOOGLE_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}

      - name: Generate Validation Report
        if: always()
        run: |
          dango validate --json > validation-report.json

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.json
```

### Pre-commit Hook

**`.git/hooks/pre-commit`**:

```bash
#!/bin/bash
# Validate before committing

echo "Running Dango validation..."

dango validate --strict --check config

if [ $? -ne 0 ]; then
  echo "❌ Validation failed! Fix issues before committing."
  echo "Run: dango validate --fix"
  exit 1
fi

echo "✅ Validation passed"
exit 0
```

**Make executable**:

```bash
chmod +x .git/hooks/pre-commit
```

### Pre-push Validation

**`.git/hooks/pre-push`**:

```bash
#!/bin/bash
# Full validation before pushing

echo "Running full Dango validation..."

dango validate --strict

if [ $? -ne 0 ]; then
  echo "❌ Validation failed! Fix all issues before pushing."
  exit 1
fi

echo "✅ All validations passed"
exit 0
```

---

## Best Practices

### 1. Validate Before Syncing

Always validate before important syncs:

```bash
# Morning routine
dango validate
dango sync
dango run
```

### 2. Run in Strict Mode in CI

Catch warnings early:

```bash
# In CI/CD
dango validate --strict

# Locally (warnings OK)
dango validate
```

### 3. Check Sources Before Adding

Test connection before saving:

```bash
# Add source with validation
dango source add stripe

# Explicit test
dango validate --check sources
```

### 4. Regular Health Checks

Schedule periodic validation:

```bash
# In cron (daily at 8am)
0 8 * * * cd /path/to/project && dango validate --json > /var/log/dango-validation.log
```

### 5. Use Auto-Fix Safely

Review before applying fixes:

```bash
# Preview fixes
dango validate --verbose

# Apply fixes
dango validate --fix

# Verify
dango validate
```

---

## Validation Checklist

Use this checklist for manual validation:

**Configuration**:

- [ ] `.dango/project.yml` exists and valid
- [ ] `.dango/sources.yml` exists and valid
- [ ] `dbt/dbt_project.yml` exists and valid
- [ ] No duplicate source names
- [ ] All ports available

**Sources**:

- [ ] All enabled sources have valid credentials
- [ ] OAuth tokens not expired (check with `dango auth list`)
- [ ] CSV files exist at specified paths
- [ ] Database connections successful

**Database**:

- [ ] DuckDB file exists and accessible
- [ ] All schemas present (raw, staging, marts)
- [ ] No corrupted tables
- [ ] Sufficient disk space (> 1 GB free)

**Dependencies**:

- [ ] Python 3.8+ installed
- [ ] dbt 1.5+ installed
- [ ] dlt 0.3+ installed
- [ ] Docker running (if using Metabase)
- [ ] dbt packages installed (`dbt deps`)

**Platform**:

- [ ] Port 8800 available (or configured port)
- [ ] File watcher patterns configured
- [ ] Auto-sync settings correct

**Run validation**:

```bash
dango validate --verbose
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-sync: **Sync & Run**

    ---

    Once validated, sync data and run transformations.

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-database-outline: **Source Management**

    ---

    Add and manage sources with confidence.

    [:octicons-arrow-right-24: Source Management](source-management.md)

-   :material-help-circle: **Troubleshooting**

    ---

    Comprehensive troubleshooting guide.

    [:octicons-arrow-right-24: Troubleshooting](../getting-started/troubleshooting.md)

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete CLI command reference.

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

</div>
