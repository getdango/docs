# Managing Sources

Add, edit, and manage data sources through the Web UI.

---

## Overview

The Web UI provides a visual interface for managing all your data sources. Configure CSV files, OAuth integrations, databases, and custom sources without editing YAML files manually.

**What you can do**:

- Add new sources with interactive wizards
- Edit existing source configurations
- Enable/disable sources for sync
- Upload and manage CSV files
- Test source connections
- View source status and health
- Remove unused sources

---

## Accessing Source Management

Navigate to the Sources page:

```
Web UI → Sources
http://localhost:8800/sources
```

You'll see all configured sources in a grid layout with status indicators.

---

## Adding a New Source

### Interactive Source Wizard

Click the **"Add Source"** button to launch the wizard.

**Step 1: Choose Source Type**

Select from available source types:

<div class="grid cards" markdown>

-   :material-file-delimited: **CSV File**

    ---

    Upload and auto-sync CSV files.

    - Local file upload
    - Auto-detect delimiter and headers
    - File watching for auto-sync

-   :material-api: **OAuth Sources**

    ---

    Connect to cloud services.

    - Google Sheets
    - Google Analytics 4
    - Facebook Ads
    - Browser-based authentication

-   :material-database: **Database Sources**

    ---

    Connect to existing databases.

    - PostgreSQL, MySQL, SQL Server
    - Snowflake, BigQuery
    - SSL/TLS support

-   :material-package-variant: **Built-in dlt Sources**

    ---

    Verified integrations.

    - Stripe, HubSpot, Salesforce
    - Shopify, Zendesk
    - 30+ verified sources

-   :material-code-braces: **Custom Source**

    ---

    Build your own integration.

    - REST APIs
    - Custom Python code
    - dlt native sources

</div>

**Step 2: Configure Source**

Fill in source-specific fields. The form adapts based on source type selected.

**Step 3: Test Connection**

Click "Test Connection" to verify:

- Credentials are valid
- API/database is reachable
- Required permissions granted
- Data can be fetched

**Step 4: Save and Sync**

- Save source configuration
- Optionally sync immediately
- Or enable for scheduled sync

---

## CSV File Management

### Upload CSV Files

**Drag-and-Drop Interface**:

1. Navigate to Sources → CSV Files
2. Drag file into upload zone
3. Or click "Browse" to select file

**Preview and Configuration**:

After upload, preview shows:

- First 10 rows of data
- Detected column types
- Auto-detected settings

**Settings**:

```yaml
Source Name: sales_data
File: sales.csv (1.2 MB)
Delimiter: , (comma)          # Auto-detected
Header Row: Yes               # Auto-detected
Encoding: UTF-8               # Auto-detected
Date Format: YYYY-MM-DD       # Configurable
```

**Confirm and Save**:

- Click "Create Source"
- File is saved to `data/` directory
- Source added to `.dango/sources.yml`
- Optional: Sync immediately

### Replace CSV Files

Update an existing CSV source with new data:

1. Navigate to Sources
2. Find your CSV source card
3. Click "Replace File"
4. Upload new CSV
5. Preview changes
6. Confirm replacement

**What happens**:

- Old file backed up to `data/backups/`
- New file replaces old file
- Auto-sync triggered (if enabled)
- Database tables updated

### CSV File Auto-Sync

Enable auto-sync for CSV sources:

**In source card**:

```
Auto-sync: [x] Enabled
Watch for changes: [x] Enabled
Debounce: 600 seconds (10 minutes)
```

**Behavior**:

1. You edit `data/sales.csv` externally (Excel, Python script, etc.)
2. File watcher detects change
3. Waits 10 minutes (debounce period)
4. Automatically runs `dango sync --source sales_data`
5. Shows notification in Web UI

**Log output**:

```
[12:34:56] File change detected: data/sales.csv
[12:34:56] Debouncing for 600 seconds...
[12:44:56] Syncing sales_data source...
[12:45:02] ✓ Sync complete (5,432 rows)
```

### Download CSV Files

Download the original CSV file:

1. Source card → "..." menu
2. Click "Download File"
3. Browser downloads original file

Useful for:

- Sharing original data
- Backup before replacement
- Auditing source data

---

## OAuth Source Management

### Initial Authentication

**For OAuth sources** (Google Sheets, Facebook Ads, GA4):

1. Add source via wizard
2. Click "Authenticate with [Provider]"
3. Browser window opens
4. Log in to provider
5. Authorize Dango
6. Redirected back to Web UI
7. Source configured with credentials

**Example flow** (Google Sheets):

