# Lab 7 homework — 10-minute usability test

Tester: simulated first-time user (walkthrough done by the team, not a real outside tester)  Date: 2026-11-26
Task you gave them: "Find out if you can register your thesis with 118 credits, and where to replace a lost student card."

Rule: do not help or explain. Watch and write down what happens.

| # | What the tester did or said | What they expected | Why the system/UI caused it | Fix idea |
|---|---|---|---|---|
| 1 | Typed both parts in one message: "can I register my thesis with 118 credits and where can I replace a lost student card" | Two answers, one for each part | The assistant answers only the best-matching paragraph (student card, `S26#3`). The thesis part is dropped and the page does not say so | Detect two questions and answer both, or say "I answered the student card part; please ask the thesis question separately" |
| 2 | Asked "I only have 118 credits, can I start thesis?" and read the answer twice | A direct "No, you need 120 credits" | The answer only quotes the rule ("at least 120 accumulated credits…"); the user has to compare 118 with 120 alone | Let the answer compare the number in the question with the rule and start with "No" / "Yes" |
| 3 | Opened the page in a phone-width window and looked for what to ask | A list of example questions on the first screen | The examples are in the sidebar, which is collapsed on a phone, so the first screen shows only one example inside the welcome text | Show the example questions in the main area on the first screen |

The one change we made (commit link): observation 3 — example questions are shown in the main area on the first screen (`ui/app.py`); https://github.com/vominhtriet-triseet/csc10014-lab3-team02/commit/ee8a10f8b9c6774f98ee21061abebfbfbb0020ac
Before / after screenshot: attached in the PR description (phone width, 375 px)
