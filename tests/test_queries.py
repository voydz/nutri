from __future__ import annotations

from pathlib import Path

from nutricli import db, queries


def test_day_and_status_summary_keys(tmp_path: Path) -> None:
    conn = db.get_connection(tmp_path / "nutrition.db")
    db.insert_meal(
        conn,
        date="2026-02-11",
        time="12:00",
        meal_type="lunch",
        description="Test",
        calories=600,
        protein_g=40,
        carbs_g=60,
        fat_g=15,
        fiber_g=5,
        sugar_g=4,
        sodium_mg=300,
        confidence="high",
        source="manual",
    )
    db.insert_target(conn, date_from="2026-02-11", calories=2200, protein_g=150)
    db.insert_water(conn, date="2026-02-11", time="10:00", amount_ml=250)

    day = queries.day_summary(conn, "2026-02-11")
    status = queries.status_summary(conn, "2026-02-11")
    conn.close()

    assert {"date", "meals", "totals", "target", "remaining", "water_ml", "water_entries"} <= set(
        day.keys()
    )
    assert {"date", "meals", "totals", "target", "remaining", "water_ml"} <= set(status.keys())