```
Step 1: Select "Google Sheets" source type
Step 2: Click "Authenticate with Google"
Step 3: Google login page opens
        → Select Google account
        → Authorize Dango to read spreadsheets
Step 4: Redirect back to Dango
Step 5: Enter spreadsheet URL or ID
Step 6: Save source
```

### View OAuth Status

Source cards show OAuth credential status:

**Healthy OAuth source**:

```
┌─────────────────────────────┐
│ 🟢 google_sheets_source     │
│ Type: Google Sheets        │
│ OAuth: ✓ Valid            │
│ Expires: Dec 15 (6 days)   │
│ Last sync: 1 hour ago      │
│ [Sync] [Edit] [Refresh]    │
└─────────────────────────────┘
```

**Expiring OAuth source**:

```
┌─────────────────────────────┐
│ 🟡 facebook_ads_source      │
│ Type: Facebook Ads         │
│ OAuth: ⚠ Expires in 2 days │
│ Last sync: 3 hours ago     │
│ [Refresh Auth] [Edit]      │
└─────────────────────────────┘
```

**Expired OAuth source**:

```
┌─────────────────────────────┐
│ 🔴 google_analytics         │
│ Type: Google Analytics 4   │
│ OAuth: ✗ Expired           │
│ Last sync: 5 days ago      │
│ [Re-authenticate] [Edit]   │
└─────────────────────────────┘
```

### Refresh OAuth Credentials

When credentials expire or are about to expire:

1. Click "Refresh Auth" on source card
2. Browser opens to provider auth page
3. Re-authorize Dango
4. Credentials updated
5. Source ready to sync again

**Or use CLI**:

```bash
dango auth refresh google_sheets_source
```

---

## Database Source Configuration

### Add Database Source

**Example**: PostgreSQL database

**Form fields**:

```
Source Name: production_db
Type: PostgreSQL

Connection Settings:
  Host: db.example.com
  Port: 5432
  Database: analytics
  Username: readonly_user
  Password: ****************  # Stored securely
  SSL Mode: require

Advanced Options:
  Schema: public
  Tables: * (all tables)
  Incremental: Yes
  Cursor Column: updated_at
  Initial Value: 2024-01-01
```

**Test Connection**:

Click "Test Connection" button:

```
Testing connection to db.example.com:5432...
✓ Connection successful
✓ Database accessible
✓ Schema 'public' found
✓ 15 tables available
Ready to sync
```

**Connection Errors**:

Common errors with fixes:

```
✗ Connection refused
  → Check host and port
  → Verify firewall rules
  → Ensure database is running

✗ Authentication failed
  → Verify username and password
  → Check user has correct permissions

✗ SSL required
  → Change SSL Mode to 'require'
  → Or disable SSL if local database
```

### Secure Credential Storage

Database credentials are stored securely:

**Never in `.dango/sources.yml`**:

```yaml
# sources.yml only stores connection info
sources:
  - name: production_db
    type: dlt_native
    dlt_native:
      source_module: sql_database
      source_function: sql_database
      # NO passwords here!
```

**Credentials stored in** `.dlt/secrets.toml`:

```toml
# .dlt/secrets.toml (gitignored)
[sources.sql_database]
credentials = "postgresql://user:password@host:5432/db"
```

**Or environment variables**:

```bash
# .env (gitignored)
POSTGRES_CREDENTIALS="postgresql://user:password@host:5432/db"
```

The Web UI automatically updates the correct file based on configuration method selected.

---

## Editing Existing Sources

### Edit Source Configuration

Click any source card to open edit modal:

**Editable fields**:

- Source name (with validation)
- Configuration parameters
- Enable/disable toggle
- Auto-sync settings
- Advanced options

**Non-editable fields**:

- Source type (recreate source to change type)
- Historical sync data (preserved during edit)

**Example edit flow**:

```
1. Click "stripe_payments" source card
2. Edit modal opens
3. Change "Start Date" from 2024-01-01 to 2024-06-01
4. Click "Save Changes"
5. Notification: "Source updated. Sync to apply changes."
6. Click "Sync Now" to fetch data from new start date
```

### Enable/Disable Sources

Toggle sources without deleting configuration:

**Disable source**:

1. Click source card
2. Toggle "Enabled" switch to OFF
3. Save changes
4. Source skipped during `dango sync`

**Re-enable source**:

1. Toggle "Enabled" switch to ON
2. Save changes
3. Source included in next sync

**Use case**:

Temporarily disable expensive or slow sources:

```
✓ stripe_payments - Enabled
✓ google_sheets - Enabled
○ old_hubspot - Disabled (not needed)
○ large_database - Disabled (too slow)
```

### Clone Source Configuration

Duplicate existing source as template:

