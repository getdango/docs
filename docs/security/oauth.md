# OAuth Token Handling

OAuth token lifecycle and security considerations.

---

## Overview

Dango uses OAuth for sources that require user authorization:

- Google Sheets
- Google Analytics (GA4)
- Facebook Ads
- Google Ads

---

## How OAuth Works in Dango

### Authentication Flow

```
1. You run: dango auth google_sheets

2. Browser opens to Google login

3. You authorize Dango to access your data

4. Google returns tokens to Dango

5. Tokens stored securely in keyring
```

### Token Types

| Token | Purpose | Lifetime |
|-------|---------|----------|
| **Access Token** | API requests | 1 hour |
| **Refresh Token** | Get new access tokens | Long-lived* |

*Refresh tokens can expire if unused for extended periods or if revoked.

---

## Token Storage

### Location

OAuth tokens are stored in the system keyring:

| Platform | Storage |
|----------|---------|
| macOS | Keychain |
| Linux | Secret Service |
| Windows | Credential Manager |

### What's Stored

```
Service: dango_oauth
Account: google_sheets
Data: {
  "access_token": "ya29.xxx",
  "refresh_token": "1//xxx",
  "expires_at": "2024-01-15T10:30:00Z",
  "token_type": "Bearer",
  "scope": "https://www.googleapis.com/auth/spreadsheets.readonly"
}
```

---

## Token Lifecycle

### Initial Authentication

```bash
# Authenticate with Google Sheets
dango auth google_sheets
```

1. Opens browser to Google consent screen
2. You approve access
3. Tokens saved to keyring

### Token Refresh

Dango automatically refreshes expired access tokens:

```
Sync starts
├── Check access token
├── Token expired?
│   ├── Yes: Use refresh token to get new access token
│   └── No: Use existing access token
└── Make API request
```

No manual intervention needed for routine refresh.

### Token Expiry

**Access tokens**: Expire after ~1 hour
- Refreshed automatically

**Refresh tokens**: Can expire due to:
- 6+ months of inactivity
- User revokes access
- Password change (some providers)
- Reaching token limit

**When refresh token expires**:
```bash
# Re-authenticate
dango auth google_sheets
```

---

## Managing OAuth Tokens

### Check Token Status

```bash
# List all authenticated providers
dango auth list

# Check specific provider
dango auth status --provider google_sheets
```

Example output:
```
Provider: google_sheets
Status: Authenticated
Expires: 2024-01-15 10:30:00
Scopes: spreadsheets.readonly
```

### Refresh Manually

```bash
# Force token refresh
dango auth refresh --provider google_sheets
```

### Remove Authorization

```bash
# Remove stored tokens
dango auth remove --provider google_sheets
```

This removes local tokens but doesn't revoke access at the provider. To fully revoke:

1. Remove from Dango: `dango auth remove`
2. Revoke in provider settings (see below)

---

## Revoking Access

### Google

1. Go to [Google Account Security](https://myaccount.google.com/permissions)
2. Find "Dango" in third-party access
3. Click "Remove Access"

### Facebook

1. Go to [Facebook Settings > Apps](https://www.facebook.com/settings?tab=applications)
2. Find "Dango"
3. Click "Remove"

### Why Revoke?

Revoke access when:
- No longer using Dango
- Credential rotation policy
- Suspected compromise
- Employee offboarding

---

## Scopes and Permissions

### What Scopes Mean

OAuth scopes define what Dango can access:

| Provider | Scope | Access |
|----------|-------|--------|
| Google Sheets | `spreadsheets.readonly` | Read spreadsheets |
| Google Analytics | `analytics.readonly` | Read analytics data |
| Facebook Ads | `ads_read` | Read ad performance |

### Minimal Permissions

Dango requests only the minimum scopes needed:

```
✓ Read spreadsheet data
✗ Edit spreadsheets
✗ Delete spreadsheets
✗ Access other Google services
```

---

## Multi-Account Handling

### Same Provider, Different Accounts

Each source can have its own OAuth credentials:

```yaml
# .dango/sources.yml
sources:
  - name: sheets_personal
    type: google_sheets
    google_sheets:
      spreadsheet_url_or_id: "xxx"

  - name: sheets_work
    type: google_sheets
    google_sheets:
      spreadsheet_url_or_id: "yyy"
```

Authenticate each:
```bash
dango auth google_sheets --source sheets_personal
dango auth google_sheets --source sheets_work
```

### Switching Accounts

```bash
# Remove current auth
dango auth remove --provider google_sheets --source my_source

# Re-authenticate with different account
dango auth google_sheets --source my_source
# Login with different Google account
```

---

## Security Considerations

### Token Security

**Protect your tokens**:
- Tokens grant access to your data
- Treat like passwords
- Don't share tokens

**Dango protections**:
- Tokens stored in system keyring (encrypted)
- Tokens never logged
- Tokens never displayed in UI

### Consent Screen Warnings

When authenticating, you may see warnings:

> "This app hasn't been verified by Google"

This is normal for development OAuth apps. Dango uses unverified OAuth credentials for simplicity. Click "Advanced" → "Go to Dango" to proceed.

### OAuth App Security

Dango's OAuth clients:
- Request minimal scopes
- Don't store data externally
- Tokens stay on your machine

---

## Troubleshooting

### "Invalid Grant" Error

**Cause**: Refresh token expired or revoked

**Solution**:
```bash
dango auth remove --provider google_sheets
dango auth google_sheets
```

### "Access Denied" Error

**Causes**:
- Insufficient permissions
- App not authorized for account type
- Organization restrictions

**Solutions**:
1. Check you're logged into correct account
2. For Google Workspace: Ask admin to allow app
3. Try with personal account

### Browser Doesn't Open

**Manual auth**:
```bash
dango auth google_sheets
# If browser doesn't open, copy the URL from terminal
# Paste in browser manually
```

### Token Not Saving

**Check keyring**:
```bash
# Verify keyring is working
python -c "import keyring; keyring.set_password('test', 'test', 'test'); print(keyring.get_password('test', 'test'))"
```

If keyring isn't working, install a backend:
```bash
pip install keyrings.alt
```

---

## Provider-Specific Notes

### Google

- Tokens valid for 6 months if unused
- Re-auth required after password change
- Workspace accounts may need admin approval

### Facebook

- Tokens have 60-day expiry for long-lived tokens
- Business accounts require Business Manager access
- App must have ads_management permission

### Best Practice

Set up calendar reminders to re-authenticate OAuth sources every 3-6 months to prevent sync failures.

---

## Next Steps

- [Credential Management](credentials.md) - API key security
- [Best Practices](best-practices.md) - Security recommendations
- [Troubleshooting](../workflows/troubleshooting.md) - Auth issues
