# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7/20 | 5/5 | 0.0 ms | 5 | Limited coverage; cannot answer many handbook questions |
| retrieval | 16/20 | 4/5 | 0.0 ms | 4 | Lexical mismatch and incorrect retrieval for some queries |
| llm (provider: stub) | 16/20 | 4/5 | 0.1 ms | 3 | Cannot reliably recognize when retrieved information is insufficient |

Which path would you ship for policy questions, and why? (3 sentences)
I would ship the retrieval path for handbook questions because it can answer more questions using the provided documents. It also provides source references, making the answers easier to verify. However, I would keep the deterministic path for fixed rules and calculations because its behavior is more predictable and controllable.


