# Remote Management

Manage your cloud deployment with `dango remote` commands.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote push` | Push local config and dbt files to server |
| `dango remote rollback` | Restore from a backup |
| `dango remote status` | Show server status, services, and resources |
| `dango remote logs` | View service logs |
| `dango remote ssh` | Open interactive SSH session |
| `dango remote query "SQL"` | Run a read-only SQL query on the warehouse |
| `dango remote history` | View deployment history |
| `dango remote auth add-user` | Add a web UI user |
| `dango remote auth list-users` | List web UI users |
| `dango remote auth remove-user` | Remove a web UI user |
| `dango remote auth reset-password` | Reset a user's password |
| `dango remote repair` | Diagnose and fix common deployment issues |
| `dango remote reset-metabase` | Reset Metabase to fresh state (SSO/H2 corruption) |

All commands require an active deployment (`.dango/cloud.yml` must exist). They work the same for both DigitalOcean and BYOS deployments &mdash; all communication happens over SSH.

---

## Pushing Changes

After making local changes to configuration or dbt models, push them to the server:

```bash
dango remote push
```

### What Gets Synced

**Config files** (uploaded via SFTP):

| Local Path | Remote Path |
|-----------|-------------|
| `.dango/sources.yml` | `/srv/dango/project/.dango/sources.yml` |
| `.dango/schedules.yml` | `/srv/dango/project/.dango/schedules.yml` |
| `.dango/monitors.yml` | `/srv/dango/project/.dango/monitors.yml` |
| `.dango/project.yml` | `/srv/dango/project/.dango/project.yml` |
| `dbt/dbt_project.yml` | `/srv/dango/project/dbt/dbt_project.yml` |
| `dbt/packages.yml` | `/srv/dango/project/dbt/packages.yml` |
| `docker-compose.yml` | `/srv/dango/project/docker-compose.yml` |
| `Dockerfile.metabase` | `/srv/dango/project/Dockerfile.metabase` |
| `entrypoint.sh` | `/srv/dango/project/entrypoint.sh` |
| `metabase-plugins/` | `/srv/dango/project/metabase-plugins/` |

**dbt directories** (synced via rsync with `--delete`):

- `dbt/models/` &mdash; all model SQL files
- `dbt/macros/` &mdash; all macro SQL files

Files that don't exist locally are skipped.

### What Is NOT Synced

These files are managed separately and never overwritten by push:

- `.env` &mdash; environment variables (see [Environment Variables](environment-variables.md))
- `.dlt/secrets.toml` &mdash; API credentials
- `warehouse.duckdb` &mdash; the DuckDB database
- Metabase H2 database &mdash; Metabase configuration and saved questions
- `dbt/profiles.yml` &mdash; auto-generated for server hardware

### Git Guardrails

By default, `dango remote push` checks your git state before deploying:

- **Branch check** &mdash; warns if you're not on the expected branch (e.g., `main`)
- **Dirty check** &mdash; warns if you have uncommitted changes

Override with flags:

```bash
# Allow uncommitted changes
dango remote push --allow-dirty

# Allow deployment from any branch
dango remote push --allow-branch

# Both
dango remote push --allow-dirty --allow-branch
```

### Pre-Deploy Backup

Every push automatically creates a backup on the server before applying changes. This backup is used by `dango remote rollback` if something goes wrong.

### Deploy Lock

Only one push can run at a time. If another push is in progress, you'll see an error. Use `--force` to override a stale lock:

```bash
dango remote push --force
```

!!! warning
    Only use `--force` if you are certain no other push is in progress. Forcing during an active push could leave the server in an inconsistent state.

### Dry Run

Preview what would be synced without making changes:

```bash
dango remote push --dry-run
```

This shows which files changed, which dbt models were added/modified/removed, and whether macros or packages changed &mdash; without uploading anything.

### Push Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show changes without applying |
| `--force` | Override an existing deploy lock |
| `--yes`, `-y` | Skip confirmation prompt |
| `--allow-dirty` | Allow deployment with uncommitted changes |
| `--allow-branch` | Allow deployment from any branch |

### Change Detection

Push uses MD5 hashing to detect changes:

- **Model changes** &mdash; individual `*.sql` files in `dbt/models/` are compared. Changed models trigger selective `dbt run --select`
- **Macro changes** &mdash; any change in `dbt/macros/` triggers a full `dbt run` (macros aren't individually selectable)
- **Package changes** &mdash; if `dbt/packages.yml` changed, `dbt deps` runs before `dbt run`
- **First deploy** &mdash; all local models are treated as "added" and a full `dbt run` executes

### Example Output

```
Syncing project files...
  ✓ .dango/sources.yml (changed)
  ✓ .dango/schedules.yml (unchanged, skipped)
  ✓ dbt/models/staging/stg_stripe_charges.sql (new)
  ✓ dbt/models/marts/mrr.sql (changed)

