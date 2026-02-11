# nutri-cli

Kleine CLI zum Tracken von Mahlzeiten, Makros, Zielen und Wasser in einer lokalen SQLite-Datenbank.

## Installation / Setup

```bash
cd ~/Code/tinkering/nutri
make setup
```

## Datenbank

Standard-Pfad:

- `~/.local/share/nutri/nutrition.db`

Override per Env-Var:

```bash
export NUTRI_DB_PATH=~/tmp/nutri.db
```

## Beispiele

```bash
# Hilfe
uv run nutri --help

# Mahlzeit loggen
uv run nutri log --meal lunch --desc "Bowl" --cal 650 --protein 45

# Heute anzeigen
uv run nutri today

# Status (coach)
uv run nutri status

# Ziele setzen / anzeigen
uv run nutri target --cal 2200 --protein 160
uv run nutri target --show

# Wasser loggen / anzeigen
uv run nutri water 300
uv run nutri water --today

# Query: letzte 7 Tage
uv run nutri query --last 7d

# Info
uv run nutri info --format json

# Export
uv run nutri export --from 2026-01-01 --to 2026-01-31 --format csv -o jan.csv
```

## Binary Build (PyInstaller)

```bash
make build
./dist/nutri --help
```

Release-Artefakt inkl. SHA256:

```bash
make package
```

## Homebrew (Tap)

Die Formel liegt im Tap-Repo unter `/opt/homebrew/Library/Taps/voydz/homebrew-tap/Formula/nutri.rb`.
Release-Prozess:

1) Version in `pyproject.toml` erhöhen
2) `make package`
3) tar.gz + `.sha256` hochladen
4) Formel-URL + SHA256 aktualisieren
