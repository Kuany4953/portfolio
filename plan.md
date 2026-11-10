# Plan

## Week 7: spoken interface

> **Source:** `spec.md` §12 and `intent/voice.md`.
> **Approved by:** _(Kuany kuany , 10/11/2026)_

### Files under voice/

| File | What it holds | Spec |
|---|---|---|
| `voice/check.py` | `wer(expected, got)`, `missing_words(must_survive, got)`, `check_clip(...)`. Pure functions, no network. | §12.4 (1, 4, 5) |
| `voice/shape.py` | `spoken(text)`: strips markdown and URLs and keeps at most three sentences. `is_audio(content_type, data)`. Pure functions, no network. | §12.4 (3, 6) |
| `voice/transcribe.py` | CLI and function. Uses `--set clips/expected.json`, `--model`, `--out`, `--language`, makes one transcription call per clip, and writes the text, audio seconds, cost and call time. | §12.2 |
| `voice/speak.py` | CLI and function. Uses `--text`/`--from`, `--model`, `--voice`, `--out`, makes one speech call, refuses non-audio, and records characters, bytes, estimated cost and call time. | §12.3 |
| `voice/tests/test_check.py` | No-key tests for the checker. | §12.4 (1, 4, 5) |
| `voice/tests/test_shape.py` | No-key tests for the spoken shape and the audio check. | §12.4 (3, 6) |
| `voice/tests/test_limits.py` | No-key tests for the request limits: a 16.5 s WAV → 413, a 10 s WAV → accepted, 600 KB of WebM → 413, `text/plain` → 415. | §12.4 (9) |
| `voice/tests/test_live.py` | Billed smoke tests: one transcription and one speech call. Skipped when `OPENROUTER_API_KEY` is unset. | §12.4 (11) |
| `voice/clips/` | My two WAV clips, the three course clips, and `expected.json` (written by me before any model hears a clip). | §12.4 (12) |
| `voice/transcripts-whisper.json`, `voice/transcripts-scribe.json` | Output of the two transcription runs. | §12.2 |
| `voice/answer-mai.wav`, `voice/answer-eleven.*` | The first clip's answer, spoken in the two voices. | §12.3 |
| `voice/CHECKS.md` | All recorded results: per clip per model, the name check, the two voices, ruff, the browser check, and One turn. | §12.5 |
| `api/voice.py` | `POST /api/voice`. Checks the size cap and type, then transcribes, answers through the typed path's function, shapes the answer, speaks it, and returns JSON. | §12.4 (2, 8, 9, 10) |
| `index.html` (recorder) | Record and stop with a 15 s auto-stop, a file-picker fallback, and "You said: …" above the answer. | §12.4 (8, 9, 10) |
| `voice/test_browser.py` | The course browser check, adapted to my page. | Lab step 6 |

Until my chatbot exists, `api/voice.py` imports the answer step and `profile.json` from `examples/voice-loop/`, and `CHECKS.md` says so.

### Order of work

Each step follows the same pattern: write the tests, run them and watch them fail, write the code, run them and watch them pass, then stop for review.

1. **Checker:** `test_check.py`, then `check.py`. Run `ruff check .` and record what it finds. Commit: *Voice: transcript checker with tests.*
2. **Spoken shape and audio check:** `test_shape.py`, then `shape.py`.
3. **Transcriber:** `transcribe.py`. Dry-run it on the course clips with no key, to confirm it fails cleanly with "no key". Then do one billed run per model.
4. **My own clips:** I record two clips, 5–10 s each, as WAV. One is a question the profile answers and one is a question it can't. **I write `expected.json` before the first transcription.** Then both models run on all five clips, and the results go in `CHECKS.md`. I listen to the clips myself. Commit: *Voice: own clips transcribed on two models.*
5. **Speaker:** `speak.py`. Speak the first clip's answer in both voices and record the numbers and what I heard. Commit: *Voice: the answer spoken, two voices.*
5a. **Misheard questions:** send the three hand-written misheard questions through the answer function once each, and record and judge the answers in `CHECKS.md`.
6. **Loop:** `api/voice.py`, the recorder on the page, `test_browser.py` (one of its assertions is that "You said: …" shows the transcript), and one real turn by microphone. The One turn section goes in `CHECKS.md`. Commit, tag `week07-submitted`, push.

### Risks

