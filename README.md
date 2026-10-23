# CSC10014 Lab 3 — Assistant Core

A maintainable, deterministic Python service for office lookup, tuition
calculation, and handbook search.

## Setup

```bash
python -m venv .venv
# Git Bash: source .venv/Scripts/activate
python -m pip install -r requirements.txt
python -m pip install -e .
cp .env.example .env
```

The sample dataset is in `data/`. It contains the library example and the
thesis-registration rule used by the lab tests; replace it with the supplied
course dataset if your instructor provides additional records. Keep local
secrets in `.env`; do not commit that file.

## Run

```bash
python -m assistant_core "hi"
python -m assistant_core "tuition for 18 credits and 2 retake"
python -m assistant_core "where is the library?"
python -m assistant_core "help"
```

## Quality checks

```bash
pytest -q
ruff check .
ruff format --check .
```

The CLI writes answers to stdout and structured logs to stderr. The application
entry point for other clients is `AssistantService.handle(Message) -> Response`.
