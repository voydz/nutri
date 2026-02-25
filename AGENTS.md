# AGENTS.md

## Project

**nutri-cli** is a small local CLI tool for tracking nutrition (meals, macros, water) in a SQLite database.

## Development

- Runtime: Python >= 3.11
- CLI: Typer (Click-compatible) + Rich as a dependency
- DB: SQLite (stdlib)

### Setup

```bash
make setup
```

### Run Locally

```bash
uv run nutri --help
uv run nutri today
```

### Database Path

- Default: XDG Data Directory (app-specific)
- Override: `NUTRI_DB_PATH=/path/to/db.sqlite3`

### Conventions

- Keep CLI output in English.
- CLI behavior/flags remain 1:1 compatible with the original Click variant.