| Risk | What happens | Mitigation |
|---|---|---|
| The course repo (`../ai-integration-course`) is not cloned on this machine | No course clips, no example `profile.json` or answer step, no `test_browser.py` | Clone it before step 3. Steps 1–2 don't need it. |
| My chatbot and `profile.yaml` don't exist yet | Nothing of mine to answer from | Use the example's answer step, record that in `CHECKS.md`, and swap mine in before November 30. |
| The transcriber mishears "Kuany", a project name, or "CPSC 415" | The answer function receives the wrong words and can't tell. At best it answers about me anyway. At worst it invents an answer around the wrong word ("Vasoko", "CPSC 450"). | The checker reports the miss on fixture clips. The page shows "You said: …" live, and the browser check asserts it is shown. The billed eval sends three hand-written misheard questions to the answer function (Proof B) and checks that it never fabricates around the wrong word. |
| The speech model doesn't have the voice | It replies with JSON instead of audio | `is_audio` rejects it, the error carries the reply text, and nothing is saved. |
| An MP3 header cuts a transcript short | The transcript stops halfway | Fixture clips are WAV. |
| The browser records `audio/webm` | The server returns 415 | Map it in the formats table (WebM is listed in §12.4 behavior 9). |
| Vercel's 4.5 MB body limit | Large uploads fail before our code runs | Cap at 4 MB with 413. A 15 s clip is far smaller. |
| The 15 s stop happens only in the browser | A held button is safe, but a direct POST of 60 s of audio passes the 4 MB cap (60 s of WebM ≈ 250 KB) and is billed for 60 s | The server checks length *before* transcribing. For WAV it reads the duration from the header (`wave` module) and refuses anything over 16 s with 413. For compressed formats it refuses bodies over 512 KB, which is 15 s even at 256 kbps. Tested without a key in `test_limits.py`. |
| Many requests in a row | Each one is billed | Not handled in Week 7. Rate limiting goes in the hosting decision, together with the measured per-turn cost. |
| A billed call ends up inside a test loop | The cost multiplies | Live tests make exactly one call each and skip without a key, and evals are run by hand once. |

### Proof

**A. No-key tests (`pytest voice/tests`, cost $0, run on every change).**

These prove that the checker and the shaping code do what §12.4 says, without trusting any model.

| Test | Proves |
|---|---|
| A perfect transcript scores 0.0 | WER doesn't penalize a correct transcript |
| One substituted word in thirteen scores 1/13 | WER uses edit distance over the expected word count |
| A deleted word and an inserted word each count | All three error kinds are counted |
| An empty or whitespace reply scores 1.0, is reported as failed, and raises nothing | Behavior 1: an empty transcript is a failure, not a crash |
| "Kuany" → "Kwani" is reported missing even though the WER is ≤ 0.15 | Behavior 5: named words are checked separately from the rate |
| "four fifteen" for "CPSC 415" is a miss | A number read out as words is a miss |
| "cpsc415" and "CPSC 415" both pass | Spacing and case don't count |
| `spoken()` strips `**`, `#`, `- `, and URLs, and keeps three sentences | Behavior 6: the spoken shape |
| `spoken()` output is always a substring-in-order of the input's words | The shaping step only removes text, never adds it |
| `is_audio` rejects a JSON body and an `application/json` content type, and accepts a `RIFF…WAVE` header | Behavior 3: a non-audio reply is never treated as audio |

**B. Billed eval (run once, by hand, with the key in the shell).**

These prove what the real models do on real audio, and what that costs.

| Run | Calls | Proves | Est. cost |
|---|---|---|---|
| Five clips (two mine, three course) × whisper-large-v3-turbo | 5 transcriptions | WER and must-survive results on the default model | ~$0.001 |
| Five clips × elevenlabs/scribe-v2 | 5 transcriptions | Same on the comparison model, and which one gets my name right | ~$0.001 |
| Three misheard questions, written by hand ("What did Kwani build at Clasona?", "What did Kuany ship on Vasoko?", "What did Kuany do in CPSC 450?") → the answer function | 3 answers | What the chatbot does with a misheard name, project, or number. A pass means it either answers correctly about me without repeating the wrong word, or says the profile doesn't say. It never makes a claim about the misheard thing. I judge each answer and record it in `CHECKS.md`. | ~$0.003 |
| The first clip's answer × two voices | 1 answer + 2 speech | Characters, bytes and cost per voice, and how each says "Kuany" and "CPSC 415" | ~$0.01 |
| `test_live.py` (optional) | 1 + 1 | The request shapes still work | <$0.005 |
| Step 6: the browser check plus one real turn by microphone | A few turns | End to end with the key on the server. The One turn section records that turn's three costs and their total. | ~$0.02 for the step; **one turn ≈ $0.005** (intent's estimate) |

**Estimated total: under $0.05.** These estimates come from the lab. The measured costs replace them in `CHECKS.md`. The per-turn total (transcription + answer + speech) is the number that goes into the hosting decision.
