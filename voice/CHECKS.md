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

`voice/test_browser.py`, adapted from the course example, run 2026-11-10 against
`voice/server.py` on localhost (Playwright 1.65, headless Chromium). It uploads
course clip-02 through the page's file picker. **1 passed in 9.8 s.**

The page showed:

> You said: Have you ever deployed anything with Kubernetes? Be honest, I'm comparing you with a boot camp graduate. Music
>
> Answer: Not yet. The profile says no project has needed more than one server, so Kubernetes hasn't come up, and Sam would expect to learn it on the job. The profile doesn't mention music, so I can't say anything about that.
>
> [transcribe $0.000027 · answer $0.00018 · speak $0.0032 · total $0.0034]

The last three assertions, read out:
1. `all(auth is None for _, auth in requests)`: no request from the browser carried an Authorization header.
2. `all("openrouter" not in url for url, _ in requests)`: the browser never contacted the provider.
3. `any(url.endswith("/api/voice") for url, _ in requests)`: it contacted our server, which holds the key.

The earlier assertions also passed: no `sk-or` or "openrouter" in the page HTML, the "You said:" line shows the transcript with "Kubernetes" in it, the answer is real (not the fallback), and audio came back.

**What I judged myself:** the answer is honest. It says "not yet" and gives the profile's reason. Whisper's hallucinated "Music" (see clip-02 above) reached the chatbot as part of the question. The chatbot refused to invent anything about it ("The profile doesn't mention music"), so the refuse-to-fabricate rule held on a misheard word. But the visitor *hears* that odd sentence, and the "You said:" line is what explains it. Models: transcription `openai/whisper-large-v3-turbo`, chat `anthropic/claude-haiku-5.5`, speech `microsoft/mai-voice-2.1-flash` / `en-IN-Priya`.

Free refusal checks with curl, same server, none of them billed:

| Request | Reply |
|---|---|
| `GET /api/voice` | 405 "POST only" |
| `text/plain` body | 415 unsupported audio type |
| empty `audio/webm` | 400 "empty recording" |
| 600 KB of `audio/webm` | 413 "compressed recording over 512 KB" |
| 5 MB `audio/wav` | 413 (refused before the body was read) |
| page HTML | 0 matches for `sk-or` or "openrouter" |

## One turn

_(step 6)_
