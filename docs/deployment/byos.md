# Bring Your Own Server

Deploy Dango to any Ubuntu server you already have &mdash; AWS, GCP, Hetzner, on-premise, or any other provider.

---

## Prerequisites

Your server must meet these requirements:

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Ubuntu 22.04 LTS | Ubuntu 22.04 or 24.04 LTS |
| **RAM** | 2 GB | 4 GB+ |
| **CPU** | 1 vCPU | 2+ vCPU |
| **Disk** | 20 GB free | 50 GB+ free |
| **Access** | SSH access (root or sudo) | Root access |
| **Ports** | 22 (SSH) | 22, 80, 443 open |

Additionally, you need:

- [ ] A **configured Dango project** with at least one source in `sources.yml`
- [ ] **Credentials configured** in `.dlt/secrets.toml` for your sources
- [ ] **SSH key** &mdash; existing key or the wizard generates one

!!! note "Docker Not Required"
    You do not need Docker pre-installed. The wizard installs Docker automatically via `get.docker.com` during server setup.

## Quick Start

```bash
dango deploy --byos
```

The wizard connects to your server via SSH, validates the environment, and installs everything. The rest of this page explains each step.

---

## Wizard Walkthrough

### Step 1: Server Connection

Provide your server's connection details:

- **IP address or hostname** &mdash; the server's public IP or DNS name
- **SSH user** &mdash; defaults to `root`
- **SSH key** &mdash; path to your private key, or the wizard generates a new keypair

```
Server IP or hostname: 203.0.113.50
SSH user [root]: root
SSH key path [~/.ssh/id_rsa]: ~/.ssh/id_rsa
```

### Step 2: Validate SSH

The wizard tests the SSH connection and checks the server environment:

```
Testing SSH connection to 203.0.113.50...
  ✓ SSH connection successful
  ✓ Ubuntu 22.04 detected
  ✓ 4 GB RAM, 2 vCPU
```

!!! note "Non-Ubuntu Warning"
    If the server is not running Ubuntu, the wizard shows a warning but allows you to proceed. Dango is tested on Ubuntu 22.04 and 24.04 &mdash; other distributions may work but are not officially supported.

The wizard auto-detects your server's hardware using `nproc` (CPU count) and `free` (RAM) to tune dbt performance settings in `profiles.yml`.

### Step 3: Admin Account

