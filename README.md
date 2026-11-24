# AccuKnox AI Security Engineer — assignments 1 and 2

Assignment 1 is three Python scripts plus one runner. Assignment 2 is the written answer in `assignment2/Assignment_2.pdf`. The PDF does not run. Assignment 3 (one project link, plus three lines on why it was hard) is not in this folder yet.

Each script lists its assumptions at the top of the file.

## How to run

Python 3.11 or newer. From the repo root, in Git Bash or PowerShell:

```bash
pip install -r requirements.txt
python assignment1/run_all.py
```

That runs the three scripts in order and stops if one fails. You should see:

- a table of books (needs internet; Open Library)
- `Average score: 80.75` and a path to `assignment1/output/student_scores.png`
- `Inserted: 8` the first time, then `Inserted: 0` if you run it again

One script:

```bash
python assignment1/books_to_sqlite.py --query "harry potter" --limit 5
python assignment1/scores_to_chart.py
python assignment1/csv_to_sqlite.py
```

Other arguments:

```bash
python assignment1/books_to_sqlite.py --query "distributed systems" --limit 10
python assignment1/scores_to_chart.py --url http://127.0.0.1:8000/student_scores.json
python assignment1/csv_to_sqlite.py --csv assignment1/data/users.csv --db assignment1/output/users.db
```

`assignment1/output/` is gitignored. Run the scripts again to recreate `books.db`, `users.db`, and `student_scores.png`.

To change the chart, edit a score in `assignment1/data/student_scores.json` and run `scores_to_chart.py` again. To add a person, add a `name,email` line to `assignment1/data/users.csv` and run `csv_to_sqlite.py` again.

### Docker

Docker Desktop has to be running. The container runs the same three scripts. Assignment 2 is not copied into the image.

```bash
docker compose build
docker compose run --rm assignment1
```

One script, without a rebuild:

```bash
docker compose run --rm assignment1 python assignment1/books_to_sqlite.py --query "databases" --limit 3
```

`assignment1/output/` is mounted into the container, so the databases and the PNG show up on your machine.

The image copies `assignment1/` at build time. After you edit a script, `users.csv`, or `student_scores.json`, run `docker compose build` again before `docker compose run`. A `--query` or `--limit` change does not need a rebuild.

The books call needs outbound HTTPS from the container. If it fails with `Network is unreachable`, confirm Docker Desktop is running and run the command again.

## Architecture

There is no web app and no shared database. `run_all.py` starts each script as its own process, with the repo root as the working directory. The scripts do not import each other. They only share the output folder.

```
run_all.py
├── books_to_sqlite.py
│     Open Library HTTPS  →  rows  →  assignment1/output/books.db  →  printed table
├── scores_to_chart.py
│     local HTTP or --url  →  scores  →  average  →  assignment1/output/student_scores.png
└── csv_to_sqlite.py
      assignment1/data/users.csv  →  rows  →  assignment1/output/users.db  →  printed counts
```

**Books.** `books_to_sqlite.py` GETs `https://openlibrary.org/search.json` with `title`, `author_name`, and `first_publish_year`. Author lists are de-duplicated. Missing authors become `Unknown`. Missing years are SQL `NULL`. Each run deletes the existing rows and inserts the latest response, so `books.db` matches the last query. The default query is `machine learning` with a limit of 15.

**Scores.** The brief does not name a scores API. With no `--url`, `scores_to_chart.py` serves `assignment1/data/student_scores.json` on `127.0.0.1` and GETs that URL, so the fetch path is the same as a real API. `--url` accepts `{"students": [{"name", "score"}, ...]}` or a bare list of those objects. A score must be a number from 0 to 100. The average is the mean of the rows that were kept. matplotlib writes the PNG with the Agg backend, so no desktop window is required. The bundled sample of 12 students averages 80.75.

**CSV.** `csv_to_sqlite.py` reads UTF-8 `name,email` rows. Extra columns are ignored. Email is lowercased and must contain one `@`. `email` is unique, and inserts use `INSERT OR IGNORE`, so a second run adds nobody. SQL values are bound parameters.

**Container.** The Dockerfile is two stages. The first installs matplotlib from `requirements.txt`. The second copies only `assignment1/`, creates user `app` (uid 1000), and runs `python assignment1/run_all.py`. Compose starts that image read-only, with a 512 MB memory limit, one CPU, and `/tmp` as a tmpfs (matplotlib writes its cache there). The only host mount is `assignment1/output`.

Assignment 2 is separate. `assignment2/Assignment_2.pdf` is the written answer: self-ratings, the high-level pieces of an LLM chatbot, and a vector-database choice. It is not part of this runtime.

## Still to add before you send the take-home

- Your A / B / C ratings in section 1 of `assignment2/Assignment_2.pdf`. Those four cells are blank.
- A link to the most complex Python you have written
- A link to the most complex database code you have written
- Assignment 3: one project link, and three lines on why it was hard

Put the finished repo on GitHub and paste that link in the form. The form also asks for a resume whose link anyone can view, and a 4-minute video on Google Drive with the same access.
