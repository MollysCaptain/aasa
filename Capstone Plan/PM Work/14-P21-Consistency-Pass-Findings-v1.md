# P.21 — Consistency Pass: findings & remaining actions (v1)

*Card P.21. I ran the mechanical cross-checks the card asks for and found **real
drift**, listed below with exact file/line references. Fixing these is quick; the
human-only items (backup, submission) are at the end.*

**Run by:** Claude (repo-wide scan of `Ash3-update`) · **Date:** 2026-07-27
**Owner to action:** Joint
**Closed:** 2026-07-30 — see the status box below and
`16-P22-Final-Consistency-Pass-v1.md` for the second, deeper pass.

> ## Status as of 2026-07-30 — read this before acting on anything below
>
> This document is now a **record of the first pass**, not a to-do list. Its
> findings are closed, and the second pass (`16-P22`) found that two of them were
> reported less accurately than they should have been:
>
> - **Finding 1 was right but badly incomplete.** It listed 4 places saying "24
>   tools". All 4 are fixed — but there were **10 more** it missed, including the
>   pitch-day spoken script at Build Guide 17:253. Those are fixed too, and listed
>   in `16-P22`. Note also that this document's own line 23 still quotes "3,023
>   cases, 24 tools" while describing the fix, which is left visible as an example
>   of how easily the number propagates.
> - **Finding 3 was a false positive.** The remaining `ATSA` occurrence in Build
>   Guide 13 (line 1144) is a deliberate post-mortem *about* the rename — "the Ash
>   branch had already renamed the project (ATSA → AASA)". Deleting it would
>   destroy the narrative. **No action taken, and none should be.**
> - **The line numbers throughout this document are stale**, including the "clean"
>   section's claim that `.DS_Store` sits at `.gitignore` line 236 (it was 254, and
>   that block has since been rewritten). Cross-check against the file, not against
>   this document.
> - **The remaining human-only actions table at the end is superseded** by the
>   equivalent table in `16-P22`, which is current.
>
> Kept in full rather than trimmed to the parts that held up, because the useful
> content of a consistency pass includes which of its own findings didn't survive
> contact with the code.

---

## Findings that need a fix

### 1. Stale pricing-table count: "24 tools" (actual: **41**) — 4 places
### — CLOSED 2026-07-30. All 4 fixed, plus 10 more this pass missed (see `16-P22`).

The pricing table has grown to 41 priced tools (verified in
`app/logic/pricing.py`), but several docs still say 24:

| File | Line | Current text |
|---|---|---|
| `Capstone Plan/AASA-Project-Handbook-v2.md` | 86 | "hand-built, **24 tools**" |
| `Capstone Plan/PM Work/01-Pitch-v2.md` | 26 | "a small, hand-built pricing table ourselves (**24 tools**)" |
| `Capstone Plan/Build Guide/11-4-Week-Action-Plan-v1.md` | 58 | "dataset stats: 3,023 cases, **24 tools**" |
| `Capstone Plan/Build Guide/17-Build-Guide-Package-Pitch-Week4-v1.md` | 211 | "the normalisation challenge (2,511 → **24 tools**)" |

**Why it matters:** the deck's data-foundation slide draws on exactly these
sentences. Saying 24 when the app shows 41 is the kind of small inconsistency a
reviewer notices. **Fix: change to 41** (or "41 priced tools").

### 2. ~~`~2 min TO BLUEPRINT` hero stat contradicts our own telemetry~~ — RESOLVED 2026-07-28

**This finding was itself wrong, and it is worth keeping visible rather than
deleting.** It compared the hero's "~2 min" against the **mean** time-to-results
(381.6s / ~6 min) and concluded the product was over-claiming.

The mean is the wrong statistic for "how long does this take a typical user". It
is dragged up by two outlier sessions of **1,287s and 1,617s**, where a
participant opened the form and came back to it later. Measured across the real
user-test round:

| Statistic | Value |
|---|---|
| **Median time-to-results** | **114s (1.9 min)** |
| Mean | 372s (6.2 min) |
| Outliers driving the mean | 1,287s and 1,617s |

So "~2 min" was accurate all along. Acting on this finding briefly changed the
hero to "~5 min", which matched **neither** the median nor the mean — a correction
that made the number less true. Reverted to `~2 min` on 2026-07-28, with the
reasoning recorded at `app/intake.py:500` and both statistics published in the
P.14 write-up.

**Lesson worth carrying:** a consistency pass that compares a claim against the
wrong summary statistic can manufacture a problem. Check which statistic the claim
is actually making before calling it an over-claim.

### 3. One `ATSA` leftover after the AASA rename
### — ~~CLOSED~~ **WITHDRAWN 2026-07-30: this finding was wrong.** The occurrence is at Build Guide 13 line 1144 and is a deliberate post-mortem about the rename itself. Leave it.

`Capstone Plan/Build Guide/13-Build-Guide-Epic2-Retrieval-v1.md` still contains
the old `ATSA` name. Low stakes, but it's in a document set we're submitting.

### 4. Duplicated Ethical Action Plan — DECIDED 2026-07-28: keep both

`PM & Ethics/Ethical-Action-Plan-v2.md` and
`Capstone Plan/PM Work/03-Ethical-Action-Plan-v2.md` are **byte-identical**
(re-verified 2026-07-28, both hash `ea9d481`).

