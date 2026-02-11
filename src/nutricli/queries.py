"""Query helpers that combine db and model operations."""

from __future__ import annotations

import sqlite3

from .db import get_meals_by_date, get_meals_in_range, get_target_for_date, get_water_by_date
from .models import (
    compute_totals,
    compute_remaining,
    compute_daily_averages,
    group_meals_by_date,
    compute_trend,
    MACRO_FIELDS,
)


def day_summary(conn: sqlite3.Connection, date: str) -> dict:
    """Full summary for a single day: meals, totals, target, remaining, water."""
    meals = get_meals_by_date(conn, date)
    totals = compute_totals(meals)
    target = get_target_for_date(conn, date)
    remaining = compute_remaining(totals, target)
    water = get_water_by_date(conn, date)
    water_total = sum(w["amount_ml"] for w in water)

    return {
        "date": date,
        "meals": meals,
        "totals": totals,
        "target": target,
        "remaining": remaining,
        "water_ml": water_total,
        "water_entries": water,
    }


def range_summary(
    conn: sqlite3.Connection,
    date_from: str,
    date_to: str,
    avg: bool = False,
    trend_field: str | None = None,
    below_field: str | None = None,
) -> dict:
    """Summary over a date range with optional aggregations."""
    meals = get_meals_in_range(conn, date_from, date_to)
    by_date = group_meals_by_date(meals)

    result: dict = {
        "date_from": date_from,
        "date_to": date_to,
        "days": len(by_date),
        "total_meals": len(meals),
    }

    if avg:
        result["averages"] = compute_daily_averages(by_date)

    if trend_field:
        result["trend"] = compute_trend(by_date, trend_field)

    if below_field:
        result["below_target_days"] = _days_below_target(conn, by_date, below_field)

    # Per-day breakdown
    result["daily"] = {}
    for d in sorted(by_date.keys()):
        day_meals = by_date[d]
        result["daily"][d] = {
            "meals": len(day_meals),
            "totals": compute_totals(day_meals),
        }

    return result


def _days_below_target(conn: sqlite3.Connection, by_date: dict[str, list[dict]], field: str) -> list[dict]:
    """Find days where a macro field was below target."""
    below = []
    for d in sorted(by_date.keys()):
        target = get_target_for_date(conn, d)
        if not target or target.get(field) is None:
            continue
        totals = compute_totals(by_date[d])
        if totals.get(field, 0) < target[field]:
            below.append(
                {
                    "date": d,
                    "actual": round(totals[field], 1),
                    "target": target[field],
                    "deficit": round(target[field] - totals[field], 1),
                }
            )
    return below


def status_summary(conn: sqlite3.Connection, date: str) -> dict:
    """Quick status for coach integration."""
    meals = get_meals_by_date(conn, date)
    totals = compute_totals(meals)
    target = get_target_for_date(conn, date)
    remaining = compute_remaining(totals, target)
    water = get_water_by_date(conn, date)
    water_total = sum(w["amount_ml"] for w in water)

    return {
        "date": date,
        "meals": len(meals),
        "totals": totals,
        "target": {k: v for k, v in target.items() if k in MACRO_FIELDS} if target else None,
        "remaining": remaining,
        "water_ml": water_total,
    }
