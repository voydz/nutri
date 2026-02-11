# AGENTS.md

## Projekt

**nutri-cli** ist ein kleines, lokales CLI-Tool zum Tracken von Ernährung (Mahlzeiten, Makros, Wasser) in einer SQLite-Datenbank.

## Entwicklung

- Runtime: Python >= 3.11
- CLI: Typer (Click-kompatibel) + Rich als Dependency
- DB: SQLite (stdlib)

### Setup

```bash
make setup
```

### Lokales Ausführen

```bash
uv run nutri --help
uv run nutri today
```

### Datenbank-Pfad

- Standard: XDG Data Directory (app-spezifisch)
- Override: `NUTRI_DB_PATH=/path/to/db.sqlite3`

### Konventionen

- Deutsche Ausgaben beibehalten
- Verhalten/Flags der CLI sind 1:1 kompatibel zur ursprünglichen Click-Variante
