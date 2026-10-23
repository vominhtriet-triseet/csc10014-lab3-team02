"""Command-line interface for assistant_core."""

from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError, ConfigError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder, TemplateResponder
from assistant_core.service import AssistantService


def build_service() -> AssistantService:
    settings = load_settings()
    setup_logging(settings.log_level)

    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")

    if settings.llm_provider == "stub":
        responder = StubLLMResponder()
    elif settings.llm_provider == "template":
        responder = TemplateResponder()
    else:
        raise ConfigError(f"Unsupported LLM_PROVIDER: {settings.llm_provider!r}")

    return AssistantService(
        settings=settings,
        offices=offices,
        handbook=handbook,
        responder=responder,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smart Virtual Assistant")
    parser.add_argument("text", help="question or request for the assistant")
    args = parser.parse_args(argv)

    try:
        service = build_service()
        response = service.handle(Message(text=args.text))
    except ValidationError as exc:
        print(f"Invalid request: {exc}", file=sys.stderr)
        return 2
    except AssistantError as exc:
        print(f"Assistant startup or request error: {exc}", file=sys.stderr)
        return 1

    print(response.answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
