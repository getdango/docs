# Testing

Comprehensive data quality testing with dbt.

---

## Overview

Data testing ensures your transformations produce accurate, reliable results. Dango uses dbt's testing framework to validate:

- **Schema constraints** - Uniqueness, nullability, accepted values
- **Referential integrity** - Foreign key relationships
- **Business logic** - Custom validations
- **Data freshness** - Timeliness checks
- **Cross-model consistency** - Data reconciliation

**Key Benefits**:

- Catch errors before they reach dashboards
- Document data quality assumptions
- Build confidence in analytics
- Enable continuous delivery of data

---

## Quick Start

### Add Basic Tests

```yaml
# dbt/models/marts/schema.yml
version: 2

models:
  - name: customer_metrics
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null

      - name: email
        tests:
          - not_null

      - name: lifetime_value
        tests:
          - not_null
```

### Run Tests

```bash
# Run all tests
dbt test --profiles-dir dbt --project-dir dbt

# Run tests for specific model
dbt test --profiles-dir dbt --project-dir dbt --select customer_metrics

# Run tests for all marts
dbt test --profiles-dir dbt --project-dir dbt --select marts.*
```

### Test Output

```
Running with dbt=1.7.0
Found 12 models, 8 tests, 0 snapshots, 0 analyses, 0 macros, 0 operations

Completed successfully

Done. PASS=8 WARN=0 ERROR=0 SKIP=0 TOTAL=8
```

---

## Auto-Generated Tests

When `dango sync` generates staging models, it also creates basic tests for primary key columns:

```yaml
# Auto-generated in _stg_<source>__schema.yml
models:
  - name: stg_stripe_charges
    columns:
      - name: id
        tests:
          - unique
          - not_null
```

Dango automatically adds `unique` and `not_null` tests for columns that appear to be primary keys (columns named `id`, `uuid`, or ending in `_id`/`_key`).

---

## Test Types

### 1. Schema Tests

Defined in YAML files, applied to columns or models.

#### Built-in Tests

dbt provides four built-in tests:

```yaml
models:
  - name: customer_metrics
    columns:
      - name: customer_id
        tests:
          - unique              # No duplicate values
          - not_null            # No NULL values

      - name: status
        tests:
          - accepted_values:    # Only allowed values
              values: ['active', 'inactive', 'suspended']

      - name: subscription_id
        tests:
          - relationships:      # Foreign key constraint
              to: ref('stg_stripe_subscriptions')
              field: id
```

#### Test Descriptions

```yaml
columns:
  - name: customer_id
    description: Unique Stripe customer identifier
    tests:
      - unique:
          config:
            severity: error  # error or warn
            error_if: ">0"   # Fail if any failures
            warn_if: ">10"   # Warn if >10 failures
```

### 2. Data Tests

Custom SQL queries that test business logic.

```sql
-- dbt/tests/assert_positive_revenue.sql
-- Test fails if query returns any rows

SELECT
    customer_id,
    lifetime_value
FROM {{ ref('customer_metrics') }}
WHERE lifetime_value < 0
```

```sql
-- dbt/tests/assert_first_before_last_order.sql
SELECT
    customer_id,
    first_order_date,
    last_order_date
FROM {{ ref('customer_metrics') }}
WHERE first_order_date > last_order_date
```

### 3. dbt_utils Tests

Extended test library from dbt-labs.

First, install dbt_utils:

```yaml
# dbt/packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.0
```

```bash
dbt deps --profiles-dir dbt --project-dir dbt
```

Use in tests:

```yaml
models:
  - name: customer_metrics
    columns:
      - name: email
        tests:
          - dbt_utils.not_null_proportion:
              at_least: 0.95  # At least 95% non-null

      - name: customer_id
        tests:
          - dbt_utils.cardinality_equality:
              field: id
              to: ref('stg_stripe_customers')

    tests:
      # Model-level tests
      - dbt_utils.expression_is_true:
          expression: "lifetime_value >= 0"

      - dbt_utils.equal_rowcount:
          compare_model: ref('stg_stripe_customers')
```

### 4. Freshness Tests

Ensure data is up-to-date:

```yaml
# dbt/models/staging/_stg_stripe__sources.yml
version: 2

sources:
  - name: stripe
    schema: raw_stripe
    tables:
      - name: charges
        loaded_at_field: _dlt_extracted_at
        freshness:
          warn_after: {count: 6, period: hour}
          error_after: {count: 12, period: hour}
```

