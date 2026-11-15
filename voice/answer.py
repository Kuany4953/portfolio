"""The chatbot's answer function. The typed path (/api/ask) and the voice path (/api/voice) both call it.

Since Week 8 every answer goes through the tool loop (tools/tool_loop.py, spec §13): the model may
ask for recent_commits (my public GitHub repositories) or request_intro (held, never run), our code
validates and runs or refuses each request, and the loop stops at four steps. The trace comes back
with the answer.

The profile is still the course example's (voice/example-profile.json, copied from
examples/voice-loop/profile.json), as voice/CHECKS.md and tools/CHECKS.md say. Swap in my own
before November 30.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))     # the repository root, for tools/

from tools.tool_loop import MAX_STEPS, run

PROFILE_PATH = Path(__file__).parent / "example-profile.json"
CHAT_MODEL = os.environ.get("CHAT_MODEL", "minimax/minimax-m3")

RULES = """You answer a visitor's questions on Kuany Kuany's portfolio site.
- The PROFILE below is a placeholder: the course's example person, until Kuany's own profile is added.
  Answer questions about that profile from it and nothing else.
- Shipped work is in "projects" and "skills_shipped". Anything in "not_yet" is something the person has
  not done yet: say "not yet" and give the reason the profile records.
- If the profile does not cover the question, say plainly "My profile doesn't say." Do not guess.
- Never claim experience, numbers, employers, or dates the profile does not record.
- If a name or word in the question is not in the profile, do not invent anything about it.

TOOLS
- recent_commits reads Kuany Kuany's public GitHub repositories (owner Kuany4953). Call it before saying
  anything about Kuany's recent work or any repository. Report only the commits, dates and messages it
  returns. If it says a repository does not exist, say there is no public repository by that name.
  If it returns an error, say you could not look it up. Never guess a commit, a date, or a repository.
- request_intro: only when the visitor explicitly asks to be introduced and gives an email. It is held
  until Kuany confirms; tell the visitor that Kuany has to confirm before anything is sent.
- Do not mention the tools by name."""

SPOKEN = """
This answer will be read aloud: at most three sentences, plain text, no markdown, no lists, no URLs."""


def system_prompt(spoken: bool) -> str:
    profile = json.loads(PROFILE_PATH.read_text())
    return RULES + (SPOKEN if spoken else "") + "\n\nPROFILE:\n" + json.dumps(profile, indent=1)


def answer_turn(client, question: str, spoken: bool = False, model: str | None = None) -> dict:
    """One question through the tool loop: {"answer", "trace", "stopped_by", "cost", "pending", "check", "model"}."""
    return run(client, system_prompt(spoken), question, model=model or CHAT_MODEL, max_steps=MAX_STEPS)


def answer(client, question: str, spoken: bool = False) -> tuple[str, float | None]:
    """The (text, cost) pair voice_turn expects; the trace is in answer_turn."""
    r = answer_turn(client, question, spoken)
    return r["answer"], r["cost"]
