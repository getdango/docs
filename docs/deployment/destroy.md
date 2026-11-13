# Destroy & Cleanup

Safely tear down a cloud deployment.

---

!!! danger "Irreversible Operation"
    Destroying a deployment permanently deletes cloud resources. For DigitalOcean, this includes the droplet and firewall. For BYOS, it removes Dango, its Docker volumes and all its data from your server. The Spaces bucket (containing backups) is **preserved by default**. Use ``--delete-spaces`` to remove it. **This cannot be undone.** Download a backup before proceeding.

---

## Before You Destroy

1. **Download a backup** of your data (works for DigitalOcean and BYOS, and needs no Spaces):

    ```bash
    dango remote backup download --from-server -o ~/dango-final-backup.tar.gz
    ```

    BYOS backups live only on the server and are deleted with it, so this is the only copy you will have.

2. **Note your secrets.** `.env` and `.dlt/secrets.toml` are **not** in backups by default. `dango deploy destroy` reminds you of this and lists the secret names (never the values) the server holds; store the values somewhere safe before you continue.

3. **Check server status** to confirm which deployment you're destroying:

    ```bash
    dango remote status
    ```

---

## CLI Options

| Option | Description |
|--------|-------------|
| `--force` | Skip confirmation and backup download prompts |
| `--delete-spaces` | Also delete the Spaces bucket and all its contents (DigitalOcean only) |
| `--keep-ssh-key` | Keep the SSH key on DigitalOcean (DigitalOcean only) |

---

## Destroying a Deployment

=== "DigitalOcean"

    ```bash
    dango deploy destroy
    ```

    ### Step 1: Destruction Summary

    The CLI shows everything that will be deleted:

    ```
    Destruction summary:
      Droplet:   143.198.xxx.xxx (s-2vcpu-4gb, nyc1)
      Firewall:  dango-fw-abc123
      SSH key:   Will be DELETED from DigitalOcean
      Spaces:    my-bucket — will be KEPT (use --delete-spaces to remove)
    ```

    Right after the summary, Dango reminds you that `.env` and `.dlt/secrets.toml` are NOT in backups by default and lists the names of the secrets on the server (names only).

    ### Step 2: Backup Download Offer

    You're offered to download the latest backup before proceeding:

    ```
    Download latest backup before destroying? [Y/n]:
    ```

    ### Step 3: Type-to-Confirm

    Type the server's IP address to confirm:

    ```
    Type the server IP to confirm destruction: 143.198.xxx.xxx
    ```

    ### Step 4: Resource Deletion

    ```
    Destroying deployment...
      ✓ Deleted droplet
      ✓ Deleted firewall
      ✓ Deleted SSH key from DigitalOcean
      ✓ Removed .dango/cloud.yml

    Deployment destroyed.
    Note: SSH key kept locally at ~/.ssh/dango_ed25519
    Spaces bucket 'my-bucket' was preserved.
    ```

    ### Delete Spaces Bucket

    By default, the Spaces bucket (and all backups) is preserved. To delete it:

    ```bash
    dango deploy destroy --delete-spaces
    ```

    ### Keep SSH Key

    Keep the SSH key registered on DigitalOcean (useful if redeploying soon):

    ```bash
    dango deploy destroy --keep-ssh-key
    ```

=== "BYOS"

    ```bash
    dango deploy destroy
    ```

    ### Step 1: Destruction Summary

    ```
    BYOS Destroy Summary
      Server: 203.0.113.50
      Provider: BYOS
      This will stop all Dango services and remove all data from the server.
      Domain: analytics.yourcompany.com
    ```

    The summary also says the server itself will not be deleted (do that through your cloud provider). Dango then reminds you that `.env` and `.dlt/secrets.toml` are not in backups, lists the secret names the server holds, and prints that backups on a server of your own are lost with the server, together with the `dango remote backup download --from-server -o <file>` command. BYOS destroy does not offer a backup download: take one first.

    ### Step 2: Type-to-Confirm

    Unless you pass `--force`, type the server IP to confirm:

    ```
    Type the server IP (203.0.113.50) to confirm: 203.0.113.50
    ```

    ### Step 3: Cleanup

    Dango connects over SSH and stops `dango-web`, removes the Docker containers, volumes and images, removes the `dango-web` unit, `/srv/dango`, the `dango` user and the Caddy configuration, then removes the local `.dango/cloud.yml`:

    ```
    Stopping dango-web service...
    Stopping Docker services...
    Removing server files...
    Server cleaned up.
    Removed .dango/cloud.yml

    BYOS deployment destroyed.
    Important: Delete the server in your cloud provider's dashboard to stop billing.
    ```

    If the Docker teardown fails, Dango starts `dango-web` again, leaves the server files and your local `cloud.yml` in place, and stops so you can retry.

    !!! note "Server Not Deleted"
        BYOS destroy removes Dango and its data from the server, but the server itself (the machine and any other software on it) is not deleted. If the SSH key is missing or the connection fails, Dango warns that it could not clean up the server and still removes the local `cloud.yml`; clean up the server by hand.

    The `--delete-spaces` and `--keep-ssh-key` options are ignored for BYOS deployments (a note is printed).

