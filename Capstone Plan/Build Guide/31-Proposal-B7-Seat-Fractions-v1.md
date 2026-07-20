# Proposal 31 — B.7 Workflow Seat-Fraction Table (FOR DISCUSSION — nothing implemented)

*Companion to Build Guide 28 (Icebox card `stackpunk #48`, board label **Won't Have**). This document is a **proposal for Ash and Gabi to argue with**, per the team's decision — no code has been changed. If the numbers below survive discussion, guide 28 has the implementation steps; the fraction table gets pasted into `app/logic/cost.py` with the agreed values, and this doc becomes the audit trail for where they came from. Same convention as Update D's seat-multiplier sign-off.*

---

## What's being decided

Replace `SEAT_CEILING = 25` (the Update D stopgap: every seat-priced tool is costed at `min(org_seats, 25)` seats regardless of workflow) with **seats = org headcount × the fraction of a company that works in the target workflow**, floored at 3.

Formula under proposal: `seats = max(3, round(ASSUMED_SEATS[org_size] × fraction[workflow]))`

## The proposed table

`ASSUMED_SEATS` today (survey-grounded, Update C): solo 3 · startup 16 · smb 123 · mid 481 · ent 2,377.

| Workflow | Fraction | Implied seats (smb 123 / mid 481 / ent 2,377) | Rationale |
|---|---|---|---|
| Customer Service | 0.12 | 15 / 58 / 285 | Support-heavy orgs run 10–15% of headcount in support; benchmark ratios for B2C SaaS cluster around 1 support agent per 8–12 employees. Our single most-queried workflow, so this number matters most. |
| Sales | 0.10 | 12 / 48 / 238 | Sales headcount commonly 8–12% outside sales-led enterprises. |
| R&D & Engineering | 0.15 | 18 / 72 / 357 | Widest plausible range of any row (5% in industrials, 40%+ in software startups). 0.15 is a cross-industry compromise — flagged as open question #2. |
| Operations & Supply Chain | 0.10 | 12 / 48 / 238 | Highly industry-dependent (manufacturing ≫ SaaS); 0.10 as a neutral midpoint. |
| IT & Platform | 0.06 | 7 / 29 / 143 | Classic IT-staff ratio benchmarks run 4–7% of employees. |
| Marketing | 0.05 | 6 / 24 / 119 | Marketing teams typically 4–6% of headcount. |
| Finance | 0.05 | 6 / 24 / 119 | Finance/accounting commonly ~5% and shrinking with automation. |
| Data & Analytics | 0.04 | 5 / 19 / 95 | Dedicated data teams rarely exceed 5% outside data-product companies. |
| Content & Creative | 0.04 | 5 / 19 / 95 | Creative teams small outside media orgs (where the Industry input, not this table, should carry the signal). |
| CX & Personalization | 0.04 | 5 / 19 / 95 | Overlaps Customer Service; kept deliberately smaller since it's the specialist slice, not frontline support. |
| HR | 0.03 | 4 / 14 / 71 | HR-to-employee benchmarks: 1.0–2.5 HR staff per 100 employees; 0.03 is the generous end (HR tooling often licenses beyond the HR team itself). |
| Process Automation & RPA | 0.03 | 4 / 14 / 71 | Automation CoEs are small specialist teams. |
| Training & L&D | 0.02 | 3 / 10 / 48 | L&D staffing is a sliver of HR — but note L&D *platforms* often license company-wide; open question #3. |
| Legal & Compliance | 0.02 | 3 / 10 / 48 | Legal teams are tiny (<1–2%) in all but law-adjacent firms. |
| Risk & Compliance | 0.02 | 3 / 10 / 48 | As Legal, except in Financial Services — see open question #4. |
| Security & Cyber | 0.02 | 3 / 10 / 48 | Security staffing benchmarks: 1–3% of IT, so well under 2% of total; rounded up for tool-licensing breadth. |
| Procurement | 0.02 | 3 / 10 / 48 | Procurement teams are small everywhere. |
| Facilities & EHS | 0.02 | 3 / 10 / 48 | Smallest white-collar function in the taxonomy. |
| **Any workflow** | **0.25** | 31 / 120 / 594 | No scoping signal — a broad-adoption assumption. Deliberately NOT 1.0: "any workflow" means "we haven't picked yet," not "every employee gets a seat." Open question #1. |

**Floor:** 3 seats (below that, a seat-licence discussion is meaningless). **No ceiling** — that's the point of retiring the stopgap.

## Sanity check against the bug that started all this

The Update D scenario (Customer Service / mid / regulated, M365 Copilot at €30/seat):

| Model | Seats | Assistant cost/mo |
|---|---|---|
| Pre-Update-D (company-wide) | 2,245* | €67,340 (the reported bug) |
| Update D stopgap (`min(seats, 25)`) | 25 | €750 |
| **This proposal** (481 × 0.12) | **58** | **€1,740** |

*\*pre-Update-D used a different seat base; figure as reported in the original bug.*

The proposal lands between the two extremes — more honest than the flat 25 (a mid-market company doesn't run customer service with 25 people), far saner than company-wide. Note it **more than doubles** the assistant line vs. today for this common query — demo screenshots and any hardcoded few-shot figures in `prompt.py` will shift (guide 28's checklist covers this).

## Sources & honesty statement

The fractions are **team judgment anchored on commonly-cited staffing-ratio ranges** (support-agent ratios, IT-staff-per-employee, HR-per-100-employees), not on a single citable dataset — there is no public "% of headcount by function × industry" table that maps onto our 18-workflow taxonomy. That's the same epistemic tier as Update D's `SEAT_CEILING`, just finer-grained and per-workflow. The disclaimer string in `cost.py` must keep saying "illustrative" either way. If anyone wants to harden a specific row later, the survey's QID16/QID25 crosstab could ground 2–3 of them, but not most.

## Open questions for the meeting (argue with these)

1. **"Any workflow" = 0.25** — too high? Too low? It's the single most consequential row for casual demo users who don't pick a workflow.
2. **R&D at 0.15** — for a Technology-industry query this understates (software firms run 30–40% engineering); do we want a per-(workflow × industry) exception or accept the error?
3. **Seat-fraction vs. licence-breadth mismatch** — some tools license beyond their "home" team (L&D platforms, M365 Copilot itself). Do we accept the fraction as a lower-bound proxy, or bump specific rows?
4. **Risk & Compliance in Financial Services** — 0.02 badly understates compliance headcount at banks. Same question as #2: exception or accepted error?
5. **Should this ship at all this sprint?** The card says Won't Have; the tutors asked what *can* land. Changing that label is a team decision — this table existing doesn't oblige anyone.

## Sign-off (same convention as the Update D seat-multiplier)

- [ ] Ash — agrees with table as-is / with amendments noted below
- [ ] Gabi — agrees with table as-is / with amendments noted below
- Amendments agreed: *(fill in)*
- Decision on question 5 (ship this sprint?): *(fill in)*

Once both boxes tick, implement per **Build Guide 28** and update its checklist + this doc's status line.
