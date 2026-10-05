# Specification

> **Status:** Draft for the Oct 5 `intent-spec` tag. Feedback only — not graded.
> **Source of truth for what the profile, chatbot, and site look like:** this file plus `intent/portfolio.md`.
> **Approved decisions (Oct 4):** language = Python · profile format = YAML · model vendor = Anthropic Claude · stack = static site + serverless function.

---

## 1. Overview

The portfolio is a personal site with a chatbot that answers one visitor question — "should we work together?" — from a profile the owner writes, and refuses to fabricate. The site is the smallest deliverable; the profile, the grounding prompt, and the adversarial test set are the work. See `intent/portfolio.md` for goals, audience, and positioning. This document specifies the technical shape.

The audience weights, the rubric, the four-question annotation, the "not yet" inventory rule, and the no-API-key-in-repo rule are all set by CPSC 415 and reused here without re-derivation.

---

## 2. Audience and tone (carried from intent)

| Group | Weight | What they need from the spec |
|---|---|---|
| Recruiters / hiring managers screening SWE internships / new-grad roles | ~80% | A chatbot that honestly answers "should we work together?" from a profile they can audit. |
| Prof. Ken Kousen (CPSC 415 grader) | ~20% | Evidence the profile, the grounding prompt, and the test set were built with discipline. The artifact chain (intent/, spec.md, plan.md, tests, reviewed PRs, ANNOTATION.md, current CLAUDE.md) is required for full credit on every rubric row. |
| Personal record | secondary | A durable, honest account of what was actually shipped. |

Tone for the site copy and the chatbot: direct, specific, no marketing adjectives. The profile is a record of shipped work; aspirational items go in "not yet."

---

## 3. Profile schema (YAML)

The profile is a single YAML file at `profile.yaml` at the repo root. The chatbot and the static site read from it. The schema below is normative; the example values are placeholders that match what `intent/portfolio.md` calls out and what needs to be filled in by `plan.md` (Oct 19).

