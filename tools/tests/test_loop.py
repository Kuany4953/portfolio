"""No-key tests for the loop with a scripted model: the six misuse cases (spec §13.3 5-10).

The fake client returns whatever replies the test scripted, in order, and raises if the loop
asks for more. So each test says exactly what the model "did" and checks what the program did.
GitHub is faked too.
"""
import copy
import json
from types import SimpleNamespace as NS

import pytest

from tools import github_tool, registry
from tools.tool_loop import CAP_ANSWER, CONFIRM_NOTE, run


def tool_call(name, arguments, call_id="call_1", cost=0.0001):
    tc = NS(id=call_id, function=NS(name=name, arguments=arguments))
    return NS(choices=[NS(message=NS(content="", tool_calls=[tc]), finish_reason="tool_calls")],
              usage=NS(cost=cost))


def answer(text, cost=0.0001):
    return NS(choices=[NS(message=NS(content=text, tool_calls=None), finish_reason="stop")], usage=NS(cost=cost))


class FakeClient:
    def __init__(self, replies):
        self.replies, self.sent, self.kwargs = list(replies), [], []

    @property
    def chat(self):
        return self

    def send(self, **kwargs):
        self.sent.append(copy.deepcopy(kwargs["messages"]))
        self.kwargs.append({k: v for k, v in kwargs.items() if k != "messages"})
        if not self.replies:
            raise AssertionError("the loop asked the model again after the script ran out")
        return self.replies.pop(0)


COMMITS = {"repo": "Kuany4953/portfolio", "found": True,
           "commits": [{"sha": "36cb8bd", "date": "2026-11-10", "message": "Voice: record skipped step 5a"}]}


@pytest.fixture(autouse=True)
def fake_github(monkeypatch):
    calls = []

    def fake(repo, count=5, fetch=None):
        calls.append(repo)
        return COMMITS if repo in ("portfolio", "Kuany4953/portfolio") else {
            "error": f"no public repository named 'Kuany4953/{repo}'", "repo": f"Kuany4953/{repo}", "found": False}
    monkeypatch.setattr(github_tool, "recent_commits", fake)
    return calls


def go(fake, question="What has Kuany committed lately?", **kw):
    return run(fake, "SYSTEM", question, model="minimax/minimax-m3", **kw)


# 1. single shot ------------------------------------------------------------------------------------
def test_single_shot_result_goes_back_as_a_tool_message_with_the_right_id():
    fake = FakeClient([tool_call("recent_commits", '{"repo": "portfolio"}', "call_abc"),
                       answer("Kuany's latest portfolio commit, on 2026-11-10, recorded a skipped step.")])
    r = go(fake)
    second = fake.sent[1]
    assert second[-2] == {"role": "assistant", "content": "",
                          "tool_calls": [{"id": "call_abc", "type": "function",
                                          "function": {"name": "recent_commits", "arguments": '{"repo": "portfolio"}'}}]}
    assert second[-1]["role"] == "tool" and second[-1]["tool_call_id"] == "call_abc"
    assert json.loads(second[-1]["content"]) == COMMITS
    assert r["stopped_by"] == "answer" and r["check"]["supported"] and r["pending"] == []
    assert [s.get("tool") for s in r["trace"]] == ["recent_commits", None]
    assert abs(r["cost"] - 0.0002) < 1e-12
    assert fake.kwargs[0]["tools"] == registry.TOOLS            # the schema goes with every request


def test_no_tool_needed_is_one_call():
    fake = FakeClient([answer("Ask me about Kuany's repositories.")])
    r = go(fake, "Hi")
    assert len(fake.sent) == 1 and r["trace"] == [r["trace"][0]] and "tool" not in r["trace"][0]


# 2. bad arguments ------------------------------------------------------------------------------------
def test_wrong_argument_name_gets_the_exact_error_and_the_loop_continues(fake_github):
    fake = FakeClient([tool_call("recent_commits", '{"name": "portfolio"}', "c1"),
                       tool_call("recent_commits", '{"repo": "portfolio"}', "c2"),
                       answer("Kuany's latest portfolio commit was on 2026-11-10.")])
    r = go(fake)
    assert fake.sent[1][-1] == {"role": "tool", "tool_call_id": "c1",
                                "content": json.dumps({"error": "missing required argument 'repo'"})}
    assert fake_github == ["portfolio"]                       # the bad call never reached GitHub
    assert r["stopped_by"] == "answer" and len(fake.sent) == 3 and r["check"]["supported"]


def test_arguments_that_are_not_json_get_an_error_result():
    fake = FakeClient([tool_call("recent_commits", '{"repo": portf'), answer("Sorry, I couldn't look that up.")])
    go(fake)
    assert json.loads(fake.sent[1][-1]["content"])["error"].startswith("arguments were not valid JSON")


