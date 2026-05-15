# REST API

Connect any REST API as a data source with configurable authentication, pagination, and endpoint mapping.

---

## Overview

The REST API source type connects Dango to any HTTP-based API. Use it for APIs that aren't covered by a built-in source — internal services, niche SaaS tools, or any service with a REST interface.

**When to use REST API**:

- The API you need isn't in the [Source Catalog](source-catalog.md)
- You want a no-code/low-code setup (no Python required)
- The API returns JSON responses

**When to use [Custom Sources](custom-sources.md) instead**:

- You need complex data transformations during ingestion
- The API requires non-standard authentication flows
- You need to call multiple dependent endpoints in sequence

---

## Prerequisites

- The API's base URL (e.g., `https://api.example.com/v2`)
- Authentication credentials (API key, username/password, or OAuth2 client credentials)
- Knowledge of the endpoints you want to sync

---

## Setup

### Via Wizard (Recommended)

The wizard walks you through every step — base URL, auth, endpoints, pagination, and a live test:

```bash
dango source add
```

```
? Select a data source: REST API
? Source name: my_api
? Base URL (e.g., https://api.example.com): https://api.example.com/v2
? Authentication method: Bearer Token
? Environment variable for bearer token [MY_API_API_TOKEN]: MY_API_API_TOKEN
? Add custom headers? No
? Endpoint path (e.g., /orders): /orders
? Resource name (table name in DuckDB) [orders]: orders
? Add query parameters? No
? Pagination type: Auto-detect (recommended)
? Test this endpoint? Yes
  ✓ 200 OK — 50 records found
? Data path [data.orders] (blank=auto-detect): data.orders
? Primary key field (default: id): id
  ✓ Added: /orders → orders
? Add another endpoint? No
```

The wizard creates your configuration, tests each endpoint, and suggests the `data_selector` (JSON path to your results array) based on the API response.

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: my_api
    type: rest_api
    enabled: true
    description: My REST API data
    rest_api:
      base_url: https://api.example.com/v2
      auth_type: bearer
      auth_token_env: MY_API_API_TOKEN
      endpoints:
        - path: /orders
          name: orders
          data_selector: data.orders
        - path: /customers
          name: customers
          data_selector: data.customers
```

=== "Local"

    Store credentials in `.env`:
    ```bash
    # .env (gitignored)
    MY_API_API_TOKEN=your_token_here
    ```

=== "Cloud"

    Set credentials on the remote server:
    ```bash
    dango remote env set MY_API_API_TOKEN your_token_here
    ```

### First Sync

```bash
dango sync --source my_api
```

---

## Authentication Types

Dango supports 6 authentication methods. Choose the one that matches your API's requirements.

### Bearer Token

The most common method. Sends an `Authorization: Bearer <token>` header.

```yaml
rest_api:
  base_url: https://api.example.com
  auth_type: bearer
  auth_token_env: MY_API_TOKEN
  endpoints:
    - path: /data
      name: data
```

```bash
# .env
MY_API_TOKEN=your_bearer_token_here
```

### API Key (Header or Query)

Sends the API key as a custom header or query parameter.

=== "Header"

    ```yaml
    rest_api:
      base_url: https://api.example.com
      auth_type: api_key
      auth_token_env: MY_API_KEY
      api_key_name: X-API-Key
      api_key_location: header
      endpoints:
        - path: /data
          name: data
    ```

    Sends: `X-API-Key: your_key` in the request header.

=== "Query Parameter"

    ```yaml
    rest_api:
      base_url: https://api.example.com
      auth_type: api_key
      auth_token_env: MY_API_KEY
      api_key_name: api_key
      api_key_location: query
      endpoints:
        - path: /data
          name: data
    ```

    Appends: `?api_key=your_key` to the URL.

```bash
# .env
MY_API_KEY=your_api_key_here
```

### HTTP Basic

Username and password sent as a standard HTTP Basic auth header.

```yaml
rest_api:
  base_url: https://api.example.com
  auth_type: basic
  basic_username_env: MY_API_USERNAME
  basic_password_env: MY_API_PASSWORD
  endpoints:
    - path: /data
      name: data
