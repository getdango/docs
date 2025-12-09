# CLI

Command-line interface for managing your Dango data platform.

---

## Overview

The Dango CLI provides powerful command-line tools for project management, data syncing, and transformation workflows. Automate your data pipelines with scriptable commands and integrate seamlessly into CI/CD systems.

**Key Commands**:

- `dango init` - Initialize new projects
- `dango sync` - Load data from sources
- `dango generate` - Auto-generate staging models
- `dango run` - Execute dbt transformations
- `dango start/stop` - Manage platform services
- `dango validate` - Check configuration health

---

## Getting Started

### Installation

Install Dango CLI via pip:

```bash
pip install getdango
```

**Verify installation**:

```bash
dango --version
# Output: dango version 0.0.5
```

### Create Your First Project

```bash
# Initialize project
dango init my-analytics
cd my-analytics

# Start platform
dango start

# Add a data source
dango source add

# Sync data
dango sync

# Generate staging models
dango generate

# Run transformations
dango run
```

### Get Help

```bash
# General help
dango --help

# Command-specific help
dango sync --help
dango source add --help
```

---

## CLI Guides

<div class="grid cards" markdown>

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete command reference for all dango commands.

    - Global options and flags
    - Project management commands
    - Data operation commands
    - Source management commands
    - Platform control commands
    - Configuration commands

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

-   :material-rocket-launch: **Init & Start**

    ---

    Project initialization and starting services.

    - Initialize new projects
    - Project configuration
    - Start/stop/restart platform
    - Manage multiple projects
    - Troubleshoot startup issues

    [:octicons-arrow-right-24: Init & Start Guide](init-start.md)

-   :material-sync: **Sync & Run**

    ---

    Data syncing and running transformations.

    - Sync data from sources
    - Generate staging models
    - Run dbt transformations
    - Incremental vs full-refresh
    - Performance optimization
    - Troubleshoot failures

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-database-outline: **Source Management**

    ---

    CLI commands for managing data sources.

    - Add sources interactively
    - List and inspect sources
    - Edit configurations
    - Manage OAuth credentials
    - Import/export sources

    [:octicons-arrow-right-24: Source Management](source-management.md)

-   :material-check-circle-outline: **Validation**

    ---

    Validate configuration and troubleshoot issues.

    - Validate project configuration
    - Check source connections
    - Verify database health
    - Auto-fix common issues
    - CI/CD integration

    [:octicons-arrow-right-24: Validation Guide](validation.md)

</div>

---

## Command Categories

### Project Lifecycle

Manage Dango projects:

```bash
dango init my-project       # Create new project
dango info                  # Show project metadata
dango status                # Check if running
dango validate              # Verify configuration
dango rename new-name       # Rename project
```

### Data Operations

Load and transform data:

```bash
dango sync                  # Sync all sources
dango sync --source stripe  # Sync specific source
dango generate              # Auto-generate staging
dango run                   # Run dbt transformations
dango run --select marts.*  # Run specific models
```

### Source Management

Configure data sources:

```bash
dango source add            # Add new source (wizard)
dango source list           # List all sources
dango source remove name    # Remove source
dango auth list             # List OAuth credentials
dango auth refresh name     # Refresh OAuth token
```

### Platform Control

Start and stop services:

```bash
dango start                 # Start all services
dango stop                  # Stop all services
dango restart               # Restart platform
dango start --no-metabase   # Skip Metabase
```

### Database Operations

Manage the data warehouse:

```bash
dango db status             # Database info
dango db clean              # Remove orphaned tables
```

### Documentation

Generate dbt documentation:

```bash
dango docs                  # Generate and serve docs
dango docs --port 8082      # Custom port
```

---

## Quick Reference

### Essential Workflow

```bash
# 1. Create project
dango init my-analytics
cd my-analytics

# 2. Add data source
dango source add

# 3. Start platform
dango start

# 4. Sync data
dango sync

# 5. Generate staging
dango generate

# 6. Run transformations
dango run

# 7. View data
# Open http://localhost:3000 (Metabase)
```

### Daily Operations

```bash
# Morning data refresh
dango sync && dango run

# Check what changed
dango status

# View recent activity
dango source list

# Validate everything
dango validate
```

### Development Iteration

```bash
# Edit dbt model
vim dbt/models/marts/my_metric.sql

# Run just that model
dango run --select my_metric

# Check results
duckdb data/warehouse.duckdb "SELECT * FROM marts.my_metric LIMIT 10"
```

---

## Common Patterns

### Sync Specific Sources

```bash
# Single source
dango sync --source stripe_payments

# Multiple sources
dango sync --source stripe --source google_sheets

# All except one
dango sync --exclude old_source
```

### Run Specific Models

```bash
# Single model
dango run --select customer_metrics

# Model and downstream
dango run --select customer_metrics+

# Model and upstream
dango run --select +customer_metrics

# Entire directory
dango run --select marts.*

# By tag
dango run --select tag:daily
```

### Full Refresh Workflows

```bash
# Full refresh data
dango sync --full-refresh

# Full refresh dbt
dango run --full-refresh

# Both
dango sync --full-refresh && dango run --full-refresh
```

---

## Scripting and Automation

### Shell Scripts

**Daily sync script** (`daily-sync.sh`):

```bash
#!/bin/bash
set -e

echo "Starting daily sync at $(date)"

# Validate configuration
dango validate --strict

# Sync all sources
dango sync

# Generate staging (if schema changed)
dango generate

# Run transformations
dango run

# Run tests
dbt test --profiles-dir .dango --project-dir dbt

echo "Daily sync complete at $(date)"
```

