"""Typer CLI for nutrition tracking (Click-compatible interface)."""

from __future__ import annotations

import csv
import io
from enum import Enum
from typing import Annotated, Optional

import typer

from . import db, formatters, models, queries


app = typer.Typer(help="nutri — Nutrition Tracker CLI", add_completion=False)


class OutputFormat(str, Enum):
    table = "table"
    json = "json"


class ExportFormat(str, Enum):
    csv = "csv"
    json = "json"


class MealType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Source(str, Enum):
    vision_ai = "vision-ai"
    manual = "manual"
    barcode = "barcode"


def get_conn():
    return db.get_connection()


# ── log ──────────────────────────────────────────────────────────────────────


@app.command()
def log(
    meal: Annotated[MealType, typer.Option("--meal", case_sensitive=False)] = MealType.snack,
    desc: Annotated[str, typer.Option("--desc", help="Meal description")] = ..., 
    cal: Annotated[float, typer.Option("--cal", help="Calories")] = ..., 
    protein: Annotated[float, typer.Option("--protein")] = 0,
    carbs: Annotated[float, typer.Option("--carbs")] = 0,
    fat: Annotated[float, typer.Option("--fat")] = 0,
    fiber: Annotated[float, typer.Option("--fiber")] = 0,
    sugar: Annotated[float, typer.Option("--sugar")] = 0,
    sodium: Annotated[float, typer.Option("--sodium")] = 0,
    confidence: Annotated[Confidence, typer.Option("--confidence", case_sensitive=False)] = Confidence.medium,
    source: Annotated[Source, typer.Option("--source", case_sensitive=False)] = Source.manual,
    time_: Annotated[Optional[str], typer.Option("--time", help="HH:MM")] = None,
    date_: Annotated[Optional[str], typer.Option("--date", help="YYYY-MM-DD")] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Log a meal."""

    conn = get_conn()
    d = date_ or models.today_str()
    t = time_ or models.now_time_str()
    meal_id = db.insert_meal(
        conn,
        date=d,
        time=t,
        meal_type=meal.value,
        description=desc,
        calories=cal,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
        fiber_g=fiber,
        sugar_g=sugar,
        sodium_mg=sodium,
        confidence=confidence.value,
        source=source.value,
    )
    result = db.get_meal(conn, meal_id)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(result))
    else:
        typer.echo(f"  Mahlzeit #{meal_id} geloggt: {desc} ({cal:.0f} kcal)")


# ── edit ─────────────────────────────────────────────────────────────────────


@app.command()
def edit(
    meal_id: Annotated[int, typer.Argument()],
    desc: Annotated[Optional[str], typer.Option("--desc")] = None,
    cal: Annotated[Optional[float], typer.Option("--cal")] = None,
    protein: Annotated[Optional[float], typer.Option("--protein")] = None,
    carbs: Annotated[Optional[float], typer.Option("--carbs")] = None,
    fat: Annotated[Optional[float], typer.Option("--fat")] = None,
    fiber: Annotated[Optional[float], typer.Option("--fiber")] = None,
    sugar: Annotated[Optional[float], typer.Option("--sugar")] = None,
    sodium: Annotated[Optional[float], typer.Option("--sodium")] = None,
    meal: Annotated[Optional[MealType], typer.Option("--meal", case_sensitive=False)] = None,
    confidence: Annotated[Optional[Confidence], typer.Option("--confidence", case_sensitive=False)] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Edit an existing meal."""

    conn = get_conn()
    updates: dict[str, object] = {}
    if desc is not None:
        updates["description"] = desc
    if cal is not None:
        updates["calories"] = cal
    if protein is not None:
        updates["protein_g"] = protein
    if carbs is not None:
        updates["carbs_g"] = carbs
    if fat is not None:
        updates["fat_g"] = fat
    if fiber is not None:
        updates["fiber_g"] = fiber
    if sugar is not None:
        updates["sugar_g"] = sugar
    if sodium is not None:
        updates["sodium_mg"] = sodium
    if meal is not None:
        updates["meal_type"] = meal.value
    if confidence is not None:
        updates["confidence"] = confidence.value

    if not updates:
        typer.echo("  Keine Änderungen angegeben.", err=True)
        conn.close()
        raise typer.Exit(1)

    ok = db.update_meal(conn, meal_id, **updates)
    if not ok:
        typer.echo(f"  Mahlzeit #{meal_id} nicht gefunden.", err=True)
        conn.close()
        raise typer.Exit(1)

    result = db.get_meal(conn, meal_id)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(result))
    else:
        typer.echo(f"  Mahlzeit #{meal_id} aktualisiert.")


