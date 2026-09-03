# Telemetry

What Dango and its bundled tools send home, and how to turn each one off.

---

## Overview

Dango bundles four separate tools, each with its own telemetry: **Dango** itself, **dbt-core**, **dlt**, and **Metabase**. Telemetry is opt-in for Dango and disclosed-and-controllable for all four — this page documents exactly what each one sends, where it goes, and how to turn it off.

This page is about the **product's** telemetry — what Dango and the tools it runs send over the network while you use it. It's a different topic from the [documentation site's privacy policy](../legal/privacy.md), which covers this *docs website* (hosting, cookies, fonts) and collects nothing product-related at all.

---

## What's collected, per provider

| Provider | What it sends | Host contacted | How to disable |
|---|---|---|---|
| **dango** | UUID, version, OS, source type names | `telemetry.getdango.dev` | `dango telemetry off --provider dango` (or `--all`) |
| **dbt-core** | OS, Python version, invocation success/duration | `fishtownanalytics.sinter-collect.com` | `dango telemetry off --provider dbt` (or `--all`), or `DBT_SEND_ANONYMOUS_USAGE_STATS=false` / `DO_NOT_TRACK=1` |
| **dlt** | Command names, hashed pipeline names, execution times | `telemetry.scalevector.ai` | `dango telemetry off --provider dlt` (or `--all`), or `dlthub_telemetry=false` in `.dlt/config.toml` |
| **metabase** | Anonymous usage statistics | `metabase.com` | `dango telemetry off --provider metabase` (or `--all`) |

The "what it sends" wording above is the same text shown in `dango telemetry status` and the `/settings/telemetry` web page — one source of truth, not three descriptions that can drift apart.

Dango's own ping fires twice: a one-time **install** ping (sent once, the first time you accept the consent prompt) and a **weekly heartbeat** while `dango start` is running. The install ping alone can't tell a one-time `dango init` apart from an install still in active use weeks later — the heartbeat is what makes "active install" measurable.

!!! note "Metabase's endpoint is not independently verified"
    Metabase runs as a separate Java process, not a Python library Dango can inspect directly. `metabase.com` is Metabase's own documented telemetry host and `PUT /api/setting/anon-tracking-enabled` is Metabase's own documented setting, but Dango's maintainers have not independently confirmed the wire-level payload the way the other three providers' payloads are confirmed (dlt's suppression, for example, has been confirmed by watching DNS resolution get blocked). Treat the Metabase row as "per Metabase's own docs," not independently verified.

---

## How to opt out

**CLI — all providers at once:**

```bash
dango telemetry off --all
```

**CLI — a single provider:**

```bash
dango telemetry off --provider dango
dango telemetry off --provider dbt
dango telemetry off --provider dlt
dango telemetry off --provider metabase
```

Check current state anytime with:

```bash
dango telemetry status
```

**Web UI:** the same four toggles are available at **`/settings/telemetry`** (admin-only).

**One-time consent prompt:** the first time you run `dango init`, Dango asks a yes/no question before sending anything:

> Help improve Dango by sending anonymous usage data (no source names, credentials, or data — just install count)?

Your answer is stored in `~/.dango/telemetry.json` and never asked again. Answering "no" (or hitting Ctrl-D / closed stdin) means nothing is ever sent — Dango's install ping only fires after an explicit "yes."

**Environment variables:** `DO_NOT_TRACK=1` and `DANGO_TELEMETRY=0` (or any other falsy value: `f`, `false`, `n`, `no`) both suppress every Dango ping, regardless of what's stored in `~/.dango/telemetry.json` — confirmed in `is_telemetry_enabled()`. `telemetry: false` in `~/.dango/config.yml` does the same. dbt-core additionally honors `DBT_SEND_ANONYMOUS_USAGE_STATS=false` and `DO_NOT_TRACK=1` directly (dbt's own opt-out, independent of Dango's).

**CI is always excluded.** Dango detects common CI environment variables (`CI`, `GITHUB_ACTIONS`, `GITLAB_CI`, `JENKINS_URL`, `BUILDKITE`, `CIRCLECI`, `TRAVIS`, `CODEBUILD_BUILD_ID`) and never sends a ping from CI, regardless of any stored consent — CI runs are the single biggest source of inflated install counts, so they're excluded unconditionally rather than relying on the same opt-out logic as everything else.

---

## What's NOT collected

Dango's own ping payload is limited to exactly what the table above lists: an anonymous install UUID, the Dango version, the OS name, the Python version, and configured source *type* names (e.g. `"postgres"`, `"stripe"` — the category, not your actual source names). Specifically, it never includes:

- No source names, connection strings, or credentials
- No table names, row counts, schema, or query text
- No data values of any kind
- No personal information or email addresses

Telemetry is also best-effort and fails silently: the network call runs on a background thread with a 2-second timeout, and any failure — DNS, timeout, TLS, a bad response — is swallowed without retry. Telemetry can never block or break a CLI command.

Identity is machine-level (`~/.dango/telemetry.json`), not project-scoped — one person running Dango against five different client projects on one laptop counts as one install, not five.

The other three providers' payloads are scoped the same way — see the table above for exactly what each one sends. None of the four sends query results, credentials, or data values.

---

## Why it exists

Dango is a small, largely unfunded open-source project. An anonymous install count — nothing more specific than "someone somewhere ran `dango init`" — is the only signal the maintainers have that anyone is actually using it. There's no other analytics, no user tracking, no product usage funnel. If you'd rather not contribute even that, every mechanism above turns it off completely.

---

## Full network egress

Telemetry is one category of outbound network traffic; Dango and its bundled tools also make other network calls that aren't telemetry (dbt package installs, DuckDB extension loading, Metabase's Docker image pull, etc.) and aren't user-controllable because they're required for the software to function. The complete, verified list of every host Dango's stack contacts — telemetry and functional — lives in [`network-egress.yml`](https://github.com/getdango/dango/blob/main/docs/network-egress.yml) in the main repo.

---

## Next Steps

- [Audit Logging](audit-logging.md) — security event logging, a separate feature from telemetry
- [Privacy Policy](../legal/privacy.md) — the documentation *website's* privacy policy (a different topic from this page)
