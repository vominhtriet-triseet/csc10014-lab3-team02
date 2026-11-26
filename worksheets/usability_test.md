# H1 — Real User Test

## User test
Duration: 10 minutes

### Observations

1. The user understood the purpose of the assistant from the first screen and could start asking questions using the example prompts.

2. The user noticed the `Thinking…` message while waiting for an answer and understood that the assistant was processing the request.

3. The user understood the 👍 / 👎 feedback buttons and received a confirmation message after submitting feedback.

### Fix made

Improved the feedback interaction so that after the user clicks 👍 or 👎, the feedback buttons disappear and a confirmation toast is shown. This prevents the same answer from being rated multiple times and gives the user clear confirmation that their feedback was received.