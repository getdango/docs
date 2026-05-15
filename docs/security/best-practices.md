# Security Best Practices

Recommendations for securing your Dango projects.

---

## Essential Security Measures

### 1. Never Commit Secrets

The most important rule:

```gitignore
# .gitignore - MUST HAVE

# Credentials
.dlt/secrets.toml
*.env
.env*
credentials.json
*_credentials.json
service_account.json

# Data
data/
*.duckdb
```

**Verify before every commit**:
```bash
# Check what will be committed
git status
git diff --cached

# Search for potential secrets
git diff --cached | grep -iE "(api_key|secret|password|token)"
```

### 2. Use Environment Variables

Don't hardcode credentials:

```toml
# BAD - hardcoded
[sources.stripe]
stripe_secret_key = "sk_live_abc123"

# GOOD - environment variable
[sources.stripe]
stripe_secret_key = "${STRIPE_API_KEY}"
```

### 3. Secure File Permissions

```bash
# Restrict secrets.toml access
chmod 600 .dlt/secrets.toml

# Verify permissions
ls -la .dlt/secrets.toml
# Should show: -rw-------
```

---

## Authentication Best Practices

### Enable Auth for All Deployments

Authentication is enabled by default in v1. Keep it enabled — even for local development — to match your production security posture.

### Set Up 2FA for Admin Accounts

All admin accounts should enable [two-factor authentication](two-factor.md). Admins have full control over user accounts, credentials, and platform configuration.

### Use Strong Passwords

