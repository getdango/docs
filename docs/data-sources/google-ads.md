# Google Ads

Connect Google Ads as a data source using OAuth 2.0.

---

## Overview

| Feature | Details |
|---------|---------|
| **Auth** | OAuth 2.0 |
| **Incremental** | No (GAQL re-queries date ranges) |
| **Category** | Marketing & Analytics |

Google Ads loads campaign performance data into DuckDB using GAQL (Google Ads Query Language). By default, Dango creates 5 tables covering campaigns, ad groups, keywords, ads, and search terms.

---

## Prerequisites

Before adding Google Ads as a source, you need:

1. **Google Ads account** with active campaigns
2. **Developer Token** — from [Google Ads API Center](https://ads.google.com/aw/apicenter)
3. **Customer ID** — the numeric account ID (digits only, no dashes)
4. **Google Cloud project** with the Google Ads API enabled
5. **OAuth 2.0 credentials** (Client ID + Client Secret) — can be shared with other Google sources

### Developer Token vs. Customer ID vs. Manager Account

??? info "Understanding Google Ads identifiers"
    - **Developer Token**: An API access credential obtained from the [API Center](https://ads.google.com/aw/apicenter) in your Google Ads account. Required to make any API calls. New tokens start with "Test account" access (limited to test accounts) — apply for Basic or Standard access for production data.

    - **Customer ID**: The specific ads account you want to pull data from. Found in the top-right of the Google Ads interface (format: `123-456-7890`). **Enter digits only** — Dango strips dashes automatically.

    - **Manager Account (MCC)**: If you use a Manager account to manage multiple client accounts, use the **child account's** Customer ID, not the MCC ID. The MCC grants access, but data lives in the child accounts.

### Create OAuth Credentials

If you already have Google OAuth credentials from another source (e.g., Google Sheets), you can reuse them — just enable the **Google Ads API** in your Google Cloud project.

Otherwise, follow the same steps as [Google Sheets > Create OAuth Credentials](google-sheets.md#create-oauth-credentials), but enable the **Google Ads API** instead of (or in addition to) the Sheets API.

### Redirect URIs

=== "CLI Setup"

    Add this redirect URI to your Google Cloud OAuth app:

    ```
    http://localhost:8080/callback
    ```

=== "Web UI Setup"

    Add this redirect URI to your Google Cloud OAuth app:

    ```
    http://localhost:8800/api/oauth/callback
    ```

---

## Setup

### Step 1: Add Source

```bash
dango source add
# Select "Google Ads" from the list
```

### Step 2: Authenticate

The wizard will:

1. Prompt for your **Client ID** and **Client Secret** (if not already saved)
2. Open your browser to the Google consent page
3. Return to the terminal after authentication
4. Prompt for your **Developer Token** (from API Center)
5. Prompt for your **Customer ID** (digits only, no dashes)

```
Opening browser for Google authentication...
✓ Authenticated as user@example.com
? Developer Token: AbCdEfGhIjKlMnOp
? Customer ID (digits only): 1234567890
? Start date (YYYY-MM-DD) [90daysAgo]:
```

### Step 3: Sync

```bash
dango sync --source my_google_ads
```

---

## Configuration

### sources.yml

```yaml
version: '1.0'
sources:
  - name: my_google_ads
    type: google_ads
    enabled: true
    description: Google Ads campaign performance
    google_ads:
      start_date: "2024-01-01"
      queries:
        - name: campaign_stats
          query: >
            SELECT
              segments.date,
              campaign.id, campaign.name, campaign.status,
              campaign.advertising_channel_type,
              metrics.impressions, metrics.clicks,
              metrics.cost_micros, metrics.conversions,
              metrics.conversions_value, metrics.ctr,
              metrics.average_cpc, metrics.average_cpm
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'

        - name: ad_group_stats
          query: >
            SELECT
              segments.date,
              campaign.id, campaign.name,
              ad_group.id, ad_group.name, ad_group.status,
              metrics.impressions, metrics.clicks,
              metrics.cost_micros, metrics.conversions,
              metrics.conversions_value, metrics.ctr,
              metrics.average_cpc
            FROM ad_group
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'

        - name: keyword_stats
          query: >
            SELECT
              segments.date,
              campaign.id, campaign.name,
              ad_group.id, ad_group.name,
              ad_group_criterion.keyword.text,
              ad_group_criterion.keyword.match_type,
              metrics.impressions, metrics.clicks,
              metrics.cost_micros, metrics.conversions,
              metrics.ctr, metrics.average_cpc
            FROM keyword_view
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'

        - name: ad_stats
          query: >
            SELECT
              segments.date,
              campaign.id, ad_group.id,
              ad_group_ad.ad.id, ad_group_ad.ad.name,
              ad_group_ad.ad.type, ad_group_ad.status,
              metrics.impressions, metrics.clicks,
              metrics.cost_micros, metrics.conversions,
              metrics.ctr
            FROM ad_group_ad
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'

        - name: search_term_stats
          query: >
            SELECT
              segments.date,
              campaign.id, campaign.name,
              ad_group.id, ad_group.name,
              search_term_view.search_term,
              search_term_view.status,
              metrics.impressions, metrics.clicks,
              metrics.cost_micros, metrics.conversions,
              metrics.ctr, metrics.average_cpc
            FROM search_term_view
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
```

### .dlt/secrets.toml

```toml
[sources.google_ads.credentials]
client_id = "123456789-abc.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
refresh_token = "1//0eF..."
project_id = "dango-oauth"
impersonated_email = "user@example.com"
dev_token = "AbCdEfGhIjKlMnOp"
customer_id = "1234567890"
```

---

## Tables Loaded

Dango creates 5 tables by default in the `raw_{source_name}` schema:

| Table | Key Columns |
|-------|------------|
| `campaign_stats` | date, campaign name/status/type, impressions, clicks, cost_micros, conversions, CTR, CPC, CPM |
| `ad_group_stats` | date, campaign, ad group name/status, impressions, clicks, cost_micros, conversions, CTR, CPC |
| `keyword_stats` | date, campaign, ad group, keyword text/match type, impressions, clicks, cost_micros, conversions |
| `ad_stats` | date, campaign, ad group, ad name/type/status, impressions, clicks, cost_micros, conversions |
| `search_term_stats` | date, campaign, ad group, search term, impressions, clicks, cost_micros, conversions |

```sql
-- Example: query campaign performance
SELECT * FROM raw_my_google_ads.campaign_stats
WHERE date >= '2024-01-01'
ORDER BY cost_micros DESC
LIMIT 10;
```

!!! note "Cost is in micros"
    `cost_micros` is in millionths of the account currency. Divide by 1,000,000 to get the actual cost (e.g., `1500000` = $1.50 USD).

### Custom GAQL Queries

??? info "Adding custom GAQL queries"
    You can add additional GAQL queries to the `queries` array in `sources.yml`. Each query becomes a separate table.

    ```yaml
    queries:
      # ... default queries above ...

      - name: audience_stats
        query: >
          SELECT
            segments.date,
            campaign.id, campaign.name,
            metrics.impressions, metrics.clicks
          FROM campaign_audience_view
          WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    ```

    Use the [Google Ads Query Builder](https://developers.google.com/google-ads/api/fields/v17/overview_query_builder) to construct and validate GAQL queries.

    The `{start_date}` and `{end_date}` placeholders are replaced automatically by Dango based on your sync configuration.

---

## Sync Behavior

- GAQL queries **re-query the full date range** on each sync — not truly incremental
- `lookback_days: 3` — re-fetches the last 3 days to capture attribution changes
- Google Ads attribution can change for up to **30 days** after a click (depending on your attribution model). Consider increasing `lookback_days` if you need more accurate attribution data.
- First sync loads data from `start_date` to today

---

## Troubleshooting

### Customer ID Format

**Problem**: `INVALID_CUSTOMER_ID` error

**Solution**: Enter the Customer ID as **digits only**, without dashes. For example, use `1234567890` instead of `123-456-7890`.

### Manager vs. Customer Account

**Problem**: No data returned or `PERMISSION_DENIED`

**Solution**: If you use a Manager (MCC) account, enter the **child account's** Customer ID, not the MCC ID. The Manager account provides authentication access, but data lives in individual client accounts.

### Developer Token Issues

**Problem**: `DEVELOPER_TOKEN_NOT_APPROVED` or `AuthenticationError`

**Solutions**:

1. Verify your developer token at [API Center](https://ads.google.com/aw/apicenter)
2. New tokens have "Test account" access — apply for Basic or Standard access for production data
3. Ensure the token belongs to the Manager account (if using one)

### PERMISSION_DENIED

**Problem**: `PERMISSION_DENIED` on specific resources

**Solutions**:

1. Verify your Google account has access to the specified Customer ID
2. Check that the Google Ads API is enabled in your Google Cloud project
3. Re-authenticate: `dango oauth google_ads`

### 7-Day Token Expiry

**Problem**: Token stops working after 7 days

**Solution**: Your Google Cloud OAuth app is in **"Testing"** mode. Set it to **"In production"** in the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - OAuth overview and token management
- **[Sync Modes](sync-modes.md)** - Understand sync strategies
- **[Deduplication](deduplication.md)** - Handle overlapping date ranges
- **[Google Sheets](google-sheets.md)** - Share OAuth credentials with Sheets
- **[Google Analytics](google-analytics.md)** - Share OAuth credentials with GA4
