# Users & Roles

Manage users with admin, editor, and viewer roles.

---

## Overview

Dango uses role-based access control (RBAC) with three built-in roles. Every user is assigned exactly one role that determines what they can see and do.

| Role | Description |
|------|-------------|
| **Admin** | Full control — all permissions, user management, platform configuration |
| **Editor** | Data operations — sync sources, run transformations, create dashboards, manage notebooks |
| **Viewer** | Read-only — view sources, dashboards, models, and health status |

---

## Role Descriptions

### Admin

Admins have a wildcard permission (`*`) that grants access to everything. This includes:

- All data operations (sync, transform, query)
- User management (create, edit, deactivate, delete users)
- Auth settings (enable/disable 2FA policy, manage API keys for any user)
- Platform configuration (start/stop services, manage settings)
- Audit log access
- Credential and secret management

### Editor

Editors can perform day-to-day data operations but cannot manage users, auth settings, or platform configuration:

- Sync data sources and manage source configuration
- Upload and delete CSV files
- Run dbt transformations and manage models
- View dashboards and create new ones
- Execute ad-hoc queries
- View and execute notebooks
- View schedules and governance reports
- View health status, logs, and project configuration

### Viewer

Viewers have read-only access to data and status:

- View data sources (but not sync or manage)
- View dbt models and documentation
- View dashboards (but not create or query)
- View health status and logs
- View notebooks (but not execute)
- View schedules and governance reports

---

## Permission Matrix

Dango has 29 named permissions organized across 9 domains.

### Source Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `source.view` — list sources, view status | :material-check: | :material-check: | :material-check: |
| `source.view_credentials` — view OAuth tokens / secrets | :material-check: | | |
| `source.sync` — trigger a sync | :material-check: | :material-check: | |
| `source.manage` — add / remove / configure sources | :material-check: | :material-check: | |

### CSV Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `csv.upload` — upload CSV files | :material-check: | :material-check: | |
| `csv.delete` — delete uploaded CSVs | :material-check: | :material-check: | |

### dbt Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `dbt.view` — view models, docs | :material-check: | :material-check: | :material-check: |
| `dbt.run` — trigger dbt runs | :material-check: | :material-check: | |
| `dbt.manage` — add / remove models | :material-check: | :material-check: | |

### Dashboard Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `dashboard.view` — view dashboards | :material-check: | :material-check: | :material-check: |
| `dashboard.create` — create / edit dashboards | :material-check: | :material-check: | |
| `query.execute` — run ad-hoc queries | :material-check: | :material-check: | |
| `dashboard.manage` — manage Metabase settings | :material-check: | | |

### Platform Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `health.view` — view health / status | :material-check: | :material-check: | :material-check: |
| `logs.view` — view logs | :material-check: | :material-check: | :material-check: |
| `platform.manage` — start / stop / configure platform | :material-check: | | |
| `config.view` — view project configuration | :material-check: | :material-check: | |
| `config.manage` — modify project configuration | :material-check: | | |

### Auth Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `users.view` — list users | :material-check: | | |
| `users.manage` — create / edit / deactivate users | :material-check: | | |
| `auth.manage` — manage auth settings | :material-check: | | |
| `audit.view` — view audit logs | :material-check: | | |

### Notebook Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `notebooks.view` — view notebooks | :material-check: | :material-check: | :material-check: |
| `notebooks.execute` — run notebook cells | :material-check: | :material-check: | |
| `notebooks.manage` — create / delete notebooks | :material-check: | :material-check: | |

### Governance Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `governance.view` — view PII reports | :material-check: | :material-check: | :material-check: |
| `governance.manage` — configure governance rules | :material-check: | | |

### Scheduler Permissions

| Permission | Admin | Editor | Viewer |
|-----------|:-----:|:------:|:------:|
| `scheduler.view` — view scheduled jobs | :material-check: | :material-check: | :material-check: |
| `scheduler.manage` — create / edit schedules | :material-check: | | |

