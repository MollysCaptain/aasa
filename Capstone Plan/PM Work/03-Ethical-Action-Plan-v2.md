# Ethical Action Plan & Timeline (v2)
*Supersedes the original. Fixes: it assigned 3 distinct role-titles (Data Security & Privacy Lead, AI Ethics Tool Specialist, Stakeholder Facilitator) as if to 3 separate people, contradicting our 2-person team. Roles are consolidated below. Actions are re-scoped to the AI-stack-only MVP.*

## Week 1: Data Minimisation & Baseline Audit — *Owner: Student A*
**Focus:** Privacy & Security
- **Action:** No accounts, no PII fields, no stored user inputs beyond the current session. The intake form only ever collects the 5 anonymous constraints (workflow, industry, org size, privacy posture, budget).
- **Milestone:** Baseline data policy drafted and reflected in-app (a one-line "we don't store your inputs" note).

## Week 2: Bias Mitigation & Model Card — *Owner: Student A*
**Focus:** Technical objectivity
- **Action:** Audit that tool ranking is driven purely by real-case frequency, not by our own preferences. Draft a short model card that documents the dataset's known skew toward enterprise productivity AI (Gemini/Workspace, Copilot) rather than hiding it.
- **Milestone:** Model card completed; ranking logic verified against the audit.

## Week 3: Stakeholder Consultation & Accessibility — *Owner: Student B*
**Focus:** Inclusion
- **Action:** Run the 5–8 real-user test sessions (see Proposal & Scope v2 — moved up from a Week-3-only sprint to avoid collision with development). Specifically include a non-technical founder and a non-native English speaker to test clarity and jargon.
- **Milestone:** Feedback logged and any confusing wording patched before the pitch.

## Week 4: Final Ethical Review & Sign-off — *Owner: both*
**Focus:** Governance
- **Action:** Walk the final build against a short Responsible AI checklist, with one item added directly from feedback: **confirm no fabricated trust signals (testimonials, certifications, reviews, press mentions) exist anywhere in the prototype.** This was a real issue in our first build and is now a standing check.
- **Milestone:** Final sign-off; pitch presented.

## Roles — corrected
Because this is a 2-person team, the three roles from v1 are consolidated:
- **Student A** absorbs Data Security & Privacy Lead + AI Ethics Tool Specialist (data policy, bias audits, model card).
- **Student B** absorbs Stakeholder Facilitator (recruiting, sessions, accessibility).
- Governance sign-off in Week 4 is shared.

## Post-Implementation & Evaluation Plan
Retained as **illustrative governance intent** beyond the capstone window, not a committed deliverable:
- **1-Month Post-Launch (Aug 2026):** review token/API usage for cost and environmental footprint; check for user reports of "sticker shock" from stale pricing.
- **6-Month Post-Launch (Jan 2027):** audit whether pricing/tool data has gone stale; survey early users on whether the tool genuinely leveled the playing field for resource-constrained founders.

## Honesty note (new)
Our compliance filter is a **shortlist, not a certification**. The product will say so explicitly in-app. We do not claim SOC 2, ISO 27001, GDPR-compliance-as-a-service, or any other certification we do not hold — this was a real gap in our first prototype build and is now treated as a standing ethical rule, not a one-time fix.
