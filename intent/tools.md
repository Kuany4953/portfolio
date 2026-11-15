# Intent: one real tool for the portfolio chatbot (Week 8)

> **Owner:** Kuany Kuany
> **Approved by:** Kuany Kuany, 2026-11-15 (from the interview answers below)

## What it is

The portfolio chatbot gets one real tool, **`recent_commits(repo)`**. It returns the last
few commits of one of my public GitHub repositories, read from GitHub's REST API. The
profile cannot answer "what has Kuany worked on lately?", and the tool can. The model never
runs anything. It writes a request, and our server validates the request, then runs it or
refuses it. The result, or the problem, goes back to the model as the next message.

A second tool, **`request_intro(email, message)`**, exists so that the side-effect rule
guards something real. A visitor can ask to be introduced. The tool *would* write to an
outbox, so it is **never run on the model's request**. It is held as *pending*, the visitor
is told that I have to confirm, and nothing is written anywhere.

## Why it matters

The audience is the same as the typed and voice chatbot: recruiters first, Prof. Kousen
second. A recruiter who is told about work I did not do, or a commit that does not exist,
loses trust in everything else on the site. Tools make that risk larger: the answer now
mixes live data with model text, and the model can confidently restate a result the tool
never returned.

## Decisions from the interview

1. **The tool:** `recent_commits` (real, mine, and it fails in real ways), plus
   `request_intro` held as pending.
2. **Only my repositories.** The model may ask for any name, but code refuses any repository
   not owned by `Kuany4953` and returns an error result. The chatbot must not describe
   someone else's repository as my work.
3. **Models:** the two class models, `minimax/minimax-m3` (default) and
   `xiaomi/mimo-v2.6-flash` (comparison). Both support tool calling.
4. **Profile:** the chatbot still answers from the course's example profile (Sam Rivera), as
   `voice/CHECKS.md` already records. The tool reads *my* repositories. `tools/CHECKS.md`
   says so, and my own profile replaces the example before November 30.
5. **The claim check (plain code)** flags an answer that names:
   - one of my repositories that no successful `recent_commits` call returned (including one
     the tool said does not exist),
   - a 7-character commit SHA a tool did not return,
   - a `YYYY-MM-DD` date a tool did not return.
6. **The held introduction** is returned as pending in the trace only. No file is written:
   Vercel's filesystem is read-only, and a real outbox needs a confirm step I have not built.
7. **The cap:** four steps. When it trips, the visitor sees the program's sentence, "I couldn't
   finish answering that in 4 steps. Please try a simpler question.", not the model's text.

## What the visitor sees

- A question only the tool can answer ("What has Kuany committed lately?") gets an answer
  built from the commits the tool returned: messages and dates, nothing more.
- A repository I do not have gets "there's no public repository by that name", not an
  invented description.
- A question the profile answers is answered without the tool, ideally in one call.
- An introduction request gets "I've noted it; Kuany has to confirm before anything is
  sent." Nothing is sent.
- If the loop hits the cap, the visitor gets the program's sentence.

## What can go wrong (the misuse cases)

1. **Bad arguments:** a wrong argument name, a wrong type, or JSON that does not parse. The
   model gets an error result saying what was wrong, and the loop continues.
2. **An unknown tool:** the model asks for a tool that does not exist. It gets an error result
   listing the real tools.
3. **A loop that never stops asking:** stopped at four steps, and the answer is the program's.
4. **A side effect the model asks for on its own:** held as pending and not run.
5. **An answer that claims more than the tool returned:** flagged by the claim check.
6. **The single honest case:** one call, with the result delivered back as a `tool` message
   with the matching `tool_call_id`.

Every one of these gets a test with a scripted model before it gets code, and none of those
tests needs a key.

## Cost

Every tool call costs a second chat call to deliver the result, so a question with a tool
costs at least twice a question without one. The billed eval (five questions on two models,
about $0.01) records the cost per question. The difference goes into the per-turn cost in
the hosting decision before November 30.

## Not in scope

Running a side effect for real, a confirm step for introductions, private repositories, and
caching GitHub results. Also out of scope: a claim check that understands meaning. Plain
code matches names, SHAs and dates. `tools/CHECKS.md` says what it cannot catch.
