# Backups

Set up automated backups and restore from snapshots.

---

## Backup vs Save

Dango has two different ways to preserve dashboard state. They serve different purposes:

| | `dango metabase save` | `dango remote backup` |
|---|---|---|
| **What it does** | Exports dashboards as YAML files | Creates a full server backup archive |
| **Where it runs** | Local or cloud | Cloud only |
| **What's included** | Dashboard/question definitions (Shared collection only) | Data, config, Metabase DB, dbt models (secrets excluded by default) |
| **Use case** | Version control, sharing configs across projects | Disaster recovery, server migration |
| **Personal collections** | Not included | Included (full Metabase DB) |
| **Format** | YAML files in `metabase/` directory | Compressed tar archive |

**When to use which:**

- **Saving dashboard configs to Git** → `dango metabase save` + `git commit`
- **Protecting against data loss on a server** → `dango remote backup`
- **Moving to a new server** → download a backup, deploy the new server, restore it (see [Moving to a New Server](server-operations.md#moving-to-a-new-server); `dango remote migrate` is switched off in 1.0.14)

See [Save & Load (YAML)](../dashboards/save-load.md) for dashboard YAML export details.

---

## Prerequisites

- [ ] An active deployment via [DigitalOcean](digitalocean.md) or [BYOS](byos.md)
- [ ] For off-site backups and for `download NAME` / `restore NAME` from Spaces: **DigitalOcean Spaces** credentials configured (see [Environment Variables](environment-variables.md)). Without Spaces, backups stay on the server only (see [Where backups are stored](#where-backups-are-stored))

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote backup` | Create an on-demand backup |
| `dango remote backup list` | List server and Spaces backups |
| `dango remote backup enable` | Enable daily scheduled backups (02:00 UTC) |
| `dango remote backup disable` | Disable scheduled backups |
| `dango remote backup download NAME` | Download a backup from Spaces |
| `dango remote backup download --from-server -o FILE` | Create a backup on the server and download it over SSH (no Spaces needed) |
| `dango remote backup restore SOURCE` | Restore from a Spaces backup |
| `dango remote backup restore FILE --from-local` | Upload a local backup file and restore from it |

---

## Where backups are stored

Every backup command says plainly whether the backup left the server. `dango remote backup`, `dango remote backup enable` and `dango remote status` print one of these lines:

| Line | Meaning |
|------|---------|
| `Off-site: yes (Spaces my-bucket)` | The archive was uploaded to Spaces and its size verified |
| `Off-site: NO: backups exist only on this server and are lost with it` | No Spaces destination is configured |
| `Off-site: NO: Spaces bucket my-bucket is set but SPACES_ACCESS_KEY / SPACES_SECRET_KEY are missing from the server .env` | The destination is set but the keys are not |
| `Off-site: NO (scheduled backups are not enabled; destination Spaces my-bucket)` | A destination exists but the daily timer is not running |
| `Off-site: unknown (...)` | The server's Dango is too old to report a destination (run `dango remote upgrade`) or the server `.env` could not be read |
| `Off-site: unverified (Spaces my-bucket): the upload could not be confirmed` | The upload finished but its size could not be confirmed |

Whenever the line is not `yes`, the command also prints `dango remote backup download --from-server -o <file>` so you can keep a copy on your own machine.

The server reads its Spaces destination (`SPACES_BUCKET`, `SPACES_REGION`) and keys (`SPACES_ACCESS_KEY`, `SPACES_SECRET_KEY`) from its own `.env`; `dango deploy` writes them there, and `dango remote backup enable` writes a missing destination from your local `.dango/cloud.yml`. A server-side `.dango/cloud.yml` is used only as a fallback.

!!! warning "BYOS backups are lost with the server"
    A BYOS server has no Spaces destination unless you set one up yourself. Until then, backups live only on the server and are lost if the server is. `dango deploy --byos`, `dango remote backup enable`, `dango remote status` and the `deploy destroy` and restore prompts all say so. Run `dango remote backup download --from-server -o ./backup.tar.gz` regularly to keep a copy.

---

## What Gets Backed Up

Every backup includes:

| Category | Files |
|----------|-------|
| **Data** | Regular files throughout `data/`, including `data/warehouse.duckdb` and uploaded files |
| **Auth and state** | `.dango/auth.db`, `.dango/auth.yml`, `.dango/dango.db`, `.dango/scheduler.db` |
| **Configuration** | `.dango/project.yml`, `.dango/sources.yml`, `.dango/schedules.yml`, `.dango/monitors.yml`, `.dango/scripts.yml`, `.dango/pii-overrides.yml`, `.dango/metabase.yml` (without the Metabase admin password) |
| **Logs** | `.dango/logs/audit.jsonl`, `.dango/logs/activity.jsonl` |
| **dbt** | `dbt/profiles.yml`, `dbt/dbt_project.yml`, `dbt/packages.yml`, `dbt/models/` (all models), `dbt/macros/`, `dbt/seeds/` |
| **Code** | `notebooks/`, `scripts/`, `custom_sources/` (entire directories) |
| **Metabase** | H2 database files (`metabase.db.mv.db`, `metabase.db.trace.db`) from the Docker volume |

Only regular files and directories are copied. Links and special files are skipped with a warning, and a copy that fails fails the backup. The server copies project directories through descriptors opened without following links, so a link swapped in during the copy is not followed. The one exception is a `data/` that is itself a link (for example to a data volume): it is backed up only if its target is a directory owned by the `dango` user, and only the entries that user owns are copied; otherwise the backup refuses.

### What is not backed up

- **Secrets, by default.** `.env` and `.dlt/secrets.toml` are excluded unless `include_secrets: true` is set in the `backup:` section of the server's `.dango/cloud.yml` (see [Retention and secrets settings](#retention-and-secrets-settings)). Treat any archive as sensitive: it still holds the auth database (user accounts and sessions).
- **`.dango/cloud.yml`**, your droplet, firewall and key ids. It is local deployment state, so a restore never overwrites your copy.
- `.dlt/pipelines/` (dlt load packages), WAL files, temporary files and directories (`*.wal`, `*.tmp`, `.tmp`), runtime state, logs of script runs, `dbt/target/` and `dbt/dbt_packages/`.

!!! warning "Secrets are not in backups, and a restore needs them"
    The manifest of every backup lists the **names** (never the values) of the variables in the server `.env` and the keys in `.dlt/secrets.toml`. `dango remote backup download` and `restore` print `secrets are not in this backup; re-enter: <names>`. Before `dango deploy destroy`, `dango remote resize` and `dango remote backup restore` ask for confirmation, they remind you that these files are not in backups and list the names the server holds, so you can keep the values somewhere safe first.

!!! warning "Only restore archives you made yourself"
    A backup can contain files that later run as code (scripts, notebooks, models). Restore only archives you created.

---

## Backup Format

Backups are stored as compressed tar archives:

- **Filename:** `backup-YYYYMMDD-HHMMSS.tar.gz` (e.g., `backup-20260515-020000.tar.gz`)
- **Manifest:** `backup-YYYYMMDD-HHMMSS.json` (metadata: timestamp, type, Dango version, file list, and `secret_names` / `secrets_included`)
- **Server location:** `/srv/dango/backups/deploy/`

### Retention

- `dango remote backup` and the daily timer upload the archive to Spaces, verify its size, then remove the local copy and its manifest from the server. Without a Spaces destination the archive stays in `/srv/dango/backups/deploy/`.
- If a Spaces upload cannot be verified, the archive and its manifest stay on the server, older Spaces backups are not pruned, and the run is recorded as failed (`last_error` and `consecutive_failures` in `/srv/dango/backups/.backup_health.json` on the server). Download a copy with `dango remote backup download --from-server -o <file>` and check the Spaces credentials and bucket.
- Backups made automatically by `dango remote push`, `upgrade`, `resize` and `backup restore` stay on the server, and only the newest archive is kept (older ones are deleted after each such backup).
- Spaces backups follow daily/weekly/monthly tiers (default 7 daily, 4 weekly, monthly off); see [Retention and secrets settings](#retention-and-secrets-settings).

---

## On-Demand Backup

Create a backup immediately:

```bash
dango remote backup
```

```
Backup completed successfully.
Off-site: yes (Spaces my-dango-backups)
```

Without a Spaces destination the last line reads `Off-site: NO: backups exist only on this server and are lost with it`, followed by the `dango remote backup download --from-server -o <file>` command.

**Backup workflow:**

1. Take the backup lock (if another backup is already running, this one fails with "Another backup is already running")
2. Stop dango-web and Metabase (prevents concurrent writes)
3. Checkpoint DuckDB (`CHECKPOINT`) and the auth database (`PRAGMA wal_checkpoint(TRUNCATE)`)
4. Stage the files into a private temporary directory
5. Create the manifest (file list, secret names)
6. Compress into a `.tar.gz` archive
7. Restart services
8. Upload to Spaces, verify the size, apply retention and remove the local copy (when a Spaces destination is configured)

---

## Listing Backups

View all available backups on the server and in Spaces:

```bash
dango remote backup list
```

```
                  Backups
Source   Name                            Size
server   backup-20260515-143000.tar.gz   256.0 MB
spaces   backup-20260513-020000.tar.gz   249.0 MB
spaces   backup-20260512-020000.tar.gz   247.0 MB
```

Backups on the server are available for immediate rollback. Backups in Spaces must be downloaded or restored via `dango remote backup restore`.

---

## Scheduled Backups

### Enable

Set up automatic daily backups:

```bash
dango remote backup enable
```

```
Scheduled backups enabled. Daily at 02:00 UTC.
  Timer: dango-backup.timer
  Service: dango-backup.service
Off-site: yes (Spaces my-dango-backups)
```

=== "DigitalOcean"

    `dango deploy` writes the bucket and region you chose to the server `.env` (`SPACES_BUCKET`, `SPACES_REGION`). The Spaces keys must be in the server `.env` as well:

    ```bash
    dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
    dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
    ```

    If the server lacks the destination, `dango remote backup enable` writes it from the `spaces:` section of your local `.dango/cloud.yml`. If a bucket is configured but either key is missing, the command stops with `SPACES_ACCESS_KEY not found in server .env file` (or the secret key) and does not enable the timer.

=== "BYOS"

    `dango remote backup enable` works on a BYOS server, but there is no Spaces destination unless you configure one yourself, so the command reports `Off-site: NO` and the backups stay on the server and are lost with it. To send them to Spaces (a DigitalOcean Spaces bucket you created), set all four variables:

    ```bash
    dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
    dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
    dango remote env set SPACES_REGION=nyc3
    dango remote env set SPACES_BUCKET=my-dango-backups
    ```

    Whether or not you do, download copies regularly with `dango remote backup download --from-server -o <file>`.

**What happens:**

- Creates a systemd timer (`dango-backup.timer`) that fires daily at **02:00 UTC**
- Each backup is created on the server, then uploaded to Spaces and verified
- Spaces backups are pruned by the retention tiers below
- `dango remote status` shows the `Off-site:` line and whether the timer is enabled

### Disable

```bash
dango remote backup disable
```

Stops the systemd timer. Existing backups (local and Spaces) are not deleted.

---

## Downloading Backups

### From the server (no Spaces needed)

Create a backup on the server and download it over SSH:

```bash
dango remote backup download --from-server -o ./backup.tar.gz
```

```
Downloaded. Saved to ./backup.tar.gz (256.0 MB)
Note: secrets are not in this backup; re-enter: DANGO_ADMIN_EMAIL, SPACES_ACCESS_KEY, SPACES_SECRET_KEY
```

This works for DigitalOcean and BYOS servers and is the way to keep a copy of a BYOS backup, which otherwise lives only on the server. It warns when the server disk is more than 50% full. Without `-o` the file is saved in the current directory under its archive name.

### From Spaces

Download a backup from Spaces to your local machine:

```bash
dango remote backup download backup-20260515-020000.tar.gz
dango remote backup download backup-20260515-020000.tar.gz -o ~/backups/dango-backup.tar.gz
```

| Argument/Option | Description |
|-----------------|-------------|
| `NAME` | Backup filename (required unless `--from-server` is used) |
| `-o`, `--output` | Local destination path (default: current directory) |
| `--from-server` | Create a backup on the server and download it over SSH instead of using Spaces |

When the archive does not contain secrets, the command prints the names to re-enter. The archive's manifest lists only names, never values.

---

## Restoring from Backup

!!! danger "Destructive Operation"
    Restoring from a backup **overwrites all current data** on the server, including the DuckDB warehouse, Metabase configuration and auth database. Secrets (`.env`, `.dlt/secrets.toml`) are never restored from an archive. This cannot be undone.

Before it asks for confirmation, `dango remote backup restore` reminds you that `.env` and `.dlt/secrets.toml` are not in backups by default and lists the secret names the server holds (names only). On a BYOS server it also reminds you that backups on the server are lost with it.

Restore from a Spaces backup:

```bash
dango remote backup restore backup-20260515-020000.tar.gz
```

Restore from a file on your machine (for example one downloaded before `dango deploy destroy`):

```bash
dango remote backup restore ./backup.tar.gz --from-local
```

A successful restore prints `Restore complete.`, any warnings the restore produced, and `secrets are not in this backup; re-enter: <names>`. A restore never turns authentication off on a server.

| Argument/Option | Description |
|-----------------|-------------|
| `SOURCE` | Backup filename in Spaces, or a local `.tar.gz` path with `--from-local` |
| `--yes`, `-y` | Skip confirmation prompt |
| `--from-local` | Upload a local backup file to the server and restore from it |

A Spaces backup name may contain only alphanumeric characters, hyphens, underscores, and dots.

### Restore refuses when Metabase has no volume

An archive that holds Metabase data is refused, before anything is stopped or changed, if the server has no Metabase Docker volume to put it in (for example on a server that has never started Metabase). The message is:

```
The Metabase Docker volume does not exist on this server, so the Metabase data in this backup cannot be restored and Metabase would start empty. Nothing was restored. Restart dango-web on the server (systemctl restart dango-web) so Dango recreates the volume, then run the restore again.
```

Follow the advice (`dango remote ssh`, then `systemctl restart dango-web`) and run the restore again.

---

## Automatic Backups

Dango automatically creates backups during certain operations:

| Trigger | Backup Type | When |
|---------|------------|------|
| `dango remote push` | Pre-deploy | Before applying file changes |
| `dango remote upgrade` | Pre-upgrade | Before upgrading Dango version |
| `dango remote resize` | Pre-resize | Before resizing the server |
| `dango remote backup restore` | Pre-restore | Safety copy of the current state before a restore overwrites it |

These automatic backups use the same archive format, stay on the server, and only the newest archive is kept (see [Retention](#retention)). You can roll back to the pre-deploy and pre-upgrade backups using `dango remote rollback`.

---

## Retention and secrets settings

`dango remote backup config` shows the `backup:` section of your **local** `.dango/cloud.yml`:

```yaml
backup:
  include_secrets: false
  on_server_retention: 1
  spaces_retention:
    daily: 7
    weekly: 4
    monthly: 0
```

The scheduled and on-demand server-side backup reads `include_secrets` and `spaces_retention` from `.dango/cloud.yml` **on the server** (`/srv/dango/project/.dango/cloud.yml`). `dango remote push` does not upload `.dango/cloud.yml`, so a setting that exists only in your local file does not change the backups the server makes. Backups started by push, upgrade, resize and restore always exclude secrets and keep only the newest archive: the `on_server_retention` value shown by `backup config` is not read by those commands.

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

Ensure `SPACES_ACCESS_KEY` and `SPACES_SECRET_KEY` are set, and that `SPACES_BUCKET` (and `SPACES_REGION`) name your bucket.

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
- The backups were uploaded to Spaces and removed from the server: use `dango remote backup list` (it lists both) or download from Spaces
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
- [Server Operations](server-operations.md): upgrade, resize, and moving to a new server
- [Destroy & Cleanup](destroy.md) &mdash; tear down a deployment
