# Database Sources

Connect to PostgreSQL, MySQL, SQLite, SQL Server, and 30+ other databases.

---

## Overview

Dango supports 30+ SQL databases through dlt's `sql_database` source. Load tables directly from any SQLAlchemy-supported database into DuckDB.

**Supported Databases**:

- PostgreSQL
- MySQL / MariaDB
- SQLite
- Microsoft SQL Server
- Oracle
- Snowflake
- BigQuery
- Redshift
- And any SQLAlchemy-compatible database

---

## Quick Start: PostgreSQL

### Step 1: Install Dependencies

```bash
# Activate your project's virtual environment
source venv/bin/activate

# Install dlt sql_database extras + PostgreSQL driver
pip install "dlt[sql_database]" psycopg2-binary
```

**Drivers by database**:

| Database | Driver Package |
|----------|---------------|
| PostgreSQL | `psycopg2-binary` |
| MySQL | `pymysql` |
| SQLite | (built into Python) |
| SQL Server | `pyodbc` |
| Oracle | `cx_oracle` |
| Snowflake | `snowflake-sqlalchemy` |
| BigQuery | `sqlalchemy-bigquery` |

### Step 2: Configure Credentials

Add credentials to `.dlt/secrets.toml` (gitignored):

```toml
[sources.sql_database.credentials]
drivername = "postgresql"
database = "mydb"
username = "myuser"
password = "mypassword"
host = "localhost"
port = 5432
```

**Alternative: Connection string**

```toml
[sources.sql_database]
credentials = "postgresql://myuser:mypassword@localhost:5432/mydb"
```

### Step 3: Add Source to sources.yml

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: my_postgres
    type: dlt_native
    enabled: true
    description: PostgreSQL database
    dlt_native:
      source_module: sql_database
      source_function: sql_database
      function_kwargs:
        schema: "public"
        table_names:
          - customers
          - orders
          - products
```

**Note**: Credentials are NOT in this file - they're read from `.dlt/secrets.toml`.

### Step 4: Sync Data

```bash
dango sync --source my_postgres
```

### Step 5: Verify

Data is loaded into `raw_my_postgres` schema in DuckDB:

```bash
# Start platform
dango start

# Query in Metabase
SELECT * FROM raw_my_postgres.customers LIMIT 10;
```

---

## Configuration Reference

### Required Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `source_module` | `sql_database` | Always use `sql_database` for database sources |
| `source_function` | `sql_database` | Always use `sql_database` |

### Optional Parameters (in function_kwargs)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `schema` | `None` | Database schema to read from (e.g., `"public"`) |
| `table_names` | All tables | List of specific tables to sync |
| `chunk_size` | `50000` | Rows per batch |
| `backend` | `"sqlalchemy"` | Processing backend: `sqlalchemy`, `pyarrow`, `pandas`, `connectorx` |
| `reflection_level` | `"full"` | Schema detail: `minimal`, `full`, `full_with_precision` |

---

## Database-Specific Examples

### MySQL

**.dlt/secrets.toml**:
```toml
[sources.sql_database.credentials]
drivername = "mysql+pymysql"
database = "mydb"
username = "root"
password = "secret"
host = "localhost"
port = 3306
```

**.dango/sources.yml**:
```yaml
- name: my_mysql
  type: dlt_native
  enabled: true
  description: MySQL production database
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "mydb"
      table_names:
        - users
        - transactions
```

**Install driver**:
```bash
pip install pymysql
```

### SQLite

**.dlt/secrets.toml**:
```toml
[sources.sql_database]
credentials = "sqlite:///path/to/database.db"
```

**.dango/sources.yml**:
```yaml
- name: my_sqlite
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      table_names:
        - customers
        - orders
```

**No driver needed** - SQLite support is built into Python.

### SQL Server

**.dlt/secrets.toml**:
```toml
[sources.sql_database.credentials]
drivername = "mssql+pyodbc"
database = "mydb"
username = "sa"
password = "YourPassword123"
host = "localhost"
port = 1433
query = { driver = "ODBC Driver 17 for SQL Server" }
```

**.dango/sources.yml**:
```yaml
- name: my_sqlserver
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "dbo"
      table_names:
        - Customers
        - Orders
```

**Install driver**:
```bash
pip install pyodbc
# Also install ODBC driver: https://docs.microsoft.com/en-us/sql/connect/odbc/
```

### Snowflake

**.dlt/secrets.toml**:
```toml
[sources.sql_database.credentials]
drivername = "snowflake"
username = "myuser"
password = "mypassword"
host = "myaccount.snowflakecomputing.com"
database = "mydb"
query = { warehouse = "COMPUTE_WH", role = "ANALYST" }
```

**.dango/sources.yml**:
```yaml
- name: my_snowflake
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "PUBLIC"
      table_names:
        - customers
        - orders
```

**Install driver**:
```bash
pip install snowflake-sqlalchemy
```

---

## Advanced Configuration

### Load All Tables in Schema

Omit `table_names` to load all tables:

```yaml
function_kwargs:
  schema: "public"
  # No table_names specified = load all tables
```

### Multiple Schemas

Create separate sources for each schema:

```yaml
- name: public_tables
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "public"

- name: analytics_tables
  type: dlt_native
  enabled: true
  dlt_native:
    source_module: sql_database
    source_function: sql_database
    function_kwargs:
      schema: "analytics"
```

### Performance Tuning

```yaml
function_kwargs:
  chunk_size: 100000        # Larger batches (faster, more memory)
  backend: "pyarrow"        # Faster than sqlalchemy
  reflection_level: "minimal"  # Skip detailed schema info