Test freshness:

```bash
dbt source freshness --profiles-dir dbt --project-dir dbt
```

---

## Test Configuration

### Severity Levels

```yaml
tests:
  - unique:
      config:
        severity: error  # Fail build

  - not_null:
      config:
        severity: warn   # Warn but continue
```

### Error Thresholds

```yaml
tests:
  - unique:
      config:
        error_if: ">0"      # Any failures = error
        warn_if: ">10"      # >10 failures = warning
```

### Store Test Results

```yaml
# dbt_project.yml
tests:
  +store_failures: true  # Store failed rows in database
```

Query failed tests:

```sql
SELECT * FROM dbt_test__audit.unique_customer_metrics_customer_id
```

---

## Common Test Patterns

### Primary Key Tests

```yaml
models:
  - name: customer_metrics
    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null
```

### Foreign Key Tests

```yaml
models:
  - name: fct_orders
    columns:
      - name: customer_id
        description: Foreign key to dim_customers
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

### Range Tests

```yaml
models:
  - name: customer_metrics
    columns:
      - name: lifetime_value
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"

      - name: discount_percentage
        tests:
          - dbt_utils.expression_is_true:
              expression: "BETWEEN 0 AND 100"
```

### Format Tests

```yaml
models:
  - name: dim_customers
    columns:
      - name: email
        tests:
          - dbt_utils.not_null_proportion:
              at_least: 0.95
          - dbt_utils.expression_is_true:
              expression: "LIKE '%@%'"  # Basic email format
```

### Date Logic Tests

```yaml
models:
  - name: customer_metrics
    tests:
      - dbt_utils.expression_is_true:
          expression: "first_order_date <= last_order_date"

      - dbt_utils.expression_is_true:
          expression: "customer_since <= first_order_date"
```

### Completeness Tests

```yaml
models:
  - name: fct_revenue
    tests:
      # All dates should be present (no gaps)
      - dbt_utils.sequential_values:
          column_name: date
          interval: 1
          datepart: day
```

---

## Advanced Testing

### Cross-Model Reconciliation

Ensure data consistency across models:

```sql
-- dbt/tests/assert_revenue_reconciliation.sql
WITH revenue_from_fact AS (
    SELECT SUM(revenue_usd) as total
    FROM {{ ref('fct_revenue') }}
),

revenue_from_staging AS (
    SELECT SUM(amount / 100.0) as total
    FROM {{ ref('stg_stripe_charges') }}
    WHERE status = 'succeeded'
)

SELECT
    f.total as fact_revenue,
    s.total as staging_revenue,
    ABS(f.total - s.total) as difference
FROM revenue_from_fact f
CROSS JOIN revenue_from_staging s
WHERE ABS(f.total - s.total) > 1.00  -- Allow $1 rounding difference
```

### Row Count Validation

```yaml
models:
  - name: dim_customers
    tests:
      # Should have same count as staging
      - dbt_utils.equal_rowcount:
          compare_model: ref('stg_stripe_customers')
```

### Duplicate Detection

```sql
-- dbt/tests/assert_no_duplicate_customers.sql
WITH duplicates AS (
    SELECT
        email,
        COUNT(*) as duplicate_count
    FROM {{ ref('dim_customers') }}
    GROUP BY email
    HAVING COUNT(*) > 1
)

SELECT * FROM duplicates
```

### Time Series Validation

```sql
-- dbt/tests/assert_no_future_dates.sql
SELECT
    customer_id,
    order_date
FROM {{ ref('fct_orders') }}
WHERE order_date > CURRENT_DATE
```

### Metric Bounds

```sql
-- dbt/tests/assert_reasonable_metrics.sql
SELECT
    customer_id,
    lifetime_value
FROM {{ ref('customer_metrics') }}
WHERE lifetime_value > 1000000  -- Flag customers over $1M
```

---

## Test Organization

### File Structure

```
dbt/
├── models/
│   ├── staging/
│   │   └── _stg_stripe__schema.yml    # Staging tests
│   ├── intermediate/
│   │   └── schema.yml                 # Intermediate tests
│   └── marts/
│       ├── finance/
│       │   └── schema.yml             # Finance mart tests
│       └── marketing/
│           └── schema.yml             # Marketing mart tests
└── tests/
    ├── assert_revenue_reconciliation.sql
    ├── assert_no_duplicates.sql
    └── assert_positive_values.sql