# 3. unknown tool ---------------------------------------------------------------------------------------
def test_a_tool_that_does_not_exist_gets_an_error_result():
    fake = FakeClient([tool_call("get_resume", "{}"), answer("I can't get a resume, but I can show recent commits.")])
    r = go(fake, "Send me Kuany's resume")
    assert json.loads(fake.sent[1][-1]["content"]) == {
        "error": "unknown tool 'get_resume'; the tools are ['recent_commits', 'request_intro']"}
    assert r["stopped_by"] == "answer"


# 4. endless caller ---------------------------------------------------------------------------------------
def test_a_model_that_asks_forever_is_stopped_by_the_cap_and_the_answer_is_the_programs():
    fake = FakeClient([tool_call("recent_commits", '{"repo": "portfolio"}', f"c{i}") for i in range(10)])
    r = go(fake)
    assert len(fake.sent) == 4                                 # no fifth call was billed
    assert r["stopped_by"] == "cap" and r["answer"] == CAP_ANSWER
    assert CAP_ANSWER == "I couldn't finish answering that in 4 steps. Please try a simpler question."
    assert [s["tool"] for s in r["trace"]] == ["recent_commits"] * 4
    assert abs(r["cost"] - 0.0004) < 1e-12


# 5. side effect held ---------------------------------------------------------------------------------------
def test_a_side_effect_is_pending_and_does_not_happen(monkeypatch):
    sent = []
    monkeypatch.setitem(registry.FUNCTIONS, "request_intro", lambda **kw: sent.append(kw) or {"sent": True})
    fake = FakeClient([tool_call("request_intro", '{"email": "r@x.com", "message": "internship"}'),
                       answer("Thanks! I've passed that along.")])
    r = go(fake, "Introduce me to Kuany, I'm r@x.com, about an internship")
    assert sent == []
    assert r["pending"] == [{"tool": "request_intro", "arguments": {"email": "r@x.com", "message": "internship"}}]
    assert "confirmation" in json.loads(fake.sent[1][-1]["content"])["error"]
    assert r["answer"] == "Thanks! I've passed that along. " + CONFIRM_NOTE


def test_the_confirm_note_is_not_doubled_when_the_model_already_says_it(monkeypatch):
    fake = FakeClient([tool_call("request_intro", '{"email": "r@x.com", "message": "hi"}'),
                       answer("Noted. Kuany will need to confirm before anything is sent.")])
    assert go(fake)["answer"] == "Noted. Kuany will need to confirm before anything is sent."


# 6. unsupported claim ---------------------------------------------------------------------------------------
def test_an_answer_that_names_what_no_tool_returned_is_flagged():
    fake = FakeClient([tool_call("recent_commits", '{"repo": "blockchain-voting"}'),
                       answer("blockchain-voting got commit 9f3c2a1 on 2026-11-14, adding React.")])
    r = go(fake, "What's new in blockchain-voting?")
    assert not r["check"]["supported"]
    assert r["check"]["unsupported"] == [
        "commit '9f3c2a1' was not returned by a tool",
        "date '2026-11-14' was not returned by a tool",
        "repository 'blockchain-voting' was not found, but the answer does not say so"]
    assert r["answer"].startswith("blockchain-voting")           # flagged, still returned for a person to see


# the rest of §13.3 ----------------------------------------------------------------------------------------
def test_parallel_calls_each_get_a_result_in_order():
    tcs = [NS(id="a", function=NS(name="recent_commits", arguments='{"repo": "portfolio"}')),
           NS(id="b", function=NS(name="recent_commits", arguments='{"repo": "nope-repo"}'))]
    both = NS(choices=[NS(message=NS(content=None, tool_calls=tcs), finish_reason="tool_calls")], usage=NS(cost=None))
    fake = FakeClient([both, answer("portfolio has commits; there's no repository called nope-repo.")])
    r = go(fake)
    tool_msgs = [m for m in fake.sent[1] if m["role"] == "tool"]
    assert [m["tool_call_id"] for m in tool_msgs] == ["a", "b"]
    assert [s["step"] for s in r["trace"]] == [1, 1, 2] and r["check"]["supported"]


def test_an_empty_answer_becomes_the_programs_sentence():
    r = go(FakeClient([answer("   ")]))
    assert r["answer"] == "I couldn't put an answer together. Please ask again."


def test_mimo_gets_reasoning_off_and_m3_keeps_it():
    fake = FakeClient([answer("ok")])
    run(fake, "S", "q", model="xiaomi/mimo-v2.6-flash")
    assert fake.kwargs[0]["reasoning"] == {"enabled": False}
    fake = FakeClient([answer("ok")])
    run(fake, "S", "q", model="minimax/minimax-m3")
    assert "reasoning" not in fake.kwargs[0]
