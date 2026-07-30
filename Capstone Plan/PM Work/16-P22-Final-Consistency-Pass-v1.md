# P.22 — Final Consistency Pass & Submit

**Run:** 2026-07-30, against `Ash6` after the Ash6 → `main` merge and the removal
of the pitch decks from the branch · **Card:** P.22

This is the second consistency pass. The first (`14-P21`) checked documents
against each other. This one checked **every stated figure against the code and
data that produce it**, which is a different and harder question — and it found
nine things the first pass didn't, one of them in shipped app text.

---

## The headline finding

**"205 of 432 workflow × industry combinations (47%) have zero cases" is no
longer true. It is 185 of 432 (43%).**

The figure was correct when it was measured. `tests/distancecheck.py --full` was
run on **2026-07-27** and reported 227 populated / 205 empty. Gabi then rebuilt
and committed `chroma_store/` on **2026-07-28** so the Streamlit Cloud deploy
would have a vector store (commit `6f6f025`, Build Guide 36). The rebuild
re-derived the canonical domain column, which moved 20 pairs from empty to
populated. Nobody re-ran the sweep, so a number measured against one store stayed
in the documents — and in the app — describing a different one.

Recounted 2026-07-30 directly from the committed store's chunk metadata, using
the same logic as `distancecheck.py`'s `case_population()` (de-duplicate by
`case_id`, count by `(domain, industry)`):

```
distinct cases                      3023
industries × workflows               24 × 18 = 432
pairs WITH real cases                247
pairs with ZERO real cases           185   (42.8%)
```

