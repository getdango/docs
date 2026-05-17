# GitHub

Connect GitHub repositories as a data source using a Personal Access Token.

---

## Overview

| Feature | Details |
|---------|---------|
| **Auth** | API Key (Personal Access Token) |
| **Incremental** | Yes (cursor-based) |
| **Category** | Development |

!!! note "Not OAuth"
    GitHub uses a **Personal Access Token (PAT)** for authentication, not an OAuth browser flow. No browser redirect is needed — you paste your token directly during setup.

GitHub loads repository data into DuckDB including issues, pull requests, comments, and reactions.

---

## Prerequisites

Before adding GitHub as a source, you need:

1. **GitHub account** with access to the target repository
2. **Personal Access Token (classic)** — not fine-grained

### Generate a Personal Access Token

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Set a descriptive name (e.g., "Dango data sync")
4. Select scopes:
    - `repo` — full repository access (required for private repos)
    - `read:org` — read org membership
    - `read:user` — read user profile
5. Click **Generate token**
6. Copy the token (starts with `ghp_`) — you won't see it again

!!! warning "Classic tokens only"
    Use **classic** personal access tokens, not fine-grained tokens. Fine-grained tokens are not fully supported by the dlt GitHub source.

---

## Setup

### Step 1: Add Source

```bash
dango source add
# Select "GitHub" from the list
```

### Step 2: Configure

The wizard will prompt for:

```
? GitHub Personal Access Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
? Repository owner (e.g., getdango): myorg
? Repository name (e.g., dango): my-repo
```

The token is saved to `.env` as `GITHUB_ACCESS_TOKEN`.

### Step 3: Sync

```bash
dango sync my_github
```

---

## Configuration

### sources.yml

```yaml
version: '1.0'
sources:
  - name: my_github
    type: github
    enabled: true
    description: GitHub issues and PRs from main repo
    github:
      owner: "myorg"
      name: "my-repo"
      access_token_env: "GITHUB_ACCESS_TOKEN"
```

### .env

```bash
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

!!! warning "Never commit secrets"
    `.env` is gitignored by default. Never add it to version control.

---

## Tables Loaded

GitHub data loads into the `raw_{source_name}` schema using dlt's `github_reactions` source function. Tables include:

| Table | Description |
|-------|-------------|
| `issues` | All issues (open and closed) |
| `pull_requests` | All pull requests |
| `comments` | Issue and PR comments |
| `reactions` | Reactions on issues, PRs, and comments |

```sql
-- Example: query open issues
SELECT * FROM raw_my_github.issues
WHERE state = 'open'
ORDER BY created_at DESC
LIMIT 10;
```

---

## Sync Behavior

- **Incremental** — dlt tracks a cursor and only fetches new/updated records after the first sync
- First sync loads all historical data for the repository
- Subsequent syncs are fast, fetching only changes since the last sync

---

## Troubleshooting

### 401 Unauthorized

**Problem**: `401 Bad credentials`

**Solutions**:

1. Verify your PAT is still valid at [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Check that the token hasn't expired (if you set an expiration date)
3. Regenerate the token and update `.env`

### 403 Forbidden

**Problem**: `403 Forbidden` on certain endpoints

**Solutions**:

1. Verify the token has the required scopes: `repo`, `read:org`, `read:user`
2. For private repos, the `repo` scope is required (not just `public_repo`)
3. Check that your GitHub account has access to the target repository

### Rate Limits

**Problem**: `403 API rate limit exceeded`

**Solution**: Authenticated requests are limited to **5,000 per hour**. If you sync large repos frequently:

1. Increase the interval between syncs
2. The dlt source handles rate limiting automatically with retries

### Private Repository Access

**Problem**: `404 Not Found` on a private repo

**Solution**: Ensure your PAT has the `repo` scope (full access to private repos). The `public_repo` scope is insufficient for private repositories.

---

## Next Steps

- **[Source Catalog](source-catalog.md)** - See all available sources
- **[Sync Modes](sync-modes.md)** - Understand incremental loading
- **[Adding Sources](adding-sources.md)** - General source setup guide
- **[Credentials](../security/credentials.md)** - Token storage and security
