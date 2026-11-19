# Lab 6 — Part F: comparing the three assistant paths

Command (from the repo root, `.env` copied from `.env.example`, `LLM_PROVIDER=stub`, `RETRIEVAL_MIN_SCORE=2.0`):

```
python eval/compare_paths.py
```

Output:

```
path                correct  abstain ok  p50 ms  max ms
deterministic          7/20       5/5     0.0     0.7   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15
retrieval             16/20       4/5     0.0     0.1   fails: E13 E14 E15 E19
llm (stub)            16/20       4/5     0.2     0.5   fails: E13 E14 E15 E19
```

| Path | Correct /20 | Abstain correct /5 | p50 latency | Controllability (1–5) | Main failure mode |
|---|---|---|---|---|---|
| deterministic | 7 | 5 | 0.0 ms | 5 | Only answers fees and offices; every handbook question is refused (13 misses). |
| retrieval | 16 | 4 | 0.0 ms | 4 | Keyword matching: a rare word in the wrong section can win (E14, E19); the router sends some questions away before search (E13, E15). |
| llm (provider: stub) | 16 | 4 | 0.2 ms | 3 | Same misses as retrieval, because the stub only rephrases the top chunk; a real model adds variable wording and seconds of latency. |

## Which path we would ship for policy questions

We would ship the **llm** path for handbook questions, because it answers as many questions as retrieval and phrases them in a friendly way, while every safety check stays in our code: it abstains before calling the model when the best score is below 2.0, it rejects answers that cite chunks we did not retrieve, and it falls back to quoting the paragraph when the model fails.
Fees and offices should stay on the deterministic path, since money must be computed exactly and the rules path is the only one with 5/5 correct refusals.
The first failure we would fix is **E15 and E13 (the router)**: both questions never reach search, because the router sees "library" or "tuition" and sends them to the office lookup or the fee calculator, so no change to retrieval or to the model can fix them.

## Why each case fails (checked by tracing the four questions)

| Case | Question | Route | Top BM25 hits | What actually goes wrong |
|---|---|---|---|---|
| E13 | when is tuition due | **fee** | F26#1 2.28, F26#3 1.48 | "tuition" sends it to the fee calculator, which answers "How many credits?". Even through search, F26#1 (tuition per credit) beats F26#3 (payment deadline), because the deadline says "paid by the end of week 6", not "due". |
| E14 | can I take 32 credits | rule | **H26#7.2 2.09**, H26#6.1 1.48 | "take" is rare and appears only in 7.2 (exam absence: "take the exam"), while "credits" appears in many chunks and is worth little. 6.1 does contain "credits", so the PDF's "credits ≠ credit" explanation does not fully apply to our data. |
| E15 | how long can I keep a library book | **office** | S26#1 2.30 | "library" matches an office name, so the user gets the library's room and hours. Search would have found the right chunk (S26#1). |
| E19 | is the final exam open-book | rule | H26#7.2 5.62 | "final" and "exam" match the exam-absence chunk strongly (5.62, far above 2.0), so we don't abstain, and the stub cannot tell that the paragraph doesn't answer the question. |

## Code changes needed to run the comparison

`eval/compare_paths.py` did not run on `main` (`'Settings' object has no attribute 'kb_dir'`). Part F adds the missing pieces from the Lab 6 starter to our own code, without replacing it:

- `config.py`: Lab 6 settings (`KB_DIR`, `RETRIEVAL_KIND`, `RETRIEVAL_MIN_SCORE`, `PROMPT_VERSION`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_TIMEOUT_S`). `ollama` no longer requires an API key.
- `models.py`: `Response.path`, `Response.escalate`, `Response.confidence`.
- `service.py`: an optional `rag` answerer. With it, rule questions pass through the privacy guard and then retrieval/LLM. Without it, the Lab 3 `handbook.json` path is unchanged. A fee question with no credit count now returns "How many credits?" instead of crashing (it was a 500 over the API).
- `tests/test_service_rag.py`: 6 tests for this wiring.

## With 5 queries added personally (H1):

path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.4   
retrieval             19/25       5/7     0.0     0.2   
llm (stub)            19/25       5/7     0.1     0.4   

E23 failed because the retrieval system did not correctly match the tuition question to its expected source, while E25 failed because the assistant did not abstain from a question about another student's private information.

