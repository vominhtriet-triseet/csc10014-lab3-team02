"""Pure tools: parse a credit request and calculate tuition.

Everything here is deterministic and side-effect free: no I/O, no global
state, no randomness, no sleeping. Money is never computed by the responder
or an LLM; `tuition` is the single source of truth.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction

from assistant_core.errors import InvalidRequest

# A whole or decimal number (optionally negative) directly followed by a unit.
# The lookbehind stops us from reading "x18" or the "5" of "2.5" as a count.
_NUMBER = r"(?<![\w.,])(-?\d+(?:[.,]\d+)*)"
_CREDITS_RE = re.compile(_NUMBER + r"\s*-?\s*credits?\b")
_RETAKE_RE = re.compile(_NUMBER + r"\s*-?\s*(?:re-?takes?|retaking|retaken)\b")
_WHOLE_NUMBER_RE = re.compile(r"-?\d+")


def _single_count(pattern: re.Pattern[str], text: str, label: str) -> int | None:
    """Return the one integer matched by `pattern`, or None if there is none.

    Raises InvalidRequest when the number is not a whole number or when the
    text mentions the same quantity more than once (ambiguous, and this is
    money, so we do not guess).
    """
    matches = pattern.findall(text)
    if not matches:
        return None
    if len(matches) > 1:
        raise InvalidRequest(f"Found more than one {label} count; please give one.")
    token = matches[0]
    if not _WHOLE_NUMBER_RE.fullmatch(token):
        raise InvalidRequest(f"The {label} count must be a whole number, got {token!r}.")
    return int(token)


def parse_credits(text: str) -> tuple[int, int]:
    """Extract ``(credits, retake)`` from a free-text tuition question.

    "tuition for 18 credits and 2 retake" -> (18, 2)

    * Case-insensitive; "credit"/"credits" and "retake"/"retakes"/"re-take".
    * ``retake`` defaults to 0 when no retake count is given.
    * Only parses; it does not range-check. ``0 credits`` returns ``(0, 0)``
      and ``tuition`` rejects it.

    Raises InvalidRequest if no credit count is present, a count is not a
    whole number, or the same quantity is stated more than once.
    """
    normalized = text.casefold()

    credits = _single_count(_CREDITS_RE, normalized, "credit")
    if credits is None:
        raise InvalidRequest(
            "I could not find a number of credits (for example: '18 credits')."
        )

    retake = _single_count(_RETAKE_RE, normalized, "retake")
    return credits, 0 if retake is None else retake


def _require_int(value: object, name: str) -> None:
    # bool is a subclass of int; True/False are not meaningful credit counts.
    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidRequest(f"{name} must be a whole number, got {value!r}.")


def tuition(
    credits: int,
    retake: int,
    rate: int,
    retake_multiplier: float,
    max_credits: int,
) -> int:
    """Return tuition in whole VND.

    ``tuition = credits * rate + retake * rate * retake_multiplier``

    ``retake`` is the number of retaken credits charged *in addition to*
    ``credits``, at ``retake_multiplier`` times the normal rate. Example:
    ``tuition(18, 2, 450_000, 1.5, 30) == 9_450_000``.

    The multiplier is applied with exact rational arithmetic, then the
    fractional VND (if any) is rounded half up, so the result never depends on
    binary floating-point error.

    Raises InvalidRequest if ``credits`` is outside ``1..max_credits`` or
    ``retake`` is negative (or either is not an integer).
    """
    _require_int(credits, "credits")
    _require_int(retake, "retake")

    if not 1 <= credits <= max_credits:
        raise InvalidRequest(
            f"credits must be between 1 and {max_credits}, got {credits}."
        )
    if retake < 0:
        raise InvalidRequest(f"retake must not be negative, got {retake}.")

    base = credits * rate
    surcharge = Fraction(retake * rate) * Fraction(str(retake_multiplier))
    return int(base + math.floor(surcharge + Fraction(1, 2)))