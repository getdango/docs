# Custom Sources

Build custom data sources using Python and the dlt framework.

---

## Overview

When built-in sources don't fit your needs, create custom sources using Python. Dango provides a `dlt_native` source type that lets you write standard dlt code while still benefiting from Dango's configuration management and automation.

**Use Cases**:

- Internal APIs not covered by the [REST API](rest-api.md) source type
- Complex data transformations during ingestion
- Web scraping
- Proprietary data formats
- dlt verified sources not yet in the Dango wizard (Notion, Asana, Zendesk, etc.)

---

## Using dlt Verified Sources (Advanced)

!!! info "Many sources now have wizard support"
    The following sources have graduated to full wizard support and no longer need manual `dlt_native` configuration:

    - **[HubSpot](hubspot.md)** — `dango source add` > HubSpot
    - **[Salesforce](salesforce.md)** — `dango source add` > Salesforce
    - **[Database Sources](database-sources.md)** — PostgreSQL, MongoDB via wizard
    - **[REST API](rest-api.md)** — any REST API via guided wizard

    Check the [Source Catalog](source-catalog.md) for the full list of wizard-enabled sources.

For dlt verified sources not yet in the Dango wizard, configure them manually via `dlt_native`.

### Quick Guide

**Step 1: Find the dlt Source**

Browse https://dlthub.com/docs/dlt-ecosystem/verified-sources/ and find your source (e.g., `notion`, `asana`, `zendesk`).

**Step 2: Install the Source**

```bash
# Install the specific dlt source
pip install dlt[notion]  # Replace 'notion' with your source
```

**Step 3: Configure in sources.yml**

```yaml
version: '1.0'
sources:
  - name: my_notion
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: dlt.sources.notion
      source_function: notion_databases
      function_kwargs:
        database_ids:
          - "abc123..."
```

**Step 4: Add Credentials**

Create `.dlt/secrets.toml` (gitignored):

```toml
[sources.my_notion]
api_key = "your-notion-integration-token"
```

Or use environment variables in `.env`:

```bash
NOTION_API_KEY="your-notion-integration-token"
```

**Step 5: Sync**

```bash
dango sync my_notion
```

### Common Manual Sources

| Source | Module | Function | Pip Install |
|--------|--------|----------|-------------|
| Notion | `dlt.sources.notion` | `notion_databases` | `pip install dlt[notion]` |
| Asana | `dlt.sources.asana` | `asana_source` | `pip install dlt[asana]` |
| Zendesk | `dlt.sources.zendesk` | `zendesk_support` | `pip install dlt[zendesk]` |
| MySQL | `dlt.sources.sql_database` | `sql_database` | `pip install dlt[mysql]` |
| SQL Server | `dlt.sources.sql_database` | `sql_database` | `pip install dlt[mssql]` |

!!! tip "Finding Configuration"
    Always check the official dlt docs for each source's specific `function_kwargs` options:
    https://dlthub.com/docs/dlt-ecosystem/verified-sources/

---

## dlt vs. Dango Workflow

### Standard dlt Workflow

```bash
# 1. Create Python source
echo "..." > my_source.py

# 2. Run directly
python my_source.py
```

### Dango Workflow

```bash
# 1. Create Python source in custom_sources/
echo "..." > custom_sources/my_source.py

# 2. Register in sources.yml

# 3. Run via Dango
dango sync
```

**Key Difference**: In Dango, Python files in `custom_sources/` are NOT automatically discovered. You must explicitly register them in `.dango/sources.yml` with a `dlt_native` entry.

---

## Quick Start

### Step 1: Create Python File

Create `custom_sources/my_api.py`:

```python
import dlt
import requests

@dlt.source
def my_api():
    """My custom API source"""

    @dlt.resource(name="items", write_disposition="replace")
    def get_items():
        response = requests.get("https://api.example.com/items")
        response.raise_for_status()
        return response.json()["items"]

    return [get_items()]
```

### Step 2: Register in sources.yml

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: my_api
    type: dlt_native
    enabled: true
    description: My custom API data
    dlt_native:
      source_module: my_api        # Python file name (without .py)
      source_function: my_api      # Function decorated with @dlt.source
      function_kwargs: {}          # Arguments to pass to function
```

### Step 3: Sync

```bash
dango sync my_api
```

Dango will:
1. Import `custom_sources/my_api.py`
2. Call `my_api()` function
3. Load data into DuckDB (`raw_my_api.items`)
4. Generate staging models in dbt

---

## Complete Example: E-commerce API

### custom_sources/ecommerce_api.py

```python
"""
E-commerce data from DummyJSON API

This source demonstrates:
- Multiple resources (products, carts, users)
- Pagination parameters
- Error handling
"""

