# Hardening Guide

Security hardening for production and cloud deployments.

---

## Overview

Dango automatically configures several security measures when you deploy to the cloud with `dango deploy`. This page covers what's auto-configured, what requires manual setup, and a checklist for production readiness.

---

## Auto-Configured on Cloud Deploy

These security measures are applied automatically during `dango deploy` via the server setup process. No manual action required.

### SSH Key-Only Authentication

Password-based SSH login is disabled. Only key-based authentication is allowed.

- Root password login disabled
- Password authentication disabled system-wide
- Only the deploy key (`.dango/cloud_key`) can access the server

### fail2ban SSH Protection

An SSH jail is configured to block brute-force SSH attempts:

| Parameter | Value |
|-----------|-------|
| Max retries | 5 |
| Ban time | 1 hour (3,600 seconds) |
| Service | SSH (port 22) |

### Caddy Auto-TLS

When a domain is configured, [Caddy](https://caddyserver.com/) automatically provisions and renews Let's Encrypt TLS certificates:

```bash
# Set a domain for your deployment
dango remote domain set analytics.example.com
```

Without a domain, Caddy serves over plain HTTP on the server's IP address.

### Unattended Security Upgrades

Ubuntu's unattended-upgrades service is configured to automatically install security patches:

- Security updates from `${distro_codename}-security`
- ESM (Extended Security Maintenance) updates
- Auto-removes unused kernel packages and dependencies
- Auto-fixes interrupted dpkg operations

### Docker Log Rotation

Docker container logs are rotated to prevent disk exhaustion:

| Parameter | Value |
|-----------|-------|
| Max log size | 10 MB per container |
| Max log files | 3 (rotated) |
| Driver | json-file |

### journald Storage Limits

System journal storage is capped:

| Parameter | Value |
|-----------|-------|
| Max storage | 500 MB |

### Application Rate Limiting

The Dango web server applies rate limiting to prevent abuse:

| Endpoint | Limit |
|----------|-------|
| `/api/auth/login` | 10 requests per 60 seconds |
| All other `/api/*` | 200 requests per 60 seconds |

Localhost requests are exempt. See [Authentication — Rate Limiting](authentication.md#rate-limiting) for details.

### Account Lockout

Brute-force login protection is always enabled:

| Parameter | Value |
|-----------|-------|
| Failed attempts before lockout | 5 |
| Lockout duration | 15 minutes |

See [Authentication — Brute-Force Protection](authentication.md#brute-force-protection) for details.

---

## Manual Hardening

These measures require manual configuration based on your deployment needs.

### Cloudflare Proxy

For DDoS protection and CDN caching, route traffic through Cloudflare:

1. Add your domain to Cloudflare
2. Point DNS to your Dango server's IP
3. Enable Cloudflare proxy (orange cloud icon)
4. Configure Caddy to trust Cloudflare IPs for accurate client IP logging

!!! tip "Recommended for Public Deployments"
    If your Dango instance is accessible from the public internet, Cloudflare's free tier provides substantial DDoS protection and CDN caching.

### IP Restriction

Restrict web access (ports 80/443) to specific IP addresses using the DigitalOcean firewall:

```bash
# Allow a specific IP or CIDR range
dango remote firewall allow-ip 203.0.113.0/24

# Allow another IP
dango remote firewall allow-ip 198.51.100.50

# Revert to public access
dango remote firewall allow-all
```

!!! note
    IP restriction uses the DigitalOcean cloud firewall API. SSH (port 22) remains accessible for server management.

### UFW Firewall (BYOS Deployments)

For "Bring Your Own Server" deployments (servers not provisioned by DigitalOcean), Dango can configure UFW (Uncomplicated Firewall):

- Allows SSH (port 22), HTTP (80), and HTTPS (443)
- Blocks all other inbound traffic
- UFW is set up automatically during BYOS provisioning

For manual UFW configuration on an existing server:

```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

---

## Shared Deploy Key Workflow

The deploy key provides SSH access to your cloud server. Here's how to share it securely with team members.

### How Deploy Keys Work

1. **Admin runs `dango deploy`** — generates `.dango/cloud_key` (SSH private key) and `.dango/cloud.yml` (server metadata)
2. **Admin shares the key** with team members via a secure channel
3. **Team members place the files** in their local `.dango/` directory
4. **Any team member can deploy** with `dango remote push`

### Sharing Securely

Share the deploy key through encrypted channels only:

- **1Password** or **Bitwarden** shared vault
- End-to-end encrypted messaging (Signal, etc.)
- Encrypted email attachment

!!! danger "Deploy Key = Root SSH Access"
    The deploy key grants root-level SSH access to your server. Treat it with the same care as a server root password. Never share via unencrypted email, Slack, or commit to git.

### Required Files

Team members need these files in their local `.dango/` directory:

```
.dango/
├── cloud_key       # SSH private key (chmod 600)
└── cloud.yml       # Server connection metadata (IP, region, etc.)
```

---

## Monitoring Integration

### Health Endpoint

Dango exposes a public health endpoint for monitoring:

```
GET /api/health
```

This endpoint returns minimal information (no sensitive data) and is designed for load balancer health probes and uptime monitoring services.

### Uptime Monitoring Setup

Configure an uptime monitoring service to watch your Dango deployment:

=== "UptimeRobot"

    1. Create a new monitor in [UptimeRobot](https://uptimerobot.com/)
    2. Set URL: `https://your-domain.com/api/health`
    3. Set interval: **5 minutes**
    4. Set alert threshold: **2 consecutive failures**

=== "BetterStack"

    1. Create a new monitor in [BetterStack](https://betterstack.com/)
    2. Set URL: `https://your-domain.com/api/health`
    3. Set interval: **5 minutes**
    4. Set incident threshold: **2 consecutive failures**

---

## Session Timeout Hardening

Session timeouts differ between local and cloud deployments:

=== "Local"

    | Parameter | Default |
    |-----------|---------|
    | Absolute expiry | 365 days |
    | Idle timeout | 24 hours |

    Local defaults are generous since the server runs on your own machine.

=== "Cloud"

    | Parameter | Default |
    |-----------|---------|
    | Absolute expiry | 30 days |
    | Idle timeout | 60 minutes |

    Tighten further for sensitive deployments:

    ```yaml
    # .dango/project.yml
    auth:
      session_max_days: 7
      idle_timeout_minutes: 30
    ```

For full session management details, see [Authentication — Session Management](authentication.md#session-management).

---

## Hardening Checklist

### Before Deployment

- [ ] Set a strong admin password during `dango init`
- [ ] Enable [two-factor authentication](two-factor.md) for all admin accounts
- [ ] Review [credential management](credentials.md) — no secrets in git

### After Cloud Deployment

- [ ] Verify SSH key-only auth is active (password login disabled)
- [ ] Set a domain for auto-TLS: `dango remote domain set <domain>`
- [ ] Configure IP restriction if not public: `dango remote firewall allow-ip <cidr>`
- [ ] Set up uptime monitoring on `/api/health`
- [ ] Share deploy key securely with team (1Password, Bitwarden)
- [ ] Review cloud session timeouts (default: 60-min idle, 30-day absolute)

### Ongoing

- [ ] Review [audit logs](audit-logging.md) regularly for suspicious activity
- [ ] Rotate credentials periodically ([credential management](credentials.md#credential-rotation))
- [ ] Keep Dango updated: `dango remote upgrade`
- [ ] Verify unattended-upgrades is running: `systemctl status unattended-upgrades`

---

## Next Steps

- [Authentication](authentication.md) — session management and lockout policy
- [Audit Logging](audit-logging.md) — monitor security events
- [Credential Management](credentials.md) — protect API keys and secrets
- [Best Practices](best-practices.md) — security recommendations
