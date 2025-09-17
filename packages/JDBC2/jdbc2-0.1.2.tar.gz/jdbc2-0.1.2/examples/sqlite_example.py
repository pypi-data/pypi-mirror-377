"""
SQLite example using jdbc2 over JDBC with JPype.

Configuration is read from a local INI file (examples\\config.ini):

[sqlite]
jar = C:\\path\\to\\sqlite-jdbc-3.45.3.0.jar
# optional, defaults to a file next to this script
# db_path = C:\\tmp\\sqlite_jdbc2_demo.db

Run:
    python examples\\sqlite_example.py
"""
from __future__ import annotations

import configparser
from pathlib import Path

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


def main() -> None:
    jar_path, db_path = read_sqlite_config()

    jdbc_url = f"jdbc:sqlite:{db_path}"
    driver = "org.sqlite.JDBC"

    with connect(jdbc_url=jdbc_url, driver=driver, jars=[str(jar_path)]) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            create table if not exists person (
                id integer primary key,
                name text not null
            )
            """
        )
        cur.executemany("insert into person(name) values (?)", [("Ada",), ("Linus",)])
        cur.execute("select id, name from person order by id")
        rows = cur.fetchall()
        print("Rows:")
        for row in rows:
            print(row)

    print(f"Done. Database at: {db_path}")


if __name__ == "__main__":
    main()
