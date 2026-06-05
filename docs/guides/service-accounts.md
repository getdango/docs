# Service Account Credentials

How to use Google service account JSON keys instead of OAuth for headless or automated setups.

---

## When to Use Service Accounts vs OAuth

| | Service Account | OAuth |
|---|---|---|
| **Best for** | Servers, CI/CD, automated pipelines | Personal accounts, interactive setup |
| **Authentication** | JSON key file (no browser needed) | Browser-based consent flow |
| **Token expiry** | Never expires | Google: auto-refreshed; Facebook: 60 days |
| **Data access** | Only data explicitly shared with the service account | All data the authenticated user can access |

**Use a service account when:**

- You're running Dango on a server without a browser (cloud deployments, CI)
- You want to avoid token expiry entirely
- You're accessing shared resources (e.g., team Google Sheets)

**Use OAuth when:**

- You need access to personal data (e.g., your own Google Analytics property)
- You're doing initial local development and want the simplest setup
- The data source doesn't support service accounts (e.g., Facebook Ads)

---

## Supported Sources

Service accounts work with Google sources that support them:

| Source | Service Account Support | Notes |
|--------|------------------------|-------|
| **Google Sheets** | Yes | Share the sheet with the service account email |
| **Google Analytics (GA4)** | Yes | Add service account as viewer in GA4 property |
| **Google Ads** | With domain-wide delegation | Requires Google Workspace admin setup |
| **Facebook Ads** | No | Facebook only supports OAuth tokens |

---

## Setup Steps

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name it (e.g., "dango-data") and click **Create and Continue**
4. Skip the optional role and user access steps → click **Done**
5. Click the service account you just created → **Keys** tab → **Add Key** → **Create new key** → **JSON**
6. Download the JSON key file — you'll need values from it in the next step

### 2. Enable the Required API

Enable the API for the source you're connecting (same as for OAuth):

| Source | API to Enable |
|--------|--------------|
| Google Sheets | **Google Sheets API** |
| Google Analytics (GA4) | **Google Analytics Data API** |
| Google Ads | **Google Ads API** |

Go to **APIs & Services** → **Library** → search and enable.

### 3. Configure Credentials in `.dlt/secrets.toml`

Open `.dlt/secrets.toml` and add the service account credentials using values from the downloaded JSON key:

```toml
[sources.google_sheets.credentials]
type = "service_account"
project_id = "your-project-id"
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEv..."
client_email = "dango-data@your-project-id.iam.gserviceaccount.com"
```

Replace `google_sheets` with the appropriate source type (`google_analytics`, `google_ads`) if needed.

!!! warning "Keep the `\n` in `private_key`"
    The private key value from the JSON file contains literal `\n` characters. Keep them as-is — dlt handles the conversion.

### 4. Share Data with the Service Account

The service account is a separate Google identity — it can only access data explicitly shared with it.

=== "Google Sheets"

    Open the Google Sheet → click **Share** → paste the service account email (`dango-data@your-project-id.iam.gserviceaccount.com`) → grant **Viewer** access.

=== "Google Analytics (GA4)"

    Go to GA4 → **Admin** → **Property Access Management** → **Add users** → paste the service account email → grant **Viewer** role.

=== "Google Ads"

    Google Ads requires [domain-wide delegation](https://developers.google.com/identity/protocols/oauth2/service-account#delegatingauthority) configured by a Google Workspace admin. The service account impersonates a user with Google Ads access.

### 5. Add the Source

Run the source wizard as usual:

```bash
dango source add
```

Select the source type (e.g., Google Sheets). dlt auto-detects the credential type from `.dlt/secrets.toml` — no code changes needed.

---

## Cloud Deployment

Service account credentials in `.dlt/secrets.toml` are included when you push to your server:

```bash
dango remote push
```

This is one of the main advantages over OAuth — no browser-based re-authentication needed on the server.

---

## Credential Sharing

All sources of the same type share one credential section. For example, if you have two Google Sheets sources, they both use `[sources.google_sheets.credentials]`. This means one service account needs access to all sheets used by those sources.

---

## Related Pages

- [OAuth Sources](../data-sources/oauth-sources.md) — OAuth setup for sources that don't support service accounts
- [OAuth Troubleshooting](oauth-troubleshooting.md) — Common OAuth issues
- [Credential Management](../security/credentials.md) — How Dango stores credentials
- [Cloud Deployment](../deployment/index.md) — Deploying with `dango remote push`