```

### Schema YAML Organization

```yaml
# dbt/models/marts/finance/schema.yml
version: 2

models:
  - name: fct_revenue
    description: Daily revenue metrics
    tests:
      # Model-level tests
      - dbt_utils.expression_is_true:
          expression: "revenue_usd >= 0"

    columns:
      - name: date
        description: Revenue date
        tests:
          - unique
          - not_null

      - name: revenue_usd
        description: Total revenue in USD
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"

  - name: fct_mrr
    description: Monthly recurring revenue
    # Additional tests...
```

---

## Testing Workflows

### Development Workflow

```bash
# 1. Build model
dbt run --select customer_metrics

# 2. Test model
dbt test --select customer_metrics

# 3. Fix issues and repeat
# Edit SQL -> dbt run -> dbt test
```

### CI/CD Workflow

```bash
#!/bin/bash
# Script: test_and_deploy.sh

# Run all models
dango run

# Run all tests
dbt test --profiles-dir dbt --project-dir dbt

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
    # Deploy to production
else
    echo "Tests failed!"
    exit 1
fi
```

### Selective Testing

```bash
# Test specific model and dependencies
dbt test --profiles-dir dbt --project-dir dbt --select customer_metrics+

# Test all marts
dbt test --profiles-dir dbt --project-dir dbt --select marts.*

# Test modified models only
dbt test --profiles-dir dbt --project-dir dbt --select state:modified+

# Test by tag
dbt test --profiles-dir dbt --project-dir dbt --select tag:daily
```

---

## Test Results and Debugging

### View Test Results

```bash
# Verbose output
dbt test --profiles-dir dbt --project-dir dbt --debug

# Store failures
dbt test --profiles-dir dbt --project-dir dbt --store-failures

# View failures in database
duckdb data/warehouse.duckdb "SELECT * FROM dbt_test__audit.unique_customer_metrics_customer_id"
```

### Investigate Failures

```sql
-- If unique test fails on customer_id
SELECT
    customer_id,
    COUNT(*) as occurrence_count
FROM {{ ref('customer_metrics') }}
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY occurrence_count DESC
```

### Test with Limits (Development)

```yaml
tests:
  - unique:
      config:
        limit: 100  # Only check first 100 rows
```

---

## Best Practices

### 1. Test Primary Keys

**Always** test primary keys:

```yaml
columns:
  - name: customer_id
    tests:
      - unique
      - not_null
```

### 2. Test Foreign Keys

Verify referential integrity:

```yaml
columns:
  - name: customer_id
    tests:
      - relationships:
          to: ref('dim_customers')
          field: customer_id
```

### 3. Test Business Logic

Document and test assumptions:

```yaml
models:
  - name: customer_metrics
    tests:
      # Business rule: customers can't have negative LTV
      - dbt_utils.expression_is_true:
          expression: "lifetime_value >= 0"
          config:
            severity: error
```

### 4. Test Critical Metrics

Add reconciliation tests for important numbers:

```sql
-- dbt/tests/assert_total_revenue_matches.sql
-- Ensure fct_revenue matches source data
...
```

### 5. Use Tags for Organization

```yaml
models:
  - name: fct_revenue
    tags: ['finance', 'daily', 'critical']
    tests: ...
```

```bash
# Test critical models
dbt test --select tag:critical
```

### 6. Document Test Rationale

```yaml
tests:
  - dbt_utils.expression_is_true:
      expression: "gross_margin <= 1.0"
      config:
        severity: error
      # Why: Gross margin can never exceed 100%
```

### 7. Set Appropriate Severity

```yaml
tests:
  - unique:
      config:
        severity: error    # Critical - must pass

  - dbt_utils.not_null_proportion:
      at_least: 0.95
      config:
        severity: warn     # Important but not critical
```

---

## Performance Optimization

### Limit Test Scope

```yaml
tests:
  - unique:
      config:
        where: "created_at >= CURRENT_DATE - INTERVAL 30 DAY"
```

### Sample Large Tables

```yaml
tests:
  - unique:
      config:
        limit: 10000  # Test first 10K rows only
