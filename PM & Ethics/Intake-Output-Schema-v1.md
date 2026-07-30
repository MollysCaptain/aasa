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

- **`workflow`** — `st.selectbox("Target AI Workflow", WORKFLOWS)` (`app/intake.py:556`). The dropdown label *is* the stored value — no separate short key. Full option set: 18 canonical domains derived from the real case dataset, plus `"Any workflow"` (`app/data/options.py:65–84`).
- **`industry`** — `st.selectbox("Industry", INDUSTRIES)` (`intake.py:557`). Same pattern: label is the value. 24 real dataset values + `"Any industry"` (`options.py:34–59`).
- **`org_size`** — `st.selectbox(..., options=list(ORG_SIZES.keys()), format_func=lambda k: ORG_SIZES[k])` (`intake.py:558–563`). The UI shows a friendly label ("Startup (11-100 people)") but the form stores the short key (`"startup"`). Full key→label mapping in `options.py:19–26`.
- **`privacy`** — `st.radio(..., options=list(PRIVACY_POSTURES.keys()), ...)` (`intake.py:564–571`). Validated to be exactly `"standard"` or `"regulated"`, nothing else (`app/validators.py:17`).
- **`budget`** — `st.number_input("Monthly Budget (€)", min_value=0, step=50, value=800)` (`intake.py:588–591`). **Gotcha:** the widget's own `min_value=0` allows 0, but `validate_intake()` separately requires `budget_value > 0` and rejects exactly 0 (`validators.py:20–27`) — so "0" passes the widget but fails validation with "Monthly budget must be greater than zero."

All five keys are passed into the pipeline exactly as named above — `run_pipeline({"workflow": ..., "industry": ..., "org_size": ..., "privacy": ..., "budget": ...})` (`intake.py:627–634`). Cards 1.1–1.4 should treat these 5 key names as fixed; Epic 2's functions all take them by these names.

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

**Rule, not a detail:** at most one `primary_api` (the first token-priced tool in the ranked list) and one `assistant` (the first seat-priced tool) — deliberately never a sum-per-tool across every recommended tool (`...:672–676`, and originally called out as a mistake to avoid in `07-Technical-Work-Breakdown-v2.md`). `total_monthly_eur` is a sum of just these two figures, not a change to that rule.

**Also new (Update D): seat counts are now capped by a `SEAT_CEILING` (currently 25) regardless of org-size band** — see `app/logic/cost.py` and Update D for why (a flat per-org-size seat assumption was costing a single-workflow query, e.g. "Customer Service," as if the whole company adopted the tool).

### C. Case references — `matched_cases`

`list[dict]`, each case shaped:

```
{ "case_id": str, "organization": str, "title": str, "industry": str,
  "source_url": str, "canonical_tools": list[str] }
```

(`13-Build-Guide-Epic2-Retrieval-v1.md:1077–1080`, confirmed again at `14-Build-Guide-Epic3-Blueprint-UI-v1.md:134`.)

**Correction to the task's draft template:** the field is `organization`, not `org`.

**On "up to 4":** the pipeline itself does not cap this list — it returns every case that survived de-dup (one entry per `case_id`) and the privacy filter, from an initial retrieval of 15 chunks (`...:1063`). The **4-case cap is UI-only**. **Update F correction:** this used to be a fixed slice in both places; as of Update F, the results page has a 4/8/All toggle (`app/dashboard.py`, `_render_case_references_block()`) while the export view (`app/export.py`) deliberately stays fixed at `matched_cases[:4]` regardless of what's toggled on-screen, so the exported blueprint text is always predictable. So: Cards 1.1–1.4/Epic 2 should pass through the *full* filtered list; Epic 3 does the slicing everywhere, not the pipeline.

### Also part of the output (not one of the 3 "blocks," but real)

- **`summary_text`** (`str`) — the LLM-generated plain-English paragraph from Card 2.6, rendered above Block A (`intake.py`-era pattern; `14-Build-Guide-Epic3-Blueprint-UI-v1.md:45`).
- **`llm_metrics`** (`dict`) — `{"duration_seconds": float, "prompt_tokens": int, "completion_tokens": int, "tokens_per_second": float|None}`, straight from `generate_summary()`'s return value, kept for Card 3.3's telemetry log (`13-Build-Guide-Epic2-Retrieval-v1.md:1110–1114`).
- **`tool_costs`** (`dict`, new in Update E) — `{canonical_tool_id: {"tool": str, "model": str, "monthly_eur": float|None, "assumption"|"note": str}}`, one entry per tool in `recommended_stack` (not just the two winning `cost_forecast` picks), from `estimate_all_tool_costs()` in `app/logic/cost.py`. Powers Block A's per-tool price display — see Update E in `18-Build-Guide-Updates-Epic1-2-v1.md` (or the Epic 3 updates doc, once created) for why this needed to exist separately from `cost_forecast`. Not sent to Card 2.6's LLM prompt — the model still only ever describes the single decided `primary_api`/`assistant` pair.
- **`query`** (`dict`, new in the Lovable-parity UI round) — `{"workflow": str, "industry": str, "org_size": str, "privacy": str}`, a plain echo of the validated intake inputs. Display-only: `app/dashboard.py` reads it for the status-chip row ("REGULATED POSTURE" chip), the "DIRECTIONAL ONLY" banner text, and Block C's per-case "why:" lines (same-industry check). Never re-enters any pipeline logic and is not sent to the LLM. Dashboard code reads it with `.get("query", {})` so results saved before this key existed still render.
- **`distance`** (`float`, inside each `matched_cases` entry — new in the Gabi
  relevance-threshold change, Ash4) — the raw Chroma distance for the chunk that
  surfaced this case, rounded to 3dp. **Scale is metric-dependent:** the
  collection is created without `hnsw:space`, so Chroma's default `l2` applies
  (`scripts/embed_cases.py`). If anyone rebuilds with cosine, or swaps the
  embedding model, these numbers — and `RELEVANCE_THRESHOLD` — change meaning
  entirely and must be re-derived with `tests/distancecheck.py`.
