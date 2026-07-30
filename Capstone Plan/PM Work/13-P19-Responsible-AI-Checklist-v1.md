# P.19 — Final Responsible-AI Checklist

*Card P.19. **Pre-filled with the evidence verifiable in code and documents.**
Items marked ⚠️ need a human to look, click, or decide. Do not tick those without
doing them; the whole point of this card is that it's a real check, not a
formality.*

**Drafted:** 2026-07-27 (audit of `Ash3-update`) · **Finalised:** 2026-07-30
(re-audited against `Ash6` after the P.22 pass)
**Sign-off owners:** Joint (Ash + Gabi)

**Status at finalisation:** P.14 signed off by Gabi 2026-07-28. Feature freeze
declared 2026-07-28 and recorded in `15-P15-Feature-Freeze-v1.md`. **Five items
remain open**, all of them requiring a human: the deck fabrication check (the
decks were pulled from the branch on 2026-07-28 and are being finalised by hand),
clicking source links, colour contrast, mobile, and the Week 4 ethics checkpoint.

> **What the P.22 pass changed about this checklist.** Two items ticked below were
> ticked on the strength of figures that turned out to be stale, and one claim in
> this document was itself wrong. They are corrected in place with notes rather
> than silently re-ticked, because a checklist that hides its own corrections is
> the failure mode this card exists to prevent. See
> `16-P22-Final-Consistency-Pass-v1.md`.

---

## No fabricated trust signals (the standing check)

This was a real flaw in our first build, so it's checked explicitly every time.

- [x] **No testimonials or quotes anywhere.** Searched the app and docs — the only
      quoted outcomes are the dataset's own `Outcomes & Benefits` text, attributed
      to named organisations with source URLs.
- [x] **No fake certifications or compliance badges.** No SOC 2 / ISO / HIPAA
      badge appears; the app states the opposite (compliance filtering is a
      "shortlist, not certification").
- [x] **No invented user counts, press mentions, awards, or logos.** The only
      numbers in the hero are computed live from the dataset (3,023 cases, 41
      tools, 24 industries).
- [x] **The prototype labels itself as one.** "PROTOTYPE · DEMO DATA" badge in the
      top bar, plus the "4-week student prototype" honest-scope note in the hero.
- [ ] ⚠️ **Same check applied to the finished deck.** Still open, and the reason
      changed: the decks were built (v2–v6) and then **removed from the branch on
      2026-07-28** while wording is finalised, to be re-added by hand. So there is
      currently no deck in the repo to check. Run this the moment one lands — no
      borrowed logos, no implied partnerships, no "trusted by", and every figure
      matching `16-P22-Final-Consistency-Pass-v1.md`.

## Honesty of claims

- [x] **Pricing is labelled illustrative** everywhere it appears (cost block
      caption, export footer, model card, known limitations).
- [x] **Compliance filtering is labelled directional** in-product, not certified.
- [x] **Dataset bias is disclosed in-product**, not just in docs — the "About this
      data — bias & dataset skew" expander gives the ~45% / ~40% concentration
      figures.
- [x] **The LLM's role is stated honestly** — "the LLM only ever writes the summary
      paragraph; it never invents the tools or the prices," and that matches the
      code (`generate_summary()` receives an already-final ranked list).
- [x] **Ranking is genuinely frequency-based** — verified in `app/logic/filter.py`:
      a plain `collections.Counter` with `most_common()`, no manual weighting,
      boosting or hand-reordering anywhere in the path.
- [x] **The `~2 min TO BLUEPRINT` hero stat is defensible — decided 2026-07-28.**
      This was flagged as the clearest over-claim in the product on the basis of
      the **mean** time-to-results (372s / ~6 min — this document said 381.6s,
      corrected 2026-07-30; 381.6 was computed over the wrong window). That was
      the wrong statistic: the mean is skewed by three sessions over 500s, two of
      them 1,287s and 1,617s, where a participant left the form open. The
      **median across the real user-test round is 114s
      (1.9 min)** — so "~2 min" describes the typical user honestly, and the number
      briefly changed to "~5 min" matched neither the median nor the mean. Reverted
      to `~2 min`, with the reasoning in a comment at `app/intake.py:500` and both
      statistics reported in the P.14 write-up so nothing is concealed.
- [ ] ⚠️ **Deck metrics match the real P.14 output**, not rounded-up versions.
      Check once a deck is back in the repo. **This got sharper on 2026-07-30:**
      the script the README tells a marker to run to regenerate that table
      (`validation_metrics_table.py`) had no window support, so it printed 23%
      export / 4/5 trust / 106 sessions against the published 83% / 5/5 / 12. Any
      deck figure must match the `--p14` output, and `--p14` now exists on all
      three log-reading scripts.
