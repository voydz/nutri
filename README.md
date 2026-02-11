# nutri-cli

Small CLI tool for tracking meals, macros, targets, and water with a SQLite backend.

## Overview

- Focus on fast, local input (no cloud account, no web UI)
- SQLite as a simple, robust data store
- Export for analysis (e.g. CSV/JSON)
- Compatible with the original Click version

## Installation / Setup

Requirements: Python 3.11+ and `uv`.

```bash
cd /path/to/nutri
make setup
```

## Quickstart

```bash
uv run nutri today
uv run nutri log --meal lunch --desc "Bowl" --cal 650 --protein 45
uv run nutri water 300
```

## Database

Default path:

- XDG Data Directory (app-specific)

Override via env var:

```bash
export NUTRI_DB_PATH=/path/to/nutri.db
```

## Examples

```bash
# Help
uv run nutri --help

# Log a meal
uv run nutri log --meal lunch --desc "Bowl" --cal 650 --protein 45

# Show today
uv run nutri today

# Status (coach)
uv run nutri status

# Set / show targets
uv run nutri target --cal 2200 --protein 160
uv run nutri target --show

# Log / show water
uv run nutri water 300
uv run nutri water --today

# Query: last 7 days
uv run nutri query --last 7d

# Info
uv run nutri info --format json

# Export
uv run nutri export --from 2026-01-01 --to 2026-01-31 --format csv -o jan.csv
```

## Commands (excerpt)

- `nutri log` log a meal
- `nutri today` daily overview
- `nutri status` status in "coach" style
- `nutri target` set/show targets
- `nutri water` log/show water
- `nutri query` data query (e.g. date range)
- `nutri export` export (CSV/JSON)

## Binary Build (PyInstaller)

```bash
make build
./dist/nutri --help
```

Release artifact incl. SHA256:

```bash
make package
```

## Homebrew (Tap)

The formula lives in the tap repo at `TAPS_DIR/homebrew-tap/Formula/nutri.rb`.
Release process:

1) Bump version in `pyproject.toml`
2) `make package`
3) Upload tar.gz + `.sha256`
4) Update formula URL + SHA256
