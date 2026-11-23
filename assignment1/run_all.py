"""Run the three assignment 1 scripts in order. Stop on the first failure."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = (
    "books_to_sqlite.py",
    "scores_to_chart.py",
    "csv_to_sqlite.py",
)


def main() -> None:
    here = Path(__file__).resolve().parent
    for name in SCRIPTS:
        print(f"\n=== {name} ===", flush=True)
        completed = subprocess.run([sys.executable, str(here / name)], cwd=ROOT)
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)
    print("\nAll three scripts finished.", flush=True)


if __name__ == "__main__":
    main()
