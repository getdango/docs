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

### v1.0.7

*Released: August 27, 2026*

**Status**: Stable

#### Added

- `dango doctor` — credential health check across all configured sources; shows ✓ OK / ✗ Missing / Expired / Unknown at a glance
- Model wizard — interactive upstream table selection with CTE scaffold auto-generation; each selected table becomes a named CTE with `{{ ref(...) }}`
- Schedule wizard — weekday preset (Mon–Fri pre-selected) in `dango schedule add`; `dango schedule reload` applies config changes without restart
- Service account auth — `dango oauth google_sheets` and `dango oauth google_analytics` offer a choice between browser OAuth and JSON key file, useful for server deployments
- Script UI history — scheduled script runs now appear in the Scripts page with last run timestamp, status, and View Log link (previously always showed "not run")
- Script failure history — cancelled, timed-out, and pre-launch-failed script runs write history entries so failures are visible in the UI
- Secrets page partial masking — env var values show the last 4 characters (`****efgh`) instead of blanket `***`
- Metabase Collection hierarchy — nested collections preserved correctly across `dango metabase save` / `dango metabase load` roundtrips
- Column descriptions — default descriptions for columns in 7 high-value sources (Google Ads, GA4, Google Sheets, Stripe, HubSpot, Facebook Ads, BigQuery) visible in the catalog
- Notebook role access — editor role can open notebooks not created by them
- Scripts cloud sync — scripts and `scripts/requirements.txt` synced to remote server on `dango remote push`; invalid script paths rejected with a clear error

#### Fixed

- Scripts page: scheduled runs no longer permanently show "not run" — history file written after every scheduled execution
- Scripts page: View Log no longer 404s on scheduled runs — log files written to the correct path
- Secrets page: duplicate `/settings/variables` page removed; env vars consolidated into `/settings/secrets`; old URL redirects (301) automatically
- DuckDB lock conflicts on local: syncs now retry up to 5 times with 10s backoff when Metabase holds the DuckDB connection (previously failed immediately)
- Schedule reload: source-list changes now detected and applied; previously `dango schedule reload` only compared cron triggers
- Google Sheets: empty range now raises a clear error instead of silently bypassing empty-replace protection
- Service account validation: no longer returns valid when `google-auth` package is not installed
- Model wizard: duplicate CTE alias no longer generated when two upstream table names produce the same identifier
- Sort/filter UI: broken on Schedules, Scripts, and Catalog pages after a JS refactor — now fixed
- `InquirerPy` added to declared package dependencies — `dango oauth google_sheets` / `dango oauth google_analytics` no longer crash on fresh installs

#### Security

- PostCSS updated 8.5.10 → 8.5.26, resolving path traversal vulnerabilities in the CSS build toolchain (build-time only; not exploitable at runtime)

---

### v1.0.6

*Released: August 19, 2026*

**Status**: Stable — quality gate round

#### Added

- Script scheduling — cron-based scheduling for Python scripts in `scripts/` via `dango schedule add`
- Scripts tab in web UI — list, run, cancel, and view logs for scripts
- `dango transform seed` — runs dbt seeds; seed tables appear in catalog with row counts and profiling
- Python 3.13 support
- Schedule-aware staleness detection — sources with a schedule show a yellow "Stale" badge when last sync exceeds 2× the schedule interval
- Per-table empty-replace protection for multi-resource dlt sources
- Source and model row counts in web UI and catalog
- Configurable backup retention, secrets exclusion from backups
- Activity log deduplication and sync history gap prevention
- `dlt` upgraded from 1.24.0 to 1.28.1

#### Fixed

