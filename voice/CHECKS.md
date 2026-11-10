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

### Course clips (spoken by a model, the baseline)

Run 2026-11-10, one call per clip per model. The answer key is the course's
`examples/voice-loop/clips/expected.json`, used as is. Files:
`transcripts-course-whisper.json`, `transcripts-course-scribe.json`.

| Clip | Model | WER | Tolerance | Missing | Audio s | Cost | Call s | Verdict |
|---|---|---|---|---|---|---|---|---|
| clip-01 | whisper-large-v3-turbo | 0.000 | 0.15 | none | 6.38 | $0.0000212 | 1.2 | ok |
| clip-01 | scribe-v2 | 0.000 | 0.15 | none | 6.38 | $0.000390 | 0.8 | ok |
| clip-02 | whisper-large-v3-turbo | 0.176 | 0.20* | none | 8.06 | $0.0000268 | 0.6 | ok |
| clip-02 | scribe-v2 | 0.118 | 0.20* | none | 8.06 | $0.000493 | 0.9 | ok |
| clip-03 | whisper-large-v3-turbo | 0.000 | 0.15 | none | 7.71 | $0.0000257 | 0.7 | ok |
| clip-03 | scribe-v2 | 0.000 | 0.15 | none | 7.71 | $0.000471 | 0.7 | ok |

\* The course key raises clip-02 to 0.20, with a note explaining why.

- **Totals:** Whisper $0.00007 for 3 clips, Scribe $0.00135, so Scribe costs about 19× as much per audio second.
- **clip-02:** both models split "bootcamp" into "boot camp". The must-survive check still passes, because spacing doesn't count. Whisper also added "Music" after the last word, which is the hallucination on trailing silence that the course key's note describes, reproduced here. That makes 3 edits in 17 words for Whisper. Scribe didn't add anything.
- "CPSC 415" survived on both models on clip-03, written as digits.

### My own clips

_(step 4: waiting for my recordings and my `expected.json`)_

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
