# AccuKnox AI Security Engineer — assignments 1 and 2

Assignment 1 is three Python scripts. Assignment 2 is the written answers in `assignment2/answers.md`. Assignment 3 (a project you are proud of, plus three lines on why it was hard) is not in this repo yet.

The brief allows assumptions if they are written down. Each script states its assumptions at the top. Read those before you change an API URL or a column name.

## Assignment 1 — what each script does

| Script | Problem it solves | Output |
| --- | --- | --- |
| `assignment1/books_to_sqlite.py` | Fetch books (title, author, publication year) from a REST API, store them in SQLite, print them | `assignment1/output/books.db` |
| `assignment1/scores_to_chart.py` | Fetch student scores from an API, print the average, draw a bar chart | `assignment1/output/student_scores.png` |
| `assignment1/csv_to_sqlite.py` | Read `name,email` rows from a CSV and insert them into SQLite | `assignment1/output/users.db` |

Books come from the Open Library Search API (`https://openlibrary.org/search.json`). That call needs a network.

The brief does not name a student-scores API. `scores_to_chart.py` GETs JSON of the form `{"students": [{"name", "score"}, ...]}`. With no `--url`, it serves the bundled file `assignment1/data/student_scores.json` on `127.0.0.1` and fetches that URL, so the demo still goes through HTTP. Point `--url` at any API that returns the same shape.

The user CSV is `assignment1/data/users.csv`.

## Run on the host

From this directory, with Python 3.11+:

```powershell
pip install -r requirements.txt
python assignment1/books_to_sqlite.py
python assignment1/scores_to_chart.py
python assignment1/csv_to_sqlite.py
```

Or all three, in that order:

```powershell
python assignment1/run_all.py
```

`matplotlib` is only needed for the chart. The other two scripts use the standard library.

## Run in a container

The image runs the same three scripts. Assignment 2 is not in the image. Docker Desktop has to be running. The books script calls Open Library, so the container needs outbound HTTPS.

```powershell
docker compose build
docker compose run --rm assignment1
```

One script:

```powershell
docker compose run --rm assignment1 python assignment1/books_to_sqlite.py --limit 5
```

Databases and the chart still land in `assignment1/output/` on your machine, because that folder is mounted into the container.

Useful overrides:

```powershell
python assignment1/books_to_sqlite.py --query "distributed systems" --limit 10
python assignment1/scores_to_chart.py --url http://127.0.0.1:8000/student_scores.json
python assignment1/csv_to_sqlite.py --csv assignment1/data/users.csv --db assignment1/output/users.db
```

Generated databases and the PNG are written under `assignment1/output/` and are gitignored. Run the scripts again to recreate them.

## Links the brief also asks for

These are your repositories, not something this repo can invent. Add them before you send the write-up:

- Most complex Python you have written:
- Most complex database code you have written:

## Assignment 2

Assignment 2 does not run. There is no server, database, or container for it. The brief asks for written answers, sent as a Word document or PDF saved under your name (or a Drive link), with your resume attached.

`assignment2/answers.md` is the draft sitting in this repo so you can edit it. You can leave it here. You do not have to put it in the Docker image, and you should not submit this git repo in place of the document.

- Section 1 is the A / B / C self-rating. The cells are empty. Fill them with ratings you can defend in the technical round.
- Section 2 is the LLM chatbot architecture.
- Section 3 explains vector databases, defines a security-assistant problem, and selects Qdrant for it.

Export that file to Word or PDF and save it under your name before you send it. Attach your latest resume. The hiring note says a copied chatbot answer can be rejected, so read sections 2 and 3 and rewrite any sentence you would not say out loud in the interview.