```

### Use Incremental Testing

```bash
# Only test changed models
dbt test --select state:modified+
```

---

## Example: Complete Testing Suite

### Schema Tests

```yaml
# dbt/models/marts/finance/schema.yml
version: 2

models:
  - name: fct_revenue
    description: Daily revenue aggregated from Stripe charges

    # Model-level tests
    tests:
      - dbt_utils.expression_is_true:
          expression: "revenue_usd >= 0"
          config:
            severity: error

      - dbt_utils.expression_is_true:
          expression: "transaction_count >= 0"
          config:
            severity: error

    columns:
      - name: date
        description: Revenue date (UTC)
        tests:
          - unique
          - not_null
          - dbt_utils.sequential_values:
              interval: 1
              datepart: day

      - name: revenue_usd
        description: Total revenue in USD
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"

      - name: transaction_count
        description: Number of successful transactions
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "> 0"

      - name: unique_customers
        description: Count of distinct customers
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "<= transaction_count"
```

### Data Tests

```sql
-- dbt/tests/finance/assert_revenue_reconciliation.sql
-- Ensures fct_revenue matches raw charges data

WITH revenue_from_fact AS (
    SELECT SUM(revenue_usd) as total
    FROM {{ ref('fct_revenue') }}
),

revenue_from_staging AS (
    SELECT SUM(amount / 100.0) as total
    FROM {{ ref('stg_stripe_charges') }}
    WHERE status = 'succeeded'
)

SELECT
    f.total as fact_total,
    s.total as staging_total,
    ABS(f.total - s.total) as difference
FROM revenue_from_fact f
CROSS JOIN revenue_from_staging s
WHERE ABS(f.total - s.total) > 1.00
```

```sql
-- dbt/tests/finance/assert_no_future_revenue.sql
-- Revenue dates should not be in the future

SELECT
    date,
    revenue_usd
FROM {{ ref('fct_revenue') }}
WHERE date > CURRENT_DATE
```

---

## Troubleshooting

### Test Failures

**Problem**: Tests fail unexpectedly

**Solutions**:

1. **Check test logic**:
   ```bash
   dbt test --select test_name --debug
   ```

2. **Examine failed rows**:
   ```bash
   dbt test --store-failures
   ```
   ```sql
   SELECT * FROM dbt_test__audit.failing_test_name
   ```

3. **Review recent data changes**:
   ```sql
   SELECT * FROM raw_stripe.charges
   WHERE _dlt_extracted_at >= CURRENT_DATE - INTERVAL 1 DAY
   ```

### Performance Issues

**Problem**: Tests take too long

**Solutions**:

1. **Add WHERE clauses**:
   ```yaml
   tests:
     - unique:
         config:
           where: "created_at >= CURRENT_DATE - INTERVAL 7 DAY"
   ```

2. **Use sampling**:
   ```yaml
   tests:
     - unique:
         config:
           limit: 10000
   ```

3. **Run tests selectively**:
   ```bash
   dbt test --select marts.* --exclude tag:slow
   ```

### False Positives

**Problem**: Tests fail on edge cases

**Solutions**:

1. **Adjust thresholds**:
   ```yaml
   tests:
     - dbt_utils.not_null_proportion:
         at_least: 0.95  # Allow 5% nulls
   ```

2. **Use warnings instead of errors**:
   ```yaml
   tests:
     - unique:
         config:
           severity: warn
   ```

---

## Integration with Dango

### Run Tests After Sync

```bash
# Load data and run transformations
dango sync && dango run

# Run tests
dbt test --profiles-dir dbt --project-dir dbt

# Check results
if [ $? -eq 0 ]; then
    echo "Data quality checks passed"
else
    echo "Data quality issues detected"
fi
```

### Complete Pipeline Script

```bash
#!/bin/bash
# Run full pipeline with tests

# Sync data (auto-generates staging templates)
dango sync --source stripe_payments

# Run transformations
dango run

# Run tests
dbt test --profiles-dir dbt --project-dir dbt

echo "Pipeline complete"
```

---

## Next Steps

- **[dbt Basics](dbt-basics.md)** - Learn dbt fundamentals
- **[Custom Models](custom-models.md)** - Build testable marts
- **[Staging Models](staging-models.md)** - Understand the foundation
- **[dbt Testing Documentation](https://docs.getdbt.com/docs/build/tests)** - Official dbt testing guide
