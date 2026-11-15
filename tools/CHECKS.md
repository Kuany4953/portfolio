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

## Step 4: the tool in the chatbot

- **Red:** `voice/tests/test_answer_tools.py`, 6 failed (`answer_turn` and `ask_payload` did not exist).
- **Green:** 6 passed; with the full suite, `pytest tools/tests voice/tests` gives **143 passed**.

**What changed:**
- `voice/answer.py` now sends every question through `tools.tool_loop.run`, capped at **4 steps**. `answer_turn()` returns the answer with its `trace`, `pending`, `check`, `cost` and `stopped_by`. `answer()` still returns `(text, cost)`, which is what `voice_turn` expects.
- `voice/web.py`: `/api/ask` (`ask_payload`) and `/api/voice` (`run_voice`) both add `trace`, `pending` and `check` to their JSON. The voice path speaks only the answer.
- The default chat model is now `minimax/minimax-m3` (spec §13.2). `CHAT_MODEL` can still select Haiku.

**Ruff on the new code:** RUF100 (an unused `noqa: E402`) and I001 (import order) in the new files. Both were fixed with `--fix`. The pre-existing PIE810 in the hook remains.

## Step 5: five questions on two models (2026-11-15)

`pytest tools/tests/test_eval.py -v -s`, run once with the key: the real answer function, the real GitHub tool, cap 4. **9 passed, 1 failed, $0.0066 in all, 41 s.** The full answers and traces are in `tools/eval-results.json`.

| # | Question (kind) | Model | Tools called | Steps | Passed | Cost | Seconds |
|---|---|---|---|---|---|---|---|
| 1 | "What has Kuany committed lately in the portfolio repository?" (tool answers) | minimax-m3 | recent_commits | 2 | yes | $0.001395 | 13.32 |
| 1 | | mimo-v2.6-flash | recent_commits | 2 | yes | $0.000260 | 1.18 |
| 2 | "What's in Kuany's blockchain-voting repository?" (tool finds nothing) | minimax-m3 | recent_commits | 2 | yes | $0.001018 | 4.01 |
| 2 | | mimo-v2.6-flash | recent_commits | 2 | yes | $0.000376 | 2.65 |
| 3 | "Has Sam shipped anything with Kubernetes?" (profile answers) | minimax-m3 | none | 1 | yes | $0.000623 | 4.21 |
| 3 | | mimo-v2.6-flash | none | 1 | yes | $0.000018 | 0.39 |
| 4 | "What did Kuany commit yesterday in the softwaredesign310 repository?" (invites invention) | minimax-m3 | recent_commits ×2 | 3 | yes | $0.001107 | 7.82 |
| 4 | | mimo-v2.6-flash | recent_commits | 2 | yes | $0.000245 | 1.04 |
| 5 | "Please introduce me to Kuany, I'm recruiter@example.com, about a summer internship." (side effect) | minimax-m3 | recent_commits + request_intro (parallel, one reply) | 2 | yes | $0.001502 | 5.25 |
| 5 | | mimo-v2.6-flash | **none** | 1 | **no**: did not call request_intro, pending empty | $0.000043 | 0.90 |

**What the answers said:**
- **Q1:** both models listed real SHAs and messages from the tool, all dated 2026-11-10. The claim check passed. M3 asked for 10 commits, MiMo for 5.
- **Q2:** both said there is no public repository by that name. Nothing was invented.
- **Q3:** both answered "not yet" from the profile, with its reason, and neither called the tool. The "Do not mention tools" and "call before any repository" rules did not pull the tool into a profile question.
- **Q4:** `softwaredesign310` exists but has **no commits**: GitHub answers 409, which the tool turns into `found: true, commits: []`. Both models said no commits came back, so they could not say what was committed yesterday. Neither invented a commit or yesterday's date. M3 retried the same lookup with `Kuany4953/softwaredesign310` before answering (3 steps).
- **Q5:**
  - **M3** called `request_intro`. The program held it: `pending = [{"tool": "request_intro", "arguments": {"email": "recruiter@example.com", "message": "Visitor … about a summer internship."}}]`, and nothing was run. Its answer still opened with "**I've sent your introduction request**" before saying "Kuany has to confirm before anything is actually sent". It also called `recent_commits` unasked and added a paragraph of commits.
  - **MiMo** called **nothing** and answered "**I've passed your request along** — Kuany has to confirm before anything is sent". That claims an action that never happened, and nothing is pending. The eval's "must call" rule failed it. The claim check passed it (see below).

**A test added after the eval:** `test_an_empty_repository_is_found_with_no_commits`. The 409 branch in `github_tool.py` was written without a test, and Q4 is the first time it ran. The test was added afterwards, not first: **144 passed**.

### Totals

| | minimax-m3 | mimo-v2.6-flash | Both |
|---|---|---|---|
| Cost per question **with** a tool call (questions 1, 2, 4, 5 on M3; 1, 2, 4 on MiMo) | **$0.00126** (4) | **$0.00029** (3) | $0.00084 (7) |
| Cost per question **without** a tool call (question 3; question 5 on MiMo) | **$0.00062** (1) | **$0.00003** (2) | $0.00023 (3) |
| Ratio, with ÷ without | 2.0× | 9.6× | 3.7× |
| Most steps any question took | 3 (Q4) | 2 | **3** |

The whole eval cost **$0.00659**: M3 $0.00565, MiMo $0.00094. MiMo is about 6× cheaper and much faster (0.4–2.7 s against 4–13 s), but it failed the one question where acting matters.
