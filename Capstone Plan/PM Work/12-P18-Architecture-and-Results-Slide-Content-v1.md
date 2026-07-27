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

**Source:** `Capstone Plan/Build Guide/P14-Validation-Metrics-Final-v1.md`,
computed by `scripts/telemetry_funnel.py` + `scripts/credible_interval.py` from
`data/telemetry.log`. **Do not retype these — copy them.**

| Metric | Target | Actual | 90% credible interval | Met? |
|---|---|---|---|---|
| Net value ("saved me research time") | ≥70% | **80%** (4/5) | 42%–94% | Yes (point estimate) |
| Blueprint export rate | ≥40% | **50%** (7/14) | 30%–70% | Yes (point estimate) |
| Compliance-rule pass rate | 100% | **100%** (2/2 regulated profiles) | — (deterministic) | Yes |
| Trust score (median) | ≥4/5 | **3/5** | — (ordinal) | **No** |
| Avg. LLM latency | — | **1.51s** (14 calls) | min 0.82 / max 3.29 | — |
| Sample size | 5–8 testers | 14 sessions / 5 survey responses | not powered for comparative claims | — |

**Funnel (read as a sequence, not three independent stats):**

> **14** viewed a blueprint → **7** exported it (50% of viewers) → **5** answered
> the survey, **4** of whom said it saved them research time (80% of respondents).

### The three things this slide must communicate

1. **We tested with real people and computed the numbers from logged behaviour**,
   not impressions.
2. **Two of four targets met, one clearly missed** — the trust score is stated as
   a miss, not massaged. That honesty is the credibility play.
3. **The intervals are wide and we say so.** At n=5, one person changing their
   answer swings the rate ~20 points. We report Beta(1,1) 90% credible intervals
   and make **no** comparative claim.

### Visual guidance

Keep it a clean table — don't over-design. If you want one graphic, a simple
horizontal bar per rate metric with a vertical target line works, but the
interval must stay visible (a whisker or the range printed next to the bar).
**Never show a bare percentage without its interval on this slide.**

### Honesty footnotes for the slide (small text, but present)

- "14 sessions" ≠ 14 distinct people — telemetry has no user identifier by
  design (privacy choice), so someone can submit more than once. The 5 survey
  responses are the best proxy for distinct testers.
- Compliance pass rate is drawn from the recorded P.9 dry-run output, checked
  against the full `GOVERNABLE_FOR_REGULATED` allowlist.
- Card P.11 (real-user testing) was still in progress when these were compiled —
  **Gabi to confirm this is the final dataset before the deck is locked.**

## How to verify this card is done

- [ ] Captions attached to every stage of the diagram on slide 5.
- [ ] Slide 6's numbers **copy-pasted** from the P.14 file, not retyped.
- [ ] Credible intervals present on the slide, not just in this doc.
- [ ] The trust-score miss is visible on the slide, not hidden in speaker notes.
- [ ] Gabi has confirmed the telemetry dataset is final (open item above).
