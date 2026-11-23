"""Fetch student test scores from an HTTP API, print the average, and save a bar chart.

Assumptions
- The brief does not name a scores API. The JSON shape this script accepts is
  either {"students": [{"name": "...", "score": 80}, ...]}
  or a bare list of those objects.
- With no --url, the bundled sample is served on 127.0.0.1 and fetched over HTTP,
  using the same GET path as an external API. Replace --url with a real endpoint
  that returns the shape above.
- score must be a number from 0 to 100. Other rows are skipped.
- The average is the arithmetic mean of the scores that were kept.
- The chart is written to a PNG. Nothing is shown on screen, so the script can
  run without a desktop session.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_OUTPUT = ROOT / "output" / "student_scores.png"
USER_AGENT = "accuknox-assignment/1.0 (scores-to-chart)"


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        help="Scores API URL. Omit to fetch the bundled sample over local HTTP.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PNG path for the bar chart")
    return parser.parse_args()


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        raise SystemExit(f"Scores request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Scores response was not JSON: {exc}") from exc


def fetch_bundled_sample() -> object:
    """Serve data/student_scores.json on localhost and GET it."""
    if not (DATA_DIR / "student_scores.json").is_file():
        raise SystemExit(f"Missing sample file: {DATA_DIR / 'student_scores.json'}")
    handler = partial(QuietHandler, directory=str(DATA_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        return fetch_json(f"http://127.0.0.1:{port}/student_scores.json")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def parse_students(payload: object) -> list[tuple[str, float]]:
    if isinstance(payload, dict):
        records = payload.get("students")
    else:
        records = payload
    if not isinstance(records, list):
        raise SystemExit("Expected a list of students, or an object with a students list")

    students: list[tuple[str, float]] = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            print(f"Skipping row {index}: not an object", file=sys.stderr)
            continue
        name = record.get("name")
        score = record.get("score")
        if not isinstance(name, str) or not name.strip():
            print(f"Skipping row {index}: missing name", file=sys.stderr)
            continue
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            print(f"Skipping {name}: score is not a number", file=sys.stderr)
            continue
        if not 0 <= float(score) <= 100:
            print(f"Skipping {name}: score {score} is outside 0-100", file=sys.stderr)
            continue
        students.append((name.strip(), float(score)))

    if not students:
        raise SystemExit("No usable student scores in the response")
    return students


def average(scores: list[float]) -> float:
    return sum(scores) / len(scores)


def save_chart(students: list[tuple[str, float]], mean: float, output: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit("matplotlib is required. Run: pip install -r requirements.txt") from exc

    names = [name for name, _ in students]
    scores = [score for _, score in students]
    output.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.bar(names, scores, color="#2F6FED")
    axis.axhline(mean, color="#B45309", linestyle="--", linewidth=1.5, label=f"Average {mean:.2f}")
    axis.set_title("Student test scores")
    axis.set_xlabel("Student")
    axis.set_ylabel("Score")
    axis.set_ylim(0, 100)
    axis.legend()
    axis.tick_params(axis="x", rotation=45)
    figure.tight_layout()
    figure.savefig(output, dpi=120)
    plt.close(figure)


def main() -> None:
    configure_stdout()
    args = parse_args()
    payload = fetch_json(args.url) if args.url else fetch_bundled_sample()
    students = parse_students(payload)
    mean = average([score for _, score in students])
    save_chart(students, mean, args.output)
    print(f"Students: {len(students)}")
    print(f"Average score: {mean:.2f}")
    print(f"Chart written to: {args.output}")


if __name__ == "__main__":
    main()
