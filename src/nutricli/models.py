"""Data models and helpers for nutrition tracking."""

from __future__ import annotations

from datetime import date, datetime, timedelta
import re


MEAL_TYPES = ("breakfast", "lunch", "dinner", "snack")
CONFIDENCE_LEVELS = ("low", "medium", "high")
SOURCES = ("vision-ai", "manual", "barcode")
MACRO_FIELDS = (
    "calories",
    "protein_g",
    "carbs_g",
    "fat_g",
    "fiber_g",
    "sugar_g",
    "sodium_mg",
)


def today_str() -> str:
    return date.today().isoformat()


def now_time_str() -> str:
    return datetime.now().strftime("%H:%M")


def parse_iso_date(value: str) -> str:
    """Validate YYYY-MM-DD and return canonical ISO date string."""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as e:
        raise ValueError(f"Invalid date: {value}. Use format YYYY-MM-DD.") from e


def parse_duration(spec: str) -> tuple[str, str]:
    """Parse a duration spec like '7d', '30d' into (date_from, date_to) strings."""
    m = re.match(r"^(\d+)d$", spec)
    if not m:
        raise ValueError(f"Invalid duration: {spec}. Use format like '7d'.")
    days = int(m.group(1))
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def get_week_range(offset: int = 0) -> tuple[str, str]:
    """Get ISO week date range. offset=0 is current week, -1 is last week."""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week += timedelta(weeks=offset)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.isoformat(), end_of_week.isoformat()


def compute_totals(meals: list[dict]) -> dict:
    """Sum up macro fields from a list of meals."""
    totals = {f: 0.0 for f in MACRO_FIELDS}
    for m in meals:
        for f in MACRO_FIELDS:
            totals[f] += m.get(f, 0) or 0
    return totals


def compute_remaining(totals: dict, target: dict | None) -> dict | None:
    """Compute remaining macros given totals and a target."""
    if not target:
        return None
    remaining: dict[str, float | None] = {}
    for f in MACRO_FIELDS:
        t_val = target.get(f)
        if t_val is not None:
            remaining[f] = t_val - totals.get(f, 0)
        else:
            remaining[f] = None
    return remaining


def compute_daily_averages(meals_by_date: dict[str, list[dict]]) -> dict:
    """Compute daily averages across multiple days."""
    if not meals_by_date:
        return {f: 0.0 for f in MACRO_FIELDS}
    day_totals = [compute_totals(meals) for meals in meals_by_date.values()]
    n = len(day_totals)
    avg: dict[str, float] = {}
    for f in MACRO_FIELDS:
        avg[f] = round(sum(d[f] for d in day_totals) / n, 1)
    return avg


def group_meals_by_date(meals: list[dict]) -> dict[str, list[dict]]:
    """Group a flat list of meals by their date field."""
    grouped: dict[str, list[dict]] = {}
    for m in meals:
        d = m["date"]
        grouped.setdefault(d, []).append(m)
    return grouped


def compute_trend(meals_by_date: dict[str, list[dict]], field: str) -> dict:
    """Compute a simple linear trend for a field across days."""
    if len(meals_by_date) < 2:
        return {"direction": "→", "change_per_week": 0, "start": 0, "end": 0}

    dates_sorted = sorted(meals_by_date.keys())
    daily_vals = []
    for d in dates_sorted:
        totals = compute_totals(meals_by_date[d])
        daily_vals.append(totals.get(field, 0))

    n = len(daily_vals)
    # Simple linear regression
    x_mean = (n - 1) / 2
    y_mean = sum(daily_vals) / n
    num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(daily_vals))
    den = sum((i - x_mean) ** 2 for i in range(n))
    slope = num / den if den != 0 else 0

    change_per_week = round(slope * 7, 1)
    direction = "↗" if change_per_week > 5 else ("↘" if change_per_week < -5 else "→")

    return {
        "direction": direction,
        "change_per_week": change_per_week,
        "start": round(daily_vals[0], 0),
        "end": round(daily_vals[-1], 0),
    }
