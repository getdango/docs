# Credential Management

How Dango stores and manages API keys and credentials.

---

## Overview

Dango needs credentials to connect to data sources:

- API keys (Stripe, etc.)
- OAuth tokens (Google, Facebook)
- Database passwords
- Custom source credentials

---

## Storage Mechanisms

### System Keyring (Default)

Dango uses the system keyring for secure credential storage:

| Platform | Backend |
|----------|---------|
| macOS | Keychain |
| Linux | Secret Service (GNOME Keyring) |
| Windows | Windows Credential Manager |

**Benefits**:
- Encrypted at rest
- Protected by OS security
- No plaintext files

### secrets.toml (File-based)

For credentials not in keyring, Dango uses `.dlt/secrets.toml`:

```toml
# .dlt/secrets.toml
[sources.stripe]
api_key = "sk_live_xxx"

[sources.my_database]
password = "database_password"
```

!!! danger "Never Commit secrets.toml"
    This file contains plaintext credentials. Always add to `.gitignore`.

---

## Credential Types

### API Keys

For services like Stripe:

```bash
# Add via wizard (stored in keyring)
dango source add stripe
# Enter API key when prompted

# Or configure manually in secrets.toml
```

```toml
# .dlt/secrets.toml
[sources.stripe]
stripe_secret_key = "sk_live_xxx"
```

### OAuth Tokens

For Google, Facebook, etc.:

```bash
# Authenticate via browser
dango auth google_sheets
```

OAuth tokens are stored in the system keyring automatically.

### Database Credentials

For database connections:

```toml
# .dlt/secrets.toml
[sources.my_postgres]
host = "localhost"
port = 5432
database = "mydb"
username = "user"
password = "password"
```

---

## Environment Variables

### Using Environment Variables

Reference environment variables in secrets.toml:

```toml
# .dlt/secrets.toml
[sources.stripe]
stripe_secret_key = "${STRIPE_API_KEY}"
```

Set the variable:

=== "Linux/macOS"
    ```bash
    export STRIPE_API_KEY="sk_live_xxx"
    ```

=== "Windows"
    ```powershell
    $env:STRIPE_API_KEY = "sk_live_xxx"
    ```

### .env Files

For development, use a `.env` file:

```bash
# .env (DO NOT COMMIT)
STRIPE_API_KEY=sk_live_xxx
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
```

Load with:
```bash
source .env  # Linux/macOS
dango sync
```

Or use a tool like `direnv` for automatic loading.

---

## Credential Lifecycle

### Adding Credentials

```bash
# Via wizard (recommended)
dango source add stripe

# Manually edit secrets.toml
nano .dlt/secrets.toml
```

### Viewing Credentials

Credentials are masked in Dango output:

```bash
dango config show
# API Key: sk_live_***************
```

To verify a credential exists:
```bash
dango auth status --provider stripe
```

### Updating Credentials

```bash
# Re-run auth for OAuth
dango auth google_sheets

# Edit secrets.toml for API keys
nano .dlt/secrets.toml
```

### Removing Credentials

```bash
# Remove OAuth token
dango auth remove --provider google_sheets

# Remove from secrets.toml manually
nano .dlt/secrets.toml
```

---

## Credential Rotation

### When to Rotate

Rotate credentials when:
- Credential may have been exposed
- Employee leaves the team
- Regular security policy (e.g., quarterly)
- Service provider recommends

### Rotation Process

1. **Generate new credential** in the service provider's dashboard
2. **Update Dango** with new credential
3. **Test** with `dango sync --source affected_source`
4. **Revoke old credential** in the service provider

```bash
# Update credential
nano .dlt/secrets.toml

# Test
dango sync --source stripe_payments

# If successful, revoke old key in Stripe dashboard
```

---

## Secrets.toml Structure

### Full Example

```toml
# .dlt/secrets.toml

# Stripe API
[sources.stripe]
stripe_secret_key = "sk_live_xxx"

# Google OAuth (manual setup)
[sources.google_sheets]
client_id = "xxx.apps.googleusercontent.com"
client_secret = "xxx"

# Database connection
[sources.postgres_db]
host = "localhost"
port = 5432
database = "analytics"
username = "dango_user"
password = "secure_password"

# Custom API
[sources.my_api]
api_key = "xxx"
base_url = "https://api.example.com"

# Using environment variables
[sources.production]
api_key = "${PROD_API_KEY}"
```

### Organizing Secrets

Group by source name (must match `sources.yml`):

```yaml
# .dango/sources.yml
sources:
  - name: stripe_payments  # <- This name
    type: stripe
```

```toml
# .dlt/secrets.toml
[sources.stripe_payments]  # <- Must match
stripe_secret_key = "sk_live_xxx"
```

---

## Keyring Operations

### Check Keyring Status

```bash
# Python check
python -c "import keyring; print(keyring.get_keyring())"
```

### Manual Keyring Access

```python
import keyring

# Store
keyring.set_password("dango", "stripe_api_key", "sk_live_xxx")

# Retrieve
key = keyring.get_password("dango", "stripe_api_key")

# Delete
keyring.delete_password("dango", "stripe_api_key")
```

### Keyring Troubleshooting

| Issue | Solution |
|-------|----------|
| "No keyring backend" | Install `keyrings.alt` or use secrets.toml |
| Permission denied | Check OS keyring permissions |
| Credential not found | Re-authenticate with `dango auth` |

---

## Security Considerations

### Plaintext Risks

`secrets.toml` stores credentials in plaintext:
- Readable by anyone with file access
- Visible in backups
- Could be accidentally committed

**Mitigations**:
- Proper file permissions: `chmod 600 .dlt/secrets.toml`
- Always use `.gitignore`
- Encrypt backups

### Credential Exposure Signs

Watch for:
- Unexpected API usage spikes
- Unknown IP addresses in service logs
- Credentials in git history
- Credentials in error logs

### If Credentials Are Exposed

1. **Immediately revoke** the compromised credential
2. **Generate new** credential
3. **Update** Dango configuration
4. **Audit** for unauthorized access
5. **Review** how exposure occurred

---

## Next Steps

- [OAuth Tokens](oauth.md) - OAuth-specific security
- [Best Practices](best-practices.md) - Security recommendations
- [Git Workflows](../workflows/git-workflows.md) - Avoiding commits of secrets
