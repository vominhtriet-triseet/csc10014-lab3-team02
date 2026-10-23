# Assistant Core Architecture

## 1. Module responsibilities

| Module | Responsibility |
|---|---|
| `config.py` | Read and validate configuration from environment variables |
| `errors.py` | Define named application exceptions |
| `models.py` | Define the public `Message`, `Response`, `Intent`, and `Source` types |
| `router.py` | Select an intent from the user's message |
| `knowledge.py` | Load and search the office directory and handbook |
| `tools.py` | Parse credit requests and calculate tuition deterministically |
| `responder.py` | Generate rule explanations behind a replaceable interface |
| `service.py` | Coordinate routing, tools, knowledge, and response generation |
| `logging_setup.py` | Configure structured JSON logging |
| `__main__.py` | Build the application and provide the command-line interface |

## 2. Service interface

```python
AssistantService.handle(msg: Message) -> Response
```

`Message` contains the request text (1–2000 characters) and a session ID.
`Response` contains the answer, intent, source list, and a `degraded` flag that
indicates whether a fallback responder was used.

The command-line interface calls the service rather than implementing
application logic itself. Future API and UI layers can use the same method.
Invalid messages are rejected by the Pydantic model. Configuration and
knowledge-data errors are reported during startup. Provider failures are
handled by the service with a template fallback; the response retains its
source and sets `degraded=True`.

## 3. Architectural decisions

### Tuition is calculated deterministically

Tuition is computed by pure functions in `tools.py`, not by an LLM. This keeps
financial calculations exact, repeatable, and testable without I/O.

### Response generation is replaceable

`AssistantService` receives a `Responder` through its constructor. Tests can
inject a fake or failing responder, and a real provider can later be added
without coupling provider details to the service.

### Configuration comes from the environment

Rates, provider selection, data paths, and log level are read from environment
variables. `.env.example` documents the available settings without committing
real secrets.
