# Known Limitations & Roadmap (v1)

*Card P.16 deliverable. Every row is a limitation we already knew about from
building the thing — not a list discovered at the last minute. Each is written as
**what it is → why it exists → what would fix it**, because the judgement is the
point, not the confession.*

**Date:** 2026-07-27 · **Owner:** Joint (Ash + Gabi) · **Applies to:** the
`Ash3-update` build submitted for the capstone.

A plain-language version of this is **visible in the product itself** — the
"Known limitations at this stage" panel and the "About this data — bias & dataset
skew" expander in the *How it works* tab. This document is the fuller version.

---

## Product & data limitations

| Limitation | Why it exists | Roadmap fix |
|---|---|---|
| **Pricing is illustrative and manually curated, not live** | A hand-built table of 41 tools (Card 2.3). Vendor pricing changes constantly and there is no free, uniform pricing API across these vendors. | Month 2: scheduled periodic sync against vendor pricing pages (Icebox B.3, build guide 30). Until then every price carries a "verify on the vendor's page" disclaimer in-app. |
| **Compliance filtering is a directional shortlist, not certification** | The "regulated" posture filters to tools we classified as governable (Card 2.5). No governance authority backs that classification, and we hold no certification. | Would need legal/compliance review — deliberately out of scope for a 2-person capstone. Stated explicitly in-app so no user can mistake it for a sign-off. |
| **The case library skews toward enterprise cloud & productivity AI** | It reflects *real-world adoption frequency* in the source library: the top 5 tools (Azure, Gemini, Azure OpenAI, Google Cloud, AWS) are ~45% of all tool mentions. | Disclosed rather than "corrected" — correcting it would mean inventing evidence. See `docs/model-card.md`. Could diversify sources post-capstone. |
| **Industry coverage is uneven** | Cases span 24 industries, but Technology, Financial Services and Healthcare alone are ~40% of the 3,023 rows. Queries in thin industries have less evidence behind them. | More source libraries; or surface the per-query evidence count so users can judge thinness themselves (partly done — the matched-case chip and "Seen in N/M cases" bars). |
| **Smaller/newer vendors are systematically under-recommended** | Ranking is frequency-based (`collections.Counter` over matched cases — verified, no manual weighting). A well-suited niche tool that few public case studies mention will rank low. | Inherent to an evidence-based approach; disclosed in the model card's fairness note. A future version could add a "challenger tools" section sourced differently. |
| **Tool-name coverage is 88.7%, not 100%** | 2,682 of 3,023 rows resolve to a canonical tool via the alias map; ~11% (and 257 unmatched raw tool strings) don't. | Tracked openly in `data/unmatched_tools.log`; the alias map absorbs more over time. |
| **No organisation-size join to the case data** | The source dataset has no company-size field. "Organisation Size" is a separate, user-stated input used **only** for the illustrative cost estimate — never to match cases. | Would require a different or joined dataset. Property of the source data, not a maturity gap. |
| **Seat/usage cost assumptions are population-level, not per-company** | Seat counts are grounded in Stack Overflow Developer Survey bands, not a headcount lookup for the user's actual org. | A workflow-scoped refinement is already specified (Icebox B.7, proposal doc 31). |
| **Seat counts model the adopting team, not the organisation** | Someone speccing an AI stack is buying for a team, not the whole company, so seats are capped at 25 (`SEAT_CEILING`) for every band above startup. This is deliberate — but it means the org-size band you pick barely moves the seat-priced side of the forecast (€750/mo for M365 Copilot at SMB, mid-market *and* enterprise alike). The survey figures ground the **adoption rate**, not the headcount; the headcounts are our judgement. | Per-workflow headcount-share table (Icebox B.7) would let seats scale with the actual scope of the request instead of a flat ceiling. |
| **Token-volume scaling is the least-grounded number in the product** | Token spend isn't per person, so unlike seats it is not capped — larger orgs push more work through the same endpoint (bigger corpora, longer context, batch jobs). That justifies the *direction* of the scaling but not its *size*: the assumption spans 500× from solo to enterprise (€8.75 → €4,375/mo on a GPT-4o-class API) and nothing in our evidence fixes the multiplier at 500× rather than 50×. Because the primary-API figure is usually token-priced, this is also the most prominent number on the Cost tab. | Needs real usage telemetry from deployed teams — impossible pre-launch. Until then it stays labelled illustrative, and the in-product disclaimer applies most strongly here. |
| **The LLM writes the summary paragraph only** | By design: retrieval, filtering, ranking and costing are deterministic code; the model never invents tools or prices. This is a *strength*, but it means the summary's prose quality varies run to run. | Prompt is pinned at temperature 0 with an eval set (Card 2.6). Ongoing prompt tuning post-capstone. |
| **Session-only persistence — nothing is stored** | No accounts, no server-side storage, by deliberate data-minimisation choice (Card P.4). A hard refresh clears saved blueprints. | Honest trade-off, not a bug: users export JSON to keep their work. Accounts would mean holding personal data we chose not to hold. |

