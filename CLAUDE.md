# CLAUDE.md

Portfolio site and chatbot for Kuany Kuany (CPSC 415). The source of truth is
`intent/` and `spec.md`; `plan.md` holds the approved plan for each week.

## Working rules

- No API key in the repository. The OpenRouter key lives in the environment
  (locally) and in the host's environment variables (deployed).
- `.claude/hooks/guard.py` blocks edits to answer keys (`expected.json`),
  destructive git/rm commands, and installs of packages `spec.md` does not name.
- Week 7: the spoken interface lives in voice/. Stages assigned: intent, spec,
  plan, tests. Commit to main.
- Transcription and speech calls are billed. One transcription per clip, one
  speech call per answer, never a model call inside a loop of tests. Fixture
  clips are WAV; expected.json is written by a person before the model hears it.
- The spoken answer is the chatbot's answer: the refuse-to-fabricate rule
  applies to what is said aloud exactly as to what is typed.
