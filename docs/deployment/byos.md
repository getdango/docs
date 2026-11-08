# Bring Your Own Server

Deploy Dango to any Ubuntu server you already have &mdash; AWS, GCP, Hetzner, on-premise, or any other provider.

---

## Prerequisites

Your server must meet these requirements:

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS (22.04 is also supported) |
| **RAM** | 4 GB | 4 GB+ |
| **CPU** | 1 vCPU | 2+ vCPU |
| **Disk** | 20 GB free | 50 GB+ free |
| **Access** | Root SSH access | Root SSH access |
| **Ports** | 22 (SSH) | 22, 80, 443 open |

Additionally, you need:

- [ ] A **configured Dango project** with at least one source in `sources.yml`
- [ ] **Credentials configured** in `.dlt/secrets.toml` for your sources
- [ ] **SSH key** &mdash; existing key or the wizard generates one
- [ ] A **fresh host**, or one where `/srv/dango` does not exist yet. If `/srv` or `/srv/dango` already exists it must be a root-owned directory closed to other users (see [Troubleshooting](#srvdango-already-exists))
- [ ] **Python 3.11&ndash;3.13 for the Dango venv.** Ubuntu 24.04 has Python 3.12. Ubuntu 22.04 ships Python 3.10, so Dango downloads a pinned, checksum-verified Python 3.12 build and installs it under `/opt/dango/python`; that needs outbound HTTPS to `github.com` and `release-assets.githubusercontent.com`, or a root-owned Python 3.11&ndash;3.13 you install yourself from the operating system's packages
- [ ] Basic tools on the host: `curl`, `sha256sum`, `tar`, `find`, `readlink`, `mktemp` and `flock` (from `util-linux`)

!!! note "Docker Not Required"
    You do not need Docker pre-installed. The wizard installs Docker automatically via `get.docker.com` during server setup.

## Quick Start

```bash
dango deploy --byos
```

The wizard connects to your server via SSH, validates the environment, and installs everything. The rest of this page explains each step.

!!! warning "HTTP and host firewall"
    Without a domain, logins and cookies travel over plain HTTP. BYOS refuses `--allow-ip` because Dango cannot manage your provider firewall; restrict ports 80/443 with your own firewall and pass `--accept-http-exposure`, or configure a domain for HTTPS. The web service binds to `127.0.0.1` behind Caddy.

!!! note "Backups on BYOS"
    The `dango deploy --byos` summary ends with "Backups: not configured. BYOS backups live only on this server and are lost with it." and prints `dango remote backup download --from-server -o ./backup.tar.gz`. Secrets (`.env`, `.dlt/secrets.toml`) are not in backups by default. See [Backups](backups.md#where-backups-are-stored).

!!! note "Host layout for runner isolation"
    Keep `/srv/dango/project` on a normal directory rather than a bind mount. A restore that replaces a bind-mounted project can fall back to copy and delete, so an interruption may leave a partial replacement. If you widen the host's `net.ipv4.ip_local_port_range`, the notebook runner can reach other local services listening within that range; keep sensitive services outside it or restrict them separately.

---

## Wizard Walkthrough

### Step 1: Server Connection

Provide your server's connection details:

- **IP address or hostname** &mdash; the server's public IP or DNS name
- **SSH user** &mdash; must be `root`; sudo-based setup is not supported
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

!!! info "Ubuntu 22.04 vs 24.04"
    Both versions are supported; 24.04 is recommended for a new server because it ships a supported Python (3.12). The SSH service name differs between versions (`sshd` on 22.04, `ssh` on 24.04); Dango detects this automatically during setup. On 22.04, Dango installs its own Python 3.12 under `/opt/dango/python` (see [Prerequisites](#prerequisites)).

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
| Automated backups (DO Spaces) | Yes | Only if you configure a Spaces bucket; otherwise backups live on the server and are lost with it (see [Backups](backups.md#where-backups-are-stored)) |
| `dango deploy destroy` | Yes (destroys droplet) | Removes Dango and its data from the server; you delete the machine |
| `dango remote firewall` | Yes (DO cloud firewall) | No &mdash; manage UFW directly |
| DNS/domain setup | Yes | Yes |
| HTTPS via Caddy | Yes | Yes |

---

## Server Setup Steps

After the wizard validates your SSH connection, the following is installed and configured on your server (approximately 2&ndash;4 minutes):

1. **System packages** &mdash; `apt` update and install build dependencies
2. **Dango user** &mdash; creates a `dango` system user
3. **Docker** &mdash; installed via `get.docker.com`; Dango normally uses a root-owned Compose helper instead of adding the `dango` user to the `docker` group. A helper setup failure leaves a warned Docker-group fallback.
4. **Caddy** &mdash; installed from the official apt repository (reverse proxy + auto-TLS)
5. **Project directories** &mdash; creates `/srv/dango/` structure
6. **Python venv**: picks a Python 3.11&ndash;3.13 (the host's root-owned one, else the pinned build under `/opt/dango/python`), creates the virtual environment and installs `getdango` from PyPI
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

## Cloud Provider Notes

Different providers have different defaults. Keep these in mind when provisioning your server:

| Factor | DigitalOcean | Hetzner | GCP | AWS |
|--------|-------------|---------|-----|-----|
| **Default disk** | 80 GB | 40 GB | 10 GB :warning: | Varies by instance |
| **SSH user** | `root` | `root` | Your username | `ubuntu` |
| **Root SSH** | Yes | Yes | Disabled by default | Disabled by default |
| **Min RAM** | 4 GB recommended | 4 GB recommended | 4 GB recommended | 4 GB recommended |

!!! warning "GCP default disk is too small"
    GCP instances default to 10 GB disk, which is not enough for Dango (DuckDB + Metabase + Docker images). Increase to at least 20 GB when creating the instance.

!!! note "Root SSH is required"
    GCP and AWS disable root login by default. BYOS setup needs SSH as `root` (`--ssh-user` other than `root` is refused: "BYOS deploys need SSH as root; sudo-based setup is not supported"), so enable root SSH login with your key on such a host before you deploy.

**Minimum RAM:** 4 GB. Servers with 2 GB RAM cause Metabase out-of-memory crashes and are not supported.

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
  --admin-password "$DANGO_ADMIN_PASSWORD"
```

### BYOS-Specific Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--byos` | Enable BYOS mode (required) | Off |
| `--server-ip` | Server IP address or hostname | Prompted |
| `--ssh-user` | SSH username (must be `root`) | `root` |
| `--ssh-key` | Path to SSH private key | Prompted |
| `--accept-http-exposure` | Required without `--domain` in non-interactive mode: acknowledge plain HTTP (`--allow-ip` is refused on BYOS) | Off |

All [common flags](digitalocean.md#cli-flags) also apply (`--non-interactive`, `--admin-email`, `--admin-password`, `--domain`).

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

### /srv/dango already exists

```
BYOS setup failed: Server setup stopped before changing anything: /srv/dango already exists and is not a root-owned directory closed to other users and without an ACL (...). Root setup would run over a tree the dango user can change.
```

Setup refuses, before any root step, a host whose `/srv` or `/srv/dango` is not a real directory owned by root, is writable by its group or others, carries an ACL, or holds a Python venv the service account can change. This includes re-running `dango deploy --byos` against an existing 1.0.13 or earlier server, where `/srv/dango` is owned by the `dango` user. To update such a server use `dango remote upgrade`. For a new server use a fresh host, or have root move the directory aside (`mv /srv/dango /srv/dango.old`) after checking it, and run `dango deploy --byos` again.

### No usable Python, or `flock` missing (`DANGO-D024`)

```
The server has no usable Python 3.11, 3.12 or 3.13 for the Dango venv and Dango could not install one: <cause>.
```

The cause is named in the message: the download from `github.com` / `release-assets.githubusercontent.com` failed, the file failed the size or SHA-256 check, `/opt/dango` is not a root-owned directory, or a required tool is missing (for example `flock (util-linux) is required`). Install the missing tool (`apt install util-linux curl`), allow outbound HTTPS to those hosts, or install Python 3.11, 3.12 or 3.13 from the operating system's packages (root-owned, under `/usr`, with its `venv` module), then run `dango deploy --byos` again.

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

### Quick recovery

Before SSH-ing in manually, try the built-in recovery commands:

```bash
# Diagnose and fix common issues (disk, RAM, services, Metabase)
dango remote repair

# If Metabase is completely broken (SSO loop, H2 corruption)
dango remote reset-metabase
```

See [Recovery Commands](remote-management.md#recovery-commands) for details.

---

## Next Steps

- [Post-Deploy Setup](post-deploy.md) &mdash; configure domain, HTTPS, firewall, and OAuth
- [Remote Management](remote-management.md) &mdash; managing your deployed server day-to-day
- [Server Operations](server-operations.md) &mdash; systemd, logs, and server maintenance
