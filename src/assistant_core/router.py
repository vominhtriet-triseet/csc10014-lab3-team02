"""Rule-based intent routing (pure)."""

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
HELP_REQUESTS = frozenset({"help", "what can you do", "what can you help with"})


def route(text: str, office_names: set[str]) -> Intent:
    t = text.lower().strip().rstrip("?!.")
    if t in GREETINGS:
        return Intent.GREETING
    if t in HELP_REQUESTS:
        return Intent.HELP
    if "fee" in t or "tuition" in t:
        return Intent.FEE
    # Names may keep their original case (e.g. "Library"), so compare lower-cased.
    if any(name.lower() in t for name in office_names):
        return Intent.OFFICE
    return Intent.RULE