**Make executable**:

```bash
chmod +x daily-sync.sh
```

**Schedule with cron** (6am daily):

```bash
0 6 * * * cd /path/to/project && ./daily-sync.sh >> /var/log/dango-sync.log 2>&1
```

### Error Handling

```bash
#!/bin/bash

# Exit on error
set -e

# Trap errors
trap 'echo "Error on line $LINENO"' ERR

# Run with error checking
dango sync || {
  echo "Sync failed! Sending alert..."
  curl -X POST https://hooks.slack.com/... \
    -d '{"text": "Dango sync failed!"}'
  exit 1
}

echo "Success!"
```

### Parallel Execution

```bash
#!/bin/bash

# Sync sources in parallel
dango sync --source stripe &
dango sync --source google_sheets &
dango sync --source sales_data &

# Wait for all to complete
wait

echo "All syncs complete"
```

---

## CI/CD Integration

### GitHub Actions

**`.github/workflows/dango.yml`**:

```yaml
name: Dango Pipeline

on:
  schedule:
    - cron: '0 6 * * *'  # 6am daily
  workflow_dispatch:

jobs:
  sync-and-transform:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install Dango
        run: pip install getdango

      - name: Validate Configuration
        run: dango validate --strict
        env:
          STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}

      - name: Sync Data
        run: dango sync
        env:
          STRIPE_API_KEY: ${{ secrets.STRIPE_API_KEY }}

      - name: Generate Staging
        run: dango generate

      - name: Run Transformations
        run: dango run

      - name: Run Tests
        run: dbt test --profiles-dir .dango --project-dir dbt

      - name: Upload Database
        uses: actions/upload-artifact@v3
        with:
          name: warehouse
          path: data/warehouse.duckdb
```

### GitLab CI

**`.gitlab-ci.yml`**:

```yaml
stages:
  - validate
  - sync
  - transform
  - test

validate:
  stage: validate
  script:
    - pip install getdango
    - dango validate --strict

sync:
  stage: sync
  script:
    - pip install getdango
    - dango sync
  artifacts:
    paths:
      - data/warehouse.duckdb

transform:
  stage: transform
  script:
    - pip install getdango
    - dango generate
    - dango run
  dependencies:
    - sync

test:
  stage: test
  script:
    - dbt test --profiles-dir .dango --project-dir dbt
  dependencies:
    - transform
```

---

## Environment Variables

### Configuration

Set environment variables for credentials:

```bash
# .env file (gitignored)
STRIPE_API_KEY=sk_live_abc123...
GOOGLE_CREDENTIALS=/path/to/credentials.json
POSTGRES_URL=postgresql://user:pass@host:5432/db
FACEBOOK_ACCESS_TOKEN=EAA...
```

**Load in shell**:

```bash
# Export for current session
export $(cat .env | xargs)

# Or use direnv (auto-loads .env)
direnv allow
```

### Common Variables

| Variable | Purpose |
|----------|---------|
| `DANGO_PROJECT_DIR` | Override project directory |
| `DANGO_LOG_LEVEL` | Set log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `DANGO_NO_COLOR` | Disable colored output |
| `STRIPE_API_KEY` | Stripe API authentication |
| `GOOGLE_CREDENTIALS` | Google API service account |
| `POSTGRES_URL` | PostgreSQL connection string |

---

## Tips and Tricks

### Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Quick commands
alias ds='dango sync'
alias dr='dango run'
alias dv='dango validate'
alias dsr='dango sync && dango run'

# Common options
alias dsf='dango sync --full-refresh'
alias drf='dango run --full-refresh'
```

### Tab Completion

Enable bash completion:

```bash
# Add to ~/.bashrc
eval "$(_DANGO_COMPLETE=bash_source dango)"

# Or for zsh (~/.zshrc)
eval "$(_DANGO_COMPLETE=zsh_source dango)"
```

### Watch Mode

Auto-run on file changes:

```bash
# Install watchdog
pip install watchdog

# Watch dbt models
watchmedo shell-command \
  --patterns="*.sql" \
  --recursive \
  --command='dango run --select marts.*' \
  dbt/models/
```

---

## CLI vs Web UI

Choose the right interface for your task:

| Task | CLI | Web UI |
|------|-----|--------|
| **Automation** | ✅ Excellent | ❌ Not scriptable |
| **Visual monitoring** | ⚠️ Terminal only | ✅ Dashboards |
| **File uploads** | ⚠️ Copy files | ✅ Drag-and-drop |
| **Quick actions** | ✅ Fast commands | ✅ One-click buttons |
| **CI/CD pipelines** | ✅ Perfect | ❌ No integration |
| **Debugging** | ✅ Verbose logs | ✅ Search/filter logs |
| **Remote access** | ✅ SSH compatible | ⚠️ Needs port forwarding |

**Both are equally powerful** - use what fits your workflow!

---

## Next Steps

<div class="grid cards" markdown>

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete reference for all CLI commands and options.

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

-   :material-rocket-launch: **Init & Start**

    ---

    Learn project initialization and service management.

    [:octicons-arrow-right-24: Init & Start Guide](init-start.md)

-   :material-sync: **Sync & Run**

    ---

    Master data syncing and transformation workflows.

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-view-dashboard: **Web UI Alternative**

    ---

    Explore the visual interface for the same functionality.

    [:octicons-arrow-right-24: Web UI Overview](../web-ui/web-ui-overview.md)

</div>
