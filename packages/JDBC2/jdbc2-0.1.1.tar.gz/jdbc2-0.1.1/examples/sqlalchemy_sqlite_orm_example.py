"""
SQLAlchemy ORM + SQLite example using jdbc2 with a creator.

Configuration is read from examples\\config.ini:

[sqlite]
jar = C:\\path\\to\\sqlite-jdbc-3.45.3.0.jar
# optional, defaults to a file next to this script
# db_path = C:\\tmp\\sqlite_jdbc2_demo.db

Run:
    python examples\\sqlalchemy_sqlite_orm_example.py
"""
from __future__ import annotations

import configparser
from pathlib import Path
from typing import Iterable

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session

# SQLAlchemy 2.0 preferred Declarative API, with fallback to older declarative_base
try:  # SQLAlchemy 2.0+
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    class Base(DeclarativeBase):
        pass
except Exception:  # pragma: no cover - fallback for SQLAlchemy 1.4
    from sqlalchemy.orm import declarative_base
    from sqlalchemy import Integer, String

    Base = declarative_base()  # type: ignore

    # Provide stand-ins so code below still type-checks/exeuctes on 1.4
    def mapped_column(*args, **kwargs):  # type: ignore
        return None

    class Mapped:  # type: ignore
        pass

from jdbc2.core import connect


DEF_CONFIG_PATH = Path(__file__).with_name("config.ini")


def read_sqlite_config(config_path: Path = DEF_CONFIG_PATH):
    cp = configparser.ConfigParser()
    if not config_path.exists():
        raise SystemExit(
            f"Missing config file: {config_path}. Create it with a [sqlite] section containing 'jar' and optional 'db_path'."
        )
    cp.read(config_path)
    if "sqlite" not in cp:
        raise SystemExit("[sqlite] section missing in config.ini")
    section = cp["sqlite"]
    jar = section.get("jar", "").strip()
    if not jar:
        raise SystemExit("[sqlite] 'jar' is required in config.ini")
    jar_path = Path(jar)
    if not jar_path.exists():
        raise SystemExit(f"SQLite JDBC JAR not found: {jar_path}")
    db_path_str = section.get("db_path", "").strip()
    if db_path_str:
        db_path = Path(db_path_str)
    else:
        db_path = Path(__file__).with_suffix(".db")
    return jar_path, db_path


# Define ORM model
try:
    # If SQLAlchemy 2.0 types are available, use typing annotations
    class Person(Base):  # type: ignore
        __tablename__ = "person"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column()
except TypeError:
    # Fallback definition for older SQLAlchemy using Column/Integer/String
    from sqlalchemy import Column, Integer, String

    class Person(Base):  # type: ignore
        __tablename__ = "person"
        id = Column(Integer, primary_key=True)
        name = Column(String, nullable=False)


def main() -> None:
    jar_path, db_path = read_sqlite_config()
    jdbc_url = f"jdbc:sqlite:{db_path}"
    driver = "org.sqlite.JDBC"

    engine = create_engine(
        "jdbc2://",
        jdbc_url=jdbc_url, driver=driver, jars=[str(jar_path)])

    # Create tables
    Base.metadata.create_all(engine)

    # Insert some rows with a Session
    with Session(engine) as session:
        # Only insert if table is empty to keep example idempotent
        count = session.scalar(select(func.count()).select_from(Person))
        if not count:
            session.add_all([Person(name="Ada"), Person(name="Linus")])
            session.commit()

    # Query and print
    with Session(engine) as session:
        people: Iterable[Person] = session.scalars(select(Person).order_by(Person.id))
        print([{"id": p.id, "name": p.name} for p in people])


if __name__ == "__main__":
    main()
