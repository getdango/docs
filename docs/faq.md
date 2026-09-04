# Frequently Asked Questions

Common questions about Dango.

---

## General

### What is Dango?

Dango is an open-source data platform that combines production-grade tools into a single, pre-configured stack:

- **[dlt](core-concepts/architecture.md)** for data ingestion (35 sources)
- **[DuckDB](core-concepts/duckdb.md)** for analytics storage
- **[dbt](transformations/index.md)** for SQL transformations
- **[Metabase](dashboards/index.md)** for dashboards and visualization

Plus built-in [authentication](security/authentication.md), [cloud deployment](deployment/index.md), [Marimo notebooks](notebooks/index.md), [scheduled syncs](scheduling-monitoring/scheduled-syncs.md), and a [web UI](web-ui/index.md) for monitoring your pipeline.

### Who is Dango for?

Dango is designed for:

- **Small teams** without dedicated data infrastructure
- Solo data practitioners and consultants
- SMBs that need production-grade analytics without the complexity
- Developers who want a complete data stack with a unified CLI
- Anyone learning modern data stack concepts

### Is Dango free?

Yes. Dango is open source under the Apache 2.0 license. You can use it for personal or commercial projects at no cost.

### What's the difference between Dango and [other tool]?

| Tool | Comparison |
|------|------------|
| **Airbyte** | Airbyte focuses on connectors. Dango is a complete pipeline (ingest + transform + visualize) with built-in auth and deployment |
| **dbt Cloud** | dbt Cloud is transformations only. Dango includes ingestion, visualization, and infrastructure |
| **Meltano** | Similar scope. Dango prioritizes simplicity, ships with a web UI, and handles cloud deployment |
| **Fivetran** | Fivetran is SaaS/paid. Dango is free and runs on your hardware |

---

## Installation

### What are the system requirements?

- **Python**: 3.10-3.12 (3.11 or 3.12 recommended)
- **Docker Desktop**: Required for Metabase and Web UI
- **Memory**: 4GB+ recommended
- **Disk**: 10GB+ free space recommended

See [Installation](getting-started/installation.md) for full details.

### Does Dango work on Windows?

Yes, Dango works on Windows, macOS, and Linux. Some features may require WSL2 on Windows for best compatibility.

### Why do I need Docker?

Docker runs Metabase for dashboards and the Web UI. You can use Dango for data syncing and dbt transformations without Docker, but dashboards and the Web UI require it.

### How do I upgrade Dango?

```bash
dango upgrade
```

Or with pip directly: `pip install --upgrade getdango`

See [Changelog](community/changelog.md) for what's new in each release.

---

## Data Sources

### How many data sources does Dango support?

Dango supports **35 data sources**, with 25 available through the interactive setup wizard (`dango source add`). Sources include Stripe, Google Sheets, GA4, Facebook Ads, HubSpot, Salesforce, GitHub, Slack, PostgreSQL, file imports (CSV, JSON, Parquet), REST API, and more.

See the [Source Catalog](data-sources/source-catalog.md) for the complete list.

### Can I add custom data sources?

Yes. See [Custom Sources](data-sources/custom-sources.md) for:

1. **REST API source** — for simple APIs with pagination
2. **Custom dlt source** — for complex APIs requiring custom logic

### How do sync modes work?

Dango supports two sync modes:

- **Full refresh** — replaces all data on each sync
- **Incremental (append/merge)** — loads only new or changed records

The sync mode depends on the source type. See [Sync Modes](data-sources/sync-modes.md) for details on which sources support incremental loading.

### How does deduplication work?

Dango uses dlt's merge strategy with primary keys to deduplicate records during incremental syncs. See [Deduplication](data-sources/deduplication.md) for configuration details.

### Can I schedule automatic syncs?

Yes. Add a schedule with the interactive wizard:

```bash
dango schedule add
```

The wizard prompts for the source, cron expression, and options. See [Scheduled Syncs](scheduling-monitoring/scheduled-syncs.md) for cron syntax and options.

### Why isn't my data syncing?

