# Workflows

Best practices and advanced workflows for working with Dango.

---

## Overview

While Dango provides a unified CLI for common operations, understanding the underlying tools gives you more flexibility. This section covers workflows for direct tool usage and operational best practices.

---

## Workflow Guides

<div class="grid cards" markdown>

-   :material-laptop: **Local Development**

    ---

    Project organization, directory structure, and development workflows.

    [:octicons-arrow-right-24: Local Development](local-development.md)

-   :material-database-import: **dlt Workflows**

    ---

    Using dlt directly for advanced data loading scenarios.

    [:octicons-arrow-right-24: dlt Workflows](dlt-workflows.md)

-   :material-transform: **dbt Workflows**

    ---

    Running dbt commands directly for debugging and development.

    [:octicons-arrow-right-24: dbt Workflows](dbt-workflows.md)

-   :material-chart-bar: **Metabase Workflows**

    ---

    Dashboard management, exports, and API usage.

    [:octicons-arrow-right-24: Metabase Workflows](metabase-workflows.md)

-   :material-backup-restore: **Backup & Restore**

    ---

    Complete backup strategies for all Dango components.

    [:octicons-arrow-right-24: Backup & Restore](backup-restore.md)

-   :material-git: **Git Best Practices**

    ---

    Version control strategies for data projects.

    [:octicons-arrow-right-24: Git Workflows](git-workflows.md)

-   :material-speedometer: **Performance**

    ---

    Optimization strategies for large datasets.

    [:octicons-arrow-right-24: Performance](performance.md)

-   :material-bug: **Troubleshooting**

    ---

    Common issues and their solutions.

    [:octicons-arrow-right-24: Troubleshooting](troubleshooting.md)

</div>

---

## When to Use Direct Tool Access

| Scenario | Use Dango CLI | Use Tool Directly |
|----------|---------------|-------------------|
| Standard sync | `dango sync` | - |
| Run all models | `dango run` | - |
| Debug specific model | - | `dbt run --select model` |
| View dlt state | - | `dlt pipeline info` |
| Export dashboards | `dango metabase save` | Metabase API |
| Custom dlt source | - | dlt Python API |

!!! tip "Best Practice"
    Start with Dango CLI commands for simplicity. Only use direct tool access when you need features not exposed through Dango.

---

## Quick Links

| Topic | Description |
|-------|-------------|
| [Local Development](local-development.md) | Project structure and workflows |
| [dlt Workflows](dlt-workflows.md) | Advanced data loading |
| [dbt Workflows](dbt-workflows.md) | Transformation debugging |
| [Backup & Restore](backup-restore.md) | Data protection |
| [Git Workflows](git-workflows.md) | Version control |
| [Troubleshooting](troubleshooting.md) | Problem solving |
