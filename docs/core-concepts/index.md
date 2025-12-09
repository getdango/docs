# Core Concepts

Understanding Dango's architecture, data flow, and key components.

---

## Overview

Dango integrates four production-grade tools into a single platform:

- **dlt** - Data ingestion from 30+ verified sources
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

- :material-layer-group:{ .lg .middle } **[Data Layers](data-layers.md)**

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
External APIs/Files → dlt → DuckDB (raw) → dbt (staging/marts) → Metabase
```

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

**Works on your laptop today. Designed to scale to production tomorrow.**

Dango is built chronologically:

1. **Local MVP** (current) - Everything runs on your laptop
2. **Cloud Production** (future) - Deploy to cloud infrastructure

The architecture supports both environments without major changes.

---

## Next Steps

Start with **[Architecture](architecture.md)** to understand how Dango's components work together, then explore the other pages to dive deeper into specific aspects.