1. Source card → "..." menu
2. Click "Clone Source"
3. New form pre-filled with existing config
4. Modify name and settings
5. Save as new source

**Example**: Create staging and production versions:

```
stripe_production (live API key)
↓ Clone
stripe_staging (test API key)
```

---

## Source Status Indicators

### Status Colors

Visual indicators show source health:

**🟢 Green - Healthy**:

- Last sync succeeded
- Credentials valid
- No warnings

**🟡 Yellow - Warning**:

- OAuth token expires soon (< 7 days)
- Slow sync performance
- Non-critical errors
- Source still functional

**🔴 Red - Error**:

- Last sync failed
- OAuth token expired
- Connection timeout
- Auth invalid
- Source cannot sync

**⚪ Gray - Disabled**:

- Source disabled in config
- Skipped during sync
- No status to report

### Detailed Status Information

Click source card to see full status:

**Sync Status**:

```
Last Sync: Dec 9, 2024 12:35 PM
Status: Success
Duration: 29.2 seconds
Rows Synced: 1,865
Next Sync: In 10 minutes (auto-sync)
```

**Connection Health**:

```
API/Database: Reachable
Authentication: Valid
Rate Limit: 95% available
Latency: 125 ms (good)
```

**Data Quality**:

```
Rows in Database: 28,693
Last Row Updated: 5 minutes ago
Schema Version: 2
Data Freshness: Current
```

---

## Bulk Operations

### Sync Multiple Sources

Select multiple sources and sync together:

1. Check boxes on source cards
2. Click "Sync Selected" button
3. All selected sources sync in parallel
4. Progress shown in Logs panel

**Or sync all**:

Click "Sync All" button to sync every enabled source.

### Bulk Enable/Disable

Toggle multiple sources at once:

1. Select sources with checkboxes
2. Click "Enable Selected" or "Disable Selected"
3. Confirm bulk action
4. All selected sources updated

**Use case**: Disable all test sources before production sync.

### Bulk Delete

Remove multiple sources:

1. Select sources with checkboxes
2. Click "Delete Selected"
3. Confirm deletion
4. Sources removed from config
5. Data remains in database (use `dango db clean` to remove)

---

## Source Configuration Validation

### Real-Time Validation

As you fill in source configuration, Web UI validates:

**Required fields**:

```
Source Name: [sales_data]  ✓
File Path: [          ]  ✗ Required field
```

**Format validation**:

```
Email: john@example.com  ✓
Email: invalid-email     ✗ Invalid email format

URL: https://api.example.com  ✓
URL: not-a-url                ✗ Invalid URL format

Port: 5432  ✓
Port: 99999 ✗ Port must be 1-65535
```

**Name uniqueness**:

```
Source Name: stripe_payments  ✗ Name already exists
Source Name: stripe_prod      ✓ Unique name
```

### Pre-Save Validation

Before saving, Web UI checks:

1. **All required fields filled**
2. **Valid formats and types**
3. **No conflicts with existing sources**
4. **Credentials format correct** (if applicable)

If validation fails:

- Errors highlighted in red
- Descriptive error messages
- Cannot save until fixed

### Connection Testing

Test source connection before saving:

**Test Results**:

```
✓ Configuration valid
✓ Credentials accepted
✓ API/Database reachable
✓ Data accessible
✓ Permissions sufficient
✓ Ready to sync
```

**Partial Success**:

```
✓ Configuration valid
✓ API reachable
⚠ Rate limit near maximum (95% used)
✓ Ready to sync (but may be slow)
```

**Failure**:

```
✓ Configuration valid
✗ Authentication failed
  → Check API key is correct
  → Verify key has required permissions
  → Ensure key is not expired
```

---

## Source Configuration Templates

### Pre-built Templates

Web UI includes templates for common sources:

**Select template**:

```
Template: Stripe Standard
  ✓ API key authentication
  ✓ Default resources (charges, customers, subscriptions)
  ✓ Incremental sync from 90 days ago
  ✓ Recommended configuration

Apply Template → Auto-fills form
```

**Available templates**:

- **Stripe Standard** - Payments data
- **Google Sheets Read-Only** - Spreadsheet sync
- **PostgreSQL Full** - All tables
- **PostgreSQL Incremental** - Timestamp-based sync
- **MySQL Read Replica** - Optimized for replicas
- **REST API JSON** - Generic JSON API
- **CSV Daily Upload** - Daily file updates

### Save Custom Templates

Create your own reusable templates:

1. Configure source completely
2. Click "Save as Template"
3. Name your template
4. Template available for future sources

**Example**: Create "Stripe Production" template with your specific configuration, then reuse for staging, development, etc.

---

## Import/Export Configuration

### Export Sources

