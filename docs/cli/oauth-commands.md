# OAuth Commands

Set up and manage OAuth connections for Google and Facebook data sources.

---

## Overview

The `dango oauth` commands manage OAuth provider credentials. These are used by data sources that require OAuth authentication (Google Sheets, Google Analytics, Google Ads, Facebook Ads).

**All 10 subcommands:**

| Command | Description |
|---------|-------------|
| `oauth setup` | Interactive setup wizard for a provider |
| `oauth status` | Show credential expiry status |
| `oauth check` | Validate OAuth configuration |
| `oauth list` | List all credentials |
| `oauth remove` | Remove a credential |
| `oauth refresh` | Re-authenticate a credential |
| `oauth google_sheets` | Authenticate Google Sheets |
| `oauth google_analytics` | Authenticate Google Analytics (GA4) |
| `oauth google_ads` | Authenticate Google Ads |
| `oauth facebook_ads` | Authenticate Facebook Ads |

!!! info
    OAuth commands manage **provider connections** (Google, Facebook). For user authentication and access control, see [Auth Commands](auth-commands.md).

---

## Setup

### dango oauth setup

Interactive OAuth setup wizard for a provider.

```bash
dango oauth setup {google|facebook}
```

| Argument | Description |
|----------|-------------|
| `google` | Set up Google OAuth (covers Sheets, Analytics, Ads) |
| `facebook` | Set up Facebook OAuth (covers Facebook Ads) |

```bash
dango oauth setup google
dango oauth setup facebook
```

The wizard guides you through creating OAuth credentials in the provider's developer console and authorizing Dango.

---

## Provider-Specific Authentication

### dango oauth google_sheets

Authenticate with Google Sheets using OAuth.

```bash
dango oauth google_sheets
```

**Flow:**

1. Create OAuth credentials in Google Cloud Console
2. Authorize Dango via browser
3. Credentials saved to `.dlt/secrets.toml`

---

### dango oauth google_analytics

Authenticate with Google Analytics (GA4) using OAuth.

```bash
dango oauth google_analytics
```

Same browser-based OAuth flow as Google Sheets.

---

### dango oauth google_ads

Authenticate with Google Ads using OAuth.

```bash
dango oauth google_ads
```

Same browser-based OAuth flow as Google Sheets.

---

### dango oauth facebook_ads

Authenticate with Facebook Ads using OAuth.

```bash
dango oauth facebook_ads
```

**Flow:**

1. Get a short-lived access token from Facebook Graph API Explorer
2. Exchange it for a long-lived token (60 days)
3. Credentials saved to `.dlt/secrets.toml`

!!! warning
    Facebook tokens expire after 60 days and must be manually refreshed. Run `dango oauth refresh <source_type>` before expiry.

---

## Credential Management

### dango oauth status

Show OAuth credential expiry status. Highlights credentials that are expired or expiring soon.

```bash
dango oauth status
```

---

### dango oauth check

Validate OAuth configuration and credential status. Checks:

- OAuth client credentials in `.env`
- Saved OAuth tokens in `.dlt/secrets.toml`
- Token expiry status

```bash
dango oauth check
```

---

### dango oauth list

List all configured OAuth credentials with account info, expiry status, and usage.

```bash
dango oauth list
```

---

### dango oauth remove

Remove an OAuth credential.

```bash
dango oauth remove SOURCE_TYPE
```

| Argument | Description |
|----------|-------------|
| `SOURCE_TYPE` | Source type to remove credentials for (e.g., `google_ads`, `facebook_ads`) |

```bash
dango oauth remove google_ads
```

---

### dango oauth refresh

Re-authenticate an OAuth credential. Use when a token is expired or about to expire.

```bash
dango oauth refresh SOURCE_TYPE
```

| Argument | Description |
|----------|-------------|
| `SOURCE_TYPE` | Source type to refresh credentials for (e.g., `google_sheets`, `facebook_ads`) |

```bash
dango oauth refresh facebook_ads
```

---

## Token Lifecycle

=== "Google"

    Google OAuth tokens are automatically refreshed by dlt using the refresh token. No manual intervention needed unless the refresh token itself is revoked.

    **Typical lifetime:** Indefinite (auto-refreshed)

=== "Facebook"

    Facebook long-lived tokens expire after 60 days. You must manually refresh before expiry.

    **Typical lifetime:** 60 days

    Set a reminder to run `dango oauth refresh` before expiry.

---

## Troubleshooting

??? info "OAuth token expired"
    Run `dango oauth status` to see which tokens are expired. Use `dango oauth refresh <source_type>` to re-authenticate. For Google, tokens auto-refresh — if expired, re-run the provider command (e.g., `dango oauth google_sheets`).

??? info "OAuth check shows missing credentials"
    Ensure your `.env` file contains the OAuth client ID and secret. Run `dango oauth setup google` or `dango oauth setup facebook` to set up from scratch.

??? info "Browser doesn't open during OAuth flow"
    Copy the URL from the terminal and paste it into your browser manually. The OAuth flow uses a local callback server to receive the authorization code.

??? info "Facebook token needs frequent refresh"
    Facebook long-lived tokens last 60 days. This is a Facebook platform limitation. Consider using `dango schedule` to set a reminder, or switch to a different data source if available.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [Auth Commands](auth-commands.md) — User authentication (separate from OAuth)
- [Source & Sync](source-sync.md) — Sync data from OAuth-authenticated sources
- [OAuth & Credentials Guide](../security/credentials.md) — How OAuth credentials are stored and managed
