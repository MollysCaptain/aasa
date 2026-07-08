# User Story and Task Mapping Matrix (v2)
*Supersedes the original. Fixes: removes all Flowise webhook/endpoint tasks in favour of direct in-process Python calls; corrects file/component names to match the simplified stack; effort re-estimated to match the Technical Work Breakdown v2.*

## 🎯 Outcome Goal
In 3 weeks, startup founders and product leads receive automated, data-backed AI stack blueprints, targeting ≥75% rating the recommendations as more trustworthy and cost-transparent than manual forum research — validated against 5–8 real test users.

## 📁 Epic 1: Intelligent Intake & Profile Contextualisation
**User Story:** As an early-stage product lead, I want to submit my AI workflow, industry, org size, privacy needs, and budget so I don't waste weeks scrolling forums.
**Acceptance Criteria:** 5-field Streamlit form → validated on submit → passed directly (in-process) to the retrieval pipeline.

| Task | Description | File/Component | Input → Output | Effort | Depends On | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| 1.1 | Render input controls & dark-mode CSS grid | `app/intake.py` | — → rendered form | 0.5d | None | Form renders responsively without truncation |
| 1.2 | Map Org Size / Industry to dropdown options (our own taxonomy) | `app/data/options.py` | Raw category list → clean dropdowns | 0.5d | 1.1 | Dropdowns populate with the 21 industries / 5 size bands in the curated dataset |
| 1.3 | Frontend validation, block bad submissions | `app/validators.py` | Submitted fields → localized warning or pass | 0.5d | 1.2 | Invalid submission halted with a clear inline message |
| 1.4 | **Direct pipeline call** *(replaces "webhook endpoint payload delivery")* | `app/pipeline.py` | Validated form state → in-process function call | 0.5d | 1.3 | Pipeline receives a clean, typed dict — no serialization/webhook step to fail |

**Learning Goal:** form/state design and building a clean internal taxonomy — without depending on an external schema we don't actually have (there is no OrgSize field in the case library to join against).

## 📁 Epic 2: Retrieval & Costing Engine
**User Story:** As a non-technical CEO, I want my AI tool selections checked against real deployments and clear pricing so I can avoid hidden costs.
**Acceptance Criteria:** pipeline loads the case CSV → normalises tool names → applies privacy filter → ranks by frequency → computes cost → returns clean structured output.

| Task | Description | File/Component | Input → Output | Effort | Depends On | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| 2.1 | Load and normalise the case CSV via the alias map | `scripts/normalise_cases.py` | Raw CSV (3,023 rows) → normalised rows with canonical tool ids | 1.0d | None | ≥90% of rows resolve to at least one canonical tool; unmatched strings logged for review |
| 2.2 | Embed normalised case text into Chroma | `scripts/embed_cases.py` | Normalised rows → vector store records | 1.0d | 2.1 | Retrieval for a test query returns cases from the correct domain with reasonable relevance |
| 2.3 | Hardcode the 24-tool pricing table | `app/logic/pricing.py` | Public pricing pages → typed Python dict tagged token/seat/compute/free | 0.5d | None | All canonical tool ids resolve to a pricing entry |
| 2.4 | Cost computation (token- and seat-aware) | `app/logic/cost.py` | Recommended tools + org size → monthly estimate | 0.5d | 2.3 | Seat-priced and token-priced tools produce correctly-typed, non-conflated estimates |
| 2.5 | **Deterministic privacy filter** *(replaces "configure Flowise orchestration routing")* | `app/logic/filter.py` | Retrieved cases + privacy posture → filtered case/tool set | 1.0d | 2.2 | Regulated posture excludes consumer-only assistants in 100% of test cases |
| 2.6 | Few-shot summary prompt | `app/logic/prompt.py` | Filtered, ranked results → structured markdown summary | 1.0d | 2.5 | Output matches the fixed 3-block template without drift across 10 test runs |

**Learning Goal:** cleaning and normalising a real messy taxonomy, tuning vector retrieval, and enforcing deterministic constraints on an LLM — without adding an orchestration tool that isn't needed for this pipeline shape.

## 📁 Epic 3: Actionable Analytics Dashboard UI
**User Story:** As a technical team lead, I want to see my recommended architecture with real case references so I can validate it with my developers.
**Acceptance Criteria:** Streamlit renders the 3-block layout → "copy blueprint" export → 1–5 trust survey popup.

| Task | Description | File/Component | Input → Output | Effort | Depends On | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| 3.1 | Render the 3-block layout | `app/dashboard.py` | Structured summary → visual blocks | 1.0d | 2.6 | Renders cleanly with clear section hierarchy |
| 3.2 | Clipboard export handler | `app/export.py` | Export click → text on clipboard | 0.5d | 3.1 | Full blueprint text copied correctly |
| 3.3 | Lightweight session telemetry | `app/analytics/tracker.py` | Session events → local log | 0.5d | 1.4 | Tracks form-start to results-view timing |
| 3.4 | Post-generation trust survey | `app/survey_modal.py` | Results shown → 1–5 rating captured | 0.5d | 3.1 | Score delivered cleanly to the feedback log |

**Learning Goal:** designing a readable, evidence-linked interface and tracking the handful of metrics that actually validate (or falsify) our core hypothesis.
