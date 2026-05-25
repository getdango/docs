# DigitalOcean

Deploy Dango to a DigitalOcean droplet with the guided wizard.

---

## Prerequisites

Before deploying, make sure you have:

- [ ] A **DigitalOcean account** ([sign up](https://cloud.digitalocean.com/registrations/new))
- [ ] A **Personal Access Token** with Read+Write scope ([create one](https://cloud.digitalocean.com/account/api/tokens))
- [ ] A **configured Dango project** with at least one source in `sources.yml`
- [ ] **Credentials configured** in `.dlt/secrets.toml` for your sources

!!! tip "API Token"
    Your DO token can be provided three ways (checked in this order):

    1. `DIGITALOCEAN_TOKEN` environment variable
    2. Stored in `.dango/cloud.yml` from a previous deployment
    3. Prompted during the wizard

## Quick Start

```bash
dango deploy
```

That's it. The wizard walks you through every decision interactively. The rest of this page explains each step in detail.

---

## Wizard Walkthrough

### Step 1: Prerequisites Check

The wizard validates your setup before proceeding:

- **API token** &mdash; checks the token is valid by making a test API call to DigitalOcean
- **sources.yml** &mdash; verifies you have at least one data source configured

If the token is invalid or expired, you'll be prompted to enter a new one.

```
✓ DigitalOcean API token validated
✓ Found 3 configured sources
```

### Step 2: Select Region

Choose which DigitalOcean data center to deploy to. The wizard suggests a region based on your UTC offset.

| Region | Location | GDPR |
|--------|----------|------|
| `nyc1` | New York 1 | |
| `nyc3` | New York 3 | |
| `sfo3` | San Francisco 3 | |
| `ams3` | Amsterdam 3 | Yes |
| `sgp1` | Singapore 1 | |
| `lon1` | London 1 | |
| `fra1` | Frankfurt 1 | Yes |
| `tor1` | Toronto 1 | |
| `blr1` | Bangalore 1 | |
| `syd1` | Sydney 1 | |

!!! tip "GDPR Compliance"
    If your data is subject to GDPR, choose **ams3** (Amsterdam) or **fra1** (Frankfurt). These regions are in the EU and your data will remain within EU borders.

```
Select a region:
  Suggested: nyc1 (New York 1)

  [1] nyc1 - New York 1
  [2] nyc3 - New York 3
  ...
```

### Step 3: Select Server Size

Choose your droplet size based on your data volume and performance needs.

| Tier | Slug | vCPU | RAM | Disk | Price |
|------|------|------|-----|------|-------|
| Budget | `s-1vcpu-2gb` | 1 | 2 GB | 50 GB | $12/mo |
| **Standard** (default) | `s-2vcpu-4gb` | 2 | 4 GB | 80 GB | **$24/mo** |
| Performance | `s-4vcpu-8gb` | 4 | 8 GB | 160 GB | $48/mo |

!!! warning "Budget Tier"
    The budget tier ($12/mo) has only 2 GB RAM. Metabase may be slow on this tier, especially with complex dashboards or large datasets. Use it for testing or small projects with minimal transformation.

You can also enter a custom DigitalOcean slug (e.g., `s-8vcpu-16gb`) if you need more resources.

```
Select server size:
  [1] Budget   - $12/mo  (1 vCPU, 2 GB RAM, 50 GB disk)
  [2] Standard - $24/mo  (2 vCPU, 4 GB RAM, 80 GB disk) [default]
  [3] Performance - $48/mo (4 vCPU, 8 GB RAM, 160 GB disk)
  [4] Custom slug
```

### Step 4: Admin Account

Set up the admin account for the web UI.

- **Email** &mdash; prompted twice for confirmation (double-entry)
- **Password** &mdash; auto-generated using `secrets.token_urlsafe(16)` for maximum entropy

```
Admin email: admin@yourcompany.com
Confirm email: admin@yourcompany.com

╭─────────────────────────────────────────╮
│  Admin Password: xK7_mN2pQ9rT4wY6zA8b  │
│                                         │
│  Save this password now — it will not   │
│  be shown again.                        │
╰─────────────────────────────────────────╯
```

!!! danger "Save Your Password"
    The generated password is displayed once and never stored in plaintext. Copy it to a password manager immediately. If you lose it, you'll need to reset it via SSH.

You can also pre-set the password via the `DANGO_ADMIN_PASSWORD` environment variable or the `--admin-password` flag for non-interactive deployments.

### Step 5: Data Sources

The wizard lists all sources from your `sources.yml` and checks that credentials exist in `.dlt/secrets.toml`:

```
Data sources to deploy:
  ✓ stripe (API key configured)
  ✓ hubspot (API key configured)
  ✓ google_sheets (OAuth token configured)
  ✗ salesforce (missing credentials)
```

!!! warning
    Sources with missing credentials will still be deployed but won't sync until you add credentials on the server via the web UI secrets page or `dango remote env set`.

### Step 6: OAuth Sources

OAuth sources (Google Sheets, Google Analytics, etc.) require re-authentication after deployment because the redirect URI changes from `localhost` to your server's domain.

This step is **always skipped** during deployment. Configure OAuth post-deploy using `dango oauth setup` or the web UI. See [Post-Deploy Setup](post-deploy.md#4-oauth-re-authentication) for instructions.

```
OAuth sources will need re-authentication after deployment.
Skipping OAuth setup — configure post-deploy.
```

### Step 7: Automated Backups

Optionally configure automated backups to DigitalOcean Spaces (S3-compatible object storage).

- **Requires** DO Spaces access key and secret key
- **Cost** ~$5/mo for storage
- **Backs up** the DuckDB warehouse, configuration files, and dbt project files

```
Enable automated backups to DigitalOcean Spaces? [y/N]
```

You can enable backups later with `dango remote backup enable`. See [Backups](backups.md) for details.

### Step 8: Cost Summary

The wizard shows a summary of all costs before proceeding:

```
╭─ Cost Summary ──────────────────────────╮
│                                         │
│  Droplet (s-2vcpu-4gb, nyc1):  $24/mo   │
│  Backups (DO Spaces):           $5/mo   │
│  ─────────────────────────────────────  │
│  Estimated total:              $29/mo   │
│                                         │
│  Billed by DigitalOcean to your account │
╰─────────────────────────────────────────╯

Proceed with deployment? [y/N]
```

!!! note
    Dango does not charge anything. All costs are billed directly by DigitalOcean to your account. The estimates shown are based on DigitalOcean's published pricing and may vary.

!!! tip "Set a domain during deployment"
    You can pass `--domain analytics.yourcompany.com` to configure HTTPS during initial deployment, skipping the [post-deploy domain setup](post-deploy.md#2-custom-domain). Make sure your DNS A record is already pointing to a placeholder or you configure it immediately after the droplet IP is assigned.

---

## Provisioning

After confirmation, the wizard provisions your server automatically. This takes approximately 2&ndash;4 minutes.

**What happens during provisioning:**

1. **Generate SSH key pair** &mdash; creates a dedicated key for server access
2. **Upload SSH key** to your DigitalOcean account
3. **Create cloud firewall** &mdash; allows SSH (22), HTTP (80), HTTPS (443) inbound
4. **Provision droplet** &mdash; creates the VM with Ubuntu 22.04
5. **Wait for droplet** &mdash; polls until the droplet is active and has an IP
6. **Verify SSH** &mdash; waits for SSH to become reachable
7. **Server setup** &mdash; installs Docker, Caddy, Python, fail2ban, and configures the server (16 steps)
8. **Sync project files** &mdash; pushes configuration and dbt files
9. **Generate dbt profiles** &mdash; creates `profiles.yml` tuned for the server's hardware
10. **Push credentials** &mdash; securely transfers `.dlt/secrets.toml` and `.env`
11. **Create admin account** &mdash; sets up the admin user and enables authentication
12. **Setup backups** &mdash; configures Spaces backup (if opted in)
13. **Save metadata** &mdash; writes server info to `.dango/cloud.yml`
14. **Start services** &mdash; launches Dango and Metabase via systemd
15. **Health check** &mdash; verifies the web UI is responding
16. **Initial sync** &mdash; triggers the first data sync

```
Provisioning server...
  [1/16] Generating SSH key pair ✓
  [2/16] Uploading SSH key to DigitalOcean ✓
  [3/16] Creating cloud firewall ✓
  [4/16] Provisioning droplet (s-2vcpu-4gb in nyc1) ✓
  [5/16] Waiting for droplet to become active ✓
  ...
  [16/16] Triggering initial sync ✓

╭─────────────────────────────────────────╮
│  Deployment complete!                   │
│                                         │
│  Server IP: 143.198.xxx.xxx             │
│  Web UI:    http://143.198.xxx.xxx      │
│  Status:    dango remote status         │
╰─────────────────────────────────────────╯
```

!!! note
    The step numbers and grouping shown above are a documentation summary. The actual CLI output may show a different breakdown depending on your configuration (e.g., backup steps are skipped if you opted out).

If any step fails, the wizard performs **automatic cleanup** &mdash; destroying the droplet, removing the SSH key, and deleting the firewall to avoid orphaned resources.

---

## Non-Interactive Mode

For scripted or CI/CD deployments, use `--non-interactive` with the required flags:

```bash
dango deploy \
  --non-interactive \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --admin-email admin@yourcompany.com \
  --admin-password "$DANGO_ADMIN_PASSWORD"
```

### CLI Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--non-interactive` | Skip all prompts (requires flags/env vars) | Off |
| `--region` | DigitalOcean region slug (e.g., `nyc1`) | Prompted |
| `--size` | Droplet size slug (e.g., `s-2vcpu-4gb`) | `s-2vcpu-4gb` |
| `--domain` | Custom domain for HTTPS | None |
| `--admin-email` | Admin account email | Prompted |
| `--admin-password` | Admin account password | Auto-generated |
| `--skip-backups` | Skip automated backup setup (backups require Spaces keys) | Off |
| `--reconnect` | Reconnect to an existing server | Off |
| `--ip` | Server IP for `--reconnect` | Prompted |
| `--byos` | Deploy to existing server (see [BYOS](byos.md)) | Off |
| `--server-ip` | Server IP/hostname for `--byos` | Prompted |
| `--ssh-user` | SSH user for `--byos` | `root` |
| `--ssh-key` | SSH key path for `--byos` | Prompted |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DIGITALOCEAN_TOKEN` | DigitalOcean API token (Read+Write) |
| `DANGO_ADMIN_PASSWORD` | Admin password (skips auto-generation) |

---

## Verification

After deployment completes, verify everything is working:

### 1. Check Server Status

```bash
dango remote status
```

Expected output:

```
Server: 143.198.xxx.xxx (nyc1, s-2vcpu-4gb)
Status: healthy

Services:
  ✓ Dango web server (running)
  ✓ Metabase (running)
  ✓ Caddy (running)
  ✓ Docker (running)

Last sync: 2 minutes ago
Sources: 3 configured, 3 healthy
```

### 2. Check Logs

```bash
dango remote logs          # Recent logs
dango remote logs --follow  # Stream logs
```

### 3. Access Web UI

Open `http://<your-server-ip>` in a browser and log in with the admin email and password from Step 4.

!!! tip
    The initial page load may take 30&ndash;60 seconds while Metabase starts up for the first time. Subsequent loads are fast.

---

## Remote Server Layout

Once deployed, the server has this structure:

```
/srv/dango/                          # Project root
├── .dango/
│   ├── sources.yml                  # Source definitions
│   ├── schedule.yml                 # Sync schedules
│   ├── cloud.yml                    # Server metadata (IP, region, etc.)
│   ├── auth.yml                     # Authentication config
│   └── state/
│       ├── sync_status_*.json       # Per-source sync status
│       └── deployments.jsonl        # Deploy history journal
├── .dlt/
│   └── secrets.toml                 # API keys and credentials
├── dbt_project/
│   ├── dbt_project.yml              # dbt configuration
│   ├── profiles.yml                 # Auto-generated for server hardware
│   └── models/                      # dbt models
├── warehouse.duckdb                 # DuckDB database
├── docker-compose.yml               # Metabase container definition
├── Dockerfile.metabase              # Metabase image with DuckDB driver
├── entrypoint.sh                    # Metabase startup script
└── venv/                            # Python virtual environment
```

---

## Troubleshooting

### Token authentication failed

```
Error: DigitalOcean API token is invalid or expired
```

Generate a new token at [cloud.digitalocean.com/account/api/tokens](https://cloud.digitalocean.com/account/api/tokens). Make sure it has **Read and Write** scope.

### Droplet not becoming active

```
Timeout waiting for droplet to become active
```

DigitalOcean occasionally has provisioning delays. Check the [DO status page](https://status.digitalocean.com). The wizard will clean up automatically &mdash; try again in a few minutes.

### SSH not reachable

```
Timeout waiting for SSH on 143.198.xxx.xxx
```

This usually means the droplet is still booting. If it persists:

1. Check the droplet is running in the [DO console](https://cloud.digitalocean.com/droplets)
2. Verify the firewall allows SSH (port 22)
3. Try `dango deploy --reconnect --ip <IP>` to retry the setup

### Health check failed

```
Server did not pass health check after 120 seconds
```

SSH into the server to diagnose:

```bash
dango remote ssh
```

Then on the server:

```bash
sudo systemctl status dango
sudo journalctl -u dango --no-pager -n 50
```

Common causes:

- Metabase container still starting (wait 60 seconds, check `docker ps`)
- Port conflict (another service on port 8800)
- Python dependency issue (check `journalctl` output)

### Reconnect to existing deployment

If your local `.dango/cloud.yml` was deleted or you're on a new machine:

```bash
dango deploy --reconnect --ip 143.198.xxx.xxx
```

This re-establishes the SSH connection and updates your local configuration without re-provisioning.

---

## Next Steps

- [Post-Deploy Setup](post-deploy.md) &mdash; configure domain, HTTPS, firewall, and OAuth
- [Remote Management](remote-management.md) &mdash; managing your deployed server day-to-day
- [Backups](backups.md) &mdash; configure and manage automated backups
- [Environment Variables](environment-variables.md) &mdash; managing secrets on the server
