# Scripts

Custom Python code that runs on a schedule or manually via "Run Now" in the Scripts tab.

---

## What Are Scripts?

Scripts are Python files in `scripts/` that execute as subprocesses for custom logic — email reports, Slack alerts, API exports, or any other Python code. Unlike notebooks, scripts are scheduled, manual, headless, and repeatable.

## Getting Started

### 1. Create a Script

Place a `.py` file in the `scripts/` directory:

```bash
mkdir -p scripts
touch scripts/my_report.py
```

### 2. Write Some Code

Open `scripts/my_report.py` and add:

```python
"""scripts/my_report.py

Example: Print a greeting to verify the execution environment.
"""
import os

project_root = os.environ.get("DANGO_PROJECT_ROOT", "unknown")
print(f"Hello from Dango! Project root: {project_root}")
```

### 3. Run It

The script appears automatically in the **Scripts** tab of the Web UI:

1. Navigate to **Scripts** in the top navigation bar
2. Find `my_report.py` in the table
3. Click **Run Now**
4. The Status column shows the current state (running, success, failed)
5. Click the status badge or **View Log** to inspect stdout and stderr

!!! tip "Script Discovery"
    Dango recursively scans the `scripts/` directory and displays all `.py` files. Files prefixed with `_` or `.`, and files named `__init__.py`, are hidden. You can organize scripts into subdirectories (e.g., `scripts/reports/daily.py`).

## Execution Environment

Scripts run as isolated subprocesses with the following environment:

| Property | Value |
|----------|-------|
| **Python interpreter** | `sys.executable` — the same Python that runs Dango (your venv) |
| **Working directory** | Your project root (`DANGO_PROJECT_ROOT`) |
| **Environment variables** | Inherited from the Dango process + `DANGO_PROJECT_ROOT` |

### Available Environment Variables

| Variable | Description | Set By |
|----------|-------------|--------|
| `DANGO_PROJECT_ROOT` | Absolute path to project root | Dango automatically |
| `DANGO_SCRIPT_RUN_ID` | Unique run identifier (manual runs only) | Dango automatically |
| Any `.env` var | All variables from your `.env` file | Inherited from Dango process |

### Setting Environment Variables

=== "Local"

    ```bash
    # Add to .env
    echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...' >> .env
    ```

=== "Cloud"

    ```bash
    dango remote env set SLACK_WEBHOOK_URL https://hooks.slack.com/services/...
    ```

## Dependencies

If your script needs packages beyond the Python standard library, create `scripts/requirements.txt`:

```text
requests>=2.31.0
gspread>=6.0.0
```

Dango automatically installs these dependencies:

- When the platform starts (`dango start` or `dango serve`)
- When a script schedule is activated (via `dango schedule add`)
- During cloud deployment (`dango deploy` or `dango remote push`)

!!! warning "Installation Failures"
    If `pip install -r scripts/requirements.txt` fails, Dango logs a warning but does not block startup. Check `.dango/logs/activity.jsonl` for details. The installation runs with a 120-second timeout.

## DuckDB Access

Your warehouse is at `data/warehouse.duckdb`. Unless your script performs writes, connect in read-only mode:

```python
import os

import duckdb

project_root = os.environ["DANGO_PROJECT_ROOT"]
db_path = os.path.join(project_root, "data", "warehouse.duckdb")

# Read-only connection (preferred for queries)
conn = duckdb.connect(db_path, read_only=True)
rows = conn.sql(
    "SELECT table_name FROM information_schema.tables"
).fetchall()
conn.close()
```

### Writing to DuckDB

If your script needs to write to the warehouse, acquire `DbtLock` to coordinate with other writers:

```python
"""scripts/import_data.py

Example: Safely write data to the warehouse.
"""
import os
from pathlib import Path

import duckdb

from dango.utils.dbt_lock import DbtLock

project_root = Path(os.environ["DANGO_PROJECT_ROOT"])
db_path = project_root / "data" / "warehouse.duckdb"

lock = DbtLock(project_root)
try:
    lock.acquire(timeout=30)
    conn = duckdb.connect(str(db_path))
    conn.sql("CREATE SCHEMA IF NOT EXISTS script_data")
    conn.sql("""
        CREATE TABLE IF NOT EXISTS script_data.my_import (
            id INTEGER PRIMARY KEY,
            value VARCHAR,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.sql(
        "INSERT INTO script_data.my_import VALUES (1, 'hello', CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()
    print("Data written successfully.")
finally:
    lock.release()
```

!!! warning "DbtLock is Not Auto-Acquired"
    Scripts are **not** automatically wrapped in a DbtLock. If your script writes to DuckDB, you must acquire the lock yourself.

## Anti-Patterns

### Don't Create Tables in DuckDB Directly

