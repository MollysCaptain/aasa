# P.18 — Architecture & Results Slide Content (v1)

*Card P.18. Ready-to-drop content for pitch slides 5 (Architecture) and
6 (Real Test Results). Every number below is copied from our actual computed
output, not retyped from memory — see the source note under each table.*

**Owner:** Person A (Gabi) · **Prepared by:** Claude, from committed project
output · **Date:** 2026-07-27 · **Hand to:** Person B for the deck (Card P.17)

---

## Slide 5 — Architecture

**Slide headline:** *Deterministic where it matters. The model only writes prose.*

Use the existing pipeline diagram (`PM & Ethics/pipeline-diagram.mmd` /
`Mermaid-Diagram.png`) and attach these short captions to each stage. The caption
explains **why it's built that way**, which is the point of the slide.

| Stage | Caption (3–8 words) |
|---|---|
| **1. Five constraints in** | "No accounts, no PII — five dropdowns" |
| **2. Semantic retrieval (Chroma + MiniLM)** | "Finds comparable real deployments, not keyword matches" |
| **3. Privacy filter (hard rule)** | "Filter before ranking → compliance is code, not a model guess" |
| **4. Vendor exclusions (user preference)** | "Your constraints applied on top of the hard rule" |
| **5. Frequency ranking** | "Plain counting — no hand-picked winners" |
| **6. Cost engine (token / seat / usage)** | "Priced by billing model, flagged against your budget" |
| **7. LLM summary (last step only)** | "Model receives the final list — it can't invent tools" |
| **8. Three-block blueprint + sources** | "Every recommendation links back to real evidence" |

**The one line to say out loud:** "The LLM is the *last* step and the *smallest*
one — by the time it runs, the tools and the prices are already decided by
deterministic code. That's deliberate: a model guessing at compliance would be
the single most dangerous thing this product could do."

**Supporting facts if asked:**
- Knowledge base: **3,023** real AI-deployment cases, **41** tools priced, **24** industries.
- Retrieval asks for 15 chunks and de-duplicates to unique cases before ranking
  (so one case can't count as three pieces of evidence).
- Ranking is a `collections.Counter` over the filtered cases — verified in code,
  no manual weighting anywhere in the path.

---

## Slide 6 — Real Test Results

**Slide headline:** *Real testers, honest numbers, intervals included.*

**Source:** `PM & Ethics/P14-Validation-Metrics-Final-v1.md`, computed by
`scripts/telemetry_funnel.py --since "2026-07-27 23:00"` +
`scripts/credible_interval.py --since "2026-07-27 23:00"` from
`data/telemetry.log`. **Do not retype these — copy them.**

Updated 2026-07-28 for the final real-user round (8 participants). The `--since`
window matters: run bare, the scripts pool our own development runs and three
earlier builds and report 18 responses over 100 sessions, which measures nothing.

| Metric | Target | Actual | 90% credible interval | Met? |
|---|---|---|---|---|
| Net value ("saved me research time") | ≥70% | **100%** (8/8) | 72%–99% | Yes |
| Blueprint export rate | ≥40% | **83%** (10/12) | 59%–93% | Yes |
| Compliance-rule pass rate | 100% | **100%** (2/2 regulated profiles) | — (deterministic) | Yes |
| Trust score (median) | ≥4/5 | **5/5** | — (ordinal) | Yes |
| Avg. LLM latency | — | **1.34s** (12 calls) | min 0.57 / max 2.62 | — |
| Sample size | 5–8 testers | 8 participants / 12 sessions | not powered for comparative claims | Yes |

**Funnel (read as a sequence, not three independent stats):**

> **12** viewed a blueprint → **10** exported it (83% of viewers) → **8** answered
> the survey, **8** of whom said it saved them research time (100% of respondents).

### The three things this slide must communicate

1. **We tested with real people and computed the numbers from logged behaviour**,
   not impressions — and each of the 8 responses ties to a named participant, in
   order, cross-checked against the recorded session sheet.
2. **All four targets met — and we don't claim credit for the improvement.** The
   earlier round missed on trust (3/5). Between rounds the build changed *and* the
   participants changed, so the jump to 5/5 is not a measured before/after. Say
   this out loud; it is more convincing than the result itself.
3. **The intervals matter more now, not less.** A bare "100%" invites disbelief;
   its 90% interval is 72–99%, and one changed answer moves the rate 12.5 points.
   Report Beta(1,1) intervals and make **no** comparative claim.

### Visual guidance

Keep it a clean table — don't over-design. If you want one graphic, a simple
horizontal bar per rate metric with a vertical target line works, but the
interval must stay visible (a whisker or the range printed next to the bar).
**Never show a bare percentage without its interval on this slide.**

### Honesty footnotes for the slide (small text, but present)

- "12 sessions" ≠ 12 distinct people — telemetry has no user identifier by
  design (privacy choice), and several participants generated more than one
  blueprint. **8 survey responses = 8 participants**, corroborated against the
  session sheet.
- Compliance pass rate is drawn from the recorded P.9 dry-run output, checked
  against the full `GOVERNABLE_FOR_REGULATED` allowlist. Note 5 of 8 participants
  chose the regulated posture, so real users exercised that path more than our dry
  run did — those live runs weren't individually audited, and the 100% is scoped to
  the two recorded profiles.
- All 8 participants are professional contacts of the team — convenience sampling,
  which plausibly inflates trust scores. Disclosed in Known-Limitations.
- Card P.11 (real-user testing) is **complete** as of 2026-07-28: 8 participants,
  all with real `survey_submitted` telemetry.

## How to verify this card is done

- [ ] Captions attached to every stage of the diagram on slide 5.
- [ ] Slide 6's numbers **copy-pasted** from the P.14 file, not retyped.
- [ ] Credible intervals present on the slide, not just in this doc.
- [ ] The trust-score miss is visible on the slide, not hidden in speaker notes.
- [ ] Gabi has confirmed the telemetry dataset is final (open item above).
