# Frequently Asked Questions

Common questions about Dango.

---

## General

### What is Dango?

Dango is an open-source data platform that helps you build analytics pipelines locally. It combines:

- **dlt** for data ingestion
- **DuckDB** for storage
- **dbt** for transformations
- **Metabase** for visualization

All running on your laptop with a unified CLI.

### Who is Dango for?

Dango is designed for:

- Solo data practitioners and consultants
- SMBs without dedicated data teams
- Developers who want production-grade tools without the complexity
- Anyone learning modern data stack concepts

### Is Dango free?

Yes. Dango is open source under the Apache 2.0 license. You can use it for personal or commercial projects at no cost.

### What's the difference between Dango and [other tool]?

| Tool | Comparison |
|------|------------|
| **Airbyte** | Airbyte focuses on connectors. Dango is a complete local pipeline (ingest → transform → visualize) |
| **dbt Cloud** | dbt Cloud is transformations only. Dango includes ingestion and visualization |
| **Meltano** | Similar scope. Dango prioritizes simplicity and local-first experience |
| **Fivetran** | Fivetran is SaaS/paid. Dango is free and runs locally |

---

## Installation

### What are the system requirements?

- **Python**: 3.9 or higher
- **Docker**: For Metabase (optional)
- **Memory**: 4GB+ recommended
- **Disk**: Varies by data volume

### Does Dango work on Windows?

Yes, Dango works on Windows, macOS, and Linux. Some features may require WSL2 on Windows for best compatibility.

### Why do I need Docker?

Docker runs Metabase for dashboards. If you don't need visualization, you can run Dango without Docker:

```bash
dango start --no-metabase
```

### How do I upgrade Dango?

```bash
pip install --upgrade getdango
```

---

## Data Sources

### How many data sources does Dango support?

Dango has 8 wizard-supported sources with guided setup:

- CSV, Stripe, Google Sheets, GA4, Facebook Ads, Google Ads, REST API, dlt Native

Plus 25+ additional sources via dlt's verified sources.

### Can I add custom data sources?

Yes. See [Custom Sources](data-sources/custom-sources.md) for:

1. REST API source (for simple APIs)
2. Custom dlt source (for complex APIs)

### How do I sync data from [specific source]?

Check [Data Sources](data-sources/index.md) for supported sources. For sources not listed:

1. Use the REST API source type
2. Build a custom dlt source
3. Request support via GitHub

### Why isn't my data syncing?

Common causes:

1. **Invalid credentials** - Re-authenticate or check API key
2. **Rate limiting** - Wait and retry
3. **Network issues** - Check connectivity
4. **Configuration error** - Run `dango validate`

See [Troubleshooting](workflows/troubleshooting.md) for detailed solutions.

---

## Transformations

### Do I need to know dbt?

For basic usage, no. Dango auto-generates staging models. For custom transformations, basic dbt/SQL knowledge helps.

### Where are my dbt models?

In the `dbt/models/` directory:

```
dbt/models/
├── staging/     # Auto-generated
├── intermediate/  # Your business logic
└── marts/       # Final tables
```

### How do I write custom transformations?

Create SQL files in `dbt/models/marts/`:

```sql
-- dbt/models/marts/my_model.sql
SELECT * FROM {{ ref('stg_my_source') }}
```

Then run: `dango run`

See [Custom Models](transformations/custom-models.md) for details.

### Why are my models failing?

Run with debug output:

```bash
cd dbt && dbt run --select my_model --debug
```

Common issues:
- Missing source data (run `dango sync` first)
- SQL syntax errors
- Incorrect refs

---

## Dashboards

### How do I access Metabase?

```bash
# Start services
dango start

# Open Metabase
open http://localhost:3000
```

Default credentials:
- Email: `admin@dango.local`
- Password: `dango123!`

### My tables don't show in Metabase

Sync the database schema:

```bash
dango metabase refresh
```

Or manually: Admin → Databases → Sync database schema

### Can I export my dashboards?

Yes:

```bash
dango metabase save
# Creates metabase_export.json

# Import on another machine
dango metabase load --file metabase_export.json
```

### Why is Metabase slow?

For large datasets:

1. Materialize models as tables (not views)
2. Add filters to reduce query scope
3. Consider [performance optimization](workflows/performance.md)

---

## Security

### Where are my credentials stored?

- **OAuth tokens**: `.dlt/secrets.toml` (optionally encrypted)
- **API keys**: `.dlt/secrets.toml` (file)

Always add `.dlt/secrets.toml` to `.gitignore`.

### Is my data secure?

Yes, data stays local:

- DuckDB runs on your machine
- No data sent to external services
- You control all credentials

### What if I accidentally commit secrets?

1. **Immediately rotate** the exposed credential
2. Remove from git history if possible
3. Treat the credential as compromised

See [Security Best Practices](security/best-practices.md).

---

## Performance

### How much data can Dango handle?

DuckDB handles gigabytes efficiently on a laptop:

| Data Size | Performance |
|-----------|-------------|
| < 100 MB | Instant |
| 100 MB - 1 GB | Fast |
| 1-10 GB | Good with optimization |
| > 10 GB | Consider partitioning |

### How do I speed up syncs?

1. Use incremental syncs (default for most sources)
2. Limit date ranges
3. Select only needed endpoints

See [Performance](workflows/performance.md).

### How do I optimize queries?

1. Materialize frequently-queried models as tables
2. Use incremental models for large fact tables
3. Check query plans with `EXPLAIN ANALYZE`

---

## Common Errors

### "Source not found"

The source name doesn't exist in `sources.yml`:

```bash
# List sources
dango source list

# Check config
cat .dango/sources.yml
```

### "Invalid credentials"

Re-authenticate or check your API key:

```bash
# OAuth sources
dango auth [provider]

# API key sources
cat .dlt/secrets.toml
```

### "Database is locked"

Another process is using DuckDB:

```bash
dango stop
# Wait a moment
dango start
```

### "Port already in use"

Another service is using the port:

```bash
# Check what's using port 3000
lsof -i :3000

# Kill if needed, or change Dango's port
```

---

## Getting Help

### Where can I report bugs?

[GitHub Issues](https://github.com/getdango/dango/issues)

### Where can I ask questions?

[GitHub Discussions](https://github.com/getdango/dango/discussions)

### How can I contribute?

See [Contributing Guide](https://github.com/getdango/docs/blob/main/CONTRIBUTING.md)

---

## Still Have Questions?

If your question isn't answered here:

1. Check the relevant documentation section
2. Search [GitHub Issues](https://github.com/getdango/dango/issues)
3. Ask in [GitHub Discussions](https://github.com/getdango/dango/discussions)
4. Open a new issue if you've found a bug
