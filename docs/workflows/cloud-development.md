# Cloud Development Workflow

How to develop and deploy dbt model changes when your data lives on a cloud server.

---

## Overview

The typical workflow for iterating on dbt models with a cloud deployment:

1. **Edit** dbt models locally (`dbt/models/`)
2. **Validate** syntax and configuration (`dango validate`)
3. **Test** against local data if available (`dango dev`)
4. **Commit** and push changes (`git commit && git push`)
5. **Deploy** to cloud (`dango remote push`)
6. **Verify** results on cloud (`dango remote query`)

---

## Step-by-Step

### 1. Edit dbt Models Locally

Make changes to your dbt models in the `dbt/models/` directory. Use your preferred editor.

### 2. Validate Before Deploying

`dango validate` catches syntax errors, missing refs, invalid YAML, and configuration issues — all without needing data:

```bash
dango validate
```

This runs dbt's `parse` phase, which catches most SQL and configuration errors before they reach your cloud server.

### 3. Test Locally with `dango dev`

If you have local data (from running `dango sync` locally), use dev mode for safe testing:

```bash
# Run dbt against a copy of your local database
dango dev

# Compare row counts between dev and production
dango dev --diff
```

Dev mode creates a copy of `data/warehouse.duckdb` and runs transformations against it, leaving your production data untouched.

### 4. Deploy to Cloud

After committing your changes:

```bash
git add dbt/models/
git commit -m "Add monthly revenue model"
dango remote push
```

`dango remote push` syncs your project files (including dbt models) to the cloud server and re-runs dbt. Ensure you're on the deploy branch configured in `.dango/cloud.yml` (default: `main`), or use `--allow-branch` to deploy from a different branch.

### 5. Verify on Cloud

Spot-check your results directly:

```bash
# Quick row count
dango remote query "SELECT count(*) FROM marts.fct_monthly_revenue"

# Sample data
dango remote query "SELECT * FROM marts.fct_monthly_revenue LIMIT 10"
```

---

## Known Limitation: Cloud-Only Data

If your data only exists on the cloud (you haven't synced sources locally), you can't fully test dbt model changes before deploying. `dango validate` catches syntax errors but not logic errors — for example, it won't catch a `WHERE` clause that filters out all rows.

**Workarounds:**

- **Sync sources locally too.** Even a small date range gives you data to test against:
    ```bash
    dango sync my_source --since 2026-01-01
    ```
- **Push and verify.** Deploy the change to cloud, then use `dango remote query` to check results. If something is wrong, fix and redeploy.
- **Use `dango dev` on cloud data.** Download a backup locally, then test against real data:
    ```bash
    # List available backups, then download one
    dango remote backup list
    dango remote backup download backup-20260224-143000.tar.gz
    # Restore the backup locally, then use dango dev
    ```

---

## Best Practices

- **Always run `dango validate` before pushing.** It's fast and catches the most common errors.
- **Use `dango dev` on a git branch** for safe local testing without affecting production data.
- **Keep a local sync for development** — even if cloud is your primary environment. Having local data makes iteration much faster.
- **Use `dango remote query` to spot-check** results after every deploy rather than waiting for dashboards to refresh.

---

## Related

- [Local Development](local-development.md) — local project workflows
- [Dev Workflow](../transformations/dev-workflow.md) — `dango dev` details
- [Remote Management](../deployment/remote-management.md) — cloud management commands
- [Troubleshooting](troubleshooting.md) — common issues and solutions
