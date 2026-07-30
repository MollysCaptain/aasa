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

- [x] **`python tests/distancecheck.py --full` — RUN AND PASSED 2026-07-27.**
      First run printed `FAIL — 5 genuine combination(s) return NOTHING at 0.52`
      (worst genuine 0.568, margin −0.048, 7/8 nonsense rejected). **The FAIL was
      the script's fault, not the threshold's** — all 5 pairs have zero cases in
      the corpus, so returning nothing is correct. Verdict logic rewritten to be
      corpus-aware; re-run confirms **PASS, 0 pairs with evidence returning
      nothing**. Threshold unchanged at 0.52. See correction 2 below.
- [x] **P.9 Profile 3 tested live (2026-07-27)** — "Facilities & EHS / Agriculture
      / solo / regulated" returned **15 matched cases, threshold filtered nothing**
      (Azure, AWS, Azure OpenAI, Bedrock, Google Cloud; €8.75/mo; WITHIN BUDGET;
      regulated chip correct). **My prediction that this would return empty was
      wrong — see the correction below.**
- [ ] **`python scripts/backend_dry_run.py`** — still worth re-running all three
      P.9 profiles to confirm matched-case counts, since
      `P9-Backend-Dry-Run-Results-v1.md` and `P14-Validation-Metrics-Final-v1.md`
      quote the pre-threshold numbers.
- [ ] **Exercise the no-match UI.** A nonsense query **cannot be entered through
      the app** (see correction below — both retrieval inputs are fixed dropdowns),
      so to see this path temporarily set `RELEVANCE_THRESHOLD = 0.3`, run any
      query, confirm the NO EVIDENCE MATCH banner and the honest Block A message
      appear with no invented summary, then set it back to `0.52`.

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
merged tree: `blueprint_to_pdf`, the Download popover, `fpdf2`, `~5 min` (the
hero stat at the time — reverted to `~2 min` on 2026-07-28 once the median was
checked rather than the mean; see P.21 finding 2),
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


---

## Correction (2026-07-27) — I misread the calibration numbers

**What I claimed:** P.9 Profile 3's best distance was 0.504 against a 0.52 cutoff,
leaving "a 0.016 margin", making it the query most likely to return nothing.

**What is actually true:** Gabi's note says plausible queries "topped **out** at
0.384–0.504" — that is the **maximum** distance among the 15 chunks, not the
minimum. So for these queries *every* chunk is at or below 0.504, i.e. inside the
cutoff. Tested live: Profile 3 kept **15 of 15** cases. Nothing was ever going to
be rejected.

**Consequences — both directions:**

- **Lower risk than I said.** For a real query to return nothing, its *nearest*
  case must exceed 0.52. Observed plausible minima sit far below that. Demo-day
  risk from an unexpected empty result is small. The no-match guard is still worth
  having (it's cheap, and it protects the script/API path), but it is unlikely to
  fire in normal use.
- **Narrower benefit than it appears.** The threshold trims far-off tail chunks
  and would reject a genuinely unrelated query; it does not change
  well-populated queries at all.
- **The structural point neither of us spotted:** the retrieval query is built
  only from the two dropdowns —
  `query_text = f"{workflow} in the {industry} industry"` — and both lists come
  from the corpus. **A user cannot submit free text into retrieval at all** (the
  project-name field never reaches it). So the "quantum toaster" class of query
  that motivated the threshold is unreachable through the UI; it only arrives via
  the test script.

**How to describe this honestly in the submission:** the threshold is correct
defence-in-depth and it stops "15 matched cases" being a fixed number regardless
of fit — but do **not** claim it prevents users from receiving irrelevant results,
because users cannot ask an irrelevant question through the dropdowns. The
`distancecheck.py --full` sweep is still worth running: it tells you whether any
real combination's *nearest* case exceeds 0.52, which is the only way a real user
sees the empty state.

---

## Correction 2 (2026-07-27) — the sweep ran, and it found something bigger

Ash ran `python tests/distancecheck.py --full`. Output:

```
Threshold under test : 0.52
Real pairs           : 432 of 432 possible (FULL sweep)
worst genuine best-distance : 0.568      MARGIN : -0.048
real queries with 0 results : 5/432
    0.555  Finance in the Education industry
    0.568  Procurement in the Education industry
    0.533  Procurement in the Government & Public Sector industry
    0.529  Procurement in the Real Estate & Construction industry
    0.558  Sales in the Education industry
NONSENSE CONTROLS: fully rejected 7/8   (leak: "competitive yodeling", best 0.476)
FAIL — 5 genuine combination(s) return NOTHING at 0.52.
```

### The FAIL was wrong, and it was my bug

I cross-checked those 5 pairs against the corpus. **All five contain zero
cases.** Education has 177 cases and Procurement has 8, but no case is both.
So returning "no comparable deployments" is the *truthful* answer, and the
threshold was behaving exactly as designed.

The `FAIL` came from an assumption I built into the script: that anything
selectable in the dropdowns must have evidence behind it. That is false. **The
threshold was not raised** — raising it to 0.58 would have cleared all 432 pairs
but made the app present 15 unrelated cases as evidence for five combinations
that have none. `RELEVANCE_THRESHOLD` stays at **0.52**.

`tests/distancecheck.py` now reads case population straight from the collection
and splits empty results in two:

| Outcome | Meaning | Verdict |
|---|---|---|
| **wrongly empty** | corpus HAS cases, threshold rejected them all | **FAIL** — evidence thrown away |
| **correctly empty** | corpus has no cases for this pair | NOTE — guard working |

Re-verified against the real corpus: 0 wrongly empty, 5 correctly empty → **PASS**.

### The bigger finding: 205 of 432 combinations have no evidence (now 185 — see the note below)

The threshold only catches 5 of them. The other **200** (180 now) return 15
nearest-neighbour cases from other industries — and the banner announced:

```python
context = f"{n} real {query['industry']} {query['workflow']} deployments matched. "
```

For 47% of possible queries that sentence was **false** (43% against the current
store). It named an
industry/workflow pair with zero deployments and called the results "real …
deployments". Block C was already honest (each case shows its own industry, and
"same industry as yours" only appears on a true match) — the banner was not.

