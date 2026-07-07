# MVP Effort-Informed Prioritisation Matrix (v2)
*Supersedes the original. Fixes: effort re-estimated per the corrected Technical Work Breakdown; the unmeasurable "Human Architect Override Ratio" metric is replaced; WBS tasks rewritten without Flowise.*

| Feature | Estimated Effort | Priority | Reason |
|---|---|---|---|
| Guided AI Intake Form (Streamlit, 5 fields, validation, direct pipeline call) | 3.5d | 🟩 MUST HAVE | Essential to capture the 5 constraints |
| Retrieval & Matching Engine (normalise tool names, embed, filter, rank, prompt) | 7.5d | 🟩 MUST HAVE | Core value; matches constraints to real deployment outcomes |
| Cost Forecast (seat + token aware parser, 24-tool pricing table) | 1.5d | ⚙️ SHOULD HAVE | Addresses risk-averse users' need for financial clarity; now correctly split by pricing model, not a single token assumption |
| 3-Block Results Display & Analytics (UI render + export + telemetry) | 2.5d | ⚙️ SHOULD HAVE | Enables trust verification and drop-off tracking |
| Plain-language cost export | 1d | 💡 COULD HAVE | High value for non-technical CEOs, not required for validation |
| One-Click Code Boilerplate | 2d | 💡 COULD HAVE | Nice accelerator, out of advisory scope for MVP |
| Live/continuous pricing scraping | 4d+ | 🚫 WON'T HAVE | Unnecessary complexity; a manually curated table is sufficient and honestly labelled illustrative |

**Total Must+Should effort:** 15 days — this now sums exactly to the Technical Work Breakdown v2's feature-by-feature total (3.5 + 7.5 + 1.5 + 2.5), instead of being an independently-derived, lower estimate as in the previous draft. **Buffer:** +30% (≈4.5 days). Across a 2-person × 3-week window that's ≈19.5 person-days of demand against ≈30 person-days available — workable, but it confirms the Should-Haves are the first thing we'd cut if behind schedule, never the retrieval core.

## Hierarchical Work Breakdown Structure

### 🎯 Outcome Goal
In 3 weeks, startup founders and product leads receive automated, data-backed AI stack blueprints, with a target of ≥75% rating the recommendations as more trustworthy and cost-transparent than manual forum research — measured against **5–8 real test users**, not the original N=50/N=12 targets, which weren't achievable by a 2-person team in this window.

### 📁 Epic 1: Intelligent Intake & Profile Contextualisation
- **Deliverable 1.1: Streamlit Client Form UI**
  - Task 1.1.1: Dark-mode CSS grid styling matching the neo-industrial direction from user research.
  - Task 1.1.2: Dropdowns for Org Size and Industry (our own taxonomy, no external schema join required).
  - Task 1.1.3: Validation routines blocking submission on empty/invalid fields.
- **Deliverable 1.2: Direct Pipeline Handoff** *(replaces "Intake Webhook Gateway" — no external orchestration service to call)*
  - Task 1.2.1: In-process function call from form submit to the retrieval pipeline.
  - Task 1.2.2: Loading state during execution.

### 📁 Epic 2: Retrieval & Costing Engine
- **Deliverable 2.1: Case Knowledge Base**
  - Task 2.1.1: Load and normalise the 3,023-row CSV using the tool-name alias map. *(Corrected from "process 3,000+ raw markdown files.")*
  - Task 2.1.2: Embed normalised case text into a local Chroma vector store.
- **Deliverable 2.2: Retrieval & Filtering Pipeline** *(replaces "Flowise Routing Orchestration Pipeline")*
  - Task 2.2.1: Deterministic Python privacy filter applied before ranking.
  - Task 2.2.2: Few-shot system prompt constraining the LLM to summary prose only.
- **Deliverable 2.3: Cost Parser**
  - Task 2.3.1: 24-tool pricing dictionary tagged token / seat / compute / free.
  - Task 2.3.2: Cost function computing one primary API + one assistant estimate against user budget.

### 📁 Epic 3: Actionable Blueprint UI
- **Deliverable 3.1: 3-Block Output Display**
  - Task 3.1.1: Render Stack / Cost / Case Reference blocks with evidence bars and source links.
  - Task 3.1.2: Clipboard export button.
- **Deliverable 3.2: Verification Telemetry**
  - Task 3.2.1: Log form completion velocity and exit points.
  - Task 3.2.2: Post-generation 1–5 trust rating popup.

## Metrics — corrected (replaces the unmeasurable original)
The original matrix's implied "Human Architect Override Ratio < 15%" requires an on-call expert architect to grade every output, which a 2-person team doesn't have. Replaced with metrics we can actually run:

| Metric | Target | How |
|---|---|---|
| Trust score (post-session) | ≥4/5 median | Micro-survey |
| Net value ("saved me research time") | ≥70% yes | Micro-survey |
| Blueprint export rate | ≥40% | Telemetry event |
| Compliance-rule pass rate | 100% | Automated check — every recommended tool respects the deterministic filter (this we *can* verify ourselves, unlike a human-override ratio) |