??? info "Complete Permission Table (All 29 Permissions)"

    | # | Permission | Admin | Editor | Viewer |
    |---|-----------|:-----:|:------:|:------:|
    | 1 | `source.view` | :material-check: | :material-check: | :material-check: |
    | 2 | `source.view_credentials` | :material-check: | | |
    | 3 | `source.sync` | :material-check: | :material-check: | |
    | 4 | `source.manage` | :material-check: | :material-check: | |
    | 5 | `csv.upload` | :material-check: | :material-check: | |
    | 6 | `csv.delete` | :material-check: | :material-check: | |
    | 7 | `dbt.view` | :material-check: | :material-check: | :material-check: |
    | 8 | `dbt.run` | :material-check: | :material-check: | |
    | 9 | `dbt.manage` | :material-check: | :material-check: | |
    | 10 | `dashboard.view` | :material-check: | :material-check: | :material-check: |
    | 11 | `dashboard.create` | :material-check: | :material-check: | |
    | 12 | `query.execute` | :material-check: | :material-check: | |
    | 13 | `dashboard.manage` | :material-check: | | |
    | 14 | `health.view` | :material-check: | :material-check: | :material-check: |
    | 15 | `logs.view` | :material-check: | :material-check: | :material-check: |
    | 16 | `platform.manage` | :material-check: | | |
    | 17 | `config.view` | :material-check: | :material-check: | |
    | 18 | `config.manage` | :material-check: | | |
    | 19 | `users.view` | :material-check: | | |
    | 20 | `users.manage` | :material-check: | | |
    | 21 | `auth.manage` | :material-check: | | |
    | 22 | `audit.view` | :material-check: | | |
    | 23 | `notebooks.view` | :material-check: | :material-check: | :material-check: |
    | 24 | `notebooks.execute` | :material-check: | :material-check: | |
    | 25 | `notebooks.manage` | :material-check: | :material-check: | |
    | 26 | `governance.view` | :material-check: | :material-check: | :material-check: |
    | 27 | `governance.manage` | :material-check: | | |
    | 28 | `scheduler.view` | :material-check: | :material-check: | :material-check: |
    | 29 | `scheduler.manage` | :material-check: | | |

---

## User Management

### Adding Users

Admins can create new users via CLI or web UI. New users receive an invite link to set their password.

=== "CLI"

    ```bash
    # Create a user with a specific role
    dango auth add-user user@example.com --role editor
    ```

    Output:

    ```
    User created successfully.
    Invite link (expires in 72 hours):
    http://localhost:8800/invite/abc123def456...
    ```

=== "Web UI"

    1. Go to **Admin** → **Users** (`/settings/users`)
    2. Click **Add User**
    3. Enter email and select a role
    4. Copy the invite link and share it with the user

### Accepting Invites

When a user receives an invite link:

1. Open the link in a browser → `/invite/{token}`
2. Set a password on the invite acceptance page
3. Automatically logged in after setting password

!!! warning "Invite Expiry"
    Invite links expire after **72 hours**. If expired, an admin can resend the invite from the web UI or create a new user.

### Changing Roles

```bash
# Promote a user to admin
dango auth change-role user@example.com admin

# Demote to viewer
dango auth change-role user@example.com viewer
```

Role changes take effect on the user's next request (existing sessions are updated). The Metabase role is also synced automatically.

### Deactivating Users

Deactivating a user immediately invalidates all their sessions:

```bash
dango auth deactivate-user user@example.com
```

Deactivated users:

- Cannot log in
- All active sessions are invalidated immediately
- Account data is preserved (can be reactivated)

To reactivate:

```bash
dango auth reactivate-user user@example.com
```

### Deleting Users

Permanently removes a user account:

```bash
dango auth delete-user user@example.com
```

!!! danger "Permanent Action"
    Deletion is permanent and requires confirmation. The user's data, sessions, and API keys are removed.

### Listing Users

```bash
dango auth list-users
```

Shows all users with their role, status (active, inactive, locked, invited, invite expired), and last login.

---

## Last-Admin Protection

Dango prevents you from accidentally losing all admin access:

- Cannot demote the only active admin to editor or viewer
- Cannot deactivate the only active admin
- Cannot delete the only active admin

If you need to change the admin, first promote another user to admin, then modify the original.

---

## Metabase Role Sync

When a user is created or their role changes, Dango automatically syncs the change to Metabase:

| Dango Role | Metabase Role |
|-----------|---------------|
| Admin | Superuser |
| Editor | Member of "Dango Editors" group |
| Viewer | "All Users" group only (default read access) |

The "Dango Editors" group is created automatically in Metabase. Editors get the ability to create questions and dashboards. Viewers can only view existing dashboards shared with "All Users."

---

## Next Steps

- [Authentication](authentication.md) — login flows and session management
- [Two-Factor Auth](two-factor.md) — enable 2FA for user accounts
- [Audit Logging](audit-logging.md) — track user management events
- [Best Practices](best-practices.md) — security recommendations