Changes detected:
  Added models: stg_stripe_charges
  Changed models: mrr
  Packages: unchanged

Creating pre-deploy backup...
  ✓ Backup: backup-20260515-143000.tar.gz

Running dbt...
  ✓ dbt run --select stg_stripe_charges mrr
  ✓ 2 models completed

Deploy complete.
```

---

## Rolling Back

Restore the server to its state before the last push:

```bash
dango remote rollback
```

This uses the most recent pre-deploy backup. To restore from a specific backup:

```bash
dango remote rollback --backup /srv/dango/backups/deploy/backup-20260515-143000.tar.gz
```

**Rollback workflow:**

1. Stop services (dango-web, Metabase)
2. Extract backup archive
3. Restore all files (config, database, Metabase data)
4. Restart services
5. Verify health

| Option | Description |
|--------|-------------|
| `--backup` | Path to a specific backup archive (default: most recent) |
| `--yes`, `-y` | Skip confirmation prompt |

---

## Checking Status

View a comprehensive overview of your deployment:

```bash
dango remote status
```

**Output panels:**

| Panel | Information |
|-------|-------------|
| **Server** | IP address, region, size (tier + price/mo), domain |
| **Services** | Status of dango-web, Caddy, Metabase (running/stopped) |
| **Resources** | CPU %, RAM usage/total (%), disk usage/total (%) |
| **Data** | DuckDB database size, last sync timestamp per source |
| **Versions** | Installed Dango version vs. latest on PyPI, upgrade available warning |
| **Last Deployment** | Git commit (short SHA), branch, deployer, timestamp |
| **Backup** | Last backup timestamp (or "No backups found" warning) |

```
Server: 143.198.xxx.xxx
Region: nyc1 (New York 1)
Size:   Standard (s-2vcpu-4gb) — $24/mo
Domain: analytics.yourcompany.com

Services:
  ✓ Dango web server (running)
  ✓ Metabase (running)
  ✓ Caddy (running)

Resources:
  CPU:  12%
  RAM:  1.8 GB / 4.0 GB (45%)
  Disk: 14.2 GB / 80.0 GB (18%)

Data:
  DuckDB: 256 MB
  Last sync: stripe (2 hours ago), hubspot (6 hours ago)

Versions:
  Installed: 1.0.0
  Latest:    1.0.0

Last Deployment:
  Commit: a1b2c3d (main)
  By: deploy@local
  At: 2026-05-15 14:30:00

Backup:
  Last: backup-20260515-020000.tar.gz (13 hours ago)
```

---

## Viewing Logs

View service logs from the server:

```bash
# Dango web server logs (default)
dango remote logs

# Specific service
dango remote logs --service caddy
dango remote logs --service metabase

# Last 100 lines
dango remote logs --tail 100

