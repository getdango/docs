# Backups

Set up automated backups and restore from snapshots.

---

## Prerequisites

- [ ] An active deployment via [DigitalOcean](digitalocean.md) or [BYOS](byos.md)
- [ ] For scheduled backups, download, and restore: **DigitalOcean Spaces** credentials configured (see [Environment Variables](environment-variables.md))

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote backup` | Create an on-demand backup |
| `dango remote backup list` | List server and Spaces backups |
| `dango remote backup enable` | Enable daily scheduled backups (02:00 UTC) |
| `dango remote backup disable` | Disable scheduled backups |
| `dango remote backup download NAME` | Download a backup from Spaces |
| `dango remote backup restore SOURCE` | Restore from a Spaces backup |

---

## What Gets Backed Up

Every backup includes:

| Category | Files |
|----------|-------|
| **Database** | `data/warehouse.duckdb` |
| **Auth** | `.dango/auth.db` |
| **Configuration** | `.dango/project.yml`, `.dango/sources.yml`, `.dango/cloud.yml`, `.dango/metabase.yml` |
| **Audit log** | `.dango/logs/audit.jsonl` |
| **Credentials** | `.dlt/secrets.toml` |
| **dbt** | `dbt/profiles.yml` |
| **dlt pipelines** | `.dlt/pipelines/` (entire directory) |
| **Metabase** | H2 database files (`metabase.db.mv.db`, `metabase.db.trace.db`) from Docker volume |

!!! note
    The backup includes credentials (`.dlt/secrets.toml`) and auth database. Treat backup archives as sensitive data.

---

## Backup Format

Backups are stored as compressed tar archives:

- **Filename:** `backup-YYYYMMDD-HHMMSS.tar.gz` (e.g., `backup-20260515-020000.tar.gz`)
- **Manifest:** `backup-YYYYMMDD-HHMMSS.json` (metadata: timestamp, type, Dango version, file list, git commit/branch)
- **Server location:** `/srv/dango/backups/deploy/`

### Retention

The server keeps the **5 most recent** local backups. Older backups are automatically deleted after each new backup. Backups uploaded to Spaces are not subject to local rotation.

---

## On-Demand Backup

Create a backup immediately:

```bash
dango remote backup
```

```
Creating backup...
  ✓ Stopped services
  ✓ Checkpointed databases
  ✓ Archived 12 files (256 MB)
  ✓ Backup: backup-20260515-143000.tar.gz
  ✓ Restarted services
  ✓ Health check passed
```

**Backup workflow:**

1. Check disk space (requires &ge;500 MB free)
2. Stop dango-web and Metabase (prevents concurrent writes)
3. Checkpoint DuckDB (`CHECKPOINT`) and auth database (`PRAGMA wal_checkpoint(TRUNCATE)`)
4. Stage files into temporary directory
5. Create manifest with metadata
6. Compress into `.tar.gz` archive
7. Rotate old backups (keep 5)
8. Restart services
9. Verify health

---

## Listing Backups

View all available backups on the server and in Spaces:

```bash
dango remote backup list
```

```
Source    Name                            Size (MB)
server   backup-20260515-143000.tar.gz   256
server   backup-20260515-020000.tar.gz   254
server   backup-20260514-020000.tar.gz   251
spaces   backup-20260513-020000.tar.gz   249
spaces   backup-20260512-020000.tar.gz   247
```

Backups on the server are available for immediate rollback. Backups in Spaces must be downloaded or restored via `dango remote backup restore`.

---

## Scheduled Backups

### Enable

Set up automatic daily backups:

=== "DigitalOcean"

    ```bash
    dango remote backup enable
    ```

    ```
    ✓ Systemd timer created (daily at 02:00 UTC)
    ✓ Backups will be uploaded to Spaces
    ```

    Requires Spaces credentials in the remote `.env`:

    ```bash
    dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
    dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
    dango remote env set SPACES_REGION=nyc3
    dango remote env set SPACES_BUCKET=my-dango-backups
    ```

=== "BYOS"

    ```bash
    dango remote backup enable
    ```

    Same command and behavior. You need to set up a DigitalOcean Spaces bucket manually (or use any S3-compatible storage) and configure the credentials:

    ```bash
    dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
    dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
    dango remote env set SPACES_REGION=nyc3
    dango remote env set SPACES_BUCKET=my-dango-backups
    ```

**What happens:**

- Creates a systemd timer (`dango-backup.timer`) that fires daily at **02:00 UTC**
- Each backup is created locally, then uploaded to Spaces
- Local rotation still applies (5 most recent kept)
- Spaces backups are retained indefinitely (manage via the Spaces console)

### Disable

```bash
dango remote backup disable
```

Stops the systemd timer. Existing backups (local and Spaces) are not deleted.

---

## Downloading Backups

Download a backup from Spaces to your local machine:

```bash
dango remote backup download backup-20260515-020000.tar.gz
```

Save to a specific path:

```bash
dango remote backup download backup-20260515-020000.tar.gz -o ~/backups/dango-backup.tar.gz
```

| Argument/Option | Description |
|-----------------|-------------|
| `NAME` | Backup filename (required) |
| `-o`, `--output` | Local destination path (default: current directory) |

---

## Restoring from Backup

!!! danger "Destructive Operation"
    Restoring from a backup **overwrites all current data** on the server, including the DuckDB warehouse, Metabase configuration, auth database, and credentials. This cannot be undone.

Restore from a Spaces backup:

```bash
dango remote backup restore backup-20260515-020000.tar.gz
```

```
⚠ This will overwrite all data on the server with backup-20260515-020000.tar.gz

