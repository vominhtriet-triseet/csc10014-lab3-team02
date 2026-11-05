# Lab 4 – H2 Reflection

In Lab 3, `service.handle()` was a plain Python function call: only Python code running in the same process could use it, and data moved as `Message`/`Response` objects.
In Lab 4, `POST /v1/chat` exposes the same service over HTTP, so any client (browser, mobile app, Postman, a program in another language) can call it by sending JSON and reading a status code.
The HTTP version gives the team a clear contract (`/docs`, Pydantic schemas, one error shape, standard codes such as 422, 401, 429, 503) that the frontend and backend can agree on and build in parallel.
It also lets us add cross-cutting concerns in one place, such as the admin API key, rate limiting, and a clean 503 when an external service is down, without changing the core service.
The cost is extra latency and more failure cases (network errors, security), but for a team building one product with several clients, HTTP is the better boundary.
