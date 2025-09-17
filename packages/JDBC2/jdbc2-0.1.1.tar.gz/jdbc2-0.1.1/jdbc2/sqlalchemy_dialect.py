"""
SQLAlchemy dialect for jdbc2.

This is a very small, generic JDBC-backed dialect intended for use with drivers
that support standard SQL over JDBC. For vendor-specific features, extend this
module with dedicated subclasses.

Usage URL: 'jdbc2+generic://'

Database URL format examples:
- postgresql via JDBC driver jar on classpath:
    create_engine(
        'jdbc2+generic://',
        connect_args={
            'jdbc_url': 'jdbc:postgresql://localhost:5432/mydb',
            'driver': 'org.postgresql.Driver',
            'user': 'me', 'password': 'secret',
            'classpath': ['C:/path/postgresql-42.7.3.jar']
        }
    )
"""

#   Copyright (c) 2025. Euan Duncan Macinnes, euan.d.macinnes@gmail.com, S7479622B - All Rights Reserved


from __future__ import annotations

from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.sql import compiler
from sqlalchemy.dialects import registry as _sa_registry

from . import core as jdbc2_dbapi

# Ensure the dialect is available even when jdbc2 isn't installed as a package with entrypoints.
# This mirrors setuptools entry point: 'sqlalchemy.dialects': 'jdbc2 = jdbc2.sqlalchemy_dialect:JDBC2Dialect'
try:
    _sa_registry.register("jdbc2.generic", "jdbc2.sqlalchemy_dialect", "JDBC2Dialect")
    _sa_registry.register("jdbc2", "jdbc2.sqlalchemy_dialect", "JDBC2Dialect")
except Exception:
    # Registration is best-effort; SQLAlchemy may already have it or registry may not be available.
    pass

try:
    import jpype
    from jpype import JArray, JClass, JString
except Exception:
    jpype = None
    JArray = JClass = JString = None


class JDBC2IdentifierPreparer(compiler.IdentifierPreparer):
    pass


