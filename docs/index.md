# Dango Documentation

Dango is an open-source data platform that integrates **dlt + dbt + DuckDB + Metabase** into a single, pre-configured stack.

Works on your laptop today. Designed to scale to production tomorrow.

---

## Quick Start

```bash
# Install Dango
curl -sSL https://getdango.dev/install.sh | bash

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

## Need Help?

- **GitHub Issues**: [github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)
- **GitHub Repository**: [github.com/getdango/dango](https://github.com/getdango/dango)
- **PyPI Package**: [pypi.org/project/getdango](https://pypi.org/project/getdango/)