Dango enforces [NIST SP 800-63B](authentication.md#password-policy) password policy: minimum 8 characters, no complexity rules, ~1,000 common passwords blocked. Use a password manager to generate strong, unique passwords.

### Review Audit Logs

Check [audit logs](audit-logging.md) regularly for suspicious activity:

```bash
# Check for failed logins in the last week
dango auth audit --type login_failure --since $(date -u -v-7d +%Y-%m-%d)

# Check for locked accounts
dango auth audit --type account_locked
```

### Configure Session Timeouts

For cloud deployments, review session timeout settings. The defaults (60-minute idle, 30-day absolute) are reasonable for most teams. Tighten for sensitive environments:

```yaml
# .dango/project.yml
auth:
  idle_timeout_minutes: 30
  session_max_days: 7
```

### Use API Keys for Automation

For scripts and CI/CD pipelines, use [API keys](authentication.md#api-keys) instead of session cookies. API keys can be scoped to specific users and revoked independently.

---

## Development Environment

### Secrets Template

Create a template for team onboarding:

```toml
# .dlt/secrets.toml.example (COMMIT THIS)
# Copy to .dlt/secrets.toml and fill in values

[sources.stripe]
stripe_secret_key = "YOUR_STRIPE_KEY_HERE"

[sources.google_sheets]
# Use: dango auth google_sheets
```

### Use Test Credentials

For development:
- Use Stripe test keys (`sk_test_*`)
- Create test Google accounts
- Use sandbox/staging APIs

```toml
# .dlt/secrets.toml (development)
[sources.stripe]
stripe_secret_key = "${STRIPE_TEST_KEY}"  # Not production key
```

### Separate Environments

```
project/
├── .dlt/
│   ├── secrets.toml        # Dev secrets (not committed)
│   └── secrets.toml.prod   # Production template
```

Or use environment-specific files:
```bash
# Development
export DLT_SECRETS_PATH=".dlt/secrets.dev.toml"

# Production
export DLT_SECRETS_PATH=".dlt/secrets.prod.toml"
```

---

## Team Collaboration

### Never Share Credentials Directly

Instead of:
- ❌ Emailing API keys
- ❌ Sharing in Slack
- ❌ Committing to git

Use:
- ✅ Password managers (1Password, Bitwarden)
- ✅ Secrets management (Vault, AWS Secrets Manager)
- ✅ Encrypted file sharing

### Per-User Credentials

Each team member should have their own:
- API keys (where possible)
- OAuth tokens
- Database credentials

Benefits:
- Audit trail per user
- Easy revocation when someone leaves
- No shared credential exposure risk

### Offboarding Checklist

When a team member leaves:

- [ ] Rotate any shared credentials
- [ ] Revoke their OAuth authorizations
- [ ] Remove their access to secrets managers
- [ ] Audit recent activity

---

## Git Security

### Pre-commit Hook

Prevent accidental commits of secrets:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for potential secrets
if git diff --cached --name-only | xargs grep -lE "(sk_live_|sk_test_|api_key.*=|password.*=)" 2>/dev/null; then
    echo "ERROR: Potential secrets detected in commit"
    echo "Please remove sensitive data before committing"
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### If Secrets Are Committed

If you accidentally commit secrets:

1. **Immediately rotate** the exposed credential
2. **Remove from history** (if not pushed):
   ```bash
   git reset --soft HEAD~1
   # Remove secret
   git commit
   ```
3. **If pushed**, treat as fully compromised:
   - Rotate credential immediately
   - Consider using BFG Repo-Cleaner for history

### Git History Scanning

Periodically scan for exposed secrets:

```bash
# Using git-secrets
git secrets --scan-history

# Manual search
git log -p --all | grep -iE "(api_key|secret|password)" | head -20
```

---

## Backup Security

### Encrypt Sensitive Backups

```bash
# Encrypt backup with gpg
tar -czf backup.tar.gz .dango/ dbt/
gpg --symmetric --cipher-algo AES256 backup.tar.gz
rm backup.tar.gz

# Decrypt when needed
gpg --decrypt backup.tar.gz.gpg > backup.tar.gz
```

### Exclude Secrets from Backups

```bash
# Backup script - exclude secrets
tar --exclude='.dlt/secrets.toml' \
    --exclude='*.env' \
    -czf backup.tar.gz .dango/ dbt/
```

### Secure Backup Storage

- Use encrypted cloud storage
- Enable versioning for recovery
- Limit access to backup location

---

## Production Considerations

### Secure Admin Accounts

- Set a strong admin password during `dango init`
- Enable [two-factor authentication](two-factor.md) for all admin accounts
- Use `dango auth list-users` to verify no unnecessary admin accounts exist

### Restrict Network Access

For cloud deployments:

```bash
# Restrict web access to specific IPs
dango remote firewall allow-ip 203.0.113.0/24

# Set up a domain for automatic HTTPS
dango remote domain set analytics.example.com
```

For local development, Dango binds to localhost by default. Don't expose ports externally without authentication.

### Monitor with Audit Logs

Review the [audit log](audit-logging.md) for security events:

```bash
# View recent audit events
dango auth audit

# Check for failed logins
dango auth audit --type login_failure

# Check for permission denials
dango auth audit --type permission_denied
```

### Set Up Uptime Monitoring

Monitor your cloud deployment's health:

```bash
# The /api/health endpoint is public and returns minimal info
curl https://your-domain.com/api/health
```

See [Hardening Guide — Monitoring Integration](hardening.md#monitoring-integration) for setup instructions.

---

## Data Security

### Sensitive Data Handling

If syncing sensitive data:

1. **Understand what you're syncing**
   - Review API endpoints
   - Check for PII in data

2. **Minimize data retention**
   ```bash
   # Regularly clean old data
   dango db clean
   ```

3. **Secure the database**
   ```bash
   # Restrict file access
   chmod 600 data/warehouse.duckdb
   ```

### Data Classification

Know your data:

| Type | Examples | Handling |
|------|----------|----------|
| Public | Product names, categories | Standard security |
| Internal | Revenue figures, metrics | Limit access |
| Confidential | Customer PII, payments | Additional encryption |

---

## Security Checklist

### Initial Setup

- [ ] Create comprehensive `.gitignore`
- [ ] Set up `secrets.toml.example` template
- [ ] Configure file permissions
- [ ] Install pre-commit hooks
- [ ] Set a strong admin password during `dango init`
- [ ] Enable [2FA](two-factor.md) for all admin accounts

### Ongoing Operations

- [ ] Use environment variables for credentials
- [ ] Rotate credentials periodically (quarterly)
- [ ] Review git history for exposures
- [ ] Review [audit logs](audit-logging.md) regularly
- [ ] Encrypt backups
- [ ] Monitor for unauthorized access

### Team Practices

- [ ] Each user has own credentials and Dango account
- [ ] Use password manager for sharing deploy keys
- [ ] Assign appropriate [roles](users-roles.md) (principle of least privilege)
- [ ] Document offboarding process (deactivate users, rotate credentials)
- [ ] Regular security reviews

### Cloud Deployments

- [ ] Set a domain for auto-TLS
- [ ] Configure [IP restriction](hardening.md#ip-restriction) if not public-facing
- [ ] Review [session timeouts](authentication.md#session-timeouts) for cloud defaults
- [ ] Set up [uptime monitoring](hardening.md#monitoring-integration)
- [ ] Share deploy key securely (never via email or Slack)

---

## Quick Reference

### Do's

- ✅ Use environment variables
- ✅ Use `.gitignore` for secrets
- ✅ Use `dango auth` for OAuth (auto-saves to secrets.toml)
- ✅ Rotate credentials regularly
- ✅ Use test credentials for development
- ✅ Encrypt backups

### Don'ts

- ❌ Commit secrets to git
- ❌ Share credentials via email/chat
- ❌ Use production credentials in development
- ❌ Leave default passwords unchanged
- ❌ Store secrets in plaintext backups
- ❌ Give everyone shared credentials

---

## Next Steps

- [Authentication](authentication.md) — login flows and session management
- [Users & Roles](users-roles.md) — user management and permissions
- [Two-Factor Auth](two-factor.md) — enable TOTP-based 2FA
- [Credential Management](credentials.md) — API key and credential security
- [OAuth Tokens](oauth.md) — OAuth token lifecycle
- [Hardening Guide](hardening.md) — production security configuration
- [Audit Logging](audit-logging.md) — track security events
- [Git Workflows](../workflows/git-workflows.md) — version control practices
