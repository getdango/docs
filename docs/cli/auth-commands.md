# Auth Commands

Manage user authentication, roles, and access control from the command line.

---

## Overview

The `dango auth` commands manage the built-in authentication system. Auth is enabled by default — `dango init` prompts for an admin password during project setup.

**All 13 subcommands:**

| Command | Description |
|---------|-------------|
| `auth enable` | Enable authentication |
| `auth disable` | Disable authentication |
| `auth status` | Show authentication status |
| `auth add-user` | Create a new user |
| `auth list-users` | List all users |
| `auth reset-password` | Generate new temporary password |
| `auth change-role` | Change a user's role |
| `auth deactivate-user` | Soft-disable a user account |
| `auth reactivate-user` | Re-enable a deactivated user |
| `auth delete-user` | Permanently delete a user |
| `auth unlock` | Unlock a locked-out account |
| `auth audit` | Query the authentication audit log |
| `auth recover` | Emergency admin account recovery |

!!! info
    Auth commands manage **user accounts and authentication**. For OAuth provider connections (Google, Facebook), see [OAuth Commands](oauth-commands.md).

---

## Enable / Disable

### dango auth enable

Enable authentication for this project.

```bash
dango auth enable
```

=== "Local"

    - 365-day session duration
    - 24-hour idle timeout

=== "Cloud"

    - 30-day session duration
    - 60-minute idle timeout

---

### dango auth disable

Disable authentication for this project. All endpoints become accessible without login.

```bash
dango auth disable
```

!!! warning
    Disabling auth removes all access control. Anyone with network access to the platform can view and modify data.

---

## User Management

### dango auth add-user

Create a new user with an invite link or temporary password.

```bash
dango auth add-user EMAIL [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--role [admin\|editor\|viewer]` | — | User role |
| `--password` | — | Generate a temporary password instead of an invite link |
| `--base-url TEXT` | — | Base URL for invite links |

**Roles:**

| Role | Permissions |
|------|-------------|
| `admin` | Full access: manage users, config, sources, and data |
| `editor` | Manage sources, sync data, run transformations |
| `viewer` | Read-only access to dashboards and data |

```bash
# Create user with invite link
dango auth add-user alice@example.com --role editor

# Create user with temporary password
dango auth add-user bob@example.com --role viewer --password
```

---

### dango auth list-users

List all users with their roles and status.

```bash
dango auth list-users
```

---

### dango auth reset-password

Generate a new temporary password for a user.

```bash
dango auth reset-password EMAIL
```

```bash
dango auth reset-password alice@example.com
```

The user must change the temporary password on next login.

---

### dango auth change-role

Change a user's role.

```bash
dango auth change-role EMAIL {admin|editor|viewer}
```

```bash
dango auth change-role alice@example.com admin
dango auth change-role bob@example.com viewer
```

---

### dango auth deactivate-user

Soft-disable a user account. The user cannot log in but the account is preserved.

```bash
dango auth deactivate-user EMAIL
```

```bash
dango auth deactivate-user alice@example.com
```

Use `dango auth reactivate-user` to re-enable.

---

### dango auth reactivate-user

Re-enable a deactivated user account.

```bash
dango auth reactivate-user EMAIL
```

```bash
dango auth reactivate-user alice@example.com
```

---

### dango auth delete-user

Permanently delete a user account.

```bash
dango auth delete-user EMAIL
```

!!! danger
    This permanently deletes the user and cannot be undone. Use `deactivate-user` for a reversible alternative.

```bash
dango auth delete-user old-employee@example.com
```

---

### dango auth unlock

Unlock a user account that was locked out due to failed login attempts.

```bash
dango auth unlock EMAIL
```

```bash
dango auth unlock alice@example.com
```

---

## Audit & Recovery

### dango auth audit

Query the authentication audit log.

```bash
dango auth audit [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--since TEXT` | Filter events after date (YYYY-MM-DD) |
| `--type TEXT` | Filter by event type |
| `--limit INTEGER` | Max events to show |

```bash
# View recent auth events
dango auth audit

# Filter by date
dango auth audit --since 2024-12-01

# Filter by event type
dango auth audit --type login_failed --limit 50
```

---

### dango auth recover

Create a recovery admin account for emergency use. Use when all admin accounts are locked out or inaccessible.

```bash
dango auth recover
```

!!! tip
    This is a last-resort command. It creates a new admin account that can be used to restore access to the system.

---

## Remote User Management

For managing users on a deployed cloud server, use `dango remote auth`:

```bash
dango remote auth add-user alice@example.com --role editor
dango remote auth list-users
dango remote auth remove-user alice@example.com
dango remote auth reset-password alice@example.com
```

See [Deploy & Remote](deploy-remote.md#remote-user-management) for details.

---

## Troubleshooting

??? info "Forgot admin password"
    Run `dango auth recover` to create a recovery admin account, then use it to reset other passwords.

??? info "User locked out"
    Run `dango auth unlock user@example.com` to unlock the account. Accounts are locked after repeated failed login attempts.

??? info "Auth enabled but can't access platform"
    Check `dango auth status` to confirm auth is enabled. If you set `DANGO_ADMIN_PASSWORD` during init, that's the admin password. For automated testing/CI, use `--skip-wizard` or set the env var.

---

## Related Pages

- [CLI Reference](cli-reference.md) — Quick reference for all commands
- [OAuth Commands](oauth-commands.md) — OAuth provider connections (separate from user auth)
- [Deploy & Remote](deploy-remote.md) — Remote server user management
- [Authentication Guide](../security/authentication.md) — How authentication works in Dango