```

### SSL Connections

**.dlt/secrets.toml**:
```toml
[sources.sql_database]
credentials = "postgresql://user:pass@host:5432/db?sslmode=require"
```

---

## Incremental Loading

### Date-Based Incremental

Load only rows added/updated since last sync:

```yaml
function_kwargs:
  schema: "public"
  table_names:
    - orders
  incremental:
    cursor_column: "updated_at"
    initial_value: "2024-01-01"
```

On subsequent syncs, only rows where `updated_at > last_sync_value` are loaded.

### ID-Based Incremental

```yaml
function_kwargs:
  schema: "public"
  table_names:
    - transactions
  incremental:
    cursor_column: "id"
    initial_value: 0
```

---

## Data Loading Behavior

### Full Table Load (Default)

By default, `sql_database` performs a **full table load**:

- Entire table is read from source database
- Loaded into DuckDB with `replace` disposition
- Previous data is dropped

**When to use**: Small to medium tables, master data

### Incremental Load

With incremental configuration:

- Only new/changed rows are fetched
- Uses `merge` disposition (upsert)
- Requires a cursor column (timestamp or ID)

**When to use**: Large tables, event data, frequently updated tables

---

## Limitations

### Custom SQL Not Supported

`sql_database` loads full tables - you cannot specify WHERE clauses or custom SQL.

**Workarounds**:

1. **Create views** in source database:
   ```sql
   -- In source database
   CREATE VIEW active_customers AS
   SELECT * FROM customers WHERE status = 'active';
   ```

   Then load the view:
   ```yaml
   table_names:
     - active_customers
   ```

2. **Filter in dbt**: Load full table, filter in dbt intermediate layer:
   ```sql
   -- dbt/models/intermediate/int_active_customers.sql
   SELECT * FROM {{ ref('stg_customers') }}
   WHERE status = 'active'
   ```

3. **Use custom dlt source**: Write Python code with custom SQL (see [Custom Sources](custom-sources.md))

### Schema Changes

If source table schema changes (columns added/removed):

1. Dango auto-detects and updates DuckDB schema
2. Staging models need manual update
3. Run `dango generate` to regenerate staging models

---

## Security Best Practices

### 1. Use Read-Only Database Users

Create a dedicated user with SELECT-only permissions:

```sql
-- PostgreSQL example
CREATE USER dango_reader WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE mydb TO dango_reader;
GRANT USAGE ON SCHEMA public TO dango_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dango_reader;
```

### 2. Never Commit Credentials

`.dlt/secrets.toml` is automatically gitignored. Verify:

```bash
cat .gitignore | grep secrets
# Should show: .dlt/secrets.toml
```

### 3. Limit Table Access

Only sync tables you need:

```yaml
table_names:
  - customers    # Include
  - orders       # Include
  # NOT users_passwords table
```

### 4. Use SSL/TLS

For production databases:

```toml
credentials = "postgresql://user:pass@host:5432/db?sslmode=require"
```

### 5. Rotate Credentials Regularly

Update `.dlt/secrets.toml` when rotating database passwords.

---

## Comparison: Database Source vs. Other Methods

| Feature | Database Source | CSV Export | Custom dlt |
|---------|----------------|------------|------------|
| Setup | Medium | Simple | Complex |
| Incremental | Yes | No | Yes |
| Custom SQL | No (views only) | N/A | Yes |
| Real-time | No (scheduled) | No | Configurable |
| Best for | Standard tables | One-time loads | Complex queries |

---

## How This Differs from Standard dlt

| Aspect | Standard dlt | Dango |
|--------|-------------|-------|
| Setup | `dlt init sql_database duckdb` | `dango init` |
| Config | Python script | `.dango/sources.yml` (YAML) |
| Credentials | `.dlt/secrets.toml` | `.dlt/secrets.toml` (same!) |
| Run | `python my_pipeline.py` | `dango sync --source X` |
| dbt | Manual setup | Auto-generates staging models |

**Why the difference?**

Dango uses YAML configuration to:
- Avoid writing Python for standard use cases
- Make configuration version-controllable
- Keep secrets separate from config
- Auto-generate dbt boilerplate

---

## Troubleshooting

### "No module named 'sqlalchemy'"

Install dlt sql_database extras:

```bash
pip install "dlt[sql_database]"
```

### "Could not import source module: sql_database"

The `sql_database` source requires extras:

```bash
pip install "dlt[sql_database]"
```

### Connection Refused

Check:
1. Database is running and accessible
2. Host/port are correct
3. Firewall allows connections
4. Credentials in `.dlt/secrets.toml` are correct

Test connection:
```bash
# PostgreSQL
psql -h localhost -U myuser -d mydb

# MySQL
mysql -h localhost -u root -p mydb
```

### "Relation does not exist"

Check:
1. `schema` parameter matches database schema
2. `table_names` lists tables that exist
3. User has SELECT permission on tables

List tables:
```sql
-- PostgreSQL
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- MySQL
SHOW TABLES;
```

### Slow Performance

Try:
1. Increase `chunk_size`: `100000`
2. Use `backend: "pyarrow"` (faster than SQLAlchemy)
3. Enable incremental loading for large tables
4. Create indexes on cursor columns (for incremental)

---

## Next Steps

- **[Custom Sources](custom-sources.md)** - Write custom SQL with Python
- **[Built-in Sources](built-in-sources.md)** - See all available dlt sources
- **[Transformations](../transformations/index.md)** - Transform database data with dbt
- **[dlt sql_database docs](https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database)** - Official dlt documentation
