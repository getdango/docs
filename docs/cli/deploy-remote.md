# Deploy & Remote

Deploy to the cloud and manage remote servers from the CLI.

---

## Overview

The `dango deploy` command provisions cloud infrastructure and deploys your project. The `dango remote` commands manage the deployed server — push updates, view logs, manage backups, configure firewalls, and more.

**Deploy commands:**

- `dango deploy` — Interactive deployment wizard
- `dango deploy destroy` — Tear down cloud infrastructure

**Remote commands (15+ subcommands across 5 groups):**

- Core: `push`, `rollback`, `status`, `logs`, `ssh`, `query`, `upgrade`, `power-on`, `resize`, `migrate` (switched off in 1.0.14), `history`, `sync`, `upload`, `isolation`
- Environment: `env set/get/list/delete`
- Firewall: `firewall list/allow-ip/allow-all`
- Domain: `domain set/remove`
- Backup: `backup list/enable/disable/download/restore/verify-metabase/config`
- Auth: `auth add-user/list-users/remove-user/reset-password`

---

## Deployment

### dango deploy

Interactive deployment wizard. Supports DigitalOcean provisioning, BYOS (bring your own server), and reconnection to existing servers.

```bash
dango deploy [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--non-interactive` | All params via flags/env (DigitalOcean only) |
| `--reconnect` | Reconnect to an existing server |
| `--ip TEXT` | Server IP for `--reconnect` |
| `--region TEXT` | DO region slug |
| `--size TEXT` | Droplet size slug |
| `--domain TEXT` | Custom domain for HTTPS |
| `--admin-email TEXT` | Admin user email |
| `--admin-password TEXT` | Admin password (or `DANGO_ADMIN_PASSWORD` env var) |
| `--skip-backups` | Skip automated backup setup |
| `--byos` | Deploy to an existing server (any provider) |
| `--server-ip TEXT` | Server IP/hostname for `--byos` |
| `--ssh-user TEXT` | SSH user for `--byos` |
| `--ssh-key TEXT` | SSH key path for `--byos` |
| `--allow-ip IPv4_OR_CIDR` | Without a domain, restrict DigitalOcean web ports to this address (repeatable) |
| `--accept-http-exposure` | Acknowledge plain HTTP with web ports open to the internet |

Without a domain, a non-interactive DigitalOcean deployment requires `--allow-ip` or `--accept-http-exposure`. BYOS refuses `--allow-ip`: configure your own firewall and use `--accept-http-exposure` if deploying without a domain. The interactive DigitalOcean wizard also offers `detect`, which uses the IP address seen by the server.

=== "Interactive (DigitalOcean)"

    ```bash
    dango deploy
    ```

    The wizard guides you through region selection, server sizing, domain setup, and admin account creation.

=== "Non-Interactive (DigitalOcean)"

    ```bash
    dango deploy --non-interactive \
      --region nyc3 \
      --size s-2vcpu-4gb \
      --admin-email admin@example.com \
      --admin-password mypassword
    ```

=== "BYOS (Your Own Server)"

    ```bash
    dango deploy --byos \
      --server-ip 203.0.113.42 \
      --ssh-user deploy \
      --ssh-key ~/.ssh/id_ed25519
    ```

=== "Reconnect"

    ```bash
    dango deploy --reconnect --ip 203.0.113.42
    ```

---

### dango deploy destroy

Tear down all cloud infrastructure for this project.

```bash
dango deploy destroy [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--force` | Skip confirmation and backup prompts |
| `--delete-spaces` | Also delete the Spaces bucket and its contents (kept by default) |
| `--keep-ssh-key` | Keep the SSH key on DigitalOcean |

=== "DigitalOcean"

    Deletes the droplet, firewall and SSH key (from DO). The Spaces bucket is kept unless `--delete-spaces` is given. Local SSH keys and project files are never deleted.

=== "BYOS"

    Stops Dango, removes its Docker containers, volumes and images, `/srv/dango`, the `dango` user and the Caddy configuration from the server, and removes the local `cloud.yml`. The machine itself is not deleted. No backup download is offered, and BYOS backups are deleted with the server.

!!! danger
    This is a destructive operation. Before asking for confirmation, Dango reminds you that `.env` and `.dlt/secrets.toml` are not in backups by default and lists the secret names (never the values) the server holds. Download a backup first with `dango remote backup download --from-server -o <file>`.

