# Post-Deploy Setup

Configure your domain, HTTPS, firewall, OAuth, and verify everything is working after deployment.

---

## Prerequisites

- [ ] Completed deployment via [DigitalOcean](digitalocean.md) or [BYOS](byos.md)
- [ ] Admin email and password from the deployment wizard
- [ ] Optional: a domain name you want to point at the server

---

## 1. Verify Deployment

### Check Server Status

```bash
dango remote status
```

All services should show as running:

```
Server: 143.198.xxx.xxx
Status: healthy

Services:
  ✓ Dango web server (running)
  ✓ Metabase (running)
  ✓ Caddy (running)
  ✓ Docker (running)
```

### Log In to the Web UI

Open `http://<your-server-ip>` in a browser. Log in with the admin email and password from the deployment wizard.

!!! tip
    The first page load may take 30&ndash;60 seconds while Metabase finishes its initial startup. Subsequent loads are fast.

### Check Initial Sync

If you did not use `--skip-initial-sync`, your data sources should already be syncing. Check the Sources page in the web UI or run:

```bash
dango remote logs
```

---

## 2. Custom Domain

Setting up a domain gives you automatic HTTPS via Let's Encrypt and a human-readable URL.

### Configure DNS

Add an **A record** pointing your domain to the server IP:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `analytics` (or `@`) | `143.198.xxx.xxx` | 300 |

Wait for DNS propagation (usually 1&ndash;5 minutes, up to 48 hours for some providers).

### Set the Domain

```bash
dango remote domain set analytics.yourcompany.com
```

**What happens:**

1. **DNS preflight check** &mdash; resolves the domain via `socket.getaddrinfo` and verifies it points to your server's IP
2. **Update Caddyfile** &mdash; switches from IP-based HTTP to domain-based HTTPS configuration
3. **Reload Caddy** &mdash; applies the new configuration
4. **TLS provisioning** &mdash; Caddy automatically obtains a Let's Encrypt certificate
5. **Update cloud.yml** &mdash; stores the domain for future reference

```
Checking DNS for analytics.yourcompany.com...
  ✓ Resolves to 143.198.xxx.xxx (matches server IP)

Updating Caddy configuration...
  ✓ Caddyfile updated for HTTPS
  ✓ Caddy reloaded
  ✓ TLS certificate provisioning started

Domain set: https://analytics.yourcompany.com
```

!!! note "HTTPS Headers"
    When a domain is configured, Caddy enables **HSTS** (HTTP Strict Transport Security) with a 2-year max-age. This tells browsers to always use HTTPS for your domain. All other security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) are always active regardless of domain configuration.

### Remove a Domain

To revert to IP-based HTTP access:

```bash
dango remote domain remove
```

This reverts the Caddyfile to HTTP-only mode and clears the domain from `cloud.yml`.

---

## 3. Firewall

Restrict network access to your server to improve security.

=== "DigitalOcean"

    DigitalOcean deployments use the **DO cloud firewall**, managed via the Dango CLI.

    **Default rules** (created during deployment):

    | Direction | Protocol | Port | Source |
    |-----------|----------|------|--------|
    | Inbound | TCP | 22 | All IPv4 + IPv6 |
    | Inbound | TCP | 80 | All IPv4 + IPv6 |
    | Inbound | TCP | 443 | All IPv4 + IPv6 |
    | Outbound | TCP/UDP/ICMP | All | All |

    **Restrict SSH to your IP:**

    ```bash
    # Allow only your IP for SSH
    dango remote firewall allow-ip 203.0.113.50

    # List current rules
    dango remote firewall list
    ```

    **Allow access from anywhere** (default for HTTP/HTTPS):

    ```bash
    dango remote firewall allow-all
    ```

    !!! warning "IPv4 Only"
        The `dango remote firewall` commands only accept IPv4 addresses and CIDR ranges. IPv6 addresses are rejected with error code `DANGO-D020`. The default rules include IPv6 access via the DO console &mdash; use the DO web UI to manage IPv6 firewall rules.

=== "BYOS"

    BYOS deployments install **UFW** (Uncomplicated Firewall) directly on the server.

    **Default rules** (configured during deployment):

    - Default deny incoming, allow outgoing
    - Allow SSH (port 22)
    - Allow HTTP (port 80)
    - Allow HTTPS (port 443)

    **Manage UFW directly via SSH:**

    ```bash
    dango remote ssh

    # Check status
    sudo ufw status verbose

    # Allow a specific IP for SSH only
    sudo ufw allow from 203.0.113.50 to any port 22

    # Deny SSH from all (after adding specific IPs)
    sudo ufw delete allow 22

    # Reload
    sudo ufw reload
    ```

    If your server is behind a cloud provider's security group (AWS, GCP, etc.), configure network rules there as well &mdash; UFW and cloud security groups are independent layers.

---

## 4. OAuth Re-authentication

OAuth sources (Google Sheets, Google Analytics, Google Ads, Facebook Ads, GitHub) require re-authentication after deployment. This is because OAuth redirect URIs change from `http://localhost:...` to your server's URL.

### Why It's Needed

