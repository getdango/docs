# Getting Started

Welcome to the Dango Getting Started guide! This section will help you install Dango, understand what it does, and get your first data pipeline running.

## Overview

Dango is an open-source data platform that integrates dlt, dbt, DuckDB, and Metabase into a single, cohesive platform. Develop locally, then deploy to the cloud when you're ready.

## What You'll Learn

<div class="grid cards" markdown>

- :material-information:{ .lg .middle } **[What is Dango?](what-is-dango.md)**

    ---

    Learn about Dango's architecture, features, and the problems it solves

- :material-download:{ .lg .middle } **[Installation](installation.md)**

    ---

    Step-by-step installation guide for macOS, Linux, and Windows

- :material-rocket-launch:{ .lg .middle } **[Quick Start](quick-start.md)**

    ---

    Get your first data pipeline running in under 10 minutes

- :material-view-dashboard:{ .lg .middle } **[Your First Dashboard](first-dashboard.md)**

    ---

    Build a Metabase dashboard from your synced data

- :material-help-circle:{ .lg .middle } **[Troubleshooting](troubleshooting.md)**

    ---

    Solutions to common installation and runtime issues

</div>

## Prerequisites

Before installing Dango, you'll need:

- **Python 3.10-3.12** (Python 3.11 or 3.12 recommended)
- **Docker Desktop** (required for Metabase and Web UI)
- **10GB free disk space** (recommended)

## Installation Quick Links

=== "macOS"

    ```bash
    curl -sSL https://getdango.dev/install.sh | bash
    ```

=== "Linux"

    ```bash
    curl -sSL https://getdango.dev/install.sh | bash
    ```

=== "Windows"

    ```powershell
    irm https://getdango.dev/install.ps1 | iex
    ```

[Full installation instructions →](installation.md){ .md-button .md-button--primary }

## What's Next?

After installation:

1. **[Quick Start](quick-start.md)** — Get your first pipeline running
2. **[Your First Dashboard](first-dashboard.md)** — Build a Metabase dashboard
3. **[Core Concepts](../core-concepts/index.md)** — Understand Dango's architecture
4. **[Data Sources](../data-sources/index.md)** — Connect to your data sources
5. **[Security](../security/index.md)** — Authentication, OAuth, credentials
6. **[Deployment](../deployment/index.md)** — Deploy to the cloud

## Need Help?

If you run into issues:

1. Check the **[Troubleshooting](troubleshooting.md)** guide
2. Search [GitHub Issues](https://github.com/getdango/dango/issues)
3. Open a new issue if you can't find a solution
