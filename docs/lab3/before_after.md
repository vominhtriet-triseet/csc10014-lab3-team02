# Before/After Maintainability Worksheet

| Question | Monolith | `assistant_core` |
| --- | --- | --- |
| Places to change the credit rate | One constant in source code | One `CREDIT_RATE_VND` environment variable |
| Tests run offline and deterministically? | No; the monolith has random provider failures | Yes; routing, tools, knowledge, service, and responder tests use deterministic implementations |
| Missing `handbook.json` | Prints/continues without a useful failure | `DataError` is raised while loading the handbook at startup |
| Secret printed or logged? | Yes, the monolith prints a test API key in debug output | No; the JSON formatter only includes an allowlist of fields and the API key is excluded from `Settings` representation |
| Module-level mutable state | Three mutable globals (nine globals total, per the lab handout) | No mutable application state; modules contain only immutable constants and a logger |
| Bare `except:` | Three | Zero |
| Longest function | About 65 lines (`handle`) | About 26 lines (`handle`); the work is split among private handlers |
| Swap the responder without touching the service? | No | Yes; a responder is injected into `AssistantService` |

## Reflection

The refactored package has more files and introduces typed models, named errors,
and dependency injection. That trade-off is worthwhile when multiple people
maintain the service or when it needs reliable tests and future extensions.
