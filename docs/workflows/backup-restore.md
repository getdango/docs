# Backup & Restore

Complete backup strategies for all Dango components.

---

## Overview

A Dango project has several components that need backup:

| Component | Location | Contents | Priority |
|-----------|----------|----------|----------|
| **DuckDB Database** | `data/warehouse.duckdb` | All synced data | High |
| **Configuration** | `.dango/`, `.dlt/` | Source configs, credentials | High |
| **dbt Models** | `dbt/` | Transformations, tests | High |
| **Metabase** | `metabase-data/` | Dashboards, settings | Medium |
| **Raw Files** | `data/uploads/` | CSV source files | Medium |

---

## Quick Backup Script

Create a complete backup with one script:

```bash
#!/bin/bash
# backup_dango.sh

PROJECT_DIR=$(pwd)
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

# 1. Stop services (optional but recommended)
dango stop

# 2. Database
cp data/warehouse.duckdb "$BACKUP_DIR/"

# 3. Configuration
cp -r .dango "$BACKUP_DIR/"
cp -r .dlt "$BACKUP_DIR/"

# 4. dbt models
cp -r dbt "$BACKUP_DIR/"

# 5. Metabase dashboards
dango metabase save
cp metabase_export.json "$BACKUP_DIR/"

# 6. Metabase data (Docker volume)
if [ -d "metabase-data" ]; then
    cp -r metabase-data "$BACKUP_DIR/"
fi

# 7. CSV files (optional - may be large)
# cp -r data/uploads "$BACKUP_DIR/"

# Restart services
dango start

echo "Backup complete: $BACKUP_DIR"
```

---

## Component-Specific Backups

### DuckDB Database

The DuckDB database contains all your synced and transformed data:

```bash
# Simple copy (while services stopped)
dango stop
cp data/warehouse.duckdb data/warehouse.duckdb.backup
dango start

# With timestamp
cp data/warehouse.duckdb "backups/warehouse_$(date +%Y%m%d).duckdb"
```

!!! warning "Stop Before Backup"
    For consistency, stop Dango services before copying the database file, or use DuckDB's export functionality for a consistent snapshot.

**Export to Parquet (alternative)**:

```sql
-- Run in DuckDB CLI or Metabase
EXPORT DATABASE 'backups/export' (FORMAT PARQUET);
```

### Configuration Files

Back up your source configurations and project settings:

```bash
# Configuration files
cp -r .dango backups/dango_config/
cp .dango/sources.yml backups/sources.yml.backup
cp .dango/project.yml backups/project.yml.backup

# dlt configuration (NO secrets!)
cp .dlt/config.toml backups/dlt_config.toml.backup
# WARNING: Don't backup secrets.toml to shared storage
```

!!! danger "Protect Secrets"
    Never commit or backup `.dlt/secrets.toml` to shared or cloud storage. Recreate credentials manually on restore.

### dbt Models

Your transformation logic should be version controlled:

```bash
# If using git (recommended)
cd dbt && git add . && git commit -m "Backup dbt models"

# Manual backup
cp -r dbt backups/dbt_backup/
```

### Metabase Dashboards

Export dashboard definitions for backup:

```bash
# Export to JSON
dango metabase save
cp metabase_export.json backups/

# Full Metabase data (H2 database)
cp -r metabase-data backups/metabase_backup/
```

### CSV Source Files

```bash
# Back up uploaded CSV files
cp -r data/uploads backups/csv_files/

# Compressed backup for large files
tar -czf backups/csv_files.tar.gz data/uploads/
```

---

## Restore Procedures

### Full Restore

```bash
# 1. Create fresh project
dango init my-project-restored
cd my-project-restored

# 2. Restore configuration
cp -r /path/to/backup/.dango .
cp -r /path/to/backup/.dlt .

# 3. Restore dbt models
rm -rf dbt
cp -r /path/to/backup/dbt .

# 4. Restore database
cp /path/to/backup/warehouse.duckdb data/

# 5. Start services
dango start

# 6. Restore Metabase dashboards
dango metabase load --file /path/to/backup/metabase_export.json

# 7. Re-enter credentials (secrets.toml)
# Edit .dlt/secrets.toml with your credentials
```

### Restore Individual Components

**Database Only**:
```bash
dango stop
rm data/warehouse.duckdb
cp /path/to/backup/warehouse.duckdb data/
dango start
```

**Metabase Only**:
```bash
dango stop
rm -rf metabase-data
cp -r /path/to/backup/metabase_backup metabase-data
dango start
# Or restore from JSON
dango metabase load --file metabase_export.json
```

**dbt Models Only**:
```bash
rm -rf dbt/models/intermediate dbt/models/marts
cp -r /path/to/backup/dbt/models/intermediate dbt/models/
cp -r /path/to/backup/dbt/models/marts dbt/models/
dango run
```

---

## Automated Backups

### Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/project && ./backup_dango.sh >> /var/log/dango_backup.log 2>&1
```

### Backup Rotation

Keep recent backups, delete old ones:

```bash
#!/bin/bash
# rotate_backups.sh

BACKUP_DIR="backups"
KEEP_DAYS=7

# Delete backups older than 7 days
find "$BACKUP_DIR" -type d -mtime +$KEEP_DAYS -exec rm -rf {} +

echo "Old backups cleaned up"
```

### Cloud Backup

**To AWS S3**:
```bash
# Install AWS CLI first
aws s3 sync backups/ s3://my-bucket/dango-backups/
```

**To Google Cloud Storage**:
```bash
# Install gsutil first
gsutil -m rsync -r backups/ gs://my-bucket/dango-backups/
```

---

## Disaster Recovery

### Recovery Checklist

1. ✅ Install Dango: `pip install getdango`
2. ✅ Initialize project: `dango init project-name`
3. ✅ Restore configuration files
4. ✅ Recreate credentials in `.dlt/secrets.toml`
5. ✅ Restore database or re-sync: `dango sync`
6. ✅ Restore or regenerate dbt models: `dango run`
7. ✅ Restore Metabase dashboards
8. ✅ Verify data integrity

### Recovery Time Estimates

| Scenario | Method | Time |
|----------|--------|------|
| **Quick recovery** | Restore from backup | 5-10 min |
| **Full re-sync** | Re-fetch all data | Hours (depends on data volume) |
| **Partial recovery** | Restore DB + re-sync recent | 30-60 min |

---

## What NOT to Backup

Some files should be excluded from backups:

```bash
# .gitignore patterns for backup exclusion
*.log
*.tmp
__pycache__/
.dlt/pipelines/        # Can be regenerated
dbt/target/            # Compiled artifacts
dbt/logs/              # dbt logs
```

---

## Verification

After backup, verify integrity:

```bash
# Check DuckDB backup
duckdb backups/warehouse.duckdb "SELECT COUNT(*) FROM information_schema.tables"

# Verify JSON export
python -c "import json; json.load(open('backups/metabase_export.json'))"

# List backup contents
ls -la backups/
```

---

## Next Steps

- [Git Workflows](git-workflows.md) - Version control for configs and models
- [Troubleshooting](troubleshooting.md) - Recovery from common issues
- [Performance](performance.md) - Optimize large database backups