Use **dbt models** for persistent tables. Script-written tables are invisible to dbt and can't participate in transformations.

```python
# BAD: creating tables directly in scripts
conn.sql("CREATE TABLE raw.my_table AS SELECT ...")

# GOOD: define a dbt model in models/
# models/script_models/my_table.sql
# {{ config(materialized='table') }}
# SELECT ...
```

### Don't Acquire DbtLock for the Entire Script

Acquire the lock only around write operations. Long-held locks block syncs and dbt runs.

```python
# BAD: holding the lock during slow network I/O
lock.acquire()
data = fetch_from_api()  # slow!
conn.sql("INSERT INTO ...")

# GOOD: lock only around writes
data = fetch_from_api()
lock.acquire()
conn.sql("INSERT INTO ...")
lock.release()
```

### Don't Import Dango Internals

Only use `dango.utils.dbt_lock.DbtLock`. Internal modules can change without notice.

```python
# BAD: importing internal modules
from dango.config.loader import ConfigLoader  # internal API

# ACCEPTABLE: using the public lock utility
from dango.utils.dbt_lock import DbtLock
```

## Examples

### Example 1: Email Report

This script queries a daily summary from DuckDB and emails it via SMTP. It uses only the Python standard library — no additional dependencies.

```python
"""scripts/email_report.py

Send a daily summary email via SMTP.
"""
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

import duckdb

project_root = Path(os.environ["DANGO_PROJECT_ROOT"])
db_path = project_root / "data" / "warehouse.duckdb"

smtp_host = os.environ.get("SMTP_HOST", "localhost")
smtp_port = 587
try:
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
except (ValueError, TypeError):
    pass
smtp_user = os.environ.get("SMTP_USER", "")
smtp_pass = os.environ.get("SMTP_PASS", "")
recipient = os.environ.get("REPORT_RECIPIENT", "team@example.com")

conn = duckdb.connect(str(db_path), read_only=True)
rows = conn.sql("""
    SELECT o.order_date,
           COUNT(*) AS order_count,
           SUM(o.total) AS revenue
    FROM raw.orders o
    WHERE o.order_date >= CURRENT_DATE - INTERVAL '1' DAY
    GROUP BY o.order_date
    ORDER BY o.order_date
""").fetchall()
conn.close()

if not rows:
    print("No orders found for the last 24 hours.")
else:
    body_lines = ["Daily Order Summary", "=" * 40, ""]
    for date, count, revenue in rows:
        body_lines.append(
            f"Date: {date}  Orders: {count}  Revenue: ${revenue:.2f}"
        )

    msg = EmailMessage()
    msg.set_content("\n".join(body_lines))
    msg["Subject"] = f"Daily Report - {rows[0][0]}"
    msg["From"] = smtp_user
    msg["To"] = recipient

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"Report sent to {recipient}")
```

### Example 2: Slack Alert

This script checks if a key model has fresh data and sends an alert to Slack if stale. Uses only the standard library.

```python
"""scripts/slack_alert.py

Check data freshness and alert Slack if stale.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

import duckdb

project_root = Path(os.environ["DANGO_PROJECT_ROOT"])
db_path = project_root / "data" / "warehouse.duckdb"
webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")

if not webhook_url:
    print("SLACK_WEBHOOK_URL not set. Skipping alert.")
    raise SystemExit(0)

conn = duckdb.connect(str(db_path), read_only=True)
result = conn.sql("""
    SELECT MAX(order_date) AS last_order_date
    FROM marts.fact_orders
    HAVING MAX(order_date) < CURRENT_DATE - INTERVAL '1' DAY
""").fetchall()
conn.close()

if not result or result[0][0] is None:
    print("Data is fresh — no alert needed.")
else:
    last_date = result[0][0]
    days_ago = (datetime.now(timezone.utc).date() - last_date).days
    text = (
        f":warning: *Stale Data Alert*\n"
        f"Latest order date is {last_date} ({days_ago} days ago)."
    )
    payload = json.dumps({"text": text}).encode()
    req = Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urlopen(req)
    print(f"Alert sent: data is {days_ago} days stale.")
```

### Example 3: Google Sheets Export

This script queries DuckDB and exports the results to a Google Sheet.

**Dependencies** (`scripts/requirements.txt`):

```text
gspread>=6.0.0
```

**Script** (`scripts/sheets_export.py`):

```python
"""scripts/sheets_export.py

Export a query result to Google Sheets.
"""
import os
from pathlib import Path

import duckdb
import gspread

project_root = Path(os.environ["DANGO_PROJECT_ROOT"])
db_path = project_root / "data" / "warehouse.duckdb"

conn = duckdb.connect(str(db_path), read_only=True)
df = conn.sql("""
    SELECT order_date,
           COUNT(*) AS orders,
           SUM(amount) AS revenue
    FROM raw.orders
    GROUP BY order_date
    ORDER BY order_date DESC
    LIMIT 100
""").fetchdf()
conn.close()

gc = gspread.service_account()
sh = gc.open(os.environ.get("SHEET_NAME", "Dango Export"))
worksheet = sh.sheet1
worksheet.clear()
worksheet.update([df.columns.values.tolist()] + df.values.tolist())
print(f"Exported {len(df)} rows to sheet '{sh.title}'.")
```

