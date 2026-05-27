# Environment Variables

Manage secrets and environment variables on your cloud server.

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `dango remote env set KEY=VALUE` | Set or update a variable |
| `dango remote env get KEY` | Display a variable (masked) |
| `dango remote env list` | List all variables (masked) |
| `dango remote env delete KEY` | Remove a variable |

---

## When to Use Env Vars vs secrets.toml

| Use Case | Where to Store |
|----------|---------------|
| Cloud provider tokens (`DIGITALOCEAN_TOKEN`) | Environment variable |
| Object storage keys (`SPACES_ACCESS_KEY`) | Environment variable |
| Source API keys (Stripe, HubSpot, etc.) | `.dlt/secrets.toml` |
| OAuth tokens (Google, Facebook, etc.) | `.dlt/secrets.toml` (managed by OAuth flow) |
| Admin password (`DANGO_ADMIN_PASSWORD`) | Environment variable |

**General rule:** credentials used by Dango itself (cloud, backups, auth) go in `.env`. Credentials used by dlt for data ingestion go in `.dlt/secrets.toml`. Both files live on the server at `/srv/dango/project/` and are never synced by `dango remote push`.

---

## Setting Variables

```bash
dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
```

```
✓ Set SPACES_ACCESS_KEY=***
```

- Creates the `.env` file if it doesn't exist (with `0600` permissions &mdash; readable only by the file owner)
- Updates the value if the key already exists
- The key cannot be empty and the format must be `KEY=VALUE`

Set multiple variables with separate commands:

```bash
dango remote env set SPACES_ACCESS_KEY=DO00EXAMPLE123
dango remote env set SPACES_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE
dango remote env set SPACES_REGION=nyc3
dango remote env set SPACES_BUCKET=my-dango-backups
```

---

## Viewing Variables

View a single variable:

```bash
dango remote env get SPACES_ACCESS_KEY
```

```
SPACES_ACCESS_KEY=***
```

List all variables:

```bash
dango remote env list
```

```
SPACES_ACCESS_KEY=***
SPACES_SECRET_KEY=***
SPACES_REGION=***
SPACES_BUCKET=***
DIGITALOCEAN_TOKEN=***

5 variable(s) total
```

!!! note
    Values are always masked in the output. To see actual values, use `dango remote ssh` and inspect the file directly: `cat /srv/dango/project/.env`

---

## Deleting Variables

```bash
dango remote env delete SPACES_REGION
```

```
✓ Deleted SPACES_REGION
```

Returns an error if the variable doesn't exist.

---

## Remote .env Location

Environment variables are stored at:

```
/srv/dango/project/.env
```

This file has `0600` permissions (owner read/write only). The `env` commands connect to the server as the `dango` user for project file operations, following the two-SSH-user pattern (root for system operations, dango for project files).

---

## Common Variables

| Variable | Used For |
|----------|----------|
| `DIGITALOCEAN_TOKEN` | DigitalOcean API access (deploy, resize, migrate, destroy) |
| `SPACES_ACCESS_KEY` | DigitalOcean Spaces access key (backups) |
| `SPACES_SECRET_KEY` | DigitalOcean Spaces secret key (backups) |
| `SPACES_REGION` | Spaces region slug, e.g., `nyc3` (backups) |
| `SPACES_BUCKET` | Spaces bucket name (backups) |
| `DANGO_ADMIN_PASSWORD` | Admin password for automated setups |

---

## Cloud Deploy Token Storage

When running deployment commands (`dango deploy`, `dango remote push`, etc.), the DigitalOcean API token is resolved in this order:

1. **Environment variable** &mdash; `DIGITALOCEAN_TOKEN` in your local shell
2. **Project credentials** &mdash; `.dango/credentials` in the project directory
3. **User credentials** &mdash; `~/.dango/credentials` in your home directory

The first match wins. Tokens saved during `dango deploy` are written to the project credentials file.

---

## Troubleshooting

### Variable not taking effect

Environment variables require a service restart to take effect:

```bash
dango remote ssh
```

Then on the server:

```bash
sudo systemctl restart dango-web
```

For Docker services (Metabase), the variables are passed through `docker-compose.yml` &mdash; rebuild the container:

```bash
sudo docker compose -f /srv/dango/project/docker-compose.yml up -d --build
```

### Permission denied

```
Error: Permission denied writing to .env
```

The `.env` file may have incorrect permissions. Fix via SSH:

```bash
dango remote ssh
sudo chown dango:dango /srv/dango/project/.env
sudo chmod 600 /srv/dango/project/.env
```

### Invalid format

```
Error: Invalid format. Use KEY=VALUE
```

The argument must contain an `=` separator and the key cannot be empty:

```bash
# Wrong
dango remote env set MYVAR
dango remote env set =value

# Right
dango remote env set MYVAR=value
dango remote env set MYVAR=value with spaces
```

---

## Next Steps

- [Remote Management](remote-management.md) &mdash; push, rollback, and other server commands
- [Backups](backups.md) &mdash; configure Spaces credentials for automated backups
- [Authentication](../security/authentication.md) &mdash; manage users and sessions
