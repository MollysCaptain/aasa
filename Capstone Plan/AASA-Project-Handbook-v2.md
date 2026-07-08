# ATSA — AI Stack Architect · Project Handbook v2 (reconciled)

**Team:** 2 students · **Duration:** 4 weeks (3-week build + 1-week package/pitch)
**Status:** post-pivot, post-feedback reconciliation. This handbook is now the single source of truth. Where it disagrees with any earlier document (Pitch, original Ethical Action Plan, or the first prototype), **this wins.**

---

## 0. What changed and why (change log)

We received feedback that our artefacts described *three different projects*: the broad "all-software" pitch, the narrowed AI-stack pivot docs, and a prototype that still sold the old scope with fabricated trust signals. We also learned our technical plan was built on a wrong picture of the source data. This v2 fixes all of it.

| # | Problem in v1 | Fix in v2 |
|---|---|---|
| 1 | Scope drift across docs (broad vs. AI-only) | One scope statement (§1), all docs re-anchored to it |
| 2 | Prototype had fake testimonials, fake SOC 2/ISO certs, fake press, wrong scope, rejected theme | Rebuilt honest prototype on real data, clean neo-industrial theme, all fabrications removed (§9) |
| 3 | WBS assumed "3,000 raw markdown files" + dirty-text risk | Data is one clean CSV; real task is tool-name normalisation (§2, §5) |
| 4 | Cost model assumed per-token pricing for all tools | Costing now distinguishes per-seat SaaS from per-token APIs (§5) |
| 5 | Implied per-case filtering by company size | Corrected: SO-survey firmographics are population-level only (§2) |
| 6 | Week 3 built the MVP *and* ran 50+12 users | Recruiting moved to Week 1; realistic N; testing spread across weeks (§7) |
| 7 | Flowise + Streamlit + webhook integration risk | Dropped Flowise; Streamlit + local vector store + direct API calls (§5) |
| 8 | Unmeasurable "Human Architect Override < 15%" | Replaced with metrics we can actually run as 2 people (§8) |
| 9 | Ethics plan written for old scope + bigger team | Re-scoped to AI-stack + 2 people wearing multiple hats (§10) |

---

## 1. Reconciled scope statement

**ATSA is an AI Stack Architect.** It takes five constraints and returns a three-block blueprint — recommended **AI models/APIs/frameworks**, an **illustrative cost forecast**, and **real-world case references** — grounded in a retrieval knowledge base of 3,023 real AI deployments.

**In scope:** AI models, APIs, model platforms, and agent/orchestration frameworks; illustrative monthly cost; traceable real-case evidence.

**Explicitly out of scope (v2):** general tech-stack advice (databases, hosting, front/back-end frameworks); live pricing feeds; application/boilerplate code generation; any claim of compliance certification. These are roadmap items, not MVP promises.

**One-line value:** *turn "what AI should we use?" into an evidence-backed shortlist in ~2 minutes, instead of a two-week research loop.*

---

## 2. Dataset reality (what we verified)

We inspected the source repo (`abbasmahdi-ai/ai-use-cases-library`) directly rather than trusting our own summary:

- It is **one clean CSV of 3,023 fully-populated rows** — not 3,000 markdown files. Every key field (Tool/Technology, Description, Outcomes, Industry, Source URL) is 100% filled. Parsing is trivial; **the C-rated "clean the raw files" task no longer exists.**
- The **real cleaning job is tool-name normalisation**: 2,511 distinct tool strings for 3,023 rows (e.g. *Gemini / Gemini models / Gemini in Docs / Gemini for Workspace*), plus junk like "AI", "Generative AI", "Not specified". Without an alias map, our pricing lookup would miss most rows. We built that map (24 canonical tools).
- The data **skews to enterprise productivity AI** (Gemini/Workspace, M365 Copilot, Bedrock), not the CrewAI/LangGraph agent world our old pitch foregrounded. Our recommendations honestly reflect that adoption pattern.
- **Many top tools are per-seat SaaS, not per-token APIs.** A token burn-rate is meaningless for M365 Copilot. Our cost model now handles both.
- **There is no org-size field and no join key to the Stack Overflow survey.** SO firmographics can only give *population-level* patterns ("X% of 100–499-person orgs use Y"), never per-case filtering.

**Design consequence:** this dataset is excellent as a **retrieval corpus** and weak as a deterministic-costing substrate. v2 leans into retrieval-of-comparable-cases (our real differentiator) and keeps costing modest and clearly illustrative.

