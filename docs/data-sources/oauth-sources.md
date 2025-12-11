# OAuth Sources

Connect to cloud services like Google Sheets, Facebook Ads, and HubSpot using OAuth 2.0 authentication.

---

## Overview

OAuth sources require authentication through the provider's web interface. Dango handles the OAuth flow and stores tokens securely in your environment.

**Wizard-Supported OAuth Sources** (via `dango source add`):

- Google Sheets
- Google Analytics 4 (GA4)
- Facebook Ads
- Google Ads

**Manual OAuth Sources** (require dlt_native configuration):

- HubSpot, Notion, Asana, Slack, and other dlt verified sources
- See [Custom Sources](custom-sources.md) for manual dlt_native setup

---

## OAuth Workflow

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Dango
    participant Provider

    User->>Dango: dango source add (select OAuth source)
    Dango->>Provider: Open OAuth consent page
    User->>Provider: Grant permissions
    Provider->>Dango: Return access token
    Dango->>Dango: Store token in .dlt/secrets.toml
    User->>Dango: dango sync
    Dango->>Provider: Fetch data with token
```

### One-Time Setup

1. **Add source** - Dango opens browser for OAuth
2. **Grant permissions** - Authenticate with provider
3. **Token stored** - Saved in `.dlt/secrets.toml` (gitignored)
4. **Sync** - Use token to fetch data

### Token Management

- **Access tokens**: Short-lived (1 hour typical)
- **Refresh tokens**: Long-lived (used to get new access tokens)
- **Auto-refresh**: Dango automatically refreshes expired tokens
- **Token expiry warnings**: Web UI shows when tokens need renewal

---

## Quick Start: Google Sheets

### Step 1: Add Source

```bash
dango source add
# Select "Google Sheets" from the list
```

This will:
1. Prompt for spreadsheet URL
2. Open browser for Google OAuth
3. Store credentials in `.dlt/secrets.toml`
4. Create entry in `.dango/sources.yml`

### Step 2: Authenticate

Browser opens to Google consent page:

- Select your Google account
- Review permissions (read-only access to Sheets)
- Click "Allow"

### Step 3: Verify Configuration

Check `.dango/sources.yml`:

```yaml
sources:
  - name: my_google_sheets
    type: google_sheets
    enabled: true
    google_sheets:
      spreadsheet_url: "https://docs.google.com/spreadsheets/d/1ABC..."
      get_sheets:
        - "Sheet1"
        - "Sales Data"
```

Check `.dlt/secrets.toml` (gitignored):

```toml
[sources.google_sheets.credentials]
client_id = "123456789-abc.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
refresh_token = "1//0eF..."
project_id = "your-project"
```

### Step 4: Sync

```bash
dango sync --source my_google_sheets
```

Data loads into `raw_my_google_sheets` schema in DuckDB.

---

## Common OAuth Sources

### Google Analytics 4 (GA4)

```yaml
- name: website_analytics
  type: google_analytics
  enabled: true
  google_analytics:
    property_id: "123456789"
    start_date: "2024-01-01"
    dimensions:
      - date
      - country
      - deviceCategory
    metrics:
      - sessions
      - pageviews
      - conversions
```

**Setup**:
```bash
dango source add
# Select "Google Analytics 4" from the list
# Follow OAuth flow
# Enter GA4 property ID when prompted
```

### Facebook Ads

```yaml
- name: facebook_campaigns
  type: facebook_ads
  enabled: true
  facebook_ads:
    account_id: "act_123456789"
    start_date: "2024-01-01"
    include_deleted: false
    access_token_env: "FACEBOOK_ACCESS_TOKEN"
```

**Setup**:
```bash
dango source add
# Select "Facebook Ads" from the list
# Follow OAuth flow (requires Facebook Business account)
# Select Ad Account when prompted
```

### HubSpot (via dlt_native)

!!! note "Manual Configuration Required"
    HubSpot is not yet wizard-supported. It requires manual dlt_native configuration.

```yaml
- name: crm_data
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: hubspot
    source_function: hubspot
```

**Setup**:
```bash
# Install HubSpot dlt extras
pip install "dlt[hubspot]"

# Add credentials to .dlt/secrets.toml
# [sources.hubspot]
# api_key = "your-hubspot-api-key"

# Sync
dango sync --source crm_data
```

See [Custom Sources](custom-sources.md) for detailed dlt_native setup.

---

## Manual Configuration

For advanced use cases, you can manually configure OAuth sources.

### Step 1: Get OAuth Credentials

Each provider requires a registered OAuth app:

#### Google (Sheets, GA4)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project (or use existing)
3. Enable API (Sheets API, GA4 API, etc.)
4. Create OAuth 2.0 credentials
5. Add `http://localhost:8080` to redirect URIs
6. Download credentials JSON

#### Facebook (Ads, Pages)

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create app (Business type)
3. Add Marketing API product
4. Generate access token
5. Copy token and app credentials

### Step 2: Configure Credentials

Edit `.dlt/secrets.toml`:

```toml
[sources.google_sheets.credentials]
client_id = "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret = "YOUR_CLIENT_SECRET"
refresh_token = ""  # Leave empty, will be populated on first auth
project_id = "your-gcp-project"
```

### Step 3: Add Source Configuration

Edit `.dango/sources.yml`:

```yaml
- name: custom_oauth_source
  type: google_sheets  # or facebook_ads, google_analytics, etc.
  enabled: true
  google_sheets:
    spreadsheet_url: "https://docs.google.com/spreadsheets/d/..."
```

### Step 4: Authenticate

```bash
dango sync --source custom_oauth_source
```

On first sync, browser opens for OAuth. After authentication, refresh token is saved to `.dlt/secrets.toml`.

---

## Token Storage & Security