```yaml
# profile.yaml — single source of truth for the chatbot and the site
profile:
  identity:
    name: Kuany Kuany
    github: https://github.com/Kuany4953

  positioning: |
    Entry-level software engineer with hands-on Forward Deployed Engineer
    experience shipping MCP-driven AI features into a real e-commerce
    platform, depth in cloud infrastructure (Kubernetes, Docker, CI/CD),
    and applied AI work through current coursework and FDE practice.

  # Every project answers the four questions, in order.
  projects:

    - id: clasona-vesoko
      kind: shipped
      role: Forward Deployed Engineer
      organization: Clasona Technologies
      dates:
        start: "[TBD]"
        end:   "[TBD]"
      summary: |
        FDE on Vesoko, a seller-side e-commerce platform. I built an
        MCP-driven AI agent that generates product descriptions from
        seller-uploaded product data. The team also worked on a flow that
        posts products to Meta Ads so they reach customers — that piece
        was team work, not mine alone.
      four_questions:
        what:    "[TBD — filled in plan.md from confirmed user input]"
        why:     "[TBD — filled in plan.md from confirmed user input]"
        breaks:  "[TBD — filled in plan.md from confirmed user input]"
        learned: "[TBD — filled in plan.md from confirmed user input]"
      result:
        metric: |
          ~92% rise in the number of buyers on Vesoko after our team's
          implementations shipped (team-wide, not just the AI + Meta
          Ads flows).
        baseline:  "[TBD for spec.md — pre-implementation reference period]"
        window:    "[TBD for spec.md — measurement window in weeks]"
      artifacts:
        visibility: description-only
        note: |
          Code and internal materials belong to Clasona and are not
          public. The portfolio entry is a written description only.

    - id: closet-x
      kind: shipped-contributed
      kind_note: |
        Team class project; my contribution is the DevOps / infrastructure
        layer. AI integration on this project was a teammate's work.
      course: "CPSC 415 'Building Cloud Native Apps,' Fall 2025, Trinity College, Prof. Jonathan Johnson"
      role: "DevOps, CI/CD pipeline, infrastructure"
      repo: https://github.com/HannaSaffi/Closet-X
      status: not-currently-live
      summary: |
        Digital wardrobe app. Users upload photos; the app builds an
        online wardrobe; an AI assistant suggests outfits from weather,
        occasion, and the user's existing items. The team's AI services
        were Google Vision AI and Google Gemini.
      four_questions:
        what:    "[TBD — filled in plan.md from confirmed user input; confirmed facts: team class project, digital wardrobe, AI integration was a teammate's work, I owned DevOps / infrastructure.]"
        why:     "[TBD — filled in plan.md from confirmed user input]"
        breaks:  "[TBD — filled in plan.md from confirmed user input]"
        learned: "[TBD — filled in plan.md from confirmed user input; confirmed facts: I shipped Docker, Kubernetes (homelab cluster + GKE configs), Harbor pipeline, Nginx ingress, DuckDNS.]"
      team_results:
        pods: 14
        restarts: 0
        images: 8
        note: "Team-level results; not mine alone."
      what_i_shipped:
        - "Docker containerization of the 8 services."
        - "Kubernetes deployment to a homelab cluster (plus GKE configs)."
        - "Build-and-push CI/CD pipeline to a private Harbor registry."
        - "Nginx ingress."
        - "DuckDNS."

    - id: cpsc-415-fall-2026-week-1
      kind: learning
      course: "CPSC 415 AI Integration, Fall 2026, Trinity College, Prof. Ken Kousen"
      summary: |
        Memorization trainer. Single-file app, built in my first coding-
        agent session. Picked one improvement, verified its behavior,
        committed it to Git.
      four_questions:
        what:     "[TBD — description + the one improvement chosen]"
        why:      "[TBD — why this improvement over others]"
        breaks:   "[TBD]"
        learned:  "[TBD]"

    - id: cpsc-415-fall-2026-week-2
      kind: learning
      course: "CPSC 415 AI Integration, Fall 2026, Trinity College, Prof. Ken Kousen"
      summary: |
        Chat client that calls an AI model through an API, built from an
        intent document I wrote. Compared model behavior and cost.
      four_questions:
        what:     "[TBD — language is Python (decision §5); describe the chat client]"
        why:      "[TBD]"
        breaks:   "[TBD]"
        learned:  "[TBD]"

    - id: cpsc-415-fall-2026-week-3
      kind: learning
      course: "CPSC 415 AI Integration, Fall 2026, Trinity College, Prof. Ken Kousen"
      summary: |
        Structured-output client that gets typed JSON responses from two
        AI providers, with a five-case evaluation suite.
      four_questions:
        what:     "[TBD — describe the structured-output client and the two providers]"
        why:      "[TBD]"
        breaks:   "[TBD]"
        learned:  "[TBD]"

  # Skills separated by what was actually shipped vs. what is in learning.
  # The chatbot's grounding prompt uses this split to enforce honesty.
  skills:
    shipped:
      - "MCP / Anthropic Model Context Protocol"
      - "Vesoko seller-side e-commerce platform (workforce-context usage)"
      - "Kubernetes deployment (homelab cluster + GKE configs)"
      - "Docker containerization of multi-service apps"
      - "CI/CD pipeline to a private Harbor registry"
      - "Nginx ingress configuration"
      - "DuckDNS dynamic DNS"
      - "Meta Ads integration — [TBD: confirm whether I personally shipped this or it was team work]"
      - "Forward Deployed Engineering practice"
    learning:
      - "Anthropic Claude API / SDK"
      - "AI integration patterns (MCP, structured outputs)"

  certificates:
    - "Claude Code 101"
    - "AI Fluency for Students"

  # "Not yet" inventory — see §4 for the rationale per item.
  not_yet:
    - area: "Frontend development (React)"
      context: "On Closet X, a teammate owned the frontend while I focused on infrastructure."
      why: "Chose depth in DevOps / cloud first."
    - area: "Mobile development (iOS / Android)"
      context: "[TBD — one sentence on what would change if mobile became a priority]"
      why: "[TBD — one sentence]"
    - area: "Training or fine-tuning ML models"
      context: "My AI work has been integrating existing models through APIs and MCP, not training them."
      why: "Not currently building toward training / fine-tuning; the depth I'm after is on the integration and shipping side."
```

The chatbot's grounding prompt receives `profile.yaml` (or a distilled version of it) and the system prompt instructs it to answer only from the data above. Items listed under `learning` are not `shipped` and must not be claimed as such.

---

## 4. "Not yet" inventory

The rubric weights the "not yet" inventory at 15% — "real self-awareness, not a token entry." Three entries, each with a one-sentence rationale and the context that produced the gap.

### 4.1 Frontend development (React)

