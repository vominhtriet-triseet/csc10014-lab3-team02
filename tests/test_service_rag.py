"""Lab 6 Part F: AssistantService wired to the RAG answerer (the setup eval/compare_paths.py uses)."""

from pathlib import Path

import pytest

from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.llm import StubLLM
from assistant_core.models import Intent, Message
from assistant_core.rag.answerer import RagAnswerer
from assistant_core.rag.chunker import load_folder
from assistant_core.rag.index import make_index
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService

DATA = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def index():
    return make_index("bm25", load_folder(DATA / "kb"))


def make_service(settings, rag):
    offices = OfficeDirectory.from_csv(DATA / "offices.csv")
    handbook = Handbook.from_json(DATA / "handbook.json")
    return AssistantService(settings, offices, handbook, TemplateResponder(), rag)


@pytest.mark.parametrize(("llm", "path"), [(None, "retrieval"), (StubLLM(), "llm")])
def test_rule_question_goes_through_rag(settings, index, llm, path):
    r = make_service(settings, RagAnswerer(index, llm)).handle(Message(text="I lost my student card"))
    assert r.path == path and r.sources[0].id == "S26#3"


def test_out_of_scope_question_abstains(settings, index):
    r = make_service(settings, RagAnswerer(index, StubLLM())).handle(Message(text="what is the capital of France"))
    assert r.path == "abstain" and r.escalate and r.intent is Intent.UNKNOWN


def test_privacy_guard_runs_before_retrieval(settings, index):
    r = make_service(settings, RagAnswerer(index, StubLLM())).handle(Message(text="what grade did my friend get"))
    assert r.path == "abstain" and not r.sources


def test_fee_question_without_credits_does_not_crash(settings, index):
    r = make_service(settings, RagAnswerer(index, None)).handle(Message(text="when is tuition due"))
    assert r.intent is Intent.FEE and r.answer == "How many credits?"


def test_without_rag_the_lab3_handbook_path_is_kept(settings):
    r = make_service(settings, None).handle(Message(text="can I register my thesis"))
    assert r.path == "deterministic" and r.intent is Intent.RULE
