"""
jdbc2.core: Minimal DB-API 2.0 layer over Java JDBC via JPype.

This module intentionally implements a small, safe subset of DB-API:
- connect(jdbc_url, driver, user=None, password=None, properties=None, jvm_path=None, classpath=None)
- Connection: cursor(), commit(), rollback(), close(), context manager
- Cursor: execute(), executemany(), fetchone(), fetchall(), fetchmany(), close(), description, rowcount

Thread-safety: 1 (threads may share the module, but not connections/cursors).
Paramstyle: pyformat (named parameters using %(name)s) and qmark (?) are both supported at API level; internally we use JDBC prepared statements.

Note: To keep this initial version dependency-light, we require JPype1 at runtime.
"""

from __future__ import annotations

import os
import threading
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import jpype
import jpype.imports

apilevel = "2.0"
threadsafety = 1
paramstyle = "qmark"

_jvm_lock = threading.Lock()
_jvm_started = False


def _ensure_jvm(
        jvm_path: Optional[str] = None,
        classpath: Optional[Sequence[str]] = None,
        jvm_args: Optional[Sequence[str]] = None,
) -> None:
    """Start the JVM once per process using JPype.

    Parameters:
        jvm_path: Optional explicit path to the JVM library. If None, use JPype's default.
        classpath: Optional list of classpath entries (directories or JARs) to add.
        jvm_args: Optional additional JVM arguments such as ["-Xmx512m"].

    Notes:
        This function is thread-safe and will only attempt to start the JVM once.
        Non-existent classpath entries are ignored to avoid startup errors.
    """
    global _jvm_started
    if jpype is None:
        raise ImportError("JPype1 is required to use jdbc2. Please install jpype1.")
    if _jvm_started:
        return
    with _jvm_lock:
        if _jvm_started:
            return
        jp_args: List[str] = []
        # Build classpath option; when overriding, include JPype's default classpath too
        if classpath:
            try:
                default_cp = jpype.getClassPath() or ""
            except Exception:
                default_cp = ""
            cp_parts: List[str] = []
            if default_cp:
                cp_parts.extend([p for p in default_cp.split(os.pathsep) if p])
            cp_parts.extend(list(classpath))
            # filter out paths that do not exist to avoid startup errors on missing optional jars
            filtered: List[str] = []
            for p in cp_parts:
                if not p:
                    continue
                try:
                    if os.path.exists(p):
                        filtered.append(p)
                    else:
                        # Silently ignore absent entries like optional support jars
                        pass
                except Exception:
                    # If os.path.exists fails for any reason, skip the entry
                    pass
            # dedupe while preserving order
            seen = set()
            merged = []
            for p in filtered:
                if p not in seen:
                    merged.append(p)
                    seen.add(p)
            print("CLASSPATH:", merged)
            cp_opt = f"-Djava.class.path={os.pathsep.join(merged)}"
            jp_args.append(cp_opt)
        # Additional JVM args
        if jvm_args:
            jp_args.extend(jvm_args)
        # Use jpype.startJVM options
        if not jpype.isJVMStarted():
            jpype.startJVM(jvm_path or jpype.getDefaultJVMPath(), *jp_args)
        _jvm_started = True


class Error(Exception):
    """Base exception for jdbc2 errors."""
    pass


class Connection:
    """DB-API 2.0 Connection wrapper over a java.sql.Connection.

    Instances are not thread-safe. Use cursor() to create Cursor objects.
    """
    def __init__(self, jconn, autocommit: bool = True):
        self._jconn = jconn
        self._closed = False
        self.autocommit = bool(autocommit)
        try:
            self._jconn.setAutoCommit(self.autocommit)
        except Exception:
            # Some drivers may not support transactions; ignore inability to set autocommit
            pass

    def cursor(self) -> "Cursor":
        """Return a new Cursor object bound to this connection."""
        self._check_open()
        return Cursor(self)

    def commit(self) -> None:
        """Commit the current transaction. No-op if autocommit is True."""
        self._check_open()
        if self.autocommit:
            return
        self._jconn.commit()

    def rollback(self) -> None:
        """Roll back the current transaction. No-op if autocommit is True."""
        self._check_open()
        if self.autocommit:
            return
        self._jconn.rollback()

    def close(self) -> None:
        """Close the connection and release underlying JDBC resources.

        Safe to call multiple times.
        """
        if not self._closed:
            try:
                self._jconn.close()
            finally:
                self._closed = True

    def _check_open(self):
        """Raise Error if the connection has been closed."""
        if self._closed:
            raise Error("Connection is closed")

    def __enter__(self) -> "Connection":
        """Support with-statement: returns self after checking open state."""
        self._check_open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """On context exit, commit if no exception, else rollback; then close.

        If autocommit is True, commit/rollback are skipped as they are no-ops.
        """
        try:
            if not self.autocommit:
                if exc is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            self.close()


