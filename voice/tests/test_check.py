"""No-key tests for the transcript checker (spec.md §12.4, behaviors 1, 4, 5).

Every transcript here is hand-written. No model is called.
"""
import pytest
from check import TOLERANCE, check_clip, missing_words, wer

# Thirteen words.
THIRTEEN = "My name is Kuany Kuany and I am taking CPSC 415 at Trinity"
# Eleven words, "Kuany" once.
ONE_NAME = "Kuany built the AI agent for Vesoko at Clasona last summer"


# --- word error rate -------------------------------------------------------

def test_perfect_transcript_scores_zero():
    assert wer(THIRTEEN, THIRTEEN) == 0.0


def test_one_substitution_in_thirteen_scores_one_thirteenth():
    got = THIRTEEN.replace("taking", "making")
    assert wer(THIRTEEN, got) == pytest.approx(1 / 13)


def test_deletion_and_insertion_each_count():
    deleted = THIRTEEN.replace(" at Trinity", " Trinity")
    inserted = THIRTEEN + " College"
    assert wer(THIRTEEN, deleted) == pytest.approx(1 / 13)
    assert wer(THIRTEEN, inserted) == pytest.approx(1 / 13)


def test_case_and_punctuation_do_not_count_toward_wer():
    got = "my name is kuany kuany, and i am taking cpsc 415 at trinity."
    assert wer(THIRTEEN, got) == 0.0


def test_tolerance_is_the_spec_value():
    assert TOLERANCE == 0.15


# --- the empty reply --------------------------------------------------------

@pytest.mark.parametrize("got", ["", "   \n", None])
def test_empty_reply_scores_one_and_is_reported_not_raised(got):
    result = check_clip(THIRTEEN, got, ["Kuany", "CPSC 415"])
    assert result["wer"] == 1.0
    assert result["empty"] is True
    assert result["passed"] is False
    assert result["missing"] == ["Kuany", "CPSC 415"]


# --- words that must survive -----------------------------------------------

def test_missing_name_is_reported_even_within_tolerance():
    got = ONE_NAME.replace("Kuany", "Kwani")
    result = check_clip(ONE_NAME, got, ["Kuany", "Vesoko"])
    assert result["wer"] <= TOLERANCE
    assert result["missing"] == ["Kuany"]
    assert result["passed"] is False


def test_number_read_as_words_is_a_miss():
    got = THIRTEEN.replace("CPSC 415", "CPSC four fifteen")
    assert missing_words(["CPSC 415"], got) == ["CPSC 415"]


@pytest.mark.parametrize("got", ["I take cpsc415 now", "I take CPSC 415 now", "I take Cpsc  415 now"])
def test_spacing_and_case_do_not_count_for_named_words(got):
    assert missing_words(["CPSC 415"], got) == []


def test_a_different_word_is_a_miss():
    assert missing_words(["Clasona"], "I worked at Classona") == ["Clasona"]


def test_clean_transcript_passes():
    result = check_clip(THIRTEEN, THIRTEEN, ["Kuany", "CPSC 415"])
    assert result == {"wer": 0.0, "missing": [], "empty": False, "passed": True}