---

## What Gets Deleted vs What Stays

### DigitalOcean

| Resource | Deleted | Notes |
|----------|---------|-------|
| Droplet (VM) | Yes | Server and all data on it |
| Cloud firewall | Yes | |
| SSH key (on DO) | Yes | Unless `--keep-ssh-key` |
| Spaces bucket | **No** (kept by default) | Unless `--delete-spaces` |
| Local `.dango/cloud.yml` | Yes | |
| Local SSH key (`~/.ssh/dango_*`) | **No** | Kept for potential reuse |
| Local project files | **No** | Your code, configs, dbt models are untouched |
| Local DuckDB database | **No** | `warehouse.duckdb` is not affected |

### BYOS

| Resource | Deleted | Notes |
|----------|---------|-------|
| Remote server | **No** | The machine stays running; delete it with your provider |
| Remote Dango data | **Yes** | Docker volumes, `/srv/dango/`, the `dango` user and the Caddy configuration are removed |
| Remote Dango services | **Yes** | Stopped and removed |
| Local `.dango/cloud.yml` | Yes | |
| Local project files | **No** | Untouched |

---

## Verification

After destroying, confirm all resources are cleaned up:

### Check Local State

```bash
# cloud.yml should be gone
ls .dango/cloud.yml
# ls: .dango/cloud.yml: No such file or directory

# SSH key still present locally
ls ~/.ssh/dango_ed25519
```

### Check DigitalOcean Console

1. Log in to [DigitalOcean](https://cloud.digitalocean.com/)
2. **Droplets** &mdash; verify the droplet is no longer listed
3. **Networking &gt; Firewalls** &mdash; verify the firewall is removed
4. **Settings &gt; Security &gt; SSH Keys** &mdash; verify the key is removed (unless `--keep-ssh-key`)
5. **Spaces**: verify the bucket is removed (only deleted with `--delete-spaces`)

---

## Redeploying After Destroy

To deploy again after destroying, run the deploy wizard:

```bash
# DigitalOcean
dango deploy

# BYOS
dango deploy --byos
```

Your local project files, dbt models, and source configurations are preserved &mdash; only the cloud infrastructure was removed. The deploy wizard will provision new infrastructure and push your current local state.

If you kept the SSH key (`--keep-ssh-key`), the new deployment can reuse it.

---

## Troubleshooting

### Token authentication failed

```
Error: DigitalOcean API authentication failed
```

The API token may have expired or been revoked. Resource deletion requires a valid token. If you can't authenticate:

1. Generate a new token in the [DO console](https://cloud.digitalocean.com/account/api/tokens)
2. Set it: `export DIGITALOCEAN_TOKEN=<new-token>`
3. Retry: `dango deploy destroy`

If the token is permanently unavailable, delete resources manually through the DigitalOcean web console, then remove the local config:

```bash
rm .dango/cloud.yml
```

### Partial deletion

If destroy fails midway (e.g., network error), some resources may remain:

```bash
# Retry
dango deploy destroy

# If retry also fails, clean up manually in the DO console
# Then remove local config
rm .dango/cloud.yml
```

Check the DigitalOcean console for orphaned resources: droplets, firewalls, SSH keys, and Spaces buckets with "dango" in the name. `dango deploy` and `dango remote status` also warn when DigitalOcean has droplets tagged `dango` that your `.dango/cloud.yml` does not name (see [Orphaned resources](#orphaned-resources)).

### BYOS cleanup failed

If the server cleanup fails during BYOS destroy (for example the SSH connection drops):

```bash
ssh root@<server-ip>
sudo systemctl stop dango-web
sudo docker compose -f /srv/dango/project/docker-compose.yml down
sudo systemctl stop caddy
```

### Orphaned resources

If you suspect resources were left behind after a destroy:

**DigitalOcean:** Check Droplets, Firewalls, SSH Keys, and Spaces in the web console. Resources created by Dango are tagged with "dango". A deploy that is killed hard (power loss, `kill -9`) cannot clean up after itself and can leave a running, billing droplet that `.dango/cloud.yml` does not record. To catch this, `dango deploy` (before provisioning) and `dango remote status` list any droplet tagged `dango` that your `cloud.yml` does not name, with its id, name and creation time, for example:

```
Warning: DigitalOcean has 1 droplet tagged 'dango' that this project's cloud.yml does not name:
  id 616435522  name dango-g4b  created 2026-11-06T05:06:55Z
  If they are leftovers, delete them in the DigitalOcean console (a deploy killed hard leaves one). They may belong to another Dango project; nothing was deleted.
```

The check only warns. It never deletes anything, and it prints nothing when no DigitalOcean token is configured or the lookup fails. A droplet tagged `dango` may belong to another Dango project: check before deleting.

**BYOS:** SSH into the server and check:

```bash
# Check if services are still running
systemctl status dango-web caddy
docker ps

# Check if data remains
ls -la /srv/dango/
```

---

## Next Steps

- [DigitalOcean](digitalocean.md) &mdash; deploy a new DigitalOcean server
- [BYOS](byos.md) &mdash; deploy to your own server
- [Backups](backups.md) &mdash; restore from a downloaded backup
