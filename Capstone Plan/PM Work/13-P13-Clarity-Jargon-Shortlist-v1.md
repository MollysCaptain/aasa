# P.13 — Clarity & Jargon Shortlist (helper for the inclusion check)

*Card P.13 needs a **human** reading the live UI as a non-technical founder and as
a non-native English speaker. This document doesn't replace that — it front-loads
it. Below is every user-facing phrase I could find that is plausibly unclear to
one of those two personas, with a suggested plainer alternative, so the session
is spent judging rather than hunting.*

**Prepared by:** Claude (static scan of `app/*.py` strings) · **Date:** 2026-07-27
**Decision owner:** Person B (Ash), with Gabi on the data/pricing terms

## How to use this in the session

1. Open the app on `Ash3-update` and walk the full flow (empty state → generate →
   all six tabs → save → clear).
2. For each row below, decide: **keep / reword / add a tooltip**. Some jargon is
   correct to keep — a founder evaluating AI tools will meet "API" everywhere, and
   dumbing it down could patronise. Judgement, not blanket simplification.
3. Note anything I missed — especially anything *you* stumbled over reading aloud.

## Priority 1 — likely to confuse a non-technical founder

| Where | Current wording | Issue | Suggested |
|---|---|---|---|
| Block A price tags | `token-priced` / `seat-priced` / `usage-based` | Billing-model jargon. "Token" is meaningless to a non-technical reader. | Tooltip on first use: "token-priced = you pay per unit of text processed"; "seat-priced = you pay per person per month"; "usage-based = you pay for what you consume". Keep the short label, add the explanation. |
| Chips row | `REGULATED POSTURE · SENSITIVE VENDORS FILTERED` | "Posture" is security-industry vocabulary; passive voice. | "Regulated mode — consumer tools removed" |
| Banner | `DIRECTIONAL ONLY` | Consultant-speak. The *content* after it is clear, the label isn't. | "Estimates only — verify before you commit" |
| Cost block | `Primary API` / `Assistant / SaaS` | "SaaS" and the API/assistant split assume the reader knows the difference. | "Main AI service (pay per use)" / "Team subscription (pay per person)" |
| Intake label | `Data-Privacy Posture` | Same "posture" problem, and it's the field most likely to be misread. | "Data sensitivity" or "How regulated is your data?" (help text already explains it) |
| `.env scaffold` button | `.env scaffold` | Meaningless to anyone who hasn't set up a project's environment file. | "Starter config file" (keep `.env` in the popover body where it's technically accurate) |
| Export caption | "Hover the code block below and click the copy icon in the top-right corner" | Describes a UI affordance that may not be obvious on touch devices. | Fine on desktop; flag for the mobile QA card. |

## Priority 2 — non-native-English-speaker friction

| Where | Current wording | Issue | Suggested |
|---|---|---|---|
| Hero headline | "Match your constraints to what teams like yours actually shipped." | "shipped" is idiomatic tech English; "constraints" is abstract. | "…to what teams like yours actually built." |
| Block A rationale prefix | `why:` | Lower-case fragment; fine visually, but reads as incomplete. | Acceptable — but consider "Why this tool:" |
| Feedback question | "Did this save you research time you'd otherwise spend on forums/Google?" | Long, contains a contraction + conditional ("you'd otherwise"), and "forums" is culturally specific. | "Did this save you time you would have spent searching online?" |
| Known-limitations bullets | "compliance filtering is a *directional* shortlist" | Double abstraction ("directional" + "shortlist"). | "a starting shortlist, not an official approval" |
| Empty-state info | "No tools cleared the privacy filter for this combination of inputs." | "cleared the filter" is idiomatic. | "No tools matched these privacy requirements. Try a different privacy setting or a broader workflow." |
| Save caption | "Saved blueprints live in this browser session only — export the JSON to keep them." | "live in… session" + "the JSON" assume familiarity. | "Saved blueprints disappear when you close this tab. Download the file to keep them." |
| Copy confirm | "Blueprint copied ✓" | Fine — short, clear, and the tick carries meaning. | Keep. |

## Priority 3 — small consistency snags worth 2 minutes

| Where | Note |
|---|---|
| "AI-Assisted Stack Architect" (top bar) vs "AI Stack Architect" (elsewhere in docs) | Pick one and use it everywhere — the deck and README should match the app. |
| `Organisation` (UK) vs `Organization` | We use UK spelling in the UI. Keep it consistent in the deck/README too. |
| Currency is € everywhere | Correct and consistent — no action, but be ready to say "illustrative, EUR" on stage. |
| `~2 min TO BLUEPRINT` hero stat | It's a claim. Our telemetry says average time-to-results was 381.6s (~6 min) including thinking time. Either soften to "~2 min of work" or align the number — **this one is a P.19/P.21 honesty item, not just clarity.** |

## What I could not check (needs the human pass)

- Whether the **overall flow** makes sense to someone seeing it cold — order,
  what to do first, whether the empty state explains itself.
- Whether the **colour contrast** is readable for someone with low vision or
  colour-blindness (the green/orange/indigo accents on dark). Worth a contrast
  check if there's time.
- Whether **screen-reader** output is sensible — our custom HTML chips/banners use
  `unsafe_allow_html`, which can produce unlabelled elements.
- Whether anything reads as **over-claiming** when spoken aloud rather than read.

## How to verify this card is done

- [ ] Both personas' walkthroughs actually done on the live app (not just this doc).
- [ ] Every Priority 1 row has a keep/reword/tooltip decision recorded.
- [ ] The `~2 min` claim resolved (see Priority 3).
- [ ] Any agreed rewording either implemented before the freeze or Iceboxed
      explicitly.
