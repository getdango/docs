# HubSpot

Sync CRM data from HubSpot into your data warehouse.

---

| Feature | Details |
|---------|---------|
| **Auth** | API Key (Private App Token) |
| **Env Variable** | `HUBSPOT_API_KEY` |
| **Incremental** | Yes |
| **Default Resources** | contacts, companies, deals, tickets, products, quotes, owners, properties, pipelines_deals, pipelines_tickets |
| **dlt Package** | `hubspot` |

!!! tip "Managing this source in the Web UI"
    After setup, manage this source from the **Sources** page in the Web UI (`http://localhost:8800/sources`). Trigger syncs, view history, and monitor status without using the CLI. See [Web UI — Sources](../web-ui/sources.md).

---

## Prerequisites

- A HubSpot account ([app.hubspot.com](https://app.hubspot.com))
- A **Private App Token** (not a legacy API key)

### Create a Private App Token

1. In HubSpot, go to **Settings** (gear icon) > **Integrations** > **Private Apps**
2. Click **Create a private app**
3. Name it (e.g., "Dango Data Pipeline")
4. Under **Scopes**, grant these read permissions:
    - `crm.objects.contacts.read`
    - `crm.objects.companies.read`
    - `crm.objects.deals.read`
    - `crm.objects.quotes.read`
    - `tickets` (if syncing tickets)
5. Click **Create app**
6. Copy the access token

!!! warning "Legacy API keys are deprecated"
    HubSpot deprecated legacy API keys in November 2022. Use **Private App Tokens** instead. Private App Tokens start with `pat-` and have granular scope control.

---

## Setup

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: HubSpot
? Source name: hubspot
? Environment variable for API key [HUBSPOT_API_KEY]: HUBSPOT_API_KEY
? Select resources:
  [x] contacts
  [x] companies
  [x] deals
  [x] tickets
  [x] products
  [x] quotes
  [x] owners
  [x] properties
  [x] pipelines_deals
  [x] pipelines_tickets
```

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: hubspot
    type: hubspot
    enabled: true
    description: HubSpot CRM data
    hubspot:
      api_key_env: HUBSPOT_API_KEY
      resources:
        - contacts
        - companies
        - deals
        - tickets
        - products
        - quotes
        - owners
        - properties
        - pipelines_deals
        - pipelines_tickets
```

=== "Local"

    Store the token in your project's `.env` file:
    ```bash
    # .env (gitignored)
    HUBSPOT_API_KEY=pat-na1-your-token-here
    ```

=== "Cloud"

    Set the token on your remote server:
    ```bash
    dango remote env set HUBSPOT_API_KEY pat-na1-your-token-here
    ```

### First Sync

```bash
dango sync hubspot
```

---

## Configuration

### Available Resources

| Resource | Description | Default |
|----------|-------------|---------|
| `contacts` | Contact records | Yes |
| `companies` | Company records | Yes |
| `deals` | Deal/opportunity records | Yes |
| `tickets` | Support tickets | Yes |
| `products` | Product catalog | Yes |
| `quotes` | Sales quotes | Yes |
| `owners` | HubSpot users/owners | Yes |
| `properties` | Custom property definitions | Yes |
| `pipelines_deals` | Deal pipeline stages | Yes |
| `pipelines_tickets` | Ticket pipeline stages | Yes |

All 10 resources are synced by default. To sync a subset, specify only the resources you want:

```yaml
hubspot:
  api_key_env: HUBSPOT_API_KEY
  resources:
    - contacts
    - companies
    - deals
    - tickets
```

---

## Tables Loaded

Data loads into the `raw_{source_name}` schema:

| Resource | Table Name |
|----------|-----------|
| contacts | `raw_hubspot.contacts` |
| companies | `raw_hubspot.companies` |
| deals | `raw_hubspot.deals` |
| tickets | `raw_hubspot.tickets` |
| products | `raw_hubspot.products` |
| quotes | `raw_hubspot.quotes` |
| owners | `raw_hubspot.owners` |

Query example:

```sql
SELECT id, properties__firstname, properties__lastname, properties__email
FROM raw_hubspot.contacts
LIMIT 10;
```

!!! tip "HubSpot properties"
    HubSpot stores custom fields as nested properties. In DuckDB, these appear as `properties__field_name` columns.

---

## Sync Behavior

- **Incremental**: After the first full sync, subsequent syncs fetch only records modified since the last sync.
- **Write disposition**: `merge` for most resources (upsert by ID). The `properties` resource uses `replace` (full reload each sync).
- **First sync**: Loads all historical data. Large accounts (100k+ contacts) may take 15-30 minutes.

---

## Common Issues

### "401 Unauthorized"

- Verify the token in `.env` is correct and not expired
- Check that the Private App is still active in HubSpot settings
- Ensure the token has the required scopes for the resources you selected

### Missing Data / Partial Results

- Some resources require specific scopes. Check your Private App's scope settings in HubSpot.
- Archived or deleted records are not included by default.

### Rate Limiting

HubSpot enforces API rate limits (100 calls per 10 seconds for Private Apps). Dango handles rate limiting automatically with retry logic. Very large accounts may see slower sync times.

### "403 Forbidden" on Specific Resources

Your Private App token lacks the required scope. Go to **Settings** > **Integrations** > **Private Apps**, edit your app, and add the missing scope.

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
- **[Source Catalog](source-catalog.md)** - All available data sources
- **[Transformations](../transformations/index.md)** - Transform HubSpot data with dbt
- [HubSpot Private Apps Documentation](https://developers.hubspot.com/docs/api/private-apps)
