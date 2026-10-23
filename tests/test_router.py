import pytest

from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"library", "student affairs office"}


@pytest.mark.parametrize(
    "text",
    ["hi", "hello", "hey", "xin chao", "Hello!", "  HI  ", "Xin Chao?!", "hey..."],
)
def test_greeting(text):
    assert route(text, OFFICES) is Intent.GREETING


@pytest.mark.parametrize("text", ["tuition for 18 credits", "What is the FEE?", "Tuition?"])
def test_fee(text):
    assert route(text, OFFICES) is Intent.FEE


@pytest.mark.parametrize(
    "text",
    ["where is the library?", "WHERE IS THE LIBRARY", "student affairs office hours."],
)
def test_office(text):
    assert route(text, OFFICES) is Intent.OFFICE


def test_office_names_keep_original_case():
    assert route("where is the library?", ("Library", "Student Affairs Office")) is Intent.OFFICE


@pytest.mark.parametrize(
    "text",
    ["thesis registration credits", "can I retake an exam?", "hello there, rules?"],
)
def test_rule(text):
    assert route(text, OFFICES) is Intent.RULE


def test_fee_has_priority_over_office():
    assert route("library fee", OFFICES) is Intent.FEE


def test_fee_has_priority_over_greeting_text():
    assert route("hi, what is the fee", OFFICES) is Intent.FEE


def test_empty_office_names():
    assert route("where is the library", set()) is Intent.RULE


def test_never_returns_unknown():
    assert route("???", OFFICES) is Intent.RULE


@pytest.mark.parametrize("text", ["help", "Help!", "what can you do?", "what can you help with"])
def test_help(text):
    assert route(text, OFFICES) is Intent.HELP