## Scheduling

You can attach a script to a cron schedule, just like sync and dbt schedules.

=== "CLI Wizard"

    ```bash
    dango schedule add
    ```

    Select **"Script (custom Python)"** when prompted for the schedule type. Then choose a script from the list of discovered files. The wizard prompts for name, frequency, timezone, and optional notifications.

=== "YAML Configuration"

    Script schedules are stored in `.dango/schedules.yml` alongside other schedule types:

    ```yaml
    schedules:
      - name: daily_report
        type: script
        cron: "0 7 * * *"
        script_path: reports/daily_summary.py
        enabled: true
        timeout_minutes: 15
        timezone: "America/New_York"
    ```

### Script Schedule Fields

| Field | Type | Required | Default | Description |
|-------|------|:--------:|---------|-------------|
| `name` | string | yes | — | Unique identifier (lowercase + underscores). |
| `type` | string | yes | — | Must be `script`. |
| `cron` | string | yes | — | 5-field cron expression or preset name. |
| `script_path` | string | yes | — | Relative path inside `scripts/`. |
| `enabled` | bool | no | `true` | Set to `false` to pause. |
| `timeout_minutes` | int | no | `30` | Maximum execution time in minutes. |
| `timezone` | string | no | UTC | IANA timezone (e.g., `America/New_York`). |
| `start_date` | datetime | no | — | Don't run before this date. |

!!! info "Timeout Defaults"
    Scheduled scripts default to **30 minutes**. Manual "Run Now" executions default to **5 minutes**. Override via `timeout_minutes` in the schedule config.

### Path Validation

At schedule activation, Dango validates the script path:

1. **Path traversal check** — the resolved path must stay inside `scripts/`
2. **File existence check** — the `.py` file must exist
3. **Syntax check** — the file must parse with `ast.parse()` (catches import errors at activation time rather than at runtime)

If validation fails, the schedule is skipped with a warning logged to `.dango/logs/activity.jsonl`.

## Logs

### Log Storage

Each script run creates a timestamped directory (or run UUID for manual runs):

```
.dango/logs/scripts/
├── my_report_20260713T070000/
│   ├── stdout.txt          # Captured stdout (truncated at 1 MB)
│   ├── stderr.txt          # Captured stderr (truncated at 1 MB)
│   └── meta.json           # Run metadata (status, duration, exit code)
└── ...
```

### Viewing Logs

**Web UI:** Click the script name or status badge in the Scripts table.

**Filesystem:**
```bash
ls -lt .dango/logs/scripts/ | head -5
cat .dango/logs/scripts/my_report_20260713T070000/stdout.txt
```

## Troubleshooting

### Script not appearing in the Scripts tab

- Verify the file is in the `scripts/` directory (project root, not inside `.dango/`)
- Check the file name doesn't start with `_` or `.` — these are hidden
- Ensure the file has a `.py` extension
- Restart or refresh the browser page

### Path traversal error on schedule activation

```
Script path '../../etc/passwd' escapes scripts/ directory
```

Dango rejects paths that resolve outside the `scripts/` directory. Use only relative paths within `scripts/`:

```yaml
# VALID
script_path: reports/daily.py

# INVALID — path traversal
script_path: ../../malicious.py
```

### Script times out

- **Manual runs** timeout after 5 minutes. Long-running scripts should be scheduled instead.
- **Scheduled runs** timeout after 30 minutes. Increase via `timeout_minutes` in the schedule config.

### Requirements install failure

Check `.dango/logs/activity.jsonl` for the error. Install manually: `pip install -r scripts/requirements.txt`. Verify package names and versions.

### Script succeeds but result is missing

- Check `stderr.txt` — exceptions may have been printed there
- If writing to DuckDB, verify the write lock was acquired
- Check the connection is in read-write mode (not `read_only=True`)

### Cancel doesn't stop the script

Dango sends `SIGTERM` first, waits 5 seconds, then `SIGKILL`. If the script traps `SIGTERM`, only `SIGKILL` terminates it.

## Further Reading

- [Scheduled Syncs](scheduling-monitoring/scheduled-syncs.md) — schedule types, cron expressions, timezone handling
- [Webhook Notifications](scheduling-monitoring/webhooks.md) — get notified when scripts succeed or fail
- [CLI Schedule Commands](cli/schedule-commands.md) — full CLI reference for schedule management
