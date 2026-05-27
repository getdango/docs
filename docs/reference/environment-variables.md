# Environment Variables

Complete reference for all environment variables used by Dango.

---

## Overview

Dango reads configuration from multiple sources in this priority order:

1. **`.dlt/secrets.toml`** (highest priority) --- source credentials managed by dlt
2. **`.env` file** in the project root
3. **System environment variables** (lowest priority)

Most environment variables are only needed for source credentials. Platform variables like `DANGO_DEBUG` are read directly from the system environment or `.env`.

---

## Platform Variables

These control Dango's runtime behavior.

| Variable | Default | Description |
|----------|---------|-------------|
| `DANGO_DEBUG` | `""` (disabled) | Enable full stack traces in error messages. Set to `1`, `true`, or `yes` (case-insensitive) |
| `DANGO_LOG_LEVEL` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DANGO_ADMIN_EMAIL` | `admin@localhost` | Email for the initial admin user created on first startup |
| `DANGO_ADMIN_PASSWORD` | -- | Password for the initial admin user. Required for automated/CI deployments |
| `DANGO_OAUTH_CALLBACK_URL` | `http://localhost:8080/callback` | OAuth redirect URI for authorization server callbacks |
| `DANGO_NOTEBOOK_DB_PATH` | `data/warehouse.duckdb` | DuckDB database path used by Marimo notebook templates |

### Usage Notes

- **`DANGO_ADMIN_EMAIL`** and **`DANGO_ADMIN_PASSWORD`** are used during `dango init` (if `--skip-wizard` is set) and during cloud deployment. For interactive setup, these are prompted instead.
- **`DANGO_NOTEBOOK_DB_PATH`** is read inside Marimo notebooks to connect to DuckDB. Override this if your warehouse is at a non-standard path.

---

## Cloud Deployment Variables

Required for DigitalOcean cloud deployment (`dango deploy`).

| Variable | Description |
|----------|-------------|
| `DIGITALOCEAN_TOKEN` | DigitalOcean API personal access token. Required for provisioning and managing droplets |
| `SPACES_ACCESS_KEY` | DigitalOcean Spaces access key (S3-compatible). Required only if using Spaces for backups |
| `SPACES_SECRET_KEY` | DigitalOcean Spaces secret key. Required only if using Spaces for backups |

!!! tip
    The `SPACES_ACCESS_KEY` and `SPACES_SECRET_KEY` env var names are configurable in `.dango/cloud.yml` via `spaces.access_key_env` and `spaces.secret_key_env`.

---

## Source Credential Variables

These are referenced by source configurations in `.dango/sources.yml` (via `*_env` fields).

### API Key Sources

| Variable | Used By | Description |
|----------|---------|-------------|
| `STRIPE_API_KEY` | Stripe | Stripe secret API key (`sk_live_...` or `sk_test_...`) |
| `HUBSPOT_API_KEY` | HubSpot | HubSpot private app access token (`pat-na1-...`) |
| `GITHUB_ACCESS_TOKEN` | GitHub | GitHub personal access token (`ghp_...`) |
| `SLACK_ACCESS_TOKEN` | Slack | Slack bot user OAuth token (`xoxb-...`) |
| `FB_ACCESS_TOKEN` | Facebook Ads | Facebook long-lived access token |

### OAuth Sources

| Variable | Used By | Description |
|----------|---------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth login provider | Google OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth login provider | Google OAuth 2.0 client secret |
| `GOOGLE_CREDENTIALS` | Google Analytics | Service account JSON or OAuth credentials |

!!! note
    Google Sheets, Google Analytics, and Google Ads use OAuth tokens stored in `.dlt/secrets.toml` after running `dango oauth setup google`. The `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` variables listed above are for the **login provider** (allowing users to sign in with Google), not for source data access.

### Facebook OAuth

| Variable | Used By | Description |
|----------|---------|-------------|
| `FACEBOOK_APP_ID` | Facebook OAuth | Facebook app ID (for OAuth login provider) |
| `FACEBOOK_APP_SECRET` | Facebook OAuth | Facebook app secret (for OAuth login provider) |

!!! warning
    Facebook access tokens expire after 60 days and must be manually refreshed. There is no automatic token refresh for Facebook.

### REST API Sources

REST API sources use configurable env var names. Common patterns:

| Variable | Description |
|----------|-------------|
| Custom `auth_token_env` | Bearer or API key token |
| Custom `basic_username_env` | HTTP Basic auth username |
| Custom `basic_password_env` | HTTP Basic auth password |
| Custom `client_id_env` | OAuth2 client credentials client ID |
| Custom `client_secret_env` | OAuth2 client credentials client secret |

---

## Internal Variables

These are set or read internally by Dango and generally should not be modified.

| Variable | Description |
|----------|-------------|
| `VIRTUAL_ENV` | Read to detect virtual environment activation (standard Python variable) |
| `DLT_PROJECT_DIR` | Set internally during sync to point dlt at the project root |

---

## `.env` File

Place a `.env` file in your project root for environment variables. This file is automatically loaded by Dango and should be **gitignored** if it contains secrets.

### Example

```bash
# Platform
DANGO_DEBUG=false
DANGO_LOG_LEVEL=INFO
DANGO_ADMIN_EMAIL=admin@mycompany.com

# Source credentials
STRIPE_API_KEY=sk_live_51ABCdef...
HUBSPOT_API_KEY=pat-na1-xxxxxxxxxxxxx
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxx
SLACK_ACCESS_TOKEN=xoxb-xxxxxxxxxxxxx
FB_ACCESS_TOKEN=EAAB1234567890...

# Google OAuth (for login provider)
GOOGLE_CLIENT_ID=123456789.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abc123...

# Cloud deployment
DIGITALOCEAN_TOKEN=dop_v1_xxxxxxxxxxxxx
```

---

## Credential Resolution

Dango uses [dlt's credential resolution](https://dlthub.com/docs/general-usage/credentials/) for source credentials:

1. **`_env` fields in source config** --- e.g., `stripe_secret_key_env: STRIPE_API_KEY` tells Dango which env var to read
2. **`.dlt/secrets.toml`** --- dlt's native credential store, checked first
3. **`.env` file** --- loaded into the process environment
4. **System environment** --- standard shell environment variables

For OAuth sources (Google, Facebook), credentials are stored in `.dlt/secrets.toml` after completing the OAuth flow via `dango oauth <provider>`. The tokens are automatically refreshed by dlt where supported.

---

## Related Pages

- [Configuration Reference](configuration.md) --- Config file schemas including `_env` field mappings
- [Credentials & Secrets](../security/credentials.md) --- Managing credentials securely
- [Cloud Deployment](../deployment/index.md) --- Cloud environment setup
