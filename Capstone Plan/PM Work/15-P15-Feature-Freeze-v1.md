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
- **No new dependencies, and now pinned.** `requirements.txt` is closed, and as
  of 2026-07-30 it pins versions rather than merely listing names — Gabi's point:
  an unpinned file means Streamlit Cloud resolves whatever is newest at build
  time, so the app a marker opens is not guaranteed to be the app we tested.
  Pinning is what makes "closed" enforceable rather than aspirational.

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

> **Corrected 2026-07-30, after Ash had already signed this document.** The table
> below originally listed **B.1** and **B.8** as cut. Both **shipped**, and the
> telemetry proves it: `onepager_downloaded` fires 8 times and `pdf_downloaded`
> 8 times across the log, 4 of the latter inside the P.14 user-test window. B.1 is
> the Markdown cost one-pager (`aasa-cost-onepager.md`) and B.8 is the PDF
> (`app/export.py:blueprint_to_pdf`), both behind the Download popover.
>
> This surfaced from an unrelated question — Gabi asked whether `fpdf2` was
> really needed, since she doesn't have it installed. Checking the answer meant
> checking whether the PDF feature exists. It does.
>
> Worth naming plainly: a feature-freeze document that misstates what shipped is
> the single most useless document in the set, and this one did so in the section
> a marker is most likely to check against the running app. The error came from
> carrying forward an Icebox list (`B.1, B.3, B.4, B.7, B.8, mobile`) that was
> accurate when written and stale by the time it was reused, without checking it
> against the code — which is *exactly* the failure the P.22 pass was created to
> catch, committed while writing up P.22.

**What actually shipped from the Icebox:** B.5 (optional project name), B.6
(session-scoped saved blueprints), **B.1** (Markdown cost one-pager) and **B.8**
(PDF blueprint export). All four are in the frozen build above.

**What is genuinely out:**

| Ref | Feature | Why it's out | Where it's written up |
|---|---|---|---|
| B.3 | Live pricing sync | Needs vendor APIs and a maintenance commitment neither of us can honour after submission. Hand-built + labelled illustrative is the honest version. Nothing was built — no `pricing_sync.py` exists | Build Guide 30 |
| B.4 | Validation overlay on `technology_landscape.csv` | Second data source, second set of licence questions. Nothing was built — no `overlay.py` exists | Build Guide 29 |
| B.7 | Seat fractions | Proposal written and declined: the fuller workflow-fraction table ("Option A") is referenced in `app/logic/cost.py:53` as the proper fix and deliberately not implemented. The `SEAT_CEILING = 25` stopgap ships instead | Build Guides 28, 31 |
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
| 2026-07-30 | P.9's blank defect list and go/no-go completed retrospectively; two previously-undisclosed defects added to `Known-Limitations-v1.md` | 1 | `16-P22`, P.9 doc |
| 2026-07-30 | **`requirements.txt` pinned** (Gabi's call). 7 of 10 pinned and verified against PyPI for Python 3.11; `pandas`/`scikit-learn`/`scipy` left unpinned because the proposed versions do not exist and a wrong pin fails the Cloud build | 1, 2 | this doc, `requirements.txt` |
| 2026-07-30 | **This document corrected:** B.1 and B.8 were listed as cut. Both shipped — telemetry shows 8 `onepager_downloaded` and 8 `pdf_downloaded`. Found via Gabi's `fpdf2` question | 1 | this doc |

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
