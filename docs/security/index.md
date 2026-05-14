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
| **Credential Storage** | API keys stored in `.dlt/secrets.toml` |
| **OAuth Tokens** | Tokens stored in `secrets.toml` (optionally encrypted) |
| **Credential Masking** | Secrets masked in logs |
| **Local Storage** | Data stays on your machine |

### What You Must Do

Security is a shared responsibility:

| Your Responsibility | How |
|--------------------|-----|
| **Protect API keys** | Never commit to git |
| **Secure secrets.toml** | Add to .gitignore |
| **Control access** | Limit who has project access |
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

- [ ] Change default Metabase password
- [ ] Secure backup storage
- [ ] Limit access to project directory
- [ ] Monitor for credential exposure

---

## Security Boundaries

### In Scope (This Documentation)

- Credential storage mechanisms
- OAuth token handling
- Git security patterns
- Secrets management

### Out of Scope

The following are not currently covered:

- Enterprise authentication (SSO, LDAP)
- Row-level security / database access control
- Network-level DDoS protection (recommend IP restriction or CDN)

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
