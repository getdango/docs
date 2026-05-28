# Stripe

Sync payment data from Stripe into your data warehouse.

---

| Feature | Details |
|---------|---------|
| **Auth** | API Key (`sk_test_` or `sk_live_`) |
| **Env Variable** | `STRIPE_API_KEY` |
| **Incremental** | No (full refresh every sync) |
| **Date Range** | Yes (default: last 90 days) |
| **Default Endpoints** | Charge, Customer, Subscription, Invoice, Product, Price |
| **dlt Package** | `stripe_analytics` |

!!! tip "Managing this source in the Web UI"
    After setup, manage this source from the **Sources** page in the Web UI (`http://localhost:8800/sources`). Trigger syncs, view history, and monitor status without using the CLI. See [Web UI — Sources](../web-ui/sources.md).

---

## Prerequisites

- A Stripe account ([dashboard.stripe.com](https://dashboard.stripe.com))
- A Stripe API key (secret key, starts with `sk_test_` or `sk_live_`)

### Get Your API Key

1. Log in to the [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** > **API keys**
3. Copy your **Secret key** (starts with `sk_test_` for test mode, `sk_live_` for production)

!!! warning "Use test keys for initial setup"
    Start with a test mode key (`sk_test_...`) to verify your pipeline works before switching to production keys.

---

## Setup

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: Stripe
? Source name: stripe
? Environment variable for API key [STRIPE_API_KEY]: STRIPE_API_KEY
? Select endpoints:
  [x] Charge
  [x] Customer
  [x] Subscription
  [x] Invoice
  [x] Product
  [x] Price
  [ ] PaymentIntent
```

The wizard creates your source configuration and prompts you to add the API key to your `.env` file.

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: stripe
    type: stripe
    enabled: true
    description: Stripe payment data
    stripe:
      stripe_secret_key_env: STRIPE_API_KEY
      endpoints:
        - Charge
        - Customer
        - Subscription
        - Invoice
        - Product
        - Price
      start_date: "2024-01-01"  # Optional: defaults to 90 days ago
```

=== "Local"

    Store the key in your project's `.env` file:
    ```bash
    # .env (gitignored)
    STRIPE_API_KEY=sk_test_your_key_here
    ```

=== "Cloud"

    Set the key on your remote server:
    ```bash
    dango remote env set STRIPE_API_KEY sk_live_your_key_here
    ```

### First Sync

```bash
dango sync stripe
```

---

## Configuration

### Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `Charge` | Payment charges (default) |
| `Customer` | Customer records (default) |
| `Subscription` | Active and past subscriptions (default) |
| `Invoice` | Invoices sent to customers (default) |
| `Product` | Product catalog entries (default) |
| `Price` | Pricing configurations (default) |
| `PaymentIntent` | Payment intent objects |

### Date Range Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `start_date` | 90 days ago | Earliest date to fetch data from |
| `end_date` | Now | Latest date to fetch data to |

```yaml
stripe:
  stripe_secret_key_env: STRIPE_API_KEY
  endpoints:
    - Charge
    - Customer
    - Invoice
  start_date: "2023-06-01"   # Load from June 2023
  end_date: "2024-12-31"     # Up to end of 2024
```

!!! tip "Omit dates for defaults"
    If you omit `start_date`, Dango fetches the last 90 days. Omit `end_date` to fetch up to the current time.

---

## Tables Loaded

Data loads into the `raw_{source_name}` schema. Endpoint names are normalized to lowercase:

| Endpoint | Table Name |
|----------|-----------|
| Charge | `raw_stripe.charge` |
| Customer | `raw_stripe.customer` |
| Subscription | `raw_stripe.subscription` |
| Invoice | `raw_stripe.invoice` |
| Product | `raw_stripe.product` |
| Price | `raw_stripe.price` |
| PaymentIntent | `raw_stripe.payment_intent` |

Query example:

```sql
SELECT id, amount, currency, status, created
FROM raw_stripe.charge
ORDER BY created DESC
LIMIT 10;
```

---

## Sync Behavior

- **Incremental**: No — every sync is a full refresh within the date range.
- **Write disposition**: `replace` — the full dataset within the date range is reloaded on each sync.
- **First sync**: Loads all data within the date range. Large Stripe accounts (100k+ charges) may take 10-20 minutes.

!!! note "Stripe API rate limits"
    Stripe allows 100 requests/second in live mode, 25/second in test mode. Dango handles rate limiting automatically via dlt's built-in retry logic.

---

## Common Issues

### "Invalid API Key provided"

- Verify the key in `.env` matches your Stripe dashboard
- Check you're using a **secret key** (starts with `sk_`), not a publishable key (`pk_`)
- Ensure there are no extra spaces or quotes around the key

### No Data Returned

- Check the `start_date` — if set too recently, there may be no matching records
- Verify the Stripe account has data for the selected endpoints
- Test mode accounts may have limited or no data

### "Permission denied" Errors

Restricted API keys may lack access to certain endpoints. Use an unrestricted key or update the key's permissions in the Stripe dashboard under **Developers** > **API keys** > key settings.

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
- **[Source Catalog](source-catalog.md)** - All available data sources
- **[Transformations](../transformations/index.md)** - Transform Stripe data with dbt
- [Stripe API Documentation](https://docs.stripe.com/api)
