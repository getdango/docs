# Security

Security guidance for protecting credentials and data in Dango projects.

---

## Overview

This section covers:

- How Dango handles credentials securely
- What you need to do to protect your data
- Best practices for production deployments

---

## Security Model

### What Dango Handles

Dango implements several security measures automatically:

| Feature | Description |
|---------|-------------|
| **Authentication** | Password login with optional 2FA, OAuth (Google/GitHub), API keys |
| **Role-Based Access Control** | 3 roles (Admin, Editor, Viewer) with 29 named permissions |
| **Brute-Force Protection** | Account lockout after 5 failed attempts, rate limiting |
| **Audit Logging** | 44 security event types logged to append-only JSONL |
| **Credential Storage** | API keys stored in `.dlt/secrets.toml` |
| **OAuth Tokens** | Auto-refresh for Google; tokens stored securely |
| **Credential Masking** | Secrets masked in logs and UI |
| **Cloud Hardening** | SSH key-only, fail2ban, auto-TLS, unattended upgrades |

### What You Must Do

Security is a shared responsibility:

| Your Responsibility | How |
|--------------------|-----|
| **Set strong passwords** | Use a password manager; min 8 chars, avoid common passwords |
| **Enable 2FA** | Set up TOTP for admin accounts |
| **Protect API keys** | Never commit to git |
| **Secure secrets.toml** | Add to .gitignore |
| **Review audit logs** | Check for suspicious activity regularly |
| **Backup securely** | Encrypt sensitive backups |

---

## Security Guides

<div class="grid cards" markdown>

-   :material-login: **Authentication**

    ---

    How Dango authentication works: passwords, sessions, and login flows.

    [:octicons-arrow-right-24: Authentication](authentication.md)

-   :material-account-group: **Users & Roles**

    ---

    Manage users with admin, editor, and viewer roles.

    [:octicons-arrow-right-24: Users & Roles](users-roles.md)

-   :material-two-factor-authentication: **Two-Factor Auth**

    ---

    TOTP-based two-factor authentication for enhanced security.

    [:octicons-arrow-right-24: Two-Factor Auth](two-factor.md)

-   :material-key: **Credential Management**

    ---

    How Dango stores and manages API keys and credentials.

    [:octicons-arrow-right-24: Credential Management](credentials.md)

-   :material-shield-account: **OAuth Tokens**

    ---

    OAuth token lifecycle and security considerations.

    [:octicons-arrow-right-24: OAuth Tokens](oauth.md)

-   :material-shield-lock: **Hardening Guide**

    ---

    Security hardening for production and cloud deployments.

    [:octicons-arrow-right-24: Hardening Guide](hardening.md)

-   :material-text-box-search: **Audit Logging**

    ---

    Track security-relevant events with the audit log.

    [:octicons-arrow-right-24: Audit Logging](audit-logging.md)

-   :material-security: **Best Practices**

    ---

    Security best practices for Dango projects.

    [:octicons-arrow-right-24: Best Practices](best-practices.md)

</div>

---

## Quick Security Checklist

### Before Starting

- [ ] Create `.gitignore` with credential patterns
- [ ] Understand where secrets are stored
- [ ] Plan credential rotation strategy

### During Development

- [ ] Use environment variables for sensitive values
- [ ] Never hardcode credentials
- [ ] Review commits before pushing

### For Production

- [ ] Enable [two-factor authentication](two-factor.md) for all admin accounts
- [ ] Configure [session timeouts](authentication.md#session-timeouts) for cloud
- [ ] Set up [IP restriction](hardening.md#ip-restriction) or Cloudflare proxy
- [ ] Set a domain for [auto-TLS](hardening.md#caddy-auto-tls)
- [ ] Review [audit logs](audit-logging.md) regularly
- [ ] Set up [uptime monitoring](hardening.md#monitoring-integration)
- [ ] Secure backup storage

---

## Security Boundaries

### In Scope (This Documentation)

- Authentication (passwords, OAuth, API keys, sessions)
- Two-factor authentication (TOTP)
- Role-based access control (Admin, Editor, Viewer)
- Credential storage and OAuth token management
- Audit logging
- Cloud hardening (SSH, TLS, fail2ban, firewall)
- Git security patterns

### Out of Scope

The following are not currently covered:

- Enterprise authentication (SSO, LDAP)
- Row-level security / database access control
- Network-level DDoS protection (recommend [IP restriction](hardening.md#ip-restriction) or [Cloudflare](hardening.md#cloudflare-proxy))

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue
2. Email security concerns to the maintainers
3. Include reproduction steps
4. Allow time for a fix before disclosure

---

## Next Steps

- [Authentication](authentication.md) - How Dango authentication works
- [Users & Roles](users-roles.md) - User management and permissions
- [Credential Management](credentials.md) - How credentials are stored
- [Hardening Guide](hardening.md) - Production security recommendations