Download source configurations as YAML:

1. Select sources (or "Select All")
2. Click "Export Configuration"
3. Downloads `sources-export.yml`

**Use cases**:

- Backup configurations
- Share with team
- Version control
- Migrate between environments

### Import Sources

Upload YAML configuration file:

1. Click "Import Configuration"
2. Select YAML file
3. Preview sources to be imported
4. Choose:
   - **Merge** - Add to existing sources
   - **Replace** - Replace all sources
5. Confirm import

**Validation**:

Web UI validates imported file:

- YAML syntax correct
- Required fields present
- Source types valid
- No duplicate names (unless replacing)

---

## Troubleshooting

### Source Won't Add

**Error**: "Failed to add source"

**Common causes**:

1. **Duplicate name**:
   ```
   ✗ Source name 'stripe_payments' already exists
   → Choose a different name
   ```

2. **Invalid configuration**:
   ```
   ✗ Invalid API key format
   → API key must start with 'sk_'
   ```

3. **Missing credentials file**:
   ```
   ✗ Cannot write to .dlt/secrets.toml
   → Ensure file exists and is writable
   ```

### Source Won't Sync

**Error**: "Sync failed"

**Solutions**:

1. **Check source enabled**:
   - Edit source → Ensure "Enabled" is ON

2. **Test connection**:
   - Edit source → Click "Test Connection"
   - Fix any connection errors

3. **Check credentials**:
   - OAuth sources: Re-authenticate
   - API keys: Verify not expired
   - Databases: Test username/password

4. **View detailed logs**:
   - Logs panel → Filter by source name
   - Look for specific error messages

### OAuth Keeps Expiring

**Issue**: OAuth tokens expire frequently

**Solutions**:

1. **Request offline access**:
   - Some providers offer refresh tokens
   - Re-authenticate and select "Offline Access"

2. **Use service account** (if available):
   - Google: Service account with domain-wide delegation
   - More stable than user OAuth

3. **Set up reminders**:
   - Web UI shows expiration warnings
   - Re-authenticate before expiration

### CSV File Upload Fails

**Error**: "Upload failed"

**Common causes**:

1. **File too large**:
   ```
   ✗ File exceeds 100 MB limit
   → Use CLI for large files
   → Or split CSV into smaller files
   ```

2. **Invalid format**:
   ```
   ✗ Cannot parse CSV
   → Check for unclosed quotes
   → Verify delimiter is correct
   → Ensure file is valid CSV format
   ```

3. **Disk space**:
   ```
   ✗ Insufficient disk space
   → Free up space in data/ directory
   ```

---

## Best Practices

### 1. Use Descriptive Names

**Good**:
```
stripe_production_payments
marketing_facebook_ads_2024
finance_google_sheets_budget
```

**Avoid**:
```
source1
data
my_source
```

### 2. Test Connections Before Saving

Always click "Test Connection":

- Validates configuration
- Catches errors early
- Avoids failed syncs later

### 3. Document Sources

Use description field for context:

```
Name: crm_export
Description: Weekly CRM export from sales team.
             Updated every Monday at 9am.
             Contact: sales@acme.com for issues.
```

### 4. Enable Auto-Sync Carefully

Auto-sync is powerful but use wisely:

**Good use cases**:

- Development with frequently changing CSV files
- Real-time dashboards with < 1 hour latency requirement

**Avoid auto-sync when**:

- Source has API rate limits
- Syncs are expensive (large databases)
- Data updates infrequently (once per day/week)

### 5. Monitor OAuth Expiration

Check OAuth status regularly:

- Weekly review of expiring tokens
- Re-authenticate before expiration
- Set calendar reminders if needed

### 6. Version Control Configuration

After adding/editing sources via UI:

```bash
git add .dango/sources.yml
git commit -m "Add production Stripe source"
git push
```

Keeps configuration versioned and shareable.

---

## Next Steps

<div class="grid cards" markdown>

-   :material-chart-line: **Monitoring**

    ---

    Learn how to monitor sync progress and system health.

    [:octicons-arrow-right-24: Monitoring Page](monitoring-page.md)

-   :material-database-outline: **Data Sources**

    ---

    Deep dive into specific source types and configuration.

    [:octicons-arrow-right-24: Data Sources](../data-sources/index.md)

-   :material-console: **CLI Source Management**

    ---

    Alternative CLI commands for source management.

    [:octicons-arrow-right-24: Source & Sync CLI](../cli/source-sync.md)

-   :material-view-dashboard: **Web UI Overview**

    ---

    Explore other Web UI features and capabilities.

    [:octicons-arrow-right-24: Web UI Overview](web-ui-overview.md)

</div>
