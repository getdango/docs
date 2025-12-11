# What is Dango?

Dango is an open-source data platform that integrates production-grade tools (dlt, dbt, DuckDB, Metabase) into a single, cohesive platform.

**Works on your laptop today. Designed to scale to production tomorrow.**

## The Problem

Building a data platform typically requires:

- Weeks of setup and configuration
- Deep knowledge of multiple tools
- Complex infrastructure decisions
- Choosing between simple (limited) or complex (powerful) tools

**Result:** Data teams spend more time on infrastructure than analysis.

## The Solution

Dango gives you a complete data stack with one command:

```bash
dango init
```

You get:

- **dlt** for data ingestion (29+ verified sources)
- **dbt** for SQL transformations
- **DuckDB** as your analytics database
- **Metabase** for dashboards and SQL queries
- **Web UI** for monitoring and management

## Architecture

Dango uses a layered data architecture:

```mermaid
graph LR
    A[Data Sources] --> B[dlt]
    B --> C[Raw Layer]
    C --> D[dbt]
    D --> E[Staging]
    E --> F[Intermediate]
    F --> G[Marts]
    G --> H[Metabase]
```

### Data Layers

1. **Raw** - Immutable source of truth with metadata
2. **Staging** - Clean, deduplicated data
3. **Intermediate** - Reusable business logic
4. **Marts** - Final business metrics

### Tech Stack

| Component | Purpose | Why This Tool? |
|-----------|---------|----------------|
| **DuckDB** | Analytics database | Embedded, fast, no server needed |
| **dlt** | Data ingestion | 29+ sources, schema evolution |
| **dbt** | Transformations | SQL-based, version controlled |
| **Metabase** | BI dashboards | Auto-configured, easy to use |
| **Docker** | Service orchestration | Consistent environments |
| **FastAPI** | Web UI backend | Fast, modern Python |

## Core Features

### Data Ingestion

- 29+ verified dlt sources (Stripe, Google Sheets, GA4, Facebook Ads, etc.)
- CSV upload and auto-sync
- Custom source development
- OAuth authentication for cloud sources

### Transformations

- dbt auto-generation for staging models
- Full dbt project access
- SQL-based transformations
- Incremental model support

### Monitoring

- Web UI with live pipeline status
- File watcher with auto-triggers
- Token expiry warnings
- Validation and health checks

### Dashboards

- Metabase auto-configured with DuckDB
- Pre-built dashboard templates
- SQL query interface
- Dashboard backup and restore

## Current Status

Dango is currently in **early development (MVP)**. Core functionality is stable and usable.

### What Works Now

- ✅ Full CLI with 10+ commands
- ✅ CSV, Stripe, Google Sheets, GA4, Facebook Ads sources
- ✅ dbt auto-generation for staging models
- ✅ Web UI with live monitoring
- ✅ Metabase dashboards
- ✅ File watcher with auto-triggers
- ✅ Custom sources via `dlt_native` type

### Coming Soon

- 🚧 Additional data sources (Google Ads), demo project, expanded documentation
- 🔮 Cloud deployment guides, advanced scheduling, team collaboration

## Design Philosophy

Dango is built on two core principles:

### Opinionated but Modular

Best practices are built-in so you can focus on insights, not infrastructure. As the open-source data ecosystem evolves, components can be swapped for better alternatives without rebuilding your entire stack.

### Democratize Analytics Infrastructure

Enterprise-grade data tooling shouldn't require a dedicated platform team. Dango brings production-quality patterns to teams of any size—the same tools used by sophisticated data teams, packaged for accessibility.

## Target Users

- **Solo data professionals** - Complete stack, zero complexity
- **Small data teams** - Full analytics stack that grows with you
- **Fractional consultants** - Fast client onboarding
- **SMEs** - Analytics infrastructure without the overhead
- **Learners** - Production tools without production costs

## Why Dango vs. Alternatives?

### vs. Cloud Platforms (Snowflake, BigQuery)

| Aspect | Dango | Cloud Platforms |
|--------|-------|-----------------|
| **Setup** | One command, ready in minutes | Assemble and integrate multiple tools |
| **Cost** | Free and open source | Pay for compute and storage |
| **Stack** | Integrated (dlt + dbt + DuckDB + Metabase) | Build your own toolchain |
| **Iteration** | Instant local feedback loop | Round-trip to cloud for each change |
| **Scale** | Local compute limits | Scales to petabytes |

### vs. Managed ETL Tools (Fivetran, Airbyte Cloud)

| Aspect | Dango | Managed ETL Tools |
|--------|-------|-------------------|
| **Customization** | Fully customizable | Limited to supported connectors |
| **Configuration** | Version controlled (YAML, SQL) | UI-based, harder to track changes |
| **Cost** | Free and open source | Subscription or usage-based pricing |
| **Integration** | Complete stack included | ETL only—BI, transforms, warehouse separate |
| **Complexity** | Requires some code for advanced use | Point-and-click for supported sources |

!!! note
    Some tools like Airbyte have open-source versions, but require separate setup for orchestration, transformations, and BI.

### vs. DIY Stack

| Dango | DIY Stack |
|-------|-----------|
| ✅ Integrated from day one | ❌ Weeks of integration work |
| ✅ Best practices built-in | ⚠️ Easy to make mistakes |
| ✅ Maintained by community | ❌ You maintain everything |
| ⚠️ Opinionated structure | ✅ Complete flexibility |

## What Dango is NOT

- **Not a SaaS platform** - It's a CLI tool that runs locally
- **Not cloud-only** - MVP is local, cloud support coming later
- **Not a BI tool** - It integrates BI (Metabase) but focuses on data infrastructure
- **Not production-ready for enterprise** - Currently in early development (MVP)

## Next Steps

Ready to try Dango?

1. **[Install Dango](installation.md)** - Get set up in minutes
2. **[Quick Start](quick-start.md)** - Run your first pipeline
3. **[Core Concepts](../core-concepts/index.md)** - Deep dive into architecture

## Questions?

- **GitHub**: [github.com/getdango/dango](https://github.com/getdango/dango)
- **Issues**: [github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)
- **PyPI**: [pypi.org/project/getdango](https://pypi.org/project/getdango/)
