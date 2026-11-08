# Server Operations

Upgrade and resize your cloud server. Moving to a new server is a manual procedure in 1.0.14 (see [Moving to a New Server](#moving-to-a-new-server)).

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote upgrade` | Upgrade Dango to a newer version |
| `dango remote power-on` | Power on a DigitalOcean server left off by an interrupted resize, then start services |
| `dango remote resize` | Resize the server (DigitalOcean only) |
| `dango remote migrate` | Switched off in 1.0.14: refuses and prints the manual steps (see [Moving to a New Server](#moving-to-a-new-server)) |
| `dango remote isolation status\|disable\|enable` | Inspect, opt out of, or restore script and notebook isolation |

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

!!! warning "Upgrade your local Dango first"
    Run `pip install -U getdango` (or `dango upgrade`) on your own machine before `dango remote upgrade`. The upgrade is driven by the local client, and a client older than the target cannot perform every 1.0.14 step (for example, installing the Python interpreter a 22.04 server needs). The command prints a notice when your local version is older than the target.

### Upgrade Workflow

1. **Version check**: compares installed version with target version
2. **Checks before anything changes**: refuses (the installed Dango keeps running) if a custom Metabase version has no administrator pin, or if no Python 3.11&ndash;3.13 can be provided for the server venv (see below)
3. **Venv rebuild (when needed)**: a venv that is not root-owned, or whose Python is too old, is rebuilt first; if that fails the old venv is kept and the upgrade stops
4. **Pre-upgrade backup**: creates a full backup (unless `--skip-backup`)
5. **Stop services**: stops dango-web and Metabase
6. **Install**: runs `pip install getdango==<version>` in the server's venv
7. **Migrations**: applies any database migrations for the new version
8. **Server setup**: root-owned runtime, Compose helper, restricted script and notebook users, Caddyfile WebSocket route
9. **Docker rebuild**: rebuilds Metabase container if needed
10. **Start services**: restarts dango-web and Metabase
11. **Health check**: verifies the server is responding

If the installed version already matches the target, the upgrade still completes pending server setup, including the notebook WebSocket Caddyfile change.

### Upgrading to 1.0.14

- **Python on the server.** Dango 1.0.14 needs Python 3.11&ndash;3.13 for the server venv. A server that already has a root-owned Python in that range (Ubuntu 24.04) uses it. Ubuntu 22.04, which ships Python 3.10, gets a pinned CPython 3.12 build that Dango downloads from GitHub (`github.com` and `release-assets.githubusercontent.com`), checks against a SHA-256 and installs under `/opt/dango/python`. This happens before anything is stopped, so 22.04 servers upgrade in place. If no interpreter can be provided, the upgrade stops with error `DANGO-D024`, services are not stopped and nothing is changed. The message names the cause (download failed, wrong size or checksum, `/opt/dango` not a root-owned directory, or a missing tool such as `flock`). Fix it by allowing outbound HTTPS to those two hosts, or by installing Python 3.11, 3.12 or 3.13 from the operating system's packages (root-owned, under `/usr`, with its `venv` module), then run `dango remote upgrade` again.
- **Custom Metabase version.** Error `DANGO-D025` means the project's `Dockerfile.metabase` names a Metabase version that has no administrator pin on the server. See the pin bullet below.
- **Isolation.** The upgrade sets up and verifies the restricted users that run scripts and notebooks. Until a server is upgraded, it refuses to run them. See [Script and notebook isolation](#script-and-notebook-isolation).
- On existing servers, the Metabase DuckDB file-access restriction is applied at the next `dango start` or service restart. `dango remote upgrade` updates an existing notebook WebSocket route in the Caddyfile; if that migration cannot complete, review the upgrade warning and complete the indicated Caddyfile change. Downgrading to 1.0.13 or earlier leaves notebooks unable to connect through the protected route.
- If an upgrade is interrupted while services are stopped, a server-side guard attempts to restart `dango-web`. Re-run `dango remote upgrade` to finish any pending steps.
- A custom Metabase version needs an administrator-approved SHA-256 digest for the exact `MB_VERSION`. On an existing server, `dango remote upgrade` checks this before it stops anything: if the project's `Dockerfile.metabase` on the server names a version with no pin, the upgrade is refused (`DANGO-D025`) and the message ends with the exact command to run as root on the server. Check the SHA-256 of the jar from Metabase's own download, run that command (a server still on 1.0.13 gets a one-line script; a server already on 1.0.14 uses `/usr/local/sbin/dango-compose pin-metabase VERSION SHA256`), then run `dango remote upgrade` again. It resumes setup even if the package is already at the target version. The pin is kept outside the service-account-writable project tree and must match the version being built.
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
| `--force` | Allow a downgrade to an older version |

### Failed Upgrade

What a failed upgrade leaves depends on where it stopped:

- **Refused before the stop** (missing Metabase pin, `DANGO-D025`; no usable Python, `DANGO-D024`; downgrade without `--force`, `DANGO-D022`): services were not stopped and the installed Dango keeps running. A venv that could not be rebuilt (`DANGO-D023`) aborts with the server unchanged. Fix the cause named in the message and run `dango remote upgrade` again.
- **Failed after the stop:** the command starts `dango-web` again before it exits. The server then runs whatever the failed step left, and the pre-upgrade backup (unless `--skip-backup`) is on the server.
- **Client lost mid-upgrade (network drop, closed laptop):** a transient systemd timer on the server (`dango-upgrade-guard-*`) starts `dango-web` once 20 minutes pass without a completed step, and it waits while pip, a venv rebuild, user setup or a Docker build is still running. Run `dango remote upgrade` again to finish.
- **Interrupted venv rebuild:** a root-owned `/srv/dango/venv.untrusted-<id>` directory can be left behind. The next upgrade names it in a warning and prints the `rm -rf` command to run as root after you have checked that no upgrade is running; Dango does not delete it itself.

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

    Before it asks to proceed, `dango remote resize` reminds you that `.env` and `.dlt/secrets.toml` are not in backups by default and lists the secret names (never the values) the server holds, so you can keep a copy of the values first. If an earlier resize was interrupted and left the droplet powered off, `resize` refuses with "Server is powered off (likely an interrupted resize). Run: dango remote power-on".

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

## Moving to a New Server

!!! warning "`dango remote migrate` is switched off in 1.0.14"
    `dango remote migrate` refuses to run, before it contacts any server or the provider, on both DigitalOcean and BYOS deployments. It prints the manual steps below. Use `dango remote resize` to change the size of a DigitalOcean server. The automated command is expected to return in a later release.

To move to a different region, a larger disk, or another host, back up, rebuild and restore:

1. **Save a local copy of the data:**

    ```bash
    dango remote backup download --from-server -o ./backup.tar.gz
    ```

    The archive does not contain `.env` or `.dlt/secrets.toml` by default. The command prints `Note: secrets are not in this backup; re-enter: <names>`: keep a note of those names and store the values somewhere safe.

2. **Destroy the old deployment.** A project attaches to one server, and `dango deploy` refuses while `.dango/cloud.yml` records a deployment:

    ```bash
    dango deploy destroy
    ```

3. **Deploy the new server** with the size, region or host you want (`dango deploy`, or `dango deploy --byos` for your own server).
4. **Restore the data:**

    ```bash
    dango remote backup restore ./backup.tar.gz --from-local
    ```

5. **Re-enter the secrets** you noted in step 1 (for example with `dango remote env set`, and by pushing or entering `.dlt/secrets.toml` values again).
6. **Update DNS** so your domain points at the new server's IP address.

There is a window with no server between steps 2 and 4: plan the downtime. The old server and its Docker volumes are deleted in step 2, so confirm the downloaded archive exists and is the size you expect first. BYOS follows the same steps, with `dango deploy --byos` against the new host in step 3. Destroying a BYOS deployment removes Dango, its Docker volumes and its data from the old server, but does not delete the machine itself; delete it with your hosting provider to stop billing.

---

## Script and notebook isolation

On a cloud server that has isolation set up, scripts and notebooks run as two restricted operating-system users (`dango-run` and `dango-nb`) instead of the `dango` service account. `dango remote upgrade` sets this up and verifies it. A server without isolation refuses to run scripts and notebooks (error `DANGO-ISO001`) rather than running them unisolated.

```bash
dango remote isolation status
```

`dango remote status` shows the same state on its `Isolation:` line. The state is one of:

| State | Meaning |
|-------|---------|
| `on` | Isolation is set up and enforced. |
| `disabled` | An administrator opted out; scripts and notebooks run as the `dango` service account. The status shows who and when. |
| `missing` | Isolation is not set up on this server. Run `dango remote upgrade`; until then script and notebook execution is refused. |
| `unsupported` | The installed Dango predates isolation (it was introduced in 1.0.14), for example after `dango remote upgrade --version 1.0.13 --force`. Nothing is enforced and scripts and notebooks run as the `dango` service account. Upgrade to 1.0.14 or later to turn it on. |
| `unknown` | The state could not be read from the server. Check connectivity with `dango remote status`. |

```bash
dango remote isolation disable --yes   # audited administrator opt-out
dango remote isolation enable          # remove the opt-out and verify isolation
```

`disable` warns what it exposes, asks you to type `disable` unless `--yes` is given, and writes an audit event. With isolation disabled, scripts and notebooks can read the server's secrets (`.env`, `.dlt`), backups and warehouse, and reach its local services. `enable` runs the same steps as `remote upgrade`, including the verification, and removes the opt-out only after they pass. Both commands arm the same server-side guard as an upgrade and refuse to start while another guarded operation seems to be running.

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

### Disk space warning

If `dango remote status` shows high disk usage:

- Remove old dlt pipeline state: `dango remote ssh` &rarr; `rm -rf /srv/dango/project/.dlt/pipelines/*/`
- Consider [resizing](#resizing-the-server) to a larger disk
- Download and remove old backups: `dango remote ssh` &rarr; check `/srv/dango/backups/deploy/`

### pip install failed on server

If `pip install` fails during upgrade (for example a dependency conflict), the command starts `dango-web` again and the server keeps running the previous installation. Read the pip message in the upgrade output, fix the cause, and run `dango remote upgrade` again. If the venv is damaged, the upgrade rebuilds it on a supported Python; do not recreate `/srv/dango/venv` by hand with the system `python3`, which is 3.10 on Ubuntu 22.04 and cannot install Dango 1.0.14.

---

## Next Steps

- [Backups](backups.md) &mdash; configure automated backups
- [Remote Management](remote-management.md) &mdash; push changes and manage the server
- [Destroy & Cleanup](destroy.md) &mdash; tear down a deployment
