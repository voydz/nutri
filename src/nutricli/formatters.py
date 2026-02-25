"""Output formatters for table and JSON display."""

from __future__ import annotations

import json


MEAL_TYPE_ORDER = {"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}


def output_json(data: dict | list) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)


def format_meal_row(m: dict) -> str:
    mt = m.get("meal_type", "snack").capitalize()
    desc = m.get("description", "")[:30]
    cal = m.get("calories", 0)
    p = m.get("protein_g", 0)
    c = m.get("carbs_g", 0)
    f = m.get("fat_g", 0)
    conf = ""
    if not m.get("confirmed") and m.get("confidence") != "high":
        conf = f" [{m.get('confidence', '?')}]"
    return f"  {mt:<12}│ {desc:<32}│ {cal:>6.0f} kcal │ P: {p:>5.1f}g │ C: {c:>5.1f}g │ F: {f:>5.1f}g{conf}"


def format_day_table(summary: dict) -> str:
    lines: list[str] = []
    meals = sorted(
        summary["meals"],
        key=lambda m: MEAL_TYPE_ORDER.get(m.get("meal_type", "snack"), 3),
    )

    if not meals:
        lines.append(f"  No meals for {summary['date']}.")
        return "\n".join(lines)

    for m in meals:
        lines.append(format_meal_row(m))

    lines.append("  " + "─" * 84)

    t = summary["totals"]
    lines.append(
        f"  {'Total':<12}│ {'':<32}│ {t['calories']:>6.0f} kcal │ P: {t['protein_g']:>5.1f}g │ C: {t['carbs_g']:>5.1f}g │ F: {t['fat_g']:>5.1f}g"
    )

    target = summary.get("target")
    if target:
        lines.append(
            f"  {'Target':<12}│ {'':<32}│ {target.get('calories', 0):>6.0f} kcal │ P: {target.get('protein_g', 0) or 0:>5.1f}g │ C: {target.get('carbs_g', 0) or 0:>5.1f}g │ F: {target.get('fat_g', 0) or 0:>5.1f}g"
        )
        rem = summary.get("remaining")
        if rem:
            lines.append(
                f"  {'Remaining':<12}│ {'':<32}│ {rem['calories'] or 0:>6.0f} kcal │ P: {rem['protein_g'] or 0:>5.1f}g │ C: {rem['carbs_g'] or 0:>5.1f}g │ F: {rem['fat_g'] or 0:>5.1f}g"
            )

    if summary.get("water_ml", 0) > 0:
        lines.append(f"\n  Water: {summary['water_ml'] / 1000:.1f}L")

    return "\n".join(lines)


def format_range_table(result: dict) -> str:
    lines: list[str] = []
    lines.append(
        f"  Range: {result['date_from']} to {result['date_to']} ({result['days']} days, {result['total_meals']} meals)"
    )
    lines.append("")

    if "averages" in result:
        a = result["averages"]
        lines.append(
            f"  Average: {a['calories']:.0f} kcal │ P: {a['protein_g']:.1f}g │ C: {a['carbs_g']:.1f}g │ F: {a['fat_g']:.1f}g"
        )

    if "trend" in result:
        tr = result["trend"]
        lines.append(
            f"  Trend: {tr['direction']} {tr['change_per_week']:+.0f} kcal/week ({tr['start']:.0f} -> {tr['end']:.0f})"
        )

    if "below_target_days" in result:
        below = result["below_target_days"]
        if below:
            lines.append(f"\n  Days below target ({len(below)}):")
            for day in below:
                lines.append(
                    f"    {day['date']}: {day['actual']:.0f} / {day['target']:.0f} (missing: {day['deficit']:.0f})"
                )
        else:
            lines.append("  All days are within target!")

    if (
        "daily" in result
        and "averages" not in result
        and "trend" not in result
        and "below_target_days" not in result
    ):
        for d, info in sorted(result["daily"].items()):
            t = info["totals"]
            lines.append(
                f"  {d} │ {info['meals']} meals │ {t['calories']:>6.0f} kcal │ P: {t['protein_g']:>5.1f}g │ C: {t['carbs_g']:>5.1f}g │ F: {t['fat_g']:>5.1f}g"
            )

    return "\n".join(lines)


def format_targets_table(targets: list[dict]) -> str:
    if not targets:
        return "  No targets set."
    lines: list[str] = []
    for t in targets:
        note = f" ({t['note']})" if t.get("note") else ""
        lines.append(
            f"  From {t['date_from']}{note}: {t['calories']:.0f} kcal │ P: {t.get('protein_g') or 0:.0f}g │ C: {t.get('carbs_g') or 0:.0f}g │ F: {t.get('fat_g') or 0:.0f}g"
        )
    return "\n".join(lines)


def format_water_table(
    entries: list[dict], total_ml: float, target: dict | None = None
) -> str:
    lines: list[str] = []
    for w in entries:
        time_str = w.get("time", "?")
        lines.append(f"  {time_str}  {w['amount_ml']:.0f} ml")
    lines.append("  " + "─" * 30)
    total_l = total_ml / 1000
    lines.append(f"  Total: {total_l:.1f}L")
    return "\n".join(lines)


def format_status_table(status: dict) -> str:
    lines: list[str] = []
    t = status["totals"]
    lines.append(f"  {status['date']}: {status['meals']} meals")
    lines.append(
        f"  {t['calories']:.0f} kcal │ P: {t['protein_g']:.1f}g │ C: {t['carbs_g']:.1f}g │ F: {t['fat_g']:.1f}g"
    )
    if status.get("target"):
        tgt = status["target"]
        lines.append(
            f"  Target: {tgt.get('calories', 0):.0f} kcal │ P: {tgt.get('protein_g', 0) or 0:.0f}g │ C: {tgt.get('carbs_g', 0) or 0:.0f}g │ F: {tgt.get('fat_g', 0) or 0:.0f}g"
        )
    if status.get("remaining"):
        r = status["remaining"]
        lines.append(
            f"  Remaining: {r['calories'] or 0:.0f} kcal │ P: {r['protein_g'] or 0:.0f}g │ C: {r['carbs_g'] or 0:.0f}g │ F: {r['fat_g'] or 0:.0f}g"
        )
    if status.get("water_ml", 0) > 0:
        lines.append(f"  Water: {status['water_ml'] / 1000:.1f}L")
    return "\n".join(lines)


def format_info_table(stats: dict) -> str:
    lines = [
        f"  DB: {stats['db_path']}",
        f"  Schema version: {stats.get('schema_version', 'n/a')}",
        f"  {stats['meals']} meals │ {stats['days_tracked']} days │ Since: {stats['since'] or 'n/a'}",
        f"  {stats['water_entries']} water entries │ {stats['targets']} targets",
    ]
    return "\n".join(lines)
