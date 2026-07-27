# 4-Week Day-by-Day Action Plan (v1)
### AI-Assisted Stack Architect (AASA)
*Built from the reconciled Handbook v2 (§7, §10), Proposal & Scope v2 (Weeks 1-4), and the User Story/Task Mapping v2 (task IDs, files, dependencies). Where docs' effort estimates differ, this plan follows the Handbook's pacing (single source of truth) while keeping doc-10's task IDs for traceability.*

**Team:** Person A — Data & Logic · Person B — UI, Validation & PM Lead. Both share testing, ethics checkpoints, and the pitch.
**Cadence:** 7 days/week numbered continuously (Day 1–28); weekends are lighter buffer/catch-up days, not days off by default — shift load as needed.

---

## Week 1 — Guardrails & Data Foundation

| Day | Person A (Data & Logic) | Person B (UI, Validation & PM) | Joint / Milestone |
|---|---|---|---|
| 1 | Review the 3,023-row CSV; confirm no PII; set up repo, Python venv, Chroma. | Draft test-user recruiting post + interview guide. | Kick off; agree on working agreement. |
| 2 | Begin tool-name alias map: inventory the 2,511 distinct tool strings. | Start recruiting outreach for 5–8 real testers (moved up from Week 3). | Draft & sign off the 1-page **Project Charter** (scope: AI stack only, no infra, no code-gen, no compliance claims). |
| 3 | Continue alias map: group variants → canonical ids; log unmatched strings for review. | Finalize the 5-field input / 3-block output schema (Workflow, Industry, Org Size, Privacy, Budget → Stack, Cost, Case Refs). | Share schema with A — this becomes the pipeline contract. |
| 4 | Finish alias map v1; verify ≥90% row coverage against target ~24 canonical tools. | **Task 1.2** — map Org Size/Industry to dropdown taxonomy (`app/data/options.py`). | — |
| 5 | **Task 2.3** — draft 24-tool pricing table, tagged token/seat/compute/free. | **Task 1.1** — start Streamlit dark-mode CSS grid intake skeleton (`app/intake.py`). | — |
| 6 *(buffer)* | **Task 2.1** — normalise the CSV using the alias map (`scripts/normalise_cases.py`); confirm unmatched-string log. | Ethics checkpoint prep (Owner: A) — confirm no accounts, inputs are anonymous constraints only. | — |
| 7 *(buffer)* | Ethics — finalize **Week 1 data-minimisation** confirmation: no PII stored anywhere. | Confirm ≥3 recruiting candidates lined up for Week 3 testing. | **Checkpoint:** alias-map coverage, pricing table draft, and schema all signed off before Week 2 starts. |

---

## Week 2 — Logic System

| Day | Person A (Data & Logic) | Person B (UI, Validation & PM) | Joint / Milestone |
|---|---|---|---|
| 8 | **Task 2.2** — embed normalised cases into Chroma (`scripts/embed_cases.py`); sanity-check retrieval on sample queries. | **Task 1.3** — frontend validation logic (`app/validators.py`). | — |
| 9 | Tune chunking/retrieval quality; confirm cases returned match domain of test queries. | **Task 1.4** — direct in-process pipeline call (`app/pipeline.py`), wiring form submit to A's backend contract. | Diagram the full pipeline (input → filter → retrieve → cost → LLM) in Mermaid. |
| 10 | **Task 2.5** — write the deterministic privacy-filter rule matrix (e.g. `IF privacy == 'regulated' THEN restrict to governable platforms`) in `app/logic/filter.py`. | Concept-test the honest prototype (`aasa-prototype.html`) with 2–3 early users. | — |
| 11 | Unit-test the privacy filter against 2–3 known compliance scenarios. | Debrief concept-test feedback; patch intake copy/UX; continue recruiting for Week 3. | — |
| 12 | **Task 2.4** — cost computation, token- vs. seat-aware (`app/logic/cost.py`); unit tests on pricing-table units. | Scaffold telemetry event plan (groundwork for Task 3.3). | — |
| 13 | **Task 2.6** — engineer the few-shot summary prompt (prose-only constraint) in `app/logic/prompt.py`; validate against 10 test runs for template drift. | Ethics support — draft short model card: dataset's enterprise-productivity skew; confirm ranking reflects real frequency, not preference. *(Owner: A, supported by B)* | — |
| 14 | Full backend dry run: normalise → embed → filter → rank → cost → prompt, on 3 sample profiles. | Same dry run, from the UI side. | **Checkpoint:** log defects; confirm 5–8 real testers are scheduled for Week 3. |

