# Server Operations

Upgrade, resize, and migrate your cloud server.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote upgrade` | Upgrade Dango to a newer version |
| `dango remote power-on` | Power on a DigitalOcean server left off by an interrupted resize, then start services |
| `dango remote resize` | Resize the server (DigitalOcean only) |
| `dango remote migrate` | Migrate to a new server (DigitalOcean only) |

---

## Upgrading Dango

Upgrade the Dango installation on your server to a newer version:

```bash
dango remote upgrade
```

This upgrades to the latest version on PyPI. To install a specific version:

```bash
dango remote upgrade --version 1.2.3
```

### Upgrade Workflow

1. **Version check** &mdash; compares installed version with target version
2. **Pre-upgrade backup** &mdash; creates a full backup (unless `--skip-backup`)
3. **Stop services** &mdash; stops dango-web and Metabase
4. **Install** &mdash; runs `pip install getdango==<version>` in the server's venv
5. **Migrations** &mdash; applies any database migrations for the new version
6. **Docker rebuild** &mdash; rebuilds Metabase container if needed
7. **Start services** &mdash; restarts dango-web and Metabase
8. **Health check** &mdash; verifies the server is responding

If the installed version already matches the target, the upgrade still completes pending server setup, including the notebook WebSocket Caddyfile change.

### Upgrading to 1.0.14

- On existing servers, the Metabase DuckDB file-access restriction is applied at the next `dango start` or service restart. `dango remote upgrade` updates an existing notebook WebSocket route in the Caddyfile; if that migration cannot complete, review the upgrade warning and complete the indicated Caddyfile change. Downgrading to 1.0.13 or earlier leaves notebooks unable to connect through the protected route.
- If an upgrade is interrupted while services are stopped, a server-side guard attempts to restart `dango-web`. Re-run `dango remote upgrade` to finish any pending steps.
- A custom Metabase version needs an administrator-approved SHA-256 digest for the exact `MB_VERSION`. On an existing server, the first upgrade attempt installs the root-owned Compose helper and reports a missing pin before building. As root on the server, run `dango-compose pin-metabase VERSION SHA256`, using the exact version and the verified jar digest, then run `dango remote upgrade` again. It resumes setup even if the package is already at the target version. The pin is kept outside the service-account-writable project tree and must match the version being built.
- Fresh DigitalOcean and BYOS deployments with a custom `MB_VERSION` are refused before server setup because the required administrator pin cannot be installed through that flow. Deploy the default version, pin the custom jar as root, set the custom version, then run `dango remote push`.
- The default Metabase jar digest is pinned in Dango and matched across the publisher's download and container image; the publisher does not provide its own checksum. In Docker-group fallback mode, helper integrity controls do not cover every Metabase build path. Resolve the server's fallback warning before relying on those controls.
- A cloud upgrade or rebuild and a restart after backup do not recheck a driver jar already on the server. Verify its origin and replace a suspect jar before using those paths.

Existing local projects retain their old, unverified `Dockerfile.metabase` after a package-only upgrade. Re-initialize the project to get the digest-checked template; review local edits before doing so. A fresh or upgraded Python installation requires Python 3.11–3.13 and Pillow 13.0.0 or newer.

On the first successful start after upgrading, Dango repairs affected saved Metabase exports: it archives only duplicate collection paths proven empty and without children, and never deletes collections. Duplicates with content or unknown status stay active and are reported in `.dango/state/metabase_collection_repair.json`. Local users need to restart Dango after installing the new package for this repair to run.

### Options

| Option | Description |
|--------|-------------|
| `--version` | Specific version to install (e.g., `1.2.3`). Must match semantic versioning. Default: latest on PyPI |
| `--yes`, `-y` | Skip confirmation prompt |
| `--skip-backup` | Skip the pre-upgrade backup |

### Failed Upgrade

If the Metabase build reports a missing administrator pin, use the exact version and digest in the command above and retry the upgrade. If the Metabase DuckDB driver fails integrity verification, check the network and run `dango start` again; Dango downloads and verifies a replacement before starting Metabase. A manual jar replacement must match Dango's pinned checksum.

If the health check fails after an upgrade:

```bash
# Roll back to the pre-upgrade backup
dango remote rollback

