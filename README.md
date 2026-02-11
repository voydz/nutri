# nutri-cli

Kleines CLI-Tool zum Tracken von Mahlzeiten, Makros, Zielen und Wasser mit SQLite-Backend.

## Ueberblick

- Fokus auf schnelle, lokale Eingaben (kein Cloud-Account, keine Web-UI)
- SQLite als simple, robuste Datenbasis
- Export für Auswertungen (z.B. CSV/JSON)
- Kompatibel zur ursprünglichen Click-Variante

## Installation / Setup

Voraussetzungen: Python 3.11+ und `uv`.

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

## Datenbank

Standard-Pfad:

- XDG Data Directory (app-spezifisch)

Override per Env-Var:

```bash
export NUTRI_DB_PATH=/path/to/nutri.db
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

## Befehle (Auszug)

- `nutri log` Mahlzeit erfassen
- `nutri today` Tagesübersicht
- `nutri status` Status im "Coach"-Stil
- `nutri target` Ziele setzen/anzeigen
- `nutri water` Wasser loggen/anzeigen
- `nutri query` Datenabfrage (z.B. Zeitraum)
- `nutri export` Export (CSV/JSON)

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

Die Formel liegt im Tap-Repo unter `TAPS_DIR/homebrew-tap/Formula/nutri.rb`.
Release-Prozess:

1) Version in `pyproject.toml` erhöhen
2) `make package`
3) tar.gz + `.sha256` hochladen
4) Formel-URL + SHA256 aktualisieren
