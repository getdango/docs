# Backup & Recovery

Comprehensive guide to Dango's backup system — creating, downloading, restoring, and disaster recovery.

---

## Overview

Dango provides a layered backup strategy for cloud deployments:

| Layer | Location | Retention | Purpose |
|-------|----------|-----------|---------|
| **On-server (automatic)** | `/srv/dango/backups/deploy/` | Newest 1 | Rollback before each push, upgrade, resize or restore |
| **Spaces (off-server)** | DigitalOcean Spaces bucket | GFS tiers (default 7 daily, 4 weekly) | Disaster recovery, rebuilding a server |
| **Local** | Your machine (`dango remote backup download`) | Manual | Offline archival; the only off-server copy for BYOS |

Scheduled backups run daily at 02:00 UTC. With a Spaces destination they are uploaded, size-verified and removed from the server; without one they stay on the server. On-demand backups can be created at any time. Every backup command prints an `Off-site:` line that says which of these applies (see [Where backups are stored](backups.md#where-backups-are-stored)).

!!! warning "BYOS backups live only on the server"
    Unless you configure a Spaces bucket yourself, BYOS backups are lost with the server. Keep a copy with `dango remote backup download --from-server -o ./backup.tar.gz`.

---

## What Gets Backed Up

| Category | Files |
|----------|-------|
| **Data** | Regular files under `data/`, including `data/warehouse.duckdb` |
| **Auth and state** | `.dango/auth.db`, `.dango/auth.yml`, `.dango/dango.db`, `.dango/scheduler.db` |
| **Configuration** | `.dango/project.yml`, `.dango/sources.yml`, `.dango/schedules.yml`, `.dango/monitors.yml`, `.dango/scripts.yml`, `.dango/pii-overrides.yml`, `.dango/metabase.yml` (without the Metabase admin password) |
| **Logs** | `.dango/logs/audit.jsonl`, `.dango/logs/activity.jsonl` |
| **dbt** | `dbt/profiles.yml`, `dbt/dbt_project.yml`, `dbt/packages.yml`, `dbt/models/`, `dbt/macros/`, `dbt/seeds/` |
| **Code** | `notebooks/`, `scripts/`, `custom_sources/` |
| **Metabase** | Metabase H2 database (dashboards, questions, users) |

### What Is NOT Backed Up

!!! warning "Secrets Are Excluded"
    By default, credentials are excluded from backup archives; set `include_secrets` in the server's `.dango/cloud.yml` to include them (see [Retention and secrets settings](backups.md#retention-and-secrets-settings)):

    - `.env` (environment variables)
    - `.dlt/secrets.toml` (dlt credentials and OAuth tokens)

    The manifest lists the **names** of these variables and keys (never the values). `download` and `restore` print `secrets are not in this backup; re-enter: <names>`, and `deploy destroy`, `remote resize` and `remote backup restore` remind you of this before asking for confirmation. A restore never restores `.env` or `.dlt/secrets.toml` from an archive. See [Post-Restore Steps](#post-restore-steps).

`.dango/cloud.yml` (your droplet, firewall and key ids, local deployment state), `.dlt/pipelines/`, WAL files, and temporary files are not backed up. Restore only archives you made yourself.

---

## Prerequisites

- An active deployment via [DigitalOcean](digitalocean.md) or [BYOS](byos.md)
- For off-site backups and Spaces download/restore: **DigitalOcean Spaces** credentials configured. Without them, backups stay on the server

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote backup` | Create an on-demand backup (uploads to Spaces when a destination is configured) |
| `dango remote backup list` | List server and Spaces backups |
| `dango remote backup enable` | Enable daily scheduled backups (02:00 UTC) |
| `dango remote backup disable` | Disable scheduled backups |
| `dango remote backup download NAME` | Download a backup from Spaces |
| `dango remote backup download --from-server -o FILE` | Create a backup on the server and download it over SSH |
| `dango remote backup restore SOURCE` | Restore server from a Spaces backup |
| `dango remote backup restore FILE --from-local` | Upload and restore from a local backup |
| `dango remote backup verify-metabase` | Check Metabase health after restore |
| `dango remote backup config` | Show current backup configuration |

---

## Creating Backups

### On-Demand Backup

Create a manual backup:

```bash
dango remote backup
```

This creates an archive of all data and configuration. With a Spaces destination it uploads the archive to your bucket under `backups/`, verifies the size, applies your retention policy and removes the local copy. It ends with an `Off-site:` line (`yes (Spaces <bucket>)` or `NO: backups exist only on this server and are lost with it`).

### Scheduled Backups

Enable daily automated backups at 02:00 UTC (works on DigitalOcean and BYOS; on BYOS without a Spaces bucket they stay on the server and the command says `Off-site: NO`):

```bash
dango remote backup enable
```

Check status (the `Backups` panel shows the `Off-site:` line and whether the timer is enabled):

```bash
dango remote status
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
                  Backups
Source   Name                            Size
server   backup-20260705-143000.tar.gz   45.0 MB
spaces   backup-20260705-020000.tar.gz   45.0 MB
spaces   backup-20260704-020000.tar.gz   44.0 MB
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

Create a fresh backup on the server and download it over SSH (useful before destroying a deployment, and the only way to keep an off-server copy on BYOS):

```bash
dango remote backup download --from-server -o ./backup.tar.gz
```

The archive is created in `/srv/dango/backups/deploy/` on the server and then copied to your machine. The command prints the secret names to re-enter, because secrets are not in the archive by default.

---

## Restoring Backups

!!! danger "Overwrites Current Data"
    Restoring a backup **overwrites** the current database, configuration, and Metabase data on the server. The restore process creates a safety backup before proceeding, but you should still download a copy beforehand. Before asking for confirmation, the command reminds you that `.env` and `.dlt/secrets.toml` are not in backups and lists the secret names the server holds.

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

This uploads the file to the server and restores from it. Restore warnings are always shown after the restore, and an archive that holds Metabase data is refused (nothing changes) if the server has no Metabase Docker volume: restart `dango-web` on the server and run the restore again.

### Restore to a New Server

`dango remote migrate` is switched off in 1.0.14; see [Moving to a New Server](server-operations.md#moving-to-a-new-server) for the manual path (download, `dango deploy destroy`, `dango deploy`, `restore --from-local`). To rebuild a lost server from a Spaces backup:

1. Deploy a new server with the **same project name and region**
2. During deployment, choose to **reuse the existing Spaces bucket** in the wizard
3. After deployment, restore the backup:
   ```bash
   dango remote backup restore backup-2026-07-05-020000.tar.gz
   ```

---

## Post-Restore Steps

After a successful restore, credentials must be reconfigured because they are excluded from backups for security. The restore prints the names to re-enter (`secrets are not in this backup; re-enter: <names>`).

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
dango remote backup download --from-server -o ./backup.tar.gz
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

Only the newest backup in `/srv/dango/backups/deploy/` is kept after a push, upgrade or resize backup. The `on_server_retention` value in the `backup:` section of `cloud.yml` is shown by `dango remote backup config`, but those commands do not read it.

### Spaces Retention

Spaces backups use GFS (Grandfather-Father-Son) retention tiers:

| Tier | Default | Purpose |
|------|---------|---------|
| Daily | 7 days | Recent recovery points |
| Weekly | 4 weeks | Weekly snapshots |
| Monthly | 0 (disabled) | Long-term archival |

Configure in the `backup:` section of `cloud.yml`. The scheduled backup reads it from `.dango/cloud.yml` **on the server**, which `dango remote push` does not upload; `dango remote backup config` shows your local copy only:

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
