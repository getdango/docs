# Team Setup Guide

Set up Dango for a small team with multiple users and roles.

---

## What You'll Set Up

By the end of this guide, you'll have:

- An admin account with full access
- Team members with appropriate roles (editor, viewer)
- Shared dashboards visible to the team
- Optionally, a cloud deployment for remote access

**Duration**: ~20 minutes

---

## Prerequisites

- A Dango project with data already synced (complete the [E-commerce Tutorial](ecommerce-tutorial.md) or similar first)
- `dango start` running

---

## Step 1: Verify Auth Is Enabled

Dango v1 enables authentication by default. Verify your setup:

```bash
dango auth status
```

Expected output shows auth enabled, your admin account, and session settings.

If auth is not enabled (e.g., you initialized with an older version):

```bash
dango auth enable
```

You'll be prompted to set an admin password.

---

## Step 2: Understand Roles

Dango has three roles with distinct permissions:

| Role | Access | Use For |
|------|--------|---------|
| **Admin** | Full access — all operations, user management, settings | Project owners, data engineers |
| **Editor** | Source management, dbt operations, dashboard creation, notebooks, scheduling | Analysts, data team members |
| **Viewer** | Read-only — view dashboards, sources, models, logs | Stakeholders, executives |

??? info "Detailed Permissions"
    - **Admin**: Wildcard access to all operations
    - **Editor**: Source CRUD, CSV upload, dbt build/run, dashboard create/edit, notebook access, scheduler management
    - **Viewer**: View sources, dbt models, dashboards, health status, logs, notebooks (read-only), schedules

    See [Users & Roles](../security/users-roles.md) for the full permissions matrix.

---

## Step 3: Add Team Members

Add users with the `dango auth add-user` command. Each user gets an invite link they can use to set their own password.

### Add an Editor

```bash
dango auth add-user analyst@yourcompany.com --role editor
```

Output:
```
User created: analyst@yourcompany.com (role: editor)
Invite link (expires in 72 hours):
  http://localhost:8800/invite/abc123...

Share this link with the user to complete setup.
```

### Add a Viewer

```bash
dango auth add-user ceo@yourcompany.com --role viewer
```

### Add Another Admin

```bash
dango auth add-user lead@yourcompany.com --role admin
```

### Verify Users

```bash
dango auth list-users
```

!!! tip "Password-Based Setup"
    If you prefer to set a temporary password instead of using invite links, use the `--password` flag:

    ```bash
    dango auth add-user analyst@yourcompany.com --role editor --password
    ```

    The user will be prompted to change the password on first login.

---

## Step 4: Accept Invites

Share the invite link with each team member. When they visit the link:

1. They see a "Set Your Password" form
2. They choose a password (minimum 8 characters, NIST-compliant — no special character requirements)
3. After setting their password, they're automatically logged in
4. They see only what their role permits

!!! warning "Invite Expiry"
    Invite links expire after **72 hours**. If an invite expires before the user accepts it, generate a new one:

    ```bash
    dango auth reset-password analyst@yourcompany.com
    ```

---

## Step 5: Manage Ongoing Access

### Change a User's Role

```bash
dango auth change-role analyst@yourcompany.com admin
```

### Deactivate a User

Deactivation preserves the user record but prevents login:

```bash
dango auth deactivate-user analyst@yourcompany.com
```

To reactivate later:

```bash
dango auth reactivate-user analyst@yourcompany.com
```

### Reset a Password

```bash
dango auth reset-password analyst@yourcompany.com
```

### Delete a User

```bash
dango auth delete-user analyst@yourcompany.com
```

!!! note "Last Admin Protection"
    Dango prevents you from demoting, deactivating, or deleting the last admin account. There must always be at least one active admin.

---

## Step 6: Deploy for Team Access (Optional)

For remote team access, deploy Dango to a cloud server:

```bash
dango deploy
```

The deploy wizard walks you through server provisioning. Once deployed, regenerate invite links with the server URL:

```bash
dango auth add-user remote-user@yourcompany.com --role editor --base-url https://dango.yourcompany.com
```

See [Deployment](../deployment/digitalocean.md) for the full deployment guide.

---

## Step 7: Dashboard Sharing Workflow

Team members access dashboards through Metabase, which is integrated into the Dango web UI.

### Share Dashboards

1. Open the Dango web UI at `http://localhost:8800` (or your server URL)
2. Log in with your credentials
3. Navigate to **Metabase** via the sidebar
4. Create dashboards in the "Shared" collection so all team members can see them
5. Personal dashboards go in each user's personal collection

### Export Dashboards

Save dashboard configurations to version control:

```bash
dango metabase save
```

This exports dashboards and questions as YAML files under `metabase/dashboards/` and `metabase/questions/`. See [Save & Load Dashboards](../dashboards/save-load.md) for details.

---

## Step 8: Audit and Monitor

Track who's accessing your Dango instance:

```bash
# View recent auth events
dango auth audit

# Filter by date
dango auth audit --since 2024-01-15

# Filter by event type
dango auth audit --type login_success

# Limit results
dango auth audit --limit 20
```

See [Audit Logging](../security/audit-logging.md) for the full list of audited events.

---

## Troubleshooting

### Locked Out

If all admin accounts are locked or passwords forgotten:

```bash
dango auth recover
```

This creates a recovery admin account.

### Expired Invite

Generate a new invite by resetting the user's password:

```bash
dango auth reset-password user@yourcompany.com
```

### Wrong Role Assigned

Change the role at any time:

```bash
dango auth change-role user@yourcompany.com viewer
```

### User Can't See Dashboards

- Verify their role with `dango auth list-users`
- Ensure dashboards are in the "Shared" collection in Metabase, not a personal collection
- Check that the user's account is active (not deactivated)

---

## Summary

You've set up Dango for team access:

- [x] Auth verified and admin account configured
- [x] Team members added with appropriate roles
- [x] Invite workflow for self-service password setup
- [x] User management commands for ongoing access control
- [x] Audit logging for security monitoring

---

## Next Steps

- [Authentication](../security/authentication.md) - Deep dive into auth configuration
- [Users & Roles](../security/users-roles.md) - Full permissions reference
- [Deployment](../deployment/digitalocean.md) - Deploy for remote team access
- [Audit Logging](../security/audit-logging.md) - Monitor access and changes