# Check what went wrong
dango remote logs
```

### Installing from Git

For pre-release testing, install directly from a Git branch via SSH:

```bash
dango remote ssh
```

Then on the server:

```bash
cd /srv/dango
source venv/bin/activate
pip install git+https://github.com/getdango/dango.git@v1
```

!!! warning
    Installing from Git bypasses the normal upgrade workflow (no backup, no migrations, no health check). Only use this for testing. Run `dango remote upgrade` to return to a stable release.

---

## Resizing the Server

Change the server's CPU, RAM, and disk allocation.

=== "DigitalOcean"

    ### View Current Size and Available Tiers

    Run without arguments to see your current tier and available options:

    ```bash
    dango remote resize
    ```

    ```
    Current: Standard (s-2vcpu-4gb) — 2 vCPU, 4 GB RAM, 80 GB disk, $24/mo

    Available tiers:
    Tier          Slug            vCPUs  RAM    Disk    Price
    Standard      s-2vcpu-4gb     2      4 GB   80 GB   $24/mo
    Performance   s-4vcpu-8gb     4      8 GB   160 GB  $48/mo

    Run: dango remote resize <SIZE_SLUG>
    ```

    ### Resize

    ```bash
    dango remote resize s-4vcpu-8gb
    ```

    ```
    Resize plan:
      Current: Standard (s-2vcpu-4gb) — $24/mo
      New:     Performance (s-4vcpu-8gb) — $48/mo

    Proceed? [y/N]: y

    Resizing...
      ✓ Pre-resize backup created
      ✓ Powered off droplet
      ✓ Resize complete
      ✓ Powered on droplet
      ✓ dbt profiles.yml regenerated (threads=4, memory_limit=2GB)
      ✓ Health check passed

    Resize complete. New size: s-4vcpu-8gb
    ```

    **What happens:**

    1. Creates a pre-resize backup
    2. Powers off the droplet (1&ndash;3 minutes downtime)
    3. Resizes the droplet via the DigitalOcean API
    4. Powers on the droplet
    5. Regenerates `dbt/profiles.yml` to match the new hardware:
        - `threads` = number of vCPUs
        - `memory_limit` = RAM &divide; 4 (e.g., 8 GB RAM &rarr; `2GB` memory limit)
    6. Verifies health

    !!! note "Disk Never Shrinks"
        DigitalOcean does not support reducing disk size. If you resize from Performance (160 GB) to Standard, the disk stays at 160 GB. Only CPU and RAM change.

    | Option | Description |
    |--------|-------------|
    | `size` | Size slug (optional &mdash; omit to view current info) |
    | `--yes`, `-y` | Skip confirmation prompt |

=== "BYOS"

    Resize is not available for BYOS deployments. To change your server's resources, resize through your hosting provider's console, then update the dbt profile via SSH:

    ```bash
    dango remote ssh
    ```

    Then edit `/srv/dango/project/dbt/profiles.yml` to match your new hardware:

    - Set `threads` to the number of vCPUs
    - Set `memory_limit` to RAM &divide; 4 (e.g., 8 GB RAM &rarr; `2GB`)

    ```yaml
    # Example for a 4 vCPU / 8 GB RAM server
    my_project:
      target: dev
      outputs:
        dev:
          type: duckdb
          path: /srv/dango/project/data/warehouse.duckdb
          schema: main
          threads: 4
          settings:
            memory_limit: 2GB
            threads: 4
    ```

---

## Migrating to a New Server

Move your deployment to a new server with a different size or region.

=== "DigitalOcean"

    ```bash
    dango remote migrate --size s-4vcpu-8gb
    ```

    Optionally change region:

    ```bash
    dango remote migrate --size s-4vcpu-8gb --region fra1
    ```

    ### Migration Workflow

    1. **Backup** &mdash; creates a backup of the current server
    2. **Upload** &mdash; uploads backup to DigitalOcean Spaces
    3. **Provision** &mdash; creates a new droplet with the specified size and region
    4. **Setup** &mdash; installs Dango on the new server
    5. **Copy secrets** &mdash; transfers `.env` and credentials to the new server
    6. **Download** &mdash; downloads backup from Spaces to the new server
    7. **Restore** &mdash; restores data on the new server
    8. **Domain** &mdash; configures domain on the new server (if set)
    9. **Firewall** &mdash; sets up firewall rules on the new server
    10. **Health check** &mdash; verifies the new server is responding
    11. **Destroy old** &mdash; removes the old server after verification

    **Downtime:** 5&ndash;15 minutes depending on data size and network speed.

    ### Prerequisites

    - DigitalOcean Spaces must be configured (used for data transfer between servers)
    - Spaces credentials must be set in the remote `.env` (see [Environment Variables](environment-variables.md))

    !!! warning "DNS Update Required"
        If you have a custom domain configured, you must update the DNS A record to point to the new server's IP address after migration completes. Dango will remind you of this.

    | Option | Description |
    |--------|-------------|
    | `--size` | Size slug for the new server (required) |
    | `--region` | Region slug for the new server (default: same as current) |
    | `--yes`, `-y` | Skip confirmation prompt |

=== "BYOS"

    Migration is not available for BYOS deployments. To migrate manually:

    1. Download a backup: `dango remote backup download <NAME>`
    2. Set up Dango on the new server following the [BYOS guide](byos.md)
    3. Copy the backup to the new server and restore

---

## Troubleshooting

### Upgrade health check failed

After a failed upgrade, the server may not be responding:

```bash
# Check logs for errors
dango remote logs

# Roll back to pre-upgrade state
dango remote rollback

# If rollback also fails, SSH in directly
dango remote ssh
sudo systemctl restart dango-web
sudo docker compose -f /srv/dango/project/docker-compose.yml up -d
```

### Resize timeout

If the droplet takes too long to power back on after resize:

1. Check the DigitalOcean console for droplet status
2. Try powering on manually from the DO console
3. Once running, verify health: `dango remote status`

### Migration Spaces error

```
Error: Spaces not configured
```

Migration requires DigitalOcean Spaces for data transfer. Set up credentials:

```bash
dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
dango remote env set SPACES_REGION=nyc3
dango remote env set SPACES_BUCKET=my-dango-backups
```

### Disk space warning

If `dango remote status` shows high disk usage:

- Remove old dlt pipeline state: `dango remote ssh` &rarr; `rm -rf /srv/dango/project/.dlt/pipelines/*/`
- Consider [resizing](#resizing-the-server) to a larger disk
- Download and remove old backups: `dango remote ssh` &rarr; check `/srv/dango/backups/deploy/`

### pip install failed on server

If `pip install` fails during upgrade (e.g., dependency conflict):

```bash
dango remote ssh
cd /srv/dango && source venv/bin/activate
pip install getdango==<version> --force-reinstall
```

If the venv is corrupted, recreate it:

```bash
rm -rf /srv/dango/venv
python3 -m venv /srv/dango/venv
source /srv/dango/venv/bin/activate
pip install getdango==<version>
```

Then restart services:

```bash
sudo systemctl restart dango-web
```

---

## Next Steps

- [Backups](backups.md) &mdash; configure automated backups
- [Remote Management](remote-management.md) &mdash; push changes and manage the server
- [Destroy & Cleanup](destroy.md) &mdash; tear down a deployment