# ── delete ───────────────────────────────────────────────────────────────────


@app.command()
def delete(
    meal_id: Annotated[int, typer.Argument()],
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Delete a meal."""

    conn = get_conn()
    meal = db.get_meal(conn, meal_id)
    ok = db.delete_meal(conn, meal_id)
    conn.close()

    if not ok:
        typer.echo(f"  Mahlzeit #{meal_id} nicht gefunden.", err=True)
        raise typer.Exit(1)

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json({"deleted": meal_id, "meal": meal}))
    else:
        typer.echo(f"  Mahlzeit #{meal_id} gelöscht.")


# ── confirm ──────────────────────────────────────────────────────────────────


@app.command()
def confirm(
    meal_id: Annotated[int, typer.Argument()],
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Confirm a meal (mark as user-verified)."""

    conn = get_conn()
    ok = db.confirm_meal(conn, meal_id)
    conn.close()

    if not ok:
        typer.echo(f"  Mahlzeit #{meal_id} nicht gefunden.", err=True)
        raise typer.Exit(1)

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json({"confirmed": meal_id}))
    else:
        typer.echo(f"  Mahlzeit #{meal_id} bestätigt.")


# ── today ────────────────────────────────────────────────────────────────────


@app.command()
def today(
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Show today's meals and totals."""

    conn = get_conn()
    summary = queries.day_summary(conn, models.today_str())
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(summary))
    else:
        typer.echo(formatters.format_day_table(summary))


# ── day ──────────────────────────────────────────────────────────────────────


@app.command()
def day(
    date: Annotated[str, typer.Argument(help="YYYY-MM-DD")],
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Show meals and totals for a specific date (YYYY-MM-DD)."""

    conn = get_conn()
    summary = queries.day_summary(conn, date)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(summary))
    else:
        typer.echo(formatters.format_day_table(summary))


# ── query ────────────────────────────────────────────────────────────────────


@app.command()
def query(
    last_spec: Annotated[Optional[str], typer.Option("--last", help="Duration, e.g. 7d, 30d")] = None,
    week: Annotated[bool, typer.Option("--week", help="Current week")] = False,
    offset: Annotated[int, typer.Option("--offset", help="Week offset (e.g. -1 for last week)")] = 0,
    from_: Annotated[Optional[str], typer.Option("--from", help="Start date YYYY-MM-DD")] = None,
    to_: Annotated[Optional[str], typer.Option("--to", help="End date YYYY-MM-DD")] = None,
    avg: Annotated[bool, typer.Option("--avg", help="Show daily averages")] = False,
    trend: Annotated[Optional[str], typer.Option("--trend", help="Show trend for field (e.g. calories)")] = None,
    below: Annotated[Optional[str], typer.Option("--below", help="Show days below target for field (e.g. protein_g)")] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Query meal data over a date range."""

    if last_spec:
        try:
            date_from, date_to = models.parse_duration(last_spec)
        except ValueError as e:
            typer.echo(f"  {e}", err=True)
            raise typer.Exit(1)
    elif week:
        date_from, date_to = models.get_week_range(offset)
    elif from_:
        date_from = from_
        date_to = to_ or models.today_str()
    else:
        typer.echo("  Bitte --last, --week, oder --from angeben.", err=True)
        raise typer.Exit(1)

    conn = get_conn()
    result = queries.range_summary(conn, date_from, date_to, avg=avg, trend_field=trend, below_field=below)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(result))
    else:
        typer.echo(formatters.format_range_table(result))


# ── target ───────────────────────────────────────────────────────────────────


