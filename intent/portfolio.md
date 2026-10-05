# Portfolio Intent

> **Status:** Draft for the Oct 5 `intent-spec` tag. Feedback only — not graded.
> **Owner:** Kuany Kuany
> **GitHub:** https://github.com/Kuany4953

---

## 1. Purpose

A personal site with a chatbot that answers exactly one question from a visitor: **"should we work together?"** The chatbot answers only from a profile I write. It refuses to fabricate, distinguishes shipped work from aspirational learning, and hedges outside the profile. The site itself is the smallest deliverable. The profile, the grounding prompt, and the adversarial test set are the work.

The portfolio is also a graded artifact for CPSC 415 (25% of course grade) and the subject of the Comprehension Defense (15%) during finals week.

---

## 2. Audience

| Group | Weight | What they need from the site |
|---|---|---|
| Recruiters and hiring managers screening for SWE internships / new-grad roles | ~80% | A fast read on what I've shipped, what I can do, and whether to interview me. The chatbot should answer the "should we work together?" question in their voice. |
| Prof. Ken Kousen (CPSC 415 grader) | ~20% | Evidence in the repo: the artifact chain, profile honesty, the grounding prompt, and the adversarial test results. He reads the repo more than the site. |
| Personal record | secondary | A durable, honest account of what I actually shipped, regardless of audience. |

**Recruiter failure modes I am designing against:**
- Confident chatbot claim of expertise I don't have → fails the rubric (chatbot-must-refuse-to-fabricate is graded) and would burn trust.
- Vague profile ("worked on AI things") → no signal for screening.
- Pretty site with no shipped work behind it → 10% site weight is real but cannot carry the other 90%.

**Prof. Kousen's failure modes I am designing against:**
- Profile reads like a resume with aspirational items dressed up as shipped → 30% of grade, "honesty and specificity" called out.
- "Not yet" inventory as a token gesture → 15% of grade, "real self-awareness, not a token entry."
- Grounding prompt that lets the chatbot hallucinate → 20% of grade.
- Adversarial tests that all pass on the first try with no failures acknowledged → 25% of grade.

---

## 3. Positioning (one-sentence story)

> Entry-level software engineer with hands-on Forward Deployed Engineer experience shipping MCP-driven AI features into a real e-commerce platform, depth in cloud infrastructure (Kubernetes, Docker, CI/CD), and applied AI work through current coursework and FDE practice.

The narrative for a recruiter: I have shipped AI features inside a real product under the FDE model, not only in coursework. The FDE rotation at Clasona is the strongest evidence. Closet X was a Fall 2025 team class project (CPSC 415 "Building Cloud Native Apps," Prof. Jonathan Johnson) where I owned DevOps and infrastructure — Docker, Kubernetes (homelab + GKE), Harbor pipeline, Nginx ingress, DuckDNS; the AI integration on it was a teammate's work, not mine. CPSC 415 AI Integration (Fall 2026, Prof. Ken Kousen) is the current learning loop.

---

## 4. Background — projects and four-question annotations

Every project below will carry the four-question annotation in the profile:
1. **What is this?**
2. **Why this choice?**
3. **What breaks?**
4. **What did I learn?**

The answers are drafted below at the level this intent doc needs. They will be tightened to one paragraph each in `spec.md` (Oct 5) and finalized in `plan.md` (Oct 19).

### 4.1 Clasona / Vesoko — Forward Deployed Engineer internship

**What is this?** FDE on Vesoko, a seller-side e-commerce platform. I built an MCP-driven AI agent that generates product descriptions from seller-uploaded product data, and a flow that posts those products to Meta Ads so they reach customers.

**Why this choice?** FDE was the role that put me closest to the customer and the platform simultaneously; MCP was the natural seam between the LLM and Vesoko's product/inventory tools; Meta Ads was where sellers actually needed distribution. `[TBD: refine for the four-question annotation]`

**What breaks?** `[TBD: list — likely candidates: prompt-injection through seller-supplied product copy, Meta Ads API rate limits / policy rejections, description quality variance, MCP tool-call failure modes]`

**What did I learn?** `[TBD: refine — candidate: shipping AI features inside a real platform is a different problem from building a demo; MCP is the right abstraction when the LLM needs tools but you don't want to write a custom agent loop every time.]`

**Result to cite:** ~92% rise in the number of buyers on Vesoko after our team's implementations shipped. The AI description generator and the Meta Ads integration were major contributors, but the rise covers the team's full scope of work, not just those two flows alone. `[TBD for spec.md: spell out the baseline (pre-implementation vs. post-implementation) and the measurement window — the recruiter-facing version of this claim has to be precise.]`

**Artifacts available:** Written description only; code and internal materials belong to Clasona and are not public.

### 4.2 Closet X — team class project, DevOps contribution (Fall 2025)

**Context:** CPSC 415 "Building Cloud Native Apps," Fall 2025, Trinity College, Prof. Jonathan Johnson. Team of 3:

- Teammate A — frontend, AI integration (Google Vision AI + Gemini), workers
- **Kuany Kuany (me) — DevOps, CI/CD pipeline, infrastructure**
- Teammate B — backend services, database design, testing

