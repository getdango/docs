# Deployment

Deploy Dango to the cloud for team access, scheduled syncs, and always-on dashboards.

---

## Deployment Paths

Dango offers two deployment paths. Both result in the same server setup &mdash; the difference is who provisions the infrastructure.

| | DigitalOcean | Bring Your Own Server |
|---|---|---|
| **What it does** | Provisions a droplet, configures everything | Installs Dango on your existing server |
| **Prerequisites** | DO account + API token | Ubuntu 22.04+ server with SSH access |
| **Cloud firewall** | Managed by Dango (`dango remote firewall`) | You manage (UFW installed automatically) |
| **Automated backups** | DO Spaces (optional, ~$5/mo) | Not included (manual snapshots) |
| **Server destruction** | `dango deploy destroy` removes everything | Your responsibility |
| **Cost** | $24&ndash;$48/mo (droplet) + optional backups | Your server costs |
| **Best for** | Quick setup, no existing infrastructure | AWS, GCP, Hetzner, on-premise, etc. |

## Quick Start

=== "DigitalOcean"

    ```bash
    dango deploy
    ```

    The interactive wizard walks you through region, server size, admin account, and cost confirmation. See the [DigitalOcean guide](digitalocean.md) for the full walkthrough.

=== "Bring Your Own Server"

    ```bash
    dango deploy --byos
    ```

    Connects to your server via SSH and installs everything. See the [BYOS guide](byos.md) for server requirements and the full walkthrough.

## What Gets Deployed

Both paths set up the same server environment: Python venv, DuckDB warehouse, dbt project, Metabase (Docker), Caddy (reverse proxy + auto-TLS), fail2ban, systemd service, and unattended security upgrades. See the [detailed server layout](digitalocean.md#remote-server-layout) for the full directory structure.

## Deployment Commands

| Command | Description |
|---------|-------------|
| `dango deploy` | Deploy to DigitalOcean (interactive wizard) |
| `dango deploy --byos` | Deploy to an existing server |
| `dango deploy --reconnect --ip <IP>` | Reconnect to an existing deployment |
| `dango remote push` | Push config and dbt files to the server |
| `dango remote status` | Check server health and service status |
| `dango remote logs` | View server logs |
| `dango remote ssh` | Open an SSH session to the server |
| `dango deploy destroy` | Destroy DigitalOcean droplet (irreversible) |

## After Deployment

Once your server is running, you'll typically want to:

1. **Verify** the deployment is healthy &mdash; `dango remote status`
2. **Configure a domain** for HTTPS &mdash; `dango remote domain set <domain>`
3. **Set up firewall rules** to restrict access &mdash; `dango remote firewall` (DO) or UFW (BYOS)
4. **Re-authenticate OAuth sources** with the new redirect URI
5. **Configure scheduled syncs** via the web UI or `dango schedule`

See [Post-Deploy Setup](post-deploy.md) for the complete walkthrough.

## The Push Model

Dango uses a **push model** for deployments. Your local machine is the source of truth for configuration and dbt files:

```bash
# Edit locally
vim .dango/sources.yml
vim dbt_project/models/staging/stg_orders.sql

# Push changes to server
dango remote push
```

`dango remote push` syncs configuration files and dbt project files. It does **not** sync credentials &mdash; manage those separately via the web UI secrets page or `dango remote env set`.

!!! warning "Credentials are never pushed"
    `.env`, `.dlt/secrets.toml`, and the DuckDB warehouse file are excluded from push. Credentials on the server are managed independently to prevent accidental overwrites.

## Related

- [DigitalOcean Guide](digitalocean.md) &mdash; full wizard walkthrough with all options
- [Bring Your Own Server](byos.md) &mdash; deploy to any Ubuntu server
- [Post-Deploy Setup](post-deploy.md) &mdash; domain, HTTPS, firewall, OAuth
- [Remote Management](remote-management.md) &mdash; managing your deployed server
- [Local vs Cloud](../core-concepts/local-vs-cloud.md) &mdash; behavioral differences between environments
