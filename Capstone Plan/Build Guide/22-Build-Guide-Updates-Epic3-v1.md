# Build Guide Updates — Epic 3

*Companion to `14-Build-Guide-Epic3-Blueprint-UI-v1.md`, following the same convention as `18-Build-Guide-Updates-Epic1-2-v1.md`: Epic 3 is marked Done on the kanban board, so rather than rewrite Card 3.1's original code sample (which doubles as the historical build record), the concrete edits below live here. Continues the Update A/B/C/D lettering from doc 18 (these are Update E/F/G) since they form one continuous change log across the app, even though this doc lives under Epic 3.*

**Why this doc exists:** after Update D (budget-aware costing) shipped and was live-verified, feedback comparing the app against a second prototype (`aasa-proto2.lovable.app`) suggested several UI improvements to Blocks A and C, plus a new explanatory section. Team decision, after a full feasibility pass: proceed with all of them except the "Best Match / Best for Budget" cost-forecast toggle, which was discarded as too large in scope for the value it added right now.

---

## Update E — Per-tool pricing + pricing-type toggle in Block A (Card 3.1 / 2.4)

**Files:** `app/logic/cost.py`, `app/pipeline.py`, `app/dashboard.py`

### What prompted this
Two related asks: (1) replace the grey secondary label under each recommended tool — previously just the pricing model name repeated (`SEAT`, `TOKEN`, `COMPUTE`) — with that tool's actual monthly price; (2) let the user filter the Recommended AI Stack list by pricing type (Recommended / Token / Seat / Compute / Free), mirroring the Lovable prototype's tab style.

Both need the same missing capability: `estimate_cost()` in `app/logic/cost.py` only ever computes a price for the single best-ranked token tool and the single best-ranked seat tool (the "one primary API + one assistant, never the sum" rule) — every other tool in `recommended_stack` has no computed cost anywhere. Showing a price under all 5 ranked tools, regardless of which one wins the headline Cost Forecast, needed that gap closed first.

### Implementation
**1. `app/logic/cost.py`** — added `estimate_all_tool_costs(recommended_tools, org_size_key)`, a new function alongside `estimate_cost()` (not a replacement) that runs every tool in the ranked list through the existing `_cost_for_tool()` helper and returns a dict keyed by canonical id. Reuses the exact same seat ceiling (`SEAT_CEILING`, Update D) and token-volume assumptions — this is a display convenience for Block A, not a second pricing model, and it doesn't change what `estimate_cost()` decides is the blueprint's headline `primary_api`/`assistant` pair.

**2. `app/pipeline.py`** — `run_pipeline()` now also calls `estimate_all_tool_costs(ranked_tools, inputs["org_size"])` and returns it as a new top-level `tool_costs` key, alongside the existing `cost_forecast`. Deliberately **not** added to `cost_forecast_for_prompt` — Card 2.6's LLM still only ever sees and describes the single decided pair, same principle as Update D.

**3. `app/dashboard.py`, `_render_stack_block()`** —
- Grey caption (previously `st.caption(pricing_model.upper())`) now shows `€{monthly_eur}/mo` when a tool has a computed price. `compute`-priced tools (no `monthly_eur` in `pricing.py` at all — usage-billed, e.g. Azure/AWS/GCP platforms) show **"Pay-as-you-go"**; `free`-priced tools (self-hosted/OSS, e.g. LangChain, Chroma) show **"Free / Self-hosted"** — both per team decision. A tool with no pricing entry at all falls back to "Pricing unavailable" (should never actually occur, since Card 2.3 requires every canonical id to have a pricing entry, but the fallback avoids a crash if that ever regresses).
- Added a `st.radio` pill toggle above the list — Recommended (default, full ranked list) / Token / Seat / Compute / Free — filtering `recommended_stack` by each tool's `model` field in `pricing.py`. The evidence-bar denominator (total matched cases) stays constant across all filter views, so the "seen in X/Y" percentage always reflects real-world evidence, not evidence within just the filtered subset. An empty filtered bucket (e.g. no free/OSS tool survived ranking for a given query) shows an info message rather than a blank block.

