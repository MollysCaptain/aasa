# Intake → Output Schema (v1)

**Status:** shared reference for Cards 1.1–1.4 (intake) and Card 1.4/Epic 2 (pipeline). Written by cross-checking the actual code (`app/intake.py`, `app/data/options.py`, `app/validators.py`, `app/pipeline.py`) against the Epic 2 build guide's pipeline-wiring section — not guessed from memory. Where the two disagreed, this doc says which one is the real, intended contract and flags the gap (see "Implementation status" at the bottom).

---

## Inputs (5 fields)

| Field | Type | Example values |
|---|---|---|
| `workflow` | string | `"Customer Service"`, `"IT & Platform"`, `"Any workflow"` |
| `industry` | string | `"Technology"`, `"Healthcare"`, `"Any industry"` |
| `org_size` | string (short key) | `"solo"`, `"startup"`, `"smb"`, `"mid"`, `"ent"` |
| `privacy` | string (short key) | `"standard"`, `"regulated"` |
| `budget` | number (EUR/month) | `800`, `1500` — must be `> 0`, not just `>= 0` |

Notes, field by field:

- **`workflow`** — `st.selectbox("Target AI Workflow", WORKFLOWS)` (`app/intake.py:60`). The dropdown label *is* the stored value — no separate short key. Full option set: 18 canonical domains derived from the real case dataset, plus `"Any workflow"` (`app/data/options.py:57–76`).
- **`industry`** — `st.selectbox("Industry", INDUSTRIES)` (`intake.py:61`). Same pattern: label is the value. 24 real dataset values + `"Any industry"` (`options.py:26–51`).
- **`org_size`** — `st.selectbox(..., options=list(ORG_SIZES.keys()), format_func=lambda k: ORG_SIZES[k])` (`intake.py:62–66`). The UI shows a friendly label ("Startup (5–20 people)") but the form stores the short key (`"startup"`). Full key→label mapping in `options.py:11–17`.
- **`privacy`** — `st.radio(..., options=list(PRIVACY_POSTURES.keys()), ...)` (`intake.py:67–74`). Validated to be exactly `"standard"` or `"regulated"`, nothing else (`app/validators.py:17`).
- **`budget`** — `st.number_input("Monthly Budget (€)", min_value=0, step=50, value=800)` (`intake.py:75–78`). **Gotcha:** the widget's own `min_value=0` allows 0, but `validate_intake()` separately requires `budget_value > 0` and rejects exactly 0 (`validators.py:20–27`) — so "0" passes the widget but fails validation with "Monthly budget must be greater than zero."

All five keys are passed into the pipeline exactly as named above — `run_pipeline({"workflow": ..., "industry": ..., "org_size": ..., "privacy": ..., "budget": ...})` (`intake.py:90–94`). Cards 1.1–1.4 should treat these 5 key names as fixed; Epic 2's functions all take them by these names.

---

## Output (3 blocks)

The pipeline's real return dict has 5 top-level keys, not 3 — the task's 3 "blocks" map onto 3 of them, plus 2 more (`summary_text`, `llm_metrics`) that Epic 3 also renders but that don't fit neatly into "stack / cost / cases." All 5 are documented here so nothing gets missed when wiring Cards 1.1–1.4 to Epic 2.

### A. Recommended stack — `recommended_stack`

`list[str]` of canonical tool ids, ranked best-first, top 5 (`rank_tools_by_frequency(filtered_cases, top_n=5)`, `13-Build-Guide-Epic2-Retrieval-v1.md:786–793`).

Example: `["openai-api", "chatgpt", "github-copilot"]`

**Important correction to the task's draft template:** this list does **not** carry an evidence count per tool — it's just the ranked ids. The "seen in 3/5 matched cases" evidence bar is computed *at render time* by the UI, by cross-referencing each tool id against `matched_cases[i]["canonical_tools"]` (`14-Build-Guide-Epic3-Blueprint-UI-v1.md:57–64`), not stored in the pipeline output. If a future card needs the evidence count available *before* the UI layer (e.g. for the export view or a telemetry log), that's a real gap to design for — right now it only exists as a UI-local calculation, computed independently wherever it's needed.

### B. Cost forecast — `cost_forecast`

```
{
  "primary_api": { "tool": str, "model": "token"|"seat"|"compute"|"free",
                    "monthly_eur": float|None, "assumption": str } | None,
  "assistant":   { same shape } | None,
  "disclaimer":  str,
  "total_monthly_eur": float|None,
  "budget": float|None,
  "within_budget": bool|None,
  "budget_delta_eur": float|None
}
```

(`estimate_cost()`, `13-Build-Guide-Epic2-Retrieval-v1.md:672–690`, updated by Update D in `18-Build-Guide-Updates-Epic1-2-v1.md`.) When a tool has no pricing entry, or is `"compute"`/`"free"`-priced, its sub-dict has `"monthly_eur": None` and a `"note"` key instead of `"assumption"` (`...:645–667`).

