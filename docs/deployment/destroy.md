# Destroy & Cleanup

Safely tear down a cloud deployment.

---

!!! danger "Irreversible Operation"
    Destroying a deployment permanently deletes cloud resources. For DigitalOcean, this includes the droplet, firewall, SSH key, and Spaces bucket. **This cannot be undone.** Download a backup before proceeding.

---

## Before You Destroy

1. **Download a backup** of your data:

    ```bash
    dango remote backup
    dango remote backup download backup-20260515-143000.tar.gz -o ~/dango-final-backup.tar.gz
    ```

2. **Check server status** to confirm which deployment you're destroying:

    ```bash
    dango remote status
    ```

---

## CLI Options

| Option | Description |
|--------|-------------|
| `--force` | Skip confirmation and backup download prompts |
| `--keep-spaces` | Keep the Spaces bucket and its contents (DigitalOcean only) |
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
      Spaces:    Will be DELETED (my-dango-backups)
    ```

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
      ✓ Deleted Spaces bucket
      ✓ Removed .dango/cloud.yml

    Deployment destroyed.
    Note: SSH key kept locally at ~/.ssh/dango_ed25519
    ```

    ### Preserve Resources

    Keep your Spaces bucket (with all backups) for archival:

    ```bash
    dango deploy destroy --keep-spaces
    ```

    Keep the SSH key registered on DigitalOcean (useful if redeploying soon):

    ```bash
    dango deploy destroy --keep-ssh-key
    ```

    Both:

    ```bash
    dango deploy destroy --keep-spaces --keep-ssh-key
    ```

=== "BYOS"

    ```bash
    dango deploy destroy
    ```

    ### Step 1: Destruction Summary

    ```
    Destruction summary:
      Server:   203.0.113.50 (BYOS)
      Domain:   analytics.yourcompany.com
    ```

    ### Step 2: Backup Download Offer

    ```
    Download latest backup before destroying? [Y/n]:
    ```

    ### Step 3: Type-to-Confirm

    ```
    Type the server IP to confirm destruction: 203.0.113.50
    ```

    ### Step 4: Cleanup

    ```
    Cleaning up...
      ✓ Optionally stopped remote Dango services
      ✓ Removed .dango/cloud.yml

    Local cleanup complete.
    Note: The server and its data are still intact.
    ```

    !!! note "Server Not Deleted"
        BYOS destroy only removes the local `cloud.yml` configuration and optionally stops Dango services on the server. The server itself, its data, and any installed software remain untouched. To fully clean up the server, SSH in and remove Dango manually.

    The `--keep-spaces` and `--keep-ssh-key` options are ignored for BYOS deployments (a warning is printed).

---

## What Gets Deleted vs What Stays

### DigitalOcean

| Resource | Deleted | Notes |
|----------|---------|-------|
| Droplet (VM) | Yes | Server and all data on it |
| Cloud firewall | Yes | |
| SSH key (on DO) | Yes | Unless `--keep-ssh-key` |
| Spaces bucket | Yes | Unless `--keep-spaces` |
| Local `.dango/cloud.yml` | Yes | |
| Local SSH key (`~/.ssh/dango_*`) | **No** | Kept for potential reuse |
| Local project files | **No** | Your code, configs, dbt models are untouched |
| Local DuckDB database | **No** | `warehouse.duckdb` is not affected |

### BYOS

| Resource | Deleted | Notes |
|----------|---------|-------|
| Remote server | **No** | Server stays running |
| Remote Dango data | **No** | Data remains at `/srv/dango/` |
| Remote Dango services | Optional | Offered to stop during destroy |
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
5. **Spaces** &mdash; verify the bucket is removed (unless `--keep-spaces`)

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

Check the DigitalOcean console for orphaned resources: droplets, firewalls, SSH keys, and Spaces buckets with "dango" in the name.

### BYOS services won't stop

If the optional service stop fails during BYOS destroy:

```bash
ssh root@<server-ip>
sudo systemctl stop dango-web
sudo docker compose -f /srv/dango/project/docker-compose.yml down
sudo systemctl stop caddy
```

### Orphaned resources

If you suspect resources were left behind after a destroy:

**DigitalOcean:** Check Droplets, Firewalls, SSH Keys, and Spaces in the web console. Resources created by Dango are tagged with "dango".

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
