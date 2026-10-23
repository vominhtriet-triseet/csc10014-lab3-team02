from __future__ import annotations

import io
import json
import logging
from dataclasses import dataclass

import pytest

from assistant_core.errors import ProviderError
from assistant_core.logging_setup import JsonFormatter, setup_logging
from assistant_core.responder import StubLLMResponder, TemplateResponder


@dataclass(frozen=True)
class DummyRule:
    id: str
    title: str
    text: str


@pytest.fixture
def sample_rule() -> DummyRule:
    return DummyRule(
        id="H26-5.3",
        title="Thesis registration",
        text=(
            "Students may register a thesis when they have at least 120 accumulated credits "
            "and a GPA of at least 2.0."
        ),
    )


def test_template_responder_deterministic(sample_rule: DummyRule) -> None:
    responder = TemplateResponder()
    result = responder.explain("thesis credits?", sample_rule)
    assert result == (
        "Thesis registration: Students may register a thesis when they have at least 120 accumulated credits "
        "and a GPA of at least 2.0."
    )


def test_stub_llm_responder_success_deterministic(sample_rule: DummyRule) -> None:
    responder = StubLLMResponder(fail=False)
    first = responder.explain("thesis credits?", sample_rule)
    second = responder.explain("thesis credits?", sample_rule)
    assert first == (
        "Based on 'Thesis registration': Students may register a thesis when they have at least 120 "
        "accumulated credits and a GPA of at least 2.0."
    )
    assert first == second


def test_stub_llm_responder_failure_raises_provider_error(
    sample_rule: DummyRule,
) -> None:
    responder = StubLLMResponder(fail=True)
    with pytest.raises(ProviderError, match="stub provider unavailable"):
        responder.explain("thesis credits?", sample_rule)


def test_json_formatter_includes_extra_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="assistant_core",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="handled",
        args=(),
        exc_info=None,
    )
    record.intent = "fee"
    record.latency_ms = 0.1
    record.session = "local"
    record.degraded = False

    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed == {
        "level": "INFO",
        "logger": "assistant_core",
        "msg": "handled",
        "intent": "fee",
        "latency_ms": 0.1,
        "session": "local",
        "degraded": False,
    }


def test_logging_does_not_leak_secrets_or_user_message() -> None:
    buffer = io.StringIO()
    logger = setup_logging(level="INFO", stream=buffer, logger_name="test_assistant_logger")

    secret_key = "sk-test-2b7c1d9e4f0a"
    raw_user_question = "My secret question about tuition for 18 credits"

    logger.info(
        "handled",
        extra={
            "intent": "fee",
            "latency_ms": 0.2,
            "session": "local",
            "degraded": False,
            "api_key": secret_key,
            "user_message": raw_user_question,
        },
    )

    log_line = buffer.getvalue().strip()
    parsed = json.loads(log_line)

    assert secret_key not in log_line
    assert raw_user_question not in log_line
    assert "api_key" not in parsed
    assert "user_message" not in parsed
    assert parsed["intent"] == "fee"
