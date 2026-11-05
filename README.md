# CSC10014 Study Assistant — Core + REST API (Lab 3–4)

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

## Run the API (Lab 4)

```bash
uvicorn assistant_api.main:create_app --factory --reload
```

Open http://127.0.0.1:8000/docs for the interactive OpenAPI documentation.

### API contract (v1)

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/health` | — | 200 `{"status":"ok","version":...}` | — |
| POST | `/v1/chat` | `{"message": str 1–2000, "session_id": str}` | 200 `{answer, intent, sources[], degraded, request_id}` | 422 invalid, 429 rate limit |
| POST | `/v1/feedback` | `{"request_id": str, "rating": -1/0/1, "comment"?: str ≤500}` | 201 feedback with `id`, `created_at` | 422 |
| GET | `/v1/feedback` | header `X-API-Key` | 200 list | 401 |
| GET | `/v1/weather` | — | 200 `{temperature_c, wind_kmh, description, observed_at, stale}` | 503 upstream down |
| GET | `/v1/offices` | — | 200 list of `{name, room, hours}` sorted by name | — |

All errors use one shape: `{"error": {"code": "...", "message": "..."}}`.

### Warm-up (P1–P5)

```bash
cd practice
uvicorn hello_api:app --reload
pytest -q test_hello_api.py
```

## Quality checks

```bash
pytest -q
ruff check .
ruff format --check .
bash api-tests/curl_tests.sh       # manual tests against a running server
```

Postman / Bruno: import `api-tests/study-assistant.postman_collection.json`.

The CLI writes answers to stdout and structured logs to stderr. The application
entry point for other clients is `AssistantService.handle(Message) -> Response`.