**Decision: keep both copies rather than replacing one with a pointer.** The two
document sets are read by different audiences — `PM & Ethics/` is the ethics
evidence bundle, `Capstone Plan/PM Work/` is the numbered PM sequence — and each
should stand on its own without a reader having to follow a cross-directory link.

**The accepted cost:** they can drift. Mitigation is a one-line check, which
belongs in the pre-submission pass:

```bash
diff "PM & Ethics/Ethical-Action-Plan-v2.md" \
     "Capstone Plan/PM Work/03-Ethical-Action-Plan-v2.md" && echo "in sync"
```

If that ever prints a diff, the `PM & Ethics/` copy is canonical.

---

## Checks that came back clean

- [x] **The 197-vs-3,023 ambiguity is already handled** — the Handbook's §9 wording
      plus its added clarification correctly distinguish the 197-case prototype
      slice from the 3,023-row product dataset. No action.
- [x] **`.DS_Store` is not tracked in git** and is correctly listed in
      `.gitignore` (line 236). It exists locally only.
- [x] **`chroma_store/`, `.env`, `.venv` are not tracked** — no secrets or large
      binaries in the repo.
- [x] **Dataset figures are consistent** where they matter: 3,023 cases / 24
      industries / 88.7% alias coverage agree across the model card, the app's
      hero (computed live), the methodology block and the P.14 write-up.
      > *Re-verified 2026-07-30 by recounting from `chroma.sqlite3` rather than by
      > comparing documents: 3,023 cases and 88.7% (2,682/3,023) both hold, and the
      > 24 dropdown industries match the corpus's 24 distinct values exactly in
      > both directions. **But this check was scoped too narrowly** — it compared
      > figures to each other and found agreement, while the workflow × industry
      > coverage figure (205/47%) agreed with itself in nine places and was wrong
      > in all nine. Agreement between documents is not verification.*
- [x] **P.14 metrics agree between the script output and the write-up** —
      re-verified 2026-07-28 against the final real-user round (n=8): 12 sessions,
      83% export rate, 100% net value, CIs 59–93% / 72–99%, trust median 5, avg
      LLM 1.34s. Figures are windowed to the round via
      `--since "2026-07-27 23:00" --until "2026-07-28 01:31"` and the boundary was stress-tested — moving it
      back an hour leaves every reported count identical.
      *Superseded:* the earlier round's 14 sessions / 50% / 80% / CIs 42–94% and
      30–70% / trust median 3 are retained in the P.14 write-up as a prior
      iteration, deliberately not pooled with the final round because the build
      differed.
- [x] **Known-limitations wording is consistent** across the app's How-it-works
      tab, `docs/model-card.md` and the new `Known-Limitations-v1.md`.
- [x] **`requirements.txt` matches what the code imports**, including `scipy` for
      `credible_interval.py`.
- [x] **No doc references a feature as shipped that doesn't exist** — B.1/B.3/B.4/
      B.7/B.8 are all described as Icebox/proposed, not delivered.

---

## Remaining human-only actions
### — SUPERSEDED 2026-07-30 by the equivalent table in `16-P22-Final-Consistency-Pass-v1.md`. Items 1 and 8 below are now done (P.15 freeze declared and recorded; Week 4 checkpoint still outstanding). Use the P.22 table.

| # | Action | Owner | Why I can't do it |
|---|---|---|---|
| 1 | **Declare + date the feature freeze** (P.15) and Icebox the unfinished Could-Haves (B.1 #38) | Joint | A decision, not a fact. I can write the changelog line once you decide. |
| 2 | ~~Confirm the telemetry dataset is final~~ **Done 2026-07-28** — Gabi confirmed after the 8-participant round; P.14 signed off. | Gabi | Closed. |
| 3 | **Click every source link** in the demo path and the deck | Human | Requires actually visiting pages. |
| 4 | **Colour-contrast + mobile checks** | Human | Needs eyes on a real screen/device. |
| 5 | **Two timed rehearsals + outside feedback** (P.20, SP.5) | Joint | Performance, not a document. |
| 6 | **Back up the whole project off-machine** (cloud/external drive) | Joint | I can't write outside the repo. |
| 7 | **Submit via the bootcamp channel + confirm receipt** | Joint | I have no access, and confirmation is required. |
| 8 | **Add the Week 4 ethics checkpoint** at submission time | Ash | Should record the final state, so it's written last. |

## Suggested order for the rest of the week

1. Freeze decision + Icebox B.1 (30 min) — unblocks everything.
2. Decide on B.8 PDF export: build it (guide 34, 45–90 min) or Icebox it.
3. Fix findings 1–3 above (15 min) — I can do these on your say-so.
4. ~~Gabi signs off P.14~~ **done 2026-07-28**. P.13 is now partly covered by real
   testing — 5 of the 8 participants were non-native English speakers, and two of
   their findings were fixed the same night (privacy-posture tooltip, org-size
   bands) — but the prepared jargon shortlist was never worked through item by item.
5. Build the deck from the P.17 outline + P.18 content (I can draft; needs your
   screenshots of the final UI).
6. P.19 checklist — work the ⚠️ items, including clicking links.
7. Rehearsals ×2.
8. Final consistency re-diff, backup, submit, Week 4 ethics checkpoint.
