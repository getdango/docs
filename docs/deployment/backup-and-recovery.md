# Backup & Recovery

Comprehensive guide to Dango's backup system — creating, downloading, restoring, and disaster recovery.

---

## Overview

Dango provides a layered backup strategy for cloud deployments:

| Layer | Location | Retention | Purpose |
|-------|----------|-----------|---------|
| **On-server** | `/srv/dango/backups/deploy/` | Configurable (default: 14) | Fast rollback, pre-deploy snapshots |
| **Spaces (off-server)** | DigitalOcean Spaces bucket | GFS tiers (daily/weekly/monthly) | Disaster recovery, server migration |
| **Local** | Your machine (`dango remote backup download`) | Manual | Offline archival |

Scheduled backups run daily at 02:00 UTC and upload to DigitalOcean Spaces. On-demand backups can be created at any time.

---

## What Gets Backed Up

| Category | Files |
|----------|-------|
| **Database** | `data/warehouse.duckdb` |
| **Auth** | `.dango/auth.db` |
| **Configuration** | `.dango/project.yml`, `.dango/sources.yml`, `.dango/cloud.yml`, `.dango/metabase.yml` |
| **Audit log** | `.dango/logs/audit.jsonl` |
| **dbt models** | `models/`, `dbt/profiles.yml`, `dbt_project.yml` |
| **Metabase** | Metabase H2 database (dashboards, questions, users) |

### What Is NOT Backed Up

