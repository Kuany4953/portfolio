# Intent: a spoken interface for the portfolio chatbot (Week 7)

> **Owner:** Kuany Kuany
> **Approved by:** _(Kuany kuany , 10/11/2026)_

## What it is

A visitor to my portfolio site asks the chatbot a question out loud. The server
transcribes the recording, the chatbot answers from the profile exactly as it does
for a typed question, and the answer is spoken back. The browser sends only audio;
the OpenRouter key stays on the server.

Until my own chatbot and `profile.yaml` exist, the loop answers from the course
example's `profile.json` and answer step. `voice/CHECKS.md` says so, and I swap
mine in before November 30.

## Why it matters

The audience is the same as the typed chatbot: recruiters first (~80%), Prof.
Kousen second (~20%). A recruiter who hears the wrong name or a wrong number
spoken confidently loses trust faster than one who reads a typo. The transcript
is model output and can be confidently wrong in exactly the places a recruiter
cares about: names and numbers.

## What the visitor sees and hears

1. **The transcript is shown.** The page shows "You said: …" above the answer,
   so a misheard name is visible to the visitor, not hidden.
2. **No guessing at a question.** An empty transcript, or one under three words,
   is not answered. The page says "I didn't catch that" and nothing is spoken
   from the profile.
3. **The spoken answer is the chatbot's answer.** At most three sentences, no
   markdown, lists, or URLs. When the profile does not cover the question, it
   says so plainly ("My profile doesn't say"). For a "not yet" item, it says
   "not yet" and gives the reason. It never claims experience the profile does
   not record.

## How the transcript is checked

On recorded clips with text I wrote down first, code (not a model) compares the
transcript with what I said:

- **Word error rate** must be at most **0.15** (about one word in seven). A
  looser tolerance on one clip is allowed only with a note saying why.
- **Words that must survive**, checked separately no matter how low the rate
  is: **Kuany, CPSC 415, Vesoko, Clasona, Kubernetes**. Spacing and case do
  not count ("CPSC415" is fine); a different word, or a number read out as
  words, is a miss.
- An empty transcript is a failed transcript, reported, not a crash.

A live visitor's question has no expected text, so the program cannot score it;
showing the transcript (item 1) is how the rest is made visible.

## Cost and limits

- One voice turn costs about half a cent on the class models; the measured
  per-turn cost goes into the hosting decision in `spec.md`.
- The page stops recording automatically at **15 seconds**.
- The server refuses bodies over **10 MB** and audio types it does not know
  (415), so a held button or a bad upload cannot run up the bill.

## Done means

- Two clips of my own voice and the three course clips transcribed on two
  models, each checked in code, results in `voice/CHECKS.md`, including which
  model got my name right.
- One answer spoken in two voices, with characters, bytes, and cost recorded.
- `/api/voice` working end to end, the browser check passing, and one real
  turn's three costs and total recorded.

## Not in scope

- Streaming or real-time conversation; one question, one answer.
- Voice cloning, or speaking in my own voice.
- Grading the live answer's honesty automatically; that is my judgment,
  recorded in `CHECKS.md`.