---

## Week 3 — Build the MVP and Test It

| Day | Person A (Data & Logic) | Person B (UI, Validation & PM) | Joint / Milestone |
|---|---|---|---|
| 15 | Fix Day-14 defects; finalize pipeline integration (`app/pipeline.py`). | **Task 3.1** — render the 3-block layout (Stack / Cost / Case Refs) in `app/dashboard.py`. | — |
| 16 | Add per-query latency / token-usage logging. | Continue Task 3.1 — evidence bars, source links; test layout at 375px mobile width. | — |
| 17 | Full pipeline wiring: form → pipeline → 3-block render. | Same — end-to-end smoke test together. | Fix integration bugs found in the smoke test. |
| 18 | Polish alias-map edge cases surfaced by testing; monitor the unmatched-tool log. | **Task 3.2** — clipboard export (`app/export.py`) + **Task 3.4** — trust survey modal (`app/survey_modal.py`). | — |
| 19 | Run the automated **compliance-rule pass-rate check** (target: 100%) across test profiles. | **Task 3.3** — finish session telemetry: form-start→results-view timing, field abandonment (`app/analytics/tracker.py`). | — |
| 20 | Sit in on user sessions; fix live bugs as they surface. | Run **real user testing** — 5–8 recruited testers; capture trust score, net-value question, export-rate telemetry live. | Log every failure as it happens. |
| 21 | Patch retrieval/cost/prompt issues from Day 20, highest-impact first. | Patch UI/copy issues from Day 20. | Ethics checkpoint (Owner: B) — confirm testing included a non-technical founder and a non-native English speaker; check output is legible without jargon. |

---

## Week 4 — Package, Roadmap, Pitch

| Day | Person A (Data & Logic) | Person B (UI, Validation & PM) | Joint / Milestone |
|---|---|---|---|
| 22 | Compile final metrics: trust-score median, net-value %, export rate, compliance pass rate. | Freeze feature scope — no more changes except critical bug fixes. | — |
| 23 | Write up dataset limitations (enterprise-productivity skew, no org-size join key). | Write up product limitations (illustrative pricing, directional-not-certified compliance). | Consolidate into a "Known Limitations" section (roadmap items, not MVP promises). |
| 24 | Prepare architecture slide content (pipeline steps, dataset stats: 3,023 cases, 41 tools, alias-map coverage). | Draft 10-slide pitch outline: Problem → Solution → Architecture → Real Test Results → Risk Management → Roadmap. | — |
| 25 | Build architecture + results slides. | Build problem/solution/roadmap slides. | Assemble into one deck; sanity-check numbers match the metrics doc. |
| 26 | Final **responsible-AI checklist** — confirm no fabricated trust signals anywhere in the prototype or deck. | Same checklist, deck side. | Ethics checkpoint (Owner: both). |
| 27 | Full pitch rehearsal — timing run-through. | Full pitch rehearsal — timing run-through. | Tighten narrative based on rehearsal feedback. |
| 28 | Final consistency pass on all technical docs. | Final consistency pass on all PM/pitch docs. | **Submit:** confirm docs 01–11 + Handbook + prototype agree with each other; submit capstone. |

---

## How this maps back to the source docs
- **Task IDs & files** (1.1–3.4) come from `10-User-Stories-and-Task-Mapping-v2.md` — check that doc for full acceptance criteria per task.
- **Week-level pacing** follows `AASA-Project-Handbook-v2.md` §7 (the reconciled source of truth) and `02-Proposal-and-Scope-v2.md`'s day ranges.
- **Ethics checkpoints** (Weeks 1–4, owners A/B/both) come from Handbook §10.
- **Metrics captured Day 20 & compiled Day 22** come from Handbook §8.
- Kanban cards for every task in this plan are on the board (`AASA-Kanban-Board.html`) — move cards to "In Progress"/"Done" as each day's work lands.
