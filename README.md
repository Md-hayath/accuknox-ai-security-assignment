# AccuKnox AI Security Engineer — assignments 1 and 2

This folder is the working copy of the take-home.

Assignment 1 is three separate Python scripts. They fetch books, chart student scores, and load a user CSV. Assignment 2 is the written answer in `assignment2/Assignment_2.pdf`. It does not run. Assignment 3 (one project link, plus three lines on why it was hard) is not in this folder yet.

Each script lists its assumptions at the top of the file.

## What the scripts do

| Script | What it does | Output |
| --- | --- | --- |
| `assignment1/books_to_sqlite.py` | Fetches books from the Open Library Search API and stores title, author, and publication year in SQLite | `assignment1/output/books.db` |
| `assignment1/scores_to_chart.py` | Fetches student scores, prints the average, and saves a bar chart | `assignment1/output/student_scores.png` |
| `assignment1/csv_to_sqlite.py` | Reads `name,email` rows from a CSV and inserts them into SQLite | `assignment1/output/users.db` |

Books come from `https://openlibrary.org/search.json`. That call needs internet access. A new search replaces the rows already in `books.db`.

The brief does not name a student-scores API. With no `--url`, the scores script serves `assignment1/data/student_scores.json` on `127.0.0.1` and fetches that URL. `--url` accepts any endpoint that returns either `{"students": [{"name", "score"}, ...]}` or a bare list of those objects. A score must be a number from 0 to 100.

The user file is `assignment1/data/users.csv`. Emails are unique. Running the import again skips people who are already in `users.db`, so a second run prints `Inserted: 0`.

## Run on your machine

Use this while you are changing the CSV, the scores file, or the Python. Python 3.11 or newer is required. Only the chart needs the package in `requirements.txt`.

```bash
pip install -r requirements.txt
python assignment1/run_all.py
```

One script:

```bash
python assignment1/books_to_sqlite.py --query "harry potter" --limit 5
python assignment1/scores_to_chart.py
python assignment1/csv_to_sqlite.py
```

Other useful arguments:

```bash
python assignment1/books_to_sqlite.py --query "distributed systems" --limit 10
python assignment1/scores_to_chart.py --url http://127.0.0.1:8000/student_scores.json
python assignment1/csv_to_sqlite.py --csv assignment1/data/users.csv --db assignment1/output/users.db
```

The databases and the PNG are written to `assignment1/output/`. That folder is gitignored. Run the scripts again to recreate the files.

To change the chart, edit a score in `assignment1/data/student_scores.json` and run `scores_to_chart.py` again. To add a person, add a `name,email` line to `assignment1/data/users.csv` and run `csv_to_sqlite.py` again.

## Run in Docker

Docker Desktop has to be running. The container runs the same three scripts. Assignment 2 is not copied into the image.

```bash
docker compose build
docker compose run --rm assignment1
```

One script, without a rebuild:

```bash
docker compose run --rm assignment1 python assignment1/books_to_sqlite.py --query "databases" --limit 3
```

`assignment1/output/` is mounted into the container, so `books.db`, `users.db`, and `student_scores.png` show up on your machine.

The image copies `assignment1/` at build time. After you edit a script, `users.csv`, or `student_scores.json`, run `docker compose build` again before `docker compose run`. A `--query` or `--limit` change does not need a rebuild.

The books call needs outbound HTTPS from the container. If it fails with `Network is unreachable`, confirm Docker Desktop is running and run the command again.

## Still to add before you send the take-home

- Your A / B / C ratings in section 1 of `assignment2/Assignment_2.pdf`. Those four cells are blank.
- A link to the most complex Python you have written
- A link to the most complex database code you have written
- Assignment 3: one project link, and three lines on why it was hard

Put the finished repo on GitHub and paste that link in the form. The form also asks for a resume whose link anyone can view, and a 4-minute video on Google Drive with the same access.
