# Changelog

Version history and release notes for Dango.

---

## Version Numbering

Dango follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

---

## Current Version

### v1.0.0

*Released: June 2026*

**Status**: First major release

This is the v1.0.0 release — a complete rewrite and expansion of the Dango platform, adding authentication, cloud deployment, a web UI, scheduled syncs, data governance, and notebooks.

#### Highlights

- **33 data sources** (up from 8 wizard-supported in v0.1.0), with 25 in the interactive wizard
- **Authentication** — password login, TOTP 2FA, API keys, three roles (admin/editor/viewer)
- **Cloud deployment** — automated DigitalOcean provisioning and Bring Your Own Server (BYOS) support
- **Web UI** — 16-page dashboard for monitoring syncs, health, data catalog, schedules, and secrets
- **Scheduled syncs** — APScheduler-based with cron expressions and webhook notifications
- **Data governance** — schema drift detection, PII scanning (Presidio), data catalog with column descriptions
- **Marimo notebooks** — integrated reactive notebooks with DuckDB snapshot isolation
- **Monitoring** — health metrics, sync history, capacity alerts
- **`dango dev` workflow** — branch-based dbt development with isolated databases
- **Snapshots** — SCD Type 2 change tracking via dbt snapshots, plus DuckDB point-in-time copies
- **Metabase SSO bridge** — automatic login through the Web UI

#### What's New by Area

**Authentication & Security (Phase 2)**

- Password authentication with bcrypt hashing
- TOTP-based two-factor authentication
- API key authentication for programmatic access
- Three user roles: admin, editor, viewer (29 permissions)
- Metabase SSO bridge — seamless login through Web UI
- Audit logging for security events
- Credential encryption for OAuth tokens

**Cloud Deployment (Phase 3)**

- `dango deploy` — automated DigitalOcean droplet provisioning
- BYOS (Bring Your Own Server) — deploy to any Ubuntu 22.04 server via SSH
- Caddy reverse proxy with automatic HTTPS (Let's Encrypt)
- Security hardening: fail2ban, SSH key-only, unattended-upgrades
- `dango remote push` — sync config and dbt models to server
- `dango remote logs`, `dango remote status`, `dango remote history`
- Deploy journal (append-only JSONL) with git guardrails

**Data Governance (Phase 4)**

- Schema drift detection — alerts when source schemas change
- PII scanning via Microsoft Presidio (targeted entity types)
- Data catalog — browsable table/column inventory
- Column descriptions (user-editable via Web UI)
- Monitor configuration via CLI and Web UI

**Scheduling (Phase 5)**

- APScheduler-based sync scheduling with cron expressions
- `dango schedule add/remove/list/enable/disable`
- Webhook notifications on sync success, failure, or stale data
- Configurable stale data thresholds
- Misfire grace handling for missed schedules

**Notebooks (Phase 6)**

- Marimo notebook integration
- Built-in templates (EDA, time series, funnel analysis, cohort analysis)
- DuckDB snapshot isolation — notebooks use read-only copies
- Launch from Web UI or CLI (`dango notebook open`)

**Web UI (Phase 7)**

- 16-page web dashboard at `http://localhost:8800`
- Dashboard page — sync status overview, health summary
- Sources page — source list, sync history, run syncs
- Models page — dbt model status, run transformations
- Health & Logs page — system health, disk usage, process status
- Catalog page — data catalog browser with search
- Monitoring page — schema drift, PII results, metrics
- Schedules page — manage sync schedules
- Notebooks page — launch and manage Marimo notebooks
- Secrets & Admin page — credential management, user administration

**CLI Additions**

- `dango init` — project initialization with admin password setup
- `dango deploy` / `dango remote push` — cloud deployment
- `dango auth` — user management (create, list, delete, reset-password)
- `dango oauth` — OAuth provider management
- `dango schedule` — sync scheduling
- `dango monitor` — monitoring and governance
- `dango notebook` — notebook management
- `dango dev` — branch-based dbt development
- `dango snapshot` — SCD Type 2 snapshots and DuckDB copies
- `dango upgrade` — in-place version upgrades with migrations
- `dango schedule webhook` — webhook notification management
- `dango config validate` — configuration validation

**Infrastructure**

- DuckDB version alignment checks (startup + pre-commit hook)
- Process separation — syncs run in subprocesses to prevent lock contention
- Single-worker uvicorn for cloud deployments (WebSocket compatibility)
- Smoke test suite (100+ checks)

#### Breaking Changes from v0.1.0

- `dango init` is now required before first use (sets up auth)
- Authentication is enabled by default (use `DANGO_ADMIN_PASSWORD` env var for automation)
- `dango sync --source SOURCE` syntax deprecated — use `dango sync SOURCE` (positional argument)
- Metabase credentials now randomly generated and stored in `.dango/metabase.yml`
- Project structure uses `.dango/` directory for configuration (migrated automatically)

---

## Previous Releases

### v0.1.0

*Released: December 17, 2025*

**Status**: MVP Release

- 8 wizard-supported data sources (CSV, Stripe, Google Sheets, GA4, Facebook Ads, Google Ads, REST API, dlt Native)
- 25+ additional sources via dlt native configuration
- Auto-generated dbt staging models
- DuckDB warehouse with incremental loading
- Metabase integration with auto-provisioned dashboards
- Dashboard export/import (`dango metabase save/load`)
- Web UI for monitoring
- OAuth authentication for Google and Facebook sources

### v0.0.5

*Released: December 8, 2025*

- `dango sync --dry-run` to preview without executing
- Unreferenced custom sources warning
- Better validation output (database check, model count)

---

## Upgrade Guide

### Upgrading to v1.0.0

```bash
# Upgrade the package
dango upgrade

# Initialize auth (required for v1)
dango init
```

After upgrading:

1. Set an admin password during `dango init`
2. Review your sources — the config format is unchanged, but new features are available
3. Access the Web UI at `http://localhost:8800` after running `dango start`

### General Upgrade

```bash
# Upgrade to latest
dango upgrade

# Or with pip directly
pip install --upgrade getdango
```

---

## Release Process

### How Releases Work

1. Features developed on feature branches off `v1`
2. Merged to `v1` after review
3. Tagged releases published to PyPI
4. Release notes added to this changelog

### Release Cadence

- **Patch releases**: As needed for bug fixes
- **Minor releases**: As features complete
- **Major releases**: When breaking changes are necessary

---

## Post-v1 Roadmap

Planned for future releases:

- Query performance logging and optimization insights
- Health history — 24h/7d trend dashboards
- Python task scheduler / reverse ETL
- REST API provider presets (Shopify, Stripe templates)
- OAuth callback unification
- DuckLake integration (pending maturity evaluation)

---

## Contributing

Want to contribute to the next release?

- [Report bugs](https://github.com/getdango/dango/issues/new)
- [Suggest features](https://github.com/getdango/dango/discussions)
- [Submit pull requests](https://github.com/getdango/dango/pulls)

See the [Contributing Guide](https://github.com/getdango/docs/blob/main/CONTRIBUTING.md) for details.

---

## Links

- [GitHub Releases](https://github.com/getdango/dango/releases)
- [PyPI Package](https://pypi.org/project/getdango/)
- [GitHub Issues](https://github.com/getdango/dango/issues)