- **`no_match`** (`bool`, new in Ash4) — `True` when the relevance threshold (or
  the privacy filter) left no rankable tools. On that path the pipeline
  **short-circuits: no LLM call is made**, `recommended_stack` is `[]`,
  `tool_costs` is `{}`, and `summary_text` is a fixed factual sentence written by
  us, not by a model. Always present on both paths.
- **`no_match_reason`** (`str`, present only when `no_match` is `True`) — either
  `"no_relevant_cases"` (nothing cleared the relevance threshold) or
  `"privacy_filter"` (cases matched, but none of their tools are governable for a
  regulated posture). The UI uses this to explain the real cause instead of
  always blaming the privacy filter.
- **`domain`** (`str`, inside each `matched_cases` entry — new in Ash4) — the
  case's own workflow/domain, copied from chunk metadata. Added so the UI can
  tell a case that genuinely matches the requested workflow from a
  nearest-neighbour case retrieved from elsewhere. `""` if absent from metadata.
- **`exact_match_count`** (`int`, new in Ash4, present on both paths) — how many
  of `matched_cases` have **both** `industry` and `domain` equal to what the user
  asked for. Retrieval is semantic, so it always returns the nearest cases: a
  full 432-pair sweep found **185 combinations (43%) have zero real cases**
  (2026-07-27 sweep said 205/47%; recounted 2026-07-30 after the store rebuild), and
  for those the banner previously claimed "N real X Y deployments matched" — a
  false statement. The banner now branches on this count (all / some / none
  genuine). `"Any workflow"`/`"Any industry"` impose no constraint, so they can't
  make a case a mismatch and the count equals `len(matched_cases)`. Blueprints
  saved before Ash4 lack this key; the UI treats absent as "make no claim".
- **`project_name`** (`str`, new in Icebox B.5 / Build Guide 24) — optional, cosmetic; empty string when the user leaves the field blank. Echoed in the dashboard heading, the plain-text export header, the board one-pager title (guide 26), and B.6's default save-name. Kept top-level, deliberately NOT inside `query` (that key is strictly the 5 validated pipeline inputs).

**Inputs (B.5 additions):** `run_pipeline`'s `inputs` dict also accepts two optional keys — `project_name` (str, cosmetic, above) and `exclude_tools` (list of canonical tool ids). Exclusions are applied by `apply_vendor_exclusions()` in `app/logic/filter.py` **after** the privacy filter and before ranking: privacy is a hard compliance rule that always sees the full case list; exclusions are a user preference layered on top. Neither field is validated by `validate_intake` — empty values are a no-op by design.

Full return shape:

```python
{
    "recommended_stack": [...],   # Block A
    "cost_forecast": {...},       # Block B
    "tool_costs": {...},          # Block A per-tool prices (Update E)
    "matched_cases": [...],       # Block C (unsliced)
    "summary_text": "...",
    "query": {...},               # intake echo, display-only (UI-parity round)
    "project_name": "...",        # optional cosmetic name (B.5), "" if unset
    "no_match": False,            # Ash4 — True only on the short-circuit path
    "exact_match_count": 0,       # Ash4 — true industry+workflow matches
    # llm_metrics gained "summary_fallback_used" (bool) on 2026-07-28 — True when
    # the model returned empty content and the deterministic summary was used
    # instead. It flows into telemetry via log_event("llm_summary_generated", ...).
    "llm_metrics": {...},
}
```

**Note on the retrieval query string (Ash4).** `query_text` is built from the two
dropdowns only — the project name never reaches retrieval. `"Any workflow"` /
`"Any industry"` are UI conveniences, not corpus values, so the unspecified half
is dropped rather than interpolated (which previously produced the literal query
`"Any workflow in the Any industry industry"` from the default form state):

| Workflow | Industry | Query sent |
|---|---|---|
| specified | specified | `{workflow} in the {industry} industry` |
| Any | specified | `AI adoption in the {industry} industry` |
| specified | Any | `{workflow}` |
| Any | Any | `enterprise AI adoption` |

---

## Implementation status (check before trusting the live code)

Epics 1–3 are all wired in and merged into `Ash2` — this doc now matches the live `app/pipeline.py`/`app/logic/cost.py`/`app/logic/prompt.py`, not Epic 1's original placeholder. (This section previously described the placeholder pipeline from before Epic 2 was wired in; corrected here as a housekeeping fix while this file was open for Update D, since it had gone stale without anyone noticing.)

Known, disclosed limitations of the current implementation, as of Update D:
- `total_monthly_eur`/`within_budget`/`budget_delta_eur` compare the forecast against budget but never alter tool selection to force a fit — an over-budget result is a legitimate, honestly-flagged outcome, not a bug to hide.
- `SEAT_CEILING` (25, in `app/logic/cost.py`) is a flat, hand-picked stopgap applied uniformly regardless of workflow — not a real per-workflow headcount estimate. See Update D in `18-Build-Guide-Updates-Epic1-2-v1.md` for the fuller "workflow-fraction table" alternative (Option A) that was considered and deliberately deferred.
