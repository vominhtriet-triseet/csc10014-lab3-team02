# Lab 7 — Usability checklist (tick before your user test)

- [x] The first screen says what the assistant can do, with example questions
- [x] Empty or too-long input shows a friendly message (not a crash)
- [x] While waiting, the user sees "Thinking…"
- [x] Every answer from documents shows its sources
- [x] "I don't know" answers tell the user who can help (escalation)
- [x] If the backend is down, the page says so clearly
- [x] Each answer has 👍 / 👎, and clicking gives a "thanks" message
- [x] The page says it is an AI assistant
- [x] Text is readable (size, contrast); buttons have clear labels
- [x] Works on a phone-width window

## What we fixed while checking

- 👍/👎 buttons stayed on screen after a vote until the next click. They now use an `on_click` callback, so they disappear right away.
- On a phone-width window the sidebar is collapsed, so the "This is an AI assistant" note was hidden. The note is now also shown under the title.
- The feedback buttons showed only emojis. They now read "👍 Helpful" and "👎 Not helpful".

## Hallway test

Tester: ____ (another team) — What surprised them: ____
