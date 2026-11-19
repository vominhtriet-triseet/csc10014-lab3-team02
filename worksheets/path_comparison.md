# Lab 6 — Three assistant paths

Run `python eval/compare_paths.py` and fill in.

| Path | Correct /25 | Abstain correct /7 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 9/25 | 7/7 | 0.0 | 5 | E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E23 |
| retrieval | 20/25 | 6/7 | 0.0 | 4 | E13 E14 E15 E19 E23 |
| llm (provider: ____) | 20/25 | 6/7 | 0.1 | 3 | E13 E14 E15 E19 E23 |

Which path would you ship for policy questions, and why? (3 sentences)
I would ship the retrieval path for policy questions because it achieves 20/25 correct answers while providing information directly from the knowledge base. It is more capable than the deterministic path, which cannot answer most document-based questions. Although it still has some retrieval and abstention errors, it is relatively predictable and easier to control than the LLM path.