- [x] **The numbers the app itself states are true of the store it ships with —
      re-verified 2026-07-30, and one was not.** The banner's explanation claimed
      205 of 432 dropdown pairs (47%) have zero cases. Recounted against the
      committed store: **185 (43%)**. The figure was measured correctly on
      2026-07-27 and then went stale when the store was rebuilt on the 28th for
      the Cloud deploy. Corrected in `app/dashboard.py`, `app/pipeline.py` (×2) and
      six documents. This is the only instance found where shipped app text stated
      a number the repo's own data refuted.

## Data minimisation & privacy

- [x] **No accounts, login, or persistent identifier** — re-scanned `app/`; no
      `user_id`/login/cookie/email pattern.
- [x] **No PII in the five intake fields** — all dropdown/radio/number widgets.
- [x] **Free-text project name never reaches the LLM or telemetry** — verified in
      `app/pipeline.py` and every `log_event()` call site.
- [x] **Telemetry contains only event names, timestamps and numeric/enum values** —
      all 9 call sites audited.
- [x] **No third-party analytics service.**
- [x] **Fonts are self-hosted** (`static/fonts/`), so no third-party font CDN call
      from the user's browser.
- [x] **Weekly data-minimisation checkpoints exist and are dated** — Weeks 1, 2, 3
      recorded in `PM & Ethics/Ethical-Action-Plan-v2.md`.
- [ ] ⚠️ **Week 4 checkpoint** still to be added at submission time.

## Traceability & evidence

- [x] **Every recommended tool links back to real cases** that used it, with
      reported outcomes and source URLs.
- [x] **Vendor links are official homepages** (41 entries added deliberately, not
      scraped) and open in a new tab with `rel="noopener"`.
- [ ] ⚠️ **Click every source link in the demo path and in the deck.** The guide
      requires this explicitly. A dead or wrong link on stage is the most
      avoidable credibility loss available. **Human must do this.**
- [ ] ⚠️ **Spot-check a sample of the 41 vendor URLs** still resolve (they're
      homepages, so low risk, but unverified by me).

## Statistical honesty

- [x] **Credible intervals reported alongside every small-sample rate** (P.14).
- [x] **No comparative claim** ("A beat B") anywhere — explicitly ruled out in the
      P.14 write-up as needing a powered study.
- [x] **All four targets are now met, and the *reason* is not overstated** — the
      final round (n=8) scored trust median 5/5 against the ≥4/5 target, up from
      the earlier round's 3/5 miss. Both the build and the participants changed
      between rounds, so no causal claim is made about our fixes raising it. The
      earlier miss stays on the record in the P.14 write-up rather than being
      deleted now that it is no longer current.
- [x] **"Sessions ≠ distinct people" caveat recorded** (telemetry has no user id) —
      and for this round the 8 responses are corroborated participant-by-participant
      against the recorded session sheet, in order.
      > **Extended 2026-07-30 (P.22):** the caveat was applied only to the
      > *denominator*. Two `export_clicked` events sit 2 seconds apart in one
      > session — a double-click — so the 10 exports came from **9** sessions. The
      > 83% headline is correct as an event count and is left as published, but
      > measured as sessions-that-exported it is 9/12 = **75%**, which still clears
      > the ≥40% target. Now stated in the P.14 write-up. Applying a caveat to one
      > side of a fraction and not the other is how a rate gets flattered.
- [x] **Recruitment bias disclosed** — all 8 participants are professional contacts
      of the team, which plausibly inflates trust scores. Stated in P.14 and
      Known-Limitations rather than left for a marker to notice.
- [x] **Telemetry dataset is final** — real-user testing completed 2026-07-28 with
      8 participants; figures are windowed to that round and reproducible via
      `scripts/telemetry_funnel.py --p14` (equivalent to
      `--since "2026-07-27 23:00" --until "2026-07-28 01:31"`). **All three**
      log-reading scripts now accept `--p14` and warn on an unbounded run.

## Accessibility & inclusion (Card P.13 overlap)

