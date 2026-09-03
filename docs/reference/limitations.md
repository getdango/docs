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

## What this page doesn't cover

Category-level positioning (Dango isn't a petabyte-scale platform, a streaming system, or an ML environment) lives on the marketing site. This page is the specific, technical version — the things you'd actually hit using Dango, not the category it's not competing in.
