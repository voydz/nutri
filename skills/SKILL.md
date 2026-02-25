---
name: nutri-cli-usage
description: Agent guide for operating `nutri` via CLI: log/edit meals, water, targets, summaries, queries, and exports with reliable JSON-first output.
---

# nutri CLI agent

## Rules
- Prefer `nutri ...`.
- Prefer `--format json` where available.
- Do not invent fields; report only CLI-returned data.
- On failure: show error + corrected command.

## DB path
- Default: XDG data dir (app-specific).
- Override:
```bash
NUTRI_DB_PATH=/path/to/db.sqlite3 nutri <command>
```

## Workflow
1. Pick the smallest command that matches intent.
2. Run with JSON output when possible.
3. Return action, IDs, dates, totals, and units.

## Global usage
- Base: `nutri <command> [flags]`
- Help: `nutri --help`
- Command help: `nutri <command> --help`

## Core commands
```bash
nutri log --meal lunch --desc "Bowl" --cal 650 --protein 45 --format json
nutri edit 12 --cal 700 --format json
nutri confirm 12 --format json
nutri delete 12 --format json
nutri today --format json
nutri day 2026-01-15 --format json
nutri query --last 7d --format json
nutri query --from 2026-01-01 --to 2026-01-31 --avg --format json
nutri target --cal 2200 --protein 160 --format json
nutri target --show --format json
nutri water 300 --format json
nutri water --today --format json
nutri status --format json
nutri info --format json
nutri export --from 2026-01-01 --to 2026-01-31 --format csv -o jan.csv
nutri export --from 2026-01-01 --to 2026-01-31 --format json
```

## Exhaustive command and flag map
- `log`
  - Positional: none
  - Flags: `--meal` `--desc` `--cal` `--protein` `--carbs` `--fat` `--fiber` `--sugar` `--sodium` `--confidence` `--source` `--time` `--date` `--format`
- `edit`
  - Positional: `meal_id`
  - Flags: `--desc` `--cal` `--protein` `--carbs` `--fat` `--fiber` `--sugar` `--sodium` `--meal` `--confidence` `--format`
- `delete`
  - Positional: `meal_id`
  - Flags: `--format`
- `confirm`
  - Positional: `meal_id`
  - Flags: `--format`
- `today`
  - Positional: none
  - Flags: `--format`
- `day`
  - Positional: `date` (`YYYY-MM-DD`)
  - Flags: `--format`
- `query`
  - Positional: none
  - Flags: `--last` `--week` `--offset` `--from` `--to` `--avg` `--trend` `--below` `--format`
- `target`
  - Positional: none
  - Flags: `--cal` `--protein` `--carbs` `--fat` `--fiber` `--note` `--date` `--show` `--format`
- `water`
  - Positional: `amount` (optional)
  - Flags: `--time` `--date` `--today` `--format`
- `status`
  - Positional: none
  - Flags: `--date` `--format`
- `info`
  - Positional: none
  - Flags: `--format`
- `export`
  - Positional: none
  - Flags: `--from` `--to` `--format` `-o` `--output`

## Input constraints
- Dates must be `YYYY-MM-DD`.
- `query` requires one of: `--last`, `--week`, or `--from`.
- `target` set mode requires at least `--cal` unless `--show` is used.
- `edit` requires at least one field to update.
- Allowed values:
  - `--meal`: `breakfast|lunch|dinner|snack`
  - `--confidence`: `low|medium|high`
  - `--source`: `vision-ai|manual|barcode`
  - `--format` (most commands): `table|json`
  - `export --format`: `csv|json`
