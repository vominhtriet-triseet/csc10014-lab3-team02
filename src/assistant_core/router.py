"""Pure intent routing.

`route` only classifies; it never looks anything up. It returns GREETING, FEE,
OFFICE or RULE. It never returns UNKNOWN: whether the handbook actually has an
answer for a RULE question is the service's decision.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

from assistant_core.models import Intent

_GREETINGS = frozenset({"hi", "hello", "hey", "xin chao"})
# Whole words only, so "coffee" and "feedback" are not fee questions.
_FEE_RE = re.compile(r"\b(?:fees?|tuition)\b")
_TRAILING_PUNCTUATION_RE = re.compile(r"[^\w\s]+$")


def _fold(text: str) -> str:
    """Lower-case and drop diacritics, so "Xin chào" == "xin chao"."""
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.replace("\u0111", "d")  # đ has no decomposition


def _normalize(text: str) -> str:
    """Fold, strip, drop trailing punctuation and collapse inner whitespace."""
    folded = _TRAILING_PUNCTUATION_RE.sub("", _fold(text).strip())
    return " ".join(folded.split())


def route(text: str, office_names: Iterable[str]) -> Intent:
    """Classify `text`. Checked in this order, first match wins:

    1. GREETING: the whole message is hi / hello / hey / xin chao
       (case, accents, surrounding spaces and trailing punctuation ignored).
       "hello, tuition for 18 credits" is therefore a FEE question, not a greeting.
    2. FEE: contains the word "fee", "fees" or "tuition".
    3. OFFICE: contains any office name (case-insensitive substring, the same
       rule `AssistantService._handle_office` uses).
    4. RULE: everything else.
    """
    normalized = _normalize(text)

    if normalized in _GREETINGS:
        return Intent.GREETING

    if _FEE_RE.search(normalized):
        return Intent.FEE

    lowered = text.casefold()
    for name in office_names:
        needle = name.strip().casefold()
        if needle and needle in lowered:
            return Intent.OFFICE

    return Intent.RULE