# Welcome to Dango Documentation

**Open source data platform built with production-grade tools**

Works on your laptop today. Designed to scale to production tomorrow.

---

## What is Dango?

Dango deploys a complete data stack (dlt + dbt + DuckDB + Metabase) to your laptop with one command.

<div class="feature-grid" markdown>

<div class="feature-item" markdown>
### Fast Setup
Get a complete data platform running on your laptop in minutes, not weeks.
</div>

<div class="feature-item" markdown>
### Production-Grade Tools
Built with dlt, dbt, DuckDB, and Metabase - the same tools used in production.
</div>

<div class="feature-item" markdown>
### Simple to Start
Wizard-driven setup for common use cases. No complex configuration required.
</div>

<div class="feature-item" markdown>
### Fully Customizable
Direct access to dlt and dbt. Build custom sources, write SQL transformations.
</div>

</div>

---

## Quick Start

```bash
# Install Dango
curl -sSL https://raw.githubusercontent.com/getdango/dango/main/install.sh | bash

# Add a data source
dango source add

# Sync your data
dango sync

# Start the platform
dango start
```

**What you get:**

- **Web UI** at `http://localhost:8800` - Monitor your data pipeline
- **dlt** for data ingestion (29+ verified sources)
- **dbt** for SQL transformations and modeling
- **DuckDB** as your analytics database
- **Metabase** for dashboards and SQL queries

---

## Getting Started

<div class="grid cards" markdown>

- :material-clock-fast:{ .lg .middle } **[What is Dango?](getting-started/what-is-dango.md)**

    ---

    Learn about Dango's architecture, features, and how it works

- :material-download:{ .lg .middle } **[Installation](getting-started/installation.md)**

    ---

    Install Dango on macOS, Linux, or Windows

- :material-rocket-launch:{ .lg .middle } **[Quick Start](getting-started/quick-start.md)**

    ---

    Get your first data pipeline running in minutes

- :material-help-circle:{ .lg .middle } **[Troubleshooting](getting-started/troubleshooting.md)**

    ---

    Common issues and solutions

</div>

---

## Who is Dango For?

- Solo data professionals
- Fractional consultants
- SMEs needing analytics fast
- Anyone who wants a "real" data stack without the complexity

---

## Why Dango?

**Most tools force you to choose:**

- ❌ Simple setup (limited features) OR Enterprise platforms (expensive, complex)
- ❌ No-code (inflexible) OR Full-code (steep learning curve)
- ❌ Fast setup (toy project) OR Production-grade (weeks of work)

**Dango gives you both:**

- ✅ Starts on your laptop, designed to scale to your infrastructure
- ✅ Wizard-driven AND fully customizable
- ✅ Fast setup AND best practices built-in

---

## Current Version: v0.0.5

Dango is in active MVP development. See the [changelog](https://github.com/getdango/dango/blob/main/CHANGELOG.md) for the latest updates.

---

## Need Help?

- **GitHub Issues**: [github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)
- **GitHub Repository**: [github.com/getdango/dango](https://github.com/getdango/dango)
- **PyPI Package**: [pypi.org/project/getdango](https://pypi.org/project/getdango/)
