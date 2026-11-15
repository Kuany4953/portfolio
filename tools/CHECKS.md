# Week 8 checks: one tool

**What the chatbot answers from:** the chatbot still answers from the course's example profile (Sam Rivera), as `voice/CHECKS.md` records. The tool, `recent_commits`, reads **my** public repositories (`Kuany4953`). The system prompt tells the model both facts. My own profile replaces the example before November 30.

## Step 3: tests first, with a scripted model

Every step was committed red, then green: `git log --oneline` shows each `(red)` commit before its code.

| Step | Red | Green |
|---|---|---|
| Registry and GitHub tool (`test_registry.py`) | `ImportError: cannot import name 'github_tool'`, 1 error in collection | 26 passed |
| Claim check (`test_claims.py`) | `ModuleNotFoundError: tools.claims`, 1 error in collection | 37 passed (26 + 11) |
| Loop, the six misuse cases (`test_tool_loop.py`) | `ModuleNotFoundError: tools.tool_loop`, 1 error in collection | 49 passed (37 + 12) |

**Changes made while writing the code:**
- **A SHA must contain a digit and a letter.** The spec says "a 7-character hex string". Without this rule, ordinary words made only of the letters a–f, such as "acceded", would be flagged (`test_ordinary_hex_looking_words_are_not_shas`).
- **The cap sentence uses the `max_steps` actually passed in**, not a fixed 4.
- **`test_loop.py` renamed to `test_tool_loop.py`.** Run together with `voice/tests`, pytest stopped with "import file mismatch": `voice/tests/test_loop.py` has the same basename. After the rename, `pytest tools/tests voice/tests` gives **137 passed**.

All runs used `env -u OPENROUTER_API_KEY`: no key, no network (GitHub is faked), well under a second.

## Lint

`ruff check .` (ruff 0.17.4):
- **First run:** 3 findings.
  - **FURB167**, twice: `re.I` instead of `re.IGNORECASE` in `tools/claims.py`. Fixed with `--fix`.
  - **PIE810** in `.claude/hooks/guard.py:28`: "call startswith once with a tuple". That is the Week 5 guard hook, not this week's code. I left it unchanged, because the hook's behavior is what the guard tests rely on.
- **Now:** 1 finding, the pre-existing PIE810 in the hook. `tools/` is clean.
