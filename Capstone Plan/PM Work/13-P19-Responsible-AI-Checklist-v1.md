# P.19 — Final Responsible-AI Checklist (pre-filled draft)

*Card P.19. **Pre-filled with the evidence I could verify in code and documents.**
Items marked ⚠️ **cannot be signed off by me** — they need a human to look, click,
or decide. Do not tick those without doing them; the whole point of this card is
that it's a real check, not a formality.*

**Prepared by:** Claude (code + doc audit of `Ash3-update`) · **Date:** 2026-07-27
**Sign-off owners:** Joint (Ash + Gabi) · **Status:** P.14 signed off by Gabi
2026-07-28 after the 8-participant round; remaining open items are the mobile,
colour-contrast and jargon-shortlist passes

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
- [ ] ⚠️ **Same check applied to the finished deck.** Must be re-run once the deck
      exists — no borrowed logos, no implied partnerships, no "trusted by".

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
      the **mean** time-to-results (381.6s / ~6 min). That was the wrong statistic:
      the mean is skewed by two sessions of 1,287s and 1,617s where a participant
      left the form open. The **median across the real user-test round is 114s
      (1.9 min)** — so "~2 min" describes the typical user honestly, and the number
      briefly changed to "~5 min" matched neither the median nor the mean. Reverted
      to `~2 min`, with the reasoning in a comment at `app/intake.py:500` and both
      statistics reported in the P.14 write-up so nothing is concealed.
- [ ] ⚠️ **Deck metrics match the real P.14 output**, not rounded-up versions.
      Check once the deck is built (Card P.21 re-checks this too).

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
- [x] **Recruitment bias disclosed** — all 8 participants are professional contacts
      of the team, which plausibly inflates trust scores. Stated in P.14 and
      Known-Limitations rather than left for a marker to notice.
- [x] **Telemetry dataset is final** — real-user testing completed 2026-07-28 with
      8 participants; figures are windowed to that round and reproducible via
      `scripts/telemetry_funnel.py --since "2026-07-27 23:00" --until "2026-07-28 01:31"`.

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
- [x] **Deferred features listed honestly** as Icebox with roadmap positions
      (B.1, B.3, B.4, B.7, B.8, mobile).
- [x] **README documents real setup steps**, including the mandatory
      `rebuild_knowledge_base.py` step for a fresh clone.
      > **Note 2026-07-28:** that step is no longer mandatory, and this line is
      > kept rather than rewritten so the change is visible. Since the Cloud
      > deploy (Build Guide 36) `chroma_store/` is committed, so a fresh clone
      > runs the app straight after `pip install` + the API key. Running
      > `rebuild_knowledge_base.py` is now actively discouraged — it deletes the
      > committed store and needs the gitignored source CSV to rebuild. The README
      > says so, and the script refuses to delete anything if that CSV is absent.
- [ ] ⚠️ **Feature freeze declared and dated** (Card P.15) — needs the human
      decision, then a line in the changelog.
- [ ] ⚠️ **No doc references a feature that got cut** — final sweep at P.21.

---

## Sign-off

| Name | Role | Confirms | Date |
|---|---|---|---|
| Ash | Person B | UI, product, ethics docs | _____ |
| Gabi | Person A | retrieval, telemetry, metrics | _____ |

**Rule:** every ⚠️ item must be either genuinely done and ticked, or explicitly
recorded as a known limitation. Nothing gets ticked on the assumption it's
probably fine.
