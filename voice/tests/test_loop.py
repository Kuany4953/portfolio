"""No-key tests for one voice turn (spec.md §12.4 behaviors 2, 6, 10).

The three billed steps are fakes, so these prove the wiring: who is called,
how often, with what, and what comes back.
"""
import base64

import pytest
from loop import voice_turn
from speak import NotAudio


class Fakes:
    def __init__(self, heard="What did Kuany build at Clasona?",
                 typed="**Kuany** built an agent for Vesoko. It writes descriptions. It ships. A fourth.",
                 speech=b"ID3fake-mp3", speak_error=None):
        self.heard, self.typed, self.speech, self.speak_error = heard, typed, speech, speak_error
        self.answer_calls, self.speak_calls = [], []

    def transcribe(self, audio, fmt):
        return {"text": self.heard, "cost": 0.00002, "seconds": 0.5}

    def answer(self, question):
        self.answer_calls.append(question)
        return self.typed, 0.0001

    def speak(self, text):
        self.speak_calls.append(text)
        if self.speak_error:
            raise self.speak_error
        return self.speech, 0.0007


def turn(f):
    return voice_turn(b"audio", "webm", f.transcribe, f.answer, f.speak)


def test_a_turn_answers_through_the_answer_function_once_and_speaks_once():
    f = Fakes()
    turn(f)
    assert f.answer_calls == ["What did Kuany build at Clasona?"]
    assert len(f.speak_calls) == 1


def test_what_is_spoken_is_the_shaped_answer():
    f = Fakes()
    r = turn(f)
    assert f.speak_calls[0] == "Kuany built an agent for Vesoko. It writes descriptions. It ships."
    assert r["answer"] == f.speak_calls[0]        # what the visitor reads is what they hear


def test_response_shape_and_costs():
    r = turn(Fakes())
    assert r["transcript"] == "What did Kuany build at Clasona?"
    assert base64.b64decode(r["audio"]) == b"ID3fake-mp3"
    assert r["costs"]["transcribe"] == 0.00002
    assert r["costs"]["answer"] == 0.0001
    assert r["costs"]["speak"] == 0.0007
    assert r["costs"]["total"] == pytest.approx(0.00082)


@pytest.mark.parametrize("heard", ["", "   ", "um", "hello there", None])
def test_under_three_words_is_not_answered_and_nothing_is_spoken(heard):
    f = Fakes(heard=heard)
    r = turn(f)
    assert f.answer_calls == [] and f.speak_calls == []
    assert r["answer"] == "I didn't catch that."
    assert r["audio"] is None
    assert r["costs"]["answer"] == 0 and r["costs"]["speak"] == 0
    assert r["costs"]["total"] == pytest.approx(0.00002)


def test_failed_speech_still_returns_transcript_and_answer():
    f = Fakes(speak_error=NotAudio("expected audio, got application/json"))
    r = turn(f)
    assert r["audio"] is None
    assert "application/json" in r["speak_error"]
    assert r["transcript"] and r["answer"]
    assert r["costs"]["speak"] == 0


def test_unknown_cost_does_not_break_the_total():
    class NoCost(Fakes):
        def answer(self, question):
            self.answer_calls.append(question)
            return "Kuany built an agent.", None
    r = turn(NoCost())
    assert r["costs"]["answer"] is None
    assert r["costs"]["total"] == pytest.approx(0.00072)
