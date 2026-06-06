# Upgrade Notes: v1.0.0b6

What changed since b3, what breaks, and how to upgrade. If you already upgraded to b4, these breaking changes were already handled — you can upgrade to b6 with just `pip install --upgrade --pre getdango` and `dango start`.

---

## Breaking Changes (from b3)

These require action if upgrading directly from b3:

### 1. GA4 Column Names Changed

Column names no longer include type suffixes:

| Before (b3) | After (b4+) |
|---|---|
| `sessions_integer` | `sessions` |
| `bounce_rate_float` | `bounce_rate` |
| `total_users_integer` | `total_users` |
| `new_users_integer` | `new_users` |
| `screen_page_views_integer` | `screen_page_views` |

**Action required:** Update any custom dbt models that reference old column names.

### 2. Google Ads / GA4 Data Types Fixed

| Column | Before (b3) | After (b4+) |
|---|---|---|
| `date` (Google Ads) | VARCHAR | DATE |
| `date` (GA4) | TIMESTAMPTZ | DATE |
| `clicks`, `impressions` (Google Ads) | VARCHAR | INTEGER |

**Action required:** Run a full refresh for each affected source:

```bash
dango sync <your_google_ads_source> --full-refresh
dango sync <your_ga4_source> --full-refresh
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

# 3. Full refresh affected sources (if upgrading from b3)
dango sync <google_ads_source> --full-refresh
dango sync <ga4_source> --full-refresh

# 4. Update custom dbt models referencing old GA4 column names

# 5. Verify dbt models compile
dango run
```

---

## What Works Automatically After Upgrade

No action needed for these — they just work after upgrading:

- **Scheduler** loads jobs from `schedules.yml` on startup (was broken in b3)
- **Staging YML** files (`sources_*.yml`) are no longer overwritten on sync — user edits preserved
- **Cloud file sync** now includes `custom_sources/` and `seeds/` directories
- **Backups** now include dbt models, custom sources, and `.env`
- **Metabase dashboard export** captures all cards (was exporting 0 in some cases)
- **Sync failures** properly logged as errors with status in sync history
- **OAuth refresh** argument changed from credential name to source type (e.g., `dango oauth refresh google_sheets`)

---

## Cloud Deployments

After upgrading locally:

```bash
# 1. Push updated project files to the server
dango remote push

# 2. SSH in and upgrade the Dango package
dango remote ssh
# On server:
cd /srv/dango/project
source venv/bin/activate
pip install --upgrade --pre getdango
dango start

# 3. Full refresh affected sources (if upgrading from b3)
dango sync <google_ads_source> --full-refresh
dango sync <ga4_source> --full-refresh
```
