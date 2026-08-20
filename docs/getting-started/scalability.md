# Is Dango Right for You?

Dango is built for small teams and growing analytics teams. This page helps you evaluate whether Dango fits your current needs — and when you might consider alternatives.

---

## Is Dango Right for Your Team?

### Good Fit

- **Small data teams** (1–10 people) — Dango reduces infrastructure overhead dramatically
- **Growing usage** — Start locally, deploy to the cloud when you're ready
- **50+ GB datasets** — DuckDB handles multi-gigabyte workloads efficiently
- **Frequent schema changes** — dlt auto-evolves tables; zero manual DDL
- **SQL-first workflows** — dbt integration makes transformations version-controlled and testable
- **Real-time dashboards** — Metabase queries run fast against DuckDB's columnar storage
- **Developer-friendly setup** — One command boots the entire stack locally

### May Be a Stretch

- **Petabyte-scale data** — DuckDB and single-server architecture aren't designed for that scale
- **Hundreds of concurrent users** — Metabase runs on a single server; CDN + reverse proxy help but have limits
- **Strict data residency** — Cloud deployment is SSH-based; BYOS required for non-DigitalOcean servers
- **Heavy external integrations** — The platform is opinionated; significant divergence requires maintaining custom forks
- **Complex team governance** — Role-based access control exists but is basic (no column-level permissions yet)

---

## Architectural Limits

### Single-Writer DuckDB

DuckDB allows only one writer process at a time. Dango serializes all write operations through a file lock — you cannot run multiple syncs in parallel, and Metabase must pause during cloud syncs to avoid fcntl lock conflicts.

This is an **intentional design choice**: one writer eliminates concurrency bugs, corruption, and complexity. For teams with 1–5 scheduled syncs per day, this is invisible.

Learn more in [DuckDB & Single-Writer](../core-concepts/duckdb.md).

### Single-Server Architecture

Dango runs on a single server (local or cloud). There is no built-in horizontal scaling or failover. Vertically scale the server (more RAM, CPU) as your data grows — DigitalOcean offers droplets up to 48 vCPU / 192 GB RAM.

### Metabase Pauses During Cloud Syncs

On cloud deployments, Metabase must stop before write operations and restart after. This prevents DuckDB lock conflicts but means dashboard queries are briefly unavailable (typically 30 seconds to 5 minutes, depending on sync duration).

Local deployments have the same limitation — it's a DuckDB constraint, not a Dango implementation detail.

---

## Capacity Estimates by Droplet Size

These estimates are based on real deployments and typical usage patterns. They are **not benchmarked** — your actual capacity depends on query complexity, data model depth, and concurrent users. Monitor actual metrics (`dango remote logs`) and resize as needed.

| Aspect | Standard (s-2vcpu-4gb, $24/mo) | Performance (s-4vcpu-8gb, $48/mo) |
|--------|--------------------------------|-----------------------------------|
| **Recommended dataset size** | Up to 20 GB | 20–100 GB |
| **Concurrent Metabase users** | 5–10 | 15–30 |
| **Scheduled syncs per day** | 5–10 | 20+ |
| **DuckDB `memory_limit`** | 2 GB | 4–6 GB |
| **dbt thread count** | 2–4 | 4–8 |
| **dbt model execution time** | < 30 min | < 10 min |
| **Typical data latency** | 30–60 min | < 15 min |

**Why these numbers?**
- **Memory:** Leave OS + Docker + service overhead ~1 GB. Allocate remaining RAM to DuckDB and Metabase.
- **Syncs:** Each sync acquires the DuckDB write lock. Back-to-back syncs wait queued; space them 5–10 minutes apart.
- **Execution time:** Slower dbt runs delay downstream dashboards. Plan buffer time between syncs and dbt completion.

---

## Signs of Resource Pressure

Watch for these warnings — they indicate it's time to resize or reconsider the platform:

### Slow Queries
```sql
-- A simple aggregation takes >30 seconds
SELECT COUNT(*), date_trunc('day', created_at)
FROM large_table
GROUP BY 2
ORDER BY 1 DESC;
```

**Action:** Increase DuckDB `memory_limit` in `dbt/profiles.yml`. Check for missing indexes on join/filter columns.

### Sync Timeouts
```
dango sync stripe
Error: Sync exceeded timeout (600 seconds)
```

**Action:** Reduce sync scope — limit endpoints or set a narrower date range. Consider full refreshes less frequently.

### Out-of-Memory Kills
```bash
dango remote logs | grep -i "killed\|oom"
```

Metabase or DuckDB process is killed by the OS due to memory exhaustion.

**Action:** Resize to the Performance tier. Monitor memory usage during peak hours.

### Unresponsive Dashboards
Dashboard loads time out or return partial results. Typically happens when a dbt model or large sync blocks Metabase access.

**Action:** Check sync duration. Increase dbt `threads` to parallelize model execution. Monitor Metabase query logs.

---

## Bigger Droplet vs. Outgrowing Dango

### Resize the Droplet If…

- Dataset is growing but still < 100 GB
- Queries are slow but model count < 200
- dbt runs take > 30 minutes
- Metabase users are pushing 20–30
- You're on Standard tier and hitting memory limits

**Cost:** Upgrade from Standard ($24/mo) to Performance ($48/mo) — a 2x jump in compute and memory. Test the larger tier first with a snapshot of your data.

```bash
dango remote resize s-4vcpu-8gb
```

### Move to an Alternative If…

- Dataset is > 100 GB and growing rapidly
- Petabyte-scale data expected in 1–2 years
- Concurrent users > 50
- Heavy requirement for column-level access control
- Need multi-server failover or disaster recovery
- Data residency requires on-premise installation

**Alternatives to consider:**
- **BigQuery / Snowflake** — Managed warehouses, infinite scale, SQL at scale
- **Databricks** — Open-source Spark + lakehouse model
- **Starburst** — Federated query across data sources

Each shifts the infrastructure burden — you trade self-hosted simplicity for managed scale.

---

## When Dango Shines

Dango is purpose-built for a specific use case: **small teams with structured data who want analytics without infrastructure overhead**.

You get:
- ✅ Zero infrastructure setup
- ✅ Version-controlled transformations (dbt)
- ✅ Built-in dashboards (Metabase)
- ✅ 33 data sources (dlt)
- ✅ Local development + cloud deployment in one CLI
- ✅ Sub-second query response for < 50 GB datasets

You accept:
- ⚠️ Single-server architecture (no failover)
- ⚠️ Single-writer DuckDB (serialized syncs)
- ⚠️ Basic role-based access (no column-level control)
- ⚠️ Horizontal scaling requires moving to a different platform

---

## Next Steps

- **Ready to start?** → [Installation](installation.md)
- **Want to see it in action?** → [Quick Start](quick-start.md)
- **Need performance tuning?** → [Performance Optimization](../workflows/performance.md)
- **Planning cloud deployment?** → [Deployment Guide](../deployment/digitalocean.md)