Corrected in nine places, of which **three are shipped code**:
`app/dashboard.py` (the banner's own explanatory comment), `app/pipeline.py`
(twice), `tests/distancecheck.py`, `Known-Limitations-v1.md`,
`Intake-Output-Schema-v1.md`, Build Guide 17 (twice — the pitch-day script) and
Build Guide 35 (annotated rather than rewritten, since it records the original
run).

### Two things this changed about how we write the number down

**The pasted terminal output in Build Guide 35 was left exactly as it was.** It
is a record of a run that really happened. Rewriting it would turn evidence into
decoration. A dated note underneath says it no longer reproduces and why.

**`distancecheck.py`'s docstring no longer states the count at all.** It now says
the count is a property of the corpus, moves whenever the store is rebuilt, and
that the run's own "Pairs WITH real cases" line is the only authority. A hardcoded
number in a docstring is how this drifted in the first place; the fix is to stop
hardcoding it, not to hardcode a fresher one.

### Confirmed by a live full sweep — 2026-07-30

The coverage count needed no embeddings, so it was verifiable statically. The rest
of the sweep was not, so Ash ran `python tests/distancecheck.py --full` against
the submitted store. **185 confirmed, and nothing else moved:**

| | 2026-07-27 (pre-rebuild) | 2026-07-30 (submitted store) |
|---|---|---|
| Pairs with real cases | 227 / 432 | **247 / 432** |
| Pairs with zero cases | 205 (47%) | **185 (43%)** |
| Empty **with** evidence — the only failure condition | 0 | 0 |
| Empty with no evidence | 5 | 5 — *the same five pairs, same distances* |
| Worst genuine best-distance | 0.568 | 0.568 |
| Margin | −0.048 | −0.048 |
| Nonsense controls rejected | 7 / 8 | 7 / 8 — same leak, 0.476 |
| Verdict | PASS | **PASS** |

**The fact that only one line moved is itself the answer to "what did the rebuild
change?"** Had it altered the embedded text, the distances would have shifted.
They are identical to three decimals. So the rebuild changed **chunk metadata
only** — the canonical domain column re-derived by `normalize_domains.py`, which
is precisely the field pairs are counted by. Twenty pairs gained a domain label;
no vector moved, no case was added or removed, and the retrieval behaviour of the
shipped product is unchanged.

That upgrades the correction from "a number we had to fix" to something worth
carrying: **a store rebuild can invalidate corpus-coverage facts while leaving
retrieval entirely intact.** The two look like one concern and are not. Coverage
went stale for two days without a single retrieval symptom to notice it by — which
is exactly why it survived a consistency pass that compared documents to each
other.

---

## Second finding: the same bug Gabi caught, in a third script

`scripts/validation_metrics_table.py` called `load_events()` with **no window**,
accepted no `--since` / `--until` / `--p14`, and printed **no warning**.

This is exactly the defect Gabi found on 2026-07-28 in `telemetry_funnel.py` —
`data/telemetry.log` is append-only, so development runs after the user-test round
closed keep inflating the denominators. Both other scripts were hardened that day.
This one was missed, and it is the one the README advertises as regenerating "the
whole P.14 results table". Running the documented command produced:

| Metric | Published (`--p14`) | What the bare script printed |
|---|---|---|
| Blueprint export rate | 83% (10/12) | 23% (24/106) |
| Net value | 100% (8/8) | 94% (17/18) |
| Trust score (median) | 5/5 | 4/5 |
| Avg. LLM latency | 1.34s (12 calls) | 1.49s (106 calls) |
| Sample size | 12 sessions / 8 responses | 106 sessions / 18 responses |

Every published figure in the submission disagreed with the script the submission
tells a marker to run. Fixed: the script now takes `--since/--until/--p14`,
imports the window constants and the warning helper from `telemetry_funnel.py` so
the three can never disagree, and `--p14` reproduces the published table exactly
(verified).

**The pattern, third time now.** Twice before on this project the measurement was
sound and the *check around it* was broken — `distancecheck.py`'s FAIL verdict
assumed every selectable pair must have evidence; the documented P.14 command was
missing its end bound. This is the same shape: three scripts read one log, two
were fixed, and "we fixed it" was recorded without anyone asking *how many places
have this*. The generalisable lesson is to fix the class, not the instance, and to
count the instances before claiming the class is closed.

---

## Everything else the pass found

Grouped by whether it would mislead a reader or merely annoy one. All fixed
except where noted.

### Factually wrong

| # | Finding | Where | Fix |
|---|---|---|---|
| 1 | **"24 tools" survived in 10 more places** after `14-P21` fixed four. Includes the pitch-day spoken script (BG17:253), which contradicted BG17:227 in the same file saying 41 | Handbook, PM Work 02/05/07, BG 11/13(×2)/17, `normalise_cases.py`, Kanban HTML | → 41 |
| 2 | **Effort total contradicted itself.** Handbook §6 said "≈ 9.5 days"; PM Work 07 and 08 both say 15; Handbook §11 asserts those two "both now sum to the same 15 days" | Handbook:95 | → 15 days task effort ≈ 7.5 each, with a note |
| 3 | **A success target no document reported a result against.** Outcome Goals asks for ">75% rating recommendations more trustworthy"; the shipped survey measures a 1–5 median, so the operational target became ≥4/5 and 75% is never mentioned again | PM Work 05, 03b, 08 | Note recording what was actually measured (median 5/5; equivalently 7/8 = 88% rated ≥4/5) rather than rewriting the goal |
| 4 | **The prototype mockup claimed the product's dataset.** `aasa-prototype.html` eyebrow read "grounded in 3,023 real AI deployments"; its embedded data holds 197 cases. Overstated by ~15× | `aasa-prototype.html`:183 | → "Static mockup · 197 curated cases (the shipped product uses 3,023)" |
| 5 | **Prototype called the dataset CC-BY**; everything else says MIT, and MIT is the basis of the whole redistribution argument in `docs/data-attribution.md` | `aasa-prototype.html` ×3 | → MIT. *Open:* `data/AICaseStudy/schema.md`:60 says "MIT and CC-BY-4.0" — upstream's own wording, left alone, flagged below |
| 6 | **Outlier values off by one, and one outlier unnamed.** True values 1,286.6s and 1,616.8s → 1,287 and **1,617**, not 1,618. And there is a **third** session over 500s (576.7s) that "inflated by two long sessions" didn't account for | `P14-Validation-Metrics-Final-v1.md`:97–98 | Corrected with a note |
| 7 | **"18 responses over 100 sessions"** — the bare log has **106** `results_shown` | P14 doc, PM Work 11 | → 106 |
| 8 | **"31 `blueprint_saved` events"** matched neither count: the window has 10, the full log 32 | BG17:178 | → 10 (32 across the log) |
| 9 | **Handbook said the prototype had 15 industries**; it has 21, and `app/intake.py` already said 21 | Handbook:132, BG20:9 | → 21 |
| 10 | **Model card said the dataset has 13 columns.** The schema documents 12; our scripts derive 2 more | `docs/model-card.md`:11 | → 12 source + 2 derived |

### Breaks a link or a table

| # | Finding | Where | Fix |
|---|---|---|---|
| 11 | **A stray blank line split the limitations table**, orphaning its two most important rows — the relevance cutoff and the empty-pairs disclosure — out of the table they belong to | `Known-Limitations-v1.md`:35 | Removed |
| 12 | **Kanban footer cited the pre-renumbering PM Work names.** After the 06–15 → 05–14 shift, `10-` and `11-` now resolve to *different documents*, so the reference silently pointed at the wrong files rather than at nothing | `AASA-Kanban-Board.html`:127 | → 06/07/08/09 |
| 13 | **`P9-Backend-Dry-Run-Results-v1.md` cited under `Capstone Plan/Build Guide/`** in two scripts. It lives in `PM & Ethics/` and never lived there | `compliance_check.py`, `validation_metrics_table.py` | Path corrected |
| 14 | **Cited the unredacted testing spreadsheet** by its original filename. Only the pseudonymised copy is committed — the original is gitignored precisely because it holds participants' names and employers | `Known-Limitations-v1.md`:45 | → `(pseudonymised).xlsx` |
| 15 | **Nine stale code line-references** in the schema doc, off by hundreds of lines, plus four build-guide anchors pointing at unrelated content | `Intake-Output-Schema-v1.md` | All nine corrected |
| 16 | **`.gitignore` listed `.python-version`, which is tracked** — the same ignored-yet-tracked contradiction we fixed for `telemetry.log`. Plus two rules for files gone for weeks (`PM_slides/`, `AASA_Week2_Stakeholder_Checkin.pptx`) | `.gitignore` | Removed, with a note **not** to add a `*.pptx` rule since the decks are coming back by hand |
| 17 | **README said "the two metrics scripts"**; there are three, and the third was the broken one | `README.md`:219 | → three, and `--p14` added to its example |
| 18 | **The upper-of-two-middles median bug had a surviving copy** in `distancecheck.py`, in a project that documents having fixed exactly that bug elsewhere | `distancecheck.py`:155 | → `statistics.median` |
| 19 | **Handbook §11 claimed to be the index and to be complete**, then listed only 01–09 — omitting 10–14, the Kanban board, and now 15–16 | Handbook §11 | Table completed; the consistency claim kept and annotated rather than deleted |
| 20 | **Size of `chroma.sqlite3` given as ~54 MB in one place, ~52 MB in two others** | `docs/data-attribution.md`:49 | → ~52 MB throughout |

### Left open on purpose

- **`data/AICaseStudy/schema.md`:60 says the upstream dataset is "MIT and
  CC-BY-4.0".** That file documents *their* schema in *their* words. Our
  attribution rests on MIT, which is the licence in the upstream repository, and
  MIT is the more permissive of the two so the argument holds either way. Changing
  someone else's licence statement to tidy ours would be the wrong instinct.
  Recorded rather than resolved.
- **Only 37 of the 41 priced tools appear anywhere in the corpus.** Four priced
  ids can never be recommended. No document claims otherwise, but "41 tools
  priced" reads as coverage when it is catalogue size. Not corrected — it is
  literally true — but worth not over-selling on stage.
- **`INDUSTRIES` contains both "Robotics" (1 case) and "Robotics & Automation"
  (7).** A near-duplicate dropdown option, and "Retail & E-commerce" is appended
  out of alphabetical order. Both are frozen (P.15) and neither is a false claim.

---

## Checks that came back clean

Verified against source, not against another document:

- **3,023 cases and 9,069 chunks** — counted in `chroma.sqlite3`. Exactly 3 chunks
  per case (domain / implementation / outcome).
- **41 priced tools** — counted in `PRICING`; all 41 carry both a `label` and a
  `url`. **41 canonical ids** in `ALIAS_MAP` across 136 raw variants, 1:1 with
  `PRICING`.
- **24 industries and 18 workflows** — the dropdown lists and the corpus's
  distinct values match *exactly* in both directions. No dead option, no orphan
  corpus value.
- **`RELEVANCE_THRESHOLD = 0.52`** in `app/pipeline.py`.
- **The P.14 window is byte-identical in all six places that quote it**, because
  they all import it from one constant.
- **P.14 headline figures reproduce**: 12 shown / 10 exported / 83% / trust median
  5 / net value 8/8 / avg LLM 1.34s, and median 114.4s vs mean 372.3s.
- **Model-card bias figures reproduce** from store metadata: 44.6% top industry,
  40.0% top-3 concentration, 88.7% alias coverage (2,682 / 3,023).
- **Hero reads `~2 min`**, matching the median. No stray `~5 min` anywhere.
- **No file carries a date later than 2026-07-28**, consistent with the P.15 freeze.
- **No pitch deck is tracked**, and no document references a deck filename — so
  removing them from the branch left nothing dangling.
- **No orphan files.** Every tracked file outside `chroma_store/` and
  `static/fonts/` is referenced by name from at least one other file.
- **The duplicated Ethical Action Plan is still byte-identical** (the accepted
  cost of the `14-P21` decision to keep both):
  ```bash
  diff "PM & Ethics/Ethical-Action-Plan-v2.md" \
       "Capstone Plan/PM Work/03-Ethical-Action-Plan-v2.md" && echo "in sync"
  ```

---

## Cannot be done from here — Ash and Gabi

| # | Action | Owner | Why |
|---|---|---|---|
| 1 | **Push `Ash6`, and confirm the merge to `main` actually landed.** In the local clone `main` and `origin/main` are both still at `a62d0a9`, five commits behind `Ash6`; `origin/Ash6` is one commit behind local. If the merge was done on GitHub, `git fetch` will show it | Joint | No network access to the remote from here |
| 2 | ~~Re-run `distancecheck.py --full`~~ **Done 2026-07-30 — PASS, 247/185, all threshold figures unchanged.** See the table above | — | Closed |
| 3 | ~~Run `backend_dry_run.py` and `compliance_check.py`~~ **Done 2026-07-30 — all 3 profiles PASS, compliance 2/2 (100%).** Both surfaced real defects in the scripts themselves, fixed: `backend_dry_run.py` couldn't import `app` at all, and wrote its results to a folder the file left weeks ago | — | Closed |
| 3b | **Re-run all three on the merged `main`** once the merge is confirmed | Either | They passed on `Ash6`; `main` is what deploys |
| 4 | **Load the deployed app and confirm the hero reads 3,023 / 41 / 24 and `~2 min`** | Either | The deploy tracks `main`, so this only becomes true once the merge is pushed |
| 5 | **Click every source link** in the demo path and in the deck | Human | P.19 has required this since it was written and it is still open |
| 6 | **Colour-contrast and mobile checks** | Human | Needs eyes on a real screen and a real phone |
| 7 | **Two timed rehearsals** (P.20, SP.5) — the test run came in at 14:19 against a 12:00 limit | Joint | Performance, not a document |
| 8 | **Back the project up off-machine** | Joint | Cannot write outside the repo |
| 9 | **Add the Week 4 ethics checkpoint** to both copies of the Ethical Action Plan, dated at submission, and re-run the `diff` above | Ash | Should record the final state, so it is written last |
| 10 | **Sign P.15 and P.19** — both need two names | Joint | A decision, not a fact |
| 11 | **Submit via the bootcamp channel and confirm receipt** | Joint | No access |

## Order for the remaining time

1. Push, verify the merge, then items 2–4 — those confirm the submitted build
   actually works, and everything else is cosmetic if they fail.
2. Re-add the decks, then re-run the fabrication check on them (P.19: no borrowed
   logos, no implied partnerships, no invented metrics) and confirm every deck
   figure matches this document.
3. Links, contrast, mobile.
4. Cut the rehearsal to under 12:00.
5. Sign P.15 and P.19, Week 4 ethics checkpoint, backup, submit.
