# Backup & Restore

Complete backup strategies for all Dango components — local and cloud.

---

## Overview

A Dango project has several components that need backup:

| Component | Location | Contents | Priority |
|-----------|----------|----------|----------|
| **DuckDB Database** | `data/warehouse.duckdb` | All synced data | High |
| **Configuration** | `.dango/`, `.dlt/` | Source configs, credentials | High |
| **dbt Models** | `dbt/` | Transformations, tests, snapshots | High |
| **Auth Database** | `.dango/auth.db` | Users, sessions, audit log | High |
| **Metabase** | `metabase-data/` | Dashboards, settings | Medium |
| **Raw Files** | `data/uploads/` | CSV source files | Medium |

Dango provides different backup mechanisms for local and cloud deployments.

---

## Local Backups

### Quick Backup Script

Create a complete local backup with one script:

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

# 4. dbt models and snapshots
cp -r dbt "$BACKUP_DIR/"

# 5. Metabase dashboards
dango metabase save --output "$BACKUP_DIR/metabase/"

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

You can also list and restore from automatic local backup archives using the CLI:

```bash
dango backup          # list archives in .dango/backups/
dango backup restore ./path/to/archive.tar.gz
```

See [Local Backup](../cli/other-commands.md#local-backup) for full details.

### Component-Specific Backups

#### DuckDB Database

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

#### Configuration Files

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

#### dbt Models

Your transformation logic should be version controlled:

```bash
# If using git (recommended)
cd dbt && git add . && git commit -m "Backup dbt models"

# Manual backup
cp -r dbt backups/dbt_backup/
```

#### Metabase Dashboards

```bash
# Export dashboards
dango metabase save --output backups/metabase/

# Full Metabase data (H2 database)
cp -r metabase-data backups/metabase_backup/
```

### Automated Local Backups

#### Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/project && ./backup_dango.sh >> /var/log/dango_backup.log 2>&1
```

#### Backup Rotation

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

---

## Cloud Backups

When deployed to the cloud, Dango provides built-in backup management with DigitalOcean Spaces (S3-compatible object storage).

### Automatic Pre-Deploy Backup

Every `dango remote push` automatically creates a backup on the server before deploying. This ensures you can roll back if a deploy causes issues.

Override an existing deploy lock with `--force` (not recommended):

```bash
# Normal deploy (backup runs automatically)
dango remote push

# Override deploy lock if another push is stuck
dango remote push --force
```

!!! warning "Use `--force` With Caution"
    Only use `--force` if you're certain no other deploy is running. Overriding the lock while another push is in progress can corrupt the deployment.

### Cloud Backup Commands

```bash
# List backups on the server
dango remote backup list

# Enable scheduled backups to DigitalOcean Spaces
dango remote backup enable

# Disable scheduled backups
dango remote backup disable

# Download a backup from the server
dango remote backup download

# Restore from a backup
dango remote backup restore
```

### Retention Policy

=== "Pre-Deploy Backups (Server Disk)"

    Stored on the server's local disk. Dango keeps the **5 most recent** pre-deploy backups and deletes older ones automatically.

=== "Scheduled Backups (DigitalOcean Spaces)"

    Stored in S3-compatible object storage with tiered retention:

    - **Daily**: Keep all backups from the last **7 days**
    - **Weekly**: Keep **1 backup per week** for up to **4 weeks** older than 7 days

    Older backups are pruned automatically.

### What Cloud Backups Include

Cloud backups are tar.gz archives containing:

- `data/warehouse.duckdb` — full database
- `.dango/auth.db` — authentication database
- `.dango/project.yml`, `.dango/sources.yml`, `.dango/cloud.yml` — configuration
- `.dango/metabase.yml` — Metabase config
- `.dango/logs/audit.jsonl` — audit log
- `.dlt/secrets.toml` — credentials
- `.dlt/pipelines/` — dlt pipeline state
- `dbt/profiles.yml` — dbt connection profile

---

## Restore Procedures

### Local Full Restore

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
dango metabase load --input /path/to/backup/metabase/

# 7. Re-enter credentials (secrets.toml)
# Edit .dlt/secrets.toml with your credentials
```

### Cloud Restore

```bash
# Restore from the most recent cloud backup
dango remote backup restore

# Or restore from a specific backup
dango remote backup download  # Download first, then restore manually
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
# Or restore from saved dashboards
dango metabase load --input /path/to/backup/metabase/
```

**dbt Models Only**:
```bash
rm -rf dbt/models/intermediate dbt/models/marts
cp -r /path/to/backup/dbt/models/intermediate dbt/models/
cp -r /path/to/backup/dbt/models/marts dbt/models/
dango run
```

For full cloud backup details, see [Cloud Backups](../deployment/backups.md).

---

## Disaster Recovery

### Recovery Checklist

1. Install Dango: `pip install getdango`
2. Initialize project: `dango init project-name`
3. Restore configuration files
4. Recreate credentials in `.dlt/secrets.toml`
5. Restore database or re-sync: `dango sync`
6. Restore or regenerate dbt models: `dango run`
7. Restore Metabase dashboards
8. Verify data integrity

### Cloud Disaster Recovery

If the cloud server is lost:

1. Provision a new server: `dango deploy`
2. Restore from the latest Spaces backup: `dango remote backup restore`
3. Verify services are healthy: `dango remote status`
4. Check data: `dango remote logs`

---

## What NOT to Backup

Some files can be excluded from **manual local backups** (they are regenerable or transient):

```bash
# Excludable from manual backups
*.log
*.tmp
__pycache__/
.dlt/pipelines/        # Can be regenerated (but slows restore — re-syncs from scratch)
dbt/target/            # Compiled artifacts
dbt/logs/              # dbt logs
.dango/state/          # Runtime state (locks, sync status)
.dango/dev/            # Dev mode artifacts
```

!!! note "Cloud backups include `.dlt/pipelines/`"
    Dango's automated cloud backups include pipeline state for faster restores. If you exclude it from manual backups, the next sync will do a full refresh instead of incremental — slower but not destructive.

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
- [Cloud Backups](../deployment/backups.md) - Full cloud backup documentation
- [Troubleshooting](troubleshooting.md) - Recovery from common issues
- [Performance](performance.md) - Optimize large database backups