class JDBC2Dialect(DefaultDialect):
    name = "jdbc2"
    driver = "generic"
    supports_native_boolean = True
    supports_native_decimal = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    default_paramstyle = jdbc2_dbapi.paramstyle
    preparer = JDBC2IdentifierPreparer

    supports_statement_cache = True

    @classmethod
    def import_dbapi(cls):
        # SQLAlchemy 2.0+ renamed dbapi() to import_dbapi(); return our DB-API module
        return jdbc2_dbapi

    @classmethod
    def dbapi(cls):
        # Backwards compatibility for SQLAlchemy < 2.0; delegate to import_dbapi()
        return cls.import_dbapi()

    def create_connect_args(self, url):
        # All parameters are passed via connect_args, so return empty args/kwargs
        return ([], {})

    def connect(self, *cargs, **ckw):  # type: ignore[override]
        # SQLAlchemy will call dbapi.connect() with connect_args via creator
        # To support URL query, merge here too if needed in future versions.
        return super().connect(*cargs, **ckw)

    def get_isolation_level(self, connection):
        # Not implemented; defer to DB defaults
        return "AUTOCOMMIT"

    # -------------------- Metadata helpers --------------------
    def _get_jconn(self, connection):
        """
        Retrieve the underlying java.sql.Connection from a SQLAlchemy Connection.

        SQLAlchemy 1.4/2.0 may wrap the DB-API connection in multiple layers.
        We try several access paths to find our jdbc2.core.Connection and its
        _jconn attribute.
        """
        # SA Connection -> (maybe) .connection (Dialect-specific wrapper)
        raw = getattr(connection, 'connection', None) or connection
        # SQLAlchemy 2.0: raw may expose .dbapi_connection
        dbapi_conn = getattr(raw, 'dbapi_connection', None) or raw
        # Some wrappers expose .driver_connection or a nested .connection
        candidate = getattr(dbapi_conn, 'driver_connection', None) or getattr(dbapi_conn, 'connection', None) or dbapi_conn
        jconn = getattr(candidate, '_jconn', None)
        if jconn is None:
            raise RuntimeError("Underlying JDBC connection not available on DB-API connection")
        return jconn

    def _get_metadata(self, connection):
        return self._get_jconn(connection).getMetaData()

    def _resultset_iter(self, rs):
        # Yield dict rows from a java.sql.ResultSet
        md = rs.getMetaData()
        col_count = md.getColumnCount()
        labels = [md.getColumnLabel(i) for i in range(1, col_count + 1)]
        while rs.next():
            row = {}
            for i, label in enumerate(labels, start=1):
                row[str(label)] = rs.getObject(i)
            yield row
        rs.close()

    # -------------------- Reflection API --------------------
    def get_schema_names(self, connection, **kw):
        try:
            md = self._get_metadata(connection)
            rs = md.getSchemas()
            out = [r.get("TABLE_SCHEM") for r in self._resultset_iter(rs) if r.get("TABLE_SCHEM")]
            return out
        except Exception:
            return []

    def has_table(self, connection, table_name, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            types = None
            rs = md.getTables(None, schema, table_name, types)
            for _ in self._resultset_iter(rs):
                return True
            return False
        except Exception:
            return False

    def get_table_names(self, connection, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            types = None
            if jpype:
                types = JArray(JString)(["TABLE"])
            rs = md.getTables(None, schema, "%", types)
            return [r.get("TABLE_NAME") for r in self._resultset_iter(rs)]
        except Exception:
            return []

    def get_view_names(self, connection, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            types = None
            if jpype:
                types = JArray(JString)(["VIEW"])
            rs = md.getTables(None, schema, "%", types)
            return [r.get("TABLE_NAME") for r in self._resultset_iter(rs)]
        except Exception:
            return []

    def get_view_definition(self, connection, viewname, schema=None, **kw):
        # Generic JDBC DatabaseMetaData does not provide view definitions portably
        # Returning None is acceptable; callers should handle this.
        try:
            return None
        except Exception:
            return None

    def get_columns(self, connection, table_name, schema=None, **kw):
        # Return list of column dicts compatible with SQLAlchemy's Inspector
        from sqlalchemy.sql import sqltypes
        cols = []
        try:
            md = self._get_metadata(connection)
            rs = md.getColumns(None, schema, table_name, "%")
            for r in self._resultset_iter(rs):
                name = r.get("COLUMN_NAME")
                nullable = (int(r.get("NULLABLE") or 0) != 0)
                default = r.get("COLUMN_DEF")
                # Data type mapping is vendor-specific; expose generic NULLTYPE to keep it portable
                coltype = sqltypes.NULLTYPE
                autoinc = False
                comment = r.get("REMARKS")
                cols.append({
                    "name": name,
                    "type": coltype,
                    "nullable": nullable,
                    "default": default,
                    "autoincrement": autoinc,
                    "comment": comment,
                })
            return cols
        except Exception:
            return cols

    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            rs = md.getPrimaryKeys(None, schema, table_name)
            rows = list(self._resultset_iter(rs))
            cols = [r.get("COLUMN_NAME") for r in sorted(rows, key=lambda x: int(x.get("KEY_SEQ") or 0))]
            name = rows[0].get("PK_NAME") if rows else None
            return {"constrained_columns": cols, "name": name}
        except Exception:
            return {"constrained_columns": [], "name": None}

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            rs = md.getImportedKeys(None, schema, table_name)
            fks = {}
            for r in self._resultset_iter(rs):
                fk_name = r.get("FK_NAME") or f"fk_{table_name}"
                col = r.get("FKCOLUMN_NAME")
                ref_table = r.get("PKTABLE_NAME")
                ref_schema = r.get("PKTABLE_SCHEM")
                ref_col = r.get("PKCOLUMN_NAME")
                entry = fks.setdefault(fk_name, {
                    "name": fk_name,
                    "constrained_columns": [],
                    "referred_schema": ref_schema,
                    "referred_table": ref_table,
                    "referred_columns": [],
                })
                entry["constrained_columns"].append(col)
                entry["referred_columns"].append(ref_col)
            return list(fks.values())
        except Exception:
            return []

    def get_indexes(self, connection, table_name, schema=None, **kw):
        try:
            md = self._get_metadata(connection)
            # unique=False -> include both unique and non-unique
            rs = md.getIndexInfo(None, schema, table_name, False, True)
            idx_map = {}
            for r in self._resultset_iter(rs):
                name = r.get("INDEX_NAME")
                if not name:
                    continue
                col = r.get("COLUMN_NAME")
                unique = not bool(r.get("NON_UNIQUE")) if r.get("NON_UNIQUE") is not None else False
                entry = idx_map.setdefault(name, {"name": name, "column_names": [], "unique": unique})
                if col:
                    entry["column_names"].append(col)
            return list(idx_map.values())
        except Exception:
            return []

    def get_unique_constraints(self, connection, table_name, schema=None, **kw):
        # Not reliably exposed; return empty and let get_indexes handle unique indexes
        return []

    def get_check_constraints(self, connection, table_name, schema=None, **kw):
        # No portable exposure via JDBC metadata
        return []


# entrypoint expects: sqlalchemy.dialects namespace
# registered in setup.py as: 'jdbc2 = jdbc2.sqlalchemy_dialect:JDBC2Dialect'
