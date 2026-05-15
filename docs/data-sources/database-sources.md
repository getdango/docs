# Database Sources

Connect to PostgreSQL, MySQL, MongoDB, SQLite, SQL Server, and other databases.

---

## Overview

Dango supports SQL and NoSQL databases as data sources. **PostgreSQL** and **MongoDB** have full wizard support — set them up with `dango source add`. Other databases (MySQL, SQLite, SQL Server, Snowflake, BigQuery) use the manual `dlt_native` approach with dlt's `sql_database` source.

**Supported Databases**:

| Database | Setup Method |
|----------|-------------|
| PostgreSQL | Wizard (`dango source add`) |
| MongoDB | Wizard (`dango source add`) |
| MySQL / MariaDB | Manual (`dlt_native`) |
| SQLite | Manual (`dlt_native`) |
| Microsoft SQL Server | Manual (`dlt_native`) |
| Snowflake | Manual (`dlt_native`) |
| BigQuery | Manual (`dlt_native`) |
| Any SQLAlchemy-compatible | Manual (`dlt_native`) |

---

## Quick Start: PostgreSQL

PostgreSQL is a wizard-enabled source. The wizard handles configuration and credential setup.

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: PostgreSQL
? Source name: my_postgres
? Environment variable for connection URL [POSTGRES_CREDENTIALS]: POSTGRES_CREDENTIALS
? Schema (default: public): public
? Table names (comma-separated, or blank for all): customers, orders, products
```

The wizard creates your source configuration and prompts you to add the connection URL to `.env`.

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: my_postgres
    type: postgres
    enabled: true
    description: Production PostgreSQL database
    generic_config:
      credentials_env: POSTGRES_CREDENTIALS
      schema: public
      table_names:
        - customers
        - orders
        - products
```

!!! note "Why `generic_config` instead of `postgres`?"
    PostgreSQL and MongoDB use `generic_config` as the YAML key because they share a common configuration model. Sources with dedicated config models (like Stripe, HubSpot) use their type name as the key.

=== "Local"

    Store the connection URL in `.env`:
    ```bash
    # .env (gitignored)
    POSTGRES_CREDENTIALS=postgresql://myuser:mypassword@localhost:5432/mydb
    ```

=== "Cloud"

    Set the connection URL on the remote server:
    ```bash
    dango remote env set POSTGRES_CREDENTIALS "postgresql://myuser:mypassword@dbhost:5432/mydb"
    ```

### First Sync

```bash
dango sync --source my_postgres
```

Data loads into `raw_my_postgres` schema in DuckDB:

```sql
SELECT * FROM raw_my_postgres.customers LIMIT 10;
```

### Connection URL Format

```
postgresql://username:password@host:port/database
```

Examples:

```bash
# Local database
POSTGRES_CREDENTIALS=postgresql://myuser:mypassword@localhost:5432/mydb

# Remote database with SSL
POSTGRES_CREDENTIALS=postgresql://myuser:mypassword@db.example.com:5432/mydb?sslmode=require

# AWS RDS
POSTGRES_CREDENTIALS=postgresql://admin:secret@mydb.abc123.us-east-1.rds.amazonaws.com:5432/mydb
```

---

## Quick Start: MongoDB

MongoDB is a wizard-enabled source. It supports document collections with automatic schema flattening.

### Via Wizard (Recommended)

```bash
dango source add
```

```
? Select a data source: MongoDB
? Source name: my_mongo
? Environment variable for connection URL [MONGODB_CONNECTION_URL]: MONGODB_CONNECTION_URL
? Database name: mydb
? Collection names (comma-separated, or blank for all): users, events, products
? Enable parallel collection loading? No
```

### Via Configuration File

Edit `.dango/sources.yml`:

```yaml
version: '1.0'
sources:
  - name: my_mongo
    type: mongodb
    enabled: true
    description: MongoDB application database
    generic_config:
      connection_url_env: MONGODB_CONNECTION_URL
      database: mydb
      collection_names:
        - users
        - events
        - products
      parallel: false
```

=== "Local"

    Store the connection URL in `.env`:
    ```bash
    # .env (gitignored)
    MONGODB_CONNECTION_URL=mongodb://myuser:mypassword@localhost:27017/mydb
    ```

=== "Cloud"

    Set the connection URL on the remote server:
    ```bash
    dango remote env set MONGODB_CONNECTION_URL "mongodb+srv://myuser:mypassword@cluster.mongodb.net/mydb"
    ```

### First Sync

```bash
dango sync --source my_mongo
```

Data loads into `raw_my_mongo` schema in DuckDB:

```sql
SELECT * FROM raw_my_mongo.users LIMIT 10;
```

### Connection URL Format

```
mongodb://username:password@host:port/database
mongodb+srv://username:password@cluster.mongodb.net/database
```

### Parallel Loading

For large databases with many collections, enable parallel loading for faster syncs:

```yaml
generic_config:
  connection_url_env: MONGODB_CONNECTION_URL
  database: mydb
  parallel: true
```

!!! note "MongoDB document flattening"
    MongoDB documents are nested JSON. dlt flattens nested objects into columns using `__` separators. For example, `address.city` becomes `address__city`.

---

## Other Databases (Manual dlt_native Setup)

MySQL, SQLite, SQL Server, Snowflake, BigQuery, and other SQLAlchemy-compatible databases use the `dlt_native` source type with dlt's `sql_database` source.

