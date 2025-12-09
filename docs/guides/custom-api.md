# Custom API Integration

Build a custom data source for any REST API.

---

## What You'll Build

By the end of this tutorial, you'll have:

- A custom dlt source for a REST API
- Data synced from the API to DuckDB
- Understanding of custom source patterns

**Duration**: ~30 minutes

---

## Prerequisites

- Dango project initialized
- Python basics
- An API you want to integrate (we'll use a sample)

---

## Approach Options

Dango offers two ways to integrate custom APIs:

| Method | Best For | Effort |
|--------|----------|--------|
| **REST API source** | Simple APIs, quick setup | Low |
| **Custom dlt source** | Complex APIs, full control | Medium |

We'll cover both approaches.

---

## Option 1: REST API Source (Quick)

For simple REST APIs, use Dango's built-in REST API source.

### Step 1: Configure Source

```yaml
# .dango/sources.yml
sources:
  - name: my_api
    type: rest_api
    enabled: true
    rest_api:
      base_url: "https://api.example.com"
      headers:
        Authorization: "Bearer ${MY_API_TOKEN}"
      resources:
        - name: users
          endpoint: /users
          method: GET
        - name: orders
          endpoint: /orders
          method: GET
          params:
            status: completed
```

### Step 2: Add Credentials

```toml
# .dlt/secrets.toml
[sources.rest_api]
MY_API_TOKEN = "your-api-token-here"
```

### Step 3: Sync

```bash
dango sync --source my_api
```

### Pagination Support

For paginated APIs:

```yaml
rest_api:
  base_url: "https://api.example.com"
  resources:
    - name: users
      endpoint: /users
      pagination:
        type: page_number  # or: offset, cursor
        param: page
        start: 1
```

---

## Option 2: Custom dlt Source (Full Control)

For complex APIs or specific requirements, create a custom dlt source.

### Step 1: Create Source File

Create `custom_sources/my_api.py`:

```python
"""
Custom dlt source for My API.
"""
import dlt
from dlt.sources.helpers import requests
from typing import Iterator, Dict, Any


@dlt.source
def my_api_source(
    api_key: str = dlt.secrets.value,
    base_url: str = "https://api.example.com"
) -> Iterator[dlt.DltResource]:
    """
    Load data from My API.

    Args:
        api_key: API authentication key
        base_url: API base URL
    """

    # Shared session with auth header
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    })

    @dlt.resource(write_disposition="replace")
    def users() -> Iterator[Dict[str, Any]]:
        """Load all users."""
        url = f"{base_url}/users"
        response = session.get(url)
        response.raise_for_status()

        for user in response.json()["data"]:
            yield user

    @dlt.resource(
        write_disposition="merge",
        primary_key="id"
    )
    def orders(
        updated_after: dlt.sources.incremental[str] = dlt.sources.incremental(
            "updated_at",
            initial_value="2024-01-01T00:00:00Z"
        )
    ) -> Iterator[Dict[str, Any]]:
        """Load orders incrementally."""
        url = f"{base_url}/orders"
        params = {"updated_after": updated_after.last_value}

        while url:
            response = session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            for order in data["data"]:
                yield order

            # Handle pagination
            url = data.get("next_page_url")
            params = {}  # Next page URL includes params

    # Return resources to load
    return users, orders
```

### Step 2: Configure in Dango

```yaml
# .dango/sources.yml
sources:
  - name: my_custom_api
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: "custom_sources.my_api"
      source_name: "my_api_source"
```

### Step 3: Add Credentials

```toml
# .dlt/secrets.toml
[sources.my_api_source]
api_key = "your-api-key-here"
```

### Step 4: Sync

```bash
dango sync --source my_custom_api
```

---

## Real-World Example: HubSpot

Here's a complete example for HubSpot contacts:

### Source Code

```python
# custom_sources/hubspot_contacts.py
import dlt
from dlt.sources.helpers import requests
from typing import Iterator, Dict, Any


@dlt.source
def hubspot_contacts_source(
    api_key: str = dlt.secrets.value,
) -> Iterator[dlt.DltResource]:
    """Load contacts from HubSpot."""

    base_url = "https://api.hubapi.com"

    @dlt.resource(
        write_disposition="merge",
        primary_key="id"
    )
    def contacts(
        updated_after: dlt.sources.incremental[int] = dlt.sources.incremental(
            "updatedAt",
            initial_value=0
        )
    ) -> Iterator[Dict[str, Any]]:
        """Load contacts with incremental updates."""

        url = f"{base_url}/crm/v3/objects/contacts"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {
            "limit": 100,
            "properties": "email,firstname,lastname,company,phone",
            "filterGroups": [{
                "filters": [{
                    "propertyName": "lastmodifieddate",
                    "operator": "GTE",
                    "value": str(updated_after.last_value)
                }]
            }]
        }

        while True:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            for contact in data.get("results", []):
                yield {
                    "id": contact["id"],
                    "email": contact["properties"].get("email"),
                    "first_name": contact["properties"].get("firstname"),
                    "last_name": contact["properties"].get("lastname"),
                    "company": contact["properties"].get("company"),
                    "phone": contact["properties"].get("phone"),
                    "created_at": contact["createdAt"],
                    "updated_at": contact["updatedAt"],
                }

            # Pagination
            if "paging" in data and "next" in data["paging"]:
                params["after"] = data["paging"]["next"]["after"]
            else:
                break

    return contacts
```

### Configuration

```yaml
# .dango/sources.yml
sources:
  - name: hubspot
    type: dlt_native
    enabled: true
    dlt_native:
      source_module: "custom_sources.hubspot_contacts"
      source_name: "hubspot_contacts_source"
```

```toml
# .dlt/secrets.toml
[sources.hubspot_contacts_source]
api_key = "pat-xxx"
```

---

## Handling Common Patterns

### Pagination

```python
# Offset-based
params = {"offset": 0, "limit": 100}
while True:
    response = session.get(url, params=params)
    data = response.json()
    yield from data["items"]

    if len(data["items"]) < params["limit"]:
        break
    params["offset"] += params["limit"]

# Cursor-based
cursor = None
while True:
    params = {"cursor": cursor} if cursor else {}
    response = session.get(url, params=params)
    data = response.json()
    yield from data["items"]

    cursor = data.get("next_cursor")
    if not cursor:
        break
```

### Rate Limiting

```python
import time
from dlt.sources.helpers import requests

# Built-in retry with backoff
session = requests.Session()
session.hooks["response"].append(
    lambda r, *args, **kwargs: time.sleep(0.1)  # Basic rate limit
)

# Or use dlt's rate limiter
from dlt.sources.helpers.rest_client import RESTClient

client = RESTClient(
    base_url="https://api.example.com",
    rate_limit=10,  # requests per second
)
```

### Authentication

```python
# API Key in header
session.headers["X-API-Key"] = api_key

# Bearer token
session.headers["Authorization"] = f"Bearer {token}"

# Basic auth
session.auth = (username, password)

# OAuth (use dlt's OAuth support)
from dlt.sources.helpers.rest_client.auth import OAuth2ClientCredentials

auth = OAuth2ClientCredentials(
    client_id=client_id,
    client_secret=client_secret,
    token_endpoint="https://api.example.com/oauth/token"
)
```

### Error Handling

```python
@dlt.resource
def robust_resource():
    try:
        response = session.get(url)
        response.raise_for_status()
        yield from response.json()
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limited - dlt will retry
            raise
        elif e.response.status_code == 404:
            # Not found - skip
            return
        else:
            raise
```

---

## Testing Your Source

### Local Test

```python
# test_source.py
from custom_sources.my_api import my_api_source

# Test locally
if __name__ == "__main__":
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="test_my_api",
        destination="duckdb",
        dataset_name="test_data"
    )

    source = my_api_source(api_key="your-test-key")
    load_info = pipeline.run(source)
    print(load_info)
```

Run:
```bash
python test_source.py
```

### Verify Data

```bash
duckdb data/warehouse.duckdb "SELECT * FROM test_data.users LIMIT 5"
```

---

## Project Structure

```
my-project/
├── custom_sources/
│   ├── __init__.py
│   ├── my_api.py
│   └── hubspot_contacts.py
├── .dango/
│   └── sources.yml
├── .dlt/
│   └── secrets.toml
└── data/
    └── warehouse.duckdb
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
export RUNTIME__LOG_LEVEL=DEBUG
dango sync --source my_custom_api
```

### Check dlt State

```bash
dlt pipeline my_custom_api show
```

### Inspect Raw Response

```python
# Add debug output
response = session.get(url)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")
```

---

## Summary

You've learned to integrate custom APIs:

- [x] REST API source for simple cases
- [x] Custom dlt source for full control
- [x] Pagination, auth, and error handling
- [x] Testing and debugging

### When to Use Each

| Use Case | Approach |
|----------|----------|
| Simple GET endpoints | REST API source |
| Complex auth (OAuth) | Custom dlt source |
| Custom pagination | Custom dlt source |
| Data transformation | Custom dlt source |
| Quick prototype | REST API source |

---

## Next Steps

- [dlt Workflows](../workflows/dlt-workflows.md) - Advanced dlt usage
- [Custom Sources Reference](../data-sources/custom-sources.md) - Full documentation
- [Multi-Source Integration](multi-source.md) - Combine with other sources
