# Google Analytics (GA4)

Connect Google Analytics 4 as a data source using OAuth 2.0.

---

## Overview

| Feature | Details |
|---------|---------|
| **Auth** | OAuth 2.0 |
| **Incremental** | Yes (date-based with lookback) |
| **Category** | Marketing & Analytics |

Google Analytics loads GA4 reporting data into DuckDB. By default, Dango creates 4 tables covering traffic, pages, landing pages, and geography. You can add custom queries for additional reports.

!!! note "GA4 only"
    Dango supports **Google Analytics 4 (GA4)** properties only. Universal Analytics (UA) properties are not supported — Google sunset UA in July 2024.

---

## Prerequisites

Before adding Google Analytics as a source, you need:

1. **GA4 property** (not Universal Analytics)
2. **Property ID** — a numeric ID found in GA4 Admin > Property Settings
3. **Viewer role** (or higher) on the GA4 property
4. **Google Cloud project** with the Analytics Data API enabled
5. **OAuth 2.0 credentials** (Client ID + Client Secret) — can be shared with other Google sources

### Create OAuth Credentials

If you already have Google OAuth credentials from another source (e.g., Google Sheets), you can reuse them — just enable the **Google Analytics Data API** in your Google Cloud project.

Otherwise, follow the same steps as [Google Sheets > Create OAuth Credentials](google-sheets.md#create-oauth-credentials), but enable the **Google Analytics Data API** instead of (or in addition to) the Sheets API.

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
# Select "Google Analytics 4" from the list
```

### Step 2: Authenticate

The wizard will:

1. Prompt for your **Client ID** and **Client Secret** (if not already saved from another Google source)
2. Open your browser to the Google consent page
3. Return to the terminal after authentication

### Step 3: Configure

```
? GA4 Property ID: 123456789
? Start date (YYYY-MM-DD or relative like '90daysAgo') [90daysAgo]:
```

- **Property ID**: The numeric ID from GA4 Admin > Property Settings (not the Measurement ID starting with `G-`)
- **Start date**: How far back to load on first sync. Accepts absolute dates (`2024-01-01`) or relative dates (`90daysAgo`, `30daysAgo`)

### Step 4: Sync

```bash
dango sync website_analytics
```

---

## Configuration

### sources.yml

```yaml
version: '1.0'
sources:
  - name: website_analytics
    type: google_analytics
    enabled: true
    description: Website traffic from GA4
    google_analytics:
      property_id: "123456789"
      start_date: "90daysAgo"
      queries:
        - name: traffic
          dimensions:
            - date
            - sessionSource
            - sessionMedium
            - sessionCampaignName
            - deviceCategory
          metrics:
            - sessions
            - engagedSessions
            - totalUsers
            - newUsers
            - averageSessionDuration
            - bounceRate

        - name: pages
          dimensions:
            - date
            - pagePath
            - pageTitle
          metrics:
            - screenPageViews
            - totalUsers
            - userEngagementDuration
            - sessions

        - name: landing_pages
          dimensions:
            - date
            - landingPage
            - sessionSource
            - sessionMedium
            - deviceCategory
          metrics:
            - sessions
            - totalUsers
            - engagedSessions
            - bounceRate

        - name: geo
          dimensions:
            - date
            - country
            - city
          metrics:
            - sessions
            - totalUsers
            - engagedSessions
```

### .dlt/secrets.toml

```toml
[sources.google_analytics.credentials]
client_id = "123456789-abc.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
refresh_token = "1//0eF..."
project_id = "dango-oauth"
```

---

## Tables Loaded

Dango creates 4 tables by default in the `raw_{source_name}` schema:

| Table | Dimensions | Metrics |
|-------|-----------|---------|
| `traffic` | date, sessionSource, sessionMedium, sessionCampaignName, deviceCategory | sessions, engagedSessions, totalUsers, newUsers, averageSessionDuration, bounceRate |
| `pages` | date, pagePath, pageTitle | screenPageViews, totalUsers, userEngagementDuration, sessions |
| `landing_pages` | date, landingPage, sessionSource, sessionMedium, deviceCategory | sessions, totalUsers, engagedSessions, bounceRate |
| `geo` | date, country, city | sessions, totalUsers, engagedSessions |

```sql
-- Example: query traffic data
SELECT * FROM raw_website_analytics.traffic
WHERE date >= '2024-01-01'
ORDER BY sessions DESC
LIMIT 10;
```

### Custom Queries

??? info "Adding custom dimension/metric queries"
    You can add additional queries to the `queries` array in `sources.yml`. Each query becomes a separate table.

    ```yaml
    queries:
      # ... default queries above ...

      - name: events
        dimensions:
          - date
          - eventName
        metrics:
          - eventCount
          - totalUsers

      - name: demographics
        dimensions:
          - date
          - userAgeBracket
          - userGender
        metrics:
          - totalUsers
          - sessions
    ```

    See the [GA4 Dimensions & Metrics Explorer](https://ga-dev-tools.google/ga4/dimensions-metrics-explorer/) for available fields.

---

## Sync Behavior

- **Incremental** with `lookback_days: 2` — each sync re-fetches the last 2 days to capture late-arriving data, then loads new days since the last sync
- First sync loads data from `start_date` to today
- Data is **aggregated** (not event-level) — each row is a dimension combination with summed metrics
- GA4 may take 24-48 hours to finalize data for a given day

---

## Troubleshooting

### Property Not Found

**Problem**: `Property not found` or `PERMISSION_DENIED`

**Solutions**:

1. Verify you're using a **GA4 Property ID** (numeric), not a UA property (starts with `UA-`)
2. The Property ID is NOT the Measurement ID (starts with `G-`) — find it in GA4 Admin > Property Settings
3. Ensure your Google account has at least **Viewer** role on the property

### 7-Day Token Expiry

**Problem**: Token stops working after 7 days

**Solution**: Your Google Cloud OAuth app is in **"Testing"** mode. Set it to **"In production"** in the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).

### Quota Limits

**Problem**: `429 Resource Exhausted` or quota errors

**Solution**: GA4 Data API allows 10 concurrent requests per property. If you have many queries or sync frequently, space out syncs or reduce the number of custom queries.

### No Data Returned

**Problem**: Tables are empty after sync

**Solutions**:

1. Check that the `start_date` is within the range of your GA4 data
2. Verify your property is receiving data (check GA4 Realtime report)
3. GA4 data may take 24-48 hours to appear in the API

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - OAuth overview and token management
- **[Sync Modes](sync-modes.md)** - Understand incremental loading
- **[Deduplication](deduplication.md)** - Handle lookback-day overlaps
- **[Google Sheets](google-sheets.md)** - Share OAuth credentials with Sheets
- **[Google Ads](google-ads.md)** - Share OAuth credentials with Ads
