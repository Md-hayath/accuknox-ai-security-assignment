"""Read user rows from a CSV file and insert them into SQLite.

Assumptions
- The CSV is UTF-8 and has a header row.
- Required columns are name and email. Extra columns are ignored.
- A row is imported when name is non-empty and email contains one "@".
- email is unique. Running the script again does not create duplicate people.
- Values are bound as SQL parameters, so a cell cannot change the statement.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_CSV = ROOT / "data" / "users.csv"
DEFAULT_DB = ROOT / "output" / "users.db"


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="CSV file with name and email columns")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path")
    return parser.parse_args()


def read_users(csv_path: Path) -> tuple[list[tuple[str, str]], int]:
    if not csv_path.is_file():
        raise SystemExit(f"CSV not found: {csv_path}")

    accepted: list[tuple[str, str]] = []
    rejected = 0
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"name", "email"} <= {name.strip() for name in reader.fieldnames}:
            found = ", ".join(reader.fieldnames or [])
            raise SystemExit(f"CSV must include name and email columns. Found: {found or '(none)'}")
        for line_number, row in enumerate(reader, start=2):
            name = (row.get("name") or "").strip()
            email = (row.get("email") or "").strip().lower()
            if not name or email.count("@") != 1 or email.startswith("@") or email.endswith("@"):
                print(f"Skipping line {line_number}: invalid name or email", file=sys.stderr)
                rejected += 1
                continue
            accepted.append((name, email))
    return accepted, rejected


def store_users(db_path: Path, users: list[tuple[str, str]]) -> tuple[int, int, list[tuple[str, str]]]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )
        inserted = 0
        skipped = 0
        for name, email in users:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)",
                (name, email),
            )
            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1
        connection.commit()
        stored = connection.execute("SELECT name, email FROM users ORDER BY name").fetchall()
        return inserted, skipped, stored
    finally:
        connection.close()


def display(inserted: int, already_present: int, rejected: int, rows: list[tuple[str, str]], db_path: Path) -> None:
    print(f"Inserted: {inserted}")
    print(f"Already in database: {already_present}")
    print(f"Rejected from CSV: {rejected}")
    print(f"Database: {db_path}")
    print(f"{'Name':<24} Email")
    print("-" * 56)
    for name, email in rows:
        print(f"{name:<24} {email}")


def main() -> None:
    configure_stdout()
    args = parse_args()
    users, rejected = read_users(args.csv)
    inserted, already_present, stored = store_users(args.db, users)
    display(inserted, already_present, rejected, stored, args.db)


if __name__ == "__main__":
    main()