| **Relevance cutoff is a single global threshold** | Retrieval drops chunks past `RELEVANCE_THRESHOLD` (0.52). One global number can't perfectly separate every absurd query from every real one: in the full 432-pair sweep the nonsense floor (0.476) sits *below* the genuine ceiling (0.568), so the two distributions overlap and 1 of 8 nonsense controls still returned chunks. No single cutoff can fix that. | Per-industry or adaptive thresholds; or surface the distance to the user. Re-derive with `tests/distancecheck.py` if the embedding model or distance metric changes — **and if free text is ever added to the UI (Gabi's condition), re-run the nonsense-control sweep before shipping it**, since that's the first time an arbitrary irrelevant query becomes reachable. |
| **47% of selectable input combinations have no evidence behind them** | The two dropdowns allow 432 workflow × industry combinations, but the corpus only populates 227 of them — **205 pairs have zero real cases** (e.g. there is no "Procurement in Education" deployment in the library at all). The lists are each derived from real corpus values independently, so every *value* is real while many *pairings* are empty. Retrieval is semantic, so those queries still return the nearest cases from adjacent industries. Verified by full sweep, 2026-07-27. | Now **disclosed in the product**: the banner distinguishes real matches from nearest-comparable ones instead of claiming "N real X Y deployments matched" (which was false for these 205). Proper fix is to disable or flag unpopulated pairs in the dropdowns before the user submits — deferred, tracked for the next iteration. |

## Validation limitations

| Limitation | Why it exists | Roadmap fix |
|---|---|---|
| **Small-sample validation (5 survey responses / 14 sessions)** | Realistic for a 2-person, 4-week team. | Larger N post-capstone. Rates are reported **with 90% credible intervals** (Card P.14: net value 80%, CI 42–94%; export rate 50%, CI 30–70%), and we make **no comparative claim** ("A beat B") because that needs a properly powered study with a control group. |
| **Telemetry has no user identifier, so "sessions" ≠ distinct people** | Deliberate privacy choice — one person can submit the form several times in a sitting. | The 5 survey responses are the best available proxy for distinct testers. Stated in the P.14 write-up rather than glossed. |
| **Trust score missed its target** | Median 3/5 against a ≥4/5 target. | Stated plainly, not reworded to sound like a pass. Feeds the next iteration's priorities. |
| **Compliance pass-rate evidence is drawn from the recorded P.9 run** | `scripts/compliance_check.py` needs the full ML/LLM stack to execute live; the 2/2 result is sourced from the already-committed P.9 dry-run output. | Re-runnable any time on a machine with the stack: `python3 scripts/compliance_check.py`. |

## Deliberately deferred features (Icebox — cut at the Card P.15 freeze)

| Deferred item | Why it was cut | Roadmap position |
|---|---|---|
| **B.1 — Plain-language cost export (board one-pager)** | Could-Have; unfinished when the freeze landed. | First candidate for the next iteration. |
| **B.3 — Periodic pricing sync** | Needs a scraping/monitoring layer — too large for the remaining time (guide 30). | Directly fixes the "pricing is illustrative" limitation above. |
| **B.4 — Mainstream-validation overlay** | Data recovered (`technology_landscape.csv`) but the feature was gated out on feasibility (guide 29). | Would add a "how mainstream is this choice" signal. |
| **B.7 — Seat-fraction cost scoping** | Specified in proposal doc 31; not built. | Fixes the population-level seat assumption above. |
| ~~**B.8 — PDF blueprint export**~~ | **Shipped** 2026-07-27 (build guide 34) — the last pre-freeze addition. Not a limitation any more. | Done: available from the Export tab's **Download** popover alongside the `.md`. |
| **Mobile / responsive polish** | Only ever tested on desktop; Streamlit gives limited responsive control. | Tracked as its own QA card — needs a real device pass before any public release. |

## What we are *not* claiming

Stated for the record, because over-claiming was a real flaw in our first
prototype and is now a standing rule:

- No SOC 2, ISO 27001, HIPAA/GDPR compliance-as-a-service, or any certification.
- No testimonials, press mentions, user counts, or reviews — there are none, and
  none appear anywhere in the product or the deck.
- No claim that AASA's recommendation is *optimal* — only that it is what
  comparable organisations, in the evidence we hold, actually deployed.
- No claim of statistical significance from our tester sample.