Common causes:

1. **Invalid credentials** — Re-authenticate (`dango oauth SOURCE`) or check API key
2. **Rate limiting** — Wait and retry
3. **Network issues** — Check connectivity
4. **Configuration error** — Run `dango validate`

See [Troubleshooting](workflows/troubleshooting.md) for detailed solutions.

---

## Transformations

### Do I need to know dbt?

For basic usage, no. Dango auto-generates staging models when you add a source. For custom transformations, basic dbt/SQL knowledge helps.

### Where are my dbt models?

In the `dbt/models/` directory:

```
dbt/models/
├── staging/       # Auto-generated from sources
├── intermediate/  # Your business logic
└── marts/         # Final tables for dashboards
```

### How do I write custom transformations?

Create SQL files in `dbt/models/marts/`:

```sql
-- dbt/models/marts/my_model.sql
SELECT * FROM {{ ref('stg_my_source') }}
```

Then run: `dango run`

See [Custom Models](transformations/custom-models.md) for details.

### What is `dango dev`?

`dango dev` lets you develop dbt models on a branch without affecting your production data. It creates a separate DuckDB database and dbt target for iterating on model changes.

See [Dev Workflow](transformations/dev-workflow.md) for the full workflow.

---

## Dashboards

### How do I access Metabase?

```bash
# Start services
dango start

# Open the Web UI (recommended — SSO bridge handles Metabase login)
open http://localhost:8800
```

Click **"Open Metabase"** in the Web UI sidebar. The SSO bridge logs you in automatically.

For direct access at `http://localhost:3000`, check credentials in `.dango/metabase.yml` (email and randomly generated password).

### My tables don't show in Metabase

Sync the database schema:

```bash
dango metabase refresh
```

Or manually: Admin > Databases > Sync database schema

### Can I export my dashboards?

Yes:

```bash
dango metabase save
# Exports to metabase/ directory

# Import on another machine
dango metabase load
```

See [Save & Load](dashboards/save-load.md) for details.

### Why is Metabase slow?

For large datasets:

1. Materialize models as tables (not views)
2. Add filters to reduce query scope
3. See [Performance](workflows/performance.md) for optimization tips

---

## Authentication & Security

### Is authentication required?

Yes. Authentication is enabled by default for both local and cloud deployments. During `dango init`, you set an admin password. See [Authentication](security/authentication.md).

### What user roles are available?

Dango has three roles:

| Role | Capabilities |
|------|-------------|
| **Admin** | Full access — manage users, configure sources, deploy |
| **Editor** | Run syncs, create dashboards, manage models |
| **Viewer** | View dashboards and data catalog (read-only) |

See [Users & Roles](security/users-roles.md) for the complete permissions matrix.

### Does Dango support 2FA?

Yes. Admins can enable TOTP-based two-factor authentication for any user. See [Two-Factor Auth](security/two-factor.md) for setup instructions.

### How does the Metabase SSO bridge work?

When you access Metabase through the Web UI at `http://localhost:8800`, the SSO bridge automatically creates a Metabase session using your Dango credentials. No separate Metabase login required.

See [Authentication](security/authentication.md) for details on the SSO bridge.

### Where are my credentials stored?

| Credential | Location |
|-----------|----------|
| OAuth tokens | `.dlt/secrets.toml` |
| API keys | `.dlt/secrets.toml` |
| Metabase credentials | `.dango/metabase.yml` |
| Admin password | `.dango/auth.yml` (hashed) |

Always add `.dlt/secrets.toml` to `.gitignore`. See [Credential Management](security/credentials.md).

### What if I accidentally commit secrets?

1. **Immediately rotate** the exposed credential
2. Remove from git history if possible
3. Treat the credential as compromised

See [Security Best Practices](security/best-practices.md).

---

## Cloud Deployment

### What cloud providers are supported?

Dango supports two deployment options:

- **DigitalOcean** — automated provisioning with `dango deploy` (creates droplet, configures DNS, sets up HTTPS)
- **Bring Your Own Server (BYOS)** — deploy to any Ubuntu server with SSH access

