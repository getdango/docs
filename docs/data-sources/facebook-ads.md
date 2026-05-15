# Facebook Ads

Connect Facebook Ads as a data source using OAuth 2.0.

!!! danger "Tokens expire every 60 days"
    Facebook Ads tokens expire after **60 days** with **no automatic refresh**. Set a **45-day calendar reminder** to re-authenticate before your syncs stop working. Run `dango oauth facebook_ads` to renew.

---

## Overview

| Feature | Details |
|---------|---------|
| **Auth** | OAuth 2.0 (manual token exchange) |
| **Incremental** | Yes (date-based with lookback) |
| **Category** | Marketing & Analytics |

Facebook Ads loads campaign data and performance insights into DuckDB. By default, Dango loads campaigns, ads, ad sets, and daily performance insights.

---

## Prerequisites

Before adding Facebook Ads as a source, you need:

1. **Facebook Business account** with access to an Ad Account
2. **Ad Account ID** — the numeric ID from your Ads Manager URL (without the `act_` prefix)
3. **Facebook App** (for token exchange) — App ID and App Secret from [developers.facebook.com](https://developers.facebook.com/)

---

## Token Lifecycle

Facebook uses a unique token flow compared to other OAuth providers:

```
Short-lived token (~1 hour)
        ↓ exchanged at setup
Long-lived token (60 days)
        ↓ expires
Must re-authenticate
```

1. **At setup**: You generate a short-lived token from the [Graph API Explorer](https://developers.facebook.com/tools/explorer/), then Dango exchanges it for a 60-day long-lived token using your App ID and App Secret.
2. **During sync**: Dango uses the long-lived token directly (no auto-refresh).
3. **At expiry**: After 60 days, you must re-authenticate. If your App ID and App Secret are stored, Dango can extend the token without a full re-auth flow.

---

## Setup

### Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps > Create App**
3. Select **Business** type
4. Add the **Marketing API** product
5. Note your **App ID** and **App Secret** (Settings > Basic)

### Step 2: Generate a Short-Lived Token

1. Go to the [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Grant the required permissions: `ads_read`, `ads_management`
5. Copy the token

### Step 3: Add Source

```bash
dango source add
# Select "Facebook Ads" from the list
```

Or authenticate directly:

```bash
dango oauth facebook_ads
```

The wizard will:

1. Prompt for your **short-lived access token** (from Graph API Explorer)
2. Prompt for your **App ID** and **App Secret**
3. Exchange for a **60-day long-lived token**
4. Prompt for your **Ad Account ID** (numeric, without `act_` prefix)

```
? Short-lived Access Token: EAABs...
? Facebook App ID: 123456789
? Facebook App Secret: abc123...
✓ Token exchanged — valid for 60 days (expires 2024-07-15)
? Ad Account ID (numeric): 987654321
```

### Step 4: Sync

```bash
dango sync --source facebook_campaigns
```

---

## Configuration

### sources.yml

```yaml
version: '1.0'
sources:
  - name: facebook_campaigns
    type: facebook_ads
    enabled: true
    description: Facebook ad campaign performance
    facebook_ads:
      account_id: "987654321"
      access_token_env: "FB_ACCESS_TOKEN"
      initial_load_past_days: 30
```

### .env

The long-lived access token is stored in your `.env` file:

```bash
FB_ACCESS_TOKEN=EAABs...long-lived-token...
```

!!! warning "Never commit secrets"
    `.env` is gitignored by default. Never add it to version control.

---

## Resources and Tables

### Available Resources

| Resource | Default | Description |
|----------|---------|-------------|
| `campaigns` | Yes | Campaign metadata (name, status, objective) |
| `ads` | Yes | Individual ad metadata |
| `ad_sets` | Yes | Ad set targeting and budget |
| `facebook_insights` | Yes | Daily performance metrics |
| `ad_creatives` | No | Creative assets and copy |
| `leads` | No | Lead form submissions |

### Default Tables Loaded

Data loads into the `raw_{source_name}` schema:

```sql
-- Campaign metadata
SELECT * FROM raw_facebook_campaigns.campaigns LIMIT 10;

-- Daily performance insights
SELECT * FROM raw_facebook_campaigns.facebook_insights
WHERE date_start >= '2024-01-01'
ORDER BY spend DESC
LIMIT 10;
```

The `facebook_insights` table includes key metrics:

- **reach** — unique users who saw the ad
- **impressions** — total times the ad was shown
- **clicks** — total clicks
- **spend** — amount spent (in account currency)
- **ctr** — click-through rate
- **cpc** — cost per click
- **cpm** — cost per 1,000 impressions

---

## Sync Behavior

- **Incremental** with `lookback_days: 3` — re-fetches the last 3 days to capture attribution updates
- First sync loads the past **30 days** of insights (configurable via `initial_load_past_days`)
- Facebook retains insights data for **37 months**
- Entity data (campaigns, ads, ad_sets) is fully reloaded each sync

---

## Renewing Tokens

### Option 1: Auto-Extend (If App Credentials Stored)

If you provided your App ID and App Secret during initial setup, Dango can extend the token:

```bash
dango oauth facebook_ads
# Dango detects the existing token and offers to extend it
# ✓ Token extended — valid for 60 more days
```

### Option 2: Full Re-Authentication

If auto-extend is unavailable, generate a new short-lived token from the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) and run the setup again:

```bash
dango oauth facebook_ads
# Enter new short-lived token when prompted
```

---

## Troubleshooting

### Token Expired

**Problem**: `Error validating access token` or sync failures after 60 days

**Solution**: Re-authenticate immediately:

```bash
dango oauth facebook_ads
```

Set a 45-day calendar reminder to renew before expiry.

### Account ID Format

**Problem**: `Invalid account ID` error

**Solution**: Use the **numeric ID only**, without the `act_` prefix. For example, use `987654321` instead of `act_987654321`. Find it in the Ads Manager URL.

### Rate Limits

**Problem**: `User request limit reached` or `Application request limit reached`

**Solution**: Facebook rate limits are 200 calls per hour per user and 4,800 per day per app. Solutions:

1. Reduce sync frequency
2. Remove unused resources (e.g., `ad_creatives`, `leads`)
3. Use a dedicated Facebook app for Dango

### Permission Errors

**Problem**: `OAuthException` with code 200 or 10

**Solutions**:

1. Re-generate the access token with `ads_read` and `ads_management` permissions
2. Verify your Facebook account has access to the Ad Account
3. Check that your Facebook App has the Marketing API product added

### Token Debugger

Use the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) to check your token's status, permissions, and expiry date.

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - OAuth overview and token management
- **[Sync Modes](sync-modes.md)** - Understand incremental loading
- **[Deduplication](deduplication.md)** - Handle lookback-day overlaps
- **[Adding Sources](adding-sources.md)** - General source setup guide
- **[Credentials](../security/credentials.md)** - Token storage and security
