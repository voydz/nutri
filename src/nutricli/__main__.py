from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    # Allow running __main__.py directly (or via PyInstaller) without a package context.
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from nutricli.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
