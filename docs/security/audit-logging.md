# Audit Logging

Track security-relevant events with the audit log.

---

## Overview

Dango records security-relevant events to an append-only JSONL log file at `.dango/logs/audit.jsonl`. The audit log captures authentication events, user management changes, permission denials, and operational actions.

Audit logging is designed to never block the operation it instruments — if a log write fails, a warning is emitted but the operation proceeds normally.

---

## Event Types

Dango tracks 44 distinct audit event types, organized by category.

### Authentication Events

| Event | Logged When |
|-------|-------------|
| `LOGIN_SUCCESS` | User successfully logs in |
| `LOGIN_FAILURE` | Failed login attempt (wrong password, unknown email) |
| `LOGOUT` | User logs out |
| `SESSION_EXPIRED` | Session invalidated due to timeout |

### Password Events

| Event | Logged When |
|-------|-------------|
| `PASSWORD_CHANGE` | User changes their own password |
| `PASSWORD_RESET` | Admin resets a user's password |

### User Management Events

| Event | Logged When |
|-------|-------------|
| `USER_CREATED` | New user account created |
| `USER_DEACTIVATED` | User account deactivated |
| `USER_REACTIVATED` | User account reactivated |
| `USER_DELETED` | User account permanently deleted |
| `ROLE_CHANGED` | User's role modified (e.g., viewer → editor) |

### Security Events

| Event | Logged When |
|-------|-------------|
| `PERMISSION_DENIED` | User attempts an action they lack permission for |
| `RATE_LIMIT_HIT` | Request blocked by rate limiter |
| `ACCOUNT_LOCKED` | Account locked after too many failed attempts |
| `ACCOUNT_UNLOCKED` | Account unlocked by admin |

### Two-Factor Events

| Event | Logged When |
|-------|-------------|
| `TWO_FA_ENABLED` | User enables 2FA on their account |
| `TWO_FA_DISABLED` | User disables 2FA |

### API Key Events

| Event | Logged When |
|-------|-------------|
| `API_KEY_CREATED` | New API key generated |
| `API_KEY_REVOKED` | API key revoked / deleted |

### Recovery & Invite Events

| Event | Logged When |
|-------|-------------|
| `RECOVERY_CODE_USED` | Recovery code consumed during 2FA login |
| `INVITE_ACCEPTED` | User accepts an invite and sets their password |
| `INVITE_RESENT` | Admin resends an invite link |

### Secrets & OAuth Events

| Event | Logged When |
|-------|-------------|
| `SECRET_SET` | Secret/credential added or updated |
| `SECRET_DELETED` | Secret/credential removed |
| `OAUTH_SOURCE_CONNECTED` | OAuth source connected via web UI |
| `OAUTH_SOURCE_DISCONNECTED` | OAuth source disconnected |

??? info "Operational Events"

    These events track routine operational actions:

    | Event | Logged When |
    |-------|-------------|
    | `SCHEDULE_CREATED` | New schedule added |
    | `SCHEDULE_UPDATED` | Schedule configuration changed |
    | `SCHEDULE_DELETED` | Schedule removed |
    | `SCHEDULE_TRIGGERED` | Schedule manually triggered |
    | `SCHEDULES_RELOADED` | Scheduler reloaded all schedules |
    | `JOB_CANCELLED` | Running job cancelled |
    | `SYNC_TRIGGERED` | Manual sync triggered from web UI |
    | `NOTEBOOK_CREATED` | New notebook created |
    | `NOTEBOOK_DELETED` | Notebook deleted |
    | `NOTEBOOK_LOCK_FORCE_RELEASED` | Admin force-released a notebook lock |
    | `GOVERNANCE_DRIFT_VIEWED` | Schema drift report viewed |
    | `GOVERNANCE_DRIFT_ACCEPTED` | Schema drift accepted by user |
    | `GOVERNANCE_PII_VIEWED` | PII scan report viewed |
    | `CATALOG_VIEWED` | Data catalog accessed |
    | `MONITORING_VIEWED` | Monitoring dashboard viewed |
    | `AI_CATALOG_VIEWED` | AI catalog feature accessed |
    | `DEPLOYMENT_HISTORY_VIEWED` | Deployment history accessed |
    | `QUERY_EXECUTED` | Ad-hoc SQL query executed |

---

## Log Format

### File Location

```
.dango/logs/audit.jsonl
```

### Entry Format

Each line is a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO-8601 UTC timestamp |
| `event` | string | Event type (e.g., `login_success`) |
| `user_id` | string | UUID of the user (if applicable) |
| `email` | string | Email of the user (if applicable) |
| `ip` | string | Client IP address |
| `details` | object | Event-specific additional data |

### Example Entries

```json
{"timestamp": "2026-05-15T10:30:00.123456+00:00", "event": "login_success", "user_id": "a1b2c3d4", "email": "admin@example.com", "ip": "192.168.1.10", "details": {"method": "password"}}
{"timestamp": "2026-05-15T10:31:15.789012+00:00", "event": "login_failure", "user_id": null, "email": "unknown@example.com", "ip": "203.0.113.50", "details": {"reason": "invalid_credentials"}}
{"timestamp": "2026-05-15T10:35:00.456789+00:00", "event": "role_changed", "user_id": "e5f6g7h8", "email": "editor@example.com", "ip": "192.168.1.10", "details": {"old_role": "viewer", "new_role": "editor", "changed_by": "admin@example.com"}}
```

---

## Querying the Audit Log

### CLI

```bash
# View recent audit events (default: last 50)
dango auth audit

# Filter by event type
dango auth audit --type login_failure

# Filter by date
dango auth audit --since 2026-05-01

# Limit results
dango auth audit --limit 100

# Combine filters
dango auth audit --type login_failure --since 2026-05-01 --limit 20
```

### Web UI

Admins can view the audit log from the **Admin** section of the web UI. This requires the `audit.view` permission (admin-only).

---

## Log Rotation

Audit logs are rotated automatically by Dango's log rotation utility to prevent unbounded disk growth:

- Old log entries are compressed with **gzip**
- Rotated files are stored alongside the active log: `.dango/logs/audit.jsonl.1.gz`, `.dango/logs/audit.jsonl.2.gz`, etc.
- Rotation is handled by `dango/utils/log_rotation.py`

---

## Monitoring for Suspicious Activity

Review audit logs regularly for patterns that may indicate a security issue:

### Warning Signs

| Pattern | What It May Indicate |
|---------|---------------------|
| Repeated `LOGIN_FAILURE` from one IP | Brute-force attack |
| `ACCOUNT_LOCKED` events | Active credential stuffing |
| `PERMISSION_DENIED` from one user | User probing for elevated access |
| `LOGIN_SUCCESS` from unusual IP | Compromised credentials |
| `ROLE_CHANGED` you didn't authorize | Unauthorized privilege escalation |
| `API_KEY_CREATED` unexpectedly | Potential persistence mechanism |

### Example Monitoring Queries

```bash
# Check for brute-force attempts in the last 24 hours
dango auth audit --type login_failure --since $(date -u -v-1d +%Y-%m-%d)

# Check for locked accounts
dango auth audit --type account_locked

# Review all role changes
dango auth audit --type role_changed
```

---

## Next Steps

- [Authentication](authentication.md) — login flows and brute-force protection
- [Users & Roles](users-roles.md) — user management events
- [Two-Factor Auth](two-factor.md) — 2FA setup and recovery
- [Hardening Guide](hardening.md) — production security configuration
