"""
jdbc2 package initializer.

- Re-exports primary DB-API symbols from jdbc2.core for convenience.
- Optionally imports the SQLAlchemy dialect module for side-effect registration
  when SQLAlchemy is installed. If SQLAlchemy is not installed, jdbc2 remains
  fully usable as a DB-API 2.0 driver without raising ImportError.
"""
from __future__ import annotations

# Re-export common DB-API items
from .core import (
    connect,
    Connection,
    Cursor,
    Error,
    apilevel,
    threadsafety,
    paramstyle,
)

# Attempt to import the SQLAlchemy dialect for its side-effect: it registers the
# "jdbc2" dialect with SQLAlchemy's dialect registry. This is optional; if
# SQLAlchemy (or the dialect's dependencies) aren't installed, just skip.
try:  # pragma: no cover - optional integration
    from . import sqlalchemy_dialect as _jdbc2_sa_dialect  # noqa: F401
except Exception:  # broad except to avoid import-time failures when optional
    pass