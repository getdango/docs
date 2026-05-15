# Configuring Monitors

Define what to measure, how to compare it, and when to alert — all in a single YAML file.

---

!!! note "Prerequisites"
    - At least one data source synced (monitors need data to query)
    - DuckDB warehouse file exists (`data/warehouse.duckdb`)

## Quick Start

1. **Sync a source** — Dango auto-generates monitor templates on first sync:

    ```bash
    dango sync stripe
    ```

2. **Review the generated monitors:**

    ```bash
    cat .dango/monitors.yml
    ```

3. **Run monitors to see results:**

    ```bash
    dango monitor run
    ```

## Detailed Steps

### `monitors.yml` Format

Monitor definitions live in `.dango/monitors.yml`. Dango auto-generates this file when you add and sync a source, but you can also create or edit it manually.

```yaml
# .dango/monitors.yml

enabled: true    # Global toggle — set to false to disable all monitors

monitors:
  - name: stripe_daily_revenue
    source_table: raw_stripe.charge
    value_expression: "SUM(amount) / 100.0"
    filter: "status = 'succeeded'"
    compare: week_over_week
    alert_threshold: 20.0
    drill_down:
      - currency

  - name: stripe_new_customers
    source_table: raw_stripe.customer
    value_expression: "COUNT(*)"
    compare: week_over_week
    alert_threshold: 25.0

  - name: hubspot_contacts_row_count
    source_table: raw_hubspot.contacts
    value_expression: "COUNT(*)"
    compare: week_over_week
    alert_threshold: 25.0
```

### MonitorConfig Fields

Each monitor defines a SQL-based metric with comparison rules:

**`name`** (required)
: Unique identifier for this monitor. Lowercase letters, numbers, and underscores only. Must start with a letter.

```yaml
name: stripe_daily_revenue
```

**`source_table`** (required)
: Schema-qualified table name in DuckDB. Source tables use the `raw_{source_name}` schema.

```yaml
source_table: raw_stripe.charge
```

**`value_expression`** (required)
: SQL expression that computes the metric value. This becomes the `SELECT` clause in a DuckDB query.

```yaml
value_expression: "SUM(amount) / 100.0"
```

**`filter`** (optional)
: SQL `WHERE` clause to filter rows before aggregation.

```yaml
filter: "status = 'succeeded'"
```

**`compare`** (optional, default: `week_over_week`)
: Comparison strategy. See [Monitoring Metrics](metrics.md) for details on each type.

```yaml
compare: rolling_7day_avg    # week_over_week | rolling_7day_avg | rolling_30day_avg | prior_period
```

**`alert_threshold`** (optional)
: Percentage change that triggers a `flagged` status and drill-down analysis. For example, `20.0` means the monitor flags when the value changes by more than 20% in either direction.

```yaml
alert_threshold: 20.0
```

**`drill_down`** (optional)
: List of column names to group by when the metric is flagged. Helps identify which segments drove the change.

```yaml
drill_down:
  - currency
  - country
```

### Auto-Generated Templates

When you add and sync a source, Dango generates monitor templates automatically:

**Stripe** (4 metrics):

| Monitor | Expression | Comparison | Threshold |
|---------|-----------|------------|-----------|
| `{name}_daily_revenue` | `SUM(amount) / 100.0` | week_over_week | 20% |
| `{name}_new_customers` | `COUNT(*)` | week_over_week | 25% |
| `{name}_refund_rate` | `COUNT(CASE WHEN refunded THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)` | rolling_7day_avg | 50% |
| `{name}_avg_order_value` | `AVG(amount) / 100.0` | rolling_7day_avg | 15% |

**Google Analytics** (discovers columns from DuckDB):

| Monitor | Expression | Comparison | Threshold |
|---------|-----------|------------|-----------|
| `{name}_daily_sessions` | `SUM({sessions_column})` | week_over_week | 20% |
| `{name}_bounce_rate` | `AVG({bounce_rate_column})` | rolling_7day_avg | 25% |
| `{name}_avg_session_duration` | `AVG({duration_column})` | rolling_7day_avg | 20% |

**All other sources** (generic — auto-discovers tables):

| Monitor | Expression | Comparison | Threshold |
|---------|-----------|------------|-----------|
| `{name}_{table}_row_count` | `COUNT(*)` | week_over_week | 25% |
| `{name}_{table}_freshness` | `MAX(_dlt_load_id)` | week_over_week | 25% |

!!! tip "Auto-generated templates are starting points"
    Edit the generated `monitors.yml` to adjust thresholds, add drill-down dimensions, or remove metrics you don't need.

### Writing Custom Metrics

You can write any SQL expression that returns a single numeric value:

**Revenue tracking:**

