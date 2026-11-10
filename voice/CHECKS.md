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

### My own clips (my voice, recorded in Voice Memos, converted to 16 kHz mono WAV)

I wrote the answer key and committed it (`237076f`) before any model heard these clips. Tolerance 0.15. Files: `transcripts-whisper.json`, `transcripts-scribe.json`, `transcripts-whisper-en.json`.

| Clip | Model | WER | Missing | Audio s | Cost | Call s | Verdict |
|---|---|---|---|---|---|---|---|
| mine-01 | whisper-large-v3-turbo | 0.818 | Kuany, Vesoko, Clasona | 7.66 | $0.0000255 | 0.9 | FAIL |
| mine-01 | scribe-v2 | 0.545 | Kuany, Vesoko, Clasona | 7.66 | $0.000468 | 1.9 | FAIL |
| mine-02 | whisper-large-v3-turbo | 0.615 | Kuany, CPSC 415 | 10.35 | $0.0000344 | 0.5 | FAIL |
| mine-02 | scribe-v2 | 0.154 | Kuany | 10.35 | $0.000632 | 1.4 | FAIL |

What each model wrote:

| Clip | What I said | Whisper | Scribe |
|---|---|---|---|
| mine-01 | Did Kuany Kuany build the AI agent for Vesoko at Clasona? | "Dit kwane kwane. the old AI agent Viseko Klaasona" | "Did Kwanikwani be all AI agent for Veseko at Klasona?" |
| mine-02 | Kuany led a team of 50 engineers at Clasona for CPSC 415, right? | "Kåre ni lære dig tem. 50 engineers at klasstorne for CPSC 4.15, right?" | "Kwan led a team of 50 engineers at Glassona for CPSC 415, right?" |

**All four transcripts fail.** On the course clips, which a model spoke, every transcript passed. On my voice, every one failed. That gap is why the lab asks for a person's voice.

- **Scribe is closer on every clip,** at about 18× the cost. On mine-02 it got everything except my name: "50" as digits, "CPSC 415" as digits, and the rest of the sentence word for word. It still turned "Clasona" into "Glassona", which isn't a must-survive word in that clip, so it counts only toward the WER (0.154, just over 0.15).
- **Whisper detected the wrong language on mine-02.** It started in Danish or Norwegian ("Kåre ni lære dig tem") and turned "CPSC 415" into "4.15", so the number survived as the wrong number.
- **Neither model ever wrote "Kuany".** The closest attempts were Whisper's "kwane", Scribe's "Kwanikwani" and "Kwan", and the microphone turn's "Kwaani".

### Language experiment: Whisper with `--language en`

I re-ran Whisper on my two clips with the English hint (2 calls, $0.00006), because of the Danish misdetection above.

| Clip | WER without hint | WER with `--language en` | With the hint, Whisper wrote |
|---|---|---|---|
| mine-01 | 0.818 | 0.818 | "Did Kwan Kwan the old AI agent physical That's cool, right?" |
| mine-02 | 0.615 | 0.769 | "Kwanileta team. about 50 engineers at class hall now Well... CPSC. 4:15, right?" |

**What changed:**
- The hint stopped the Danish, but the transcripts didn't improve, and on mine-02 the WER got worse.
- With the hint, Whisper **invented words I never said**: "That's cool, right?" and "Well...". It also turned "415" into a clock time, "4:15".
- A language hint isn't a fix for a name the model has never heard. Scribe, without any hint, was better than both Whisper runs.

## Which model got my name right

**Neither.** On every clip, and on the live microphone turn, "Kuany" came back as something else: kwane, Kwan Kwan, Kwanikwani, Kwan, Kwaani, Kåre. **Scribe got my numbers right** ("50", "CPSC 415") on mine-02. **Whisper got "50" right but turned 415 into 4.15 or 4:15.**

**What I heard when I played the clips myself:** _(fill in: after `afplay clips/mine-01.wav` and `clips/mine-02.wav`, did I say every word clearly? Which transcript is closer to what I hear?)_

**What this means for the site:** a visitor who says my name will usually be transcribed wrong. The chatbot must not treat "Kwan" as a different person, and must not invent anything about a misheard name. The live turn shows it refusing rather than inventing. The "You said:" line is what lets the visitor see the problem. When my own profile goes in, the grounding prompt should say that a close misspelling of "Kuany" in a question is about me.

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

My own voice, through the microphone on `http://localhost:8000` (Chrome, `audio/webm`), 2026-11-10.

- **What I said:** _(fill in: the exact words I spoke)_
- **You said (the transcript):** "Kwaani kwaani, agent Klaasona?"
- **Answer:** "I'm not sure what you're asking. "Kwaani" and "Klaasona" don't appear in Sam Rivera's profile, so I can't answer that. I can tell you about Sam's projects, shipped skills, or the areas Sam hasn't worked in yet, like Kubernetes, React, and Rust."

| Step | Model | Cost |
|---|---|---|
| Transcribe | openai/whisper-large-v3-turbo | $0.000024 |
| Answer | anthropic/claude-haiku-5.5 | $0.00019 |
| Speak | microsoft/mai-voice-2.1-flash / en-IN-Priya | $0.0037 (estimated, per character) |
| **Total** | | **$0.0039** |

**What it shows:**
- **The transcriber failed on exactly the words a recruiter cares about.** "Kuany" became "Kwaani" and "Clasona" became "Klaasona", and most of the question didn't survive.
- **The "You said:" line made that visible** (intent item 1). As a visitor, I could see at once why the answer was off.
- **The refuse-to-fabricate rule held on the wrong transcript.** The chatbot said the words don't appear in the profile and invented nothing about "Kwaani" or "Klaasona".
- **Speech is about 95% of the cost.** It is billed per character, so the three-sentence limit is also the cost limit.
- It answered from the course example's profile (Sam Rivera), as the note at the top says.

**Per-turn cost for the hosting decision:** about **$0.004 per voice question** (this turn $0.0039; the browser check's turn $0.0034).
