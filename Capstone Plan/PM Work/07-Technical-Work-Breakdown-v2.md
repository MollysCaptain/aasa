# Technical Work Breakdown (v2)
*Supersedes the original. Fixes: the original rated "parse/clean 3,000+ raw text files" as Complex (4 days) — the source is one clean, fully-populated CSV, so this task barely exists. The real, previously-uncosted task — tool-name normalisation — is now costed explicitly. All Flowise-specific tasks are replaced with plain-Python equivalents, removing the webhook/cross-origin risk entirely.*

## Feature 1: Guided AI Intake Flow

| Area | Description | Effort | Risks |
|---|---|---|---|
| Data / Model | Map Org Size / Industry to structured dropdown options (no survey-schema join needed — this is just our own taxonomy). | S (0.5d) | Category list too coarse/fine for real users — validate in Week-1 recruiting conversations. |
| Backend | Input validation ensuring all 5 fields are populated and budget is numeric before the pipeline runs. | S (0.5d) | Minimal — no external service dependency now that Flowise is removed. |
| Frontend | Streamlit dark-mode form, 5 fields, matching the "neo-industrial" direction from user research. | M (1.5d) | Drop-off if the form feels long — mitigate by defaulting sensible values. |
| Integration | Direct in-process function call from form submit to the retrieval pipeline. **No webhook, no cross-origin request** — this removes a whole risk category from v1. | S (0.5d) | None significant; same process, same runtime. |
| Analytics | Streamlit session-state or lightweight event log for form-start/submit timestamps and field changes. | S (0.5d) | Reduced telemetry granularity vs. a dedicated tool — acceptable trade-off for the extra reliability. |

## Feature 2: Retrieval & Matching Logic Engine

| Area | Description | Effort | Risks |
|---|---|---|---|
| Data / Model | **Corrected from v1.** The source is one clean 3,023-row CSV, not raw files — direct `pandas`/`csv` read. The real work is the **tool-name normalisation map** (2,511 raw variants → ~24 canonical tools) and the accompanying pricing table. | M (2d) — down from the original C/4d, because parsing itself is trivial; the days go to the alias map and its edge cases. | Alias map misses a variant → tool undercounted in ranking. Mitigate: log unmatched strings and review weekly. |
| Backend | Deterministic privacy filter (plain Python function) applied before ranking; frequency-based ranking. *(Cost calculation lives in Feature 3 only — v1 of this table double-counted it in both features.)* | S (1.5d) | Filter too strict/loose — validate against 2–3 known compliance scenarios manually. |
| Frontend | Loading state while retrieval + LLM summary run. | S (0.5d) | Minimal — single local call, not a remote orchestration hop. |
| Integration | Embed the 3,023 normalised case descriptions into a local Chroma vector store (one-off script, rerun only if data changes). | M (1.5d) — down from the original "interface vector store into Flowise" M/2d, since there's no orchestration layer to interface with. | Chunking strategy affects retrieval quality — start with case-level chunks (already short), no complex splitting needed. |
| Analytics | Log per-query latency and (if using a paid API) token usage for cost/efficiency tracking. | S (0.5d) | Only relevant once the LLM summary step is live. |

## Feature 3: 3-Block AI Blueprint UI

| Area | Description | Effort | Risks |
|---|---|---|---|
| Data / Model | Few-shot prompt template constraining the LLM to prose-only output — it never selects tools or computes prices (those come from deterministic code). | M (1.5d) | Model drifting into inventing a tool name — mitigate by validating LLM output tool mentions against our canonical list before display. |
| Backend | Cost parser: per-token (input/output €/M tokens × assumed volume) or per-seat (€/seat × team size), clearly separated — **this distinction was missing in v1's single token-cost model.** | M (1.5d) | Currency/unit mixing — covered by unit tests on the pricing table. |
| Frontend | Render the 3-block layout (Stack / Cost / Case References) with evidence bars and source links. | M (1.5d) | Visual clutter on mobile — test at 375px width. |
| Integration | "Copy to clipboard" export of the blueprint text. | S (0.5d) | Clipboard API permission edge cases on some browsers — provide a manual-select fallback. |
| Analytics | Track export-click events and the post-session 1–5 trust rating. | S (0.5d) | Missed submissions if a user closes the tab early — acceptable, not a blocker metric. |

## Summary of MVP Scope Distribution (corrected)
- **Total sized tasks:** 15 (unchanged count, effort re-estimated).
- **Development allocation:** ≈ **15 days** of combined effort — down from the original ~24 days, because (a) the "clean 3,000+ raw files" task doesn't exist as described, and (b) removing Flowise eliminates several integration tasks entirely rather than just shrinking them. (Feature 1: 3.5d · Feature 2: 6d · Feature 3: 5.5d. This total is cross-checked against the Effort-Informed Prioritisation Matrix v2, which reorganises the same 15 days by MoSCoW priority rather than by feature — the two now sum to the same figure.)
- **Critical path:** the tool-name normalisation map and the deterministic privacy filter — both correctness-critical and both now explicitly costed, unlike in v1.
- **Buffer:** +30% (not the original 20%), because two of us are still learning Chroma and prompt-constraint techniques even though the data-cleaning risk has gone down.
