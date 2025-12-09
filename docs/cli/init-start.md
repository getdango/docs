# Init & Start

Project initialization and starting services via CLI.

---

## Overview

This guide covers the essential commands for creating and starting Dango projects. Learn how to initialize new projects, configure settings, and start the platform.

**What you'll learn**:

- Initialize new Dango projects
- Understanding project structure
- Configure platform settings
- Start and stop services
- Manage multiple projects
- Troubleshoot startup issues

---

## Initializing a New Project

### Interactive Initialization

The recommended way to create a new project:

```bash
dango init my-analytics
```

**Interactive wizard prompts**:

```
Welcome to Dango!

Let's set up your data analytics project.

Project name: my-analytics
Organization (optional): Acme Corp
Created by: alice@acme.com

What's the purpose of this project?
> Track customer behavior and revenue metrics

Would you like to add a stakeholder? (Y/n): y
  Name: Bob Chen
  Role: CEO
  Email: bob@acme.com

Would you like to add another stakeholder? (y/N): n

Data SLA/Cadence (optional): Daily updates by 9am UTC

Known limitations (optional): Stripe data has 24h delay

Would you like to add a data source now? (Y/n): y

Select source type:
  1. CSV files
  2. Stripe
  3. Google Sheets
  ...

Creating project structure...
✓ Created .dango/project.yml
✓ Created .dango/sources.yml
✓ Created dbt/ directory
✓ Created data/ directory
✓ Created custom_sources/ directory
✓ Created docker-compose.yml
✓ Created .gitignore

Project initialized successfully!

Next steps:
  cd my-analytics
  dango start        # Start the platform
  dango sync         # Sync your first data source
```

### Non-Interactive Initialization

Create a blank project without the wizard:

```bash
dango init my-analytics --skip-wizard
```

**What it creates**:

```
my-analytics/
├── .dango/
│   ├── project.yml          # Project metadata
│   └── sources.yml          # Data source configuration
├── .dlt/
│   ├── config.toml          # dlt configuration
│   └── secrets.toml         # Credentials (gitignored)
├── data/
│   └── .gitkeep             # Data files directory
├── dbt/
│   ├── dbt_project.yml      # dbt configuration
│   ├── profiles.yml         # DuckDB connection (auto-configured)
│   ├── models/
│   │   ├── staging/         # Auto-generated models
│   │   ├── intermediate/    # Your models
│   │   └── marts/           # Your models
│   ├── tests/               # Custom tests
│   ├── macros/              # Reusable SQL
│   └── packages.yml         # dbt packages
├── custom_sources/
│   └── __init__.py          # Custom dlt sources
├── docker-compose.yml       # Metabase + dbt-docs
├── .gitignore               # Git ignore rules
└── .env.example             # Environment variables template
```

### Initialize in Current Directory

Initialize Dango in an existing directory:

```bash
cd existing-project
dango init .
```

**Safety check**:

```
Warning: Directory is not empty.
Files found:
  - data/sales.csv
  - README.md

Dango will create:
  - .dango/ directory
  - dbt/ directory
  - docker-compose.yml

Proceed? (y/N): y
```

### Template-Based Initialization

Use pre-configured templates:

```bash
# Analytics template (Stripe + GA4 + dbt)
dango init my-analytics --template analytics

# ETL template (databases + custom sources)
dango init my-etl --template etl

# Minimal template (bare bones)
dango init my-project --template minimal
```

**Templates include**:

- **analytics**: Stripe, Google Analytics 4, example dashboards
- **etl**: PostgreSQL, MySQL connectors, scheduling config
- **minimal**: Blank project, no pre-configured sources

### Force Reinitialize

Reinitialize an existing project:

```bash
dango init my-analytics --force
```

**Warning**:

```
⚠ Project 'my-analytics' already exists!

This will OVERWRITE:
  - .dango/project.yml (backup created)
  - dbt/dbt_project.yml (backup created)

This will PRESERVE:
  - .dango/sources.yml
  - data/ directory
  - dbt/models/ (your custom models)

Backups saved to .dango/backups/2024-12-09-12-34-56/

Proceed? (y/N): y
```

---

## Project Configuration

### Project Metadata

**Edit `.dango/project.yml`**:

