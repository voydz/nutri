---
name: nutri-cli-usage
description: Operate the finished nutri CLI for logging meals, water, targets, status, queries, and export. Use when a user asks how to run nutri commands, interpret output, or find database paths and output formats.
---

# nutri CLI usage skill

## Purpose
Use this skill when helping users operate the finished `nutri` CLI. Focus on commands, options, output, and DB path. Do not cover development, testing, or release tasks.

## Scope
- Logging meals and water
- Targets, status, queries, exports
- Output formats
- Database location and overrides

## Key constraints
- Keep user-facing CLI output in German.
- Keep existing CLI flags and semantics intact.
- Default database path: `~/.local/share/nutri/nutrition.db`
- Output format: `table` or `json` (and `csv` for export)

## Quick start
```bash
nutri --help
nutri today
```

## Common usage patterns
```bash
# Log a meal
nutri log --meal lunch --desc "Bowl" --cal 650 --protein 45

# Edit / delete / confirm a meal
nutri edit 12 --cal 700 --protein 50
nutri delete 12
nutri confirm 12

# Show today
nutri today
nutri day 2026-01-15

# Status (coach)
nutri status

# Set / show targets
nutri target --cal 2200 --protein 160
nutri target --show

# Log / show water
nutri water 300
nutri water --today

# Query: last 7 days
nutri query --last 7d

# Info
nutri info --format json

# Export
nutri export --from 2026-01-01 --to 2026-01-31 --format csv -o jan.csv
nutri export --from 2026-01-01 --to 2026-01-31 --format json
```

## Commands and flags (current CLI)
- `log`: `--meal` `--desc` `--cal` `--protein` `--carbs` `--fat` `--fiber` `--sugar` `--sodium` `--confidence` `--source` `--time` `--date` `--format`
- `edit`: `meal_id` + any of `--desc` `--cal` `--protein` `--carbs` `--fat` `--fiber` `--sugar` `--sodium` `--meal` `--confidence` `--format`
- `delete`: `meal_id` `--format`
- `confirm`: `meal_id` `--format`
- `today`: `--format`
- `day`: `date` (YYYY-MM-DD) `--format`
- `query`: `--last` `--week` `--offset` `--from` `--to` `--avg` `--trend` `--below` `--format`
- `target`: `--cal` `--protein` `--carbs` `--fat` `--fiber` `--note` `--date` `--show` `--format`
- `water`: `amount` `--time` `--date` `--today` `--format`
- `status`: `--date` `--format`
- `info`: `--format`
- `export`: `--from` `--to` `--format` (`csv` or `json`) `-o/--output`

## Output format
- `table` (default): human-friendly text
- `json`: machine-readable records
- `export --format csv`: CSV file output

## Database location
- Default: `~/.local/share/nutri/nutrition.db`
- Override: set `NUTRI_DB_PATH=/path/to/nutri.db`
