# Troubleshooting

Common issues and their solutions.

---

## Quick Diagnostics

Run these commands first:

```bash
# Check overall status
dango status

# Validate configuration
dango validate

# Check specific source
dango info --source my_source
```

---

## DuckDB Locks

### Symptom

Sync or dbt run fails with "Database is locked" or "Could not acquire DbtLock".

### Cause

DuckDB allows only one writer process at a time. Dango enforces this with `DbtLock`, a file lock at `.dango/state/dbt.lock`. The lock holder's details are stored in `.dango/state/dbt.lock.json`:

```json
{
  "pid": 12345,
  "source": "stripe",
  "operation": "sync",
  "started_at": "2026-05-15T10:30:00",
  "hostname": "my-laptop"
}
```

### Diagnosis

```bash
# Check if a lock file exists
cat .dango/state/dbt.lock.json

# Check if the holding process is still running
ps -p <pid_from_json>
```

### Resolution

**If another sync is legitimately running** — wait for it to finish. Web UI syncs wait up to 5 minutes automatically.

**If the process crashed and left a stale lock:**

```bash
# Remove the stale lock files
rm .dango/state/dbt.lock .dango/state/dbt.lock.json

# Retry your operation
dango sync
```

!!! warning "Only Remove Locks If the Process Is Dead"
    Check `ps -p <pid>` first. Removing a lock while a sync is running can cause data corruption from concurrent DuckDB writes.

**DuckDB `read_only` does not prevent locks.** Even a `read_only=True` Python connection acquires a shared lock that blocks exclusive (write) locks from other processes. For Metabase, Dango uses a Docker `:ro` volume mount as the actual guard. For notebooks, use `dango snapshot db` to create an isolated read-only copy.

See [DuckDB Single-Writer](../core-concepts/duckdb.md) for the full locking model.

---

## OAuth Token Expiry

### Symptom

Sync fails with "Invalid token", "Token expired", or "Unauthorized" errors for OAuth-authenticated sources.

### Cause

OAuth tokens have limited lifetimes. Behavior varies by provider:

| Provider | Token Lifetime | Refresh |
|----------|---------------|---------|
| Google (Sheets, Analytics, Ads) | 1 hour | **Automatic** — dlt refreshes using the stored refresh token |
| Facebook (Ads) | 60 days | **Manual** — must re-authenticate before expiry |

### Diagnosis

```bash
# Check OAuth status for all sources
dango oauth check
```

This shows token validity, expiry dates, and warnings for tokens expiring within 7 days.

### Resolution

**Google sources** — tokens auto-refresh. If sync still fails:

```bash
# Re-authenticate to get a fresh refresh token
dango oauth setup google_sheets
```

**Facebook sources** — tokens expire after 60 days and cannot be auto-refreshed:

```bash
# Re-authenticate before the token expires
dango oauth setup facebook_ads
```

!!! tip "Set a Calendar Reminder"
    Facebook tokens expire silently after 60 days. Set a recurring reminder to run `dango oauth setup facebook_ads` before expiry.

See [OAuth](../security/oauth.md) for full provider details.

---

## Deploy Failures

### Symptom

`dango remote setup` or `dango remote push` fails partway through.

### Cause

Cloud deployment has 10 sub-steps. Failures can occur at any step:

1. Generate SSH key pair
2. Upload SSH key to DigitalOcean
3. Provision droplet
4. Create firewall
5. Server setup (install Docker, Caddy, Python, systemd)
6. Sync project files
7. Push secrets
8. Create admin + enable auth
9. Setup backups (optional)
10. Start services + health check + initial sync

### Diagnosis

```bash
# Check server status
dango remote status

# View recent server logs
dango remote logs

# Check deploy history
dango remote history
```

### Common Failures and Fixes

**SSH timeout (step 5-6)**:
```bash
# Verify SSH connectivity
ssh -i .dango/cloud_key root@<droplet-ip> echo "Connected"

# If firewall is blocking, check DigitalOcean console
```

**Quota exceeded (step 3)**: Check your DigitalOcean account limits. The default droplet size is `s-2vcpu-4gb`.

**Docker build timeout (step 10)**: Docker image pulls can be slow on small droplets. The default timeout is 300 seconds. If builds consistently fail, try a larger droplet size.

**Health check fails (step 10)**: Services started but `/api/health` didn't respond in time.
```bash
# Check what's running on the server
dango remote status

# View application logs
dango remote logs
```

**Rollback after failure:**
```bash
# If a deploy fails after backup was taken, the backup is preserved
# Redeploy after fixing the issue
dango remote push
```