Same as the [DigitalOcean wizard](digitalocean.md#step-4-admin-account) &mdash; set an admin email (double-confirmed) and receive an auto-generated password.

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

### Step 4: Data Sources

Same as the [DigitalOcean wizard](digitalocean.md#step-5-data-sources) &mdash; lists your configured sources and checks for credentials.

### Step 5: OAuth Sources

Always skipped. Configure OAuth post-deploy. See [Post-Deploy Setup](post-deploy.md#4-oauth-re-authentication).

---

## What BYOS Does (and Doesn't Do)

The BYOS wizard installs and configures Dango on your server. It does **not** manage infrastructure outside the server itself.

| Capability | DigitalOcean | BYOS |
|-----------|--------------|------|
| Provision VM | Yes | No &mdash; you provide the server |
| Install Docker, Caddy, Python | Yes | Yes |
| Configure fail2ban, unattended-upgrades | Yes | Yes |
| Cloud firewall (DO API) | Yes | No &mdash; installs UFW instead |
| Automated backups (DO Spaces) | Yes | No &mdash; use manual snapshots |
| `dango remote destroy` | Yes (destroys droplet) | No &mdash; you manage the server |
| `dango remote firewall` | Yes (DO cloud firewall) | No &mdash; manage UFW directly |
| DNS/domain setup | Yes | Yes |
| HTTPS via Caddy | Yes | Yes |

---

## Server Setup Steps

After the wizard validates your SSH connection, the following is installed and configured on your server (approximately 2&ndash;4 minutes):

1. **System packages** &mdash; `apt` update and install build dependencies
2. **Dango user** &mdash; creates a `dango` system user
3. **Docker** &mdash; installed via `get.docker.com`, `dango` user added to `docker` group
4. **Caddy** &mdash; installed from the official apt repository (reverse proxy + auto-TLS)
5. **Project directories** &mdash; creates `/srv/dango/` structure
6. **Python venv** &mdash; creates virtual environment and installs `getdango` from PyPI
7. **SSH hardening** &mdash; disables root password login, enforces key-only authentication
8. **Docker daemon** &mdash; configures logging (json-file driver, 10MB max, 3 rotated files)
9. **journald** &mdash; caps log retention at 500 MB
10. **Log rotation** &mdash; configures `logrotate` for Dango activity logs
11. **systemd service** &mdash; installs `dango.service` for process management and auto-restart
12. **Caddyfile** &mdash; writes reverse proxy configuration (HTTP initially, HTTPS after domain setup)
13. **fail2ban** &mdash; SSH brute-force protection (ban after failed attempts)
14. **Unattended upgrades** &mdash; automatic security patches
15. **UFW firewall** &mdash; allows SSH (22), HTTP (80), HTTPS (443); denies all other inbound
16. **Sync project files** &mdash; pushes configuration and dbt files to the server
17. **dbt profiles** &mdash; generates `profiles.yml` tuned for detected hardware
18. **Push credentials** &mdash; securely transfers `.dlt/secrets.toml` and `.env`
19. **Create admin** &mdash; sets up admin user and enables authentication
20. **Start services** &mdash; launches Dango and Metabase via systemd
21. **Health check** &mdash; verifies the web UI is responding
22. **Initial sync** &mdash; triggers the first data sync

!!! tip "UFW is BYOS-only"
    DigitalOcean deployments use the DO cloud firewall (managed via API). BYOS deployments install UFW directly on the server since there's no cloud-level firewall to manage.

---

## Non-Interactive Mode

```bash
dango deploy \
  --byos \
  --non-interactive \
  --server-ip 203.0.113.50 \
  --ssh-user root \
  --ssh-key ~/.ssh/id_rsa \
  --admin-email admin@yourcompany.com \
  --admin-password "$DANGO_ADMIN_PASSWORD" \
  --skip-initial-sync
```

### BYOS-Specific Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--byos` | Enable BYOS mode (required) | Off |
| `--server-ip` | Server IP address or hostname | Prompted |
| `--ssh-user` | SSH username | `root` |
| `--ssh-key` | Path to SSH private key | Prompted |

All [common flags](digitalocean.md#cli-flags) also apply (`--non-interactive`, `--admin-email`, `--admin-password`, `--domain`, `--skip-initial-sync`).

---

## Verification

After deployment completes, verify everything is working:

```bash
dango remote status
```

Expected output:

```
Server: 203.0.113.50
Status: healthy

Services:
  ✓ Dango web server (running)
  ✓ Metabase (running)
  ✓ Caddy (running)
  ✓ Docker (running)

Last sync: 2 minutes ago
Sources: 3 configured, 3 healthy
```

Open `http://<your-server-ip>` in a browser and log in with the admin credentials from Step 3.

---

## Troubleshooting

### SSH connection refused

```
Error: SSH connection to 203.0.113.50 failed
```

- Verify the server is running and reachable: `ping 203.0.113.50`
- Check that port 22 is open in your cloud provider's security group / firewall
- Verify your SSH key: `ssh -i ~/.ssh/id_rsa root@203.0.113.50`
- If using a non-standard port, configure it in your `~/.ssh/config`

### Non-Ubuntu warning

```
Warning: Server is not running Ubuntu. Proceed anyway? [y/N]
```

Dango is tested on Ubuntu 22.04 and 24.04 LTS. Other Debian-based distributions (Debian 11+) may work. Non-Debian distributions (CentOS, Fedora, Arch) are not supported and will likely fail during package installation.

### Setup step failed

If server setup fails partway through:

```bash
# SSH into the server to check what happened
ssh -i ~/.ssh/id_rsa root@203.0.113.50

# Check logs
journalctl -u dango --no-pager -n 50
docker ps  # Is Metabase running?
systemctl status caddy
```

Unlike DigitalOcean deployments, BYOS does **not** automatically clean up on failure (since it didn't create the server). You can fix the issue and re-run `dango deploy --byos` &mdash; the wizard is idempotent and will skip steps that already completed successfully.

### Services not starting

```bash
dango remote ssh
```

Then on the server:

```bash
# Check service status
sudo systemctl status dango
sudo systemctl status caddy
sudo docker ps

# Restart services
sudo systemctl restart dango
sudo systemctl restart caddy
```

Common causes:

- **Port conflict** &mdash; another service already using port 8800, 80, or 443
- **Docker not running** &mdash; `sudo systemctl start docker`
- **Disk full** &mdash; `df -h` to check available space

---

## Next Steps

- [Post-Deploy Setup](post-deploy.md) &mdash; configure domain, HTTPS, firewall, and OAuth
- [Remote Management](remote-management.md) &mdash; managing your deployed server day-to-day
- [Server Operations](server-operations.md) &mdash; systemd, logs, and server maintenance
