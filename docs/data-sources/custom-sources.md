# Custom Sources

Build custom data sources using Python and the dlt framework.

---

## Overview

When built-in sources don't fit your needs, create custom sources using Python. Dango provides a `dlt_native` source type that lets you write standard dlt code while still benefiting from Dango's configuration management and automation.

**Use Cases**:

- Internal APIs
- REST APIs not in dlt's verified sources
- Web scraping
- Custom data transformation logic
- Proprietary data formats
- **Using dlt verified sources not yet in the Dango wizard** (HubSpot, Notion, Asana, etc.)

---

## Using dlt Verified Sources (Advanced)

Many popular sources like HubSpot, Notion, Asana, and Salesforce are available as [dlt verified sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources/) but not yet in the Dango wizard. You can still use them by configuring them manually via `dlt_native`.

### Quick Guide

**Step 1: Find the dlt Source**

Browse https://dlthub.com/docs/dlt-ecosystem/verified-sources/ and find your source (e.g., `hubspot`, `notion`, `asana`).

**Step 2: Install the Source**

```bash
# Install the specific dlt source
pip install dlt[hubspot]  # Replace 'hubspot' with your source
```

**Step 3: Configure in sources.yml**

```yaml
version: '1.0'
sources:
  - name: my_hubspot
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: dlt.sources.hubspot  # From dlt verified sources
      source_function: hubspot            # Function name from docs
      function_kwargs:
        api_key: ${HUBSPOT_API_KEY}      # Reference from env/secrets
```

**Step 4: Add Credentials**

Create `.dlt/secrets.toml` (gitignored):

```toml
[sources.my_hubspot]
api_key = "your-hubspot-api-key-here"
```

Or use environment variables in `.env`:

```bash
HUBSPOT_API_KEY="your-hubspot-api-key-here"
```

**Step 5: Sync**

```bash
dango sync --source my_hubspot
```

### Real Example: HubSpot

Based on the [dlt HubSpot docs](https://dlthub.com/docs/dlt-ecosystem/verified-sources/hubspot), here's a complete configuration:

**1. Install:**
```bash
pip install dlt[hubspot]
```

**2. Configure `.dango/sources.yml`:**
```yaml
sources:
  - name: hubspot_crm
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: dlt.sources.hubspot
      source_function: hubspot
      function_kwargs:
        api_key: ${HUBSPOT_API_KEY}
        include_history: false  # Set to true for historical data
```

**3. Add credentials to `.dlt/secrets.toml`:**
```toml
[sources.hubspot_crm]
api_key = "your-hubspot-private-app-token"
```

**4. Sync:**
```bash
dango sync --source hubspot_crm
```

**What gets loaded:**
- `raw_hubspot_crm.contacts`
- `raw_hubspot_crm.companies`
- `raw_hubspot_crm.deals`
- `raw_hubspot_crm.tickets`
- And more (depends on HubSpot source configuration)

### Common Manual Sources

| Source | Module | Function | Pip Install |
|--------|--------|----------|-------------|
| HubSpot | `dlt.sources.hubspot` | `hubspot` | `pip install dlt[hubspot]` |
| Notion | `dlt.sources.notion` | `notion` | `pip install dlt[notion]` |
| Asana | `dlt.sources.asana` | `asana` | `pip install dlt[asana]` |
| Salesforce | `dlt.sources.salesforce` | `salesforce` | `pip install dlt[salesforce]` |
| MongoDB | `dlt.sources.mongodb` | `mongodb` | `pip install dlt[mongodb]` |
| PostgreSQL | `dlt.sources.sql_database` | `sql_database` | `pip install dlt[postgres]` |
| MySQL | `dlt.sources.sql_database` | `sql_database` | `pip install dlt[mysql]` |

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
dango sync --source my_api
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

After running `dango sync --source ecommerce`:

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

Set environment variable before running:

```bash
export MY_API_KEY="your-key-here"
dango sync --source my_api
```

Or use `.env` file:

```bash
# .env (gitignored)
MY_API_KEY=your-key-here
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
dango sync --source my_api
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

Never hardcode credentials:

```python
# Good
api_key = os.environ.get("API_KEY")

# Bad
api_key = "sk_live_abc123..."
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

- **[Database Sources](database-sources.md)** - Connect to SQL databases
- **[Built-in Sources](built-in-sources.md)** - See all dlt verified sources
- **[dlt Documentation](https://dlthub.com/docs)** - Official dlt docs
- **[Transformations](../transformations/index.md)** - Transform your custom source data
