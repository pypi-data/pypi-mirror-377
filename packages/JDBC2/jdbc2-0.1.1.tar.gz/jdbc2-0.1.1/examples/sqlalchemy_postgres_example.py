"""
SQLAlchemy + PostgreSQL example using jdbc2 with a creator.

Configuration is read from examples\\config.ini:

[postgres]
jar = C:\\path\\to\\postgresql-42.7.4.jar
url = jdbc:postgresql://localhost:5432/postgres
user = postgres
password = postgres

Run:
    python examples\\sqlalchemy_postgres_example.py
"""
from __future__ import annotations

import configparser
from pathlib import Path

from sqlalchemy import create_engine, text

DEF_CONFIG_PATH = Path(__file__).with_name("config.ini")


def read_pg_config(config_path: Path = DEF_CONFIG_PATH):
    cp = configparser.ConfigParser()
    if not config_path.exists():
        raise SystemExit(
            f"Missing config file: {config_path}. Create it with a [postgres] section containing 'jar', 'url', 'user', 'password'."
        )
    cp.read(config_path)
    if "postgres" not in cp:
        raise SystemExit("[postgres] section missing in config.ini")
    section = cp["postgres"]
    jar = section.get("jar", "").strip()
    url = section.get("url", "").strip()
    user = section.get("user", "").strip()
    password = section.get("password", "").strip()
    if not jar:
        raise SystemExit("[postgres] 'jar' is required in config.ini")
    if not url:
        raise SystemExit("[postgres] 'url' is required in config.ini")
    if not user:
        raise SystemExit("[postgres] 'user' is required in config.ini")
    if not password:
        raise SystemExit("[postgres] 'password' is required in config.ini")
    jar_path = Path(jar)
    if not jar_path.exists():
        raise SystemExit(f"PostgreSQL JDBC JAR not found: {jar_path}")
    return jar_path, url, user, password


def main() -> None:
    jar_path, jdbc_url, user, password = read_pg_config()
    driver = "org.postgresql.Driver"

    engine = create_engine(
        "jdbc2://",jdbc_url=jdbc_url, driver=driver, user=user, password=password, jars=[str(jar_path)])

    with engine.begin() as conn:
        conn.execute(text(
            """
            create table if not exists jdbc2_demo (
                id serial primary key,
                note text not null
            )
            """
        ))
        conn.execute(text("insert into jdbc2_demo(note) values (:n)"), [{"n": "hello from jdbc2"}])
        res = conn.execute(text("select id, note from jdbc2_demo order by id desc limit 5"))
        print([dict(r._mapping) for r in res])


if __name__ == "__main__":
    main()