---

## 3. Core hypothesis to validate

> Resource-constrained founders and product leads will trust an automated AI-stack recommendation **if** it is (a) grounded in traceable real-world deployments and (b) paired with a plain, honest monthly-cost estimate — enough to replace days of forum research.

---

## 4. MVP definition (MoSCoW)

| Feature | Effort | Priority | Note |
|---|---|---|---|
| Curated case retrieval (normalise + filter + rank) | 3 d | **MUST** | Core value; the real differentiator |
| 5-field intake form | 1.5 d | **MUST** | Workflow, Industry, Org size, Privacy, Budget |
| 3-block blueprint output (stack / cost / cases) | 2 d | **MUST** | Traceable to sources |
| Illustrative cost forecast (seat + token aware) | 1.5 d | **SHOULD** | Directional, disclaimed |
| Telemetry + trust micro-survey | 1 d | **SHOULD** | Feeds validation |
| Copy/export blueprint | 0.5 d | **SHOULD** | Simple clipboard |
| Investor-ready PDF export | — | **COULD** | Roadmap Month 2 |
| One-click boilerplate | — | **COULD** | Roadmap Month 2 |
| Live pricing scraper | — | **WON'T** | Manual table is fine for MVP |

---

## 5. Technical plan — Epic 2 rewritten

**Stack (simplified, per feedback):** Streamlit UI → Python logic → local vector store (Chroma) → one model API (gpt-4o-mini class) for the summary only. **Flowise dropped** — a filter→retrieve→prompt pipeline is simpler and more debuggable in plain Python, and it removes the webhook / cross-origin risk we flagged ourselves.

**Pipeline (deterministic first, LLM last):**
1. **Normalise** the 3,023 rows' tool names via the alias map → canonical tool ids.
2. **Embed** case descriptions + outcomes into Chroma (one-off script).
3. **Hard filter** on privacy posture *before* ranking (regulated → prefer governable platforms/self-host; exclude consumer assistants). This is directional, not certification.
4. **Retrieve + rank** comparable cases by workflow/industry; rank tools by evidence frequency.
5. **Cost**: for each recommended tool, apply the pricing table — **per-token** (input/output €/M tokens × assumed volume) or **per-seat** (€/seat × team size) or **compute-billed** (shown, not costed). Estimate one primary API + one assistant, not the sum of everything.
6. **Summarise**: the LLM writes prose only; it never invents tools or prices. Few-shot prompt fixes the output template.

**Pricing table:** hand-built, 24 tools, each tagged `token | seat | compute | free`, marked **illustrative / verify on vendor page**. No live scraping in the MVP.

---

## 6. Work breakdown (2 people, honest effort)

**Person A — Data & Logic:** normalisation map, embeddings, hard-filter + ranking, cost parser, prompt.
**Person B — UI & Validation:** Streamlit intake + 3-block output, telemetry, micro-survey, user recruiting & sessions, pitch.

Both share testing and the pitch deck. Total build ≈ **9.5 days**; with two people in parallel that fits the 3-week window **only if** the Should-Haves are treated as the cut line. Realistic buffer is **~30%** (not 20%) because we are learning Chroma + prompt tuning; if we slip, we drop cost-PDF/telemetry-polish first, never the retrieval core.

---

## 7. Revised 4-week timeline (fixes the Week-3 collision)

| Week | Build | Users / PM |
|---|---|---|
| **1** | Normalise data, build embeddings + pricing table, draft charter & reconciled scope | **Start recruiting** 5–8 real testers; write interview guide |
| **2** | Retrieval + ranking + cost logic; intake form | Concept test the honest prototype (this page) with 2–3 users; refine |
| **3** | Wire full pipeline; polish 3-block output; telemetry | **Test working build with 5–8 real users**; log & patch |
| **4** | Freeze; write limitations as "technical debt"; roadmap | Analyse results; build & rehearse 10-slide pitch |

**Sample-size honesty:** 5–8 real users surface the majority of usability/trust blockers. We drop the old N=50 / N=12 targets; a small, well-documented study beats an aspirational one we can't deliver.

---

## 8. Metrics (only what 2 people can measure)

| Metric | Target | How we measure it |
|---|---|---|
| Trust score (post-session 1–5) | ≥ 4/5 median | Micro-survey after blueprint |
| Net value ("replaced hours of research?") | ≥ 70% yes | Micro-survey |
| Blueprint export/copy rate | ≥ 40% | Telemetry event |
| Compliance-rule pass rate | 100% | Automated check: every recommended tool respects the hard filter |
| Form completion velocity | trend only | Telemetry (start→submit) |
| Field abandonment | trend only | Telemetry per field |