```bash
dango deploy destroy
dango deploy destroy --force
dango deploy destroy --delete-spaces --keep-ssh-key
```

---

## Remote Server Management

### dango remote status

Show server status, resource usage (CPU, RAM, disk), service health, DuckDB size, the `Off-site:` backup line, version info, Docker access state and script/notebook `Isolation:` state. On DigitalOcean it also warns about droplets tagged `dango` that `cloud.yml` does not name.

```bash
dango remote status
```

---

### dango remote logs

View logs from a remote service.

```bash
dango remote logs [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--service [dango\|caddy\|metabase]` | `dango` | Service to view logs for |
| `--tail INTEGER` | — | Number of log lines to show |
| `-f`, `--follow` | — | Stream logs in real-time (Ctrl+C to stop) |

```bash
dango remote logs
dango remote logs --service caddy --tail 20
dango remote logs -f
```

---

### dango remote ssh

Open an interactive SSH session to the remote server. Replaces the current process with SSH, providing full TTY support.

```bash
dango remote ssh
```

---

### dango remote query

Run a read-only SQL query against the remote DuckDB database.

```bash
dango remote query SQL [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--timeout INTEGER` | Query timeout in seconds |

The query runs in read-only mode — INSERT/UPDATE/DELETE are rejected.

```bash
dango remote query "SELECT count(*) FROM information_schema.tables"
dango remote query "SELECT * FROM raw.my_table LIMIT 10" --timeout 120
```

---

### dango remote push

Push local project files to the remote server and rebuild.

```bash
dango remote push [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--dry-run` | Show changes without applying |
| `--force` | Override an existing deploy lock |
| `-y`, `--yes` | Skip confirmation prompt |
| `--allow-dirty` | Allow deployment with uncommitted changes |
| `--allow-branch` | Allow deployment from any branch |

Syncs config and dbt files, creates a pre-deploy backup, runs `dbt compile`, and selectively rebuilds changed models.

```bash
dango remote push
dango remote push --dry-run
dango remote push --force --yes
dango remote push --allow-dirty --allow-branch
```

!!! tip
    By default, `dango remote push` checks for uncommitted changes and the current branch. Use `--allow-dirty` and `--allow-branch` to override these guardrails.

---

### dango remote rollback

Restore the remote server from a backup.

```bash
dango remote rollback [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--backup TEXT` | Path to a specific backup archive (defaults to most recent) |
| `-y`, `--yes` | Skip confirmation prompt |

Stops services, restores the backup, then restarts and verifies health.

```bash
dango remote rollback
dango remote rollback --backup /srv/dango/backups/deploy/backup-20260224-143000.tar.gz
```

---

### dango remote upgrade

Upgrade Dango on the remote server.

```bash
dango remote upgrade [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--version TEXT` | Specific version (defaults to latest on PyPI) |
| `-y`, `--yes` | Skip confirmation prompt |
| `--skip-backup` | Skip the pre-upgrade backup |
| `--force` | Allow a downgrade to an older version |