class Cursor:
    """DB-API 2.0 Cursor wrapper over a JDBC PreparedStatement/ResultSet.

    Created by Connection.cursor(). Not thread-safe and bound to its Connection.
    """
    def __init__(self, connection: Connection):
        """Initialize the cursor bound to a Connection.

        Parameters:
            connection: The owning Connection instance.
        """
        self.connection = connection
        self.arraysize = 1000
        self._jstmt = None
        self._jrs = None
        self.description: Optional[List[Tuple]] = None
        self.rowcount = -1
        self.lastrowid = None  # DB-API attribute: row id of last modified row, if available
        self._closed = False

    def close(self) -> None:
        """Close the cursor and release JDBC resources.

        Safe to call multiple times.
        """
        if self._closed:
            return
        try:
            if self._jrs is not None:
                self._jrs.close()
            if self._jstmt is not None:
                self._jstmt.close()
        finally:
            self._jrs = None
            self._jstmt = None
            self._closed = True

    def execute(self, operation: str, parameters: Optional[Dict[str, Any] | Sequence[Any]] = None):
        """Execute a SQL operation with optional parameters.

        Parameters:
            operation: SQL string with JDBC parameter placeholders '?'.
            parameters: Sequence of positional parameters. Named dict not supported.
        Returns:
            self for chaining.
        Raises:
            Error: If named parameters are provided or cursor is closed.
        """
        self._check_open()
        jconn = self.connection._jconn
        # Prepare statement; request generated keys to support lastrowid when possible
        from jpype import JClass  # local import to avoid module-level JPype dependency shenanigans
        Statement = JClass("java.sql.Statement")
        try:
            self._jstmt = jconn.prepareStatement(operation, Statement.RETURN_GENERATED_KEYS)
        except Exception:
            # Fallback if driver/JDBC doesn't support the flag
            self._jstmt = jconn.prepareStatement(operation)
        # Bind params
        if parameters:
            if isinstance(parameters, dict):
                # Named parameters not natively supported by JDBC; simple mapping not implemented in this minimal version.
                raise Error(
                    "Named parameters not supported in this minimal version; use positional parameters with '?'.")
            for idx, val in enumerate(parameters, start=1):
                self._jstmt.setObject(idx, val)
        # Execute
        has_result_set = self._jstmt.execute()
        if has_result_set:
            self._jrs = self._jstmt.getResultSet()
            self._build_description()
            self._consume_rowcount_from_resultset()
        else:
            self._jrs = None
            self.rowcount = self._jstmt.getUpdateCount()
            self.description = None
            # Attempt to populate lastrowid from JDBC generated keys
            try:
                gk = self._jstmt.getGeneratedKeys()
            except Exception:
                gk = None
            last_id = None
            try:
                if gk is not None:
                    if gk.next():
                        try:
                            last_id = gk.getObject(1)
                        except Exception:
                            # As a fallback, try common numeric getters
                            try:
                                last_id = gk.getLong(1)
                            except Exception:
                                try:
                                    last_id = gk.getInt(1)
                                except Exception:
                                    last_id = None
            finally:
                try:
                    if gk is not None:
                        gk.close()
                except Exception:
                    pass
            self.lastrowid = last_id
        return self

    def executemany(self, operation: str, seq_of_parameters: Iterable[Sequence[Any]]):
        """Execute a SQL operation against all parameter sequences.

        Parameters:
            operation: SQL string with '?' placeholders.
            seq_of_parameters: Iterable of parameter sequences to apply.
        Returns:
            self for chaining. rowcount is set to total affected rows.
        """
        self._check_open()
        jconn = self.connection._jconn
        self._jstmt = jconn.prepareStatement(operation)
        total = 0
        for params in seq_of_parameters:
            for idx, val in enumerate(params, start=1):
                self._jstmt.setObject(idx, val)
            total += self._jstmt.executeUpdate()
        self.rowcount = total
        self._jstmt.close()
        self._jstmt = None
        self._jrs = None
        self.description = None
        return self

    def fetchone(self) -> Optional[Tuple]:
        """Fetch the next row of a query result, or None if no more rows."""
        self._check_open()
        if self._jrs is None:
            return None
        if not self._jrs.next():
            return None
        return self._read_current_row()

    def fetchmany(self, size: Optional[int] = None) -> List[Tuple]:
        """Fetch up to 'size' rows; defaults to arraysize if not provided."""
        self._check_open()
        if self._jrs is None:
            return []
        size = size or self.arraysize
        out = []
        count = 0
        while count < size and self._jrs.next():
            out.append(self._read_current_row())
            count += 1
        return out

    def fetchall(self) -> List[Tuple]:
        """Fetch all remaining rows of the result set."""
        self._check_open()
        if self._jrs is None:
            return []
        out = []
        while self._jrs.next():
            out.append(self._read_current_row())
        return out

    def _read_current_row(self) -> Tuple:
        """Read values from the current ResultSet row and return as a tuple."""
        md = self._jrs.getMetaData()
        cols = md.getColumnCount()
        row = []
        for i in range(1, cols + 1):
            row.append(self._jrs.getObject(i))
        return tuple(row)

    def _build_description(self) -> None:
        """Populate DB-API 'description' from ResultSet metadata."""
        md = self._jrs.getMetaData()
        cols = md.getColumnCount()
        desc = []
        for i in range(1, cols + 1):
            name = md.getColumnLabel(i)
            type_code = md.getColumnType(i)
            display_size = md.getColumnDisplaySize(i)
            internal_size = None
            precision = md.getPrecision(i)
            scale = md.getScale(i)
            null_ok = md.isNullable(i) != md.columnNoNulls
            desc.append((name, type_code, display_size, internal_size, precision, scale, null_ok))
        self.description = desc

    def _consume_rowcount_from_resultset(self) -> None:
        """Set rowcount based on JDBC behavior (unknown until iterated)."""
        # JDBC does not provide rowcount without iterating; leave as -1
        self.rowcount = -1

    def _check_open(self):
        """Raise Error if the cursor has been closed."""
        if self._closed:
            raise Error("Cursor is closed")