During local development, OAuth tokens are issued with `http://localhost:8800/oauth/callback` as the redirect URI. When you deploy to a server with a domain, the redirect URI must be updated to `https://analytics.yourcompany.com/oauth/callback` in your OAuth provider's console (Google Cloud, Facebook Developer, etc.) and new tokens must be obtained.

### Re-authenticate via CLI

```bash
dango oauth setup google_sheets
```

This opens a browser for the OAuth consent flow. After authorizing, the new tokens are saved directly to the server.

### Re-authenticate via Web UI

1. Navigate to the **Secrets & Admin** page in the web UI
2. Find the OAuth source
3. Click **Re-authenticate**
4. Complete the OAuth flow in the browser

!!! tip "Update Redirect URIs First"
    Before re-authenticating, update the **Authorized redirect URI** in your OAuth provider's developer console to match your server's URL:

    - **With domain:** `https://analytics.yourcompany.com/oauth/callback`
    - **Without domain:** `http://143.198.xxx.xxx/oauth/callback`

---

## 5. Scheduled Syncs

Cloud deployments typically use scheduled syncs instead of the local file watcher (which is not available on cloud).

Configure schedules via the web UI Schedules page or the CLI:

```bash
dango schedule set stripe --cron "0 */6 * * *"   # Every 6 hours
dango schedule set hubspot --cron "0 2 * * *"     # Daily at 2am
```

See [Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md) for full documentation on schedule configuration, cron syntax, and misfire handling.

---

## 6. Push Updates

After making local changes to configuration or dbt models, push them to the server:

```bash
dango remote push
```

??? info "What gets synced"
    `dango remote push` syncs these files to the server:

    - `.dango/sources.yml` &mdash; source definitions
    - `.dango/schedule.yml` &mdash; sync schedules
    - `dbt_project/` &mdash; all dbt models, tests, and configuration
    - `docker-compose.yml` &mdash; Metabase container definition
    - `Dockerfile.metabase` &mdash; Metabase image configuration
    - `entrypoint.sh` &mdash; Metabase startup script

    **Not synced** (managed separately):

    - `.env` &mdash; environment variables
    - `.dlt/secrets.toml` &mdash; API credentials
    - `warehouse.duckdb` &mdash; DuckDB database

!!! warning "Deploy Lock"
    Only one push can run at a time. If another push is in progress, you'll see an error. Wait for it to complete or check `dango remote status`.

---

## Verification Checklist

After completing post-deploy setup, verify everything:

- [ ] `dango remote status` shows all services healthy
- [ ] Web UI is accessible and login works
- [ ] Domain resolves correctly (if configured): `nslookup analytics.yourcompany.com`
- [ ] HTTPS certificate is valid (if domain configured): check browser lock icon
- [ ] Firewall rules are restrictive (SSH not open to all, if possible)
- [ ] OAuth sources re-authenticated and syncing
- [ ] Scheduled syncs configured and running
- [ ] `dango remote push` succeeds from local machine

---

## Troubleshooting

### DNS not resolving

```
Error: analytics.yourcompany.com does not resolve to 143.198.xxx.xxx
```

- Verify the A record is correct in your DNS provider
- Wait for propagation: `nslookup analytics.yourcompany.com` or `dig analytics.yourcompany.com`
- Some DNS providers cache aggressively &mdash; try a public resolver: `nslookup analytics.yourcompany.com 8.8.8.8`

### TLS certificate not issuing

```
Error: Caddy failed to obtain certificate
```

Common causes:

- **DNS not propagated** &mdash; Caddy can't verify domain ownership until DNS resolves
- **Ports 80/443 blocked** &mdash; Let's Encrypt uses HTTP-01 challenge (port 80 must be open)
- **Rate limited** &mdash; Let's Encrypt has [rate limits](https://letsencrypt.org/docs/rate-limits/) (50 certificates per domain per week)

Check Caddy logs:

```bash
dango remote ssh
sudo journalctl -u caddy --no-pager -n 50
```

### OAuth re-authentication failing

- Verify the redirect URI matches **exactly** in your OAuth provider's console (including protocol, domain, and path)
- For Google: update in [Google Cloud Console](https://console.cloud.google.com/apis/credentials) > OAuth 2.0 Client IDs > Authorized redirect URIs
- For Facebook: update in [Facebook Developer Console](https://developers.facebook.com/) > App Settings > Valid OAuth Redirect URIs

### Deploy lock stuck

```
Error: Deploy lock is held by another process
```

If no other push is running, the lock may be stale:

!!! warning
    Only delete the lock file if you are certain no push is in progress. Deleting it during an active push could leave the server in an inconsistent state.

```bash
dango remote ssh
rm /srv/dango/.dango/state/deploy.lock
```

---

## Next Steps

- [Remote Management](remote-management.md) &mdash; day-to-day server management commands
- [Backups](backups.md) &mdash; configure automated backups
- [Server Operations](server-operations.md) &mdash; systemd, logs, and maintenance
- [Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md) &mdash; configure automated data syncs
- [Authentication](../security/authentication.md) &mdash; manage users, sessions, and 2FA
