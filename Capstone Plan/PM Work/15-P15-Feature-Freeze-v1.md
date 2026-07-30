# P.15 — Feature Freeze

**Freeze date: 2026-07-28.** The last change to product behaviour was made that
day. Everything committed since has been documentation, verification tooling, or
correction of statements that were factually wrong — see the change-control rule
below for why those are permitted and how each one is logged.

**Declared by:** Ash + Gabi · **Recorded:** 2026-07-30 · **Card:** P.15

---

## What "frozen" means here

The product is `app/` plus the committed `chroma_store/`. From 2026-07-28:

- **No new features.** Nothing new in the intake form, the blueprint, the cost
  engine, the export, or the retrieval path.
- **No new dropdown values, no new priced tools, no re-embedding.** The corpus
  and the pricing table are fixed as committed.
- **No new dependencies.** `requirements.txt` is closed.

What is *not* frozen: the pitch deck, the speaker notes, and this document set.
Those are submission artefacts and are still being finalised.

## The build being submitted

| Layer | Frozen state |
|---|---|
| Intake | 5 constraints — target AI workflow (18 + "Any"), industry (24 + "Any"), organisation size (5 bands), data-privacy posture (2), monthly budget. Plus optional vendor exclusions and an optional cosmetic project name |
| Retrieval | Chroma over 3,023 cases / 9,069 chunks, `all-MiniLM-L6-v2`, `RELEVANCE_THRESHOLD = 0.52`, top-15 |
| Filtering | Deterministic privacy hard-rule (`GOVERNABLE_FOR_REGULATED`, 25 ids) then user vendor exclusions |
| Ranking | Plain frequency count, no weighting |
| Cost | 41 priced tools across seat / token / compute / free models, illustrative |
| LLM | Groq, summary paragraph only, after the stack and prices are already decided |
| Output | 3 blocks (stack, cost, cases) in tabs, evidence dropdown, export, `.env` scaffold, session-scoped saves |
| Telemetry | Local JSON-lines, no identifier, no free text |

## What is deliberately NOT in the freeze

These were scoped, understood, and cut. They are Icebox, not forgotten — each
has a build guide or a roadmap position, which is the difference between a
deferred feature and an abandoned one.

| Ref | Feature | Why it's out | Where it's written up |
|---|---|---|---|
| B.1 | Cost PDF export | The text/markdown export covers the need; PDF is polish | Build Guide 26 |
| B.3 | Live pricing sync | Needs vendor APIs and a maintenance commitment neither of us can honour after submission. Hand-built + labelled illustrative is the honest version | Build Guide 30 |
| B.4 | Validation overlay on `technology_landscape.csv` | Second data source, second set of licence questions | Build Guide 29 |
| B.7 | Seat fractions | Proposal written, judged not worth the added model complexity at this scale | Build Guides 28, 31 |
| B.8 | PDF blueprint export | Guide written (34), 45–90 min of work, cut in favour of finishing verification. **This was the last live build/no-build decision and it was decided as "no".** | Build Guide 34 |
| — | Mobile / responsive layout | Never tested on a phone. Desktop-only is stated as a known limitation rather than implied to work | `Known-Limitations-v1.md` |
| — | Disabling or flagging unpopulated dropdown pairs | The real fix for the 185 empty workflow × industry pairs. Too large for freeze week; the product discloses the problem instead of hiding it | `Known-Limitations-v1.md`, Build Guide 35 |
| — | Free-text intake | Would change the relevance-threshold picture entirely — the nonsense-control distributions only overlap harmlessly *because* input is constrained to dropdowns. Gabi's condition on the current threshold was explicitly "if there will ever be free text, we should check again" | Build Guide 35 |

## Change control after the freeze

Three categories of change are permitted, in descending order of how much
justification they need:

1. **Factual corrections.** A statement in the product or the docs that is
   *false* gets fixed, because leaving a known-false claim in a submission is
   worse than editing during a freeze. Every one is dated in place and listed in
   `16-P22-Final-Consistency-Pass-v1.md`.
2. **Verification tooling.** Scripts and tests that only *measure* the frozen
   product. These cannot change behaviour, so they carry no regression risk.
3. **Submission artefacts.** Deck, notes, README, PM documents.

Explicitly **not** permitted, no matter how small or how tempting: changing a
number in the code to make a document true, adding a feature because a user
asked for it late, or "quick" UI improvements. If something in the frozen product
is wrong but not false — a design choice we'd now make differently — it becomes a
known limitation, not a patch.

### Changes made under this rule since the freeze

| Date | Change | Category | Logged in |
|---|---|---|---|
| 2026-07-28 | `--until` bound + unbounded-run warning on the two P.14 metrics scripts (Gabi's finding: published 83% export rate had silently become 56%) | 2 | Build Guide 37 |
| 2026-07-28 | Repository clean + README pass (15 items) | 1, 3 | `14-P21` |
| 2026-07-30 | Corpus-coverage figure corrected from 205/47% to 185/43% in 3 code files and 6 documents, after the store rebuild changed it | 1 | `16-P22` |
| 2026-07-30 | `--since/--until/--p14` added to `validation_metrics_table.py`, the third and last log-reading script — it was silently producing a different table from the published one | 1, 2 | `16-P22` |
| 2026-07-30 | Ten surviving "24 tools" references corrected to 41; effort total, prototype licence label, column count, outlier values, session counts corrected | 1 | `16-P22` |

No change in that table altered what the app does for a user. That is the test
the freeze is meant to enforce, and it holds.

---

## Sign-off

| Name | Confirms | Date |
|---|---|---|
| Ash | The frozen scope above is what we are submitting, and the Icebox list is complete | A.CARLIN - 30.07.26 |
| Gabi | Retrieval, corpus, pricing table and telemetry are final as committed | _____ |

**Both names required.** A freeze one person declared is a preference, not a
freeze.