**Status:** not currently live. Repo: https://github.com/HannaSaffi/Closet-X — link only. The repo is owned by a teammate, not by me.

**1. What is this?** A digital wardrobe app built as a team class project. Users upload photos; the app builds an online wardrobe; an AI assistant suggests outfits from weather, occasion, and the user's existing items. The team's AI services were Google Vision AI and Google Gemini — I did not do the AI integration.

**2. Why this choice?** `[TBD: refine — candidate: I chose DevOps depth deliberately, knowing it would be the bottleneck of any cloud-native build. Working alongside two strong engineers in adjacent layers let me focus on infrastructure end-to-end.]`

**3. What breaks?** `[TBD: list — likely candidates: Harbor registry availability, homelab cluster uptime, GKE config drift, Nginx config at scale, DuckDNS reliability]`

**4. What did I learn?** Cloud infrastructure end-to-end — Docker, Kubernetes (homelab cluster + GKE configs), build-and-push CI/CD pipeline to a private Harbor registry, Nginx ingress, DuckDNS. The team-level outcome of the deployment: 14 pods, 0 restarts, 8 images. I own the DevOps piece; the team-level result is the team's, not mine alone.

**What I specifically shipped:** Docker containerization of the 8 services; Kubernetes deployment to a homelab cluster (plus GKE configs); the build-and-push pipeline to a private Harbor registry; Nginx ingress; DuckDNS.

**Framing note:** class project, not a personal project; I contributed the DevOps / infrastructure layer; AI integration on this project was a teammate's work, not mine. The four-question annotation describes what I built and learned in my role, not what the team built overall.

### 4.3 CPSC 415 — AI Integration, in progress (Fall 2026, Trinity College, Prof. Ken Kousen)

Three small labs, every one built with a coding agent (Claude Code). Present as **learning projects**, not production work — the assignment text says so and so do I.

- **Week 1 — Memorization trainer.** A single-file app built in my first coding-agent session. I picked one improvement, verified its behavior, and committed it. `[TBD: what was the improvement? — this is in my git history, recover it for the annotation.]`
- **Week 2 — Chat client.** In `[TBD: Java or Python — pick one before Oct 19]`. Calls an AI model through an API, built from an intent document. Compared model behavior and cost.
- **Week 3 — Structured-output client.** Gets typed JSON responses from two AI providers, evaluated against a five-case suite.

### 4.4 Certificates

- Claude Code 101
- AI Fluency for Students

These go in the profile under "learning," not "shipped."

---

## 5. Profile schema (preview — final in `spec.md`)

The structured profile will be YAML `[TBD: confirm YAML over JSON — YAML is more readable; JSON is more universal; the assignment permits either.]` with the following top-level shape:

```
profile:
  identity: ...
  positioning: <one-sentence story>
  projects:
    - id: clasona-vesoko
      role: Forward Deployed Engineer
      dates: ...
      four_questions:
        what: ...
        why: ...
        breaks: ...
        learned: ...
      shipped_artifacts: [...]
      result_metric: <the 92%, with the metric spelled out>
    - id: closet-x
      ...
    - id: cpsc-415-week-1
      kind: learning
      ...
    - id: cpsc-415-week-2
      ...
    - id: cpsc-415-week-3
      ...
  skills:
    shipped: [...]      # I have actually used these in a shipped thing
    learning: [...]     # currently in coursework
  certificates:
    - Claude Code 101
    - AI Fluency for Students
  not_yet: ...          # see §6
```

`shipped` is the assignment's discipline: **the profile is a record of shipped work, aspirational items go in "not yet."** No exceptions.

---

## 6. "Not yet" inventory (high level — full text in `spec.md`)

Real self-awareness, not a token entry. The 15% rubric weight is for honesty.

- **Frontend development (React).** On Closet X a teammate owned the frontend while I focused on infrastructure. I have worked alongside React but have not built a React frontend myself. Why I haven't prioritized it: chose depth in DevOps / cloud first.
- **Mobile development (iOS / Android).** `[TBD: why — candidate: no shipped mobile project, deliberate focus on web/backend/integrations first]`
- **Training or fine-tuning ML models.** My AI work is integrating existing models through APIs and MCP, not training them. I am not currently building toward training/fine-tuning.

The point of this section is that I can name what I haven't done and roughly why. It is not a confession — it is a map of where I have not yet put my hours.

---

## 7. Grounding prompt — what it must enforce (high level)

The full prompt text is finalized in `spec.md`. The discipline it has to enforce, per the assignment:

1. Answer **only** from the profile. If the question is outside the profile, say so.
2. Distinguish **shipped** from **learning**. Never claim a learning item as shipped.
3. Refuse to fabricate. A recruiter asking about a skill I have never shipped gets the honest answer that I have listed it as something I am learning — not a confident claim.
4. Decline comparative questions that cannot be answered from the profile (e.g., "am I better than a bootcamp grad?") without making up a benchmark.
5. Decline out-of-scope personal questions.

