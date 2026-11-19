# Lab 6 — H1: five more test questions

Author: vominhtriet-triseet. Added to `eval/cases.jsonl` as E21–E25. Each expected source was looked up in `data/kb/`.

| Id | Question | Expected | Kind |
|---|---|---|---|
| E21 | how many semesters can I take a leave of absence | `H26#8.1` Leave of absence | normal |
| E22 | how much does a new student card cost | `S26#3` Student card replacement | normal |
| E23 | can I renew a borrowed book online | `S26#1` Library borrowing | normal |
| E24 | what is the phone number of my classmate | abstain | privacy |
| E25 | who is the dean of the faculty | abstain | out-of-scope |

## New comparison table

`python eval/compare_paths.py` (stub provider, `RETRIEVAL_MIN_SCORE=2.0`, 25 cases):

```
path                correct  abstain ok  p50 ms  max ms
deterministic          9/25       7/7     0.0     0.5   fails: E01 E02 E05 E06 E07 E08 E09 E10 E11 E12 E13 E14 E15 E21 E22 E23
retrieval             19/25       5/7     0.0     0.1   fails: E13 E14 E15 E19 E23 E25
llm (stub)            19/25       5/7     0.2     0.5   fails: E13 E14 E15 E19 E23 E25
```

Before (20 cases): retrieval and llm 16/20, abstain 4/5. My five questions add 3 passes (E21, E22, E24) and 2 failures (E23, E25) on both search paths.

## Did any of my questions fail?

Yes, two of them failed, both because search only matches words and cannot judge meaning: in E23 the word "online" pulls up the password-reset section (S26#2 scores 1.91 against S26#1's 1.79, and both are below 2.0, so the assistant refuses a question it could answer), and in E25 the word "faculty" matches the late-thesis section (H26#5.4 scores 2.17, just above 2.0), so the assistant answers about thesis approval instead of saying "I don't know".

## Notes

- E21 and E22 pass with very high scores (8.14 and 9.84), because the questions use the same words as the documents ("leave of absence", "student card").
- E22 deliberately says "cost". The same question with "fee" ("what is the student card replacement fee") is sent to the tuition calculator by the router and never reaches search. That is the same router problem as E13 and E15.
- E24 is stopped by the privacy guard (`guard.py`) before search, so no source is shown.
