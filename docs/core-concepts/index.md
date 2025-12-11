# Core Concepts

Understanding Dango's architecture, data flow, and key components.

---

## Overview

Dango integrates four production-grade tools into a single platform:

- **dlt** - Data ingestion from 30+ sources (with access to 60+ via dlt_native)
- **dbt** - SQL transformations and data modeling
- **DuckDB** - Embedded analytics database
- **Metabase** - Business intelligence and dashboards

This section explains how these components work together to create a complete data platform.

---

## What You'll Learn

<div class="grid cards" markdown>

- :material-sitemap:{ .lg .middle } **[Architecture](architecture.md)**

    ---

    How Dango's components interact and data flows through the platform

- :material-layers:{ .lg .middle } **[Data Layers](data-layers.md)**

    ---

    Understanding raw, staging, intermediate, and marts schemas

- :material-console:{ .lg .middle } **[CLI Overview](cli-overview.md)**

    ---

    Command categories and common workflows

- :material-folder-open:{ .lg .middle } **[Project Structure](project-structure.md)**

    ---

    Directory layout and configuration files

</div>

---

## Key Concepts at a Glance

### Data Flow

```
Sources → dlt → DuckDB (raw)
                    ↓
              dbt transforms
                    ↓
             DuckDB (staging/marts)
                    ↓
               Metabase
```

All data layers live in DuckDB. dbt reads from and writes to DuckDB, transforming raw data into analytics-ready tables.

### Three-Layer Data Architecture

1. **Raw Layer** - Immutable source data as-is
2. **Staging Layer** - Cleaned and deduplicated data
3. **Marts Layer** - Business metrics and analytics

### Unified Interface

All functionality accessible through:
- **CLI** - `dango sync`, `dango start`, etc.
- **Web UI** - Monitoring and management at `localhost:8800`
- **Direct SQL** - Query DuckDB directly or use Metabase

---

## Design Philosophy

Dango is built on two core principles:

### Opinionated but Modular

Best practices are built-in so you can focus on insights, not infrastructure. As the open-source data ecosystem evolves, components can be swapped for better alternatives without rebuilding your entire stack.

### Democratize Analytics Infrastructure

Enterprise-grade data tooling shouldn't require a dedicated platform team. Dango brings production-quality patterns to teams of any size.

---

## Next Steps

Start with **[Architecture](architecture.md)** to understand how Dango's components work together, then explore the other pages to dive deeper into specific aspects.
