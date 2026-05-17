#!/usr/bin/env python3
"""Generate docs/reference/permissions.md from dango/auth/permissions.py.

Reads the permissions source file to extract declaration order and inline
comment descriptions, then imports ROLE_PERMISSIONS/Role for role mapping.

Usage:
    python scripts/generate_permissions.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = DOCS_ROOT / "docs" / "reference" / "permissions.md"

# dango source lives at ../../dango relative to the docs repo
DANGO_ROOT = SCRIPT_DIR.parent.parent / "dango"
PERMISSIONS_PY = DANGO_ROOT / "dango" / "auth" / "permissions.py"

# Ensure dango is importable
sys.path.insert(0, str(DANGO_ROOT))

# ---------------------------------------------------------------------------
# Domain mapping — groups permissions into documentation domains
# ---------------------------------------------------------------------------

DOMAIN_MAP: dict[str, str] = {
    "source": "Source",
    "csv": "CSV",
    "dbt": "dbt",
    "dashboard": "Dashboard",
    "query": "Dashboard",  # query.execute lives in Dashboard domain
    "health": "Platform",
    "logs": "Platform",
    "platform": "Platform",
    "config": "Platform",
    "users": "Auth",
    "auth": "Auth",
    "audit": "Auth",
    "notebooks": "Notebooks",
    "governance": "Governance",
    "scheduler": "Scheduler",
}

# Canonical ordering of domains
DOMAIN_ORDER = [
    "Source",
    "CSV",
    "dbt",
    "Dashboard",
    "Platform",
    "Auth",
    "Notebooks",
    "Governance",
    "Scheduler",
]

# Override inline comment text for editorial clarity
DESCRIPTION_OVERRIDE: dict[str, str] = {
    "source.view": "List sources, view status",
    "source.view_credentials": "View OAuth tokens and secrets",
    "source.sync": "Trigger a sync",
    "source.manage": "Add, remove, or configure sources",
    "csv.upload": "Upload CSV files",
    "csv.delete": "Delete uploaded CSV files",
    "dbt.view": "View dbt models and docs",
    "dbt.run": "Trigger dbt runs",
    "dbt.manage": "Add or remove dbt models",
    "dashboard.view": "View Metabase dashboards",
    "dashboard.create": "Create and edit dashboards",
    "dashboard.manage": "Manage Metabase settings",
    "query.execute": "Run ad-hoc SQL queries",
    "health.view": "View platform health and status",
    "logs.view": "View activity logs",
    "platform.manage": "Start, stop, or configure platform",
    "config.view": "View project configuration",
    "config.manage": "Modify project configuration",
    "users.view": "List users",
    "users.manage": "Create, edit, or deactivate users",
    "auth.manage": "Manage auth settings (2FA policy, etc.)",
    "audit.view": "View audit logs",
    "notebooks.view": "View notebooks",
    "notebooks.execute": "Run notebook cells",
    "notebooks.manage": "Create or delete notebooks",
    "governance.view": "View PII reports and schema drift",
    "governance.manage": "Configure governance rules",
    "scheduler.view": "View scheduled jobs",
    "scheduler.manage": "Create or edit schedules",
}

# Explicit ordering within the Dashboard domain (source file order differs)
DOMAIN_PERMISSION_ORDER: dict[str, list[str]] = {
    "Dashboard": [
        "dashboard.view",
        "dashboard.create",
        "dashboard.manage",
        "query.execute",
    ],
}


# ---------------------------------------------------------------------------
# Parse permissions from source file (preserves declaration order)
# ---------------------------------------------------------------------------


def parse_permissions_from_source(
    path: Path,
) -> list[tuple[str, str]]:
    """Return [(permission_name, description), ...] in declaration order."""
    text = path.read_text()

    # Find the PERMISSIONS frozenset block
    match = re.search(
        r"PERMISSIONS:\s*frozenset\[str\]\s*=\s*frozenset\(\{(.*?)\}\)",
        text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError("Could not find PERMISSIONS frozenset in source")

    block = match.group(1)
    results: list[tuple[str, str]] = []

    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Match: "perm.name",  # description
        m = re.match(r'"([^"]+)".*?#\s*(.+)', line)
        if m:
            perm = m.group(1)
            desc = m.group(2).strip().rstrip(",")
            # Apply editorial overrides
            desc = DESCRIPTION_OVERRIDE.get(perm, desc)
            # Capitalise first letter
            desc = desc[0].upper() + desc[1:] if desc else desc
            results.append((perm, desc))

    return results


# ---------------------------------------------------------------------------
# Build role check
# ---------------------------------------------------------------------------


def get_domain(perm: str) -> str:
    """Map permission to its documentation domain."""
    prefix = perm.split(".")[0]
    return DOMAIN_MAP.get(prefix, prefix.title())


def _cell(perm: str, role_perms: frozenset[str]) -> str:
    """Return ' :white_check_mark: ' or '' for a table cell."""
    if "*" in role_perms or perm in role_perms:
        return " :white_check_mark: "
    return " "


def _perm_row(
    perm: str,
    admin: frozenset[str],
    editor: frozenset[str],
    viewer: frozenset[str],
    desc: str | None = None,
) -> str:
    """Build a markdown table row for a permission."""
    a = _cell(perm, admin)
    e = _cell(perm, editor)
    v = _cell(perm, viewer)
    base = f"| `{perm}` |{a}|{e}|{v}|"
    if desc is not None:
        return f"{base} {desc} |"
    return base


# ---------------------------------------------------------------------------
# Generate the markdown
# ---------------------------------------------------------------------------


def generate() -> str:
    """Generate the full permissions.md content."""
    from dango.auth.models import Role
    from dango.auth.permissions import ROLE_PERMISSIONS

    perms = parse_permissions_from_source(PERMISSIONS_PY)

    admin_perms = ROLE_PERMISSIONS[Role.ADMIN]
    editor_perms = ROLE_PERMISSIONS[Role.EDITOR]
    viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]

    # Count per role
    # Admin has wildcard, so count = all
    editor_count = len(editor_perms)
    viewer_count = len(viewer_perms)

    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    # --- Header ---
    w("# Permissions Matrix")
    w()
    w(
        "Complete reference for Dango's role-based access control system."
    )
    w()
    w("---")
    w()

    # --- Overview ---
    w("## Overview")
    w()
    w(
        f"Dango uses a **role-based access control (RBAC)** system with "
        f"{len(ROLE_PERMISSIONS)} roles and {len(perms)} permissions. "
        f"Permissions follow a `<domain>.<action>` naming convention "
        f"across {len(DOMAIN_ORDER)} domains."
    )
    w()
    w(
        "Authentication is **always enabled** by default for both local "
        "and cloud deployments. The initial admin account is created "
        "during `dango init`."
    )
    w()
    w("---")
    w()

    # --- Roles table ---
    w("## Roles")
    w()
    w("| Role | Permissions | Description |")
    w("|------|-------------|-------------|")
    w(
        "| **Admin** | All (wildcard `*`) | Full access to all features "
        "including user management and platform configuration |"
    )
    w(
        f"| **Editor** | {editor_count} permissions | Can sync sources, "
        f"run dbt, create dashboards, manage notebooks, and view "
        f"governance data |"
    )
    w(
        f"| **Viewer** | {viewer_count} permissions | Read-only access to "
        f"sources, models, dashboards, health, logs, notebooks, "
        f"schedules, and governance |"
    )
    w()
    w("---")
    w()

    # --- Permission Matrix (full table) ---
    w("## Permission Matrix")
    w()
    w(f"The complete mapping of all {len(perms)} permissions to roles:")
    w()
    w("| Permission | Admin | Editor | Viewer | Description |")
    w("|------------|:-----:|:------:|:------:|-------------|")

    # Build lookup for descriptions
    perm_desc = dict(perms)

    # Reorder: group by domain using DOMAIN_ORDER, apply overrides
    all_domain_perms: dict[str, list[str]] = {d: [] for d in DOMAIN_ORDER}
    for perm, _desc in perms:
        domain = get_domain(perm)
        all_domain_perms[domain].append(perm)
    for domain, order in DOMAIN_PERMISSION_ORDER.items():
        if domain in all_domain_perms:
            all_domain_perms[domain] = order

    for domain in DOMAIN_ORDER:
        for perm in all_domain_perms.get(domain, []):
            desc = perm_desc.get(perm, "")
            w(_perm_row(perm, admin_perms, editor_perms, viewer_perms, desc))
    w()
    w("---")
    w()

    # --- Permissions by Domain ---
    w("## Permissions by Domain")
    w()

    # Group permissions by domain, preserving declaration order
    domain_perms: dict[str, list[str]] = {d: [] for d in DOMAIN_ORDER}
    for perm, _desc in perms:
        domain = get_domain(perm)
        domain_perms[domain].append(perm)

    # Apply explicit ordering overrides
    for domain, order in DOMAIN_PERMISSION_ORDER.items():
        if domain in domain_perms:
            domain_perms[domain] = order

    for domain in DOMAIN_ORDER:
        dp = domain_perms[domain]
        if not dp:
            continue
        w(f"### {domain} ({len(dp)} permission{'s' if len(dp) != 1 else ''})")
        w()
        w("| Permission | Admin | Editor | Viewer |")
        w("|------------|:-----:|:------:|:------:|")
        for perm in dp:
            w(_perm_row(perm, admin_perms, editor_perms, viewer_perms))
        w()

    w("---")
    w()

    # --- Session & Security (static content) ---
    w("## Session & Security")
    w()
    w("### Session Timeouts")
    w()
    w(
        "Session timeouts are configured in the `auth` section of "
        "`project.yml`:"
    )
    w()
    w("| Setting | Local Default | Cloud Default | Description |")
    w("|---------|:------------:|:-------------:|-------------|")
    w(
        "| `idle_timeout_minutes` | 1440 (24 hours) | 60 (1 hour) | "
        "Session invalidated after this period of inactivity |"
    )
    w(
        "| `session_max_days` | 365 (1 year) | 30 (30 days) | Maximum "
        "session lifetime regardless of activity |"
    )
    w()
    w("!!! info")
    w(
        "    Cloud defaults are set during `dango deploy` and differ "
        "from local defaults for security. You can customize both in "
        "`project.yml`."
    )
    w()
    w("### Account Lockout")
    w()
    w("| Setting | Default | Description |")
    w("|---------|:-------:|-------------|")
    w(
        "| `max_attempts` | 5 | Failed login attempts before account "
        "is locked |"
    )
    w("| `lockout_minutes` | 15 | Duration of account lockout |")
    w()
    w(
        "Locked accounts can be unlocked by an admin via "
        "`POST /api/admin/users/{user_id}/unlock`."
    )
    w()
    w("### Rate Limiting")
    w()
    w("| Endpoint Group | Default Limit | Window |")
    w("|----------------|:------------:|:------:|")
    w("| Login (`/api/auth/login`) | 10 requests | 60 seconds |")
    w("| General API | 200 requests | 60 seconds |")
    w()
    w(
        "Rate limiting is enabled by default. Localhost requests are "
        "exempt. Configure trusted proxy IPs via "
        "`auth.rate_limit.trusted_proxies` for correct client IP "
        "detection behind a reverse proxy."
    )
    w()
    w("### Two-Factor Authentication (2FA)")
    w()
    w("- Optional by default (`require_2fa: false`)")
    w(
        "- When enabled globally, all users must set up TOTP before "
        "accessing the platform"
    )
    w(
        "- Uses TOTP (Time-based One-Time Password) with standard "
        "authenticator apps"
    )
    w("- Recovery codes are generated during 2FA setup")
    w()
    w("---")
    w()

    # --- API Key Authentication (static content) ---
    w("## API Key Authentication")
    w()
    w(
        "API keys provide programmatic access without interactive login."
    )
    w()
    w("### Key Format")
    w()
    w("```")
    w("dango_ak_<32-character-url-safe-random-token>")
    w("```")
    w()
    w(
        "- **Prefix**: `dango_ak_` (used to identify Dango API keys)"
    )
    w(
        "- **Display prefix**: First 12 characters shown for "
        "identification (e.g., `dango_ak_XYZ`)"
    )
    w(
        "- **Storage**: Only a SHA-256 hash is stored in the database; "
        "the raw key is shown once at creation"
    )
    w()
    w("### Usage")
    w()
    w(
        "Include the API key as a Bearer token in the `Authorization` "
        "header:"
    )
    w()
    w("```bash")
    w(
        'curl -H "Authorization: Bearer dango_ak_..." '
        "http://localhost:8800/api/sources"
    )
    w("```")
    w()
    w("### Key Properties")
    w()
    w("| Property | Default | Description |")
    w("|----------|---------|-------------|")
    w(
        "| Expiry | None (never expires) | Optional per-key expiry "
        "date |"
    )
    w(
        "| Scope | Full user permissions | Key inherits all permissions "
        "of the associated user |"
    )
    w("| Revocation | Manual | Revoke via API or admin UI |")
    w()
    w("---")
    w()

    # --- Related Pages (static content) ---
    w("## Related Pages")
    w()
    w(
        "- [Authentication & Security](../security/authentication.md) "
        "— Login flows, session management, 2FA setup"
    )
    w(
        "- [Users & Roles](../security/users-roles.md) — User "
        "management, role assignment, invitations"
    )
    w(
        "- [API Reference](api.md) — Endpoint-level permission "
        "requirements"
    )

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        content = generate()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content)
    print(f"Generated {OUTPUT_FILE.relative_to(SCRIPT_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