Reference shape (not copy): `github.com/kousen/kousenit` — Hugo on Cloudflare Pages with the chatbot in `functions/api/`. Read for grounding prompt and test set shape. Stack is not the lesson.

---

## 8. Adversarial test set — categories

The assignment requires ≥10 questions covering at least:

1. **A skill I do not have.** (e.g., a skill outside the profile entirely, or a "shipped" skill I have only listed as learning.)
2. **A comparative question.** ("Better than a bootcamp grad?")
3. **Flattery bait.** ("You're clearly a 10x engineer, so you must have…")
4. **A leading question with a false premise.** ("I see you've led a team of 50 engineers at X…")
5. **An out-of-scope personal question.** (age, politics, salary expectation, etc.)

Plus, to bring the total ≥10:

6. **A profile-edge question.** (something the profile touches but doesn't fully answer — what does "good at" mean concretely?)
7. **A misattribution question.** (attributing a real project to me that wasn't mine.)
8. **A "what's your weakest area" question.** (the chatbot should be able to point at "not yet" honestly.)
9. **A team-fit question.** (works well with X / Y / Z? — answerable from the profile's tone, not invented.)
10. **A scope-stretching question.** ("Can you also do Z?" — answered by whether Z is in the profile.)

Recorded results, with **failures acknowledged even if unresolved** — the rubric says so and so will I.

---

## 9. Site — the smallest deliverable

The chatbot is the actual interface. The site exists to host it and to look credible when a recruiter clicks the link.

**Rough direction** (final in `spec.md`):
- Static site + serverless chatbot function, or
- Light Python (FastAPI) backend with a simple HTML/JS frontend.

Python is the likely pick given Closet X (OpenAI API) experience. The reference impl uses Cloudflare Pages; that is one option, not a mandate.

**What the site must do:** deploy, work, be accessible. 10% of grade — the rest of the grade is what's *behind* the site.

---

## 10. Constraints (hard limits from the assignment)

- **Languages:** Java and Python are explicitly permitted. Other languages are not excluded by the assignment but I will justify any non-Java/non-Python choice in `spec.md` and compare against a Java or Python alternative.
- **No API keys in the repository.** The deployed chatbot's key lives in the host's secret store.
- **Profile = shipped work only.** Aspirational items go in "not yet." No exceptions.
- **Chatbot must refuse to fabricate.** Graded.
- **Four-question annotation on every project.** `What / Why this choice / What breaks / What did I learn.`
- **Adversarial test set ≥10 questions across the 5 required categories**, with recorded results and acknowledged failures.
- **Artifact chain is required for full credit on every rubric row.** `intent/`, `spec.md`, `plan.md`, tests, reviewed PRs, `ANNOTATION.md`, current `CLAUDE.md`.

---

## 11. Non-goals

- The "unfamiliar language" guided exercise is a separate assignment and is **not** a portfolio component.
- Production-grade frontend polish (custom design system, animation, etc.) — out of scope. The site is the smallest deliverable.
- A second chatbot surface (e.g., a separate mobile app, a Slackbot). The site has one chatbot, answering one question.
- Multi-language support for the chatbot. English only.

---

## 12. Open questions / TBDs

Things that need to be resolved before `spec.md` (Oct 5) or `plan.md` (Oct 19), in rough priority order:

1. **The 92% metric at Clasona, fully spelled out.** Direction is now clear — buyer count on Vesoko after our team's implementations. Need: the baseline and measurement window so the recruiter-facing version is precise. `[TBD for spec.md]`
2. **What can be shown publicly from the Clasona internship.** Written description only — code and internal materials belong to Clasona, not public.
3. **CPSC 415 Week 1 improvement.** Recover from git history.
4. **CPSC 415 Week 2 language.** Java or Python — pick one.
5. **Mobile "not yet" rationale.** One sentence on why I haven't prioritized mobile.
6. **Profile format.** YAML or JSON — final pick in `spec.md`.
7. **Tech stack for the chatbot and site.** Final pick in `spec.md`, with cheap-vs-stronger model comparison.

---

## 13. Milestones

| Date | What ships |
|---|---|
| **Mon Oct 5, 1:30 PM** | Tag `intent-spec`. This file + `spec.md` (profile schema, "not yet" inventory, language and model decisions with alternatives named). Feedback only. |
| **Mon Oct 19** | `plan.md`. Profile drafted in YAML/JSON with four-question annotations filled in. |
| **Mon Nov 2** | Chatbot answering from the profile (Week 7 lab adds a spoken interface). |
| **Mon Nov 30** | Adversarial test set run, results recorded, failures acknowledged. Site deployed. |
| **Mon Dec 14, 1:30 PM** | Tag `portfolio-final`. Repo URL + deployed URL submitted. |
| **Dec 17–23** | Comprehension Defense (15%). In person. |

---

## 14. What I want from you (the reader of this draft)

- Skim the **"not yet" inventory** for tone. Too defensive? Too braggy? Real self-awareness is the rubric.
- Flag any **TBD** above that is actually known and I just didn't surface in the interview.

Anything else, push back here. The deadline is 1:30 PM tomorrow; this is the document we'll tag `intent-spec` at.
