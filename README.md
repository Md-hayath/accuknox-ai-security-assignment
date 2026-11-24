# AccuKnox AI Security Engineer take-home

Three parts. Assignment 1 is code you can run. Assignment 2 and Assignment 3 are written, and the scripts do not import them.

## Assignment 1

Three Python scripts, started together by `assignment1/run_all.py`. They do not import each other. Each one writes into `assignment1/output/`, and that folder is gitignored, so a fresh clone has no database and no chart until you run it. The assumptions for each script are at the top of the file.

Python 3.11 or newer. From the repo root, in Git Bash or PowerShell:

```bash
pip install -r requirements.txt
python assignment1/run_all.py
```

`run_all.py` runs the three scripts in order and stops if one fails. You should see a table of books from Open Library, then `Average score: 80.75` and a path to `assignment1/output/student_scores.png`, then `Inserted: 8`. Run the CSV script a second time and it prints `Inserted: 0`, because the email is unique and the insert is ignored.

One script at a time:

```bash
python assignment1/books_to_sqlite.py --query "harry potter" --limit 5
python assignment1/scores_to_chart.py
python assignment1/csv_to_sqlite.py
```

`books_to_sqlite.py` calls `https://openlibrary.org/search.json` and keeps the title, the author, and the first publish year. Author lists are de-duplicated. A missing author is stored as `Unknown`, and a missing year is SQL `NULL`. Each run clears the table and inserts the latest response, so `books.db` matches the last query. The default query is `machine learning` with a limit of 15. This call needs the internet.

`scores_to_chart.py` prints the average and writes a bar chart. The brief does not name a scores API, so with no `--url` the script serves `assignment1/data/student_scores.json` on `127.0.0.1` and fetches that URL. The body can be `{"students": [{"name", "score"}, ...]}` or a bare list of those objects. A score has to be a number from 0 to 100. matplotlib uses the Agg backend, so no window opens. The sample has 12 students and the average is 80.75. Edit a score in the JSON and run the script again if you want a different chart.

`csv_to_sqlite.py` reads `assignment1/data/users.csv`, which is `name,email` in UTF-8. Extra columns are ignored. The email is lowercased and has to contain one `@`. Values are bound parameters, and the insert is `INSERT OR IGNORE`. Add a `name,email` line to the CSV and run the script again to add a person.

A few other flags:

```bash
python assignment1/books_to_sqlite.py --query "distributed systems" --limit 10
python assignment1/scores_to_chart.py --url http://127.0.0.1:8000/student_scores.json
python assignment1/csv_to_sqlite.py --csv assignment1/data/users.csv --db assignment1/output/users.db
```

### Docker

Docker Desktop has to be running. The container runs the same three scripts. The written assignments are not copied into the image.

```bash
docker compose build
docker compose run --rm assignment1
```

One script, and a different query does not need a rebuild:

```bash
docker compose run --rm assignment1 python assignment1/books_to_sqlite.py --query "databases" --limit 3
```

`assignment1/output/` is mounted from your machine, so the databases and the PNG show up on the host. The image copies `assignment1/` when it is built. After you edit a script, `users.csv`, or `student_scores.json`, run `docker compose build` again before `docker compose run`.

The books call needs outbound HTTPS from the container. If it fails with `Network is unreachable`, check that Docker Desktop is up and run the command again.

The Dockerfile has two stages. The first installs matplotlib and the rest of `requirements.txt`. The second copies only `assignment1/`, creates user `app` (uid 1000), and runs `python assignment1/run_all.py`. Compose starts that image read-only, with a 512 MB memory limit, one CPU, and `/tmp` as a tmpfs, because matplotlib writes its cache there.

There is no web app and no shared database. `run_all.py` starts each script as its own process, with the repo root as the working directory.

```
run_all.py
├── books_to_sqlite.py
│     Open Library HTTPS  →  rows  →  assignment1/output/books.db  →  printed table
├── scores_to_chart.py
│     local HTTP or --url  →  scores  →  average  →  assignment1/output/student_scores.png
└── csv_to_sqlite.py
      assignment1/data/users.csv  →  rows  →  assignment1/output/users.db  →  printed counts
```

## Assignment 2

Written answers, in [Assignment2/My Experience in ML GenAI & Multi Agent Orchestration .pdf](<Assignment2/My Experience in ML GenAI & Multi Agent Orchestration .pdf>). The PDF does not run.

Three questions.

How I rate myself on LLM, deep learning, AI, and ML. A means I can build it alone, B means I can build it with someone reviewing the design, and C means I have little or no understanding. I marked LLM, deep learning, and AI as B, and ML as A.

The pieces of a chatbot built on an LLM, at a high level. The model writes the reply. Around it I describe the channel, one orchestrator for the turn, a short memory of the chat, hybrid retrieval, how the prompt is assembled, tool calling, checks on the way in and out, and a log so a bad answer can be traced.

What a vector database is, and which one I would use. I have built hybrid RAG: a dense embedding for meaning, and BM25 for the exact words, merged with reciprocal rank fusion. For an internal assistant over security documents I would keep the dense vectors in Qdrant, self-hosted, with a BM25 index beside it, because the documents have to stay on our network and the queries mix paraphrases with ids and error strings.

## Assignment 3

The project is FinGuard, a graph neural network that scores Bitcoin transactions for fraud.

https://github.com/Md-hayath/FinGuard-GNN-Fraud-Detection

The three lines, and the longer write-up of how I approached it, are in [Assignment3/README.md](Assignment3/README.md).

Fraud in that data is a pattern of payments, so the model learns over 203,769 transactions and 234,355 edges. The split has to be by time, otherwise a test transaction can sit next to future training data and the score looks better than it is. About 2% of nodes are labelled illicit and about 77% have no label; gradient boosting on the same features beat the graph network (test AUC-PR 0.80 against 0.56), and writing that down clearly mattered more than getting the network to train.