- **What I haven't done:** built a React frontend myself.
- **Context:** On Closet X, a teammate owned the frontend. I worked alongside it but did not write it.
- **Why I haven't prioritized it:** chose depth in DevOps / cloud first. Re-prioritizing React is something I can do, but I haven't put hours against it yet.

### 4.2 Mobile development (iOS / Android)

- **What I haven't done:** shipped a native or cross-platform mobile app.
- **Context:** `[TBD — one sentence on the kind of project I'd build if mobile became a priority]`
- **Why I haven't prioritized it:** `[TBD — one sentence]`

### 4.3 Training or fine-tuning ML models

- **What I haven't done:** trained or fine-tuned an ML model.
- **Context:** my AI work has been integrating existing models through APIs and MCP, not training them.
- **Why I haven't prioritized it:** the depth I'm building toward is on the integration and shipping side, not the training side. Fine-tuning is not on my near roadmap.

---

## 5. Language decision: Python

### 5.1 Decision

**Python** is the language for the chatbot logic, the chatbot's serverless function, and any server-side code in the artifact chain. One language end-to-end.

### 5.2 Alternatives named

| Alternative | Pros | Cons | When it would have won |
|---|---|---|---|
| **Java** | Type system for the chatbot layer; Spring AI is a real option; explicitly permitted by the assignment. | Heavier scaffolding; less direct match to the Closet X-era LLM SDKs. | If a Java-centric stack were a personal goal for this course, or if Java were the strongest match to other course work. |
| **JavaScript / TypeScript (Node)** | One-language stack with the static frontend; large ecosystem. | Not explicitly named by the assignment; would have required switching the serverless function to JavaScript and splitting the stack (Python for the model SDK, JS for the function shell). | If matching the reference impl's literal Cloudflare Pages stack mattered more than Python consistency. |

### 5.3 Rationale

- Python is the default for LLM SDK work (Anthropic, OpenAI, Google all ship first-class Python SDKs).
- FastAPI is a clean fit for a small chatbot API surface.
- The Week 2 chat client and Week 3 structured-output client CPSC 415 labs were written in `[TBD — Python or Java]`. The portfolio's chatbot is Python either way; if the labs are also Python, the chatbot can share code paths with them.
- Keeping Python end-to-end (logic + function) avoids a split-language stack; the alternative would have been to write the chatbot logic in Python but the Cloudflare Pages Functions wrapper in JavaScript.

---

## 6. Stack decision: static site + Python serverless function on Vercel

### 6.1 Decision

**Static site + Python serverless function on Vercel.** The chatbot is a Python serverless function; the site is a static bundle served from the same Vercel project. The reference impl at `github.com/kousen/kousenit` (Hugo on Cloudflare Pages with `functions/api/`) is the pattern to follow — static site + serverless function — but **not the literal stack**, because Cloudflare Pages Functions does not support Python. Vercel preserves the pattern while keeping Python end-to-end.

### 6.2 Concrete shape

- **Static site:** Hugo (matches the reference) or a hand-rolled HTML/CSS/JS bundle. One page, one chatbot widget. Hosted on Vercel as the static side of a single project.
- **Chatbot function:** Python, served from Vercel Python serverless functions (`api/chat.py`, optionally FastAPI). Reads `profile.yaml` at request time. Calls Claude through **OpenRouter** — the course's access route — using the OpenRouter API key stored in Vercel's environment variables. Model IDs are TBD at run time (resolved when the comparison is run; see §8). Streams the response back to the page.
- **Profile data:** `profile.yaml` at the repo root. Bundled into the deployable artifact or read from the repo's deploy context.
- **Hosting:** Vercel, single project for static + functions. Environment variables hold the OpenRouter API key; the key never enters the repo.

### 6.3 Alternatives named

