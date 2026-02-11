# nutri-cli agent workflow

## Purpose
Use this skill when working on the nutri-cli project. It covers setup, local usage, database handling, testing, build/release, and coding conventions that agents must follow.

## Scope
- CLI usage and examples
- Local development workflow
- Database path and env override
- Tests, build, and release steps
- Code and output conventions

## Key constraints
- Keep user-facing CLI output in German.
- CLI behavior and flags must remain compatible with the original Click version.
- Runtime: Python >= 3.11
- CLI stack: Typer (Click-compatible) + Rich
- DB: SQLite (stdlib)

## Quick start
```bash
make setup
uv run nutri --help
uv run nutri today
```

## Common usage patterns
```bash
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

## Database location
- Default: XDG Data Directory (app-specific)
- Override: set `NUTRI_DB_PATH=/path/to/nutri.db`

## Development workflow
1) Read `AGENTS.md` and `README.md` for project rules and usage.
2) Use `rg` to find relevant code and tests.
3) Keep CLI output strings in German and preserve existing flags.
4) Add or update tests when changing behavior.
5) Run tests if requested or if behavior changed.

## Testing
- Use the project test command if needed:
```bash
make test
```

## Build and packaging
```bash
make build
./dist/nutri --help

make package
```

## Homebrew release notes
- Formula path: `TAPS_DIR/homebrew-tap/Formula/nutri.rb`
- Release steps:
  1) Bump version in `pyproject.toml`
  2) Run `make package`
  3) Upload tar.gz + `.sha256`
  4) Update formula URL + SHA256

## Files to know
- `README.md`: user-facing usage and examples
- `AGENTS.md`: repo rules for agents
- `src/`: CLI implementation
- `tests/`: automated tests
- `pyproject.toml`: version and dependencies