**The last four keys are new (Update D)** — previously `budget` was collected on the intake form and validated (`> 0`) but never read again anywhere downstream; the forecast could come back many multiples over budget with no comparison or flag at all. Now:
- `total_monthly_eur` — sum of whichever of `primary_api`/`assistant` are actually costed (skips `None`/uncosted entries). `None` if nothing was costed.
- `budget` — passed straight through from the intake form for convenience at render/prompt time.
- `within_budget` — `total_monthly_eur <= budget`, or `None` if either side is `None` (e.g. an ad-hoc call to `estimate_cost()` that didn't pass a budget).
- `budget_delta_eur` — `budget - total_monthly_eur` (negative when over budget), or `None` under the same conditions as above.

**Important: this is comparison-only, not budget-fitting.** `estimate_cost()` never drops or swaps tools to force a result under budget — the ranked tool list is Card 2.5's decision, not this card's. The forecast can still legitimately come back over budget; the point of these fields is to make that visible and honest (in the UI and in Card 2.6's summary) rather than silent.

Worked example (startup, `["openai-api", "chatgpt", "langchain"]`, budget €1200):

```json
{
  "primary_api": {
    "tool": "openai-api", "model": "token", "monthly_eur": 43.75,
    "assumption": "~10M tokens/mo (75% in / 25% out) at €2.5/€10.0 per M tokens"
  },
  "assistant": {
    "tool": "chatgpt", "model": "seat", "monthly_eur": 960.0,
    "assumption": "16 seats x €60.0/seat/mo"
  },
  "disclaimer": "Pricing shown is illustrative and may be out of date. Always verify current pricing on the vendor's official page before budgeting.",
  "total_monthly_eur": 1003.75,
  "budget": 1200,
  "within_budget": true,
  "budget_delta_eur": 196.25
}
```

**Rule, not a detail:** at most one `primary_api` (the first token-priced tool in the ranked list) and one `assistant` (the first seat-priced tool) — deliberately never a sum-per-tool across every recommended tool (`...:672–676`, and originally called out as a mistake to avoid in `08-Technical-Work-Breakdown-v2.md`). `total_monthly_eur` is a sum of just these two figures, not a change to that rule.

**Also new (Update D): seat counts are now capped by a `SEAT_CEILING` (currently 25) regardless of org-size band** — see `app/logic/cost.py` and Update D for why (a flat per-org-size seat assumption was costing a single-workflow query, e.g. "Customer Service," as if the whole company adopted the tool).

### C. Case references — `matched_cases`

`list[dict]`, each case shaped:

```
{ "case_id": str, "organization": str, "title": str, "industry": str,
  "source_url": str, "canonical_tools": list[str] }
```

(`13-Build-Guide-Epic2-Retrieval-v1.md:1006–1013`, confirmed again at `14-Build-Guide-Epic3-Blueprint-UI-v1.md:134`.)

**Correction to the task's draft template:** the field is `organization`, not `org`.

**On "up to 4":** the pipeline itself does not cap this list — it returns every case that survived de-dup (one entry per `case_id`) and the privacy filter, from an initial retrieval of 15 chunks (`...:988–1000`). The **4-case cap is UI-only** — both the results page and the export view independently slice `matched_cases[:4]` for display, "per the prototype's own convention" (`14-Build-Guide-Epic3-Blueprint-UI-v1.md:103, 181`). So: Cards 1.1–1.4/Epic 2 should pass through the *full* filtered list; Epic 3 does the slicing to 4, not the pipeline.

### Also part of the output (not one of the 3 "blocks," but real)

- **`summary_text`** (`str`) — the LLM-generated plain-English paragraph from Card 2.6, rendered above Block A (`intake.py`-era pattern; `14-Build-Guide-Epic3-Blueprint-UI-v1.md:45`).
- **`llm_metrics`** (`dict`) — `{"duration_seconds": float, "prompt_tokens": int, "completion_tokens": int, "tokens_per_second": float|None}`, straight from `generate_summary()`'s return value, kept for Card 3.3's telemetry log (`13-Build-Guide-Epic2-Retrieval-v1.md:1032–1064`).

Full return shape:

```python
{
    "recommended_stack": [...],   # Block A
    "cost_forecast": {...},       # Block B
    "matched_cases": [...],       # Block C (unsliced)
    "summary_text": "...",
    "llm_metrics": {...},
}
```

---

## Implementation status (check before trusting the live code)

Epics 1–3 are all wired in and merged into `Ash2` — this doc now matches the live `app/pipeline.py`/`app/logic/cost.py`/`app/logic/prompt.py`, not Epic 1's original placeholder. (This section previously described the placeholder pipeline from before Epic 2 was wired in; corrected here as a housekeeping fix while this file was open for Update D, since it had gone stale without anyone noticing.)

Known, disclosed limitations of the current implementation, as of Update D:
- `total_monthly_eur`/`within_budget`/`budget_delta_eur` compare the forecast against budget but never alter tool selection to force a fit — an over-budget result is a legitimate, honestly-flagged outcome, not a bug to hide.
- `SEAT_CEILING` (25, in `app/logic/cost.py`) is a flat, hand-picked stopgap applied uniformly regardless of workflow — not a real per-workflow headcount estimate. See Update D in `18-Build-Guide-Updates-Epic1-2-v1.md` for the fuller "workflow-fraction table" alternative (Option A) that was considered and deliberately deferred.
