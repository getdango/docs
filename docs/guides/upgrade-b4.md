# Upgrade Notes: v1.0.0b4

What changed in b4, what breaks, and how to upgrade.

---

## Breaking Changes

These require action after upgrading:

### 1. GA4 Column Names Changed

Column names no longer include type suffixes:

| Before (b3) | After (b4) |
|---|---|
| `sessions_integer` | `sessions` |
| `bounce_rate_float` | `bounce_rate` |
| `total_users_integer` | `total_users` |
| `new_users_integer` | `new_users` |
| `screen_page_views_integer` | `screen_page_views` |

**Action required:** Update any custom dbt models that reference old column names.

### 2. Google Ads / GA4 Data Types Fixed

| Column | Before (b3) | After (b4) |
|---|---|---|
| `date` (Google Ads) | VARCHAR | DATE |
| `date` (GA4) | TIMESTAMPTZ | DATE |
| `clicks`, `impressions` (Google Ads) | VARCHAR | INTEGER |

**Action required:** Run a full refresh for each affected source:

```bash
dango sync --full-refresh --source <your_google_ads_source>
dango sync --full-refresh --source <your_ga4_source>
```

### 3. GA4 Default Queries Updated

The `events` and `conversions` queries now include the `landingPage` dimension.

**Action (existing projects only):** If you want the new dimension, edit `.dango/sources.yml` for your GA4 source to add `landingPage` to the dimensions list, then run `--full-refresh`. New projects get this automatically.

---

## Upgrade Steps

```bash
# 1. Upgrade the package
pip install --upgrade --pre getdango

# 2. Start Dango (auto-runs database migrations)
dango start

# 3. Full refresh affected sources
dango sync --full-refresh --source <google_ads_source>
dango sync --full-refresh --source <ga4_source>

# 4. Update custom dbt models referencing old GA4 column names

# 5. Verify dbt models compile
dango run

# 6. Check .gitignore — add any missing entries (see below)
```

---

## What Works Automatically After Upgrade

No action needed for these fixes:

- **Scheduler** now loads jobs from `schedules.yml` on startup (was broken in b3)
- **Staging YML** files (`sources_*.yml`) are no longer overwritten on sync — user edits are preserved
- **Cloud file sync** now includes `custom_sources/` and `seeds/` directories
- **Backups** now include dbt models, custom sources, and `.env`
- **Metabase dashboard export** now captures all cards (was exporting 0 in some cases)
- **Sync failures** now properly logged as errors with status recorded in sync history

---

## .gitignore Updates

b4 adds entries that may be missing from existing projects. Compare your `.gitignore` against the current template:

```gitignore
# Add these if missing
.dango/state/
.dango/logs/
.dango/scheduler.db
.dango/auth.db
data/
metabase-data/
.dlt/pipelines/
__pycache__/
*.pyc
venv/
.env
```

---

## Cloud Deployments

After upgrading locally:

```bash
# Push updated code to server
dango remote push

# Full refresh on server (via remote sync)
dango remote ssh
# On server:
cd /srv/dango/project
source venv/bin/activate
dango sync --full-refresh --source <google_ads_source>
dango sync --full-refresh --source <ga4_source>
```