import dlt
import requests


@dlt.source
def ecommerce_api():
    """DummyJSON e-commerce API source"""

    @dlt.resource(name="products", write_disposition="replace")
    def get_products():
        """Fetch all products with pagination"""
        response = requests.get(
            "https://dummyjson.com/products",
            params={"limit": 100}
        )
        response.raise_for_status()
        return response.json()["products"]

    @dlt.resource(name="carts", write_disposition="replace")
    def get_carts():
        """Fetch all shopping carts"""
        response = requests.get("https://dummyjson.com/carts")
        response.raise_for_status()
        return response.json()["carts"]

    @dlt.resource(name="users", write_disposition="replace")
    def get_users():
        """Fetch user profiles"""
        response = requests.get(
            "https://dummyjson.com/users",
            params={"limit": 30}
        )
        response.raise_for_status()
        return response.json()["users"]

    return [get_products(), get_carts(), get_users()]
```

### .dango/sources.yml

```yaml
version: '1.0'
sources:
  - name: ecommerce
    type: dlt_native
    enabled: true
    description: E-commerce data from DummyJSON API
    dlt_native:
      source_module: ecommerce_api
      source_function: ecommerce_api
      function_kwargs: {}
```

### Result

After running `dango sync ecommerce`:

- **Raw tables**: `raw_ecommerce.products`, `raw_ecommerce.carts`, `raw_ecommerce.users`
- **Staging models**: Auto-generated in `dbt/models/staging/`
- **Metabase**: Tables appear in data browser

---

## Using Function Arguments

Pass configuration to your source function via `function_kwargs`:

### custom_sources/paginated_api.py

```python
import dlt
import requests

@dlt.source
def paginated_api(base_url: str, page_size: int = 100):
    """API with configurable pagination"""

    @dlt.resource(name="items", write_disposition="replace")
    def get_items():
        page = 0
        while True:
            response = requests.get(
                f"{base_url}/items",
                params={"limit": page_size, "offset": page * page_size}
            )
            response.raise_for_status()
            items = response.json()["items"]

            if not items:
                break

            yield from items
            page += 1

    return [get_items()]
```

### .dango/sources.yml

```yaml
- name: my_paginated_source
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: paginated_api
    source_function: paginated_api
    function_kwargs:
      base_url: "https://api.example.com"
      page_size: 50
```

---

## Using Environment Variables

For sensitive data like API keys, use environment variables:

### custom_sources/authenticated_api.py

```python
import os
import dlt
import requests