**Fixed** by counting true matches deterministically. `pipeline.py` now carries
`domain` on each matched case and returns `exact_match_count`; the banner says:

| Situation | Banner text |
|---|---|
| all matches genuine | "15 real Healthcare Data & Analytics deployments matched." |
| none genuine | "No direct Education Procurement deployments in the library — showing the 15 closest comparable deployments from adjacent industries." |
| some genuine | "4 real Healthcare Data & Analytics deployments matched, plus 11 closest comparable from adjacent industries." |
| "Any" selected | "15 deployments matched from across the whole case library." |
| pre-fix saved blueprint | "15 comparable deployments matched." (no claim, since the old one may be wrong) |

This turns a hidden over-claim into a visible, accurate statement about evidence
depth — and it costs nothing, because the data was already in the metadata.

### Third issue found while checking: the "Any" defaults reached retrieval raw

`WORKFLOWS` and `INDUSTRIES` both start with `"Any workflow"` / `"Any industry"`,
neither `st.selectbox` passes `index=`, and `validate_intake` accepts them
(they're non-empty strings). So the **default form state** built the query
literally:

```
"Any workflow in the Any industry industry"
```

That is the query anyone gets by pressing *Generate my blueprint* without
touching the dropdowns — the most likely first action at a demo. `pipeline.py`
now drops the unspecified half instead:

| Workflow | Industry | Query sent |
|---|---|---|
| Data & Analytics | Healthcare | `Data & Analytics in the Healthcare industry` |
| Any workflow | Healthcare | `AI adoption in the Healthcare industry` |
| Marketing | Any industry | `Marketing` |
| Any workflow | Any industry | `enterprise AI adoption` |

### Verification

`py_compile` clean on `pipeline.py`, `dashboard.py`, `distancecheck.py`. With a
stubbed collection: all five banner branches produce the expected sentence,
`count_exact_matches` correct on 7 cases including the "Any" variants, query
construction correct on all four combinations, **0 LLM calls** on the
empty-retrieval path, and `exact_match_count` present on both return paths.

### Confirmed live — `distancecheck.py --full`, re-run 2026-07-27

```
Pairs WITH real cases: 227 of 432 tested (205 have no cases at all)
worst genuine best-distance : 0.568     MARGIN : -0.048 (informational)
chunks kept per real query  : min=0 median=15 max=15
EMPTY + evidence exists (BUG) : 0
EMPTY + no evidence (correct)  : 5
NONSENSE CONTROLS: fully rejected 7/8   (leak: "competitive yodeling", 0.476)
PASS — every combination that has evidence returns it (threshold 0.52).
```

**Note added 2026-07-30 — the first line of that output no longer reproduces.**
The output above is kept as the record of the real 2026-07-27 run, but Gabi
rebuilt and committed `chroma_store` on the 28th for the Cloud deploy, and the
rebuild populated 20 more pairs. Recounted against the committed store it is now
**247 populated / 185 empty**, not 227/205. The threshold findings on the other
lines (0 wrongly empty, 5 correctly empty, worst genuine 0.568, nonsense leak
0.476) have **not** been re-confirmed against the rebuilt store — they need a
live `--full` re-run before anyone quotes them as current. See
`Capstone Plan/PM Work/16-P22-Final-Consistency-Pass-v1.md`.

Matches the offline corpus check exactly. **The threshold discards no real
evidence anywhere in the 432-pair space.** `RELEVANCE_THRESHOLD = 0.52` is now
verified rather than assumed, and this is a repeatable regression test: if anyone
rebuilds the store, changes the embedding model, or edits the dropdown lists,
re-running this will catch evidence being thrown away.

### Thin-evidence pairs — the weakest output the app can produce

The run exposed a third category, visible in the "risky end" table: pairs with
**zero real cases that still keep only 1–2 chunks**.

| Pair | kept | real cases |
|---|---|---|
| Legal & Compliance × Hospitality & Travel | 1/15 | 0 |
| Finance × Real Estate & Construction | 2/15 | 0 |
| Procurement × Automotive | 2/15 | 0 |

These produce a full ranked stack, cost forecast and summary from **one or two
cases belonging to a different industry**. Not a bug — it's the honest edge of an
evidence-based approach — but it is the thinnest the product ever gets, and the
new banner is what keeps it truthful ("No direct … showing the N closest
comparable deployments from adjacent industries"). Block A's "Seen in N/M cases"
bars will read 1/1 or 2/2, which is accurate but looks stronger than it is;
worth a glance before the freeze.

### Still outstanding

- [ ] **Live-check `Procurement × Automotive`** (solo / standard / any budget).
      Best single test of the banner fix: zero real cases *and* only 2 chunks, so
      it exercises the "no direct deployments" wording and the thin-stack case at
      once. Expect the DIRECTIONAL ONLY banner to name no false pairing.
- [ ] Live-check the default `Any workflow / Any industry` submit returns a
      sensible blueprint (it now queries `enterprise AI adoption`).
- [ ] Consider flagging unpopulated pairs in the dropdowns — the real fix, but a
      bigger change than the freeze allows. Recorded in Known-Limitations.