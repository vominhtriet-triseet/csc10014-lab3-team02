# Assistant Core Architecture

Browser
   |
   v
ui/app.py
   |
   v
ui/api_client.py
   |
   v
FastAPI (assistant_api)
   |
   v
AssistantService (assistant_core)
   |
   +---- tools
   |
   +---- knowledge
   |
   +---- rag
   |       +---- index
   |       +---- answerer
   |       +---- llm
   |
   +---- database (db.py)

## 1. Module responsibilities

| Module | Responsibility |
|---|---|
| `assistant_api/main.py` | Create the FastAPI application and expose API endpoints |
| `assistant_api/schemas.py` | Define and validate API request and response schemas |
| `assistant_api/db.py` | Store interaction metadata and feedback in the database |
| `assistant_api/ratelimit.py` | Limit the number of requests from clients |
| `assistant_api/weather.py` | Provide weather-related functionality through the API |
| `assistant_core/config.py` | Read and validate configuration from environment variables |
| `assistant_core/errors.py` | Define named application exceptions |
| `assistant_core/models.py` | Define the public `Message`, `Response`, `Intent`, and `Source` types |
| `assistant_core/router.py` | Select an intent from the user's message, including help requests |
| `assistant_core/knowledge.py` | Load and search the office directory and handbook |
| `assistant_core/tools.py` | Parse credit requests and calculate tuition deterministically |
| `assistant_core/responder.py` | Generate rule explanations behind a replaceable interface |
| `assistant_core/service.py` | Coordinate routing, tools, knowledge, and response generation |
| `assistant_core/rag/index.py` | Index and retrieve relevant knowledge documents |
| `assistant_core/rag/answerer.py` | Generate grounded answers using retrieved sources and handle escalation |
| `assistant_core/rag/llm.py` | Provide the language-model interface for response generation |
| `assistant_core/logging_setup.py` | Configure structured JSON logging |
| `assistant_core/__main__.py` | Build the application and provide the command-line interface |
| `ui/app.py` | Render the Streamlit user interface and handle user interactions |
| `ui/api_client.py` | Send HTTP requests to the backend API and handle API errors |
| `ui/logic.py` | Format sources and status messages for display in the UI |

## 2. Service interface

```python
AssistantService.handle(msg: Message) -> Response
```

`Message` contains the request text (1–2000 characters) and a session ID.
`Response` contains the answer, intent, source list, and a `degraded` flag that
indicates whether a fallback responder was used.

The command-line interface calls the service rather than implementing
application logic itself. The FastAPI layer also calls the service, allowing
the API and CLI to share the same application logic.

The Streamlit UI communicates with the backend exclusively through HTTP
requests handled by `ui/api_client.py`. It does not import or call
`assistant_core` directly. This separation allows the UI and backend to be
developed and tested independently.

Invalid API requests are rejected through request validation. Configuration
and knowledge-data errors are reported during startup. Provider failures are
handled through fallback behavior where supported, and the response retains
its source information and indicates degraded operation when applicable.

## 3. Architectural decisions

### The UI communicates with the backend through the API

The Streamlit UI sends requests to the FastAPI backend through
`ui/api_client.py`. It does not import `assistant_core` or access the
database directly. This keeps presentation logic separate from application
logic and allows the backend to serve other clients in the future.

### Interaction data is stored with privacy in mind

The database stores interaction metadata and feedback rather than raw user
message content. Session identifiers are stored as salted hashes instead of
raw session IDs. This reduces the amount of identifiable information retained
by the application.

### RAG responses must be grounded in retrieved sources

The RAG pipeline retrieves relevant knowledge documents before generating an
answer. When retrieval confidence is too low, the system can abstain and
escalate the question instead of generating an unsupported answer. Generated
answers are checked against their retrieved sources to improve grounding.

### API errors are handled by the UI client

`ui/api_client.py` centralizes HTTP communication and error handling. Backend
connection failures and unsuccessful responses are converted into
understandable messages for the UI instead of exposing raw exceptions or
causing the Streamlit application to crash.

### Response generation supports fallback behavior

The service and RAG components separate response generation from the
underlying language-model provider. When a provider is unavailable, supported
fallback behavior allows the application to communicate that it is operating
in a degraded state while preserving available source information.