Are you sure? [y/N]: y

Restoring...
  ✓ Downloaded from Spaces
  ✓ Stopped services
  ✓ Restored 12 files
  ✓ Restarted services
  ✓ Health check passed
```

| Argument/Option | Description |
|-----------------|-------------|
| `SOURCE` | Backup filename (required) |
| `--yes`, `-y` | Skip confirmation prompt |

The backup filename is validated &mdash; only alphanumeric characters, hyphens, underscores, and dots are allowed.

---

## Automatic Backups

Dango automatically creates backups during certain operations:

| Trigger | Backup Type | When |
|---------|------------|------|
| `dango remote push` | Pre-deploy | Before applying file changes |
| `dango remote upgrade` | Pre-upgrade | Before upgrading Dango version |
| `dango remote resize` | Pre-resize | Before resizing the server |

These automatic backups follow the same format and retention policy as on-demand backups. You can roll back to any of them using `dango remote rollback`.

---

## Troubleshooting

### Disk space insufficient

```
Error: Insufficient disk space for backup
```

The server needs at least 500 MB free to create a backup. Check disk usage:

```bash
dango remote status
```

To free space, remove old data or [resize the server](server-operations.md).

### Spaces credentials invalid

```
Error: Failed to upload to Spaces
```

Verify your Spaces credentials:

```bash
dango remote env list
```

Ensure all four variables are set: `SPACES_ACCESS_KEY`, `SPACES_SECRET_KEY`, `SPACES_REGION`, `SPACES_BUCKET`.

### Backup timeout

On-demand backups have a 15-minute timeout. If your DuckDB database is very large (>10 GB), the backup may time out during compression. Consider:

- Running backups during low-activity periods
- [Resizing the server](server-operations.md) for faster I/O

### No backups found

```
No backups found
```

If `dango remote backup list` shows no backups:

- No on-demand or automatic backup has been created yet &mdash; run `dango remote backup`
- Scheduled backups are not enabled &mdash; run `dango remote backup enable`
- Spaces credentials are missing (for Spaces backups)

### Corrupt archive

If a restore fails due to a corrupt archive, try a different backup:

```bash
# List available backups
dango remote backup list

# Try an older backup
dango remote backup restore backup-20260514-020000.tar.gz
```

If all Spaces backups are corrupt, check the server for local backups via SSH:

```bash
dango remote ssh
ls -la /srv/dango/backups/deploy/
```

---

## Next Steps

- [Remote Management](remote-management.md) &mdash; push changes and manage the server
- [Server Operations](server-operations.md) &mdash; upgrade, resize, and migrate
- [Destroy & Cleanup](destroy.md) &mdash; tear down a deployment
