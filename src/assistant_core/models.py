from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"
    HELP = "help"


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"


class Source(BaseModel):
    id: str
    title: str


class Response(BaseModel):
    answer: str
    intent: Intent
    sources: list[Source] = Field(default_factory=list)
    degraded: bool = False  # True when a fallback path was used
    # Lab 6 - AI services
    escalate: bool = False  # True when the assistant abstained and suggests a human
    path: str = "deterministic"  # deterministic | retrieval | llm | tool | abstain
    confidence: float | None = None
