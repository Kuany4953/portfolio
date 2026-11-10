"""The chatbot's answer function. The typed path (/api/ask) and the voice path (/api/voice) both call it.

Until my profile.yaml and chatbot exist, this answers from the course example's
profile (voice/example-profile.json, copied from examples/voice-loop/profile.json),
as voice/CHECKS.md says. Swap in my own before November 30.
"""
import json
import os
from pathlib import Path

PROFILE_PATH = Path(__file__).parent / "example-profile.json"
CHAT_MODEL = os.environ.get("CHAT_MODEL", "anthropic/claude-haiku-5.5")

RULES = """You answer a visitor's questions about one person, from the profile below and nothing else.
- Shipped work is in "projects" and "skills_shipped". Anything in "not_yet" is something the person has
  not done yet: say "not yet" and give the reason the profile records.
- If the profile does not cover the question, say plainly "My profile doesn't say." Do not guess.
- Never claim experience, numbers, employers, or dates the profile does not record.
- If a name or word in the question is not in the profile, do not invent anything about it."""

SPOKEN = """
This answer will be read aloud: at most three sentences, plain text, no markdown, no lists, no URLs."""


def system_prompt(spoken: bool) -> str:
    profile = json.loads(PROFILE_PATH.read_text())
    return RULES + (SPOKEN if spoken else "") + "\n\nPROFILE:\n" + json.dumps(profile, indent=1)


def answer(client, question: str, spoken: bool = False) -> tuple[str, float | None]:
    """One chat call. Returns the answer text and its cost from usage."""
    c = client.chat.send(model=CHAT_MODEL, max_tokens=800, messages=[
        {"role": "system", "content": system_prompt(spoken)},
        {"role": "user", "content": question}])
    text = (c.choices[0].message.content or "").strip()
    if not text:        # an empty answer is a failed answer, said so, never spoken as if it were one
        text = "I couldn't put an answer together. Please ask again."
    return text, getattr(c.usage, "cost", None)