See [Deployment](deployment/index.md) for details.

### What are the server requirements for BYOS?

- Ubuntu 22.04 LTS
- 2 vCPU / 4 GB RAM minimum
- SSH access with key-based authentication
- A domain name (for automatic HTTPS via Caddy)

See [BYOS Setup](deployment/byos.md) for the full checklist.

### How much does cloud deployment cost?

Dango itself is free. Infrastructure costs depend on your provider:

- **DigitalOcean**: ~$24/month for the default s-2vcpu-4gb droplet
- **BYOS**: Whatever your server costs

### How do I push updates to my server?

```bash
dango remote push
```

This syncs your configuration, dbt models, and Docker build files. Credentials are managed separately via the web UI secrets page or `dango remote env set`. See [Remote Management](deployment/remote-management.md).

### Does Dango set up HTTPS automatically?

Yes. Cloud deployments use [Caddy](https://caddyserver.com/) as a reverse proxy, which automatically provisions and renews TLS certificates via Let's Encrypt. You need a domain name pointing to your server.

---

## Notebooks

### What notebook tool does Dango use?

Dango integrates [Marimo](https://marimo.io/), a reactive Python notebook. Launch notebooks from the Web UI or CLI:

```bash
dango notebook open my_analysis
```

See [Notebooks](notebooks/index.md) for getting started.

### How do notebooks access my data?

Notebooks connect to a read-only DuckDB snapshot (a copy of your warehouse). This prevents file locking conflicts with syncs and Metabase. See [DuckDB Snapshots](notebooks/duckdb-snapshots.md).

### Can I run notebooks while syncs are active?

Yes. Notebooks use a snapshot copy of the database, so they don't conflict with write operations. See [File Locking](notebooks/file-locking.md) for how this works.

---

## Monitoring & Governance

### What monitoring does Dango provide?

The Web UI shows:

- **Sync status** — success/failure, last run time, row counts
- **Health metrics** — disk usage, database size, process status
- **Schema drift detection** — alerts when source schemas change
- **Data catalog** — browsable table/column inventory with descriptions

See [Monitoring Metrics](scheduling-monitoring/metrics.md) and the [Monitoring Page](web-ui/monitoring-page.md).

### What is schema drift detection?

Dango detects when a source's schema changes (columns added, removed, or type changes) and alerts you. This helps catch upstream breaking changes before they affect your dashboards.

See [Schema Drift](scheduling-monitoring/schema-drift.md) for configuration.

### Does Dango scan for PII?

Yes. Dango uses Microsoft Presidio to scan columns for personally identifiable information (email addresses, phone numbers, etc.). Results appear in the data catalog.

See [PII Scanning](scheduling-monitoring/pii-scanning.md) for configuration and supported entity types.

### Can I get webhook notifications?

Yes. Add a webhook with the interactive wizard:

```bash
dango schedule webhook add
```

The wizard prompts for the webhook URL and event types (success, failure, stale data). See [Webhook Notifications](scheduling-monitoring/webhooks.md) for setup and payload format.

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
# List configured sources
dango source list

# Check config
cat .dango/sources.yml
```

### "Invalid credentials"

Re-authenticate or check your API key:

```bash
# OAuth sources — re-authenticate
dango oauth google_sheets
dango oauth facebook_ads

# API key sources — check your credentials
cat .dlt/secrets.toml
```

### "Database is locked"

DuckDB allows only one writer at a time. Another process (a sync, Metabase, or notebook) is holding a write lock:

```bash
dango stop
# Wait a moment
dango start
```

See [DuckDB & Single-Writer](core-concepts/duckdb.md) for details.

### "Sync shows queued"

Syncs queue when another sync is already running. DuckDB's single-writer constraint means syncs execute one at a time. The queued sync starts automatically when the active sync finishes (up to 5 minutes).

### "Port already in use"

Another service is using the port:

```bash
# Check what's using port 8800 (Web UI)
lsof -i :8800

# Check Metabase port
lsof -i :3000
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
