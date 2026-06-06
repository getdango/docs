#!/usr/bin/env python3
"""Generate docs/cli/cli-reference.md from Click command introspection.

Walks the dango CLI command tree using Click's API to extract command
names, help text, and parameters. Combines with COMMAND_METADATA for
prose, examples, admonitions, and links that aren't derivable from code.

Usage:
    python scripts/generate_cli_reference.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = DOCS_ROOT / "docs" / "cli" / "cli-reference.md"

DANGO_ROOT = SCRIPT_DIR.parent.parent / "dango"
if not DANGO_ROOT.exists():
    print(f"ERROR: dango repo not found at {DANGO_ROOT}", file=sys.stderr)
    print("Scripts must run from the docs repo with dango as a sibling directory.", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(DANGO_ROOT))

# Suppress noisy import warnings during Click introspection
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ---------------------------------------------------------------------------
# Type mapping for Click parameter types
# ---------------------------------------------------------------------------

import click  # noqa: E402


# ---------------------------------------------------------------------------
# Command tree ordering (curated to match manual page)
# ---------------------------------------------------------------------------

# Top-level command order. "---" inserts a blank separator line (│).
TREE_ORDER: list[str] = [
    "init", "start", "stop", "status", "info", "rename",
    "serve", "upgrade", "cleanup", "validate",
    "---",
    "sync", "generate", "run", "docs",
    "---",
    "source", "---",
    "model", "---",
    "config", "---",
    "db", "---",
    "auth", "---",
    "oauth", "---",
    "deploy", "---",
    "remote", "---",
    "schedule", "---",
    "dev", "---",
    "snapshot", "---",
    "monitor", "analyze", "---",
    "governance", "---",
    "notebook", "---",
    "metabase", "---",
    "dashboard", "---",
    "migrate", "---",
    "web",
]

# Children for groups. Each child: (display_name, path_for_lookups)
TREE_SUBGROUPS: dict[str, list[tuple[str, str]]] = {
    "source": [
        ("add", "source.add"),
        ("list", "source.list"),
        ("remove", "source.remove"),
        ("edit", "source.edit"),
    ],
    "model": [
        ("add", "model.add"),
        ("remove", "model.remove"),
    ],
    "config": [
        ("validate", "config.validate"),
        ("show", "config.show"),
        ("do-token", "config.do-token"),
    ],
    "config.do-token": [
        ("clear", "config.do-token.clear"),
    ],
    "db": [
        ("status", "db.status"),
        ("clean", "db.clean"),
    ],
    "auth": [
        ("enable", "auth.enable"),
        ("disable", "auth.disable"),
        ("status", "auth.status"),
        ("add-user", "auth.add-user"),
        ("list-users", "auth.list-users"),
        ("reset-password", "auth.reset-password"),
        ("change-role", "auth.change-role"),
        ("deactivate-user", "auth.deactivate-user"),
        ("reactivate-user", "auth.reactivate-user"),
        ("delete-user", "auth.delete-user"),
        ("unlock", "auth.unlock"),
        ("audit", "auth.audit"),
        ("recover", "auth.recover"),
    ],
    "oauth": [
        ("setup", "oauth.setup"),
        ("status", "oauth.status"),
        ("check", "oauth.check"),
        ("list", "oauth.list"),
        ("remove", "oauth.remove"),
        ("refresh", "oauth.refresh"),
        ("google_sheets", "oauth.google_sheets"),
        ("google_analytics", "oauth.google_analytics"),
        ("google_ads", "oauth.google_ads"),
        ("facebook_ads", "oauth.facebook_ads"),
    ],
    "deploy": [
        ("destroy", "deploy.destroy"),
    ],
    "remote": [
        ("push", "remote.push"),
        ("rollback", "remote.rollback"),
        ("status", "remote.status"),
        ("logs", "remote.logs"),
        ("ssh", "remote.ssh"),
        ("query", "remote.query"),
        ("upgrade", "remote.upgrade"),
        ("resize", "remote.resize"),
        ("migrate", "remote.migrate"),
        ("history", "remote.history"),
        ("sync", "remote.sync"),
        ("env", "remote.env"),
        ("firewall", "remote.firewall"),
        ("domain", "remote.domain"),
        ("backup", "remote.backup"),
        ("auth", "remote.auth"),
    ],
    "remote.env": [
        ("set", "remote.env.set"),
        ("get", "remote.env.get"),
        ("list", "remote.env.list"),
        ("delete", "remote.env.delete"),
    ],
    "remote.firewall": [
        ("list", "remote.firewall.list"),
        ("allow-ip", "remote.firewall.allow-ip"),
        ("allow-all", "remote.firewall.allow-all"),
    ],
    "remote.domain": [
        ("set", "remote.domain.set"),
        ("remove", "remote.domain.remove"),
    ],
    "remote.backup": [
        ("list", "remote.backup.list"),
        ("enable", "remote.backup.enable"),
        ("disable", "remote.backup.disable"),
        ("download", "remote.backup.download"),
        ("restore", "remote.backup.restore"),
    ],
    "remote.auth": [
        ("add-user", "remote.auth.add-user"),
        ("list-users", "remote.auth.list-users"),
        ("remove-user", "remote.auth.remove-user"),
        ("reset-password", "remote.auth.reset-password"),
    ],
    "schedule": [
        ("add", "schedule.add"),
        ("list", "schedule.list"),
        ("remove", "schedule.remove"),
        ("status", "schedule.status"),
        ("enable", "schedule.enable"),
        ("disable", "schedule.disable"),
        ("webhook", "schedule.webhook"),
    ],
    "schedule.webhook": [
        ("add", "schedule.webhook.add"),
        ("list", "schedule.webhook.list"),
        ("remove", "schedule.webhook.remove"),
        ("test", "schedule.webhook.test"),
    ],
    "dev": [
        ("clean", "dev.clean"),
    ],
    "snapshot": [
        ("add", "snapshot.add"),
        ("list", "snapshot.list"),
        ("run", "snapshot.run"),
        ("db", "snapshot.db"),
    ],
    "monitor": [
        ("run", "monitor.run"),
    ],
    "governance": [
        ("drift-report", "governance.drift-report"),
        ("pii-report", "governance.pii-report"),
        ("pii-set", "governance.pii-set"),
        ("pii-list", "governance.pii-list"),
        ("accept", "governance.accept"),
    ],
    "notebook": [
        ("new", "notebook.new"),
        ("open", "notebook.open"),
    ],
    "metabase": [
        ("save", "metabase.save"),
        ("load", "metabase.load"),
        ("refresh", "metabase.refresh"),
    ],
    "dashboard": [
        ("provision", "dashboard.provision"),
    ],
    "migrate": [
        ("status", "migrate.status"),
        ("run", "migrate.run"),
    ],
}


# ---------------------------------------------------------------------------
# Command tree builder (ASCII art)
# ---------------------------------------------------------------------------


def _build_curated_tree() -> list[str]:
    """Build the curated command tree matching the manual page layout.

    Uses TREE_ORDER (top-level) and TREE_SUBGROUPS (children) for
    explicit ordering. TREE_HELP and TREE_ARGS provide display text.
    """
    result: list[str] = []

    # Count non-separator items to determine last
    items = [x for x in TREE_ORDER if x != "---"]
    last_item = items[-1] if items else ""

    for entry in TREE_ORDER:
        if entry == "---":
            result.append("\u2502")
            continue
        _emit_node(entry, entry, "", entry == last_item, result)

    return result


def _emit_node(
    name: str,
    path: str,
    prefix: str,
    is_last: bool,
    result: list[str],
) -> None:
    """Emit a single tree node and recurse into children."""
    connector = "\u2514\u2500\u2500" if is_last else "\u251c\u2500\u2500"
    continuation = "    " if is_last else "\u2502   "

    help_text = TREE_HELP.get(path, "")
    args_hint = TREE_ARGS.get(path, "")
    display = f"{name} {args_hint}" if args_hint else name
    padding = " " * max(1, 41 - len(prefix) - 4 - len(display))
    line = f"{prefix}{connector} {display}{padding}{help_text}"
    result.append(line.rstrip())

    children = TREE_SUBGROUPS.get(path)
    if children:
        child_prefix = prefix + continuation
        for ci, (cname, cpath) in enumerate(children):
            c_last = ci == len(children) - 1
            _emit_node(cname, cpath, child_prefix, c_last, result)


# ---------------------------------------------------------------------------
# Command tree: display names, argument hints, and short help overrides
# ---------------------------------------------------------------------------

# Argument hints shown in the tree after the command name
TREE_ARGS: dict[str, str] = {
    "init": "[PROJECT_NAME]",
    "rename": "NEW_NAME",
    "sync": "[SOURCE_NAME]",
    "run": "[DBT_ARGS]...",
    "auth.add-user": "EMAIL",
    "auth.reset-password": "EMAIL",
    "auth.change-role": "EMAIL ROLE",
    "auth.deactivate-user": "EMAIL",
    "auth.reactivate-user": "EMAIL",
    "auth.delete-user": "EMAIL",
    "auth.unlock": "EMAIL",
    "oauth.setup": "{google|facebook}",
    "oauth.remove": "SOURCE_TYPE",
    "oauth.refresh": "SOURCE_TYPE",
    "remote.query": "SQL",
    "remote.resize": "[SIZE]",
    "remote.sync": "SOURCE",
    "remote.env.set": "KEY=VALUE",
    "remote.env.get": "KEY",
    "remote.env.delete": "KEY",
    "remote.firewall.allow-ip": "IP_ADDRESS",
    "remote.domain.set": "DOMAIN_NAME",
    "remote.backup.download": "NAME",
    "remote.backup.restore": "SOURCE",
    "remote.auth.add-user": "EMAIL",
    "remote.auth.remove-user": "EMAIL",
    "remote.auth.reset-password": "EMAIL",
    "schedule.remove": "NAME",
    "schedule.status": "[NAME]",
    "schedule.enable": "NAME",
    "schedule.disable": "NAME",
    "schedule.webhook.remove": "NAME",
    "schedule.webhook.test": "NAME",
    "notebook.open": "NAME",
    "governance.accept": "SOURCE",
    "governance.pii-set": "SOURCE TABLE COLUMN",
    "source.remove": "SOURCE_NAME",
    "source.edit": "[NAME]",
    "model.remove": "MODEL_NAME",
}

# Short help text overrides (when Click's help text doesn't match docs)
TREE_HELP: dict[str, str] = {
    "init": "Create a new project",
    "start": "Start platform services",
    "stop": "Stop platform services",
    "status": "Show platform status",
    "info": "Show project information",
    "rename": "Rename project",
    "serve": "Production server mode",
    "upgrade": "Upgrade Dango version",
    "cleanup": "Remove old artifacts",
    "validate": "Validate project config",
    "sync": "Sync data from sources",
    "generate": "Generate dbt staging models",
    "run": "Run dbt models",
    "docs": "Generate dbt documentation",
    "source.add": "Add a data source (wizard)",
    "source.list": "List configured sources",
    "source.remove": "Remove a source",
    "source.edit": "Open sources.yml in editor",
    "model.add": "Create a dbt model (wizard)",
    "model.remove": "Remove a dbt model",
    "config.validate": "Validate config files",
    "config.show": "Show current config",
    "config.do-token.clear": "Remove stored DO token",
    "db.status": "Show database status",
    "db.clean": "Remove orphaned tables",
    "auth.enable": "Enable authentication",
    "auth.disable": "Disable authentication",
    "auth.status": "Show auth status",
    "auth.add-user": "Create a new user",
    "auth.list-users": "List all users",
    "auth.reset-password": "Reset user password",
    "auth.change-role": "Change user role",
    "auth.deactivate-user": "Soft-disable a user",
    "auth.reactivate-user": "Re-enable a user",
    "auth.delete-user": "Permanently delete user",
    "auth.unlock": "Unlock locked account",
    "auth.audit": "Query audit log",
    "auth.recover": "Emergency admin recovery",
    "oauth.setup": "OAuth setup wizard",
    "oauth.status": "Show token expiry",
    "oauth.check": "Validate OAuth config",
    "oauth.list": "List all credentials",
    "oauth.remove": "Remove a credential",
    "oauth.refresh": "Re-authenticate",
    "oauth.google_sheets": "Authenticate Google Sheets",
    "oauth.google_analytics": "Authenticate Google Analytics",
    "oauth.google_ads": "Authenticate Google Ads",
    "oauth.facebook_ads": "Authenticate Facebook Ads",
    "deploy": "Deploy wizard (interactive)",
    "deploy.destroy": "Tear down cloud infra",
    "remote.push": "Push files and rebuild",
    "remote.rollback": "Restore from backup",
    "remote.status": "Show server status",
    "remote.logs": "View service logs",
    "remote.ssh": "Open SSH session",
    "remote.query": "Run read-only SQL",
    "remote.upgrade": "Upgrade remote Dango",
    "remote.resize": "Resize server",
    "remote.migrate": "Migrate to new server",
    "remote.history": "Show deploy history",
    "remote.sync": "Trigger remote sync",
    "remote.env.set": "Set env var",
    "remote.env.get": "Get env var (masked)",
    "remote.env.list": "List env vars (masked)",
    "remote.env.delete": "Remove env var",
    "remote.firewall.list": "Show firewall rules",
    "remote.firewall.allow-ip": "Restrict to IP",
    "remote.firewall.allow-all": "Open to public",
    "remote.domain.set": "Configure HTTPS",
    "remote.domain.remove": "Revert to IP-only",
    "remote.backup.list": "List backups",
    "remote.backup.enable": "Enable daily backups",
    "remote.backup.disable": "Disable daily backups",
    "remote.backup.download": "Download from Spaces",
    "remote.backup.restore": "Restore from backup",
    "remote.auth.add-user": "Create remote user",
    "remote.auth.list-users": "List remote users",
    "remote.auth.remove-user": "Remove remote user",
    "remote.auth.reset-password": "Reset remote password",
    "schedule.add": "Add schedule (wizard)",
    "schedule.list": "List schedules",
    "schedule.remove": "Remove a schedule",
    "schedule.status": "Show scheduler status",
    "schedule.enable": "Enable a schedule",
    "schedule.disable": "Disable a schedule",
    "schedule.webhook.add": "Add webhook (wizard)",
    "schedule.webhook.list": "List webhooks",
    "schedule.webhook.remove": "Remove a webhook",
    "schedule.webhook.test": "Test a webhook",
    "dev": "Run dbt on dev copy",
    "dev.clean": "Remove dev artifacts",
    "snapshot.add": "Create dbt snapshot (wizard)",
    "snapshot.list": "List dbt snapshots",
    "snapshot.run": "Execute dbt snapshot",
    "snapshot.db": "Create DuckDB snapshot",
    "monitor.run": "Run monitor analysis",
    "analyze": "Alias for monitor run",
    "governance.drift-report": "Show schema drift",
    "governance.pii-report": "Show PII findings",
    "governance.pii-set": "Set PII override",
    "governance.pii-list": "List PII overrides",
    "governance.accept": "Accept schema drift",
    "notebook.new": "Create notebook",
    "notebook.open": "Open in Marimo",
    "metabase.save": "Export dashboards to files",
    "metabase.load": "Import dashboards from files",
    "metabase.refresh": "Refresh Metabase schema",
    "dashboard.provision": "Create health dashboard",
    "migrate.status": "Show migration status",
    "migrate.run": "Apply pending migrations",
    "web": "Start Web UI server",
}

# ---------------------------------------------------------------------------
# Section definitions — organizes commands into doc sections
# ---------------------------------------------------------------------------

# Each section: (heading, [command_paths], section_key, separators_between)
# command_paths use dots: "remote.env.set"
# separators_between: if True, emit --- between commands in this section

SECTIONS: list[tuple[str, list[str], str, bool]] = [
    # Sections with separators_between=True put --- between each command
    ("Project Lifecycle", [
        "init", "start", "stop", "status", "info", "rename",
        "serve", "upgrade", "cleanup",
    ], "project_lifecycle", True),
    ("Data Operations", [
        "sync", "generate", "run", "docs", "validate",
    ], "data_operations", True),
    ("Source Management", [
        "source.add", "source.list", "source.remove", "source.edit",
    ], "source_management", True),
    ("Model Management", [
        "model.add", "model.remove",
    ], "model_management", True),
    ("Config", [
        "config.validate", "config.show", "config.do-token.clear",
    ], "config", True),
    ("Database", [
        "db.status", "db.clean",
    ], "database", True),
    ("Auth", [
        "auth.enable", "auth.disable", "auth.status", "auth.add-user",
        "auth.list-users", "auth.reset-password",
        "auth.deactivate-user", "auth.reactivate-user",
        "auth.delete-user", "auth.unlock", "auth.change-role",
        "auth.audit", "auth.recover",
    ], "auth", False),
    ("OAuth", [
        "oauth.setup", "oauth.status", "oauth.check", "oauth.list",
        "oauth.remove", "oauth.refresh",
        "oauth.google_sheets", "oauth.google_analytics",
        "oauth.google_ads", "oauth.facebook_ads",
    ], "oauth", False),
    ("Deploy", [
        "deploy", "deploy.destroy",
    ], "deploy", False),
    ("Remote", [
        "remote.push", "remote.rollback", "remote.status", "remote.logs",
        "remote.ssh", "remote.query", "remote.upgrade", "remote.resize",
        "remote.migrate", "remote.history", "remote.sync",
        "remote.env.set", "remote.env.get", "remote.env.list",
        "remote.env.delete",
        "remote.firewall.list", "remote.firewall.allow-ip",
        "remote.firewall.allow-all",
        "remote.domain.set", "remote.domain.remove",
        "remote.backup.list", "remote.backup.enable",
        "remote.backup.disable", "remote.backup.download",
        "remote.backup.restore",
        "remote.auth.add-user", "remote.auth.list-users",
        "remote.auth.remove-user", "remote.auth.reset-password",
    ], "remote", False),
    ("Schedule", [
        "schedule.add", "schedule.list", "schedule.remove",
        "schedule.status", "schedule.enable", "schedule.disable",
        "schedule.webhook.add", "schedule.webhook.list",
        "schedule.webhook.remove", "schedule.webhook.test",
    ], "schedule", False),
    ("Dev", ["dev", "dev.clean"], "dev", False),
    ("Snapshot", [
        "snapshot.add", "snapshot.list", "snapshot.run", "snapshot.db",
    ], "snapshot", False),
    ("Monitor", ["monitor.run", "analyze"], "monitor", False),
    ("Governance", [
        "governance.drift-report", "governance.pii-report",
        "governance.pii-set", "governance.pii-list",
        "governance.accept",
    ], "governance", False),
    ("Notebook", [
        "notebook.new", "notebook.open",
    ], "notebook", False),
    ("Metabase", [
        "metabase.save", "metabase.load", "metabase.refresh",
    ], "metabase", False),
    ("Dashboard", ["dashboard.provision"], "dashboard", False),
    ("Migrate", ["migrate.status", "migrate.run"], "migrate", False),
    ("Web", ["web"], "web", False),
]

# ---------------------------------------------------------------------------
# Per-command metadata: prose, examples, options tables, admonitions
# ---------------------------------------------------------------------------

# Structure: COMMAND_METADATA[cmd_path] = {
#   "heading": str (override h3 heading),
#   "description": str (prose paragraph),
#   "usage": str (code block),
#   "options": list[dict] with keys: option, type?, default?, required?, description
#   "examples": str (code block content),
#   "admonitions": list[str] (admonition blocks),
#   "link": str ([:octicons-...] link),
# }
# Most commands only need a subset of these fields.

COMMAND_METADATA: dict[str, dict] = {
    # --- Project Lifecycle ---
    "init": {
        "description": "Create a new Dango data project.",
        "usage": "dango init [PROJECT_NAME] [OPTIONS]",
        "options": [
            {"option": "`PROJECT_NAME`", "description": "Project directory name (default: current directory `.`)"},
            {"option": "`--skip-wizard`", "description": "Skip interactive wizard, create blank project"},
            {"option": "`--force`", "description": "Force initialization even if project exists"},
        ],
        "examples": "dango init my-analytics\ndango init . --skip-wizard\ndango init my-project --force",
        "link": "[:octicons-arrow-right-24: Full guide](init-start.md)",
    },
    "start": {
        "description": "Start all platform services (Web UI, Metabase, dbt-docs, file watcher).",
        "usage": "dango start [OPTIONS]",
        "options": [
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompts"},
        ],
        "examples": "dango start\ndango start -y",
        "after_examples": 'Access the platform at `http://localhost:<port>` (default: 8800). Change port in `.dango/project.yml` under `platform.port`.',
        "link": "[:octicons-arrow-right-24: Full guide](init-start.md)",
    },
    "stop": {
        "description": "Stop all platform services.",
        "usage": "dango stop [OPTIONS]",
        "options": [
            {"option": "`--all`", "description": "Stop ALL Dango containers from any project"},
        ],
        "examples": "dango stop\ndango stop --all",
    },
    "status": {
        "description": "Show platform status including service health and access URLs.",
        "usage": "dango status",
        "no_options": True,
    },
    "info": {
        "description": "Show project information: name, purpose, stakeholders, data refresh schedule, last sync time.",
        "usage": "dango info",
        "no_options": True,
    },
    "rename": {
        "description": "Rename the project and update its local domain routing.",
        "usage": "dango rename NEW_NAME",
        "arguments": [
            {"argument": "`NEW_NAME`", "description": "New project name (becomes `<new_name>.dango`)"},
        ],
        "after_options": "Updates config, routing table, nginx config, and `/etc/hosts`.",
        "examples": "dango rename my-new-analytics",
    },
    "serve": {
        "description": "Run Dango in production server mode (foreground). Intended for systemd on cloud servers.",
        "usage": "dango serve [OPTIONS]",
        "options": [
            {"option": "`--host`", "type": "TEXT", "default": "`0.0.0.0`", "description": "Bind address"},
            {"option": "`--port`", "type": "INTEGER", "default": "config or 8800", "description": "Port"},
            {"option": "`--workers`", "type": "INTEGER", "default": "1", "description": "Number of uvicorn workers"},
        ],
        "after_options": "Unlike `dango start`, this binds to all interfaces, runs in the foreground, and skips browser/file-watcher.",
    },
    "upgrade": {
        "description": "Upgrade Dango to the latest version (or a specific version), then run pending migrations.",
        "usage": "dango upgrade [OPTIONS]",
        "options": [
            {"option": "`--version TEXT`", "description": "Specific version to install (e.g. `1.2.3`)"},
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompts"},
        ],
        "examples": "dango upgrade\ndango upgrade --version 1.2.3 -y",
        "after_examples": "Restart services with `dango start` after upgrading.",
    },
    "cleanup": {
        "description": "Remove old log archives, dbt artifacts, and Python cache.",
        "usage": "dango cleanup [OPTIONS]",
        "options": [
            {"option": "`--dry-run`", "description": "Show what would be deleted without deleting"},
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompt"},
            {"option": "`--logs-only`", "description": "Only clean log archives, skip dbt/cache"},
            {"option": "`--docker`", "description": "Also prune dangling Docker volumes"},
        ],
        "examples": "dango cleanup --dry-run\ndango cleanup --yes\ndango cleanup --logs-only\ndango cleanup --docker",
    },
    # --- Data Operations ---
    "sync": {
        "description": "Load data from all sources (or a specific source).",
        "usage": "dango sync [SOURCE_NAME] [OPTIONS]",
        "options": [
            {"option": "`SOURCE_NAME`", "type": "positional", "description": "Sync only this source"},
            {"option": "`--source TEXT`", "type": "option", "description": "Sync specific source (deprecated, use positional arg)"},
            {"option": "`--since TEXT`", "type": "date", "description": "Start date for incremental loading (YYYY-MM-DD)"},
            {"option": "`--until TEXT`", "type": "date", "description": "End date for incremental loading (YYYY-MM-DD)"},
            {"option": "`--backfill TEXT`", "type": "duration", "description": "Backfill duration (e.g. `7d`, `2w`, `1m`)"},
            {"option": "`--limit INTEGER`", "type": "number", "description": "Limit rows per source (dev testing)"},
            {"option": "`--full-refresh`", "type": "flag", "description": "Drop existing data and reload from scratch"},
            {"option": "`--dry-run`", "type": "flag", "description": "Show what would be synced without executing"},
            {"option": "`--allow-schema-changes`", "type": "flag", "description": "Allow CSV schema changes (add columns, NULL for missing)"},
            {"option": "`-y`, `--yes`", "type": "flag", "description": "Skip confirmation prompts"},
        ],
        "examples": (
            "dango sync                               # Sync all enabled sources\n"
            "dango sync chess                         # Sync only 'chess'\n"
            "dango sync --since 2024-01-01            # Override start date\n"
            "dango sync --backfill 30d                # Backfill last 30 days\n"
            "dango sync --limit 1000                  # Dev mode: limit rows\n"
            "dango sync --full-refresh                # Reset and reload all\n"
            "dango sync --dry-run                     # Preview only"
        ),
        "link": "[:octicons-arrow-right-24: Full guide](source-sync.md)",
    },
    "generate": {
        "description": "Generate dbt staging models and schema artifacts from data sources.",
        "usage": "dango generate [OPTIONS]",
        "options": [
            {"option": "`--models`", "description": "Generate staging models only"},
            {"option": "`--all`", "description": "Generate all artifacts (models + schema)"},
        ],
        "examples": "dango generate --models\ndango generate --all",
        "post_admonitions": [
            "!!! tip",
            "    Run `dango sync` first to load data into DuckDB before generating models.",
        ],
        "link": "[:octicons-arrow-right-24: Full guide](transform-model.md)",
    },
    "run": {
        "description": "Run dbt models. All dbt build arguments are passed through.",
        "usage": "dango run [DBT_ARGS]...",
        "after_usage": "Any `dbt build` argument works \u2014 `--select`, `--full-refresh`, `--exclude`, etc.",
        "examples": (
            "dango run                            # Run all models\n"
            "dango run --select my_model          # Run specific model\n"
            "dango run --select my_model+         # Model and downstream\n"
            "dango run --select tag:marts         # By tag\n"
            "dango run --full-refresh             # Full refresh incremental models"
        ),
        "link": "[:octicons-arrow-right-24: Full guide](transform-model.md)",
    },
    "docs": {
        "description": "Generate dbt documentation.",
        "usage": "dango docs",
        "no_options": True,
        "after_no_options": "No additional options. After generation, view docs at `http://localhost:<port>/catalog` if the platform is running.",
    },
    "validate": {
        "description": "Validate project configuration and setup.",
        "usage": "dango validate",
        "no_options": True,
        "after_no_options": "No additional options. Checks project structure, config files, source configs, dbt setup, database connectivity, dependencies, and file permissions.",
        "link": "[:octicons-arrow-right-24: Full guide](other-commands.md#dango-validate)",
    },
    # --- Source Management ---
    "source.add": {
        "description": "Add a new data source via interactive wizard. Supports 27+ sources across 9 categories.",
        "usage": "dango source add",
        "no_options": True,
        "after_no_options": "No additional options \u2014 the wizard handles all configuration interactively.",
        "link": "[:octicons-arrow-right-24: Full guide](source-sync.md#adding-sources)",
    },
    "source.list": {
        "description": "List all configured data sources.",
        "usage": "dango source list [OPTIONS]",
        "options": [
            {"option": "`--enabled-only`", "description": "Show only enabled sources"},
        ],
        "examples": "dango source list\ndango source list --enabled-only",
    },
    "source.remove": {
        "description": "Remove a data source.",
        "usage": "dango source remove SOURCE_NAME [OPTIONS]",
        "options": [
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompt"},
        ],
        "examples": "dango source remove my_csv\ndango source remove my_csv --yes",
    },
    "source.edit": {
        "description": "Open `sources.yml` in your default editor (`$EDITOR`).",
        "usage": "dango source edit [NAME]",
        "arguments": [
            {"argument": "`NAME`", "description": "Optional \u2014 hints at the section to focus on"},
        ],
        "examples": "dango source edit\ndango source edit chess",
    },
    # --- Model Management ---
    "model.add": {
        "description": "Create a new dbt model (intermediate or marts layer) via interactive wizard.",
        "usage": "dango model add",
        "after_usage": "Staging models are auto-generated by `dango generate` \u2014 this wizard handles intermediate and marts layers only.",
        "link": "[:octicons-arrow-right-24: Full guide](transform-model.md#dango-model-add)",
    },
    "model.remove": {
        "description": "Remove a custom dbt model and cascade cleanup (SQL file, schema entry, monitors, optionally DuckDB table).",
        "usage": "dango model remove MODEL_NAME [OPTIONS]",
        "options": [
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompt"},
            {"option": "`--dry-run`", "description": "Show what would be removed without executing"},
        ],
        "examples": "dango model remove fct_daily_sales\ndango model remove int_orders --yes\ndango model remove fct_daily_sales --dry-run",
    },
    # --- Config ---
    "config.validate": {
        "description": "Validate all configuration files: `sources.yml`, `project.yml`, and dbt source documentation.",
        "usage": "dango config validate",
        "no_options": True,
    },
    "config.show": {
        "description": "Show current configuration.",
        "usage": "dango config show",
        "no_options": True,
    },
    "config.do-token.clear": {
        "description": "Remove the stored DigitalOcean API token.",
        "usage": "dango config do-token clear",
    },
    # --- Database ---
    "db.status": {
        "description": "Show database status including orphaned tables (tables in DuckDB with no matching source config).",
        "usage": "dango db status",
        "no_options": True,
    },
    "db.clean": {
        "description": "Remove orphaned tables from DuckDB.",
        "usage": "dango db clean [OPTIONS]",
        "options": [
            {"option": "`-y`, `--yes`", "description": "Skip confirmation prompt"},
        ],
        "admonitions": [
            "!!! warning",
            "    This permanently removes tables from DuckDB. Run `dango db status` first to review what will be deleted.",
        ],
        "examples": "dango db clean\ndango db clean --yes",
    },
    # --- Auth ---
    "auth._section_intro": {
        "intro": "User authentication and access management. See the [Auth Commands](auth-commands.md) page for detailed usage.",
    },
    "auth.enable": {
        "heading": "dango auth enable / disable",
        "usage_block": "dango auth enable\ndango auth disable",


    },
    "auth.disable": {"skip": True},
    "auth.status": {
        "usage_block": "dango auth status",

    },
    "auth.add-user": {
        "usage_block": "dango auth add-user EMAIL [OPTIONS]",
        "options": [
            {"option": "`--role [admin\\|editor\\|viewer]`", "description": "User role"},
            {"option": "`--password`", "description": "Generate temp password instead of invite link"},
            {"option": "`--base-url TEXT`", "description": "Base URL for invite links"},
        ],

    },
    "auth.list-users": {
        "usage_block": "dango auth list-users",

    },
    "auth.reset-password": {
        "usage_block": "dango auth reset-password EMAIL",

    },
    "auth.deactivate-user": {
        "heading": "dango auth deactivate-user / reactivate-user",
        "usage_block": "dango auth deactivate-user EMAIL\ndango auth reactivate-user EMAIL",


    },
    "auth.reactivate-user": {"skip": True},
    "auth.delete-user": {
        "usage_block": "dango auth delete-user EMAIL",
        "admonitions": [
            "!!! danger",
            "    Permanently deletes the user. This cannot be undone.",
        ],

    },
    "auth.unlock": {
        "usage_block": "dango auth unlock EMAIL",

    },
    "auth.change-role": {
        "usage_block": "dango auth change-role EMAIL {admin|editor|viewer}",

    },
    "auth.audit": {
        "usage_block": "dango auth audit [OPTIONS]",
        "options": [
            {"option": "`--since TEXT`", "description": "Filter events after date (YYYY-MM-DD)"},
            {"option": "`--type TEXT`", "description": "Filter by event type"},
            {"option": "`--limit INTEGER`", "description": "Max events to show"},
        ],

    },
    "auth.recover": {
        "usage_block": "dango auth recover",
        "after_usage": "Creates a recovery admin account for emergency access.",
        "link": "[:octicons-arrow-right-24: Full guide](auth-commands.md)",
    },
    # --- OAuth ---
    "oauth._section_intro": {
        "intro": "OAuth provider authentication. See the [OAuth Commands](oauth-commands.md) page for detailed usage.",
    },
    "oauth.setup": {
        "usage_block": "dango oauth setup {google|facebook}",

    },
    "oauth.status": {
        "heading": "dango oauth status / check / list",
        "usage_block": "dango oauth status      # Show credential expiry\ndango oauth check       # Validate OAuth config\ndango oauth list        # List all credentials",
    },
    "oauth.check": {"skip": True},
    "oauth.list": {"skip": True},
    "oauth.remove": {
        "usage_block": "dango oauth remove SOURCE_TYPE",

    },
    "oauth.refresh": {
        "usage_block": "dango oauth refresh SOURCE_TYPE",

    },
    "oauth.google_sheets": {
        "heading": "Provider-specific commands",
        "usage_block": (
            "dango oauth google_sheets\n"
            "dango oauth google_analytics\n"
            "dango oauth google_ads\n"
            "dango oauth facebook_ads"
        ),
        "after_usage": "Each walks through the browser-based OAuth flow and saves credentials to `.dlt/secrets.toml`.",
        "link": "[:octicons-arrow-right-24: Full guide](oauth-commands.md)",
    },
    "oauth.google_analytics": {"skip": True},
    "oauth.google_ads": {"skip": True},
    "oauth.facebook_ads": {"skip": True},
    # --- Deploy ---
    "deploy": {
        "description": "Interactive deployment wizard. Supports DigitalOcean, BYOS (bring your own server), and reconnection.",
        "usage": "dango deploy [OPTIONS]",
        "options": [
            {"option": "`--non-interactive`", "description": "All params via flags/env (DigitalOcean)"},
            {"option": "`--reconnect`", "description": "Reconnect to an existing server"},
            {"option": "`--ip TEXT`", "description": "Server IP for `--reconnect`"},
            {"option": "`--region TEXT`", "description": "DO region slug"},
            {"option": "`--size TEXT`", "description": "Droplet size slug"},
            {"option": "`--domain TEXT`", "description": "Custom domain for HTTPS"},
            {"option": "`--admin-email TEXT`", "description": "Admin user email"},
            {"option": "`--admin-password TEXT`", "description": "Admin password (or `DANGO_ADMIN_PASSWORD` env)"},
            {"option": "`--skip-backups`", "description": "Skip automated backup setup"},
            {"option": "`--skip-initial-sync`", "description": "Skip initial data sync"},
            {"option": "`--byos`", "description": "Deploy to an existing server (any provider)"},
            {"option": "`--server-ip TEXT`", "description": "Server IP/hostname for `--byos`"},
            {"option": "`--ssh-user TEXT`", "description": "SSH user for `--byos`"},
            {"option": "`--ssh-key TEXT`", "description": "SSH key path for `--byos`"},
        ],
        "examples": (
            "dango deploy                                    # Interactive wizard\n"
            "dango deploy --non-interactive --region nyc3    # Scripted DO deploy\n"
            "dango deploy --reconnect --ip 1.2.3.4          # Reconnect\n"
            "dango deploy --byos --server-ip 1.2.3.4        # Your own server"
        ),
    },
    "deploy.destroy": {
        "description": "Tear down all cloud infrastructure for this project.",
        "usage": "dango deploy destroy [OPTIONS]",
        "options": [
            {"option": "`--force`", "description": "Skip confirmation and backup prompts"},
            {"option": "`--keep-spaces`", "description": "Keep the Spaces bucket"},
            {"option": "`--keep-ssh-key`", "description": "Keep the SSH key on DigitalOcean"},
        ],
        "admonitions": [
            "!!! danger",
            "    This deletes the Droplet, firewall, SSH key (from DO), and Spaces bucket. Local files and SSH keys are never deleted.",
        ],
        "link": "[:octicons-arrow-right-24: Full guide](deploy-remote.md)",
    },
    # --- Remote ---
    "remote._section_intro": {
        "intro": "Manage the remote cloud server. See the [Deploy & Remote](deploy-remote.md) page for detailed usage.",
    },
    "remote.push": {
        "heading": "Core commands",
        "usage_block": (
            "dango remote push [OPTIONS]           # Push files and rebuild\n"
            "dango remote rollback [OPTIONS]       # Restore from backup\n"
            "dango remote status                   # Show server status\n"
            "dango remote logs [OPTIONS]           # View service logs\n"
            "dango remote ssh                      # Interactive SSH session\n"
            "dango remote query SQL [OPTIONS]      # Read-only SQL query\n"
            "dango remote upgrade [OPTIONS]        # Upgrade remote Dango\n"
            "dango remote resize [SIZE]            # Resize server\n"
            "dango remote migrate [OPTIONS]        # Migrate to new server\n"
            "dango remote history [OPTIONS]        # Show deploy history\n"
            "dango remote sync SOURCE [OPTIONS]    # Trigger remote sync"
        ),
    },
    "remote.rollback": {"skip": True},
    "remote.status": {"skip": True},
    "remote.logs": {"skip": True},
    "remote.ssh": {"skip": True},
    "remote.query": {"skip": True},
    "remote.upgrade": {"skip": True},
    "remote.resize": {"skip": True},
    "remote.migrate": {"skip": True},
    "remote.history": {"skip": True},
    "remote.sync": {"skip": True},
    "remote.env.set": {
        "heading": "Environment variables",
        "usage_block": (
            "dango remote env set KEY=VALUE\n"
            "dango remote env get KEY\n"
            "dango remote env list\n"
            "dango remote env delete KEY"
        ),
    },
    "remote.env.get": {"skip": True},
    "remote.env.list": {"skip": True},
    "remote.env.delete": {"skip": True},
    "remote.firewall.list": {
        "heading": "Firewall",
        "usage_block": (
            "dango remote firewall list\n"
            "dango remote firewall allow-ip IP_ADDRESS\n"
            "dango remote firewall allow-all"
        ),
    },
    "remote.firewall.allow-ip": {"skip": True},
    "remote.firewall.allow-all": {"skip": True},
    "remote.domain.set": {
        "heading": "Domain & HTTPS",
        "usage_block": "dango remote domain set DOMAIN_NAME\ndango remote domain remove",


    },
    "remote.domain.remove": {"skip": True},
    "remote.backup.list": {
        "heading": "Backups",
        "usage_block": (
            "dango remote backup list\n"
            "dango remote backup enable\n"
            "dango remote backup disable\n"
            "dango remote backup download NAME [-o PATH]\n"
            "dango remote backup restore SOURCE [-y]"
        ),
    },
    "remote.backup.enable": {"skip": True},
    "remote.backup.disable": {"skip": True},
    "remote.backup.download": {"skip": True},
    "remote.backup.restore": {"skip": True},
    "remote.auth.add-user": {
        "heading": "Remote user management",
        "usage_block": (
            "dango remote auth add-user EMAIL [--role ROLE]\n"
            "dango remote auth list-users\n"
            "dango remote auth remove-user EMAIL\n"
            "dango remote auth reset-password EMAIL"
        ),
        "link": "[:octicons-arrow-right-24: Full guide](deploy-remote.md)",
    },
    "remote.auth.list-users": {"skip": True},
    "remote.auth.remove-user": {"skip": True},
    "remote.auth.reset-password": {"skip": True},
    # --- Schedule ---
    "schedule._section_intro": {
        "intro": "Manage data sync schedules and webhook notifications. See the [Schedule Commands](schedule-commands.md) page for detailed usage.",
    },
    "schedule.add": {
        "heading": "Schedules",
        "usage_block": (
            "dango schedule add                   # Interactive wizard\n"
            "dango schedule list                  # List all schedules\n"
            "dango schedule remove NAME [-y]      # Remove by name\n"
            "dango schedule status [NAME]         # Overview or single schedule detail\n"
            "dango schedule enable NAME           # Enable a schedule\n"
            "dango schedule disable NAME          # Disable a schedule"
        ),
    },
    "schedule.list": {"skip": True},
    "schedule.remove": {"skip": True},
    "schedule.status": {"skip": True},
    "schedule.enable": {"skip": True},
    "schedule.disable": {"skip": True},
    "schedule.webhook.add": {
        "heading": "Webhooks",
        "usage_block": (
            "dango schedule webhook add           # Interactive wizard\n"
            "dango schedule webhook list          # List webhooks\n"
            "dango schedule webhook remove NAME   # Remove webhook\n"
            "dango schedule webhook test NAME     # Send test payload"
        ),
        "link": "[:octicons-arrow-right-24: Full guide](schedule-commands.md)",
    },
    "schedule.webhook.list": {"skip": True},
    "schedule.webhook.remove": {"skip": True},
    "schedule.webhook.test": {"skip": True},
    # --- Dev ---
    "dev": {
        "description": "Run dbt against a copy of the production database. The production database is never modified.",
        "usage": "dango dev [OPTIONS]",
        "options": [
            {"option": "`-s`, `--select TEXT`", "description": "dbt model selection (e.g. `stg_*`, `my_model+`)"},
            {"option": "`--diff`", "description": "Show row-count comparison after run"},
        ],
        "examples": (
            "dango dev                     # Run all models on dev copy\n"
            "dango dev -s stg_orders       # Run specific model\n"
            "dango dev --diff              # Show diff after run"
        ),
        "after_examples": "The dev database persists at `.dango/dev/warehouse_dev.duckdb` for inspection.",
    },
    "dev.clean": {
        "description": "Remove the dev database and related artifacts.",
        "usage": "dango dev clean",
        "link": "[:octicons-arrow-right-24: Full guide](transform-model.md#dango-dev)",
    },
    # --- Snapshot ---
    "snapshot.add": {
        "description": "Interactive wizard to create a dbt snapshot (SCD Type 2).",
        "usage": "dango snapshot add",
    },
    "snapshot.list": {
        "description": "List configured dbt snapshots.",
        "usage": "dango snapshot list",
    },
    "snapshot.run": {
        "description": "Execute dbt snapshot to capture SCD Type 2 change history.",
        "usage": "dango snapshot run [OPTIONS]",
        "options": [
            {"option": "`-s`, `--select TEXT`", "description": "Run specific snapshot(s) by name"},
        ],
        "examples": "dango snapshot run\ndango snapshot run -s snap_shopify_orders",
    },
    "snapshot.db": {
        "description": "Create a DuckDB read-only snapshot for notebook use.",
        "usage": "dango snapshot db [OPTIONS]",
        "options": [
            {"option": "`-u`, `--user TEXT`", "description": "Username for the snapshot"},
        ],
        "link": "[:octicons-arrow-right-24: Full guide](transform-model.md#snapshots)",
    },
    # --- Monitor ---
    "monitor.run": {
        "description": "Run monitor analysis and display data quality results.",
        "usage": "dango monitor run [OPTIONS]",
        "options": [
            {"option": "`--source TEXT`", "description": "Filter by source name"},
        ],
    },
    "analyze": {
        "description": "Alias for `dango monitor run`.",
        "usage": "dango analyze [OPTIONS]",
        "options": [
            {"option": "`--source TEXT`", "description": "Filter by source name"},
        ],
    },
    # --- Governance ---
    "governance.drift-report": {
        "description": "Show schema drift events.",
        "usage": "dango governance drift-report [OPTIONS]",
        "options": [
            {"option": "`--source TEXT`", "description": "Filter by source name"},
            {"option": "`--table TEXT`", "description": "Filter by table name"},
            {"option": "`--limit INTEGER`", "description": "Max events to show"},
        ],
    },
    "governance.pii-report": {
        "description": "Show PII findings.",
        "usage": "dango governance pii-report [OPTIONS]",
        "options": [
            {"option": "`--source TEXT`", "description": "Filter by source name"},
            {"option": "`--table TEXT`", "description": "Filter by table name"},
            {"option": "`--limit INTEGER`", "description": "Max findings to show"},
        ],
    },
    "governance.pii-set": {
        "description": "Set a PII override for a column.",
        "usage": "dango governance pii-set SOURCE TABLE COLUMN [OPTIONS]",
        "options": [
            {"option": "`--status [pii\\|not_pii]`", "required": "Yes", "description": "PII status to set"},
            {"option": "`--reason TEXT`", "required": "No", "description": "Reason for the override"},
        ],
        "examples": 'dango governance pii-set my_source users email --status pii --reason "Contains user emails"\ndango governance pii-set my_source orders order_id --status not_pii',
    },
    "governance.pii-list": {
        "description": "List PII overrides.",
        "usage": "dango governance pii-list [OPTIONS]",
        "options": [
            {"option": "`--source TEXT`", "description": "Filter by source name"},
        ],
    },
    "governance.accept": {
        "description": "Accept schema drift for a source and resume dbt.",
        "usage": "dango governance accept SOURCE",
    },
    # --- Notebook ---
    "notebook.new": {
        "description": "Create a new Marimo notebook from a starter template.",
        "usage": "dango notebook new [OPTIONS]",
        "options": [
            {"option": "`-t`, `--template [explore\\|quality\\|blank]`", "required": "No", "description": "Starter template"},
            {"option": "`-n`, `--name TEXT`", "required": "Yes", "description": "Notebook name (no extension)"},
        ],
        "examples": "dango notebook new -n my_analysis -t explore\ndango notebook new -n data_quality -t quality",
    },
    "notebook.open": {
        "description": "Open a notebook in Marimo. Acquires a lock, creates a DuckDB snapshot, and starts Marimo. Press Ctrl+C to exit.",
        "usage": "dango notebook open NAME",
    },
    # --- Metabase ---
    "metabase.save": {
        "description": "Export Metabase dashboards and questions to files (YAML format in `metabase/` directory).",
        "usage": "dango metabase save [OPTIONS]",
        "options": [
            {"option": "`--all`", "description": 'Include personal collections (currently exports "Shared" only)'},
            {"option": "`--collections TEXT`", "description": "Specific collections to export (comma-separated)"},
        ],
        "examples": "dango metabase save\ndango metabase save --collections \"Shared,Marketing\"",
    },
    "metabase.load": {
        "description": "Import Metabase dashboards and questions from files.",
        "usage": "dango metabase load [OPTIONS]",
        "options": [
            {"option": "`--overwrite`", "description": "Replace existing dashboards/questions"},
            {"option": "`--dry-run`", "description": "Preview what would be imported"},
        ],
        "admonitions": [
            "!!! warning",
            "    `--overwrite` replaces existing items in Metabase. Uncommitted changes will be lost.",
        ],
        "examples": "dango metabase load\ndango metabase load --dry-run\ndango metabase load --overwrite",
    },
    "metabase.refresh": {
        "description": "Refresh Metabase schema to discover new tables and schemas.",
        "usage": "dango metabase refresh",
    },
    # --- Dashboard ---
    "dashboard.provision": {
        "description": "Provision the Data Pipeline Health dashboard in Metabase.",
        "usage": "dango dashboard provision [OPTIONS]",
        "options": [
            {"option": "`--url TEXT`", "description": "Metabase URL"},
            {"option": "`--username TEXT`", "description": "Metabase admin username (auto-detected from auth DB)"},
            {"option": "`--password TEXT`", "description": "Metabase admin password"},
        ],
        "after_options": "Creates a pre-built dashboard with pipeline health score, source sync status, data freshness indicators, row count trends, and dbt test results.",
    },
    # --- Migrate ---
    "migrate.status": {
        "description": "Show migration status for all databases.",
        "usage": "dango migrate status",
    },
    "migrate.run": {
        "description": "Apply pending migrations.",
        "usage": "dango migrate run [OPTIONS]",
        "options": [
            {"option": "`--db TEXT`", "description": "Apply to a specific database only"},
        ],
    },
    # --- Web ---
    "web": {
        "description": "Start the Web UI backend server only (without Metabase, file watcher, or dbt-docs).",
        "usage": "dango web [OPTIONS]",
        "options": [
            {"option": "`--host TEXT`", "description": "Host to bind to"},
            {"option": "`--port INTEGER`", "description": "Port to bind to"},
            {"option": "`--reload`", "description": "Enable auto-reload (development)"},
        ],
        "link": "[:octicons-arrow-right-24: Full guide](other-commands.md#dango-web)",
    },
}


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


def generate() -> str:
    from dango.cli.main import cli

    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    # --- Auto-gen header ---
    w("<!-- Auto-generated by scripts/generate_cli_reference.py — do not edit manually -->")
    w()
    w("# CLI Reference")
    w()
    w("Complete command reference for all `dango` commands.")
    w()
    w("---")
    w()

    # --- Command Tree ---
    w("## Command Tree")
    w()
    w("```")
    w("dango")

    tree_lines = _build_curated_tree()
    for line in tree_lines:
        w(line)

    w("```")
    w()
    w("---")
    w()

    # --- Global Options ---
    w("## Global Options")
    w()
    w("```bash")
    w("dango [OPTIONS] COMMAND [ARGS]...")
    w("```")
    w()
    w("| Option | Description |")
    w("|--------|-------------|")
    w("| `--version` | Show the version and exit |")
    w("| `--help` | Show help message and exit |")
    w()
    w("Get help for any command:")
    w()
    w("```bash")
    w("dango <command> --help")
    w("dango <group> <subcommand> --help")
    w("```")
    w()
    w("---")
    w()

    # --- Sections ---
    for section_title, cmd_paths, section_key, separators_between in SECTIONS:
        w(f"## {section_title}")
        w()

        # Section intro if present
        intro_key = f"{cmd_paths[0].split('.')[0]}._section_intro"
        intro_meta = COMMAND_METADATA.get(intro_key, {})
        if intro_meta.get("intro"):
            w(intro_meta["intro"])
            w()

        # Filter to visible commands
        visible = [cp for cp in cmd_paths if not COMMAND_METADATA.get(cp, {}).get("skip")]

        for ci, cmd_path in enumerate(visible):
            meta = COMMAND_METADATA.get(cmd_path, {})
            is_last = ci == len(visible) - 1

            # Heading
            heading = meta.get("heading", f"dango {cmd_path.replace('.', ' ')}")
            w(f"### {heading}")
            w()

            # Description
            if meta.get("description"):
                w(meta["description"])
                w()

            # Usage (full-format with ```bash block)
            if meta.get("usage"):
                w("```bash")
                w(meta["usage"])
                w("```")
                w()

            # Usage block (multi-line, no description, used for grouped commands)
            if meta.get("usage_block"):
                w("```bash")
                for uline in meta["usage_block"].split("\n"):
                    w(uline)
                w("```")
                w()

            # After usage prose
            if meta.get("after_usage"):
                w(meta["after_usage"])
                w()

            # No options note
            if meta.get("no_options"):
                after = meta.get("after_no_options", "No additional options.")
                w(after)
                w()

            # Arguments table (separate from options)
            if meta.get("arguments"):
                args = meta["arguments"]
                w("| Argument | Description |")
                w("|----------|-------------|")
                for a in args:
                    w(f"| {a['argument']} | {a['description']} |")
                w()

            # Options table
            if meta.get("options"):
                opts = meta["options"]
                # Detect if we need Required column
                has_required = any("required" in o for o in opts)
                # Detect if we need Type column
                has_type = any("type" in o for o in opts)
                # Detect if we need Default column
                has_default = any("default" in o for o in opts)

                if has_required:
                    w("| Option | Required | Description |")
                    w("|--------|----------|-------------|")
                    for o in opts:
                        opt = o["option"]
                        req = o.get("required", "No")
                        desc = o["description"]
                        w(f"| {opt} | {req} | {desc} |")
                elif has_type and has_default:
                    w("| Option | Type | Default | Description |")
                    w("|--------|------|---------|-------------|")
                    for o in opts:
                        opt = o["option"]
                        t = o.get("type", "")
                        d = o.get("default", "")
                        desc = o["description"]
                        w(f"| {opt} | {t} | {d} | {desc} |")
                elif has_type:
                    w("| Option | Type | Description |")
                    w("|--------|------|-------------|")
                    for o in opts:
                        opt = o["option"]
                        t = o.get("type", "")
                        desc = o["description"]
                        w(f"| {opt} | {t} | {desc} |")
                else:
                    w("| Option | Description |")
                    w("|--------|-------------|")
                    for o in opts:
                        opt = o["option"]
                        desc = o["description"]
                        w(f"| {opt} | {desc} |")
                w()

            # After options prose
            if meta.get("after_options"):
                w(meta["after_options"])
                w()

            # Admonitions (before examples)
            if meta.get("admonitions"):
                for adm_line in meta["admonitions"]:
                    w(adm_line)
                w()

            # Examples
            if meta.get("examples"):
                w("```bash")
                for eline in meta["examples"].split("\n"):
                    w(eline)
                w("```")
                w()

            # After examples prose
            if meta.get("after_examples"):
                w(meta["after_examples"])
                w()

            # Post-admonitions (after examples, before link)
            if meta.get("post_admonitions"):
                for adm_line in meta["post_admonitions"]:
                    w(adm_line)
                w()

            # Link
            if meta.get("link"):
                w(meta["link"])
                w()

            # Separator: always after last command; between commands
            # only if the section uses separators_between
            if is_last or separators_between:
                w("---")
                w()

    # --- Exit Codes ---
    w("## Exit Codes")
    w()
    w("| Code | Meaning |")
    w("|------|---------|")
    w("| `0` | Success |")
    w("| `1` | Error (check output for details) |")
    w()
    w("---")
    w()

    # --- Related Pages ---
    w("## Related Pages")
    w()
    w("- [Init & Start Guide](init-start.md) \u2014 Project setup and service management")
    w("- [Source & Sync](source-sync.md) \u2014 Data source and sync operations")
    w("- [Transform & Model](transform-model.md) \u2014 dbt transformations and model management")
    w("- [Auth Commands](auth-commands.md) \u2014 User authentication details")
    w("- [OAuth Commands](oauth-commands.md) \u2014 OAuth provider setup")
    w("- [Deploy & Remote](deploy-remote.md) \u2014 Cloud deployment and server management")
    w("- [Schedule Commands](schedule-commands.md) \u2014 Scheduled syncs and webhooks")
    w("- [Other Commands](other-commands.md) \u2014 Config, database, governance, and more")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    try:
        content = generate()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content)
    print(f"Generated {OUTPUT_FILE.relative_to(SCRIPT_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
