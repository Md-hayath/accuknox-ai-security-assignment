"""Fetch books from the Open Library Search API and store them in SQLite.

Assumptions
- The brief does not name a books API. This uses the public Open Library
  search endpoint: https://openlibrary.org/search.json
- Attributes used: title, author_name, first_publish_year.
- author_name is a list. Duplicate names are dropped, then joined with commas.
  Missing authors are stored as "Unknown". Missing years are stored as NULL.
- A row with no title is skipped.
- Each run replaces the books table so the database matches the latest response.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://openlibrary.org/search.json"
USER_AGENT = "accuknox-assignment/1.0 (books-to-sqlite)"
ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "output" / "books.db"


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="machine learning", help="Search text sent to Open Library")
    parser.add_argument("--limit", type=int, default=15, help="How many books to request (1-100)")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite database path")
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    return args


def fetch_books(query: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "limit": str(limit),
            "fields": "title,author_name,first_publish_year",
        }
    )
    request = urllib.request.Request(
        f"{API_URL}?{params}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.URLError as exc:
        raise SystemExit(f"Open Library request failed: {exc}") from exc

    docs = payload.get("docs")
    if not isinstance(docs, list):
        raise SystemExit("Open Library response did not contain a docs list")
    return docs


def format_authors(names: object) -> str:
    if not isinstance(names, list):
        return "Unknown"
    unique: list[str] = []
    for name in names:
        if isinstance(name, str) and name and name not in unique:
            unique.append(name)
    return ", ".join(unique) if unique else "Unknown"


def publication_year(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def rows_from_docs(docs: list[dict], query: str) -> list[tuple[str, str, int | None, str]]:
    rows: list[tuple[str, str, int | None, str]] = []
    for doc in docs:
        title = doc.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        rows.append(
            (
                title.strip(),
                format_authors(doc.get("author_name")),
                publication_year(doc.get("first_publish_year")),
                query,
            )
        )
    return rows


def store_books(db_path: Path, rows: list[tuple[str, str, int | None, str]]) -> list[tuple]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publication_year INTEGER,
                source_query TEXT NOT NULL
            )
            """
        )
        connection.execute("DELETE FROM books")
        connection.executemany(
            """
            INSERT INTO books (title, author, publication_year, source_query)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()
        return connection.execute(
            """
            SELECT publication_year, author, title
            FROM books
            ORDER BY publication_year IS NULL, publication_year, title
            """
        ).fetchall()
    finally:
        connection.close()


def display(rows: list[tuple], db_path: Path) -> None:
    print(f"Stored {len(rows)} books in {db_path}")
    print(f"{'Year':<6} Author | Title")
    print("-" * 100)
    for year, author, title in rows:
        year_text = "n/a" if year is None else str(year)
        print(f"{year_text:<6} {author} | {title}")


def main() -> None:
    configure_stdout()
    args = parse_args()
    docs = fetch_books(args.query, args.limit)
    rows = rows_from_docs(docs, args.query)
    stored = store_books(args.db, rows)
    display(stored, args.db)


if __name__ == "__main__":
    main()
