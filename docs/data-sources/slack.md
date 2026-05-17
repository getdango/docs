# Slack

Sync channel messages and metadata from Slack into your data warehouse.

---

| Feature | Details |
|---------|---------|
| **Auth** | Bot User OAuth Token (`xoxb-`) |
| **Env Variable** | `SLACK_ACCESS_TOKEN` |
| **Incremental** | Yes |
| **Date Range** | Yes (default: last 90 days) |
| **dlt Package** | `slack` |

---

## Prerequisites

- A Slack workspace where you have admin (or app-install) permissions
- A Slack Bot User OAuth Token (`xoxb-...`)

### Create a Slack App and Bot Token

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App**
2. Choose **From scratch**, name it (e.g., "Dango Data"), and select your workspace
3. Go to **OAuth & Permissions** in the sidebar
4. Under **Bot Token Scopes**, add these scopes:
    - `channels:history` — read messages in public channels
    - `channels:read` — list public channels
    - `groups:history` — read messages in private channels (optional)
    - `groups:read` — list private channels (optional)
    - `users:read` — read user profiles
5. Click **Install to Workspace** at the top of the page
6. Authorize the app
7. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

!!! warning "Invite the bot to channels"
    After creating the app, you must **invite the bot to each channel** you want to sync:

    ```
    /invite @Dango Data
    ```

    The bot can only read messages from channels it has been invited to.

---

## Setup

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: Slack
? Source name: slack
? Environment variable for access token [SLACK_ACCESS_TOKEN]: SLACK_ACCESS_TOKEN
? Filter to specific channels? (leave empty for all): 
? Start date (default: 90 days ago): 
```

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: slack
    type: slack
    enabled: true
    description: Slack workspace messages
    slack:
      access_token_env: SLACK_ACCESS_TOKEN
```

=== "Local"

    Store the token in your project's `.env` file:
    ```bash
    # .env (gitignored)
    SLACK_ACCESS_TOKEN=xoxb-your-bot-token-here
    ```

=== "Cloud"

    Set the token on your remote server:
    ```bash
    dango remote env set SLACK_ACCESS_TOKEN xoxb-your-bot-token-here
    ```

### First Sync

```bash
dango sync slack
```

---

## Configuration

### Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `selected_channels` | All channels | List of specific channel IDs to sync |
| `start_date` | 90 days ago | Earliest date to fetch messages from |

### Filter to Specific Channels

To sync only certain channels, provide their channel IDs:

```yaml
slack:
  access_token_env: SLACK_ACCESS_TOKEN
  selected_channels:
    - C01ABCDEF    # #general
    - C02GHIJKL    # #engineering
    - C03MNOPQR    # #sales
```

??? info "How to find a channel ID"
    1. Open Slack in a web browser
    2. Navigate to the channel
    3. The URL looks like: `https://app.slack.com/client/TXXXXXXX/C01ABCDEF`
    4. The last segment (`C01ABCDEF`) is the channel ID

    Or right-click the channel name > **View channel details** > scroll to the bottom to find the Channel ID.

### Set a Custom Start Date

```yaml
slack:
  access_token_env: SLACK_ACCESS_TOKEN
  start_date: "2024-01-01"    # Sync messages from January 2024 onward
```

### Full Configuration Example

```yaml
version: '1.0'
sources:
  - name: slack
    type: slack
    enabled: true
    description: Engineering Slack channels
    slack:
      access_token_env: SLACK_ACCESS_TOKEN
      selected_channels:
        - C01ABCDEF
        - C02GHIJKL
      start_date: "2024-06-01"
```

---

## Tables Loaded

Data loads into the `raw_{source_name}` schema. By default, each channel gets its own message table:

| Table | Description |
|-------|-------------|
| `raw_slack.channels` | Channel metadata (name, topic, purpose, member count) |
| `raw_slack.users` | User profiles (display name, email, status) |
| `raw_slack.{channel_name}` | Messages for each channel (one table per channel) |

For example, if the bot is in `#general` and `#engineering`:

- `raw_slack.general` — messages from #general
- `raw_slack.engineering` — messages from #engineering

Query example:

```sql
SELECT user, text, ts
FROM raw_slack.general
ORDER BY ts DESC
LIMIT 20;
```

---

## Sync Behavior

- **Incremental**: After the first sync, subsequent syncs fetch only messages posted since the last sync.
- **Write disposition**: `append` for messages (new messages are added, never deleted).
- **First sync**: Loads messages within the date range from all invited channels. Large workspaces with extensive history may take 10-30 minutes.

!!! note "Slack API rate limits"
    Slack enforces rate limits (typically 1 request per second for `conversations.history`). Dango handles rate limiting automatically. Very large channel histories may take longer to sync.

---

## Common Issues

### No Messages Returned

- **Bot not invited**: The most common issue. Run `/invite @YourBotName` in each channel you want to sync.
- **Channel IDs wrong**: If using `selected_channels`, verify the IDs. Channel IDs start with `C` (public) or `G` (private).
- **Start date too recent**: Check your `start_date` setting.

### "not_authed" or "invalid_auth"

- Verify the bot token in `.env` starts with `xoxb-`
- Check that the app is still installed in your workspace (not uninstalled by an admin)
- Regenerate the token if needed: go to your app's **OAuth & Permissions** page and reinstall

### "missing_scope" Errors

Your bot token lacks a required scope. Go to [api.slack.com/apps](https://api.slack.com/apps) > your app > **OAuth & Permissions** > add the missing scope > **Reinstall to Workspace**.

### Private Channels Not Syncing

Private channels require the `groups:history` and `groups:read` scopes. Add these scopes and reinstall the app, then invite the bot to the private channel.

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
- **[Source Catalog](source-catalog.md)** - All available data sources
- **[Transformations](../transformations/index.md)** - Transform Slack data with dbt
- [Slack API Documentation](https://api.slack.com/docs)