Upgrade your local `dango` first. See [Server Operations](../deployment/server-operations.md#upgrading-dango) for the workflow, the 1.0.14 notes (Python on the server, custom Metabase pin, interrupted upgrades) and what a failed upgrade leaves.

---

### dango remote power-on

Power on a DigitalOcean droplet left off by an interrupted resize, then start services. It uses the DigitalOcean API, so it works when SSH cannot connect. Not available for BYOS.

```bash
dango remote power-on
```

---

### dango remote upload

Upload one file into the server project's `data/` directory.

```bash
dango remote upload LOCAL_PATH [REMOTE_PATH]
```

`REMOTE_PATH` is relative to the project root and must be under `data/` (default: the file's own path inside the project). Single regular files up to 2 GiB; `data/warehouse.duckdb*` and `data/.tmp` are refused. See [Remote Management](../deployment/remote-management.md#upload-one-data-file).

---

### dango remote isolation

Inspect, opt out of, and restore the restricted users that run scripts and notebooks on the server.

```bash
dango remote isolation status         # on | disabled | missing | unknown | unsupported
dango remote isolation disable --yes  # audited administrator opt-out
dango remote isolation enable         # remove the opt-out and verify isolation
```

See [Script and notebook isolation](../deployment/server-operations.md#script-and-notebook-isolation).

---

### dango remote resize

Resize the remote server (change CPU/RAM).

```bash
dango remote resize [SIZE]
```

| Parameter | Description |
|-----------|-------------|
| `SIZE` | Droplet size slug. If omitted, shows current spec and available tiers |
| `-y`, `--yes` | Skip confirmation prompt |

---

### dango remote migrate

**Switched off in 1.0.14.** The command refuses before it contacts any server or provider, exits with status 1, and prints the manual path. It returns in a later release.

```bash
dango remote migrate
```

Options (`--size`, `--region`, `--yes`) are accepted and ignored. To change the server size, use [`dango remote resize`](#dango-remote-resize). To move to another server or region:

1. `dango remote backup download --from-server -o ./backup.tar.gz`
2. `dango deploy destroy`
3. `dango deploy`
4. `dango remote backup restore ./backup.tar.gz --from-local`
5. Re-enter secrets (they are not in backups by default) and update DNS.

See [Moving to a New Server](../deployment/server-operations.md#moving-to-a-new-server) for details.

---

### dango remote history

Show deployment history from the remote server's deployment journal.

```bash
dango remote history [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-n`, `--limit INTEGER` | Number of entries to show |

```bash
dango remote history
dango remote history -n 20
```

---

### dango remote sync

Trigger a data sync on the remote cloud server.

```bash
dango remote sync SOURCE [OPTIONS]
```

| Parameter | Description |
|-----------|-------------|
| `SOURCE` | Source name to sync (required) |
| `--full-refresh` | Run a full refresh sync |
| `--backfill TEXT` | Backfill duration (e.g. `7d`, `2w`, `1m`) |
| `--wait` | Wait for sync to complete and show result |

```bash
dango remote sync my_source
dango remote sync my_source --full-refresh --wait
dango remote sync my_source --backfill 7d --wait
```

Without `--wait`, the command launches the sync in the background on the server and checks only the first 2 seconds: it reports a failed start (for example the project directory cannot be entered, or the command exits with an error within that time). A sync that fails later is not reported by this command; check `dango remote status`.

---

## Environment Variables

### dango remote env set

Set an environment variable on the remote server.

```bash
dango remote env set KEY=VALUE
```

```bash
dango remote env set GOOGLE_CLIENT_ID=123456.apps.googleusercontent.com
```

---

### dango remote env get

Display an environment variable (value masked).

```bash
dango remote env get KEY
```

---

### dango remote env list

List all environment variables on the remote server (values masked).

```bash
dango remote env list
```

---

### dango remote env delete

Remove an environment variable from the remote server.

```bash
dango remote env delete KEY
```

---

## Firewall

### dango remote firewall list

Show current inbound and outbound firewall rules.

```bash
dango remote firewall list
```

---

### dango remote firewall allow-ip

Restrict ports 80 and 443 to a specific IP address or CIDR range. SSH (port 22) is always left open.

```bash
dango remote firewall allow-ip IP_ADDRESS
```

```bash
dango remote firewall allow-ip 203.0.113.42          # Single IP (/32)
dango remote firewall allow-ip 203.0.113.0/24        # CIDR range
```

---

### dango remote firewall allow-all

Revert ports 80 and 443 to allow all public traffic.

```bash
dango remote firewall allow-all
```

---

## Domain & HTTPS

### dango remote domain set

Configure HTTPS for a custom domain with automatic Let's Encrypt certificates.

```bash
dango remote domain set DOMAIN_NAME
```

DNS must point `DOMAIN_NAME` to the droplet IP for certificate issuance. If DNS hasn't propagated yet, the configuration is still applied — Caddy retries automatically.

```bash
dango remote domain set app.example.com
```

---

### dango remote domain remove

Revert to IP-only HTTP access. Removes the domain from config and rewrites the Caddyfile for plain HTTP on port 80.

```bash
dango remote domain remove
```

---

## Backups

### dango remote backup

Trigger an on-demand backup on the server. It ends with an `Off-site:` line: `yes (Spaces <bucket>)` or `NO: backups exist only on this server and are lost with it`.

```bash
dango remote backup
```

---

### dango remote backup list

List backups on the server and in Spaces.

```bash
dango remote backup list
```

---

### dango remote backup enable

Enable daily scheduled backups via systemd timer. With a Spaces destination (and both Spaces keys in the server `.env`) backups are uploaded off-site; without one (always the case on BYOS unless you configure it) they stay on the server, and the command prints `Off-site: NO` with the command to keep a copy.

```bash
dango remote backup enable
```

---

### dango remote backup disable

Disable daily scheduled backups.

```bash
dango remote backup disable
```

---

### dango remote backup download

Download a backup archive from Spaces, or create one on the server and download it over SSH with `--from-server` (no Spaces needed; works on BYOS).

```bash
dango remote backup download NAME [OPTIONS]
dango remote backup download --from-server [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-o`, `--output PATH` | Local path to save the backup (defaults to current directory) |
| `--from-server` | Create a backup on the server and download it over SSH instead of using Spaces |

The command prints `secrets are not in this backup; re-enter: <names>` when the archive has no secrets (names only, never values).

```bash
dango remote backup download backup-20260224-143000.tar.gz
dango remote backup download backup-20260224-143000.tar.gz -o ./my-backup.tar.gz
dango remote backup download --from-server -o ./latest-backup.tar.gz
```

---

### dango remote backup restore

Restore the server from a Spaces backup (the server downloads it, then restores it) or from a local file with `--from-local` (the file is uploaded first).

```bash
dango remote backup restore SOURCE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |
| `--from-local` | `SOURCE` is a local `.tar.gz` file to upload and restore |

!!! warning
    Current data on the server will be overwritten. Before asking, the command reminds you that `.env` and `.dlt/secrets.toml` are not in backups and lists the secret names on the server. A backup that holds Metabase data is refused, with nothing changed, if the server has no Metabase Docker volume. See [Backups](../deployment/backups.md#restoring-from-backup).

```bash
dango remote backup restore backup-20260224-143000.tar.gz
dango remote backup restore ./my-backup.tar.gz --from-local
```

---

## Remote User Management

### dango remote auth add-user

Create a new user on the remote server with a temporary password.

```bash
dango remote auth add-user EMAIL [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--role [admin\|editor\|viewer]` | Role for the new user |

```bash
dango remote auth add-user alice@example.com --role editor
```

---

### dango remote auth list-users

List all users on the remote server.

```bash
dango remote auth list-users
```

---

### dango remote auth remove-user

Permanently remove a user from the remote server.

```bash
dango remote auth remove-user EMAIL
```

!!! danger
    This permanently deletes the user and cannot be undone.

---

### dango remote auth reset-password

Reset a user's password on the remote server. Generates a new temporary password.

```bash
dango remote auth reset-password EMAIL
```

### dango remote repair

Diagnose and repair common cloud deployment issues. Checks disk, RAM, DNS, restarts services, re-runs Metabase setup if `metabase.yml` is missing, and triggers a Metabase schema scan.

```bash
dango remote repair
```

---

### dango remote reset-metabase

Reset Metabase to a fresh state without losing warehouse data. Stops Metabase, removes its Docker volume (H2 database), restarts it, and lets `dango-web` re-run Metabase setup on next startup.

```bash
dango remote reset-metabase
```

---

## Troubleshooting

??? info "Deploy fails with SSH connection error"
    Verify the server IP and SSH key. For BYOS, ensure the SSH user has sudo access and port 22 is open.

??? info "Push rejected due to deploy lock"
    Another push may be in progress. Wait for it to complete, or use `--force` to override the lock (only if you're sure no other deploy is running).

??? info "Domain HTTPS not working"
    Ensure DNS is pointed to the server IP. Caddy automatically retries certificate issuance. Check `dango remote logs --service caddy` for details.

??? info "Firewall locked you out"
    SSH (port 22) is always kept open. Connect via `dango remote ssh` and troubleshoot from the server. If needed, use DigitalOcean console access.

??? info "Backup restore fails"
    Ensure Spaces credentials are configured (`SPACES_ACCESS_KEY`, `SPACES_SECRET_KEY`). Check available backups with `dango remote backup list`.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [Auth Commands](auth-commands.md) — Local user management
- [Schedule Commands](schedule-commands.md) — Configure scheduled syncs on the remote server
