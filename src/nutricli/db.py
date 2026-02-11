"""SQLite database layer for nutrition tracking."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Callable


def get_db_path() -> Path:
    """Resolve the DB path.

    - Default (XDG-ish): ~/.local/share/nutri/nutrition.db
    - Override: NUTRI_DB_PATH
    """

    override = os.environ.get("NUTRI_DB_PATH")
    if override:
        return Path(override).expanduser()

    return Path.home() / ".local" / "share" / "nutri" / "nutrition.db"


SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS meals (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    time        TEXT,
    meal_type   TEXT DEFAULT 'snack',
    description TEXT NOT NULL,
    calories    REAL NOT NULL,
    protein_g   REAL DEFAULT 0,
    carbs_g     REAL DEFAULT 0,
    fat_g       REAL DEFAULT 0,
    fiber_g     REAL DEFAULT 0,
    sugar_g     REAL DEFAULT 0,
    sodium_mg   REAL DEFAULT 0,
    confidence  TEXT DEFAULT 'medium',
    confirmed   BOOLEAN DEFAULT 0,
    source      TEXT DEFAULT 'vision-ai',
    created_at  TEXT DEFAULT (datetime('now')),
    updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS targets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date_from   TEXT NOT NULL,
    calories    REAL NOT NULL,
    protein_g   REAL,
    carbs_g     REAL,
    fat_g       REAL,
    fiber_g     REAL,
    note        TEXT
);

CREATE TABLE IF NOT EXISTS water (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT NOT NULL,
    time        TEXT,
    amount_ml   REAL NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
CREATE INDEX IF NOT EXISTS idx_water_date ON water(date);
"""


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Get a database connection, creating the DB and schema if needed."""
    path = (db_path or get_db_path()).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version < SCHEMA_VERSION:
        _migrate(conn, version)
    elif version > SCHEMA_VERSION:
        raise RuntimeError(
            f"Datenbank-Schema-Version {version} ist neuer als diese CLI "
            f"(max {SCHEMA_VERSION}). Bitte nutri aktualisieren."
        )


def _migrate(conn: sqlite3.Connection, version: int) -> None:
    while version < SCHEMA_VERSION:
        next_version = version + 1
        migration = MIGRATIONS.get(next_version)
        if not migration:
            raise RuntimeError(f"Keine Migration auf Schema-Version {next_version} vorhanden.")
        migration(conn)
        conn.execute(f"PRAGMA user_version = {next_version}")
        version = next_version
    conn.commit()


def _migration_1(conn: sqlite3.Connection) -> None:
    # Schema v1 is the initial schema; tables are created via SCHEMA.
    return None


MIGRATIONS: dict[int, Callable[[sqlite3.Connection], None]] = {
    1: _migration_1,
}


def insert_meal(conn: sqlite3.Connection, **kwargs) -> int:
    cols = list(kwargs.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    cur = conn.execute(
        f"INSERT INTO meals ({col_names}) VALUES ({placeholders})",
        list(kwargs.values()),
    )
    conn.commit()
    return int(cur.lastrowid)


def update_meal(conn: sqlite3.Connection, meal_id: int, **kwargs) -> bool:
    if not kwargs:
        return False
    kwargs["updated_at"] = "datetime('now')"
    sets: list[str] = []
    vals: list[object] = []
    for k, v in kwargs.items():
        if k == "updated_at":
            sets.append(f"{k} = datetime('now')")
        else:
            sets.append(f"{k} = ?")
            vals.append(v)
    vals.append(meal_id)
    cur = conn.execute(
        f"UPDATE meals SET {', '.join(sets)} WHERE id = ?",
        vals,
    )
    conn.commit()
    return cur.rowcount > 0


def delete_meal(conn: sqlite3.Connection, meal_id: int) -> bool:
    cur = conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    conn.commit()
    return cur.rowcount > 0


def confirm_meal(conn: sqlite3.Connection, meal_id: int) -> bool:
    return update_meal(conn, meal_id, confirmed=1)


def get_meal(conn: sqlite3.Connection, meal_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM meals WHERE id = ?", (meal_id,)).fetchone()
    return dict(row) if row else None


def get_meals_by_date(conn: sqlite3.Connection, date: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM meals WHERE date = ? ORDER BY time, id", (date,)).fetchall()
    return [dict(r) for r in rows]


def get_meals_in_range(conn: sqlite3.Connection, date_from: str, date_to: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM meals WHERE date >= ? AND date <= ? ORDER BY date, time, id",
        (date_from, date_to),
    ).fetchall()
    return [dict(r) for r in rows]


def insert_target(conn: sqlite3.Connection, **kwargs) -> int:
    cols = list(kwargs.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    cur = conn.execute(
        f"INSERT INTO targets ({col_names}) VALUES ({placeholders})",
        list(kwargs.values()),
    )
    conn.commit()
    return int(cur.lastrowid)


def get_target_for_date(conn: sqlite3.Connection, date: str) -> dict | None:
    row = conn.execute(
        "SELECT * FROM targets WHERE date_from <= ? ORDER BY date_from DESC LIMIT 1",
        (date,),
    ).fetchone()
    return dict(row) if row else None


def get_all_targets(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM targets ORDER BY date_from DESC").fetchall()
    return [dict(r) for r in rows]


def insert_water(conn: sqlite3.Connection, **kwargs) -> int:
    cols = list(kwargs.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    cur = conn.execute(
        f"INSERT INTO water ({col_names}) VALUES ({placeholders})",
        list(kwargs.values()),
    )
    conn.commit()
    return int(cur.lastrowid)


def get_water_by_date(conn: sqlite3.Connection, date: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM water WHERE date = ? ORDER BY time, id", (date,)).fetchall()
    return [dict(r) for r in rows]


def get_db_stats(conn: sqlite3.Connection) -> dict:
    meal_count = conn.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    days_tracked = conn.execute("SELECT COUNT(DISTINCT date) FROM meals").fetchone()[0]
    first_date = conn.execute("SELECT MIN(date) FROM meals").fetchone()[0]
    water_entries = conn.execute("SELECT COUNT(*) FROM water").fetchone()[0]
    target_count = conn.execute("SELECT COUNT(*) FROM targets").fetchone()[0]
    schema_version = conn.execute("PRAGMA user_version").fetchone()[0]
    db_path = None
    for row in conn.execute("PRAGMA database_list").fetchall():
        if row["name"] == "main":
            db_path = row["file"]
            break
    return {
        "db_path": db_path or str(get_db_path()),
        "schema_version": schema_version,
        "meals": meal_count,
        "days_tracked": days_tracked,
        "since": first_date,
        "water_entries": water_entries,
        "targets": target_count,
    }
