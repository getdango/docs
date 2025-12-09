# Git Best Practices

Version control strategies for Dango data projects.

---

## Overview

Using Git with Dango projects requires care:
- Some files should be committed (configs, models)
- Some files must never be committed (secrets, data)
- Team collaboration needs clear conventions

---

## What to Commit

### Always Commit

| File/Directory | Reason |
|---------------|--------|
| `.dango/sources.yml` | Source configurations |
| `.dango/project.yml` | Project settings |
| `dbt/` | Transformation models |
| `.dlt/config.toml` | dlt settings (no secrets) |
| `metabase_export.json` | Dashboard definitions |

### Project Files

```bash
# Always commit
git add .dango/sources.yml
git add .dango/project.yml
git add dbt/
git add .dlt/config.toml
git add metabase_export.json
```

---

## What NOT to Commit

### Never Commit

| File/Directory | Reason |
|---------------|--------|
| `.dlt/secrets.toml` | Credentials and API keys |
| `data/` | Raw data files and database |
| `metabase-data/` | Metabase internal state |
| `.dango/logs/` | Log files |
| `dbt/target/` | Compiled dbt artifacts |
| `dbt/logs/` | dbt logs |

### Gitignore Template

Create a comprehensive `.gitignore`:

```gitignore
# .gitignore for Dango projects

# === CREDENTIALS (CRITICAL - NEVER COMMIT) ===
.dlt/secrets.toml
*.env
.env*
credentials.json
*_credentials.json
service_account.json

# === DATA FILES ===
data/
*.duckdb
*.duckdb.wal
*.parquet
*.csv

# === METABASE ===
metabase-data/
metabase.db/

# === LOGS ===
*.log
.dango/logs/
dbt/logs/

# === COMPILED/GENERATED ===
dbt/target/
dbt/dbt_packages/
__pycache__/
*.pyc
.pytest_cache/

# === IDE/EDITOR ===
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# === BACKUPS ===
backups/
*.backup
*.bak

# === TEMPORARY ===
*.tmp
.temp/
```

---

## Repository Structure

### Recommended Layout

```
my-analytics/
├── .gitignore              # MUST HAVE
├── README.md               # Project documentation
├── .dango/
│   ├── sources.yml         # ✅ Commit
│   └── project.yml         # ✅ Commit
├── .dlt/
│   ├── config.toml         # ✅ Commit
│   └── secrets.toml        # ❌ DO NOT COMMIT
├── dbt/                    # ✅ Commit entire directory
│   ├── models/
│   ├── macros/
│   ├── tests/
│   └── dbt_project.yml
├── data/                   # ❌ DO NOT COMMIT
└── metabase_export.json    # ✅ Commit
```

### Initial Setup

```bash
# Initialize git
git init

# Add .gitignore FIRST
cp /path/to/template/.gitignore .
git add .gitignore
git commit -m "Add .gitignore"

# Then add project files
git add .dango/sources.yml .dango/project.yml
git add .dlt/config.toml
git add dbt/
git add README.md
git commit -m "Initial project setup"
```

---

## Credential Management

### Store Credentials Safely

**Option 1: Environment Variables**

```bash
# Set in shell profile (~/.bashrc, ~/.zshrc)
export STRIPE_API_KEY="sk_live_xxx"
export GA_CLIENT_ID="xxx.apps.googleusercontent.com"
```

Reference in secrets.toml:
```toml
# .dlt/secrets.toml
[sources.stripe]
api_key = "${STRIPE_API_KEY}"
```

**Option 2: Secrets Template**

Create a template for team members:

```toml
# .dlt/secrets.toml.example (COMMIT THIS)
[sources.stripe]
api_key = "YOUR_STRIPE_API_KEY_HERE"

[sources.google]
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
```

**Option 3: External Secrets Manager**

For production, use tools like:
- HashiCorp Vault
- AWS Secrets Manager
- 1Password CLI

---

## Team Collaboration

### Branch Strategy

```
main
├── feature/add-stripe-source
├── feature/revenue-dashboard
└── fix/ga4-sync-issue
```

### Branching Workflow

```bash
# Start new feature
git checkout main
git pull origin main
git checkout -b feature/add-stripe-source

# Make changes
dango source add stripe
git add .dango/sources.yml
git commit -m "Add Stripe data source"

# Push and create PR
git push -u origin feature/add-stripe-source
```

### Pull Request Checklist

Before merging:
- [ ] No secrets in diff
- [ ] sources.yml changes reviewed
- [ ] dbt models tested locally
- [ ] metabase_export.json updated if dashboards changed

---

## Handling Conflicts

### sources.yml Conflicts

```yaml
# When merging, sources.yml may conflict
# Resolution: Keep all sources, ensure no duplicates

sources:
<<<<<<< HEAD
  - name: stripe_payments
    type: stripe
=======
  - name: google_analytics
    type: google_analytics
>>>>>>> feature/add-ga4

# Resolution: Include both
sources:
  - name: stripe_payments
    type: stripe
  - name: google_analytics
    type: google_analytics
```

### dbt Model Conflicts

For SQL model conflicts:
1. Review both versions
2. Keep the correct business logic
3. Test after resolution: `cd dbt && dbt run`

---

## Synchronizing Environments

### Developer Onboarding

```bash
# 1. Clone repository
git clone https://github.com/company/analytics.git
cd analytics

# 2. Create secrets file
cp .dlt/secrets.toml.example .dlt/secrets.toml
# Edit with your credentials

# 3. Initialize Dango
dango start

# 4. Sync data
dango sync

# 5. Run transformations
dango run

# 6. Restore dashboards
dango metabase load --file metabase_export.json
```

### Keeping Dashboards in Sync

```bash
# After changing dashboards, export and commit
dango metabase save
git add metabase_export.json
git commit -m "Update revenue dashboard"
git push

# Other team members pull and load
git pull
dango metabase load --file metabase_export.json
```

---

## Commit Messages

### Convention

```
<type>: <short description>

<detailed description if needed>
```

**Types**:
- `feat`: New source, model, or dashboard
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation changes
- `chore`: Maintenance tasks

### Examples

```bash
git commit -m "feat: add Stripe payment source"
git commit -m "fix: correct revenue calculation in fct_daily_revenue"
git commit -m "refactor: reorganize staging models by source"
git commit -m "docs: update README with setup instructions"
```

---

## Advanced: Separate Repos

For larger teams, consider splitting:

```
company-analytics/           # Main repo
├── configs/                # sources.yml, project.yml
└── dbt/                    # Models

company-analytics-dashboards/  # Separate repo
└── metabase_export.json     # Dashboard definitions
```

Benefits:
- Different access controls
- Dashboard changes don't require model review
- Cleaner history

---

## Verification Commands

```bash
# Check for accidentally committed secrets
git log --all --full-history -- "*.toml" | head -20

# Search for potential secrets in history
git log -p --all -S 'api_key' -- "*.yml" "*.toml"

# Verify .gitignore is working
git status --ignored

# List all tracked files
git ls-files
```

---

## Next Steps

- [Local Development](local-development.md) - Development workflow
- [Backup & Restore](backup-restore.md) - Data protection
- [Security Best Practices](../security/best-practices.md) - Credential security