```yaml
project:
  name: my-analytics
  organization: Acme Corp
  created_at: 2024-12-09
  created_by: alice@acme.com
  dango_version: 0.0.5

  purpose: |
    Track customer behavior and revenue metrics for
    executive dashboards and marketing analysis.

  stakeholders:
    - name: Bob Chen
      role: CEO
      email: bob@acme.com
      slack: "@bob"

    - name: Sarah Lee
      role: Senior Analyst
      email: sarah@acme.com
      slack: "@sarah"

  sla:
    description: Daily updates by 9am UTC
    frequency: daily
    time: "09:00"
    timezone: UTC

  limitations:
    - Stripe data has 24h processing delay
    - Google Sheets updated manually
    - Facebook Ads API rate limited

platform:
  port: 8800
  metabase_port: 3000
  dbt_docs_port: 8081

  auto_sync: true
  debounce_seconds: 600  # 10 minutes

  file_watcher:
    enabled: true
    patterns:
      - "*.csv"
      - "*.json"
    ignored_dirs:
      - ".git"
      - "venv"
      - "node_modules"

database:
  path: data/warehouse.duckdb

  settings:
    memory_limit: "2GB"
    threads: 4
```

### View Configuration

Display current configuration:

```bash
# Human-readable
dango info

# YAML format
dango config show

# JSON format
dango config show --format json

# Specific section
dango config show --section platform
```

---

## Starting the Platform

### Basic Start

Start all services:

```bash
dango start
```

**Startup sequence**:

```
Starting Dango platform...

[1/5] Starting FastAPI Web UI...
      ✓ Web UI started on http://localhost:8800

[2/5] Starting File Watcher...
      ✓ Watching data/ for changes
      ✓ Auto-sync enabled (600s debounce)

[3/5] Starting Docker services...
      Pulling metabase:latest (if needed)
      ✓ Metabase container started

[4/5] Waiting for Metabase to be ready...
      This may take 30-60 seconds on first run...
      ✓ Metabase ready on http://localhost:3000

[5/5] Starting dbt-docs server...
      ✓ dbt-docs started on http://localhost:8081

──────────────────────────────────────────────
✓ Platform running successfully!

Services:
  Web UI:    http://localhost:8800
  Metabase:  http://localhost:3000
  dbt-docs:  http://localhost:8081

Press Ctrl+C to stop, or run 'dango stop' in another terminal.
──────────────────────────────────────────────
```

**First-time setup takes longer**:

- Docker images downloaded (Metabase ~500 MB)
- Metabase initializes database
- dbt compiles project

**Subsequent starts are faster** (~10 seconds).

### Custom Port

Override default Web UI port:

```bash
dango start --port 8888
```

**Access at**: http://localhost:8888

**Persistent port change** - edit `.dango/project.yml`:

```yaml
platform:
  port: 8888
```

### Selective Services

Start only specific services:

```bash
# Skip Metabase
dango start --no-metabase

# Skip dbt-docs
dango start --no-docs

# Skip file watcher
dango start --no-watcher

# Only Web UI
dango start --no-metabase --no-docs --no-watcher
```

**Use cases**:

- **No Metabase**: Docker not available, or using external BI tool
- **No dbt-docs**: Don't need documentation UI
- **No watcher**: Disable auto-sync for production

### Background Mode

Run platform in background:

```bash
dango start --background
```

**Or use shorthand**:

```bash
dango start -d
```

**Background output**:

```
Starting Dango platform in background...
✓ Platform started (PID: 12345)

View logs: dango logs
Stop: dango stop
Status: dango status
```

**View logs**:

```bash
# Tail logs
dango logs --follow

# Last 100 lines
dango logs --tail 100

# Logs since timestamp
dango logs --since "2024-12-09 12:00"
```

---

## Checking Status

### Platform Status

Check if platform is running:

```bash
dango status
```

**Output when running**:

```
Project: my-analytics (Port: 8800)
Status: ● Running

Services:
  FastAPI Web UI     ● Running (http://localhost:8800)
  File Watcher       ● Running (auto-sync enabled)
  Metabase          ● Running (http://localhost:3000)
  dbt-docs          ● Running (http://localhost:8081)

Database: data/warehouse.duckdb (42.3 MB)
Sources: 5 configured (4 enabled, 1 disabled)
Last activity: 2 minutes ago

Uptime: 3 hours 24 minutes
```

**Output when stopped**:

```
Project: my-analytics (Port: 8800)
Status: ○ Stopped

All services are stopped.
Run 'dango start' to start the platform.
```

### JSON Output

For scripting:

```bash
dango status --json
```

**Response**:

