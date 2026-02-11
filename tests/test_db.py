from __future__ import annotations

from pathlib import Path

from nutricli import db


def test_schema_created_and_versioned(tmp_path: Path) -> None:
    path = tmp_path / "nutrition.db"
    conn = db.get_connection(path)
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }
    assert {"meals", "targets", "water"}.issubset(tables)
    schema_version = conn.execute("PRAGMA user_version").fetchone()[0]
    assert schema_version == db.SCHEMA_VERSION
    conn.close()


def test_insert_meal_target_water(tmp_path: Path) -> None:
    conn = db.get_connection(tmp_path / "nutrition.db")
    meal_id = db.insert_meal(
        conn,
        date="2026-02-11",
        time="08:00",
        meal_type="breakfast",
        description="Test Meal",
        calories=500,
        protein_g=20,
        carbs_g=50,
        fat_g=10,
        fiber_g=5,
        sugar_g=3,
        sodium_mg=200,
        confidence="medium",
        source="manual",
    )
    target_id = db.insert_target(
        conn,
        date_from="2026-02-11",
        calories=2200,
        protein_g=150,
        carbs_g=250,
        fat_g=70,
        fiber_g=25,
        note="Test",
    )
    water_id = db.insert_water(conn, date="2026-02-11", time="09:00", amount_ml=300)

    meal = db.get_meal(conn, meal_id)
    target = db.get_target_for_date(conn, "2026-02-11")
    water = db.get_water_by_date(conn, "2026-02-11")

    assert meal is not None
    assert meal["description"] == "Test Meal"
    assert target is not None
    assert target["id"] == target_id
    assert water and water[0]["id"] == water_id
    conn.close()
