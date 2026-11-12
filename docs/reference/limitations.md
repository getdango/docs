# Limitations

Dango is honest about what it doesn't do yet. This page lists the real, current constraints — not vague caveats — along with whether each one is planned, and if so, roughly when.

**Essentially nobody outside the maintainer has run this in production yet.** Dango is early. Treat that as the headline limitation, not a footnote.

## Known limitations

| Limitation | Status |
|---|---|
| Single-writer concurrency — Marimo cannot do concurrent read-write with the rest of the platform today | **Planned.** Fixed by the Quack migration (DuckDB's concurrent read/write storage format), targeted for when DuckDB 2.0 stabilizes (~September 2026). Waiting on DuckDB upstream, not on Dango. |
| Cloud deploy is DigitalOcean-only for managed, automated provisioning | **Not planned.** Bring-your-own-server (BYOS) works with any provider today via manual setup. Automated wizards for AWS/GCP/Hetzner are only revisited on user demand from those providers — none yet. |
| 35 data sources, vs. Airbyte's 300+ | **Not scheduled.** Sources are added when a specific user asks for one, not on a fixed roadmap or schedule. |
| No SSO / SAML — admin login, 2FA, and API keys only | **Not planned.** Revisited on enterprise customer signal — none yet. |
| No streaming, CDC, or reverse ETL | **Not planned.** Out of scope for what Dango is; revisited only on user demand. |
| Chrome-tested only — Safari and Firefox are untested, not merely unverified | **Not scheduled.** Sits in the demand-driven backlog, pulled in on user signal rather than a committed date. |
| No encryption at rest on the server — the DuckDB file is unencrypted | **Planned, no date.** A real roadmap item, independent of the Quack migration. Not a typical small-team need today, so it's further out than the "not planned" items above. |
| Deploying model changes is blind — no `dango diff` or `dev --remote` yet | **Planned.** A core workflow gap, estimated at 3–4 weeks of work. |
| Scale ceiling is stated as "tested to X," not estimated | **Not scheduled.** Large-dataset performance testing hasn't been run past what's actually been exercised in practice — this isn't a number we're willing to invent. |
| Single project per server | **Not scheduled.** Multi-project-per-droplet sits in the demand-driven backlog. |
| BYOS deployments without a configured backup destination store backups locally only — if the server is lost, so are the backups | **Partially addressed, full fix planned.** Deploying without a backup destination now shows an explicit warning at deploy time. Full S3-compatible backup support for BYOS depends on two roadmap items — cloud storage configuration, then the BYOS backup destination itself — neither shipped yet. |

## Known issues in 1.0.14

Things you can hit in Dango 1.0.14 that are understood and not fixed in this release. Each entry says what to do.

| Issue | What to do |
|---|---|
| **Windows installer is unverified.** The PowerShell installer (`install.ps1`) failed in a test and has not been verified for 1.0.14. A fix is planned for 1.0.15. | If the installer fails on Windows, the [manual installation steps](../getting-started/installation.md#manual-installation) install Dango directly with Python 3.11, 3.12 or 3.13. |
| **`dango remote migrate` is switched off.** It refuses and prints the manual steps. It is expected to return in a later release. | Use `dango remote resize` to change size. To move servers, follow [Moving to a New Server](../deployment/server-operations.md#moving-to-a-new-server). There is a window with no server, so plan the downtime. |
| **Docker-group fallback on a server.** If the root-owned Compose helper cannot be installed, the server keeps Docker-group access for the service account and shows a warning; some Metabase build paths are then not covered by the helper's integrity checks. | Run `dango remote upgrade` to retry after fixing the cause named in the warning. `dango remote status` shows `Docker access: group (fallback)` while this applies. |
| **The Metabase driver file is not re-checked on cloud upgrade, rebuild or restart after a backup.** | Verify the origin of the driver file on a server and replace a suspect one before using those paths. |
| **BYOS host layout.** A bind-mounted `/srv/dango/project` can make a restore fall back to copy and delete, and a widened `net.ipv4.ip_local_port_range` lets the notebook runner reach other local services in that range. | See the host-layout note on [Bring Your Own Server](../deployment/byos.md). |
| **A hand-edited or truncated backup archive can restore without error.** A restore does not check the manifest's file list against the archive. | Restore only archives you made yourself, and keep the downloaded copy unchanged. |
| **An interrupted venv rebuild can leave a large `/srv/dango/venv.untrusted-*` directory.** Dango does not delete it. | The next `dango remote upgrade` names it and prints the cleanup command to run as root once no upgrade is running. |
| **Server-side backup settings.** `include_secrets` and `spaces_retention` are read from `.dango/cloud.yml` on the server, which `dango remote push` does not upload; `on_server_retention` is shown by `dango remote backup config` but not read by any backup command. | See [Retention and secrets settings](../deployment/backups.md#retention-and-secrets-settings). |
| **With `auth.require_2fa`, a user who has not enrolled TOTP can enroll it with only their password.** Nothing else (an invite or an email check) gates the enrollment session. | After you turn `require_2fa` on, have every user enroll promptly, and review accounts that have not. See [Two-Factor Auth](../security/two-factor.md#when-2fa-is-required). |
| **A locked account cannot change its password.** While an account is locked by failed attempts, the owner's change-password request is refused even with the correct password. | Wait for the lock to end, or run `dango auth unlock EMAIL`. |
| **Live-update (WebSocket) connections outlive a sign-out.** A page that is already open can keep receiving live events after logout, deactivation, session revocation or a role downgrade, until that connection closes. | Close the browser tab; restart `dango-web` if you need every open connection closed at once. |
| **With `dango auth disable`, a local project is reachable from the local network.** The web server then binds all interfaces and serves its pages without sign-in. | Keep authentication enabled, or use it only on a network you trust. |
| **Notebook pages are served from Dango's own web origin, and notebook code runs with Editor-level capability.** | Give the Editor and Admin roles only to people you trust with notebook execution. See [Users & Roles](../security/users-roles.md#security-boundaries). |
| **Metabase device-trust and timeout cookies are not passed through the `/metabase` proxy**; only the Metabase session cookie is. Not checked against every Metabase setting. | If Metabase asks you to re-verify a device or shows session oddities after upgrading, sign out of Dango and sign in again. |
| **A first DigitalOcean deploy can wait a long time at "Waiting for platform"** (one test waited about 17 minutes although the server was ready after about 90 seconds). Cause not found. | Check `dango remote status`; the deploy completed after the wait. |
| **The `fs.protected_hardlinks` check after a push warns instead of refusing.** Server setup refuses a host where it is not 1, but a push to a server whose setting changed later only warns. | Keep `fs.protected_hardlinks=1` (see [Bring Your Own Server](../deployment/byos.md#fsprotected_hardlinks-is-not-1)). |
| **A killed `dango remote push` can leave a `/tmp/dango-req-*` directory on the server** (root-only). | Remove it as root on the server when no push is running. |
| **A failed `dango remote env set` can leave a private staging directory.** If the final write command fails (timeout or dropped connection), a `dango`-owned `/tmp/tmp.*` directory holding the new `.env` content is not removed. | Remove it on the server and run the command again. |
| **A fresh cloud deploy shows an error page for a short time.** For a few seconds after Caddy is installed it answers with its own default page, and until Dango is up (several minutes) it answers a short "Dango is starting" page (HTTP 503). | Wait for the deploy to finish; check `dango remote status`. |

## What this page doesn't cover

Category-level positioning (Dango isn't a petabyte-scale platform, a streaming system, or an ML environment) lives on the marketing site. This page is the specific, technical version — the things you'd actually hit using Dango, not the category it's not competing in.
