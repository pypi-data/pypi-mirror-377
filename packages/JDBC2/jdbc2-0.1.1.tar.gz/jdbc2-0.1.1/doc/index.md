# jdbc2 Documentation (Sample)

This repository provides a minimal Python DB-API 2.0 interface that talks to databases via JDBC using JPype. It also includes a lightweight SQLAlchemy dialect so you can use SQLAlchemy by supplying a `creator`.

This page shows how to connect to SQLite and PostgreSQL and how to run the included examples.

## Prerequisites

- Python 3.8+
- JPype1
  - Install with: `pip install jpype1`
- JDBC driver JAR for your target database
  - SQLite (Xerial): https://github.com/xerial/sqlite-jdbc
  - PostgreSQL: https://jdbc.postgresql.org/
- On Windows, use backslashes in paths. Examples below assume PowerShell or `cmd.exe`.

## API overview

Use the `jdbc2.core.connect()` function to obtain a DB-API 2.0 `Connection`:

- `jdbc_url`: JDBC URL, e.g. `jdbc:sqlite:C:\\tmp\\test.db` or `jdbc:postgresql://localhost:5432/postgres`
- `driver`: Fully-qualified JDBC driver class, e.g. `org.sqlite.JDBC` or `org.postgresql.Driver`
- `user` / `password`: Optional credentials (required for PostgreSQL)
- `jars`: List of JAR paths to add to the JVM classpath
- `jvm_args`: Optional list of extra JVM arguments (e.g. ["-Xmx512m"])

Example skeleton:

```python
from jdbc2.core import connect

with connect(jdbc_url="jdbc:...", driver="com.vendor.Driver", jars=[r"C:\\path\\to\\driver.jar"]) as conn:
    cur = conn.cursor()
    cur.execute("select 1")
    print(cur.fetchall())
```

## Quick reference: JDBC connection strings and drivers

Below are common JDBC URLs, driver class names, and notes. Supply these to jdbc2.core.connect along with the path(s) to the driver JAR(s) via the jars parameter.

- SQLite
  - Driver: org.sqlite.JDBC
  - URL: jdbc:sqlite:C:\\path\\to\\file.db
  - Driver JAR: Xerial SQLite JDBC (https://github.com/xerial/sqlite-jdbc)
- PostgreSQL
  - Driver: org.postgresql.Driver
  - URL: jdbc:postgresql://localhost:5432/yourdb
  - Driver JAR: https://jdbc.postgresql.org/
- MySQL
  - Driver: com.mysql.cj.jdbc.Driver
  - URL: jdbc:mysql://localhost:3306/yourdb?serverTimezone=UTC
  - Driver JAR: https://dev.mysql.com/downloads/connector/j/
- MariaDB
  - Driver: org.mariadb.jdbc.Driver
  - URL: jdbc:mariadb://localhost:3306/yourdb
  - Driver JAR: https://mariadb.com/kb/en/about-mariadb-connector-j/
- Microsoft SQL Server
  - Driver: com.microsoft.sqlserver.jdbc.SQLServerDriver
  - URL: jdbc:sqlserver://localhost:1433;databaseName=yourdb;encrypt=true;trustServerCertificate=true
  - Driver JAR: https://learn.microsoft.com/sql/connect/jdbc/microsoft-jdbc-driver-for-sql-server
- Oracle
  - Driver: oracle.jdbc.OracleDriver
  - URL (Service): jdbc:oracle:thin:@//host:1521/servicename
  - URL (SID):     jdbc:oracle:thin:@host:1521:SID
  - Driver JAR: ojdbc8/ojdbc11 (https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html)
- H2
  - Driver: org.h2.Driver
  - URL (file): jdbc:h2:C:\\path\\to\\h2db
  - URL (mem):  jdbc:h2:mem:test;DB_CLOSE_DELAY=-1
  - Driver JAR: https://h2database.com/
- HSQLDB
  - Driver: org.hsqldb.jdbc.JDBCDriver
  - URL (file): jdbc:hsqldb:file:C:\\path\\to\\hsqldb
  - URL (mem):  jdbc:hsqldb:mem:mymemdb
  - Driver JAR: http://hsqldb.org/
- IBM Db2
  - Driver: com.ibm.db2.jcc.DB2Driver
  - URL: jdbc:db2://localhost:50000/YOURDB
  - Driver JAR: IBM Data Server Driver for JDBC and SQLJ
- Snowflake
  - Driver: net.snowflake.client.jdbc.SnowflakeDriver
  - URL: jdbc:snowflake://<account>.snowflakecomputing.com/?db=YOURDB&schema=PUBLIC&warehouse=COMPUTE_WH&role=SYSADMIN
  - Driver JAR: https://docs.snowflake.com/en/developer-guide/jdbc/jdbc
- Microsoft Access (via UCanAccess)
  - Driver: net.ucanaccess.jdbc.UcanaccessDriver
  - URL: jdbc:ucanaccess://C:/path/to/file.accdb;memory=false
  - JARs: ucanaccess-<ver>.jar plus dependencies (jackcess, hsqldb, commons-logging, commons-lang)
  - Download: http://ucanaccess.sourceforge.net/site.html
  - Note: Put all required JARs on the classpath by passing them in the jars list.

On Windows, remember to escape backslashes in Python strings (e.g., r"C:\\path\\to\\driver.jar").

## Running the examples

Examples are configured via a local INI file at `examples\config.ini`. A template is provided as `examples\config.ini.sample` — copy it to `config.ini` in the same folder and edit the paths and settings.

### Configure
1) Download the appropriate JDBC driver JAR(s):
   - SQLite (Xerial): e.g. `sqlite-jdbc-3.45.3.0.jar`
   - PostgreSQL: e.g. `postgresql-42.7.4.jar`
