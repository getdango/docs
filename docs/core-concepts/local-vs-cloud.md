# Local vs Cloud

Dango is designed as a **local-first** platform. You develop and test locally, then optionally deploy to the cloud for team access and scheduled syncs. Both modes use the same codebase and configuration, but several behaviors differ based on where Dango is running.

This page covers the key differences so you know what to expect in each environment.

## Comparison

| Feature | Local | Cloud |
|---------|-------|-------|
| **Start command** | `dango start` | `dango deploy` + `dango remote push` |
| **Authentication** | Enabled (can disable) | Required (always enabled) |
| **Session idle timeout** | 24 hours (default) | 60 minutes (recommended) |
| **Session max lifetime** | 365 days (default) | 30 days (recommended) |
| **Web server** | Uvicorn (single worker) | Uvicorn (multi-worker) behind Caddy |
| **HTTPS** | No (localhost only) | Yes (auto-TLS via Let's Encrypt) |
| **File watcher** | Yes (auto-sync on file changes) | No |
| **Notebook idle timeout** | 2 hours | 1 hour |
| **Backups** | Manual (`dango snapshot db`) | DigitalOcean Spaces (automated) |
| **Metabase access** | Web UI (localhost:8800) or direct (localhost:3000) | Via Caddy reverse proxy with auth |

## Authentication

=== "Local"

    Authentication is **enabled by default** but can be disabled if you're the only user:

    ```bash
    dango auth disable
    ```

    When enabled, `dango init` prompts you to set an admin password. Local sessions use relaxed timeouts suitable for solo development.

=== "Cloud"

    Authentication is **always required** and cannot be disabled. Cloud deployments log warnings at startup if your session settings are too permissive:

    - Idle timeout above 60 minutes
    - Max session lifetime above 30 days
    - Two-factor authentication not enabled

    These are warnings, not enforced limits &mdash; you can set any values you want, but tighter settings are strongly recommended for cloud deployments accessible over the internet.

## Session Timeouts

The default session settings are designed for local development:

| Setting | Default | Cloud Recommendation |
|---------|---------|---------------------|
| `idle_timeout_minutes` | 1440 (24 hours) | 60 minutes or less |
| `session_max_days` | 365 days | 30 days or less |
| `require_2fa` | `false` | `true` |

You can change these in your authentication configuration. Cloud deployments will warn you at startup if the values exceed the recommended thresholds, but won't prevent you from using them.

## Networking

=== "Local"

    Dango runs Uvicorn directly on `localhost:8800`. There is no HTTPS &mdash; traffic never leaves your machine.

    Access Metabase through the Web UI at `localhost:8800` (recommended — SSO bridge handles login automatically), or directly at `localhost:3000`.

=== "Cloud"

    Dango runs behind **Caddy**, which provides:

    - **Automatic HTTPS** via Let's Encrypt (if you configure a domain)
    - **Reverse proxy** routing to the Dango web server and Metabase
    - **Security headers** (HSTS, CSP, X-Frame-Options)

    Caddy handles TLS certificate provisioning and renewal automatically. If no domain is configured, the server is accessible via IP address over HTTP.

    Uvicorn runs with **multiple workers** in cloud mode. This means `app.state` is not shared across workers &mdash; the scheduler runs in only one worker (via the lifespan context), and WebSocket connections are per-worker.

## File Watcher

=== "Local"

    Dango watches your project directory for file changes (CSV, JSON, JSONL, NDJSON, Parquet files). When a file changes, Dango waits for a **10-minute debounce window** and then triggers an automatic sync followed by a dbt run.

    This is useful for local file sources &mdash; drop a CSV into your project and it gets ingested automatically.

=== "Cloud"

    The file watcher is **not available** on cloud deployments. Data syncs are triggered either manually (via the web UI or CLI) or on a schedule.

## Notebook Idle Timeout

Marimo notebook servers are automatically shut down after a period of inactivity to free resources.

=== "Local"

    Notebooks time out after **2 hours** of inactivity.

=== "Cloud"

    Notebooks time out after **1 hour** of inactivity. The shorter timeout conserves server resources on shared cloud deployments.

The idle check runs every 5 minutes. When a notebook times out, any unsaved work in the notebook session is lost (the notebook file itself is preserved).

## Backups

=== "Local"

    Backups are manual. Use `dango snapshot db` to create a copy of your DuckDB warehouse file:

    ```bash
    dango snapshot db
    ```

    Snapshots are saved to `.dango/snapshots/`.

=== "Cloud"

    Cloud deployments can use **automated backups** to DigitalOcean Spaces (S3-compatible object storage):

    ```bash
    dango remote backup enable
    dango remote backup list
    dango remote backup download <backup-id>
    dango remote backup restore <backup-id>
    ```

    Backups include the DuckDB warehouse, configuration files, and dbt project files.

## Deploy Model

=== "Local"

    Start Dango directly:

    ```bash
    dango start
    ```

    This launches the web server, Metabase (via Docker), and optionally the file watcher and scheduler. Everything runs on your machine.

=== "Cloud"

    Cloud deployment is a two-step process:

    1. **Deploy** the server infrastructure:

        ```bash
        dango deploy              # DigitalOcean guided wizard
        dango deploy --byos       # Bring your own server
        ```

    2. **Push** your local configuration and dbt files to the server:

        ```bash
        dango remote push
        ```

    Subsequent changes are pushed with `dango remote push`. Credentials are **not** synced with push &mdash; manage them separately via the web UI secrets page or `dango remote env set`.

??? info "What gets pushed"
    `dango remote push` syncs configuration files (`.dango/*.yml`), dbt project files, `docker-compose.yml`, `Dockerfile.metabase`, and `entrypoint.sh`. It does **not** sync `.env`, `.dlt/secrets.toml`, or the DuckDB warehouse file.

## Cloud Detection

Dango determines whether it's running in cloud mode by checking for `.dango/cloud.yml` with a `droplet_ip` value. If this file exists and contains a server IP, cloud-specific behaviors activate (stricter security warnings, shorter notebook timeouts, multi-worker uvicorn).

## Key Points

- **Local-first** means you develop locally, then deploy to cloud &mdash; not that Dango is local-only
- Authentication defaults are relaxed for local development; cloud deployments should tighten them
- Cloud uses **Caddy** for HTTPS and reverse proxying; local runs Uvicorn directly
- The **file watcher** (auto-sync on file changes) is local-only
- Notebook idle timeouts are **2 hours** locally, **1 hour** on cloud
- `dango remote push` syncs config and code but **never credentials**

## Related

- [DuckDB & Single-Writer](duckdb.md) &mdash; how the database lock works in both modes
- [Architecture](architecture.md) &mdash; system components and how they interact
- [Deployment](../deployment/index.md) &mdash; step-by-step cloud deployment guides
- [Authentication](../security/authentication.md) &mdash; configuring auth for your environment
- [Scheduled Syncs](../scheduling-monitoring/scheduled-syncs.md) &mdash; automating data syncs (replaces file watcher on cloud)
