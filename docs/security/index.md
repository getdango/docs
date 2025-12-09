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
| **Credential Storage** | API keys stored via system keyring |
| **OAuth Tokens** | Tokens encrypted at rest |
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

-   :material-key: **Credential Management**

    ---

    How Dango stores and manages API keys and credentials.

    [:octicons-arrow-right-24: Credential Management](credentials.md)

-   :material-shield-account: **OAuth Tokens**

    ---

    OAuth token lifecycle and security considerations.

    [:octicons-arrow-right-24: OAuth Tokens](oauth.md)

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

Dango is a local-first MVP. The following are not currently covered:

- Network security (Dango runs locally)
- Database access control (DuckDB is single-user)
- Enterprise authentication (SSO, LDAP)
- Audit logging for compliance

These features may be added in future cloud-enabled versions.

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** open a public GitHub issue
2. Email security concerns to the maintainers
3. Include reproduction steps
4. Allow time for a fix before disclosure

---

## Next Steps

- [Credential Management](credentials.md) - How credentials are stored
- [OAuth Tokens](oauth.md) - Token security details
- [Best Practices](best-practices.md) - Security recommendations
