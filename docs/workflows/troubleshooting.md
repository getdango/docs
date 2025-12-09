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
# Check if source API is responsive
curl -I https://api.stripe.com/v1/charges

# Enable debug logging
RUNTIME__LOG_LEVEL=DEBUG dango sync --source my_source

# Reduce scope with date range
dango sync --source my_source --start-date 2024-01-01
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
dango sync --source my_source --full-refresh
```

---

## Authentication Issues

### OAuth Token Expired

**Symptom**: "Invalid token" or "Unauthorized" errors

**Solution**:
```bash
# Re-authenticate
dango auth [provider]
# Example: dango auth google_sheets

# Check token status
dango auth status --provider google_sheets
```

### API Key Invalid

**Symptom**: 401/403 errors during sync

**Check**:
```bash
# Verify secrets file
cat .dlt/secrets.toml

# Test key manually (example for Stripe)
curl https://api.stripe.com/v1/charges \
  -u sk_test_xxx:
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
| "Column not found" | Check source schema changed |
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

### Database Locked

**Symptom**: "Database is locked" error

**Cause**: Multiple processes accessing DuckDB

**Solution**:
```bash
# Stop all services
dango stop

# Kill any hanging processes
pkill -f duckdb

# Restart
dango start
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

## Metabase Issues

### Can't Access Metabase

**Symptom**: http://localhost:3000 not responding

**Check**:
```bash
# Is Metabase running?
dango status

# Check Docker
docker ps | grep metabase
```

**Solutions**:
```bash
# Restart Metabase
dango stop
dango start

# Check Docker logs
docker logs $(docker ps -q --filter name=metabase)
```

### Tables Not Showing

**Symptom**: DuckDB tables not visible in Metabase

**Solutions**:
```bash
# Refresh database connection
dango metabase refresh

# Or manually in Metabase:
# Admin → Databases → Sync database schema
```

### Dashboard Load Failed

**Symptom**: Error loading metabase_export.json

**Check JSON validity**:
```bash
python -c "import json; json.load(open('metabase_export.json'))"
```

**Solutions**:
- Re-export from working Metabase
- Check for version compatibility

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

**Solution**: Increase Docker memory in Docker Desktop settings

---

## Log Locations

### Finding Logs

| Component | Location |
|-----------|----------|
| Dango CLI | `.dango/logs/` |
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

```markdown
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
```

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

---

## Next Steps

- [Performance](performance.md) - Optimize slow operations
- [Backup & Restore](backup-restore.md) - Recovery procedures
- [Community](../community/index.md) - Get help