```

```bash
# .env
MY_API_USERNAME=your_username
MY_API_PASSWORD=your_password
```

### OAuth2 Client Credentials

For APIs using OAuth2 Client Credentials Grant (machine-to-machine). Dango fetches an access token automatically from the token endpoint.

```yaml
rest_api:
  base_url: https://api.example.com
  auth_type: oauth2_client_credentials
  access_token_url: https://auth.example.com/oauth/token
  client_id_env: MY_API_CLIENT_ID
  client_secret_env: MY_API_CLIENT_SECRET
  endpoints:
    - path: /data
      name: data
```

```bash
# .env
MY_API_CLIENT_ID=your_client_id
MY_API_CLIENT_SECRET=your_client_secret
```

!!! warning "Not all OAuth2 APIs support Client Credentials"
    Some APIs (e.g., Shopify) require Authorization Code Grant, which involves a browser-based login flow. Client Credentials only works for APIs that support machine-to-machine authentication. If you get authentication errors, check whether the API requires a different OAuth2 flow.

### Custom Header Token

For APIs that use a non-standard header name (e.g., `X-Shopify-Access-Token`, `X-Auth-Token`).

```yaml
rest_api:
  base_url: https://mystore.myshopify.com/admin/api/2024-01
  auth_type: custom_header
  auth_header_name: X-Shopify-Access-Token
  auth_token_env: SHOPIFY_ACCESS_TOKEN
  endpoints:
    - path: /orders.json
      name: orders
      data_selector: orders
```

```bash
# .env
SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
```

### No Authentication

For public APIs that don't require authentication.

```yaml
rest_api:
  base_url: https://jsonplaceholder.typicode.com
  auth_type: none
  endpoints:
    - path: /posts
      name: posts
```

### Custom Headers (Any Auth Type)

Add extra headers to every request, regardless of auth type. Useful for API versioning, content negotiation, or additional authentication headers.

```yaml
rest_api:
  base_url: https://api.github.com
  auth_type: bearer
  auth_token_env: GITHUB_TOKEN
  headers:
    Accept: application/vnd.github.v3+json
    X-Custom-Header: my-value
  endpoints:
    - path: /user/repos
      name: repos
```

Header values can reference environment variables with `${VAR_NAME}` syntax:

```yaml
headers:
  X-Workspace-ID: ${MY_WORKSPACE_ID}
```

---

## Pagination Types

Most APIs return data in pages. Dango supports 6 pagination strategies.

### Auto-Detect (Recommended)

Omit the `paginator` field entirely. dlt inspects response headers and body to determine the correct pagination strategy automatically.

```yaml
endpoints:
  - path: /orders
    name: orders
    # No paginator — dlt auto-detects
```

!!! tip "Start with auto-detect"
    Auto-detect works for most APIs (GitHub, Stripe, HubSpot, etc.). Only specify a paginator if auto-detect fails or returns incomplete data.

### Link Header

Used by APIs that return a `Link` header with `rel="next"` (GitHub, Shopify, many REST APIs).

```yaml
endpoints:
  - path: /repos
    name: repos
    paginator: header_link
```

### Page Number

Increments a page parameter (`?page=1`, `?page=2`, etc.).

```yaml
endpoints:
  - path: /items
    name: items
    paginator:
      type: page_number
      page_param: page       # Default: "page"
```

### Cursor-Based

Uses a cursor/token from the response to fetch the next page (Stripe, Slack, GraphQL APIs).

```yaml
endpoints:
  - path: /events
    name: events
    paginator:
      type: cursor
      cursor_path: next_cursor    # Default: "next"
```

The `cursor_path` is the JSON path in the response body that contains the next page cursor.

### Offset-Based

Uses `offset` and `limit` parameters (`?offset=0&limit=100`, `?offset=100&limit=100`, etc.).

```yaml
endpoints:
  - path: /records
    name: records
    paginator:
      type: offset
      limit: 100               # Default: 100