@app.command()
def target(
    cal: Annotated[Optional[float], typer.Option("--cal", help="Calorie target")] = None,
    protein: Annotated[Optional[float], typer.Option("--protein")] = None,
    carbs: Annotated[Optional[float], typer.Option("--carbs")] = None,
    fat: Annotated[Optional[float], typer.Option("--fat")] = None,
    fiber: Annotated[Optional[float], typer.Option("--fiber")] = None,
    note: Annotated[Optional[str], typer.Option("--note", help="Note (e.g. Training day)")] = None,
    date_: Annotated[Optional[str], typer.Option("--date", help="Effective date (default: today)")] = None,
    show: Annotated[bool, typer.Option("--show", help="Show current targets")] = False,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Set or show nutrition targets."""

    conn = get_conn()

    if show:
        targets = db.get_all_targets(conn)
        conn.close()
        if fmt == OutputFormat.json:
            typer.echo(formatters.output_json(targets))
        else:
            typer.echo(formatters.format_targets_table(targets))
        return

    if cal is None:
        typer.echo("  Bitte mindestens --cal angeben.", err=True)
        conn.close()
        raise typer.Exit(1)

    d = date_ or models.today_str()
    target_id = db.insert_target(
        conn,
        date_from=d,
        calories=cal,
        protein_g=protein,
        carbs_g=carbs,
        fat_g=fat,
        fiber_g=fiber,
        note=note,
    )
    conn.close()

    result = {
        "id": target_id,
        "date_from": d,
        "calories": cal,
        "protein_g": protein,
        "carbs_g": carbs,
        "fat_g": fat,
    }
    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(result))
    else:
        typer.echo(f"  Ziel gesetzt ab {d}: {cal:.0f} kcal")


# ── water ────────────────────────────────────────────────────────────────────


@app.command()
def water(
    amount: Annotated[Optional[float], typer.Argument()] = None,
    time_: Annotated[Optional[str], typer.Option("--time", help="HH:MM")] = None,
    date_: Annotated[Optional[str], typer.Option("--date", help="YYYY-MM-DD")] = None,
    show_today: Annotated[bool, typer.Option("--today", help="Show today's water intake")] = False,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Log or show water intake (in ml)."""

    conn = get_conn()
    d = date_ or models.today_str()

    if show_today or amount is None:
        entries = db.get_water_by_date(conn, d)
        total = sum(w["amount_ml"] for w in entries)
        conn.close()

        data = {"date": d, "entries": entries, "total_ml": total}
        if fmt == OutputFormat.json:
            typer.echo(formatters.output_json(data))
        else:
            if entries:
                typer.echo(formatters.format_water_table(entries, total))
            else:
                typer.echo(f"  Kein Wasser für {d} geloggt.")
        return

    t = time_ or models.now_time_str()
    water_id = db.insert_water(conn, date=d, time=t, amount_ml=amount)
    entries = db.get_water_by_date(conn, d)
    total = sum(w["amount_ml"] for w in entries)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json({"id": water_id, "amount_ml": amount, "total_ml": total}))
    else:
        typer.echo(f"  {amount:.0f} ml geloggt. Heute: {total / 1000:.1f}L")


# ── status ───────────────────────────────────────────────────────────────────


@app.command()
def status(
    date_: Annotated[Optional[str], typer.Option("--date", help="YYYY-MM-DD")] = None,
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Quick status summary (for coach)."""

    conn = get_conn()
    d = date_ or models.today_str()
    result = queries.status_summary(conn, d)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(result))
    else:
        typer.echo(formatters.format_status_table(result))


# ── info ─────────────────────────────────────────────────────────────────────


@app.command()
def info(
    fmt: Annotated[OutputFormat, typer.Option("--format", case_sensitive=False)] = OutputFormat.table,
):
    """Show database info and stats."""

    conn = get_conn()
    stats = db.get_db_stats(conn)
    conn.close()

    if fmt == OutputFormat.json:
        typer.echo(formatters.output_json(stats))
    else:
        typer.echo(formatters.format_info_table(stats))


# ── export ───────────────────────────────────────────────────────────────────


@app.command()
def export(
    from_: Annotated[str, typer.Option("--from", help="Start date YYYY-MM-DD")] = ...,
    to_: Annotated[Optional[str], typer.Option("--to", help="End date YYYY-MM-DD")] = None,
    fmt: Annotated[ExportFormat, typer.Option("--format", case_sensitive=False)] = ExportFormat.csv,
    outfile: Annotated[Optional[str], typer.Option("-o", "--output", help="Output file path")] = None,
):
    """Export meal data."""

    conn = get_conn()
    date_to = to_ or models.today_str()
    meals = db.get_meals_in_range(conn, from_, date_to)
    conn.close()

    if fmt == ExportFormat.json:
        content = formatters.output_json(meals)
    else:
        buf = io.StringIO()
        if meals:
            writer = csv.DictWriter(buf, fieldnames=meals[0].keys())
            writer.writeheader()
            writer.writerows(meals)
        content = buf.getvalue()

    if outfile:
        with open(outfile, "w") as f:
            f.write(content)
        typer.echo(f"  Exportiert: {len(meals)} Mahlzeiten → {outfile}")
    else:
        typer.echo(content)
