# 35 — Build Guide: Ash4 — relevance threshold, merged and made safe

**Branch:** `Ash4` (merge of `Gabi` into `Ash3-update`) · **Date:** 2026-07-27
**Owner:** Ash, on Gabi's change · **Status:** merged + fixed here; **two live
checks below are still outstanding and are the gate on shipping this.**

## What Gabi's change does

`app/pipeline.py` gained `RELEVANCE_THRESHOLD = 0.52`. Retrieved chunks whose
Chroma distance exceeds it are dropped **before** de-duplication, ranking, costing
and the LLM summary. Each surviving case also carries its raw `distance`.

Before this, every query returned the 15 nearest chunks no matter how far away
they were — so a nonsense query still produced a confident "15 real deployments
matched". That directly undercut the product's core claim (*grounded in real
deployments, every recommendation traceable*), so the change is the right call.

`tests/distancecheck.py` is the calibration: plausible queries vs deliberately
absurd controls. The absurd controls are the good part — they test the failure
mode nobody thinks to test.

## Why it wasn't safe to ship as-is (and what was fixed)

### Fix 1 — the empty path called the LLM with no evidence

`RELEVANCE_THRESHOLD` can legitimately reject **everything** — that's the point
for a nonsense query. Traced downstream, that produced:

- `rank_tools_by_frequency([])` → `[]`
- `estimate_cost([])` → primary/assistant/total all `None`
- **`generate_summary()` had no empty-input guard** — the model was handed
  "Ranked tools: []" and "Matched cases: 0 comparable deployments" and still asked
  to write a recommendation.

An LLM asked to summarise nothing will write *something* — the exact failure this
architecture exists to prevent. `run_pipeline()` now **short-circuits** when no
tools survive: no LLM call, `no_match=True`, `no_match_reason` set, and a fixed
factual sentence written by us. `llm_metrics` is zeroed rather than fabricated, so
Card 3.3's telemetry schema stays intact.

### Fix 2 — the empty state blamed the wrong thing

Block A's message read *"No tools cleared the privacy filter for this combination
of inputs"* — which became actively misleading once relevance could empty the list
for a different reason. It now branches on `no_match_reason`:

| Reason | Message |
|---|---|
| `no_relevant_cases` | nothing in the library was close enough — try a broader workflow/related industry, and it says this limit is deliberate |
| `privacy_filter` | cases matched but their tools aren't governable for a regulated posture — try the standard posture |
| fallback | generic (covers vendor exclusions emptying the list) |

The DIRECTIONAL-ONLY banner also no longer announces "**0** real X Y deployments
matched" as if it were a finding; on the no-match path it renders a
**NO EVIDENCE MATCH** banner explaining the limit.

### Fix 3 — the threshold was calibrated on 8 data points

The original script tested 4 plausible + 4 nonsense queries. The problem:

```
plausible max observed = 0.504      threshold = 0.52      margin = 0.016
```

A 0.016 margin, from 4 of **several hundred** possible workflow × industry
combinations — and the tightest observed case ("Facilities & EHS in Agriculture")
is exactly the kind of thin combination the model card says has least evidence. If
a real user's combination lands above 0.52 they get **zero results**.

`tests/distancecheck.py` was rewritten to measure the number that matters — how
close the **worst genuine** query gets to the cutoff:

```bash
python tests/distancecheck.py              # ~40 sampled real pairs
python tests/distancecheck.py --full       # every workflow x industry pair
python tests/distancecheck.py --threshold 0.55
```

It reports the worst genuine distance, the signed margin, chunks-kept
min/median/max, **every real combination that would return nothing**, and which
nonsense controls leaked. Exit code 1 if any genuine combination is rejected, and
it warns at MARGINAL if the margin is under 0.02. Nonsense controls extended from
4 to 8.

## ⚠️ Still outstanding — the gate on shipping this

Neither can be done from this environment (no `chroma_store`, no embedding model,
no `GROQ_API_KEY`). **Both must pass before `Ash4` merges to main.**

- [ ] **`python tests/distancecheck.py --full`** — must not print FAIL. If it
      does, raise the threshold above the reported worst value, or add a floor
      (always keep the top-k nearest chunks) rather than shipping a cutoff that
      silently returns nothing for real inputs.
- [ ] **`python scripts/backend_dry_run.py`** — re-run the three P.9 profiles.
      Profile 3 ("Facilities & EHS / Agriculture / solo / regulated") is
      deliberately the sparse case and is the most likely to now come back empty.
      If matched-case counts changed, `P9-Backend-Dry-Run-Results-v1.md` and
      `P14-Validation-Metrics-Final-v1.md` quote the old numbers.
- [ ] **Try one nonsense query in the live app** and confirm you get the
      NO EVIDENCE MATCH banner and the honest Block A message — no invented
      summary, no crash.

## Knock-on effects to watch

- **Matched-case counts can change**, which moves the "N MATCHED CASES" chip, the
  banner text, the summary's "Based on N comparable deployments", and the numbers
  quoted on deck slides 6/7 plus any screenshots.
- **The threshold is coupled to the distance metric.** The collection is created
  with no `hnsw:space`, so Chroma's default `l2` applies — a note is now in
  `scripts/embed_cases.py`. Rebuild with cosine, or change the embedding model,
  and 0.52 silently means something else.
- **Schema changed**: `matched_cases[i].distance`, plus `no_match` /
  `no_match_reason` — recorded in `Intake-Output-Schema-v1.md`.
- Saved-blueprint JSON now includes `distance` (harmless; older saved files
  simply lack it).

## The merge

`Ash4 = Ash3-update + Gabi`, in that direction **on purpose**: Gabi's branch was
behind on the UI/export work, so merging the other way would have dropped the B.8
PDF export and reinstated the `~2 min` hero over-claim. Verified present in the
merged tree: `blueprint_to_pdf`, the Download popover, `fpdf2`, `~5 min`,
`RELEVANCE_THRESHOLD`, `distancecheck.py`, `validation_metrics_table.py`.

Two conflicts resolved by hand rather than by picking a side:

- **Build Guide 17** — 3-way text merge, keeping both the "24 → 41 tools"
  correction and Gabi's P.14 table-view notes.
- **`data/telemetry.log`** — union of both sides, de-duplicated, re-sorted by
  timestamp (265 + 259 → 280 unique lines). Append-only log, so no real events
  are lost from either machine.

## Verification done here

`py_compile` clean on `pipeline.py`, `dashboard.py`, `distancecheck.py`,
`embed_cases.py`. Both pipeline paths exercised with a stubbed collection:

- all chunks beyond threshold → `no_match=True`, `no_match_reason="no_relevant_cases"`,
  empty stack, **0 LLM calls**, all required result keys present;
- chunks within threshold → `no_match=False`, stack populated, **exactly 1** LLM
  call, `distance` carried on each case.

## Rollback

The threshold is one constant. Setting `RELEVANCE_THRESHOLD` to a large number
(e.g. `99`) disables the filter without touching anything else — the no-match
guard and messages simply never trigger. Reverting the merge drops Gabi's work
wholesale, which is the heavier option.