@dlt.source
def authenticated_api():
    """API requiring authentication"""

    api_key = os.environ.get("MY_API_KEY")
    if not api_key:
        raise ValueError("MY_API_KEY environment variable required")

    headers = {"Authorization": f"Bearer {api_key}"}

    @dlt.resource(name="data", write_disposition="replace")
    def get_data():
        response = requests.get(
            "https://api.example.com/data",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    return [get_data()]
```

### Usage

**Recommended: Use `.env` file** (persists across sessions):

```bash
# .env (gitignored)
MY_API_KEY=your-key-here
```

Then run:
```bash
dango sync my_api
```

**Alternative: Environment variable** (current session only):

```bash
export MY_API_KEY="your-key-here"
dango sync my_api
```

---

## Write Dispositions

Control how data is loaded into DuckDB:

### replace (Full Refresh)

```python
@dlt.resource(name="products", write_disposition="replace")
def get_products():
    # Drops table and reloads all data each sync
    return fetch_all_products()
```

**Use for**: Master data, small datasets, data that changes frequently

### append (Incremental Append)

```python
@dlt.resource(name="events", write_disposition="append")
def get_events():
    # Adds new rows, never deletes
    return fetch_new_events()
```

**Use for**: Logs, events, immutable data

### merge (Upsert)

```python
@dlt.resource(
    name="orders",
    write_disposition="merge",
    primary_key="order_id"
)
def get_orders():
    # Updates existing rows, inserts new ones
    return fetch_all_orders()
```

**Use for**: Transactional data that can be updated

---

## Incremental Loading

Load only new/changed data since last sync:

### Date-Based Incremental

```python
import dlt
from dlt.sources.helpers import requests

@dlt.resource(
    name="orders",
    write_disposition="append"
)
def get_orders(updated_since=dlt.sources.incremental("updated_at")):
    """Fetch orders updated since last sync"""

    response = requests.get(
        "https://api.example.com/orders",
        params={"updated_since": updated_since.last_value or "2024-01-01"}
    )

    for order in response.json():
        yield order
```

### Cursor-Based Incremental

```python
@dlt.resource(
    name="transactions",
    write_disposition="append"
)
def get_transactions(last_id=dlt.sources.incremental("id")):
    """Fetch transactions by ID cursor"""

    cursor = last_id.last_value or 0

    while True:
        response = requests.get(
            f"https://api.example.com/transactions",
            params={"after_id": cursor, "limit": 100}
        )

        data = response.json()
        if not data:
            break

        yield data
        cursor = data[-1]["id"]
```

### Lookback Window (Re-fetching Recent Data)

Some APIs retroactively update recent records (e.g., ad attribution, analytics corrections). Use dlt's `lag` parameter with incremental loading to re-fetch a window of recent data on each sync:

```python
@dlt.resource(
    name="daily_stats",
    write_disposition="merge",
    primary_key=["date", "campaign_id"]
)
def get_daily_stats(
    date_cursor=dlt.sources.incremental("date", lag=7)  # re-fetch last 7 days
):
    """Fetch stats, re-fetching recent days for corrections."""
    start = date_cursor.last_value or "2024-01-01"
    for row in fetch_stats(start_date=start):
        yield row
```

**How `lag` units work:**

The `lag` value units depend on the cursor column's data type:

| Cursor type | `lag` unit | Example |
|---|---|---|
| String date (`"2024-01-15"`) | Days | `lag=7` → re-fetch last 7 days |
| `datetime` / `DateTime` | Seconds | `lag=604800` → re-fetch last 7 days (7 * 86400) |
| Integer (ID) | Same unit as the ID | `lag=1000` → re-fetch last 1000 IDs |

Dango's built-in sources use `lookback_days` as a configuration parameter and convert internally:

- **Google Ads** (string date cursor): `lag=lookback_days` (days directly)
- **GA4** (DateTime cursor): `lag=lookback_days * 86400` (converted to seconds)

When writing your own source, choose `merge` write disposition with a primary key so re-fetched rows update in place rather than creating duplicates.

### Seed / Manual Data Files

For static reference data (mapping tables, manual inputs), place files in the `seeds/` directory:

```
my-project/
├── seeds/
│   ├── region_mapping.csv
│   └── budget_targets.csv
```

Reference seed files in dbt models:

```sql
-- dbt/models/marts/budget_vs_actual.sql
SELECT
    a.campaign_id,
    a.spend,
    b.budget
FROM {{ ref('stg_google_ads__campaign_performance') }} a
LEFT JOIN {{ ref('budget_targets') }} b ON a.campaign_id = b.campaign_id
```

Load seed files with:

```bash
dango run --select seeds
```

### Reading from DuckDB

Custom sources can read from the DuckDB warehouse directly — useful for transformations that need existing data:

```python
import dlt
import duckdb

@dlt.source
def enriched_data():
    @dlt.resource(name="enriched_orders", write_disposition="replace")
    def enrich():
        conn = duckdb.connect("data/warehouse.duckdb", read_only=True)
        orders = conn.execute("""
            SELECT o.*, c.segment
            FROM raw_my_api.orders o
            JOIN raw_my_api.customers c ON o.customer_id = c.id
        """).fetchall()
        conn.close()

        for row in orders:
            yield dict(zip(["order_id", "amount", "customer_id", "segment"], row))

    return [enrich()]
```

!!! warning "Single-writer constraint"
    Open DuckDB with `read_only=True` to avoid blocking syncs. Only one process can write to DuckDB at a time.

### Deploying Custom Sources to Cloud

Custom sources in `custom_sources/` are automatically synced to the cloud server when you run:

```bash
dango remote push
```

This uploads the `custom_sources/` directory alongside your config and dbt models. On the server, syncs run exactly as they do locally.

If your custom source needs additional Python packages, add them to `requirements.txt` in your project root:

```
# requirements.txt
requests>=2.28
beautifulsoup4>=4.12
```

These are installed on the server during `dango remote push`.

---

## Advanced Patterns

### Pagination with yield

```python
@dlt.resource(name="items", write_disposition="replace")
def get_items():
    """Fetch paginated data"""
    page = 1

    while True:
        response = requests.get(
            "https://api.example.com/items",
            params={"page": page, "per_page": 100}
        )
        response.raise_for_status()

        data = response.json()
        if not data["items"]:
            break

        # Yield each item individually
        yield from data["items"]

        page += 1
```

### Multiple Resources from One API

```python
@dlt.source
def multi_resource_api():
    """Fetch related data from one API"""

    @dlt.resource(name="customers")
    def get_customers():
        return requests.get("https://api.example.com/customers").json()

    @dlt.resource(name="orders")
    def get_orders():
        return requests.get("https://api.example.com/orders").json()

    @dlt.resource(name="products")
    def get_products():
        return requests.get("https://api.example.com/products").json()

    return [get_customers(), get_orders(), get_products()]
```

### Dependent Resources

```python
@dlt.source
def dependent_resources():
    """Fetch child data for each parent"""

    @dlt.resource(name="accounts")
    def get_accounts():
        return requests.get("https://api.example.com/accounts").json()

    @dlt.transformer(
        name="account_details",
        write_disposition="replace"
    )
    def get_account_details(account):
        """Fetch details for each account"""
        account_id = account["id"]
        response = requests.get(f"https://api.example.com/accounts/{account_id}")
        return response.json()

    return get_accounts() | get_account_details
```

---

## Error Handling

### Basic Error Handling

```python
@dlt.resource(name="data", write_disposition="replace")
def get_data():
    try:
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        raise
```

### Retry Logic

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session_with_retries():
    """Create requests session with retry logic"""
    session = requests.Session()

    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

@dlt.resource(name="data", write_disposition="replace")
def get_data():
    session = get_session_with_retries()
    response = session.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

---

## Unreferenced Sources Warning

If you create a file like `custom_sources/my_api.py` but don't add it to `sources.yml`, Dango will show a warning:

```
⚠️  Unreferenced custom sources detected:
   - custom_sources/my_api.py

These files won't be synced. To use them, add to .dango/sources.yml:

  - name: my_api
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: my_api
      source_function: <function_name>
      function_kwargs: {}
```

This warning appears in:
- `dango sync` - before syncing starts
- `dango validate` - in the General section
- `dango source list` - at the top of output

---

## Testing Custom Sources

### Test Independently First

Before integrating with Dango, test your dlt source standalone:

```python
# custom_sources/my_api.py

# ... source code ...

if __name__ == "__main__":
    # Test locally
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline",
        destination="duckdb",
        dataset_name="test"
    )

    data = my_api()
    load_info = pipeline.run(data)
    print(load_info)
