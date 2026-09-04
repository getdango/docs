#!/usr/bin/env python3
"""Generate docs/data-sources/source-catalog.md from source registry.

Imports SOURCE_REGISTRY and AuthType from dango, then combines with
supplementary editorial data (display name overrides, incremental
overrides, notes, category ordering) to produce the full catalog page.

Usage:
    python scripts/generate_source_catalog.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DOCS_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = DOCS_ROOT / "docs" / "data-sources" / "source-catalog.md"

DANGO_ROOT = SCRIPT_DIR.parent.parent / "dango"
if not DANGO_ROOT.exists():
    print(f"ERROR: dango repo not found at {DANGO_ROOT}", file=sys.stderr)
    print("Scripts must run from the docs repo with dango as a sibling directory.", file=sys.stderr)
    sys.exit(1)
sys.path.insert(0, str(DANGO_ROOT))

# ---------------------------------------------------------------------------
# Supplementary editorial data (not derivable from registry)
# ---------------------------------------------------------------------------

# Display name overrides where the docs page differs from registry
DISPLAY_NAME_OVERRIDE: dict[str, str] = {
    "local_files": "File Import (CSV, JSON, Parquet)",
    "rest_api": "REST API (Generic)",
    "dlt_native": "dlt Native (Advanced)",
    "filesystem": "Files & Cloud Storage",
    "google_analytics": "Google Analytics 4",
    "matomo": "Matomo",
    "inbox": "Email (IMAP)",
    "kafka": "Apache Kafka",
    "kinesis": "AWS Kinesis",
    "chess": "Chess.com",
}

# Incremental column overrides (registry only has boolean)
INCREMENTAL_OVERRIDE: dict[str, str] = {
    "dlt_native": "Varies",
    "mux": "Partial",
    "salesforce": "Partial",
    "zendesk": "Partial",
    "workable": "Partial",
    "stripe": "Partial",
    "shopify": "\u2014",  # em dash
    "slack": "Partial",
    "chess": "Partial",
    "asana": "Partial",
    "personio": "Partial",
    "github": "No",  # registry says True but actual behavior is full refresh
}

# Notes / guide links for each source
NOTES: dict[str, str] = {
    "local_files": "[Local Files Guide](local-files/index.md)",
    "rest_api": "Connect to any REST API \u2014 [REST API Guide](rest-api.md)",
    "dlt_native": "Bring any dlt source \u2014 [Custom Sources Guide](custom-sources.md)",
    "csv": "**Hidden** \u2014 use `local_files` instead",
    "filesystem": "**Hidden** \u2014 use `local_files` for local files",
    "google_sheets": "[Google Sheets Guide](google-sheets.md)",
    "facebook_ads": "[Facebook Ads Guide](facebook-ads.md)",
    "google_analytics": "[Google Analytics Guide](google-analytics.md)",
    "google_ads": "[Google Ads Guide](google-ads.md)",
    "airtable": "Bases and tables",
    "mux": "Video analytics",
    "matomo": "**Coming Soon**",
    "hubspot": "[HubSpot Guide](hubspot.md) \u2014 contacts, companies, deals, tickets",
    "salesforce": "[Salesforce Guide](salesforce.md)",
    "pipedrive": "16 resources available",
    "freshdesk": "Support tickets and contacts",
    "zendesk": "Support tickets and users",
    "workable": "Applicant tracking",
    "jira": "**Coming Soon**",
    "asana": "**Coming Soon**",
    "stripe": "[Stripe Guide](stripe.md) \u2014 charges, customers, subscriptions",
    "shopify": "**Coming Soon** \u2014 pending OAuth flow update",
    "github": "[GitHub Guide](github.md) \u2014 issues, PRs, commits",
    "slack": "[Slack Guide](slack.md) \u2014 channels, messages, users",
    "notion": "Pages and databases",
    "inbox": "IMAP email import",
    "postgres": "Full table or incremental loading",
    "mongodb": "Collections with optional filtering",
    "kafka": "Consumer-based ingestion",
    "kinesis": "AWS stream processing",
    "chess": "Public API \u2014 great for testing",
    "strapi": "**Coming Soon**",
    "personio": "**Coming Soon**",
}

# Explicit ordering of sources within each category
CATEGORY_SOURCE_ORDER: dict[str, list[str]] = {
    "Local & Custom": ["local_files", "rest_api", "dlt_native", "csv", "filesystem"],
    "Marketing & Analytics": [
        "google_sheets", "facebook_ads", "google_analytics",
        "google_ads", "airtable", "mux", "matomo",
    ],
    "Business & CRM": [
        "hubspot", "salesforce", "pipedrive", "freshdesk",
        "zendesk", "workable", "jira", "asana",
    ],
    "E-commerce & Payment": ["stripe", "shopify"],
    "Development": ["github"],
    "Communication": ["slack"],
    "Files & Storage": ["notion", "inbox"],
    "Databases": ["postgres", "mongodb", "sql_database"],
    "Streaming": ["kafka", "kinesis"],
    "Other": ["chess", "strapi", "personio", "scrapy"],
}

# Category descriptions
CATEGORY_DESC: dict[str, str] = {
    "Local & Custom": "Sources for local files, generic APIs, and advanced dlt integrations.",
    "Marketing & Analytics": "Sources for advertising platforms, analytics tools, and marketing data.",
    "Business & CRM": "Sources for CRM platforms, helpdesks, project management, and HR tools.",
    "E-commerce & Payment": "Sources for payment processors and online stores.",
    "Development": "Sources for developer tools and code repositories.",
    "Communication": "Sources for team messaging and collaboration.",
    "Files & Storage": "Sources for knowledge bases and email.",
    "Databases": "Sources for relational and document databases.",
    "Streaming": "Sources for real-time data streams.",
    "Other": "Utility and niche sources.",
}

# Category-level admonitions (placed after the table)
CATEGORY_ADMONITIONS: dict[str, list[str]] = {
    "Databases": [
        '!!! note "Other databases"',
        "    Connect to MySQL, SQL Server, and other databases via the "
        "`dlt_native` source type using dlt's "
        "[sql_database](https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database) "
        "source. See [Database Sources](database-sources.md).",
    ],
}

# SourceType members with no SOURCE_REGISTRY entry — recognized as valid
# `type:` values (accepted by dango.config.models.SourceType) but not yet
# backed by wizard/registry metadata. Rendered with fixed placeholder cells
# rather than guessed auth/incremental data we can't verify from the registry.
NOT_YET_IMPLEMENTED: dict[str, dict[str, str]] = {
    "sql_database": {
        "display_name": "Generic SQL Database",
        "note": (
            "Recognized as a source type, but not yet exposed as a dedicated "
            "wizard entry or registry-backed config — use `dlt_native` with "
            "dlt's `sql_database` source today"
        ),
    },
    "scrapy": {
        "display_name": "Scrapy (Web Scraping)",
        "note": "Reserved for a future release — not yet implemented",
    },
}

# Auth type display mapping
AUTH_TYPE_DISPLAY: dict[str, str] = {
    "none": "None",
    "api_key": "API Key",
    "oauth": "OAuth",
    "basic": "Basic",
    "service_account": "Service Account",
}

# Coming Soon reasons
COMING_SOON_REASONS: dict[str, str] = {
    "shopify": "Shopify requires Authorization Code Grant OAuth \u2014 flow not yet implemented",
    "matomo": "Awaiting testing and validation",
    "jira": "Awaiting testing and validation",
    "asana": "Awaiting testing and validation",
    "strapi": "Awaiting testing and validation",
    "personio": "Awaiting testing and validation",
    "sql_database": "Recognized as a source type but not yet exposed as a dedicated wizard "
    "entry or registry config \u2014 use `dlt_native` with dlt's `sql_database` source today",
    "scrapy": "Reserved for a future release \u2014 not yet implemented",
}


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


def generate() -> str:
    from dango.config.models import SourceType
    from dango.ingestion.sources.registry import SOURCE_REGISTRY

    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    # The registry can drift from SourceType in both directions (e.g. a
    # leftover registry key with no matching SourceType member, like a
    # dead "mysql" entry). SourceType is the actual source of truth for
    # what `type:` values dango accepts, so counts are derived from it,
    # not from raw `len(SOURCE_REGISTRY)`.
    valid_types = {s.value for s in SourceType}

    total = len(valid_types)
    wizard_count = sum(
        1 for k in valid_types if SOURCE_REGISTRY.get(k, {}).get("wizard_enabled")
    )
    coming_soon = [
        k for k in valid_types
        if k not in ("csv", "filesystem")
        and not SOURCE_REGISTRY.get(k, {}).get("wizard_enabled")
    ]
    hidden = [k for k in valid_types if k in ("csv", "filesystem")]

    # --- Auto-gen header ---
    w("<!-- Auto-generated by scripts/generate_source_catalog.py — do not edit manually -->")
    w()
    w("# Source Catalog")
    w()
    w(
        f"Complete catalog of all {total} data sources supported by Dango, "
        f"grouped by category."
    )
    w()
    w("---")
    w()

    # --- Overview ---
    w("## Overview")
    w()
    w(
        f"Dango ships with **{total} built-in source connectors** powered by "
        f"[dlt (data load tool)](https://dlthub.com/docs):"
    )
    w()
    w(f"- **{wizard_count} wizard-enabled** \u2014 add via `dango source add` interactive wizard")
    w(f"- **{len(coming_soon)} coming soon** \u2014 registered but disabled pending testing")
    w(f"- **{len(hidden)} hidden** \u2014 legacy aliases (use the recommended alternative)")
    w()
    w(
        "Every source is defined in the [source registry]"
        "(../reference/source-registry.md) with its authentication type, "
        "default resources, and configuration parameters."
    )
    w()
    w("### Reading the Tables")
    w()
    w(
        "Each category table includes an **Incremental** column indicating "
        "sync behavior:"
    )
    w()
    w(
        "- **Yes** \u2014 supports incremental sync "
        "(only new/changed data loaded on each run)"
    )
    w(
        "- **Partial** \u2014 some resources are incremental, "
        "others always reload all data"
    )
    w("- **No** \u2014 always reloads all data on each sync (full refresh)")
    w(
        "- **Varies** \u2014 depends on user configuration "
        "(e.g., dlt_native sources)"
    )
    w()
    w(
        "See [Sync Modes](sync-modes.md) for details on incremental vs "
        "full refresh behavior."
    )
    w()
    w('!!! tip "Can\'t find your source?"')
    w(
        "    Use the **REST API** source to connect to any API with JSON "
        "responses, or **dlt_native** to bring in any "
        "[dlt verified source]"
        "(https://dlthub.com/docs/dlt-ecosystem/verified-sources/). "
        "See [Custom Sources](custom-sources.md) for details."
    )
    w()
    w("---")
    w()

    # --- Category tables ---
    for cat, source_order in CATEGORY_SOURCE_ORDER.items():
        w(f"## {cat}")
        w()
        w(CATEGORY_DESC[cat])
        w()
        w("| Source | Display Name | Auth | Incremental | Wizard | Notes |")
        w("|--------|-------------|------|-------------|--------|-------|")

        for src in source_order:
            if src in NOT_YET_IMPLEMENTED:
                info = NOT_YET_IMPLEMENTED[src]
                w(f"| `{src}` | {info['display_name']} | — | — | No | {info['note']} |")
                continue
            meta = SOURCE_REGISTRY[src]
            display = DISPLAY_NAME_OVERRIDE.get(src, meta["display_name"])
            auth_raw = meta["auth_type"].value if hasattr(meta["auth_type"], "value") else str(meta["auth_type"])
            auth = AUTH_TYPE_DISPLAY.get(auth_raw, auth_raw)
            wizard = "Yes" if meta.get("wizard_enabled") else "No"
            caps = meta.get("capabilities", {})
            inc = INCREMENTAL_OVERRIDE.get(
                src,
                "Yes" if caps.get("incremental") else "No",
            )
            notes = NOTES.get(src, "")
            w(f"| `{src}` | {display} | {auth} | {inc} | {wizard} | {notes} |")

        w()

        # Category-level admonitions
        if cat in CATEGORY_ADMONITIONS:
            for line in CATEGORY_ADMONITIONS[cat]:
                w(line)
            w()

        w("---")
        w()

    # --- Source Counts ---
    w("## Source Counts by Category")
    w()
    w("| Category | Total | Wizard | Coming Soon |")
    w("|----------|-------|--------|-------------|")

    total_all = 0
    total_wizard = 0
    total_coming = 0

    for cat, source_order in CATEGORY_SOURCE_ORDER.items():
        cat_total = len(source_order)
        cat_wizard = sum(
            1 for s in source_order
            if SOURCE_REGISTRY.get(s, {}).get("wizard_enabled")
        )
        cat_coming = sum(
            1 for s in source_order if s in COMING_SOON_REASONS
        )
        w(f"| {cat} | {cat_total} | {cat_wizard} | {cat_coming} |")
        total_all += cat_total
        total_wizard += cat_wizard
        total_coming += cat_coming

    w(f"| **Total** | **{total_all}** | **{total_wizard}** | **{total_coming}** |")
    w()
    w("---")
    w()

    # --- Authentication Types ---
    w("## Authentication Types")
    w()
    w("Each source uses one of five authentication methods:")
    w()
    w("| Auth Type | Description | Credential Storage |")
    w("|-----------|-------------|-------------------|")
    w("| **None** | No authentication required | \u2014 |")
    w(
        "| **API Key** | Secret key provided by the service | "
        "`.env` file (e.g., `STRIPE_API_KEY`) |"
    )
    w(
        "| **OAuth** | Browser-based OAuth 2.0 flow | "
        "`.dlt/secrets.toml` (auto-managed) |"
    )
    w("| **Basic** | Username + password or token | `.env` file |")
    w(
        "| **Service Account** | Service account credentials "
        "(JSON key file or similar) | `.env` file or `.dlt/secrets.toml` |"
    )
    w()
    w('!!! tip "OAuth token management"')
    w(
        "    OAuth tokens are automatically refreshed by dlt. The wizard "
        "warns you when tokens are expiring. Re-authenticate with "
        "`dango oauth refresh <source_type>`. See "
        "[OAuth Tokens](../security/oauth.md)."
    )
    w()
    w("---")
    w()

    # --- Coming Soon ---
    w("## Coming Soon Sources")
    w()
    w(
        f"These {len(COMING_SOON_REASONS)} sources are registered in the "
        f"source catalog but disabled pending testing or API updates:"
    )
    w()
    w("| Source | Reason |")
    w("|--------|--------|")
    for src, reason in COMING_SOON_REASONS.items():
        w(f"| `{src}` | {reason} |")
    w()
    w(
        "These sources will be enabled in future releases. In the meantime, "
        "you can connect to them via "
        "[Custom Sources (dlt_native)](custom-sources.md)."
    )
    w()
    w("---")
    w()

    # --- Hidden Sources ---
    w("## Hidden Sources")
    w()
    w(
        "Two legacy source types are hidden from the wizard but still "
        "functional:"
    )
    w()
    w("| Source | Replacement | Reason |")
    w("|--------|------------|--------|")
    w(
        "| `csv` | `local_files` | `local_files` supports CSV plus JSON, "
        "JSONL, and Parquet |"
    )
    w(
        "| `filesystem` | `local_files` | `local_files` is the recommended "
        "local file loader |"
    )
    w()
    w(
        "If you have existing `type: csv` configurations, they continue to "
        "work. New projects should use `type: local_files`."
    )
    w()
    w("---")
    w()

    # --- Related Pages ---
    w("## Related Pages")
    w()
    w(
        "- [Adding Sources](adding-sources.md) \u2014 step-by-step wizard "
        "walkthrough"
    )
    w(
        "- [Sync Modes](sync-modes.md) \u2014 incremental, full refresh, "
        "and date range syncs"
    )
    w(
        "- [Custom Sources](custom-sources.md) \u2014 connect any API or "
        "dlt source via `dlt_native`"
    )
    w(
        "- [Source Registry Reference](../reference/source-registry.md) "
        "\u2014 raw registry data and parameters"
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
        import traceback
        traceback.print_exc()
        return 1

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content)
    print(f"Generated {OUTPUT_FILE.relative_to(SCRIPT_DIR.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
