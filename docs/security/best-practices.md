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

### Change Default Passwords

After `dango start`:

```bash
# Change Metabase password immediately
# Login to http://localhost:3000
# Admin → Account → Password
```

### Restrict Network Access

For services exposed on localhost:

```bash
# Only bind to localhost (default)
# Don't expose ports externally without auth
```

If you need external access:
- Use VPN or SSH tunnel
- Add authentication proxy
- Configure firewall rules

### Audit Logging

Track access to sensitive operations:

```bash
# Check sync logs
ls -la .dango/logs/

# Monitor for unusual activity
grep -i "error\|failed\|unauthorized" .dango/logs/*.log
```

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

### Ongoing Operations

- [ ] Use environment variables for credentials
- [ ] Rotate credentials periodically (quarterly)
- [ ] Review git history for exposures
- [ ] Encrypt backups
- [ ] Monitor for unauthorized access

### Team Practices

- [ ] Each user has own credentials
- [ ] Use password manager for sharing
- [ ] Document offboarding process
- [ ] Regular security reviews

---

## Quick Reference

### Do's

- ✅ Use environment variables
- ✅ Use `.gitignore` for secrets
- ✅ Use system keyring for OAuth
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

- [Credential Management](credentials.md) - Detailed credential guidance
- [OAuth Tokens](oauth.md) - OAuth security
- [Git Workflows](../workflows/git-workflows.md) - Version control practices
