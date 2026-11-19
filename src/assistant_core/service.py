"""Application service for routing assistant messages."""

from __future__ import annotations

import logging
from time import perf_counter

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError, InvalidRequest, ProviderError
from assistant_core.guard import PRIVATE_REPLY, is_private_request
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

logger = logging.getLogger("assistant_core")


class AssistantService:
    """Coordinate routing, knowledge retrieval, tools, and response generation."""

    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: Responder,
        rag: RagAnswerer | None = None,
    ) -> None:
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()
        self.rag = rag  # None = old handbook.json path (Lab 3); set = Lab 6 retrieval/LLM path

    def handle(self, msg: Message) -> Response:
        started = perf_counter()
        intent = route(msg.text, set(self.offices.names))

        if intent is Intent.GREETING:
            response = Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=intent,
            )
        elif intent is Intent.HELP:
            response = Response(
                answer="I can help with greetings, office locations, tuition fees, and handbook rules.",
                intent=intent,
            )
        elif intent is Intent.FEE:
            response = self._handle_fee(msg.text)
        elif intent is Intent.OFFICE:
            response = self._handle_office(msg.text)
        else:
            response = self._handle_rule(msg.text)

        logger.info(
            "handled",
            extra={
                "intent": response.intent.value,
                "latency_ms": round((perf_counter() - started) * 1000, 2),
                "session": msg.session_id,
                "degraded": response.degraded,
            },
        )
        return response

    def _handle_fee(self, text: str) -> Response:
        try:
            credits, retake = parse_credits(text)
            amount = tuition(
                credits=credits,
                retake=retake,
                rate=self.settings.credit_rate_vnd,
                retake_multiplier=self.settings.retake_multiplier,
                max_credits=self.settings.max_credits,
            )
        except InvalidRequest as exc:  # e.g. "when is tuition due" has no credit count
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(
            answer=f"Your tuition is {amount:,} VND",
            intent=Intent.FEE,
        )

    def _handle_office(self, text: str) -> Response:
        query = text.casefold()
        matched_name = next(
            (name for name in self.offices.names if name.casefold() in query),
            None,
        )
        office = self.offices.find(matched_name) if matched_name else None
        if office is None:
            return Response(
                answer="Sorry, I could not find that office.",
                intent=Intent.UNKNOWN,
            )

        return Response(
            answer=f"{office.name}: room {office.room}, open {office.hours}.",
            intent=Intent.OFFICE,
        )

    def _handle_rule(self, text: str) -> Response:
        if self.rag is not None:  # Lab 6: guard first, then retrieval + LLM with abstain
            if is_private_request(text):
                return Response(answer=PRIVATE_REPLY, intent=Intent.UNKNOWN, path="abstain")
            return self.rag.answer(text)
        rule = self.handbook.search(text)
        if rule is None:
            return Response(
                answer="Sorry, I don't know that yet.",
                intent=Intent.UNKNOWN,
            )

        sources = [Source(id=rule.id, title=rule.title)]
        try:
            answer = self.responder.explain(text, rule)
        except ProviderError:
            logger.warning(
                "provider failed; using template fallback",
                extra={"degraded": True},
            )
            answer = self.fallback.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=True,
            )

        return Response(answer=answer, intent=Intent.RULE, sources=sources)


def build_service(settings: Settings | None = None) -> AssistantService:
    """Build the service from settings (read from the environment when not given)."""
    settings = settings or load_settings()
    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")

    if settings.llm_provider == "stub":
        responder: Responder = StubLLMResponder()
    elif settings.llm_provider == "template":
        responder = TemplateResponder()
    else:
        raise ConfigError(f"Unsupported LLM_PROVIDER: {settings.llm_provider!r}")

    return AssistantService(settings=settings, offices=offices, handbook=handbook, responder=responder)
