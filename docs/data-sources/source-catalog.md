# Source Catalog

Complete catalog of all 33 data sources supported by Dango, grouped by category.

---

## Overview

Dango ships with **33 built-in source connectors** powered by [dlt (data load tool)](https://dlthub.com/docs):

- **25 wizard-enabled** — add via `dango source add` interactive wizard
- **6 coming soon** — registered but disabled pending testing
- **2 hidden** — legacy aliases (use the recommended alternative)

Every source is defined in the [source registry](../reference/source-registry.md) with its authentication type, default resources, and configuration parameters.

### Reading the Tables

Each category table includes an **Incremental** column indicating sync behavior:

- **Yes** — supports incremental sync (only new/changed data loaded on each run)
- **Partial** — some resources are incremental, others always reload all data
- **No** — always reloads all data on each sync (full refresh)
- **Varies** — depends on user configuration (e.g., dlt_native sources)

See [Sync Modes](sync-modes.md) for details on incremental vs full refresh behavior.

!!! tip "Can't find your source?"
    Use the **REST API** source to connect to any API with JSON responses, or **dlt_native** to bring in any [dlt verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/). See [Custom Sources](custom-sources.md) for details.

---

## Local & Custom

Sources for local files, generic APIs, and advanced dlt integrations.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `local_files` | File Import (CSV, JSON, Parquet) | None | Yes | Yes | [Local Files Guide](local-files/index.md) |
| `rest_api` | REST API (Generic) | API Key | Yes | Yes | Connect to any REST API — [REST API Guide](rest-api.md) |
| `dlt_native` | dlt Native (Advanced) | None | Varies | Yes | Bring any dlt source — [Custom Sources Guide](custom-sources.md) |
| `csv` | CSV Files | None | Yes | No | **Hidden** — use `local_files` instead |
| `filesystem` | Files & Cloud Storage | None | No | No | **Hidden** — use `local_files` for local files |

---

## Marketing & Analytics

Sources for advertising platforms, analytics tools, and marketing data.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `google_sheets` | Google Sheets | OAuth | No | Yes | [Google Sheets Guide](google-sheets.md) |
| `facebook_ads` | Facebook Ads | OAuth | Yes | Yes | [Facebook Ads Guide](facebook-ads.md) |
| `google_analytics` | Google Analytics 4 | OAuth | Yes | Yes | [Google Analytics Guide](google-analytics.md) |
| `google_ads` | Google Ads | OAuth | No | Yes | [Google Ads Guide](google-ads.md) |
| `airtable` | Airtable | API Key | No | Yes | Bases and tables |
| `mux` | Mux | API Key | Partial | Yes | Video analytics |
| `matomo` | Matomo | API Key | Yes | No | **Coming Soon** |

---

## Business & CRM

Sources for CRM platforms, helpdesks, project management, and HR tools.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `hubspot` | HubSpot | API Key | Yes | Yes | [HubSpot Guide](hubspot.md) — contacts, companies, deals, tickets |
| `salesforce` | Salesforce | Service Account | Partial | Yes | [Salesforce Guide](salesforce.md) |
| `pipedrive` | Pipedrive | API Key | Yes | Yes | 16 resources available |
| `freshdesk` | Freshdesk | API Key | Yes | Yes | Support tickets and contacts |
| `zendesk` | Zendesk | Basic | Partial | Yes | Support tickets and users |
| `workable` | Workable | API Key | Partial | Yes | Applicant tracking |
| `jira` | Jira | Basic | No | No | **Coming Soon** |
| `asana` | Asana | API Key | Partial | No | **Coming Soon** |

---

## E-commerce & Payment

Sources for payment processors and online stores.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `stripe` | Stripe | API Key | Partial | Yes | [Stripe Guide](stripe.md) — charges, customers, subscriptions |
| `shopify` | Shopify | OAuth | — | No | **Coming Soon** — pending OAuth flow update |

---

## Development

Sources for developer tools and code repositories.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `github` | GitHub | API Key | No | Yes | [GitHub Guide](github.md) — issues, PRs, commits |

---

## Communication

Sources for team messaging and collaboration.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `slack` | Slack | API Key | Partial | Yes | [Slack Guide](slack.md) — channels, messages, users |

---

## Files & Storage

Sources for knowledge bases and email.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `notion` | Notion | API Key | No | Yes | Pages and databases |
| `inbox` | Email (IMAP) | Basic | Yes | Yes | IMAP email import |

---

## Databases

Sources for relational and document databases.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `postgres` | PostgreSQL | Basic | Yes | Yes | Full table or incremental loading |
| `mongodb` | MongoDB | Basic | Yes | Yes | Collections with optional filtering |

!!! note "Other databases"
    Connect to MySQL, SQL Server, and other databases via the `dlt_native` source type using dlt's [sql_database](https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database) source. See [Database Sources](database-sources.md).

---

## Streaming

Sources for real-time data streams.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `kafka` | Apache Kafka | None | Yes | Yes | Consumer-based ingestion |
| `kinesis` | AWS Kinesis | Service Account | Yes | Yes | AWS stream processing |

---

## Other

Utility and niche sources.

| Source | Display Name | Auth | Incremental | Wizard | Notes |
|--------|-------------|------|-------------|--------|-------|
| `chess` | Chess.com | None | Partial | Yes | Public API — great for testing |
| `strapi` | Strapi | API Key | No | No | **Coming Soon** |
| `personio` | Personio | API Key | Partial | No | **Coming Soon** |

---

## Source Counts by Category

| Category | Total | Wizard | Coming Soon |
|----------|-------|--------|-------------|
| Local & Custom | 5 | 3 | 0 |
| Marketing & Analytics | 7 | 6 | 1 |
| Business & CRM | 8 | 6 | 2 |
| E-commerce & Payment | 2 | 1 | 1 |
| Development | 1 | 1 | 0 |
| Communication | 1 | 1 | 0 |
| Files & Storage | 2 | 2 | 0 |
| Databases | 2 | 2 | 0 |
| Streaming | 2 | 2 | 0 |
| Other | 3 | 1 | 2 |
| **Total** | **33** | **25** | **6** |

---

## Authentication Types

Each source uses one of five authentication methods:

| Auth Type | Description | Credential Storage |
|-----------|-------------|-------------------|
| **None** | No authentication required | — |
| **API Key** | Secret key provided by the service | `.env` file (e.g., `STRIPE_API_KEY`) |
| **OAuth** | Browser-based OAuth 2.0 flow | `.dlt/secrets.toml` (auto-managed) |
| **Basic** | Username + password or token | `.env` file |
| **Service Account** | Service account credentials (JSON key file or similar) | `.env` file or `.dlt/secrets.toml` |

!!! tip "OAuth token management"
    OAuth tokens are automatically refreshed by dlt. The wizard warns you when tokens are expiring. Re-authenticate with `dango oauth refresh <source_type>`. See [OAuth Tokens](../security/oauth.md).

---

## Coming Soon Sources

These 6 sources are registered in the source catalog but disabled pending testing or API updates:

| Source | Reason |
|--------|--------|
| `shopify` | Shopify requires Authorization Code Grant OAuth — flow not yet implemented |
| `matomo` | Awaiting testing and validation |
| `jira` | Awaiting testing and validation |
| `asana` | Awaiting testing and validation |
| `strapi` | Awaiting testing and validation |
| `personio` | Awaiting testing and validation |

These sources will be enabled in future releases. In the meantime, you can connect to them via [Custom Sources (dlt_native)](custom-sources.md).

---

## Hidden Sources

Two legacy source types are hidden from the wizard but still functional:

| Source | Replacement | Reason |
|--------|------------|--------|
| `csv` | `local_files` | `local_files` supports CSV plus JSON, JSONL, and Parquet |
| `filesystem` | `local_files` | `local_files` is the recommended local file loader |

If you have existing `type: csv` configurations, they continue to work. New projects should use `type: local_files`.

---

## Related Pages

- [Adding Sources](adding-sources.md) — step-by-step wizard walkthrough
- [Sync Modes](sync-modes.md) — incremental, full refresh, and date range syncs
- [Custom Sources](custom-sources.md) — connect any API or dlt source via `dlt_native`
- [Source Registry Reference](../reference/source-registry.md) — raw registry data and parameters