**Dropped:** "Human Architect Override Ratio < 15%" — we have no on-call human architect to grade every output, so it isn't measurable. The compliance-rule pass rate is the honest, automatable substitute.

---

## 9. Prototype changes (honesty pass)

The first prototype was a Lovable-generated marketing shell. Everything below was **removed** because it contradicts our ethics workstream and, in a real launch, would be misleading or unlawful:

- **Removed:** fabricated testimonials & named people/companies; "4.9 · 312 reviews"; customer logo wall; "Featured in TLDR / Product Hunt / YC alum"; invented case metrics; **fake SOC 2 Type II / ISO 27001 / AWS & Google Partner badges**; fake pricing scarcity ("12 seats left").
- **Changed:** scope realigned from general tech-stack → AI stack; the rejected "StackPunk" steampunk theme replaced with the **neo-industrial blueprint** direction our user research chose; stats are now **real** (197 curated cases, 24 priced tools, 15 industries) with a visible "prototype · demo data" tag.
- **Added:** a plain "known limitations" section; source links on every case; "no data stored" and "illustrative pricing / directional, not advice" disclaimers.

The rebuilt prototype (`atsa-prototype.html`) runs on the actual dataset: pick five constraints → it retrieves real matched deployments, ranks their tools, estimates a seat+token cost against your budget, and links every recommendation back to its source.

---

## 10. Ethics plan (re-scoped to AI stack + 2 people)

The bones of the original plan were good; we re-anchored the actions and collapsed the four invented roles into two people wearing multiple hats.

- **Week 1 — Data minimisation:** no PII stored; inputs are anonymous constraints only; the app keeps no accounts. *(Owner: A)*
- **Week 2 — Bias & honesty:** document the dataset's enterprise-productivity skew in a short model card; ensure ranking reflects real frequency, not our preferences; state every limitation in-product. *(Owner: A)*
- **Week 3 — Inclusion & clarity:** test with a non-technical founder and a non-native English speaker; check the output is legible without jargon. *(Owner: B)*
- **Week 4 — Governance:** final responsible-AI checklist; confirm no fabricated trust signals remain anywhere. *(Owner: both)*

Post-capstone review dates (Aug 2026 / Jan 2027) are retained as **illustrative governance intent**, not committed work.

---

## 11. Document set (v2) — what changed where

This handbook is the index and change-rationale. The individual capstone deliverables have each been updated in place so the submitted set is internally consistent (no document contradicts another):

| File | Status |
|---|---|
| `01-Pitch-v2.md` | Rewritten — scope corrected to AI-stack-only, dataset facts corrected |
| `02-Proposal-and-Scope-v2.md` | Rewritten — 2-role team (was 3), Flowise dropped |
| `03-Ethical-Action-Plan-v2.md` | Rewritten — roles consolidated to 2 people, fabrication check added |
| `03b-User-Research-v2.md` | **Corrected on re-audit** — discovery work (personas/interviews/hypotheses) unchanged, but the "Data Strategy Design" section still specified N=50/N=12, "Human Architect Override Ratio", and Flowise-based logging; all three now aligned with the rest of the doc set |
| `04-MVP-Scoping-v2.md` | Rewritten — Flowise dropped, seat/token cost split added |
| `06-Outcome-Goals-v2.md` | **Corrected on re-audit** — the "Teachable" bullet named Flowise specifically; fixed to match the simplified stack |
| `07-Roadmap-v2.md` | Rewritten — Flowise references replaced, pricing-sync claim made honest |
| `08-Technical-Work-Breakdown-v2.md` | Rewritten, then **corrected on re-audit** — a cost-calculation task was double-counted across two features; totals now reconcile with the priority matrix |
| `09-Effort-Informed-Prioritisation-v2.md` | Rewritten, then **corrected on re-audit** — its effort totals didn't match the Technical Work Breakdown for the same scope; both now sum to the same 15 days |
| `10-User-Stories-and-Task-Mapping-v2.md` | Rewritten — webhook tasks replaced with direct function calls |
| `atsa-prototype.html` | Rebuilt — fabrications removed, runs on real curated data |

*End of handbook v2. Together with the files above, this is now a fully reconciled, internally consistent capstone submission.*