```yaml
- name: daily_revenue
  source_table: raw_stripe.charge
  value_expression: "SUM(amount) / 100.0"
  filter: "status = 'succeeded'"
  compare: week_over_week
  alert_threshold: 20.0
  drill_down: [currency]
```

**Row count monitoring:**

```yaml
- name: orders_count
  source_table: raw_shopify.orders
  value_expression: "COUNT(*)"
  compare: prior_period
  alert_threshold: 50.0
```

**Data freshness:**

```yaml
- name: contacts_freshness
  source_table: raw_hubspot.contacts
  value_expression: "MAX(_dlt_load_id)"
  compare: week_over_week
  alert_threshold: 25.0
```

**Ratio metric:**

```yaml
- name: refund_rate
  source_table: raw_stripe.charge
  value_expression: "COUNT(CASE WHEN refunded THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)"
  compare: rolling_7day_avg
  alert_threshold: 50.0
```

## Configuration Reference

### Field Reference

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | yes | — | Unique monitor name (lowercase, alphanumeric + underscores) |
| `source_table` | string | yes | — | Schema-qualified table (`raw_stripe.charge`) |
| `value_expression` | string | yes | — | SQL aggregation expression (`SUM(amount)`, `COUNT(*)`) |
| `filter` | string | no | `null` | SQL WHERE clause to filter rows |
| `compare` | string | no | `week_over_week` | Comparison type: `week_over_week`, `rolling_7day_avg`, `rolling_30day_avg`, `prior_period` |
| `alert_threshold` | float | no | `null` | Percentage change threshold for alerts (e.g., `20.0` = 20%) |
| `drill_down` | list | no | `[]` | Column names for drill-down analysis when flagged |

### Top-Level Config

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | bool | `true` | Global toggle — set to `false` to disable all monitors |
| `monitors` | list | `[]` | List of monitor definitions |

### Threshold Guidance

| Metric Type | Suggested Threshold | Rationale |
|-------------|-------------------|-----------|
| Revenue / financial | 15–20% | Revenue is critical; catch drops early |
| Row counts | 25–50% | Some variation is normal; flag major changes |
| Ratios (refund rate, conversion) | 30–50% | Ratios can be noisy; higher threshold reduces false alerts |
| Freshness | 25% | Catches stale data without false positives |

!!! tip "Start with higher thresholds"
    It's better to start with thresholds around 25–50% and lower them over time as you learn what's normal for your data. Too-sensitive thresholds create alert fatigue.

### Enabling/Disabling

**Disable all monitors:**

```yaml
enabled: false
monitors:
  - ...   # Monitors are preserved but won't run
```

**Remove a specific monitor:** Delete its entry from the `monitors` list, or remove the entire file to clear all monitors.

## Verification

After configuring monitors, run them manually to verify:

```bash
# Run all monitors
dango monitor run

# Run monitors for a specific source only
dango monitor run --source stripe
```

Expected output:

```
Monitoring Results
──────────────────
Monitor                  Status    Current    Baseline   Change
stripe_daily_revenue     normal    $8,450     $8,200     +3.0%
stripe_new_customers     normal    142        138        +2.9%
stripe_refund_rate       flagged   8.5%       4.2%       +102.4%
  ↳ Drill-down: currency
    USD    8.2% → 4.0%  (+105.0%)
    EUR    9.1% → 4.5%  (+102.2%)
```

You can also view results in the **Monitoring** page of the Web UI, which shows a table of all monitor results with trend charts.

## Troubleshooting

**"No data" results**

- Verify the `source_table` exists: run `dango db status` to list available tables
- Check the schema name — source tables are in `raw_{source_name}` (e.g., `raw_stripe.charge`, not `stripe.charge`)
- Make sure you've synced the source at least once

**SQL syntax errors in `value_expression`**

- The expression is injected into `SELECT {value_expression} FROM {source_table}` — it must be a valid DuckDB SQL aggregation
- Test your expression directly: `dango db query "SELECT SUM(amount) FROM raw_stripe.charge"`
- Common mistake: using MySQL/PostgreSQL syntax instead of DuckDB syntax

**Threshold too sensitive**

- Increase the `alert_threshold` value — start with 25–50% and tune down
- Consider using `rolling_7day_avg` instead of `week_over_week` to smooth out noise
- Check if your data has natural weekly seasonality that looks like anomalies

**Monitors not running after sync**

- Verify `enabled: true` in `monitors.yml`
- Check that the monitor's `source_table` matches a source that was just synced
- Monitors run as a post-sync hook — they require `dango start` (not just `dango sync`)

## Next Steps

- [Monitoring Metrics](metrics.md) — understand comparison types and trend detection
- [Webhook Notifications](webhooks.md) — get `metric_alert` notifications
- [Scheduled Syncs](scheduled-syncs.md) — monitors run after each scheduled sync
- [Configuration Files](../reference/configuration.md) — full reference for all Dango config files
