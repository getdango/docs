# Troubleshooting

Common issues and solutions for Dango installation and usage.

---

## Installation Issues

### Python Version Too Old

**Error:**

```
ERROR: Dango requires Python 3.10 or higher
```

**Solution:**

Check your Python version and install a newer version:

=== "macOS / Linux"

    ```bash
    # Check your version
    python3 --version

    # Install Python 3.11 (recommended)
    # macOS:
    brew install python@3.11

    # Ubuntu:
    sudo apt install python3.11 python3.11-venv python3-pip
    ```

=== "Windows"

    Download from [python.org](https://www.python.org/downloads/) or install from Microsoft Store.

---

### Docker Not Found

**Error:**

```
ERROR: Docker is not installed or not running
```

**Solution:**

1. Install Docker Desktop: [docs.docker.com/desktop](https://docs.docker.com/desktop/)
2. Start Docker Desktop (check system tray icon)
3. Verify installation:

```bash
docker --version
```

!!! info "Can I use Dango without Docker?"
    You can use Dango for data syncing and dbt transformations without Docker, but Metabase dashboards and the Web UI require Docker.

---

### Docker Desktop Not Running

**Error:**

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**

Docker is installed but the daemon isn't running:

1. **Open Docker Desktop** from your Applications folder or system tray
2. Wait for the Docker icon to show "Docker Desktop is running" (the whale icon stops animating)
3. Verify it's ready:

```bash
docker info
```

If Docker Desktop won't start, try restarting your computer. On Linux, you may need to start the service manually:

```bash
sudo systemctl start docker
```

---

### pip install getdango Failed

**Error:**

```
ERROR: Could not find a version that satisfies the requirement getdango
```

**Solutions:**

**1. Check internet connection:**

```bash
ping pypi.org
```

**2. Upgrade pip:**

```bash
pip install --upgrade pip
```

**3. Try again:**

```bash
pip install getdango
```

**4. If still failing, check Python version:**

```bash
python --version  # Must be 3.10 or higher
```

---

### Permission Denied

**Error:**

```
ERROR: Permission denied while installing
```

**Solution:**

Don't use `sudo` with pip in a virtual environment. Check that you're in a virtual environment:

=== "macOS / Linux"

    ```bash
    # Activate virtual environment
    source venv/bin/activate

    # Your prompt should show (venv)
    # Then install
    pip install getdango
    ```

=== "Windows"

    ```powershell
    # Activate virtual environment
    .\venv\Scripts\Activate.ps1

    # Then install
    pip install getdango
    ```

---

## Runtime Issues

### Background Process Behavior (macOS)

On macOS, `dango start` launches background processes that **continue running after you close the terminal**. This is normal — your syncs and schedules keep running.

**Checking if Dango is running:**

```bash
dango status
```

**Restarting after closing terminal:**

```bash
# Just run start again — it detects the existing process
dango start
```

**Stopping Dango:**

```bash
dango stop
```

---

### "dango: command not found" (Virtual Environment)

**Solution:**

Make sure your virtual environment is activated:

=== "macOS / Linux"

    ```bash
    # Navigate to your project
    cd my-analytics

    # Activate venv
    source venv/bin/activate

    # Or use full path
    ./venv/bin/dango --version
    ```

=== "Windows"

    ```powershell
    # Navigate to your project
    cd my-analytics

    # Activate venv
    .\venv\Scripts\Activate.ps1

    # Verify
    dango --version
    ```

---

### "dango: command not found" (Global Install)

If you just installed Dango globally, your terminal needs to reload.

**Solution:**

**Option 1: Restart terminal (recommended)**

Close and reopen your terminal, then verify:

```bash
dango --version
```

**Option 2: Reload shell config**

=== "macOS / Linux"

    ```bash
    # For zsh users:
    source ~/.zshrc

    # For bash on macOS:
    source ~/.bash_profile

    # For bash on Linux:
    source ~/.bashrc

    # Then verify:
    dango --version
    ```

=== "Windows"

    Restart PowerShell or Terminal.

---

### "dango: command not found" After pip Install

**Problem:** You ran `pip install getdango` (or `pip install --upgrade getdango`) but the `dango` command still points to the old version or isn't found.

**Solution:**

Your shell caches the location of commands. Clear the cache after installing:

```bash
hash -r
dango --version
```

This tells your shell to re-scan `PATH` for the `dango` command. If you're using a virtual environment, make sure it's activated first.

---

### Port 8800 Already in Use

**Error:**

```
ERROR: Port 8800 is already in use
```

**Solutions:**

**Option 1: Stop Dango (if running)**

```bash
dango stop
```

**Option 2: Kill the process using the port**

=== "macOS / Linux"

    ```bash
    lsof -ti:8800 | xargs kill -9
    ```

=== "Windows"

    ```powershell
    # Find process using port 8800
    netstat -ano | findstr :8800

    # Kill process (replace <PID> with process ID)
    taskkill /PID <PID> /F
    ```

**Option 3: Change the port**

Edit `.dango/project.yml` and change `platform.port` to a different value (e.g., 8801).

---

### Port 3000 Already in Use (Metabase)

**Error:**

Metabase fails to start because port 3000 is already in use by another application.

**Solution:**

Find and stop the process using port 3000:

=== "macOS / Linux"

    ```bash
    # Find what's using port 3000
    lsof -ti:3000

    # Kill the process
    lsof -ti:3000 | xargs kill -9
    ```

=== "Windows"

    ```powershell
    netstat -ano | findstr :3000
    taskkill /PID <PID> /F
    ```

Then restart the platform:

```bash
dango stop
dango start
```

Common applications that use port 3000: React dev servers, Grafana, Rails applications.

---

### Port 2718 Already in Use (dbt Docs)

**Error:**

The dbt docs server fails to start because port 2718 is occupied.

**Solution:**

=== "macOS / Linux"

    ```bash
    lsof -ti:2718 | xargs kill -9
    ```

Then restart:

```bash
dango stop
dango start
```

---

### Metabase Not Starting

**Error:**

```
ERROR: Metabase container failed to start
```

**Solutions:**

**1. Check Docker is running:**

```bash
docker ps
```

**2. Check container logs:**

```bash
# Get container ID
docker ps -a

# View logs
docker logs <container-id>
```

**3. Restart everything:**

```bash
dango stop
dango start
```

**4. Check Docker resources:**

Make sure Docker has enough resources allocated:

- Open Docker Desktop → Settings → Resources
- Allocate at least 4GB RAM
- Restart Docker Desktop

---

### Metabase Cold Start (Slow First Launch)

**Problem:** Metabase shows a loading screen for several minutes on first launch.

**This is normal.** Metabase takes 2–3 minutes to initialize its internal database on the first startup. Subsequent starts are much faster.

**How to check progress:**

```bash
# Check container health status
docker ps
```

The Metabase container will show "health: starting" during initialization and "healthy" when ready. Wait for the healthy status before accessing `http://localhost:8800`.

---

### Sync Failed

**Error:**

```
ERROR: Failed to sync data from source
```

**Solutions:**

**1. Check API credentials:**

Verify your credentials in `.dango/sources.yml`:

```bash
cat .dango/sources.yml
```

**2. Verify internet connection:**

```bash
ping google.com
```

**3. Check source-specific documentation:**

Different sources have different requirements. See:

- [Data Sources Documentation](../data-sources/index.md)
- [dlt Source Documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/)

**4. Run with debug logging:**

```bash
RUNTIME__LOG_LEVEL=DEBUG dango sync
```

---

### Token Expired (OAuth Sources)

**Error:**

```
ERROR: OAuth token expired for source 'google_sheets'
```

**Solution:**

Re-authenticate with the OAuth provider:

```bash
# Check which tokens need renewal
dango oauth status

# Option A: Refresh the token (simplest)
dango oauth refresh <source_type>  # e.g., google_sheets, facebook_ads

# Option B: Re-authenticate with provider-specific command
dango oauth google_sheets
dango oauth facebook_ads

# Option C: Remove and re-add (if refresh fails)
dango oauth remove <source_type>  # e.g., google_sheets
dango source add
```

!!! info "Token lifetimes"
    Google tokens are refreshed automatically by dlt. Facebook tokens last 60 days and require manual re-authentication. Run `dango oauth status` periodically to check expiry dates.

See [OAuth Troubleshooting](../guides/oauth-troubleshooting.md) for detailed setup and error resolution.

---

### dbt Run Failed

**Error:**

```
ERROR: dbt run failed with compilation error
```

**Solutions:**

**1. Check your SQL syntax:**

Look at the error message for the specific model file and line number.

**2. Validate dbt project:**

```bash
cd dbt_project
dbt debug
```

**3. Run specific model:**

```bash
dango run --select staging.stg_my_source
```

**4. Check model dependencies:**

Make sure all `{{ ref() }}` references point to existing models.

---

### Database Locked

**Error:**

```
ERROR: database is locked
```

**Cause:**

DuckDB uses a single-writer model — only one process can write to the database at a time. This happens when:

- Two `dango sync` commands run simultaneously
- A sync is running while you try to query with write access
- A previous process crashed and left a lock file

**Solutions:**

**1. Stop all Dango processes:**

```bash
dango stop
```

**2. Check for running sync processes:**

=== "macOS / Linux"

    ```bash
    ps aux | grep dango
    ```

=== "Windows"

    ```powershell
    Get-Process | Where-Object { $_.ProcessName -like "*dango*" }
    ```

Kill any stuck processes, then restart:

```bash
dango start
```

**3. Remove stale lock files (if no processes are running):**

```bash
# Only do this if no dango processes are running
rm -f data/warehouse.duckdb.wal
```

Learn more about DuckDB's concurrency model in [DuckDB](../core-concepts/duckdb.md).

---

## Data Issues

### Data Not Appearing in Metabase

**Solutions:**

**1. Verify data was synced:**

Open a DuckDB session to check:

```bash
duckdb data/warehouse.duckdb "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema LIKE 'staging%'"
```

**2. Refresh Metabase schema:**

After adding new sources or dbt models, tell Metabase to discover the new tables:

```bash
dango metabase refresh
```

**3. Check tables exist:**

```bash
duckdb data/warehouse.duckdb "SHOW TABLES"
```

**4. Check Metabase database connection:**

Open Metabase → Admin → Databases → Verify DuckDB is connected

---

### CSV File Not Loading

**Error:**

```
ERROR: Failed to load CSV file
```

**Solutions:**

**1. Check file path:**

```bash
# Verify file exists
ls -la /path/to/your/file.csv
```

**2. Check file permissions:**

```bash
# Make sure file is readable
chmod 644 /path/to/your/file.csv
```

**3. Check CSV format:**

- Ensure file has headers
- Check for proper comma/delimiter usage
- Verify encoding (UTF-8 recommended)

**4. Try with a sample:**

Test with a small sample CSV first:

```bash
head -10 /path/to/your/file.csv > sample.csv
dango source add  # Add sample.csv as a File Import source
```

!!! tip "Use File Import, not CSV"
    When adding file sources, select **File Import (CSV, JSON, Parquet)** in the wizard. This is the `local_files` source type. The legacy `csv` type is hidden from the wizard.

---

### Incremental Load Issues

**Error:**

```
ERROR: Incremental load failed - duplicate key
```

**Solution:**

This usually means the primary key configuration is incorrect:

1. Check your dbt model configuration:
   ```sql
   {{ config(
       materialized='incremental',
       unique_key='id'  # Make sure this column exists and is unique
   ) }}
   ```

2. Force full refresh:
   ```bash
   dango sync --full-refresh
   ```

---

## Performance Issues

### Sync Taking Too Long

**Solutions:**

**1. Use incremental loads:**

Instead of full refreshes, use incremental models in dbt.

**2. Limit data extraction:**

Configure start dates or filters in `.dango/sources.yml`.

**3. Increase DuckDB memory:**

Edit `.dango/project.yml` and increase `database.memory_limit`.

**4. Check network speed:**

For API sources, slow network can impact sync times.

---

### High Memory Usage

**Solutions:**

**1. Reduce DuckDB memory limit:**

Edit `.dango/project.yml`:

```yaml
database:
  memory_limit: "2GB"  # Adjust as needed
```

**2. Process data in chunks:**

For large datasets, configure batch sizes in dlt sources.

**3. Close unused applications:**

Free up system memory by closing other applications.

---

## Platform Issues

### Web UI Not Loading

**Solutions:**

**1. Check platform is running:**

```bash
dango status
```

**2. Verify port 8800 is accessible:**

```bash
curl http://localhost:8800
```

**3. Check browser console:**

Open browser developer tools (F12) and check for errors.

**4. Try different browser:**

Some browser extensions can interfere with local development.

---

### File Watcher Not Detecting Changes

**Solutions:**

**1. Check file watcher is running:**

```bash
dango status
```

**2. Verify file path configuration:**

Check `.dango/sources.yml` for correct file paths.

**3. Check file system events:**

Some systems have limits on file system watchers:

=== "Linux"

    ```bash
    # Increase inotify watches
    echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
    ```

---

## Getting Help

If you're still experiencing issues:

### 1. Search Existing Issues

Check if someone else has had the same problem:

[github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)

### 2. Enable Debug Logging

Run commands with debug logging for detailed output:

```bash
RUNTIME__LOG_LEVEL=DEBUG dango sync
```

### 3. Validate Installation

```bash
dango validate
```

### 4. Open a New Issue

If you can't find a solution, open an issue with:

- Dango version (`dango --version`)
- Operating system and version
- Python version (`python --version`)
- Docker version (`docker --version`)
- Full error message and stack trace
- Steps to reproduce

[Open an issue →](https://github.com/getdango/dango/issues/new)

---

## Additional Resources

- **[Installation Guide](installation.md)** — Reinstall if needed
- **[Quick Start](quick-start.md)** — Review basic workflows
- **[CLI Reference](../cli/cli-reference.md)** — All available commands
- **[Security & Authentication](../security/index.md)** — Auth, OAuth, credentials
- **[Scheduling & Monitoring](../scheduling-monitoring/index.md)** — Syncs, alerts, health checks
- **[Deployment](../deployment/index.md)** — Cloud deployment guide
- **[GitHub Issues](https://github.com/getdango/dango/issues)** — Community support

## Related

- [Advanced Troubleshooting](../workflows/troubleshooting.md) — in-depth debugging techniques and solutions
- [FAQ](../faq.md) — answers to common questions
- [DuckDB & Single-Writer](../core-concepts/duckdb.md) — understanding database locking issues