### Where Tokens Are Stored

```
my-dango-project/
├── .dlt/
│   └── secrets.toml      # OAuth tokens (GITIGNORED)
├── .dango/
│   └── sources.yml       # Source config (NO SECRETS)
└── .gitignore            # Includes .dlt/
```

### .gitignore Protection

Dango automatically creates `.gitignore` with:

```gitignore
.dlt/secrets.toml
.dlt/config.toml
.env
*.env
```

**NEVER commit `.dlt/secrets.toml` to Git!**

### Token Refresh

Dango automatically refreshes expired access tokens using refresh tokens:

```
Access token expires → Dango uses refresh token → Gets new access token → Continues sync
```

No manual intervention needed unless:
- Refresh token is revoked (user removes app access)
- OAuth app credentials change
- Provider API changes

### Token Expiry Warnings

Web UI shows warnings for:
- Tokens expiring within 7 days
- Revoked tokens
- Invalid credentials

---

## Environment Variables (Alternative)

For CI/CD or server deployments, use environment variables instead of interactive OAuth:

### Step 1: Get Long-Lived Token

Complete OAuth flow once locally:
```bash
dango source add
# Select "Google Sheets" from the list
# Authenticate in browser
```

### Step 2: Extract Token

From `.dlt/secrets.toml`:
```toml
[sources.google_sheets.credentials]
refresh_token = "1//0eF5a..."  # Copy this
```

### Step 3: Set Environment Variable

```bash
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__REFRESH_TOKEN="1//0eF5a..."
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__CLIENT_ID="123..."
export SOURCES__GOOGLE_SHEETS__CREDENTIALS__CLIENT_SECRET="GOCSPX-..."
```

### Step 4: Update sources.yml

No changes needed - dlt automatically reads env vars.

### CI/CD Example (GitHub Actions)

!!! warning "Experimental"
    CI/CD deployment for OAuth sources has not been fully tested. The example below shows the expected pattern but may require adjustments for your use case.

```yaml
name: Sync Data
on:
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dango
        run: pip install getdango

      - name: Sync Data
        env:
          SOURCES__GOOGLE_SHEETS__CREDENTIALS__REFRESH_TOKEN: ${{ secrets.GS_REFRESH_TOKEN }}
          SOURCES__GOOGLE_SHEETS__CREDENTIALS__CLIENT_ID: ${{ secrets.GS_CLIENT_ID }}
          SOURCES__GOOGLE_SHEETS__CREDENTIALS__CLIENT_SECRET: ${{ secrets.GS_CLIENT_SECRET }}
        run: |
          dango sync --source my_google_sheets
```

---

## Troubleshooting

### OAuth Flow Not Opening

**Problem**: Browser doesn't open when adding OAuth source

**Solutions**:
1. Check that you're running locally (not SSH session)
2. Manually open URL shown in terminal
3. Set `BROWSER` environment variable: `export BROWSER=chrome`

### Token Expired / Invalid

**Problem**: `401 Unauthorized` or `Token expired`

**Solutions**:
1. Re-authenticate:
   ```bash
   dango source remove <name>
   dango source add
   # Select the source type from the list
   # Complete OAuth flow again
   ```

2. Check token in `.dlt/secrets.toml` is present

3. Verify OAuth app credentials are valid

### Insufficient Permissions

**Problem**: `403 Forbidden` or `Insufficient permissions`

**Solutions**:
1. Re-authenticate and grant all requested permissions
2. Check OAuth app scopes in provider console
3. Verify API is enabled (for Google Cloud)

### Rate Limiting

**Problem**: `429 Too Many Requests`

**Solutions**:
1. Add delays between syncs
2. Use incremental loading (see Built-in Sources)
3. Check provider's rate limits and upgrade plan if needed

---

## Best Practices

### 1. Use Separate OAuth Apps for Prod/Dev

Create different OAuth apps for:
- Local development
- Staging environment
- Production

Prevents token conflicts and makes debugging easier.

### 2. Set Up Monitoring for Token Expiry

Use Web UI or CLI to check token status:

```bash
dango validate
# Shows warnings for expiring tokens
```

### 3. Document OAuth Setup Steps

Create a `docs/SETUP.md` in your project:

```markdown
# OAuth Setup

## Google Sheets
1. Go to Google Cloud Console
2. Create OAuth client ID
3. Add to .dlt/secrets.toml
4. Run: dango source add (select "Google Sheets")
```

### 4. Use Service Accounts (When Available)

Some providers offer service accounts (no OAuth flow):

```toml
# Google Sheets with service account
[sources.google_sheets.credentials]
type = "service_account"
project_id = "your-project"
private_key = "-----BEGIN PRIVATE KEY-----\n..."
client_email = "service-account@project.iam.gserviceaccount.com"
```

Benefits:
- No interactive authentication
- No token expiry
- Better for automation

### 5. Rotate Tokens Regularly

For security:
1. Remove app access from provider
2. Re-authenticate with `dango source add`
3. Old tokens are invalidated

---

## Comparison: OAuth vs. API Keys

| Feature | OAuth | API Keys |
|---------|-------|----------|
| Setup | Interactive browser flow | Copy/paste key |
| Security | Scoped permissions | Full access |
| Token expiry | Yes (auto-refreshed) | Usually none |
| Revocation | User can revoke | Must regenerate key |
| Best for | End-user data | Service-to-service |

---

## Next Steps

- **[Built-in Sources](built-in-sources.md)** - See all available dlt sources
- **[Custom Sources](custom-sources.md)** - Build OAuth sources for custom APIs
- **[Web UI](../web-ui/managing-sources.md)** - Manage OAuth sources visually
- **[Troubleshooting](../getting-started/troubleshooting.md)** - Common OAuth issues
