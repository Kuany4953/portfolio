"""No-key tests: the chatbot's answer function goes through the tool loop and returns the trace
(spec §13.3 9). The typed path (/api/ask) and the voice path (/api/voice) both carry it."""
import copy
from types import SimpleNamespace as NS

import pytest

import answer as answer_mod
import web
from tools import github_tool

COMMITS = {"repo": "Kuany4953/portfolio", "found": True,
           "commits": [{"sha": "36cb8bd", "date": "2026-11-10", "message": "Voice: record skipped step 5a"}]}


def tool_call(name, arguments, call_id="call_1"):
    tc = NS(id=call_id, function=NS(name=name, arguments=arguments))
    return NS(choices=[NS(message=NS(content="", tool_calls=[tc]), finish_reason="tool_calls")], usage=NS(cost=0.0001))


def reply(text):
    return NS(choices=[NS(message=NS(content=text, tool_calls=None), finish_reason="stop")], usage=NS(cost=0.0001))


class FakeClient:
    def __init__(self, replies):
        self.replies, self.sent = list(replies), []

    @property
    def chat(self):
        return self

    def send(self, **kwargs):
        self.sent.append(copy.deepcopy(kwargs))
        return self.replies.pop(0)


@pytest.fixture(autouse=True)
def fake_github(monkeypatch):
    monkeypatch.setattr(github_tool, "recent_commits", lambda repo, count=5, fetch=None: COMMITS)


def script():
    return FakeClient([tool_call("recent_commits", '{"repo": "portfolio"}'),
                       reply("Kuany's latest portfolio commit, on 2026-11-10, recorded a skipped step.")])


def test_answer_turn_goes_through_the_loop_and_returns_the_trace():
    fake = script()
    r = answer_mod.answer_turn(fake, "What has Kuany committed lately?")
    assert r["stopped_by"] == "answer" and r["check"]["supported"]
    assert r["trace"][0]["tool"] == "recent_commits" and r["trace"][0]["result"] == COMMITS
    assert fake.sent[0]["model"] == answer_mod.CHAT_MODEL == "minimax/minimax-m3"
    system = fake.sent[0]["messages"][0]["content"]
    assert "PROFILE:" in system and "Kuany4953" in system and "recent_commits" in system
    assert fake.sent[0]["tools"]                                   # the schema goes with the request


def test_the_loop_is_capped_at_four_steps():
    fake = FakeClient([tool_call("recent_commits", '{"repo": "portfolio"}', f"c{i}") for i in range(4)])
    r = answer_mod.answer_turn(fake, "loop forever")
    assert r["stopped_by"] == "cap" and len(fake.sent) == 4


def test_answer_still_returns_text_and_cost_for_the_voice_turn():
    text, cost = answer_mod.answer(script(), "What has Kuany committed lately?")
    assert text.startswith("Kuany's latest") and abs(cost - 0.0002) < 1e-12


def test_spoken_adds_the_spoken_instruction():
    fake = FakeClient([reply("ok")])
    answer_mod.answer_turn(fake, "hi", spoken=True)
    assert "read aloud" in fake.sent[0]["messages"][0]["content"]


def test_typed_path_returns_trace_pending_and_check():
    out = web.ask_payload(script(), "What has Kuany committed lately?")
    assert out["answer"].startswith("Kuany's latest") and out["audio"] is None
    assert out["trace"][0]["tool"] == "recent_commits" and out["pending"] == [] and out["check"]["supported"]
    assert abs(out["costs"]["answer"] - 0.0002) < 1e-12


def test_voice_path_returns_the_trace_and_speaks_only_the_answer(monkeypatch):
    spoken_text = []
    monkeypatch.setattr(web, "transcribe", lambda c, a, f: {"text": "What has Kuany committed lately?", "cost": 0.00002})

    def fake_speak(c, text, out):
        spoken_text.append(text)
        out.write_bytes(b"ID3fake")
        return {"cost": 0.003}
    monkeypatch.setattr(web, "speak", fake_speak)
    out = web.run_voice(script(), b"audio", "webm")
    assert out["trace"][0]["tool"] == "recent_commits" and out["check"]["supported"]
    assert spoken_text == [out["answer"]] and "recent_commits" not in out["answer"]
