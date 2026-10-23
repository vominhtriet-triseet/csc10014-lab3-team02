from __future__ import annotations

from typing import Protocol

from assistant_core.errors import ProviderError


class RuleLike(Protocol):
    id: str
    title: str
    text: str


class Responder(Protocol):
    def explain(self, question: str, rule: RuleLike) -> str: ...


class TemplateResponder:
    def explain(self, question: str, rule: RuleLike) -> str:
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def explain(self, question: str, rule: RuleLike) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"
