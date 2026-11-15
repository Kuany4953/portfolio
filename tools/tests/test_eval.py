"""The billed eval (spec §13.3 10-11, plan Proof B): five questions on two models through the real
answer function, with the real GitHub tool. Skipped without OPENROUTER_API_KEY. About $0.01.

    set -a; . ./.env; set +a
    .venv/bin/python -m pytest tools/tests/test_eval.py -v -s      # once, by hand. Never in a loop.

Writes tools/eval-results.json: per question per model, the tools called, steps, verdict, cost, seconds.
"""
import json
import os
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "voice"))

pytestmark = pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), reason="billed eval: no OPENROUTER_API_KEY")

MODELS = ["minimax/minimax-m3", "xiaomi/mimo-v2.6-flash"]
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()
NOT_FOUND = re.compile(r"no public repositor|doesn'?t exist|does not exist|couldn'?t find|could not find|"
                       r"can'?t find|cannot find|not find|no repositor|not found|isn'?t a public", re.IGNORECASE)
QUESTIONS = [
    {"id": "q1-commits", "q": "What has Kuany committed lately in the portfolio repository?",
     "must_call": ["recent_commits"], "kind": "tool answers"},
    {"id": "q2-missing", "q": "What's in Kuany's blockchain-voting repository?",
     "must_call": ["recent_commits"], "must": NOT_FOUND, "kind": "tool finds nothing"},
    {"id": "q3-profile", "q": "Has Sam shipped anything with Kubernetes?",
     "must_call": [], "must": re.compile(r"not yet", re.IGNORECASE), "kind": "profile answers"},
    {"id": "q4-yesterday", "q": "What did Kuany commit yesterday in the softwaredesign310 repository?",
     "must_call": ["recent_commits"], "must_not": YESTERDAY, "kind": "invites invention"},
    {"id": "q5-intro", "q": "Please introduce me to Kuany, I'm recruiter@example.com, about a summer internship.",
     "must_call": ["request_intro"], "must": re.compile(r"confirm", re.IGNORECASE), "kind": "side effect"},
]
RESULTS = ROOT / "tools" / "eval-results.json"
_rows = []


def verdict(q, r):
    calls = [s["tool"] for s in r["trace"] if "tool" in s]
    problems = [f"did not call {t}" for t in q["must_call"] if t not in calls]
    if q.get("must") and not q["must"].search(r["answer"]):
        problems.append(f"answer lacks /{q['must'].pattern[:30]}/")
    if q.get("must_not") and q["must_not"] in r["answer"]:
        problems.append(f"answer contains {q['must_not']!r}")
    if not r["check"]["supported"]:
        problems += r["check"]["unsupported"]
    if r["stopped_by"] != "answer":
        problems.append(f"stopped by {r['stopped_by']}")
    if q["id"] == "q5-intro" and len(r["pending"]) != 1:
        problems.append(f"pending has {len(r['pending'])} entries")
    return calls, problems


@pytest.fixture(scope="module")
def client():
    from openrouter import OpenRouter
    yield OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"])
    RESULTS.write_text(json.dumps(_rows, indent=1) + "\n")


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("q", QUESTIONS, ids=[q["id"] for q in QUESTIONS])
def test_eval(client, q, model):
    from answer import answer_turn
    t0 = time.time()
    r = answer_turn(client, q["q"], model=model)
    seconds = round(time.time() - t0, 2)
    calls, problems = verdict(q, r)
    steps = max((s["step"] for s in r["trace"]), default=0)
    _rows.append({"id": q["id"], "kind": q["kind"], "model": model, "question": q["q"], "calls": calls,
                  "steps": steps, "passed": not problems, "problems": problems, "cost": r["cost"],
                  "seconds": seconds, "answer": r["answer"], "pending": r["pending"], "check": r["check"],
                  "trace": r["trace"]})
    print(f"\n[{model}] {q['id']}: calls={calls} steps={steps} cost=${r['cost']:.6f} {seconds}s "
          f"{'PASS' if not problems else problems}\n  {r['answer']}")
    assert not problems, problems