- Custom `dlt_native` sources in `custom_sources/` now auto-discovered without manual config
- Sources page crash when a dlt_native source has a `null` incremental capability
- `@dlt.source` decorator crash during import inspection
- "Incremental" sync mode label now derived from actual write_disposition in DuckDB
- Models page: "Run" button no longer overwrites Schema column
- Models page: "Last Run" column now sortable
- Catalog: tab navigation no longer freezes when viewing tables filtered by source
- Catalog: dbt docs 📖 link opens in new tab
- DbtLock scope narrowed to write phase — long-running API syncs no longer block concurrent sources
- DbtLock unlink race condition fixed
- Metabase kept running during sync extract phase
- Scheduled sync lock timeout aligned with direct sync (60s → 300s)
- Notebook startup hang fixed; admin restart now shows warning modal
- Scheduled sync "Unknown sync completed" toast fixed
- Column alignment and filter inputs improved across Sources, Models, Schedules pages
- DuckDB 1.5.2 → 1.5.4, Metabase JDBC driver 1.5.1.0 → 1.5.3.0, dbt-core 1.10.20 → 1.10.22

---

### v1.0.5

*Released: June 25, 2026*

#### Added

- Sync queue — concurrent syncs wait instead of failing, with queued status in the web UI
- WebSocket sync phase events — UI shows "Processing..." during post-sync hooks
- Structured logging to `.dango/logs/dango.log` with daily rotation and gzip compression
- `dango_version` field in activity log, audit log, and sync subprocess headers
- Schedules page: sources displayed as alphabetically sorted bullet list
- OAuth timeout with 120s limit, retry option, and provider-specific troubleshooting

#### Fixed

- OAuth credentials saved only after token exchange succeeds
- Cross-project port kill — `dango stop` scoped to current project
- Staging models generate explicit column lists instead of `SELECT *`
- Sync log filenames include source name and timestamp
- Notebook startup waits indefinitely for marimo to respond

---

### v1.0.4

*Released: June 15, 2026*

#### Added

- Global sync status indicator in UI header
- Activity log entries for CSV uploads, deletes, and manual schedule triggers
- "View in Metabase" link in catalog table detail
- Empty sync protection — replace-mode syncs that return 0 rows preserve existing data
- `--allow-empty-replace` CLI flag to override empty sync protection

#### Fixed

- OAuth wizard shows success only after actual tokens obtained
- Duplicate `sync_started` event emission removed

---

### v1.0.3

*Released: June 2026*

#### Fixed

- Metabase session bridging stability improvements
- Schedule execution reliability fixes
- OAuth refresh handling for long-running deployments

---

### v1.0.2

*Released: June 2026*

#### Fixed

- Cloud deployment stability fixes
- Remote backup and restore improvements
- Firewall and domain management fixes

---

### v1.0.1

*Released: June 2026*

#### Fixed

- Background Metabase schema sync on startup
- Port conflict detection improvements
- Initial sync reliability fixes

---

### v1.0.0b4

*Released: June 2026*

**Status**: Beta 4 — bug fix round

See [Upgrade Notes for b4](../guides/upgrade-b4.md) for breaking changes and upgrade steps.

#### Breaking Changes

- **GA4 column names:** Type suffixes removed (`sessions_integer` → `sessions`, `bounce_rate_float` → `bounce_rate`, etc.). Update custom dbt models referencing old names.
- **Google Ads / GA4 data types:** `date` columns now DATE (were VARCHAR/TIMESTAMPTZ), `clicks`/`impressions` now INTEGER (were VARCHAR). Requires `--full-refresh` per source.
- **GA4 default queries:** `events` and `conversions` now include `landingPage` dimension.

#### Fixes

- Scheduler now loads jobs from `schedules.yml` on startup
- Staging YML files (`sources_*.yml`) no longer overwritten on sync
- Cloud file sync now includes `custom_sources/` and `seeds/`
- Backups now include dbt models, custom sources, and `.env`
- Metabase dashboard export captures all cards
- Sync failures properly logged as errors with status in sync history
- OAuth wizard error handling improvements
- `resolve_install_source()` correctly detects PyPI installs

---

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

1. Features developed on feature branches off `main`
2. Merged to `main` after review
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