```

Run:
```bash
python custom_sources/my_api.py
```

### Debugging

Add print statements:

```python
@dlt.resource(name="data")
def get_data():
    print("Fetching data...")
    response = requests.get("https://api.example.com/data")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Got {len(data)} items")
    return data
```

Run sync to see output:
```bash
dango sync my_api
```

---

## Best Practices

### 1. Always Use raise_for_status()

Fail fast on HTTP errors:

```python
response = requests.get(url)
response.raise_for_status()  # Raises exception for 4xx/5xx
```

### 2. Use Environment Variables for Secrets

Never hardcode credentials. Use `.env` file (recommended) or export:

```python
# Good - reads from .env or environment
api_key = os.environ.get("API_KEY")

# Bad - hardcoded credentials
api_key = "sk_live_abc123..."
```

Store in `.env` file (gitignored):
```bash
API_KEY=your-key-here
```

### 3. Add Docstrings

Document what each resource fetches:

```python
@dlt.resource(name="orders")
def get_orders():
    """
    Fetch all orders from the API.

    Returns:
        List of order dictionaries with id, customer_id, total, created_at
    """
    pass
```

### 4. Choose Correct write_disposition

- `replace`: Master data, small datasets
- `append`: Logs, events, immutable data
- `merge`: Transactional data with updates

### 5. Handle Pagination

Use generators for memory efficiency:

```python
def get_items():
    page = 1
    while True:
        items = fetch_page(page)
        if not items:
            break
        yield from items  # Generator, not return
        page += 1
```

### 6. Test Before Integrating

Run as standalone dlt script first, then integrate with Dango.

---

## Troubleshooting

### Source Not Appearing

1. Check file is in `custom_sources/` directory
2. Verify `source_module` matches file name (without `.py`)
3. Ensure `type: dlt_native` is set
4. Run `dango validate`

### Import Errors

1. Install dependencies in same venv as Dango
2. Check for syntax errors
3. Verify `source_function` name matches `@dlt.source` decorated function

### Data Not Loading

1. Add debug prints
2. Test standalone with `python custom_sources/my_source.py`
3. Check API responses
4. Verify data format matches expectations

---

## Next Steps

- **[REST API](rest-api.md)** - Connect any REST API without writing Python
- **[Database Sources](database-sources.md)** - Connect to SQL databases
- **[Source Catalog](source-catalog.md)** - See all wizard-enabled sources
- **[dlt Documentation](https://dlthub.com/docs)** - Official dlt docs
- **[Transformations](../transformations/index.md)** - Transform your custom source data
