# OAuth Troubleshooting

Common issues when setting up OAuth sources (Google Sheets, Google Analytics, Google Ads, Facebook Ads) and how to fix them.

---

## Consent Screen Setup

Before creating OAuth credentials, you must configure the OAuth consent screen in Google Cloud Console. This is the screen users see when authorizing your app.

### Testing vs Production Mode

| | Testing Mode | Production Mode |
|---|---|---|
| **Who can authorize** | Only emails you add as test users | Anyone with a Google account |
| **Token expiry** | **7 days** — tokens expire and must be re-authorized | No expiry (until revoked) |
| **Verification** | Not required | Requires Google review |
| **Best for** | Personal projects, small teams | Apps serving external users |

!!! warning "Testing mode tokens expire after 7 days"
    If your tokens stop working after a week, this is why. Either re-authorize (`dango oauth refresh <source_type>`) or switch to production mode.

### Setting Up the Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **OAuth consent screen**
2. Select **External** (Internal requires Google Workspace)
3. Fill in:
    - **App name**: anything (e.g., "My Analytics")
    - **User support email**: your email
    - **Developer contact**: your email
4. **Scopes**: click **Add or Remove Scopes** and add the scopes for your source:

    | Source | Required Scope |
    |--------|---------------|
    | Google Sheets | `https://www.googleapis.com/auth/spreadsheets.readonly` |
    | Google Analytics (GA4) | `https://www.googleapis.com/auth/analytics.readonly` |
    | Google Ads | `https://www.googleapis.com/auth/adwords` |

5. **Test users**: add the Google account email you'll authorize with
6. Click **Save**

### Switching to Production Mode

To avoid 7-day token expiry:

1. Go to **OAuth consent screen** → click **Publish App**
2. Google may require a verification review — for apps that only access your own data (limited users, no sensitive scopes), this is usually a quick self-attestation
3. After publishing, existing tokens continue working and new tokens don't expire

---

## Common Errors

### "App not verified" Warning

**What you see:** Google shows "This app isn't verified" with a warning screen.

**Why:** Google shows this warning for any OAuth app that hasn't gone through their verification review process. Since you created this OAuth app yourself in your own Google Cloud Console, it's unverified by default — but that's expected. No third party has access to your data. The OAuth credentials live entirely on your machine, and the app belongs to you.

**Fix:** Click through the warning — this is safe for your own data.

1. Click **Advanced** (small text at bottom left of the warning screen)
2. Click **Go to [your app name] (unsafe)** — the link text includes whatever you named your app in the consent screen
3. Review the permissions Google lists (e.g., "View your Google Sheets spreadsheets") and click **Continue** to grant them

This is a one-time step per authorization. You won't see this screen again unless you revoke access and re-authorize.

!!! tip "Want to remove the warning permanently?"
    Switch your OAuth consent screen to **Production mode** (see [Switching to Production Mode](#switching-to-production-mode) above). This also prevents the 7-day token expiry that applies to testing mode apps.

### "Access blocked: This app's request is invalid"

**Cause:** OAuth redirect URI mismatch.

**Fix:** In Google Cloud Console → **Credentials** → your OAuth client → **Authorized redirect URIs**, add:

```
http://localhost:8080/callback
```

If using the Web UI OAuth flow instead of the CLI, add this URI instead:

```
http://localhost:8800/api/oauth/callback
```

### "Port 8080 already in use"

**Cause:** A previous OAuth attempt didn't release the callback port.

**Fix:**

```bash
# Find and kill the process using port 8080
lsof -ti:8080 | xargs kill -9

# Then retry
dango source add
```

### Token Expired (7-day Testing Mode)

**Symptoms:** Syncs fail with authentication errors after working for a week.

**Fix:** Re-authorize the source:

```bash
# Option A: Refresh the existing token (simplest)
dango oauth refresh <source_type>  # e.g., google_sheets, facebook_ads

# Option B: Remove and re-add (if refresh fails)
dango oauth remove <source_type>  # e.g., google_sheets, google_ads
dango source add
# Select the same source type, same configuration
```

### "Request had insufficient authentication scopes"

**Cause:** The OAuth token was granted with fewer scopes than needed (e.g., you authorized Sheets but now want Analytics).

**Fix:** Remove the credential and re-authorize with the correct scopes:

```bash
dango oauth remove <source_type>  # e.g., google_sheets
dango source add
```

### Facebook "App Not Reviewed"

**Cause:** Facebook requires app review for certain permissions.

**Note:** Facebook tokens have a fixed 60-day expiry regardless of app review status. Set a reminder to re-authorize before tokens expire:

```bash
dango oauth remove facebook_ads
dango source add
# Complete the Facebook OAuth flow again
```

---

## Re-Authorization Flow

When tokens expire or you need to change scopes:

### Local

```bash
# 1. Try refreshing the token first
dango oauth refresh <source_type>  # e.g., google_sheets, facebook_ads

# 2. If refresh fails, remove and re-add
dango oauth remove <source_type>  # e.g., google_sheets
dango source add
# Select the source type and follow the OAuth prompts

# 3. Verify the new token works
dango sync <source_name>
```

### Cloud

After re-authorizing locally, push the updated credentials to your server:

```bash
# 1. Re-authorize locally (steps above)

# 2. Push updated credentials to cloud
dango remote push

# 3. Verify on server
dango remote logs --tail 20
```

---

## Enabling APIs

Each Google source requires its specific API enabled in Google Cloud Console:

| Source | API to Enable | Console Name |
|--------|--------------|-------------|
| Google Sheets | Google Sheets API | **Google Sheets API** (not "Sheet" — note the plural) |
| Google Analytics (GA4) | Google Analytics Data API | **Google Analytics Data API** (not Admin API) |
| Google Ads | Google Ads API | **Google Ads API** |

To enable:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Library**
2. Search for the exact API name
3. Click **Enable**

!!! tip "Google Ads also needs a Developer Token"
    Google Ads requires a Developer Token from your Google Ads account (not Google Cloud Console). Find it in Google Ads → **Tools & Settings** → **API Center**. A test account token works for development.

---

## Checking Token Status

```bash
# See all OAuth sources and token status
dango oauth status
```

This shows credentials that are expired or expiring soon, and prompts you to re-authenticate.

For a full diagnostic (client credentials, saved tokens, live validation):

```bash
dango oauth check
```

---

## Quick Reference

| Problem | Solution |
|---------|----------|
| "App not verified" warning | Click Advanced → Go to app (expected) |
| Token expired after 7 days | Switch consent screen to production mode, or re-authorize |
| Port 8080 in use | `lsof -ti:8080 \| xargs kill -9` |
| Wrong scopes | `dango oauth remove <source_type>` then re-add |
| Facebook 60-day expiry | Re-authorize before expiry, push to cloud |
| API not enabled | Enable exact API name in Google Cloud Console |
| Cloud tokens expired | Re-authorize locally, then `dango remote push` |