For full deployment documentation, see [DigitalOcean Deployment](../deployment/digitalocean.md).

---

## Port Conflicts

### Symptom

`dango start` fails with "Address already in use" or services don't respond.

### Cause

Another process is using one of Dango's ports.

### Diagnosis

Check each port:

```bash
# Web UI / API (default 8800)
lsof -i :8800

# Metabase (default 3000)
lsof -i :3000

# dbt docs (default 8081)
lsof -i :8081

# Marimo notebooks (default 7805)
lsof -i :7805
```

### Resolution

**Option 1: Stop the conflicting process**

```bash
# Kill the process using the port
kill <PID>
```

**Option 2: Change the port in Dango**

```yaml
# .dango/project.yml
platform:
  port: 8801            # Default: 8800
  metabase_port: 3001   # Default: 3000
  dbt_docs_port: 8082   # Default: 8081
  marimo_port: 7806     # Default: 7805
```

Then restart: `dango stop && dango start`

---

## Sync Queuing

### Symptom

Clicking "Sync Now" in the web UI shows "Another sync in progress" or sync hangs for several minutes before failing.

### Cause

DuckDB's single-writer constraint means only one sync can run at a time. There is no queue — concurrent sync attempts either wait or fail.

| Trigger | Behavior |
|---------|----------|
| CLI (`dango sync`) | Fails immediately if lock is held |
| Web UI (Sync Now) | Waits up to **5 minutes** for the lock, then fails |
| Scheduler | Waits up to **5 minutes** for the lock, then fails |

### Diagnosis

```bash
# Check what's holding the lock
cat .dango/state/dbt.lock.json

# Check sync status
dango status
```

### Resolution

**Wait for the current sync to finish.** The web UI shows real-time progress via WebSocket.