```json
{
  "project": "my-analytics",
  "port": 8800,
  "running": true,
  "services": {
    "web_ui": {
      "status": "running",
      "url": "http://localhost:8800",
      "pid": 12345
    },
    "file_watcher": {
      "status": "running",
      "auto_sync": true,
      "pid": 12346
    },
    "metabase": {
      "status": "running",
      "url": "http://localhost:3000",
      "container_id": "abc123..."
    },
    "dbt_docs": {
      "status": "running",
      "url": "http://localhost:8081",
      "container_id": "def456..."
    }
  },
  "database": {
    "path": "data/warehouse.duckdb",
    "size_mb": 42.3
  },
  "uptime_seconds": 12240
}
```

### Status Checks

Exit code check for scripts:

```bash
dango status --check
if [ $? -eq 0 ]; then
  echo "Platform is running"
else
  echo "Platform is stopped"
  dango start
fi
```

---

## Stopping the Platform

### Normal Stop

Gracefully stop all services:

```bash
dango stop
```

**Shutdown sequence**:

```
Stopping Dango platform...

[1/4] Stopping File Watcher...
      ✓ File watcher stopped

[2/4] Stopping FastAPI Web UI...
      ✓ Web UI stopped

[3/4] Stopping Docker containers...
      ✓ Metabase container stopped
      ✓ dbt-docs container stopped

[4/4] Cleanup...
      ✓ PID files removed
      ✓ Temp files cleaned

Platform stopped successfully.
```

### Force Stop

Force kill processes if graceful stop fails:

```bash
dango stop --force
```

**Use when**:

- Normal stop hangs
- Services not responding
- Process crashed

**Warning**: May cause data loss if sync in progress.

### Stop All Projects

Stop all Dango projects on machine:

```bash
dango stop --all
```

**Output**:

```
Found 3 running Dango projects:

1. my-analytics (port 8800)
2. marketing-data (port 8801)
3. finance-etl (port 8802)

Stop all projects? (y/N): y

Stopping my-analytics...
✓ Stopped

Stopping marketing-data...
✓ Stopped

Stopping finance-etl...
✓ Stopped

All Dango projects stopped.
```

---

## Restarting the Platform

### Quick Restart

Restart all services:

```bash
dango restart
```

**Equivalent to**:

```bash
dango stop && dango start
```

**Use when**:

- Configuration changes
- Upgrading Dango version
- Resolving stuck processes

### Restart with Options

```bash
# Restart on different port
dango restart --port 8888

# Restart without Metabase
dango restart --no-metabase

# Restart in background
dango restart --background
```

---

## Managing Multiple Projects

### Project Routing

Dango maintains a routing registry for multiple projects:

**Location**: `~/.dango/routing.json`

**Contents**:

```json
{
  "projects": {
    "my-analytics": {
      "path": "/Users/alice/projects/my-analytics",
      "port": 8800,
      "created": "2024-12-09T12:00:00Z",
      "last_started": "2024-12-09T14:30:00Z"
    },
    "marketing-data": {
      "path": "/Users/alice/projects/marketing-data",
      "port": 8801,
      "created": "2024-11-15T09:00:00Z",
      "last_started": "2024-12-08T08:00:00Z"
    }
  }
}
```

### Running Multiple Projects

**Project 1**:

```bash
cd ~/projects/my-analytics
dango start
# Web UI: http://localhost:8800
# Metabase: http://localhost:3000
```

**Project 2** (different ports):

```bash
cd ~/projects/marketing-data
# Edit .dango/project.yml
#   port: 8801
#   metabase_port: 3001
#   dbt_docs_port: 8082
dango start
# Web UI: http://localhost:8801
# Metabase: http://localhost:3001
```

**Access both simultaneously**:

- my-analytics: http://localhost:8800
- marketing-data: http://localhost:8801

### List All Projects

```bash
dango projects list
```

**Output**:

```
Dango Projects:

  ● my-analytics (Running)
      Path: /Users/alice/projects/my-analytics
      Port: 8800
      Started: 2 hours ago

  ○ marketing-data (Stopped)
      Path: /Users/alice/projects/marketing-data
      Port: 8801
      Last started: Yesterday

  ○ finance-etl (Stopped)
      Path: /Users/alice/projects/finance-etl
      Port: 8802
      Last started: 3 days ago
```

### Switch Between Projects

```bash
# Stop current project
dango stop

# Navigate to another project
cd ~/projects/marketing-data

# Start new project
dango start
```

**Or use `--project-dir`**:

```bash
dango --project-dir ~/projects/marketing-data start
```

---

## Troubleshooting Startup

### Port Already in Use

**Error**:

```
✗ Failed to start Web UI
Error: Address already in use (port 8800)
```

**Solution 1: Find and kill process**:

