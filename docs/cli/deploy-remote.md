# Deploy & Remote

Deploy to the cloud and manage remote servers from the CLI.

---

## Overview

The `dango deploy` command provisions cloud infrastructure and deploys your project. The `dango remote` commands manage the deployed server — push updates, view logs, manage backups, configure firewalls, and more.

**Deploy commands:**

- `dango deploy` — Interactive deployment wizard
- `dango deploy destroy` — Tear down cloud infrastructure

**Remote commands (15+ subcommands across 5 groups):**

- Core: `push`, `rollback`, `status`, `logs`, `ssh`, `query`, `upgrade`, `resize`, `migrate`, `history`, `sync`
- Environment: `env set/get/list/delete`
- Firewall: `firewall list/allow-ip/allow-all`
- Domain: `domain set/remove`
- Backup: `backup list/enable/disable/download/restore`
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
| `--skip-initial-sync` | Skip initial data sync |
| `--byos` | Deploy to an existing server (any provider) |
| `--server-ip TEXT` | Server IP/hostname for `--byos` |
| `--ssh-user TEXT` | SSH user for `--byos` |
| `--ssh-key TEXT` | SSH key path for `--byos` |

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
| `--keep-spaces` | Keep the Spaces bucket and its contents |
| `--keep-ssh-key` | Keep the SSH key on DigitalOcean |

=== "DigitalOcean"

    Deletes the Droplet, firewall, SSH key (from DO), and Spaces bucket. Local SSH keys and project files are never deleted.

=== "BYOS"

    Optionally stops remote services and removes local `cloud.yml`.

!!! danger
    This is a destructive operation. For DigitalOcean deployments, the server and all its data will be permanently deleted.

```bash
dango deploy destroy
dango deploy destroy --force
dango deploy destroy --keep-spaces --keep-ssh-key
```

---

## Remote Server Management

### dango remote status

Show server status, resource usage (CPU, RAM, disk), service health, DuckDB size, and version info.

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

Migrate to a new server (new droplet for disk/region changes). Transfers data via Spaces.

```bash
dango remote migrate [OPTIONS]
```

| Option | Required | Description |
|--------|----------|-------------|
| `--size TEXT` | Yes | Size slug for the new server |
| `--region TEXT` | No | Region slug (defaults to current region) |
| `-y`, `--yes` | No | Skip confirmation prompt |

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

### dango remote backup list

List backups on the server and in Spaces.

```bash
dango remote backup list
```

---

### dango remote backup enable

Enable daily scheduled backups via systemd timer. Requires Spaces to be configured.

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

Download a backup archive from Spaces.

```bash
dango remote backup download NAME [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-o`, `--output PATH` | Local path to save the backup (defaults to current directory) |

```bash
dango remote backup download backup-20260224-143000.tar.gz
dango remote backup download backup-20260224-143000.tar.gz -o ./my-backup.tar.gz
```

---

### dango remote backup restore

Restore the server from a Spaces backup. Downloads the backup to the server, then restores it.

```bash
dango remote backup restore SOURCE [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `-y`, `--yes` | Skip confirmation prompt |

!!! warning
    Current data on the server will be overwritten.

```bash
dango remote backup restore backup-20260224-143000.tar.gz
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