### Common pitfalls
- Don't confuse `tool_costs` with `cost_forecast` — they answer different questions. `cost_forecast` is "what's the one recommended primary API + assistant going to cost" (the headline number, budget-compared). `tool_costs` is "what would every ranked tool cost, individually" (Block A's per-row display). Keep both; don't merge them.
- `compute` and `free` tools will never have a `monthly_eur` value by design (see `pricing.py`'s own model-type comment) — the fallback labels are a UI concern, not a sign the cost function is broken.

### How to verify
- `estimate_all_tool_costs(['azure-platform', 'ibm-watsonx', 'azure-openai', 'google-cloud', 'ms365-suite'], 'mid')` returns a dict with 5 entries; `azure-platform`/`google-cloud` (`compute`) have `monthly_eur: None`, `ibm-watsonx`/`ms365-suite` (`seat`) and `azure-openai` (`token`) have real figures. Verified.
- Filtering the same 5-tool list by `model == "seat"` returns `['ibm-watsonx', 'ms365-suite']`; by `"compute"` returns `['azure-platform', 'google-cloud']`; by `"free"` returns `[]` (triggers the empty-state message). Verified.
- `python3 -m py_compile app/dashboard.py app/pipeline.py app/logic/cost.py` — verified, no syntax errors.
- **Not yet re-verified live in the running Streamlit app** — see the companion guide, `23-Build-Guide-Epic3-UI-Verification-v1.md`.

**Status: implemented, unit-verified. Live Streamlit re-test pending.**

---

## Update F — Case-count toggle + "Stack used" line in Block C (Card 3.1)

**Files:** `app/dashboard.py`

### What prompted this
Two asks: let the user choose how many matched cases to see (4 / 8 / All, mirroring the Lovable prototype), and show which specific tool(s) each case used, just above its source link, so a user can visually connect a case back to the exact recommendation it's evidence for.

### Implementation
**1. Count toggle** — `_render_case_references_block()` previously hardcoded `matched_cases[:4]`. Per `Intake-Output-Schema-v1.md`, the pipeline itself never capped this list — the cap was always UI-only — so this only needed a display-layer change: a `st.radio` toggle (4 / 8 / All) replaces the fixed slice. "All" is handled as no limit at all, not a literal count, since the real number varies per query.

**By team decision, `app/export.py`'s own independent `matched_cases[:4]` slice stays exactly as it is, unchanged by this update** — the plain-text export always starts at 4 regardless of what's toggled on-screen, so the exported blueprint stays predictable. Only the on-screen results view got the toggle.

**2. "Stack used" line** — added just above each case's source link. Deliberately shows only the tool(s) a case shares with the **current `recommended_stack`** (not the case's full raw `canonical_tools` list) — per team decision, so the line visibly ties each case back to the specific recommendation it's supporting, rather than listing every tool the case happened to mention (which could include tools nowhere in the current top-5). Kept in `recommended_stack`'s rank order for readability. If a case has zero overlap with the current recommendations, the line is omitted entirely rather than shown empty.

`_render_case_references_block()`'s signature changed to also accept `ranked_tools` (already available in `render_blueprint()` as `result["recommended_stack"]`) to support the intersection.

### Common pitfalls
- Don't compute the "Stack used" intersection against the case's raw `canonical_tools` — always intersect against `recommended_stack` specifically, or the line loses its "this justifies today's recommendation" meaning.
- Remember `app/export.py` was deliberately left untouched — don't "fix" its slice to match the dashboard toggle later without checking this decision first.

### How to verify
- A synthetic case with `canonical_tools = ['ibm-watsonx', 'chatgpt', 'azure-openai']` against `recommended_stack = ['azure-platform', 'ibm-watsonx', 'azure-openai', 'google-cloud', 'ms365-suite']` produces `"Stack used: IBM watsonx (Assistant/AI/Orchestrate), Azure OpenAI Service"` — `chatgpt` correctly excluded (not in the current stack), order matches `recommended_stack`'s rank order. Verified.
- **Not yet re-verified live in the running Streamlit app** — see `23-Build-Guide-Epic3-UI-Verification-v1.md`.

**Status: implemented, unit-verified. Live Streamlit re-test pending.**

---

## Update G — "How the recommendation is made" section (Card 3.1)

**Files:** `app/dashboard.py`

### What prompted this
A comparative look at the Lovable prototype's own methodology/limitations section suggested adding an equivalent here — a plain-English explanation of the pipeline (retrieve → rank & price → trace) plus an honest "known limitations" box, placed between the Export block and the Feedback section.

### Implementation
New `_render_methodology_block()` function, called at the end of `render_blueprint()` — right after the existing Export block, before `render_blueprint()` returns. This lands it exactly between Export and Feedback: `app/intake.py` calls `render_blueprint(...)` and then `render_trust_survey()` back to back, so anything appended inside `render_blueprint()` sits before Feedback without touching `intake.py` at all.

Content is written with this project's own real numbers, not copied from Lovable's (their "2,511 raw variants" is their dataset, not ours):
- **01 Retrieve** — 3,023 real case studies, Chroma vector search, privacy posture as a deterministic hard filter before ranking.
- **02 Rank & price** — 88.7% canonical-tool coverage (Card 2.1's real, disclosed number), the hand-built pricing table's distinction between per-seat/per-token/usage-billed/free tools.
- **03 Trace** — every recommended tool links back to real cases with reported outcomes and source URLs.
- **Known limitations box** — illustrative/manually-curated pricing (matches `pricing.py`'s own disclaimer), directional-not-certified compliance filtering (matches `filter.py`'s own docstring: "NOT a compliance certification"), the case library's real skew toward large-scale enterprise deployments, and the population-level (not per-case) Stack Overflow-grounded seat/usage assumptions (Update C/D).

### Common pitfalls
- Keep this section's numbers in sync if the dataset or coverage percentage ever changes (e.g. a future re-run of `scripts/normalise_cases.py` with an expanded `ALIAS_MAP`) — it's hand-written prose, not computed from the live data, so it won't update itself.

### How to verify
- `python3 -m py_compile app/dashboard.py` — verified, no syntax errors.
- **Not yet visually reviewed in the running Streamlit app** (does the 3-column layout read well, does the limitations box's Markdown bullet list render correctly) — see `23-Build-Guide-Epic3-UI-Verification-v1.md`.

**Status: implemented, not yet visually verified live.**