### Step 1: Install Dependencies

```bash
# Activate your project's virtual environment
source venv/bin/activate

# Install dlt sql_database extras + database driver
pip install "dlt[sql_database]" psycopg2-binary    # PostgreSQL
pip install "dlt[sql_database]" pymysql             # MySQL
pip install "dlt[sql_database]" pyodbc              # SQL Server
pip install "dlt[sql_database]"                     # SQLite (built-in)
pip install "dlt[sql_database]" snowflake-sqlalchemy # Snowflake
pip install "dlt[sql_database]" sqlalchemy-bigquery  # BigQuery
```

### Step 2: Configure Credentials

Add credentials to `.dlt/secrets.toml` (gitignored):

=== "MySQL"

    ```toml
    [sources.sql_database.credentials]
    drivername = "mysql+pymysql"
    database = "mydb"
    username = "root"
    password = "secret"
    host = "localhost"
    port = 3306
    ```

=== "SQLite"

    ```toml
    [sources.sql_database]
    credentials = "sqlite:///path/to/database.db"
    ```

=== "SQL Server"

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

=== "Snowflake"

    ```toml
    [sources.sql_database.credentials]
    drivername = "snowflake"
    username = "myuser"
    password = "mypassword"
    host = "myaccount.snowflakecomputing.com"
    database = "mydb"
    query = { warehouse = "COMPUTE_WH", role = "ANALYST" }
    ```

### Step 3: Add Source to sources.yml

```yaml
version: '1.0'
sources:
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

!!! note "Credentials location"
    For `dlt_native` database sources, credentials go in `.dlt/secrets.toml` (not `.env`). The `sources.yml` file only contains non-sensitive configuration.

### Step 4: Sync

```bash
dango sync --source my_mysql
```

---

## Advanced Configuration

### Load All Tables in Schema

Omit `table_names` to load all tables:

=== "Wizard (PostgreSQL/MongoDB)"

    Leave the table/collection names blank when prompted.

=== "Manual (dlt_native)"

    ```yaml
    function_kwargs:
      schema: "public"
      # No table_names specified = load all tables
    ```

### Multiple Schemas

Create separate sources for each schema:

```yaml
- name: public_tables
  type: postgres
  enabled: true
  generic_config:
    credentials_env: POSTGRES_CREDENTIALS
    schema: public

- name: analytics_tables
  type: postgres
  enabled: true
  generic_config:
    credentials_env: POSTGRES_CREDENTIALS
    schema: analytics
```

### Performance Tuning (dlt_native)

```yaml
function_kwargs:
  chunk_size: 100000        # Larger batches (faster, more memory)
  backend: "pyarrow"        # Faster than sqlalchemy
  reflection_level: "minimal"  # Skip detailed schema info
```

### SSL Connections

Include SSL parameters in your connection URL:

```bash
# .env (PostgreSQL with SSL)
POSTGRES_CREDENTIALS=postgresql://user:pass@host:5432/db?sslmode=require

# Or in .dlt/secrets.toml
# [sources.sql_database]
# credentials = "postgresql://user:pass@host:5432/db?sslmode=require"
```

---

## Incremental Loading

### Date-Based Incremental (dlt_native)

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

By default, database sources perform a **full table load**:

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

`sql_database` loads full tables — you cannot specify WHERE clauses or custom SQL.

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
2. Staging models are automatically regenerated during sync
3. Custom dbt models may need manual updates

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

`.dlt/secrets.toml` and `.env` are automatically gitignored. Verify:

```bash
cat .gitignore | grep -E "secrets|\.env"
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

For production databases, always use SSL connections.

### 5. Rotate Credentials Regularly

Update `.env` or `.dlt/secrets.toml` when rotating database passwords.

---

## Troubleshooting

### Connection Refused

Check:
1. Database is running and accessible
2. Host/port are correct
3. Firewall allows connections
4. Credentials are correct

Test connection:
```bash
# PostgreSQL
psql "postgresql://myuser:mypassword@localhost:5432/mydb"

# MySQL
mysql -h localhost -u root -p mydb

# MongoDB
mongosh "mongodb://myuser:mypassword@localhost:27017/mydb"
```

### "No module named 'sqlalchemy'" (dlt_native only)

Install dlt sql_database extras:

```bash
pip install "dlt[sql_database]"
```

### "Relation does not exist"

Check:
1. Schema name matches database schema (e.g., `public` for PostgreSQL)
2. `table_names` lists tables that actually exist
3. User has SELECT permission on tables

### Slow Performance

Try:
1. Increase `chunk_size`: `100000` (dlt_native)
2. Use `backend: "pyarrow"` (faster than SQLAlchemy)
3. Enable incremental loading for large tables
4. Limit `table_names` to only needed tables

---

## Next Steps

- **[Adding Sources](adding-sources.md)** - Full wizard walkthrough
- **[Custom Sources](custom-sources.md)** - Write custom SQL with Python
- **[Source Catalog](source-catalog.md)** - See all available sources
- **[Sync Modes](sync-modes.md)** - Incremental vs. full refresh
- **[Transformations](../transformations/index.md)** - Transform database data with dbt
- [dlt sql_database docs](https://dlthub.com/docs/dlt-ecosystem/verified-sources/sql_database) - Official dlt documentation
