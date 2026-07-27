# P.17 — 10-Slide Pitch Outline (v1)

*Card P.17. An outline to agree **before** any slide gets designed. Every slide
lists the one thing it must land, the real asset it draws on, and what to say —
so nothing on stage depends on a number we haven't actually computed.*

**Owner:** Person B (Ash) · **Date:** 2026-07-27 · **Target:** ~10 min + Q&A

**Drafted by Claude from our real assets — Ash to reshape the narrative.** The
facts are checked; the story arc is a judgement call and should sound like you.

---

## The spine (one line)

> Small teams pick their AI stack from vendor marketing and forum threads. AASA
> answers the same question from **3,023 real deployments** — in about two
> minutes, with every recommendation traceable to a real source.

## Slide-by-slide

| # | Slide | Must land | Source asset |
|---|---|---|---|
| 1 | **Title + one-liner** | What this is, in one sentence, plus the honest framing: a 4-week student prototype. | Hero copy from the app |
| 2 | **The problem** | A resource-constrained founder choosing an AI stack has no evidence base — just vendor claims and opinions. Cost surprises and compliance dead-ends follow. | Personas / user research (`03b-User-Research-v2.md`) |
| 3 | **The user + the job** | Who we built for and the job-to-be-done: "tell me what teams like mine actually shipped, and what it costs." | Proposal & Scope v2 |
| 4 | **The product — live demo or screenshots** | Five inputs → three-block blueprint. Keep it concrete: one real query, end to end. | The `Ash3-update` build (see demo script below) |
| 5 | **How it works (architecture)** | The pipeline is deterministic where it matters; the LLM only writes prose. | Mermaid diagram + P.18 captions |
| 6 | **Real test results** | We tested with real people and report the numbers honestly, intervals included. | Card P.14 table (see P.18 doc) |
| 7 | **Evidence & traceability** | Every tool links to the real cases that used it — click one. This is the credibility slide. | Block A "why:" lines + Block C source links |
| 8 | **Ethics & data minimisation** | No accounts, no PII, no third-party calls, disclosed dataset bias. Deliberate choices, documented weekly. | P.4 checkpoints + `docs/model-card.md` |
| 9 | **Known limitations & roadmap** | Condensed table — what it doesn't do *yet* and what would fix it. | `PM & Ethics/Known-Limitations-v1.md` |
| 10 | **Close + ask** | What we'd build next and what we learned as a 2-person team in 4 weeks. | Roadmap v2 |

## Demo script for slide 4 (60–75 seconds, rehearse it)

1. Open with the sidebar form visible. Pick a query with a **healthy** match count
   — e.g. *Customer Service · Technology · Startup · Standard · €800*. (Avoid a
   thin combination on stage.)
2. Click **Generate my blueprint** — say "about two minutes of work, not two days
   of forum reading" while it runs.
3. Land on **Stack**: point at one tool's `why:` line and its evidence bar
   ("seen in 3 of 13 matched cases") — *this is the whole pitch in one line.*
4. **Cost** tab: name the figure, then immediately say "illustrative — and the app
   says so."
5. **Cases** tab: click one real source link. Let the audience see a real vendor
   case study open. This is the moment that separates us from a demo that could
   be faked.
6. **Export** tab: show the copy block / download. "They leave with something they
   can put in front of their board."

**Backup plan:** if the live app fails on stage, have the screenshots and one
downloaded blueprint export open in another window. Say so calmly and continue —
a prepared fallback reads as competence, fumbling does not.

## Q&A prep — the five questions we should expect

| Likely question | Honest answer |
|---|---|
| "Isn't 8 testers far too small to claim anything?" | Yes — that's why we report credible intervals and make **no** comparative claim. 100% net value sounds absolute; its interval is 72–99%, and one changed answer moves the rate 12.5 points. Point at the CI column. |
| **"All four targets met — isn't that a bit convenient?"** | Fair challenge, and the honest answer is that we can't take credit for it cleanly. The earlier round scored trust 3/5 and missed. Between rounds *both* the build and the participants changed, so we don't claim our fixes caused the improvement — that would need the same people testing both builds. The earlier miss is still in the P.14 write-up. |
| **"Who were your testers?"** | 8 practitioners at 7 real companies — SumUp, BMG, CoachHub, Delivery Hero, AUTODOC, Plan A, Ordio — 5 of them non-native English speakers, 5 choosing the regulated posture. All recruited through our own networks, which is convenience sampling and plausibly inflates trust. Disclosed in Known-Limitations. |
| "How do you know the LLM isn't making the tools up?" | It can't — retrieval, filtering, ranking and costing are deterministic Python; the model receives an already-final list and only writes the summary paragraph. Slide 5. |
| "Is the compliance filter safe to rely on?" | No, and we never claim it is — it's a directional shortlist, labelled as such in-product. |
| "Why is it always the big cloud vendors?" | Because that's what the real evidence contains. We disclose the skew (~45% of mentions from 5 tools) rather than hide it — model card, slide 8. |

## Design rules for whoever builds the deck

- Numbers on slides must be **copy-pasted from the P.14 output**, never retyped
  from memory (Card P.21 checks this).
- Keep credible intervals visible — "100% (8/8), 90% CI 72–99%" beats a bare "100%",
  and matters more now that every target is met: a bare 100% invites disbelief.
- No fabricated trust signals of any kind (Card P.19's standing check).
- Reuse the product's own visual language (dark theme, indigo accent, mono
  labels) so the deck and the demo feel like one thing.

## How to verify this card is done

- [ ] Both team members have read this outline and agree the arc before design starts.
- [ ] Every slide has a named source asset that actually exists in the repo.
- [ ] The demo query is chosen and rehearsed, with a screenshot fallback ready.
