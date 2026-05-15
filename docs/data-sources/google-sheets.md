# Google Sheets

Connect Google Sheets spreadsheets as a data source using OAuth 2.0.

---

## Overview

| Feature | Details |
|---------|---------|
| **Auth** | OAuth 2.0 |
| **Incremental** | No (full reload each sync) |
| **Category** | Marketing & Analytics |

Google Sheets loads spreadsheet data into DuckDB. Each selected sheet/tab becomes a separate table. Column names come from the spreadsheet header row.

---

## Prerequisites

Before adding Google Sheets as a source, you need:

1. **Google account** with access to the spreadsheet
2. **Google Cloud project** with the Sheets API enabled
3. **OAuth 2.0 credentials** (Client ID + Client Secret) with redirect URIs configured

### Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Navigate to **APIs & Services > Library**
4. Search for and enable **Google Sheets API**
5. Go to **APIs & Services > Credentials**
6. Click **Create Credentials > OAuth client ID**
7. Select **Desktop app** as the application type
8. Add redirect URIs (see below)
9. Copy the **Client ID** and **Client Secret**

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

!!! tip "Google testing mode"
    If your OAuth app is in **"Testing"** status, refresh tokens expire after **7 days**. Move your app to **"In production"** status to get permanent tokens. Apps with limited scopes (like Sheets read-only) do not require Google verification.

---

## Setup

### Step 1: Add Source

```bash
dango source add
# Select "Google Sheets" from the list
```

### Step 2: Authenticate

The wizard will:

1. Prompt for your **Client ID** and **Client Secret** (saved to `.env` for reuse across Google sources)
2. Open your browser to the Google consent page
3. Select your Google account and click **Allow**
4. Return to the terminal after authentication

```
? Spreadsheet ID or URL: https://docs.google.com/spreadsheets/d/1ABC.../edit
Opening browser for Google authentication...
✓ Authenticated as user@example.com
? Select sheets/tabs to load:
  [x] Sheet1
  [x] Sales Data
  [ ] Notes
```

### Step 3: Select Sheets

Choose which sheets/tabs to load. Each selected sheet becomes a table in DuckDB.

### Step 4: Sync

```bash
dango sync --source my_google_sheets
```

---

## Configuration

### sources.yml

```yaml
version: '1.0'
sources:
  - name: my_google_sheets
    type: google_sheets
    enabled: true
    description: Monthly sales data from shared spreadsheet
    google_sheets:
      spreadsheet_url_or_id: "https://docs.google.com/spreadsheets/d/1ABC..."
      range_names:
        - "Sheet1"
        - "Sales Data"
```

### .dlt/secrets.toml

Credentials are stored automatically during the OAuth flow:

```toml
[sources.google_sheets.credentials]
client_id = "123456789-abc.apps.googleusercontent.com"
client_secret = "GOCSPX-..."
refresh_token = "1//0eF..."
project_id = "dango-oauth"
```

!!! warning "Never commit secrets"
    `.dlt/secrets.toml` is gitignored by default. Never add it to version control.

---

## Tables Loaded

Each selected sheet becomes a table in the `raw_{source_name}` schema:

```sql
-- Source name: my_google_sheets, sheet: "Sales Data"
SELECT * FROM raw_my_google_sheets.sales_data LIMIT 10;
```

- Table names are the sheet name, lowercased with spaces replaced by underscores
- Column names come from the spreadsheet header row (first row)
- Data types are inferred automatically

---

## Sync Behavior

- **Full reload** every sync — all data is replaced, not appended
- No incremental loading (the Sheets API does not support change tracking)
- All rows from the selected sheets are fetched on every sync

!!! tip "Deduplication"
    Since Google Sheets uses full reload, consider using `latest_only` dedup mode if you add the source to a schedule. See [Deduplication](deduplication.md) for details.

---

## Troubleshooting

### Spreadsheet Not Found

**Problem**: `404 Not Found` or `Spreadsheet not found`

**Solutions**:

1. Verify the spreadsheet URL or ID is correct
2. Ensure the spreadsheet is **shared** with the Google account you authenticated with
3. Check that the Sheets API is enabled in your Google Cloud project

### 7-Day Token Expiry

**Problem**: Token stops working after 7 days

**Solution**: Your Google Cloud OAuth app is in **"Testing"** mode. Go to the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) and set the publishing status to **"In production"**.

### Insufficient Permissions

**Problem**: `403 Forbidden` when syncing

**Solutions**:

1. Re-authenticate: `dango oauth google_sheets`
2. Ensure the Sheets API is enabled in Google Cloud Console
3. Verify your OAuth app has the `spreadsheets.readonly` scope

### API Quota Limits

**Problem**: `429 Too Many Requests`

**Solution**: Google Sheets API has quota limits (300 requests per minute per project). If you have many sheets or sync frequently, consider spacing out syncs or using a dedicated Google Cloud project.

---

## Next Steps

- **[OAuth Sources](oauth-sources.md)** - OAuth overview and token management
- **[Sync Modes](sync-modes.md)** - Understand full reload vs. incremental
- **[Deduplication](deduplication.md)** - Handle duplicate data from full reloads
- **[Adding Sources](adding-sources.md)** - General source setup guide
- **[Credentials](../security/credentials.md)** - Token storage and security
