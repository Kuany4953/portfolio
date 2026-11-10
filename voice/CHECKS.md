# Week 7 checks: spoken interface

> **Answer source:** my chatbot and `profile.yaml` do not exist yet. The loop
> answers from the course example's `profile.json` and answer step
> (`examples/voice-loop/`). Mine are swapped in before November 30.

## Linter

`ruff check .` (ruff 0.17.4), run after the checker's first green run (15 passed):

| Finding | File | What I did |
|---|---|---|
| I001: import block un-sorted (ruff treats `check` as third-party) | `voice/tests/test_check.py:5` | Applied `ruff --fix`. |
| PIE810: call `startswith` once with a tuple | `.claude/hooks/guard.py:28` | Left as is. It's the course-supplied guard, and the finding is style, not a bug. |
| FURB167 ×3: regex alias `re.S` / `re.M` | `voice/shape.py` | Applied `ruff --fix` (now `re.DOTALL` / `re.MULTILINE`). 34 tests still pass. |

## Transcripts: per clip per model

_(step 4)_

## Which model got my name right

_(step 4)_

## The answer, spoken

_(step 5)_

## Misheard questions

_(step 5a)_

## Browser check

_(step 6)_

## One turn

_(step 6)_