def connect(
        jdbc_url: str,
        driver: str,
        user: Optional[str] = None,
        password: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        autocommit: bool = True,
        jvm_path: Optional[str] = None,
        classpath: Optional[Sequence[str]] = None,
        jars: Optional[Sequence[str]] = None,
        jvm_args: Optional[Sequence[str]] = None,
) -> Connection:
    """
    Establish a JDBC connection using java.sql.DriverManager.

    Parameters:
        jdbc_url: e.g. "jdbc:postgresql://host/db" or vendor-specific URLs.
        driver: Fully qualified class name of JDBC driver, e.g. "org.postgresql.Driver".
        user, password: Optional credentials.
        properties: Optional dict of additional java.util.Properties entries.
        autocommit: If True (default), enable JDBC autocommit; when False, commit/rollback must be called.
        jvm_path: Optional explicit path to JVM dll.
        classpath: Optional list of jar paths to add to classpath.
        jars: Optional list of additional JAR file paths to add to the classpath.
        jvm_args: Optional list of additional JVM arguments, e.g. ["-Xmx512m"].

    Returns:
        Connection: A DB-API 2.0 Connection wrapper around the JDBC connection.

    Raises:
        ImportError: If JPype1 is not installed.
        Exception: Any exceptions arising from JVM startup or DriverManager.getConnection.
    """
    # Merge classpath and jars for JVM startup
    merged_cp: Optional[List[str]] = None
    if classpath or jars:
        merged_cp = []
        if classpath:
            merged_cp.extend(list(classpath))
        if jars:
            merged_cp.extend(list(jars))

    _ensure_jvm(jvm_path=jvm_path, classpath=merged_cp, jvm_args=jvm_args)

    from jpype import JClass

    # Load driver class to ensure registration
    JClass(driver)()

    DriverManager = JClass("java.sql.DriverManager")
    if properties:
        Properties = JClass("java.util.Properties")
        props = Properties()
        for k, v in properties.items():
            props.setProperty(str(k), str(v))
        if user is not None:
            props.setProperty("user", user)
        if password is not None:
            props.setProperty("password", password)
        jconn = DriverManager.getConnection(jdbc_url, props)
    else:
        if user is None and password is None:
            jconn = DriverManager.getConnection(jdbc_url)
        else:
            jconn = DriverManager.getConnection(jdbc_url, user or "", password or "")

    return Connection(jconn, autocommit=autocommit)