```

### None (Single Page)

For endpoints that return all data in a single response.

```yaml
endpoints:
  - path: /config
    name: config
    paginator: single_page
```

---

## Endpoint Configuration

Each endpoint defines one API path to sync. The data from each endpoint becomes a separate table in DuckDB.

### Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `path` | Yes | — | API endpoint path (e.g., `/orders`) |
| `name` | Yes | Derived from path | Table name in DuckDB |
| `data_selector` | No | Auto-detected | JSON path to the results array |
| `primary_key` | No | `id` | Field used for merge/deduplication |
| `params` | No | — | Query parameters as key-value pairs |
| `paginator` | No | Auto-detect | Pagination strategy (see above) |

### Query Parameters

Add static query parameters to every request for an endpoint:

```yaml
endpoints:
  - path: /orders
    name: orders
    params:
      status: active
      sort: created_at
      per_page: "100"
```

### Data Path Detection

The `data_selector` tells Dango where the actual records are inside the JSON response. Many APIs wrap results in a container:

```json
{
  "status": "ok",
  "data": {
    "orders": [
      {"id": 1, "total": 99.99},
      {"id": 2, "total": 49.50}
    ]
  },
  "meta": {"page": 1, "total": 42}
}
```

For this response, set `data_selector: data.orders` to extract the orders array.

**When to set it**:

- API wraps results in an envelope (e.g., `{"data": [...]}`) — set to `data`
- API nests results deeper (e.g., `{"response": {"items": [...]}}`) — set to `response.items`
- API returns a bare array `[{...}, {...}]` — leave blank (auto-detected)

!!! tip "Use the wizard test"
    When you use the wizard and test an endpoint, Dango inspects the response and suggests the correct `data_selector`. Accept the suggestion or override it.

---

## Configuration Reference

Complete annotated YAML example:

```yaml
version: '1.0'
sources:
  - name: my_api
    type: rest_api
    enabled: true
    description: My REST API data source
    rest_api:
      # Required
      base_url: https://api.example.com/v2

      # Authentication (pick one auth_type)
      auth_type: bearer                    # bearer | api_key | basic | oauth2_client_credentials | custom_header | none
      auth_token_env: MY_API_TOKEN         # For bearer, api_key, custom_header
      # api_key_name: X-API-Key           # For api_key: header/param name
      # api_key_location: header           # For api_key: "header" or "query"
      # basic_username_env: MY_USER        # For basic
      # basic_password_env: MY_PASS        # For basic
      # access_token_url: https://...      # For oauth2_client_credentials
      # client_id_env: MY_CLIENT_ID        # For oauth2_client_credentials
      # client_secret_env: MY_SECRET       # For oauth2_client_credentials
      # auth_header_name: X-Custom-Auth    # For custom_header

      # Optional: extra headers on every request
      headers:
        Accept: application/json
        X-Custom: ${MY_ENV_VAR}            # Env var reference

      # Endpoints (at least one required)
      endpoints:
        - path: /orders
          name: orders
          data_selector: data.orders       # JSON path to results array
          primary_key: order_id            # Default: "id"
          params:
            status: active
          paginator:
            type: page_number
            page_param: page

        - path: /customers
          name: customers
          data_selector: data
          paginator: header_link           # String shorthand

        - path: /config
          name: config
          paginator: single_page           # No pagination
```

---

## Examples

### Example 1: JSONPlaceholder (No Auth, No Pagination)

The simplest possible REST API source — a public API with no authentication.

```yaml
version: '1.0'
sources:
  - name: jsonplaceholder
    type: rest_api
    enabled: true
    description: JSONPlaceholder test API
    rest_api:
      base_url: https://jsonplaceholder.typicode.com
      auth_type: none
      endpoints:
        - path: /posts
          name: posts
        - path: /users
          name: users
        - path: /comments
          name: comments