- [x] **Non-native English speakers included in real testing** — 5 of the 8 final-round
      participants (Card P.13's ask was at least one). Two of their findings were
      acted on the same night: the privacy-posture tooltip previously defined only
      "Regulated" and left "Standard" to be inferred, and the org-size bands left a
      gap testers didn't see themselves in.
- [ ] ⚠️ **Jargon pass completed with both personas** (non-technical founder,
      non-native speaker) — shortlist prepared in `12-P13-Clarity-Jargon-Shortlist-v1.md`.
      Partially superseded: the tooltip and band fixes above came from real
      non-native speakers rather than the prepared shortlist, but the shortlist
      itself was never worked through item by item.
- [ ] ⚠️ **Colour-contrast check** on the dark theme's green/orange/indigo accents.
- [ ] ⚠️ **Mobile/responsive check** — never tested on a phone; tracked as its own
      QA card.

## Scope & documentation integrity

- [x] **Known limitations documented** in `PM & Ethics/Known-Limitations-v1.md`
      **and** visible in-product (How it works tab).
- [x] **Deferred features listed honestly** as Icebox with roadmap positions —
      **corrected 2026-07-30.** This bullet said the deferred set was
      "B.1, B.3, B.4, B.7, B.8, mobile". **B.1 and B.8 both shipped**: the Markdown
      cost one-pager and the PDF blueprint export, behind the Download popover,
      with 8 `onepager_downloaded` and 8 `pdf_downloaded` events in telemetry (4 of
      the PDFs inside the P.14 window). The genuinely deferred set is **B.3, B.4,
      B.7 and mobile** — verified against the code, not against the previous
      version of this list. Corrected in `15-P15-Feature-Freeze-v1.md` too.
      > Under-claiming what we built is a smaller sin than over-claiming, but it is
      > the same defect: an Icebox list reused without re-checking it. It was found
      > because Gabi asked whether `fpdf2` was really a dependency.
- [x] **README documents real setup steps**, including the mandatory
      `rebuild_knowledge_base.py` step for a fresh clone.
      > **Note 2026-07-28:** that step is no longer mandatory, and this line is
      > kept rather than rewritten so the change is visible. Since the Cloud
      > deploy (Build Guide 36) `chroma_store/` is committed, so a fresh clone
      > runs the app straight after `pip install` + the API key. Running
      > `rebuild_knowledge_base.py` is now actively discouraged — it deletes the
      > committed store and needs the gitignored source CSV to rebuild. The README
      > says so, and the script refuses to delete anything if that CSV is absent.
- [x] **Feature freeze declared and dated** (Card P.15) — **2026-07-28**, recorded
      in `15-P15-Feature-Freeze-v1.md` with the frozen scope, the Icebox list
      (B.1, B.3, B.4, B.7, B.8, mobile, unpopulated-pair flagging, free-text
      intake), the change-control rule and a log of every post-freeze change.
      Still needs both signatures.
- [x] **No doc references a feature that got cut, and no doc references a file
      that isn't there** — swept 2026-07-30. Every Icebox item is described as
      Icebox or proposed, never as delivered. Broken references found and fixed:
      the Kanban footer's pre-renumbering PM Work names (which pointed at *wrong*
      documents, not missing ones), two scripts citing `P9-Backend-Dry-Run` under
      the wrong folder, a citation to the unredacted testing spreadsheet, and nine
      stale code line-numbers in the schema doc. No deck filename is referenced
      anywhere, so pulling the decks left nothing dangling.

---

## The five open items, and who does each

| # | Item | Owner | Blocked on |
|---|---|---|---|
| 1 | Fabrication check + figure check on the finished deck | Joint | A deck being back in the repo |
| 2 | Click every source link in the demo path and the deck | Human | Nothing — do this first, it's the cheapest credibility save available |
| 3 | Colour-contrast check on the dark theme's green/orange/indigo | Human | Nothing |
| 4 | Mobile/responsive check | Human | Nothing. If it fails, it stays a known limitation — the freeze forbids fixing it |
| 5 | Week 4 ethics checkpoint, dated at submission, in **both** copies of the Ethical Action Plan | Ash | Should be written last |

Also unticked and deliberately so: the **jargon shortlist** in
`12-P13-Clarity-Jargon-Shortlist-v1.md` was never worked through item by item. It
is partly superseded — 5 of the 8 real testers were non-native English speakers
and two of their findings were fixed the same night — but "partly superseded by
better evidence" is not "done", so it stays open rather than being quietly ticked.

## Sign-off

| Name | Role | Confirms | Date |
|---|---|---|---|
| Ash | Person B | UI, product, ethics docs | A.CARLIN - 30.07.26|
| Gabi | Person A | retrieval, telemetry, metrics | G.SCZUKA - 30.07.26 |

**Rule:** every ⚠️ item must be either genuinely done and ticked, or explicitly
recorded as a known limitation. Nothing gets ticked on the assumption it's
probably fine.

**The rule earned its keep.** Two items on this list were ticked on 2026-07-27
against figures that were true then and stale by the 28th, and one stated the mean
as 381.6s when it was 372.3s. Nothing was ticked dishonestly — but "verified once"
and "verified against the build being submitted" are different claims, and only
the second one is worth a signature. Hence the re-audit on 2026-07-30 and the
corrections above.