```bash
# Find process using port 8800
lsof -i :8800
# Output: python 12345 alice ...

# Kill process
kill 12345

# Restart Dango
dango start
```

**Solution 2: Change port**:

```bash
# Temporary
dango start --port 8888

# Permanent
vim .dango/project.yml
# Change port: 8888
dango start
```

### Docker Not Running

**Error**:

```
✗ Failed to start Metabase
Error: Cannot connect to Docker daemon
```

**Solution**:

```bash
# Start Docker Desktop (macOS/Windows)
open -a Docker

# Or start Docker daemon (Linux)
sudo systemctl start docker

# Wait for Docker to start, then
dango start
```

**Or skip Docker**:

```bash
dango start --no-metabase
```

### Database Locked

**Error**:

```
✗ Failed to connect to database
Error: database is locked
```

**Cause**: Another process has database open.

**Solution**:

```bash
# Find processes with database open
lsof data/warehouse.duckdb

# Kill processes
kill <PID>

# Restart
dango start
```

### Metabase Won't Start

**Error**:

```
✗ Metabase failed to start
Container exited with code 1
```

**Check logs**:

```bash
docker logs dango-metabase-my-analytics
```

**Common fixes**:

1. **Port conflict**:
   ```bash
   # Change Metabase port in docker-compose.yml
   ports:
     - "3001:3000"  # Change 3000 to 3001
   ```

2. **Corrupted Metabase data**:
   ```bash
   # Remove Metabase volume
   docker volume rm dango-metabase-my-analytics

   # Restart (will reinitialize)
   dango start
   ```

3. **Insufficient memory**:
   ```bash
   # Increase Docker memory limit
   # Docker Desktop → Settings → Resources → Memory
   # Set to at least 4 GB
   ```

### File Watcher Not Working

**Symptom**: CSV files change but don't auto-sync.

**Check file watcher status**:

```bash
dango status
# Look for: File Watcher ● Running
```

**If stopped**:

```bash
# Check .dango/project.yml
platform:
  file_watcher:
    enabled: true  # Should be true

# Restart
dango restart
```

**Check watched patterns**:

```yaml
platform:
  file_watcher:
    patterns:
      - "*.csv"      # Ensure your file type is listed
      - "*.json"
```

---

## Best Practices

### 1. Use Version Control

Initialize git after creating project:

```bash
dango init my-analytics
cd my-analytics

git init
git add .
git commit -m "Initial Dango project setup"
```

**What's automatically gitignored**:

- `.dlt/secrets.toml` (credentials)
- `.env` (environment variables)
- `data/warehouse.duckdb` (database file)
- `dbt/target/` (compiled dbt files)
- `dbt/logs/` (dbt logs)

### 2. Document Your Project

Fill in `project.yml` metadata:

- **Purpose**: Why does this project exist?
- **Stakeholders**: Who uses this data?
- **SLA**: When is data expected?
- **Limitations**: Known issues or delays

**Benefits**:

- Onboard new team members faster
- Set clear expectations
- Track project evolution

### 3. Start Small

Don't configure everything upfront:

```bash
# Initialize with minimal config
dango init my-analytics --skip-wizard

# Add sources incrementally
dango source add  # First source
dango sync
dango generate
dango run

# Add more sources as needed
dango source add  # Second source
```

### 4. Use Templates for Consistency

For multiple similar projects:

```bash
# Create first project with full config
dango init project-a
# ... configure everything ...

# Export as template
dango template export project-a my-company-template

# Use template for new projects
dango init project-b --template my-company-template
dango init project-c --template my-company-template
```

### 5. Monitor Resource Usage

Check database size regularly:

```bash
dango db status
```

**Clean up if needed**:

```bash
# Remove orphaned tables
dango db clean

# Full database cleanup (careful!)
duckdb data/warehouse.duckdb "VACUUM;"
```

---

## Next Steps

<div class="grid cards" markdown>

-   :material-sync: **Sync & Run**

    ---

    Learn how to sync data and run transformations.

    [:octicons-arrow-right-24: Sync & Run Guide](sync-run.md)

-   :material-database-outline: **Source Management**

    ---

    Add and configure data sources via CLI.

    [:octicons-arrow-right-24: Source Management](source-management.md)

-   :material-check-circle-outline: **Validation**

    ---

    Validate configuration and troubleshoot issues.

    [:octicons-arrow-right-24: Validation Guide](validation.md)

-   :material-book-open-outline: **CLI Reference**

    ---

    Complete reference for all CLI commands.

    [:octicons-arrow-right-24: CLI Reference](cli-reference.md)

</div>