**If the lock is stale** (process crashed), see [DuckDB Locks](#duckdb-locks) above.

**Schedule syncs to avoid overlap.** If multiple sources sync on overlapping schedules, stagger their cron expressions. Use `dango schedule add` (interactive wizard) to create schedules with different times:

- Source 1: every 6 hours starting at midnight (`0 0,6,12,18 * * *`)
- Source 2: every 6 hours starting at 1 AM (`0 1,7,13,19 * * *`)

---

## Schema Drift

### Symptom

After a sync, dbt transformations are skipped with a message about schema drift requiring attention.

### Cause

Dango runs a post-sync hook that compares the current schema against a stored baseline. When it detects **breaking changes**, it blocks dbt to prevent SQL errors from running against a changed schema.

**Breaking changes** (block dbt):
- Column removed
- Column type changed

**Additive changes** (logged, don't block):
- New column added

### Diagnosis

```bash
# View drift report for all sources
dango governance drift-report

# Check which sources need attention
dango governance drift-report --needs-attention
```

### Resolution

Review the drift report and accept the new schema:

```bash
# Accept the current schema as the new baseline
dango governance accept --source my_source
```

After accepting, the next sync will run dbt normally.

??? info "How Schema Drift Detection Works"
    The post-sync hook compares column names and types in `raw_{source}` schemas against a stored baseline. When breaking drift is detected, the baseline is NOT updated (frozen state) — the same breaking events are re-detected on every sync until you explicitly accept. This prevents dbt from silently running against a schema it wasn't designed for.

For full details, see [Schema Drift](../scheduling-monitoring/schema-drift.md).

---

## Metabase Connection Issues

### Symptom

Metabase shows "Database connection failed", tables don't appear, or queries return errors.

### Diagnosis

```bash
# Check if Metabase container is running
docker ps | grep metabase

# Check Metabase container logs
docker logs $(docker ps -q --filter name=metabase)

# Verify DuckDB file exists
ls -la data/warehouse.duckdb
```

### Common Issues and Fixes

**Docker container not running:**
```bash
dango stop
dango start
```

**Tables not showing after sync:**
```bash
# Force Metabase to re-scan the database schema
dango metabase refresh
```

**Driver version mismatch:**
If you see errors about incompatible database files, the DuckDB Python library and Metabase JDBC driver versions have diverged. Check `dango status` for version alignment warnings. See [Metabase Workflows > DuckDB Driver Version](metabase-workflows.md#duckdb-driver-version).

**SSO / login issues:**
Dango bridges authentication to Metabase automatically. If SSO fails:

1. Check that `dango start` completed without auth errors
2. Verify `.dango/auth.db` exists
3. Try restarting: `dango stop && dango start`

**DuckDB locked by Metabase (cloud):**
On cloud deployments, the Docker volume mount should be `:ro`. If Metabase is holding a write lock, verify the Docker Compose configuration uses a read-only mount.

---

## WebSocket Issues

### Symptom

The web UI shows stale data, sync progress doesn't update in real time, or you see "Connection lost — try refreshing your browser".

### Cause

WebSocket connections can drop due to network interruptions, proxy timeouts, or multi-worker deployment characteristics.

### Resolution

**Refresh the browser.** This re-establishes the WebSocket connection and fetches the latest state.

**Multi-worker limitation:** In multi-worker uvicorn deployments (used on cloud), WebSocket connections are per-worker. A sync launched by worker A broadcasts progress to worker A's clients. Worker B's clients receive updates via a file-based watcher (with slight delay). If real-time updates seem inconsistent, refresh the page.

**Proxy/reverse proxy timeout:** If using Caddy or nginx in front of Dango, ensure WebSocket upgrade headers are passed through. Dango's default Caddy configuration handles this automatically.

---

## Guard Rails

### Symptom

`dango start` or `dango remote push` shows warnings or requires confirmation.

### Cause

Dango includes safety checks to prevent common mistakes.

### Warning: "This looks like a cloned project"

**Trigger:** Project has `sources.yml` but no `warehouse.duckdb` — typical after `git clone`.

**Fix:** Run `dango sync` to load data before starting.

### Warning: "This project is deployed to {target}"

**Trigger:** Starting locally when a cloud deployment exists.

**What it means:** Your local instance is completely separate from the cloud. Changes here don't affect the cloud server.

**Skip the prompt:**
```bash
dango start --yes
```

### Warning: Git guardrails on deploy

**Trigger:** `dango remote push` when not on the expected branch or with uncommitted changes.

**Skip with explicit flags:**
```bash
# Deploy from a non-main branch
dango remote push --allow-branch

# Deploy with uncommitted changes
dango remote push --allow-dirty

# Override an existing deploy lock (not recommended)
dango remote push --force
```

---

## Sync Issues

### Sync Fails Immediately

**Symptom**: `dango sync` fails without starting

**Check configuration**:
```bash
dango validate
```

**Common causes**:

| Error | Solution |
|-------|----------|
| "Source not found" | Check source name in `sources.yml` |
| "Invalid configuration" | Review source-specific settings |
| "Missing credentials" | Check `.dlt/secrets.toml` |

### Sync Hangs or Times Out

**Symptom**: Sync runs but doesn't complete

**Solutions**:

```bash
# Enable debug logging
RUNTIME__LOG_LEVEL=DEBUG dango sync my_source

# Reduce scope with date range
dango sync my_source --since 2024-01-01
```

### Partial Sync / Missing Data

**Symptom**: Some records not appearing

**Check**:
1. Date range filters in source config
2. API rate limits (check logs)
3. Incremental state issues

**Reset incremental state**:
```bash
# Force full refresh
dango sync my_source --full-refresh
```

---

## Authentication Issues

### API Key Invalid

**Symptom**: 401/403 errors during sync

**Check**:
```bash
# Verify secrets file exists and has values
cat .dlt/secrets.toml
```

**Common issues**:
- Key copied with extra whitespace
- Wrong key (test vs live)
- Key revoked or expired

### Google OAuth "Access Denied"

**Symptom**: Can't complete OAuth flow

**Solutions**:
1. Ensure correct scopes are enabled in Google Cloud Console
2. Check OAuth consent screen configuration
3. Verify redirect URI matches exactly

---

## dbt Issues

### Models Fail to Run

**Symptom**: `dango run` fails with SQL errors

**Debug**:
```bash
# Get detailed error
cd dbt && dbt run --select failing_model --debug

# Check compiled SQL
cat dbt/target/compiled/*/models/**/failing_model.sql
```

**Common causes**:

| Error | Solution |
|-------|----------|
| "Relation does not exist" | Run `dango sync` first |
| "Column not found" | Source schema changed — check [Schema Drift](#schema-drift) |
| "Syntax error" | Review SQL in model file |

### Staging Models Not Generated

**Symptom**: No models in `dbt/models/staging/`

**Check**:
```bash
# Verify sync completed
dango status

# Manually trigger generation
dango generate
```

### Circular Dependencies

**Symptom**: "Circular dependency" error

**Solution**:
1. Check model refs: `grep -r "ref(" dbt/models/`
2. Draw dependency graph: `dbt docs generate && dbt docs serve`
3. Refactor to break cycle

---

## Database Issues

### DuckDB Connection Failed

**Symptom**: Can't connect to database

**Check**:
```bash
# Verify file exists
ls -la data/warehouse.duckdb

# Test connection
duckdb data/warehouse.duckdb "SELECT 1"
```

**Solutions**:
```bash
# If corrupted, restore from backup
cp backups/warehouse.duckdb data/

# Or clean and re-sync
dango db clean
dango sync
```

### Disk Space Full

**Symptom**: Sync or queries fail with disk errors

**Check**:
```bash
df -h .
du -sh data/
```

**Solutions**:
```bash
# Remove old backups
rm -rf backups/*.duckdb

# Clean database
dango db clean

# Compact DuckDB
duckdb data/warehouse.duckdb "VACUUM"
```

---

## Docker Issues

### Containers Won't Start

**Symptom**: `dango start` fails

**Check**:
```bash
# Docker running?
docker info

# Port conflicts?
lsof -i :3000  # Metabase
lsof -i :8800  # Web UI
```

**Solutions**:
```bash
# Clean Docker state
docker system prune

# Remove Dango containers
docker rm -f $(docker ps -aq --filter name=dango)

# Retry
dango start
```

### Out of Memory

**Symptom**: Containers killed, OOM errors

**Solution**: Increase Docker memory in Docker Desktop settings.

---

## Log Locations

### Finding Logs

| Component | Location |
|-----------|----------|
| Dango CLI | `.dango/logs/` |
| Audit log | `.dango/logs/audit.jsonl` |
| Sync status | `.dango/state/sync_status_*.json` |
| dlt pipelines | `.dlt/pipelines/*/runtime.log` |
| dbt | `dbt/logs/` |
| Metabase | `docker logs metabase` |

### Reading Logs

```bash
# Recent Dango logs (JSON lines format)
ls -lt .dango/logs/ | head -5
cat .dango/logs/activity.jsonl | tail -20

# dbt logs
cat dbt/logs/dbt.log | tail -100

# Search for errors
grep -i "error" .dango/logs/activity.jsonl
```

---

## Getting Help

### Gather Information

Before asking for help, collect:

```bash
# Version info
dango --version
dbt --version
python --version

# Configuration (sanitize secrets!)
cat .dango/sources.yml
cat .dango/project.yml

# Error logs
cat .dango/logs/activity.jsonl | tail -50
```

### Support Channels

1. **GitHub Issues**: [github.com/getdango/dango/issues](https://github.com/getdango/dango/issues)
2. **Discussions**: [github.com/getdango/dango/discussions](https://github.com/getdango/dango/discussions)

### Issue Template

````markdown
**Describe the issue**
What happened vs what you expected

**Steps to reproduce**
1. Run `dango ...`
2. See error

**Environment**
- Dango version: X.X.X
- OS: macOS/Linux/Windows
- Python version: X.X

**Logs**
```
Paste relevant log output
```

**Configuration** (sanitize secrets!)
```yaml
Paste relevant config
```
````

---

## Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Source not enabled" | Source disabled in config | Set `enabled: true` |
| "Pipeline failed" | dlt sync error | Check dlt logs |
| "Compilation error" | dbt SQL invalid | Check model SQL |
| "Connection refused" | Service not running | Run `dango start` |
| "Permission denied" | File access issue | Check file permissions |
| "Rate limit exceeded" | API throttling | Wait and retry |
| "Could not acquire DbtLock" | Another sync running | See [DuckDB Locks](#duckdb-locks) |
| "Schema drift requires attention" | Breaking schema change | See [Schema Drift](#schema-drift) |
| "OAuth token expired" | Token needs refresh | See [OAuth Token Expiry](#oauth-token-expiry) |

---

## Cloud API Provider IP Blocking

### Symptom

A data source works locally but returns 403 errors when syncing on a cloud deployment.

### Cause

Some API providers (e.g., chess.com) block requests from cloud provider IP ranges (DigitalOcean, AWS, GCP) to prevent scraping. Your local IP is allowed, but your server's IP is not.

### Resolution

- **Try a different data source** for initial cloud testing
- **Contact the API provider** about allowlisting your server's IP address
- **Use a residential proxy** if the provider offers no allowlisting mechanism

This is not a Dango issue — it affects any tool making API calls from cloud infrastructure.

---

## Next Steps

- [Performance](performance.md) - Optimize slow operations
- [Backup & Restore](backup-restore.md) - Recovery procedures
- [Community](../community/index.md) - Get help
