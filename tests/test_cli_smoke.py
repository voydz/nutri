from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "nutricli", *args]
    return subprocess.run(cmd, env=env, text=True, capture_output=True, check=False)


def test_cli_smoke(tmp_path: Path) -> None:
    db_path = tmp_path / "nutrition.db"
    home = tmp_path / "home"
    home.mkdir()

    env = os.environ.copy()
    project_root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = str(project_root / "src")
    env["NUTRI_DB_PATH"] = str(db_path)
    env["HOME"] = str(home)

    result = _run_cli(["info", "--format", "json"], env)
    assert result.returncode == 0, result.stderr
    info = json.loads(result.stdout)
    assert "schema_version" in info

    result = _run_cli(["target", "--cal", "2200", "--protein", "150", "--format", "json"], env)
    assert result.returncode == 0, result.stderr
    target = json.loads(result.stdout)
    assert target["calories"] == 2200

    result = _run_cli(
        ["log", "--meal", "lunch", "--desc", "Test", "--cal", "600", "--protein", "40", "--format", "json"],
        env,
    )
    assert result.returncode == 0, result.stderr
    log_entry = json.loads(result.stdout)
    assert log_entry["description"] == "Test"

    result = _run_cli(["status", "--format", "json"], env)
    assert result.returncode == 0, result.stderr
    status = json.loads(result.stdout)
    assert status["target"] is not None

    result = _run_cli(["day", "today"], env)
    assert result.returncode == 1
    assert "Invalid date: today. Use format YYYY-MM-DD." in result.stderr
