# Secrets & Admin

Manage environment variables, OAuth credentials, user accounts, and authentication settings.

---

!!! warning "Admin access required"
    The Secrets & Credentials and User Management pages require the **admin** role. Account Settings is available to all authenticated users.

## Secrets & Credentials

The Secrets page (`/settings/secrets`) manages environment variables and OAuth connections. Access it from the **gear menu** → **Secrets & Credentials**.

### Environment Variables

A table of all configured environment variables:

| Column | Description |
|--------|-------------|
| **Key** | Variable name (monospace font) |
| **Value** | Always displayed as `***` (masked for security) |
| **Actions** | **Edit** and **Delete** buttons |

#### Adding a Variable

1. Click **Add Variable** (top-right).
2. Enter the **Key** (variable name) and **Value** in the modal.
3. Click **Save**.

The variable is written to the project's `.env` file with restrictive permissions (mode 0600).

#### Editing a Variable

1. Click **Edit** on the variable row.
2. The key field is read-only. Enter the new value.
3. Click **Save**.

#### Deleting a Variable

1. Click **Delete** on the variable row.
2. Confirm in the modal: "Delete [key]? This cannot be undone."
3. Click **Delete**.

### OAuth Connections

Below the environment variables, the OAuth section shows connected and available OAuth sources.

#### Connected Sources

Each connected source card shows:

- **Source name** — formatted display name (e.g., "Google Sheets")
- **Provider and identifier** — the OAuth provider and account email
- **Connected date** — when the connection was established
- **Expiry status**:
    - Red "Expired" — token has expired
    - Yellow "Expires [date]" — expires within 7 days
    - Gray "Expires [date]" — valid with no upcoming expiry

Actions:

- **Reconnect** — appears when the token is expired or expiring within 7 days. Redirects to the OAuth provider for re-authentication.
- **Disconnect** — removes the OAuth credentials after confirmation.

#### Available Sources

On non-localhost deployments, a list of available OAuth providers shows **Connect** buttons for sources that haven't been connected yet (e.g., Google Ads, Google Analytics, Google Sheets, Facebook Ads).

!!! info "Local OAuth"
    On localhost, OAuth connections require a domain with HTTPS. Use `dango oauth setup` from the CLI for local OAuth configuration.

---

## User Management

The User Management page (`/settings/users`) shows all platform users. Access it from the **gear menu** → **User Management**.

!!! info "CLI-managed"
    Users are created and managed via CLI commands like `dango auth add-user`. The web UI provides a read-only view of user accounts.

### Users Table

| Column | Description |
|--------|-------------|
| **Email** | User's email address |
| **Role** | Role badge — **admin** (red), **editor** (blue), or **viewer** (gray) |
| **Status** | Current account state (see below) |
| **Last Login** | Date of last successful login, or "Never" |
| **Created** | Account creation date |

### User Status Values

| Status | Color | Meaning |
|--------|-------|---------|
| **Active** | Green | User has logged in and account is in good standing |
| **Invited** | Indigo | User has a pending invite that hasn't been accepted |
| **Invite Expired** | Orange | Invite link expired before the user accepted |
| **Locked** | Yellow | Account temporarily locked due to failed login attempts |
| **Inactive** | Red | Account has been deactivated by an admin |

---

## Account Settings

The Account Settings page (`/settings/account`) is available to all authenticated users. Access it from the **gear menu** → **Account Settings**.

### Profile

Read-only display of your email, role badge, and membership date. Contact an admin to change your email.

### Change Password

1. Enter your **Current Password**.
2. Enter a **New Password** (at least 8 characters).
3. Confirm the new password.
4. Click **Change Password**.

On success, all existing sessions are invalidated and you're redirected to the login page.

### Active Sessions

A table showing all your active sessions:

| Column | Description |
|--------|-------------|
| **IP** | IP address of the session |
| **User Agent** | Browser/client identifier (truncated) |
| **Last Active** | When the session was last used. The current session shows a green "Current" badge. |
| **Action** | **Revoke** button (not available on the current session — use Logout instead) |

Click **Revoke All Others** in the header to invalidate all sessions except your current one.

### API Keys

Manage API keys for programmatic access:

