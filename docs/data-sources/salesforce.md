# Salesforce

Sync CRM objects from Salesforce into your data warehouse.

---

| Feature | Details |
|---------|---------|
| **Auth** | Username + Password + Security Token |
| **Credentials** | `.dlt/secrets.toml` (not `.env`) |
| **Incremental** | Yes |
| **Default Resources** | account, contact, lead, opportunity, campaign |
| **dlt Package** | `salesforce` |

!!! tip "Managing this source in the Web UI"
    After setup, manage this source from the **Sources** page in the Web UI (`http://localhost:8800/sources`). Trigger syncs, view history, and monitor status without using the CLI. See [Web UI — Sources](../web-ui/sources.md).

---

## Prerequisites

- A Salesforce account with API access
- Your Salesforce username, password, and security token
- The `simple-salesforce` Python package (installed automatically by the wizard)

### Get Your Security Token

1. Log in to Salesforce
2. Click your profile icon > **Settings**
3. Go to **My Personal Information** > **Reset My Security Token**
4. Click **Reset Security Token** — the token is emailed to you

!!! note "Security token required"
    Salesforce requires a security token when connecting from an IP address not in your org's trusted IP ranges. The token is appended to your password during authentication.

---

## Setup

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: Salesforce
? Source name: salesforce
? Salesforce username: your.email@company.com
? Salesforce password: ********
? Security token: ********
? Select resources:
  [x] account
  [x] contact
  [x] lead
  [x] opportunity
  [x] campaign
  [ ] task
  [ ] event
  [ ] sf_user
  [ ] user_role
  [ ] product_2
```

The wizard stores credentials in `.dlt/secrets.toml` (gitignored).

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: salesforce
    type: salesforce
    enabled: true
    description: Salesforce CRM data
    salesforce:
      resources:
        - account
        - contact
        - lead
        - opportunity
        - campaign
```

Add credentials to `.dlt/secrets.toml` (gitignored):

```toml
[sources.salesforce.credentials]
user_name = "your.email@company.com"
password = "your_password"
security_token = "your_security_token"
```

!!! warning "Credentials go in `secrets.toml`, not `.env`"
    Unlike most Dango sources that use environment variables, Salesforce credentials are stored in `.dlt/secrets.toml`. This file is automatically gitignored. Never commit it to version control.

=== "Local"

    Store credentials in `.dlt/secrets.toml` as shown above. This file is inside your project directory and is gitignored.

=== "Cloud"

    For cloud deployment, set credentials as environment variables on the remote server:
    ```bash
    dango remote env set SALESFORCE_USERNAME your.email@company.com
    dango remote env set SALESFORCE_PASSWORD your_password
    dango remote env set SALESFORCE_SECURITY_TOKEN your_security_token
    ```

### First Sync

```bash
dango sync salesforce
```

---

## Configuration

### Available Resources

| Resource | Description | Default |
|----------|-------------|---------|
| `account` | Company/organization records | Yes |
| `contact` | Individual contact records | Yes |
| `lead` | Sales lead records | Yes |
| `opportunity` | Deal/opportunity records | Yes |
| `campaign` | Marketing campaign records | Yes |
| `task` | Task/activity records | No |
| `event` | Calendar event records | No |
| `sf_user` | Salesforce user records | No |
| `user_role` | User role definitions | No |
| `product_2` | Product catalog records | No |

### Full Configuration Example

```yaml
version: '1.0'
sources:
  - name: salesforce
    type: salesforce
    enabled: true
    description: Full Salesforce CRM sync
    salesforce:
      resources:
        - account
        - contact
        - lead
        - opportunity
        - campaign
        - task
        - event
        - sf_user
```

---

## Tables Loaded

Data loads into the `raw_{source_name}` schema:

| Resource | Table Name |
|----------|-----------|
| account | `raw_salesforce.account` |
| contact | `raw_salesforce.contact` |
| lead | `raw_salesforce.lead` |
| opportunity | `raw_salesforce.opportunity` |
| campaign | `raw_salesforce.campaign` |
| task | `raw_salesforce.task` |
| event | `raw_salesforce.event` |
| sf_user | `raw_salesforce.sf_user` |
| user_role | `raw_salesforce.user_role` |
| product_2 | `raw_salesforce.product_2` |

Query example:

```sql
SELECT id, name, industry, annual_revenue
FROM raw_salesforce.account
ORDER BY annual_revenue DESC
LIMIT 10;
```

---

## Sync Behavior

- **Incremental**: After the first full sync, subsequent syncs fetch only records modified since the last sync.
- **Write disposition**: Varies by resource — `merge` for account, opportunity, task, event (upsert by ID); `replace` for contact, lead, campaign, sf_user, user_role, product_2 (full reload each sync).
- **First sync**: Loads all objects. Large Salesforce orgs (100k+ records) may take 30+ minutes.

---

## Common Issues

### "INVALID_LOGIN: Invalid username, password, security token"

- Verify all three credentials in `.dlt/secrets.toml`
- Reset your security token (Salesforce emails a new one after reset)
- Check that your password hasn't expired
- If your org uses SSO, you may need a Salesforce-specific password

### "INSUFFICIENT_ACCESS" Errors

Your Salesforce user profile may lack API access or object permissions:

1. In Salesforce Setup, go to **Profiles** > your profile
2. Ensure **API Enabled** is checked
3. Verify read access to the objects you're syncing

### "REQUEST_LIMIT_EXCEEDED"

Salesforce enforces daily API call limits based on your edition. Check your remaining API calls in **Setup** > **Company Information**. Consider syncing fewer resources or reducing sync frequency.

### Missing Fields

Salesforce field-level security may restrict access to certain fields. Check your profile's field-level permissions for each object.

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
- **[Source Catalog](source-catalog.md)** - All available data sources
- **[Transformations](../transformations/index.md)** - Transform Salesforce data with dbt
- [Salesforce API Documentation](https://developer.salesforce.com/docs/apis)