!!! warning "Secrets Are Excluded"
    For security, credentials are **never** included in backup archives:
    - `.env` (environment variables)
    - `.dlt/secrets.toml` (dlt credentials and OAuth tokens)

    After restore, you must reconfigure credentials. See [Post-Restore Steps](#post-restore-steps).

---

## Prerequisites

- An active deployment via [DigitalOcean](digitalocean.md) or [BYOS](byos.md)
- For scheduled backups, download, and restore: **DigitalOcean Spaces** credentials configured

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote backup` | Create an on-demand backup (uploads to Spaces) |
| `dango remote backup list` | List server and Spaces backups |
| `dango remote backup enable` | Enable daily scheduled backups (02:00 UTC) |
| `dango remote backup disable` | Disable scheduled backups |
| `dango remote backup download NAME` | Download a backup from Spaces |
| `dango remote backup download --from-server` | Download latest backup from server |
| `dango remote backup restore SOURCE` | Restore server from a Spaces backup |
| `dango remote backup restore FILE --from-local` | Upload and restore from a local backup |
| `dango remote backup verify-metabase` | Check Metabase health after restore |
| `dango remote backup config` | Show current backup configuration |

---

## Creating Backups

### On-Demand Backup

Create a manual backup that uploads directly to Spaces:

```bash
dango remote backup
```

This creates an archive of all data and configuration, uploads it to your Spaces bucket under `backups/`, and applies your retention policy.

### Scheduled Backups

Enable daily automated backups at 02:00 UTC:

```bash
dango remote backup enable
```

Check status:

```bash
dango remote backup list
```

Disable if needed:

```bash
dango remote backup disable
```

### Automatic Pre-Deploy Backups

Before each `dango remote push`, Dango automatically creates a local backup on the server (stored in `/srv/dango/backups/deploy/`). These enable fast rollback with `dango remote rollback`.

---

## Listing Backups

List all available backups across both server and Spaces:

```bash
dango remote backup list
```

Example output:

```
Server backups (on-server):
  backup-2026-07-05-020000.tar.gz   (45 MB, 2026-07-05 02:00)
  backup-2026-07-04-020000.tar.gz   (44 MB, 2026-07-04 02:00)

Spaces backups (off-server):
  backup-2026-07-05-020000.tar.gz   (45 MB, 2026-07-05 02:00)
  backup-2026-07-04-020000.tar.gz   (44 MB, 2026-07-04 02:00)
  backup-2026-07-03-020000.tar.gz   (43 MB, 2026-07-03 02:00)
```

---

## Downloading Backups

### From Spaces

Download a specific backup by name:

```bash
dango remote backup download backup-2026-07-05-020000.tar.gz
```

This saves the file to your current directory.

### From Server

Download the latest on-server backup (useful before destroying a deployment):

```bash
dango remote backup download --from-server
```

This downloads from `/srv/dango/backups/deploy/` on the server.

---

## Restoring Backups

!!! danger "Overwrites Current Data"
    Restoring a backup **overwrites** the current database, configuration, and Metabase data on the server. The restore process creates a safety backup before proceeding, but you should still download a copy beforehand.

### Restore from Spaces

```bash
dango remote backup restore backup-2026-07-05-020000.tar.gz
```

This downloads the backup from Spaces to the server, stops services, restores data, and restarts services.

### Restore from Local File

If you have a backup file locally (e.g., downloaded before destroying a previous deployment):

```bash
dango remote backup restore ./dango-backup-2026-07-05.tar.gz --from-local
```

This uploads the file to the server and restores from it.

### Restore to a New Server

When migrating to a new deployment:

1. Deploy a new server with the **same project name and region**
2. During deployment, choose to **reuse the existing Spaces bucket** in the wizard
3. After deployment, restore the backup:
   ```bash
   dango remote backup restore backup-2026-07-05-020000.tar.gz
   ```

---

## Post-Restore Steps

After a successful restore, credentials must be reconfigured because they are excluded from backups for security.

### 1. Reconnect OAuth Sources

```bash
dango oauth setup
```

This re-authenticates Google Sheets, Google Analytics, Google Ads, and Facebook Ads.

### 2. Restore Environment Variables

```bash
dango remote env list              # Check current variables
dango remote env set KEY VALUE     # Set missing values
```

Common variables to restore:
- API keys for third-party services
- Custom SMTP settings
- Notification webhook URLs

### 3. Save a Local Copy

```bash
dango remote backup download --from-server
```

Keep a local backup for offline archival.

### 4. Verify Services

```bash
dango remote status
dango remote backup verify-metabase
```

---

## Retention Configuration

### On-Server Retention

Controlled by `BackupConfig.on_server_retention` in `cloud.yml`. Default: 1 (only the most recent pre-deploy backup is kept).

### Spaces Retention

Spaces backups use GFS (Grandfather-Father-Son) retention tiers:

| Tier | Default | Purpose |
|------|---------|---------|
| Daily | 7 days | Recent recovery points |
| Weekly | 4 weeks | Weekly snapshots |
| Monthly | 0 (disabled) | Long-term archival |

Configure via `dango remote backup config` or by editing `cloud.yml`:

```yaml
backup:
  on_server_retention: 1
  spaces_retention:
    daily: 7
    weekly: 4
    monthly: 0
```

---

## Reusing Spaces Buckets

### During Deploy

The deploy wizard (Step 7) automatically discovers existing `dango-backup-*` buckets and offers to reuse them:

```
Spaces buckets in your account:
  1. dango-backup-myproj-nyc1 (12 backups, 450 MB, created 2026-05-15)
  2. Create new bucket → dango-backup-myproj-nyc3
```

Reusing a bucket preserves existing backups and applies your current retention policy to all contents.

### During Destroy

By default, `dango deploy destroy` **preserves** your Spaces bucket and all backups:

```
Spaces bucket: my-bucket — will be KEPT (use --delete-spaces to remove)
```

To delete the bucket and all backups:

```bash
dango deploy destroy --delete-spaces
```

If you keep the bucket and redeploy with the same project name and region, the wizard will offer to reuse it — giving you access to all previous backups on the new server.

---

## Disaster Recovery Checklist

1. **Download the latest backup** from Spaces (if server is unreachable):
   ```bash
   dango remote backup download <name>
   ```

2. **Deploy a new server** with the same project name and region:
   ```bash
   dango deploy
   ```
   Choose "reuse existing bucket" when prompted.

3. **Restore the backup** to the new server:
   ```bash
   dango remote backup restore ./<backup-file> --from-local
   ```

4. **Reconfigure credentials** (see [Post-Restore Steps](#post-restore-steps)).

5. **Verify**:
   ```bash
   dango remote status
   dango remote backup verify-metabase
   ```

---

## Troubleshooting

### Backup fails with "Spaces credentials not configured"

Run `dango remote backup enable` to add Spaces keys, or check your `.env` variables:

```bash
dango remote env list | grep SPACES
```

### Restore fails with "Insufficient disk space"

Check server disk usage:

```bash
dango remote status
```

Free up space by removing old on-server backups or unused Docker images.

### Restore succeeds but services won't start

Check service status:

```bash
dango remote status
```

Review server logs:

```bash
dango remote logs
```

### "No backups found" during destroy

Backups may exist in Spaces even if on-server backups have been cleaned up. The destroy prompt now checks both locations. If your server is unreachable but Spaces backups exist, you'll be offered a Spaces download.