| Column | Description |
|--------|-------------|
| **Name** | Key name (e.g., "CLI access") |
| **Prefix** | First 8 characters of the key for identification |
| **Created** | When the key was created |
| **Last Used** | When the key was last used, or "Never" |
| **Action** | **Revoke** button |

Click **Create Key** to generate a new API key:

1. Enter a **Key Name** in the modal.
2. Click **Create**.
3. **Copy the key immediately** — it is shown only once and cannot be retrieved later.

### Two-Factor Authentication (2FA)

Set up TOTP-based two-factor authentication for enhanced security:

#### Enabling 2FA

1. Click **Enable 2FA**.
2. Enter your current password to confirm identity.
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.).
4. Enter the 6-digit verification code from the app.
5. Click **Verify & Enable**.
6. **Save the recovery codes** — these one-time-use codes let you log in if you lose access to your authenticator app. You can copy them to clipboard or download as a text file.

!!! warning "Save recovery codes"
    Store your recovery codes in a safe place. Each code can only be used once. If you lose both your authenticator app and recovery codes, an admin must reset your account.

#### Disabling 2FA

1. Click **Disable 2FA**.
2. Enter your current password.
3. Click **Disable 2FA** to confirm.

#### Regenerating Recovery Codes

1. Click **Regenerate Recovery Codes**.
2. Enter your current password and a TOTP code from your authenticator.
3. Click **Regenerate**.
4. Save the new codes — old codes are invalidated.

---

## Authentication Pages

### Login

The login page (`/login`) uses a two-step flow:

1. **Credentials step** — enter email and password, then click **Sign In**.
2. **TOTP step** (if 2FA is enabled) — enter the 6-digit code from your authenticator app, or click "Use a recovery code instead" to enter a one-time recovery code.

If OAuth providers are configured, "Continue with [Provider]" buttons appear below the login form.

Account lockout occurs after 5 failed login attempts, with a countdown timer showing when you can try again.

### Accept Invite

New users receive an invite link that opens the invite page (`/invite/{token}`). Enter a password (minimum 8 characters) and confirm it to activate your account.

### Change Password (First Login)

If an admin creates your account with a temporary password, you're redirected to `/setup` on first login to set a new password.

??? info "How it works"
    - **Environment variables:** `GET /api/secrets` lists masked env vars. `POST /api/secrets` creates/updates. `DELETE /api/secrets/{key}` removes.
    - **OAuth:** `GET /api/secrets/oauth` lists connections with expiry status. `DELETE /api/secrets/oauth/{source_type}` disconnects. OAuth connect flow starts at `GET /oauth/connect/{sourceType}`.
    - **Users:** `GET /api/admin/users` lists all users with role, status, and login history.
    - **Auth:** `POST /api/auth/login` authenticates. `POST /api/auth/2fa/verify` verifies TOTP. `POST /api/auth/change-password` updates password. Session management via `GET /api/auth/sessions` and `DELETE /api/auth/sessions/{id}`. API keys via `GET/POST/DELETE /api/auth/api-keys`. 2FA setup via `POST /api/auth/2fa/setup`, `POST /api/auth/2fa/verify-setup`, `POST /api/auth/2fa/disable`, `POST /api/auth/2fa/regenerate-recovery`.
    - **Invite:** `POST /api/auth/accept-invite` accepts an invite token and sets the user's password.
    - All admin actions are logged as audit events.

## Troubleshooting

**"OAuth connections require a domain with HTTPS"**
:   OAuth only works on deployed instances with a domain name. For local development, use `dango oauth setup` from the CLI to configure OAuth with a local callback server.

**Account locked after failed logins**
:   Wait for the lockout timer to expire (shown on the login page), or ask an admin to unlock your account.

**Lost 2FA authenticator and recovery codes**
:   Contact an admin to disable 2FA on your account and reset your password.

**API key not working**
:   Check that the key hasn't been revoked. API keys are tied to your user account — if your account is deactivated, API keys stop working.

## Related Pages

- [Web UI Overview](web-ui-overview.md) — navigation and feature summary
- [Health & Logs](health-logs.md) — platform health monitoring
- [Sources Page](sources.md) — source configuration that uses environment variables and OAuth
