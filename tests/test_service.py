from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from assistant_core.errors import ProviderError
from assistant_core.models import Intent, Message
from assistant_core.service import AssistantService


@dataclass(frozen=True)
class FakeOffice:
    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class FakeRule:
    id: str
    title: str
    text: str


class FakeOffices:
    names = ("Library", "Student Affairs")

    def find(self, name: str) -> FakeOffice | None:
        if name == "Library":
            return FakeOffice("Library", "B.201", "Mon-Sat 07:00-20:00")
        if name == "Student Affairs":
            return FakeOffice("Student Affairs", "A.101", "Mon-Fri 08:00-17:00")
        return None


class FakeHandbook:
    rule = FakeRule(
        "H26-5.3",
        "Thesis registration",
        "Students may register a thesis when they have at least 120 accumulated credits and a GPA of at least 2.0.",
    )

    def search(self, query: str) -> FakeRule | None:
        if "thesis" in query.casefold():
            return self.rule
        return None


class FakeResponder:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls = 0

    def explain(self, question: str, rule: FakeRule) -> str:
        self.calls += 1
        if self.fail:
            raise ProviderError("provider unavailable")
        return f"{rule.title}: {rule.text}"


@pytest.fixture
def service() -> AssistantService:
    settings = SimpleNamespace(
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
    )
    return AssistantService(
        settings=settings,
        offices=FakeOffices(),
        handbook=FakeHandbook(),
        responder=FakeResponder(),
    )


def test_greeting(service: AssistantService) -> None:
    response = service.handle(Message(text="hello"))

    assert response.intent is Intent.GREETING
    assert response.answer == "Hello! I can help with offices, fees and rules."
    assert response.degraded is False


def test_help_lists_capabilities_without_calling_responder(
    service: AssistantService,
) -> None:
    response = service.handle(Message(text="what can you do?"))

    assert response.intent is Intent.HELP
    assert "office locations" in response.answer
    assert "tuition fees" in response.answer
    assert response.degraded is False
    assert service.responder.calls == 0


def test_fee_characterization(service: AssistantService) -> None:
    response = service.handle(Message(text="tuition for 18 credits and 2 retake"))

    assert response.intent is Intent.FEE
    assert response.answer == "Your tuition is 9,450,000 VND"


def test_office_lookup_uses_name_found_in_question(
    service: AssistantService,
) -> None:
    response = service.handle(Message(text="where is the library?"))

    assert response.intent is Intent.OFFICE
    assert response.answer == "Library: room B.201, open Mon-Sat 07:00-20:00."


def test_rule_response_includes_source(service: AssistantService) -> None:
    response = service.handle(Message(text="thesis registration credits"))

    assert response.intent is Intent.RULE
    assert response.sources[0].id == "H26-5.3"
    assert response.degraded is False


def test_rule_not_found_returns_unknown(service: AssistantService) -> None:
    response = service.handle(Message(text="unrelated topic"))

    assert response.intent is Intent.UNKNOWN
    assert response.sources == []


def test_provider_failure_uses_template_fallback() -> None:
    settings = SimpleNamespace(
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
    )
    service = AssistantService(
        settings=settings,
        offices=FakeOffices(),
        handbook=FakeHandbook(),
        responder=FakeResponder(fail=True),
    )

    response = service.handle(Message(text="thesis registration credits"))

    assert response.intent is Intent.RULE
    assert response.sources[0].id == "H26-5.3"
    assert response.degraded is True
    assert response.answer == (
        "Thesis registration: Students may register a thesis when they have at least "
        "120 accumulated credits and a GPA of at least 2.0."
    )