| Alternative | Pros | Cons | When it would have won |
|---|---|---|---|
| **Cloudflare Pages + JavaScript function (the reference impl's literal stack)** | Matches the reference impl exactly; cheap to host; Pages Functions are JavaScript-only and mature. | Forces the function into JavaScript while the chatbot logic is Python — split-language stack. Less natural for sharing code with the CPSC 415 lab projects (which are Python). | If matching the reference impl's literal platform mattered more than Python end-to-end. |
| **Python FastAPI + simple static frontend (e.g., Render, Fly, Railway)** | Full control over the backend; easier local testing; conventional Python web stack. | Always-on server (more cost, more ops); more deployment config; needs a separate host from the static bundle. | If I wanted a long-running backend for analytics, logging, or richer server-side state. |
| **Java Spring AI + static frontend** | Spring AI is a real option for Java; same control as FastAPI. | Heavier; more boilerplate; less natural for a single-page chatbot. | If Java had won §5. |
| **Client-side page + thin serverless proxy** | Smallest backend surface; cheapest to host. | More JS in the page; less control over prompt / response shape. | If the model call had no server-side state and the prompt could be safely exposed client-side. |

### 6.4 Rationale

- **Why not Cloudflare Pages + JS function:** Cloudflare Pages Functions are JavaScript-only (the `/functions` directory expects `.js`/`.ts` files). Using Cloudflare would have meant writing the function in JavaScript while the chatbot logic stayed in Python — a split-language stack. The pattern (static + serverless) was the lesson, not the platform.
- **Why Vercel:** Vercel supports Python serverless functions natively (including FastAPI), preserves the static + serverless pattern, has a free tier that covers the expected traffic, and lets the API key live in the host's environment variables (assignment rule preserved).
- **Trade-off vs. the reference impl:** diverges from the literal Cloudflare Pages platform. Acceptable because the assignment says "Spring AI with a static site, Python with FastAPI, or a client-side page calling an API through a small serverless function all work" — Vercel Python serverless functions is a fourth shape in that spirit, not a departure from it.
- **Trade-off vs. FastAPI on Render/Fly/Railway:** Vercel keeps the single-project static + function model. FastAPI on a separate host means always-on cost and a second deploy. Vercel wins for this site's traffic shape (low, recruiter-driven).

---

## 7. Model decision: Anthropic Claude

### 7.1 Decision

**Anthropic Claude, accessed via OpenRouter.** The chatbot uses Claude for inference, called through OpenRouter — the course's access route — with the OpenRouter API key stored in Vercel's environment variables. The cheap-vs-stronger comparison (§8) is run on Claude Haiku 4.5 against Claude Sonnet. **Model IDs are TBD at run time**, resolved when the comparison is run and noted in `ANNOTATION.md`.

### 7.2 Alternatives named

| Alternative | Pros | Cons | When it would have won |
|---|---|---|---|
| **OpenAI** | Broad tooling; well-documented SDK; GPT-4o-mini vs GPT-4o is a clean cheap-vs-stronger pair. | No direct project familiarity; would be net-new SDK integration. | If the personal record needed an OpenAI credit, or if a recruiter-facing story leaned on OpenAI. |
| **Google (Gemini)** | Flash vs Pro is the natural cheap-vs-stronger pair. | No direct project familiarity; less mature SDK for chatbot-style integration; less direct match to MCP-grounded prompt discipline. | If a non-Anthropic comparison was specifically required. |
| **Self-hosted (e.g., Llama, Mistral)** | No API key, no vendor cost; full control. | Operational burden is far above the assignment's scope; would need GPU/host infra. | Not applicable here — the assignment explicitly puts the chatbot key in a host secret store. |

### 7.3 Rationale

- The FDE internship at Clasona used Anthropic's Model Context Protocol (MCP); choosing Claude for the chatbot continues the same Anthropic protocol family.
- The reference impl at `kousenit` is Claude-based.
- OpenRouter is the course's access route for Claude API calls — the OpenRouter API key is the secret in Vercel's environment variables; no key ever enters the repo.
- The assignment's "cheap model vs stronger one" language maps cleanly to Haiku 4.5 vs Sonnet, resolved at run time.
- A second model provider for the comparison would have been defensible but adds operational cost without changing the grading story.

---

## 8. Comparison plan: cheap model vs stronger model on the adversarial test set

The assignment requires a cheap model compared against a stronger one on the portfolio's own test set. The test set is the adversarial set required by CPSC 415 (≥10 questions across 5 categories — see `intent/portfolio.md` §8). This plan covers both the build and the record of results.

### 8.1 Models compared

- **Cheap:** Claude Haiku 4.5, called through OpenRouter (model ID TBD at run time — likely `anthropic/claude-haiku-4.5` or current equivalent).
- **Stronger:** Claude Sonnet, called through OpenRouter (model ID TBD at run time — likely `anthropic/claude-sonnet-5.5` or current equivalent).

Both IDs are resolved at the time the comparison is run, and the resolved IDs are written into `ANNOTATION.md`. If the Anthropic model lineup changes between spec and run, the comparison pair is updated to whatever "cheap" and "stronger" map to in the lineup at run time, with a one-line note in `ANNOTATION.md`.

### 8.2 What gets compared

For each question in the adversarial test set:

1. **Pass / fail** on the question's intent (correct refusal, correct answer, or correct hedge — depending on what the question is probing).
2. **Fabrication count** — number of claims made that are not in `profile.yaml`. The grader counts a fabrication as a fail.
3. **Shipped-vs-learning discipline** — does the chatbot claim a learning item as shipped? Counts as a fail.
4. **Length and tone** — within the expected range for a recruiter-facing response? (Logged, not graded.)
5. **Cost** — input + output tokens × model's published price. Logged per question, summed across the set.

### 8.3 How the comparison is run

- Each adversarial question is asked of each model with the same system prompt and the same `profile.yaml`.
- The system prompt is the grounding prompt in production — no test-only softening.
- Runs are scripted (`tests/run_adversarial.py` or equivalent), deterministic where the model supports it (seed where possible), and the raw responses are saved alongside the verdicts.
- Results table:

| Question | Category | Expected behavior | Haiku verdict | Sonnet verdict | Notes |
|---|---|---|---|---|---|
| Q1 | Skill I do not have | Refuse or hedge | … | … | … |
| … | … | … | … | … | … |

### 8.4 What "wins" looks like

- The comparison is **not** "who passes more." Both models must pass the categories that grade chatbot-must-refuse-to-fabricate. A cheaper model that hallucinates more is a worse choice even if it costs less.
- The comparison answers: *is the stronger model worth its higher cost on this test set, or does the cheap model pass cleanly enough to ship?*
- If the cheap model passes cleanly: ship the cheap model. Note the comparison in `ANNOTATION.md`.
- If the cheap model fails any fabrication / shipped-vs-learning question: ship the stronger model. Note the failure modes of the cheap model in `ANNOTATION.md`.
- Failures from either model are **acknowledged in the recorded results**, even if unresolved. The rubric explicitly requires this.

### 8.5 What is not in scope

- Comparing a third model family (e.g., GPT-4o-mini). Naming it as an alternative is enough.
- Cost-optimization beyond the two-model comparison.
- Latency / throughput benchmarks — out of scope for the assignment.

---

## 9. Constraints (hard limits from the assignment)

- **Languages:** Java and Python are explicitly permitted. Python is the choice (§5). Any non-Java / non-Python component would need an explicit justification in this spec.
- **No API keys in the repository.** The OpenRouter API key lives in Vercel's environment variables; it never enters the repo.
- **Profile = shipped work only.** Aspirational items go in "not yet" (§4). No exceptions.
- **Chatbot must refuse to fabricate.** Graded.
- **Four-question annotation on every project.** `What / Why this choice / What breaks / What did I learn.`
- **Adversarial test set ≥10 questions across 5 categories**, with recorded results and acknowledged failures.
- **Artifact chain required for full credit on every rubric row.** `intent/`, `spec.md`, `plan.md`, tests, reviewed PRs, `ANNOTATION.md`, current `CLAUDE.md`.
- **Tech stack:** static site + Python serverless function on Vercel (decided in §6 after verifying that Cloudflare Pages Functions are JavaScript-only).

---

## 10. Open questions carried from `intent/portfolio.md`

These are the same TBDs from the intent doc, ordered by impact on this spec and the next deliverable.

1. **The 92% metric at Clasona, baseline + window.** Direction is clear (buyer count on Vesoko after our team's implementations). The baseline and window make the recruiter-facing claim precise. `[TBD for plan.md, Oct 19]`
2. **Clasona internship dates.** Start / end dates for the project entry. `[TBD]`
3. **CPSC 415 Week 1 improvement.** Recover from git history. `[TBD]`
4. **Mobile "not yet" — context and why.** Both currently `[TBD]` placeholders. `[TBD]`
5. **CPSC 415 Week 2 / Week 3 four-question answers.** Placeholders in the schema. `[TBD for plan.md]`
6. **The exact Sonnet model ID.** The Anthropic lineup changes. Resolve at run time, note in `ANNOTATION.md`.

---

## 11. Cross-references

- `intent/portfolio.md` — goals, audience, project inventory, "not yet" sketch, adversarial test categories.
- This file — profile schema, "not yet" full text, language / stack / model decisions, comparison plan.
- `plan.md` (Oct 19) — implementation steps, project-by-project four-question answers, deployment.
- `ANNOTATION.md` — recorded results from the comparison run, acknowledged failures.
- `profile.yaml` — the data the chatbot reads.
