import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.tools import parse_credits, tuition


def test_parse_with_retake():
    assert parse_credits("tuition for 18 credits and 2 retake") == (18, 2)


def test_parse_without_retake():
    assert parse_credits("fee for 12 credits") == (12, 0)


def test_parse_uppercase():
    assert parse_credits("TUITION FOR 18 CREDITS AND 2 RETAKE") == (18, 2)


def test_parse_retake_first():
    assert parse_credits("2 retake and 18 credits") == (18, 2)


def test_parse_same_number_for_credits_and_retake():
    assert parse_credits("fee for 2 credits and 2 retake") == (2, 2)


def test_parse_zero_is_parsed_not_validated():
    assert parse_credits("fee for 0 credits") == (0, 0)


@pytest.mark.parametrize("text", ["what is the tuition", "", "tuition and 2 retake"])
def test_parse_no_credits_raises(text):
    with pytest.raises(InvalidRequest):
        parse_credits(text)


def test_tuition_value():
    assert tuition(18, 2, 450_000, 1.5, 30) == 9_450_000  # same as the monolith


def test_tuition_no_retake():
    assert tuition(18, 0, 450_000, 1.5, 30) == 8_100_000


def test_tuition_boundaries_ok():
    assert tuition(1, 0, 450_000, 1.5, 30) == 450_000
    assert tuition(30, 0, 450_000, 1.5, 30) == 13_500_000


@pytest.mark.parametrize("credits", [0, -1, 31])
def test_tuition_out_of_range(credits):
    with pytest.raises(InvalidRequest):
        tuition(credits, 0, 450_000, 1.5, 30)


def test_tuition_respects_max_credits_argument():
    assert tuition(10, 0, 450_000, 1.5, 10) == 4_500_000
    with pytest.raises(InvalidRequest):
        tuition(11, 0, 450_000, 1.5, 10)


def test_parse_then_tuition_end_to_end():
    credits, retake = parse_credits("Tuition for 18 credits and 2 retake?")
    assert tuition(credits, retake, 450_000, 1.5, 30) == 9_450_000