2) Create `examples\config.ini` with contents like:

```
[sqlite]
jar = C:\\path\\to\\sqlite-jdbc-3.45.3.0.jar
# optional
# db_path = C:\\tmp\\sqlite_jdbc2_demo.db

[postgres]
jar = C:\\path\\to\\postgresql-42.7.4.jar
url = jdbc:postgresql://localhost:5432/postgres
user = postgres
password = postgres
```

### Run DB-API examples
- SQLite:
  ```powershell
  python examples\sqlite_example.py
  ```
- PostgreSQL:
  ```powershell
  python examples\postgres_example.py
  ```

### Run SQLAlchemy examples
- SQLite + SQLAlchemy (Core):
  ```powershell
  python examples\sqlalchemy_sqlite_example.py
  ```
- SQLite + SQLAlchemy (ORM):
  ```powershell
  python examples\sqlalchemy_sqlite_orm_example.py
  ```
- PostgreSQL + SQLAlchemy:
  ```powershell
  python examples\sqlalchemy_postgres_example.py
  ```

The scripts will create demo tables as needed, insert rows, and print results.

## Using with SQLAlchemy

This project ships a simple SQLAlchemy dialect that is auto-registered at import time. You can create an engine by passing a `creator` function that returns a `jdbc2.core.Connection`:

```python
from sqlalchemy import create_engine, text
from jdbc2.core import connect

jdbc_url = "jdbc:sqlite:C:\\tmp\\sa_demo.db"
driver = "org.sqlite.JDBC"
jar = r"C:\\path\\to\\sqlite-jdbc-3.50.3.0.jar"

engine = create_engine(
    "jdbc2://",  # DSN placeholder; actual connection comes from args
    jdbc_url=jdbc_url, driver=driver, jars=[jar])

with engine.begin() as conn:
    res = conn.execute(text("select 1 as x"))
    print(list(res))
```

## Troubleshooting

- ImportError: JPype1 is required to use jdbc2
  - Install JPype1 with `pip install jpype1`.
- JVM not starting or class not found
  - Ensure you pass the correct path to the JDBC driver JAR via the `jars` parameter and that the path exists.
- Authentication failures (PostgreSQL)
  - Verify `PG_JDBC_URL`, `PG_USER`, and `PG_PASSWORD`. Check server connectivity and SSL requirements.

## License

This is sample documentation for demonstration purposes.