```

No `.env` file needed. Sync with:

```bash
dango sync --source jsonplaceholder
```

**Tables created**: `raw_jsonplaceholder.posts`, `raw_jsonplaceholder.users`, `raw_jsonplaceholder.comments`

### Example 2: GitHub API (Bearer Auth, Link Header Pagination)

```yaml
version: '1.0'
sources:
  - name: github
    type: rest_api
    enabled: true
    description: GitHub repository data
    rest_api:
      base_url: https://api.github.com
      auth_type: bearer
      auth_token_env: GITHUB_TOKEN
      headers:
        Accept: application/vnd.github.v3+json
      endpoints:
        - path: /user/repos
          name: repos
          paginator: header_link
          params:
            per_page: "100"
            sort: updated
        - path: /user/starred
          name: starred_repos
          paginator: header_link
          params:
            per_page: "100"
```

```bash
# .env
GITHUB_TOKEN=ghp_your_personal_access_token
```

**Tables created**: `raw_github.repos`, `raw_github.starred_repos`

??? info "Creating a GitHub token"
    1. Go to **Settings** > **Developer settings** > **Personal access tokens** > **Fine-grained tokens**
    2. Click **Generate new token**
    3. Select the repositories and permissions you need
    4. Copy the token (starts with `ghp_`)

### Example 3: Shopify API (Custom Header Auth, Data Selector)

Shopify uses a custom authentication header and wraps responses in a container object.

```yaml
version: '1.0'
sources:
  - name: shopify
    type: rest_api
    enabled: true
    description: Shopify store data
    rest_api:
      base_url: https://mystore.myshopify.com/admin/api/2024-01
      auth_type: custom_header
      auth_header_name: X-Shopify-Access-Token
      auth_token_env: SHOPIFY_ACCESS_TOKEN
      endpoints:
        - path: /orders.json
          name: orders
          data_selector: orders
          paginator: header_link
          params:
            status: any
            limit: "250"
        - path: /products.json
          name: products
          data_selector: products
          paginator: header_link
          params:
            limit: "250"
        - path: /customers.json
          name: customers
          data_selector: customers
          paginator: header_link
          params:
            limit: "250"
```

```bash
# .env
SHOPIFY_ACCESS_TOKEN=shpat_your_access_token
```

**Tables created**: `raw_shopify.orders`, `raw_shopify.products`, `raw_shopify.customers`

!!! note "Shopify data_selector"
    Shopify wraps responses like `{"orders": [...]}`. The `data_selector: orders` extracts the array from the wrapper object.

---

## Common Issues

### Pagination Not Working / Missing Data

**Symptoms**: Only the first page of results is returned.

**Solutions**:

1. Try a specific paginator instead of auto-detect. Check the API docs for how pagination works.
2. For `page_number`, verify the correct `page_param` name (some APIs use `p`, `pageNo`, etc.).
3. For `cursor`, check the correct `cursor_path` in the response body.

### 401 Unauthorized / 403 Forbidden

- Verify your credentials in `.env` are correct
- Check that the token/key hasn't expired
- For API keys, verify the key has access to the endpoints you configured
- For OAuth2, verify the `access_token_url` is correct

### Empty Data / No Records

- **Wrong `data_selector`**: Test the endpoint manually (e.g., with `curl`) and check the JSON structure. Set `data_selector` to the correct path.
- **Wrong endpoint path**: Verify the path is correct relative to the `base_url`.
- **Query parameters filtering too aggressively**: Remove `params` temporarily to test.

### data_selector Troubleshooting

If the API response looks like:

```json
{"result": {"items": [{"id": 1}, {"id": 2}]}, "count": 2}
```

Set `data_selector: result.items`.

If the API returns a bare array:

```json
[{"id": 1}, {"id": 2}]
```

Leave `data_selector` blank — dlt detects this automatically.

### Rate Limiting (429 Errors)

Most APIs enforce rate limits. dlt includes built-in retry logic with exponential backoff for 429 responses. If you still hit limits:

- Reduce the number of endpoints synced at once
- Add `per_page` or `limit` parameters to reduce request frequency
- Increase time between syncs in your schedule

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Source Catalog](source-catalog.md)** - Pre-built sources that skip manual config
- **[Custom Sources](custom-sources.md)** - Python-based sources for complex APIs
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
