# Dango Documentation

Dango is an open-source data platform that integrates **dlt + dbt + DuckDB + Metabase** into a single, pre-configured stack.

Works on your laptop today. Deploy to the cloud when you're ready.

---

## Quick Start

```bash
# Install Dango
curl -sSL https://getdango.dev/install.sh | bash

# Initialize your project
dango init

# Add a data source
dango source add

# Sync your data
dango sync

# Start the platform
dango start
```

**What you get:**

- **[Web UI](web-ui/index.md)** at `http://localhost:8800` — monitor your data pipeline
- **[35 data sources](data-sources/source-catalog.md)** via dlt (25 in the setup wizard)
- **[dbt](transformations/index.md)** for SQL transformations and modeling
- **[DuckDB](core-concepts/duckdb.md)** as your analytics database
- **[Metabase](dashboards/index.md)** for dashboards and SQL queries
- **[Authentication](security/authentication.md)** with user roles and 2FA
- **[Cloud deployment](deployment/index.md)** to DigitalOcean or your own server
- **[Scheduled syncs](scheduling-monitoring/scheduled-syncs.md)** with webhook notifications
- **[Data governance](scheduling-monitoring/index.md)** — schema drift detection, PII scanning, data catalog
- **[Marimo notebooks](notebooks/index.md)** for ad-hoc analysis

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

## Explore

<div class="grid cards" markdown>

- :material-database-import:{ .lg .middle } **[Data Sources](data-sources/index.md)**

    ---

    Connect to 35 sources — APIs, databases, files, and more

- :material-cog:{ .lg .middle } **[Transformations](transformations/index.md)**

    ---

    Build dbt models to clean and reshape your data

- :material-chart-bar:{ .lg .middle } **[Dashboards](dashboards/index.md)**

    ---

    Create Metabase dashboards and SQL queries

- :material-cloud-upload:{ .lg .middle } **[Deployment](deployment/index.md)**

    ---

    Deploy to DigitalOcean or your own server

- :material-shield-lock:{ .lg .middle } **[Security](security/index.md)**

    ---

    Authentication, user roles, 2FA, and credentials

- :material-notebook:{ .lg .middle } **[Notebooks](notebooks/index.md)**

    ---

    Marimo notebooks for ad-hoc analysis

- :material-monitor-dashboard:{ .lg .middle } **[Web UI](web-ui/index.md)**

    ---

    Monitor syncs, health, and data quality

- :material-calendar-clock:{ .lg .middle } **[Scheduling](scheduling-monitoring/index.md)**

    ---

    Automated syncs, webhooks, and monitoring

</div>

---

## Need Help?

- **FAQ**: [Frequently Asked Questions](faq.md)
- **GitHub Issues**: [github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)
- **GitHub Repository**: [github.com/getdango/dango](https://github.com/getdango/dango)
- **PyPI Package**: [pypi.org/project/getdango](https://pypi.org/project/getdango/)
