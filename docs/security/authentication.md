# Authentication

How Dango authenticates users: passwords, sessions, API keys, and login flows.

---

## Overview

Authentication is **enabled by default** in Dango v1. When you run `dango init`, you're prompted to set an admin password. All web UI and API access requires authentication — there is no anonymous mode.

Dango supports three login methods:

- **Password login** — email + password, with optional [two-factor authentication](two-factor.md)
- **OAuth login** — Google or GitHub (admin must pre-create the user account)
- **API key** — for programmatic access (scripts, CI/CD)

---

## Enabling Authentication

Authentication is enabled automatically during `dango init`. For existing projects created before v1:

```bash
# Enable auth and create the admin account
dango auth enable

# You'll be prompted for an admin email and password
```

To check the current auth status:

```bash
dango auth status
```

---

## Login Flows

### Password Login

The standard login flow:

1. User submits email and password at `/login`
2. Server checks [brute-force lockout](#brute-force-protection) status
3. Password verified against bcrypt hash
4. If [2FA is enabled](two-factor.md) → partial session created (5-minute timeout) → user enters TOTP code → full session
5. If 2FA is not enabled → full session created immediately
6. [Metabase SSO](#metabase-sso-bridge) session bridged automatically

### OAuth Login

For Google and GitHub social login:

1. User clicks "Sign in with Google" or "Sign in with GitHub" on the login page
2. Redirected to the provider's consent screen
3. After approval, redirected back to Dango with an authorization code
4. Dango exchanges the code for user info (email, name)
5. If a Dango user with that email exists → logged in automatically
6. If no matching user exists → redirected to login page with an error

!!! important "Admin Must Pre-Create Users"
    OAuth login does not create new accounts. An admin must first create the user via `dango auth add-user` or the web UI. The OAuth provider is linked automatically when the email matches.

### API Key Authentication

For programmatic access, use API keys instead of sessions:

```bash
curl -H "Authorization: Bearer dango_ak_xxxxx" \
  http://localhost:8800/api/sources
```

See [API Keys](#api-keys) below for creating and managing keys.

---

## Session Management

After successful login, Dango creates a session and sets a cookie.

### Session Timeouts

=== "Local"

    | Parameter | Value |
    |-----------|-------|
    | Absolute expiry | 365 days |
    | Idle timeout | 24 hours (1,440 minutes) |

    Local sessions use generous timeouts since the server runs on your own machine.

=== "Cloud"

    | Parameter | Value |
    |-----------|-------|
    | Absolute expiry | 30 days |
    | Idle timeout | 60 minutes |

    Cloud timeouts are configured automatically by `dango deploy`. Customize in `.dango/project.yml`:

    ```yaml
    auth:
      session_max_days: 30
      idle_timeout_minutes: 60
    ```

- **Absolute expiry**: Session expires this many days after creation, regardless of activity
- **Idle timeout**: Session expires after this period of inactivity (no API requests)

### Session Cookie

| Property | Value |
|----------|-------|
| Name | `dango_session` |
| HttpOnly | Yes (not accessible to JavaScript) |
| SameSite | Lax |
| Secure | Yes (when served over HTTPS) |

### Managing Sessions

View and manage your active sessions from the **Account** page (`/account`) in the web UI. You can sign out of individual sessions or all sessions at once.

---

## API Keys

API keys provide stateless authentication for scripts and automation.

### Key Properties

| Property | Value |
|----------|-------|
| Prefix | `dango_ak_` |
| Storage | SHA-256 hashed (plaintext never stored) |
| Expiry | Optional (set at creation time) |

### Creating API Keys

=== "Web UI"

    1. Go to **Account** (`/account`)
    2. Scroll to **API Keys**
    3. Click **Create API Key**
    4. Set a name and optional expiry date
    5. Copy the key — it's shown only once

=== "API"

    ```bash
    curl -X POST http://localhost:8800/api/auth/api-keys \
      -H "Cookie: dango_session=..." \
      -H "X-Requested-With: XMLHttpRequest" \
      -H "Content-Type: application/json" \
      -d '{"name": "ci-deploy", "expires_in_days": 90}'
    ```

### Using API Keys

Include the key in the `Authorization` header:

```bash
curl -H "Authorization: Bearer dango_ak_xxxxx" \
  http://localhost:8800/api/sources
```

API keys carry the same role and permissions as the user who created them.

---

## Metabase SSO Bridge

Dango provides transparent single sign-on with Metabase. When you log into Dango, a Metabase session is created automatically — no separate Metabase login required.

**How it works:**

1. Each Dango user gets a corresponding Metabase account (created automatically)
2. On Dango login, a Metabase session cookie (`metabase.SESSION`) is set alongside the Dango session
3. When accessing dashboards, the Metabase proxy uses this session
4. On Dango logout, the Metabase session is also terminated

Metabase accounts use randomly generated passwords (encrypted and stored in the auth database). Users never need to know their Metabase password.

For role mapping details, see [Users & Roles — Metabase Role Sync](users-roles.md#metabase-role-sync).

---

## Password Policy

Dango follows [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) guidelines:

| Rule | Value |
|------|-------|
| Minimum length | 8 characters |
| Maximum length | No limit |
| Complexity rules | None (no uppercase/number/symbol requirements) |
| Common password check | ~1,000 blocked passwords |
| Bcrypt work factor | 12 rounds |

!!! tip "Why No Complexity Rules?"
    NIST research shows complexity requirements lead to weaker passwords (predictable patterns like `Password1!`). Length and avoiding common passwords are more effective.

---

## Brute-Force Protection

Dango protects against credential stuffing and brute-force attacks.

### Lockout Policy

| Parameter | Value |
|-----------|-------|
| Failed attempts before lockout | 5 |
| Lockout duration | 15 minutes |
| Tracking | Per (IP, email) pair |

After 5 failed login attempts to the same email from the same IP address, further attempts to that email from that IP are blocked for 15 minutes. Both existing and non-existing emails receive identical lockout behavior, preventing username enumeration through lockout timing.

### Unlocking Accounts

```bash
# Unlock a specific user (clears failed attempt counter)
dango auth unlock user@example.com
```

### Timing Oracle Prevention

All login failure paths (wrong password, unknown email, inactive account) perform a dummy bcrypt verification to ensure consistent response times. This prevents attackers from distinguishing between valid and invalid email addresses based on response timing.

### Rate Limiting

In addition to account lockout, the web server applies rate limiting:

| Endpoint | Limit |
|----------|-------|
| `/api/auth/login` | 10 requests per 60 seconds |
| All other `/api/*` | 200 requests per 60 seconds |

Localhost requests (`127.0.0.1`, `::1`) are exempt from rate limiting.

---

## Troubleshooting

### Locked Out of Admin Account

If you're locked out due to too many failed attempts:

```bash
# Clear the lockout
dango auth unlock admin@example.com
```

### Lost Admin Password

If you've forgotten the admin password entirely:

```bash
# Create an emergency admin account with a temporary password
dango auth recover
```

This creates a new admin user with a temporary password displayed in the terminal. Use it to log in and reset the original admin's password.

### Session Expired Unexpectedly

Check your session timeout settings:

```bash
dango auth status
```

For cloud deployments, the default idle timeout is 60 minutes. Adjust in `.dango/project.yml` if needed:

```yaml
auth:
  idle_timeout_minutes: 120  # 2 hours
```

---

## Next Steps

- [Users & Roles](users-roles.md) — manage users and permissions
- [Two-Factor Auth](two-factor.md) — enable TOTP-based 2FA
- [Audit Logging](audit-logging.md) — track security events
- [Hardening Guide](hardening.md) — production security configuration