# Stream logs in real-time (Ctrl+C to stop)
dango remote logs --follow
```

| Option | Description |
|--------|-------------|
| `--service` | Service to view: `dango`, `caddy`, or `metabase` (default: `dango`) |
| `--tail` | Number of log lines to show (default: 50) |
| `--follow`, `-f` | Stream logs in real-time |

**Log sources by service:**

| Service | Log Command |
|---------|-------------|
| `dango` | `journalctl -u dango-web` |
| `caddy` | `journalctl -u caddy` |
| `metabase` | `docker logs metabase` |

---

## Interactive SSH

Open an interactive SSH session to the server:

```bash
dango remote ssh
```

This connects as `root` with full shell access. The command replaces your current process &mdash; when you exit the SSH session, you're back in your local terminal.

!!! tip
    Use SSH for tasks that aren't covered by the CLI, such as inspecting system logs, debugging services, or checking disk usage.

---

## Querying Data

Run a read-only SQL query against the remote DuckDB warehouse:

```bash
dango remote query "SELECT count(*) FROM stripe.charges"
```

```bash
dango remote query "SELECT * FROM hubspot.contacts LIMIT 10" --timeout 120
```

| Argument/Option | Description |
|-----------------|-------------|
| `sql` | SQL query to execute (required) |
| `--timeout` | Query timeout in seconds (default: 60) |

The query runs in read-only mode &mdash; INSERT, UPDATE, DELETE, and other write operations are rejected by DuckDB's `access_mode=read_only` setting.

---

## Deployment History

View a log of all deployments to the server:

```bash
dango remote history
```

```bash
# Show last 20 entries
dango remote history --limit 20
```

| Option | Description |
|--------|-------------|
| `--limit`, `-n` | Number of entries to show (default: 10) |

**Output columns:**

| Column | Description |
|--------|-------------|
| Time | Deployment timestamp (ISO format) |
| Commit | Git commit short SHA (8 chars) |
| Branch | Git branch name |
| Deployer | Who triggered the deploy |
| Duration | How long the deploy took |
| Status | OK (green) or FAIL (red) |

```
Time                 Commit    Branch  Deployer       Duration  Status
2026-05-15 14:30:00  a1b2c3d4  main    deploy@local   45s       OK
2026-05-14 10:15:00  e5f6g7h8  main    deploy@local   1m 12s    OK
2026-05-13 16:45:00  i9j0k1l2  main    deploy@local   38s       FAIL
```

---

## Recovery Commands

When things go wrong, these commands fix common issues without SSH access:

### Repair

```bash
dango remote repair
```

Diagnoses and fixes common deployment issues: checks disk space, RAM, DNS resolution, restarts services, re-runs Metabase setup if `metabase.yml` is missing, and triggers a Metabase schema scan. **Run this first** when something isn't working.

### Reset Metabase

```bash
dango remote reset-metabase
```

Resets Metabase to a fresh state when SSO breaks or the H2 database corrupts. Stops Metabase, removes its Docker volume, restarts it, and lets `dango-web` re-run Metabase setup on next startup. **Does not affect your warehouse data** &mdash; only Metabase's internal state (saved questions, dashboards) is lost. Re-import with `dango metabase load` after reset.

!!! tip "Try repair first"
    `dango remote repair` fixes most issues. Only use `dango remote reset-metabase` if Metabase is completely broken (SSO loop, database corruption errors, blank screen after login).

---

## Remote User Management

Manage web UI user accounts on the server. These commands run remotely &mdash; they modify the authentication database on the server, not locally.

### Add a User

```bash
dango remote auth add-user
```

Prompts for email and password interactively.

### List Users

```bash
dango remote auth list-users
```

Shows all registered users with their email, role, and creation date.

### Remove a User

```bash
dango remote auth remove-user
```

Prompts to select a user for removal.

### Reset Password

```bash
dango remote auth reset-password
```

Prompts to select a user and enter a new password.

---

## Troubleshooting

### Deploy lock stuck

```
Error: Deploy lock is held by another process
```

If no other push is running, the lock may be stale from a previous push that was interrupted:

!!! warning
    Only delete the lock file if you are certain no push is in progress.

```bash
dango remote ssh
```

Then on the server:

```bash
rm /srv/dango/.dango/state/deploy.lock
```

### SSH connection failed

```
Error: SSH connection failed
```

- Verify the server is running: check your cloud provider's console
- Check that port 22 is open in the firewall
- Verify the SSH key exists locally: `ls ~/.ssh/dango_*`
- Test connectivity manually: `ssh -i ~/.ssh/dango_ed25519 root@<server-ip>`

### Push failed mid-deploy

If a push fails partway through (e.g., network interruption), the server may be in a partially updated state:

1. Check server status: `dango remote status`
2. If services are running, try pushing again: `dango remote push --force`
3. If services are down, roll back: `dango remote rollback`
4. Check logs for errors: `dango remote logs`

### Query timeout

```
Error: Query timed out after 60 seconds
```

Increase the timeout for complex queries:

```bash
dango remote query "SELECT ..." --timeout 300
```

If queries consistently time out, consider [resizing the server](server-operations.md) for more CPU and RAM.

### Git guardrails blocking push

```
Warning: You have uncommitted changes
```

Either commit your changes or override:

```bash
# Commit first (recommended)
git add -A && git commit -m "Update models"
dango remote push

# Or override
dango remote push --allow-dirty --allow-branch
```

---

## Next Steps

- [Environment Variables](environment-variables.md) &mdash; manage secrets on the server
- [Backups](backups.md) &mdash; configure automated backups and restore
- [Server Operations](server-operations.md) &mdash; upgrade, resize, and migrate
- [Destroy & Cleanup](destroy.md) &mdash; tear down a deployment
