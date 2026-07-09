# Ethical Action Plan & Timeline (v2)
*Supersedes the original. Fixes: it assigned 3 distinct role-titles (Data Security & Privacy Lead, AI Ethics Tool Specialist, Stakeholder Facilitator) as if to 3 separate people, contradicting our 2-person team. Roles are consolidated below. Actions are re-scoped to the AI-stack-only MVP.*

## Week 1: Data Minimisation & Baseline Audit — *Owner: Student A*
**Focus:** Privacy & Security
- **Action:** No accounts, no PII fields, no stored user inputs beyond the current session. The intake form only ever collects the 5 anonymous constraints (workflow, industry, org size, privacy posture, budget).
- **Milestone:** Baseline data policy drafted and reflected in-app (a one-line "we don't store your inputs" note).

### Week 1 Ethics Checkpoint — Data Minimisation (Card P.4)
**Date:** 2026-07-09  **Owner:** Person A (Student A / Gabi)

- [x] **No PII collected in any of the 5 intake fields.** All 5 are `st.selectbox`/`st.radio`/`st.number_input` widgets — `workflow`, `industry`, `org_size`, `privacy` (all closed dropdown/radio option lists) and `budget` (a plain number). There is no `st.text_input` or other free-text widget anywhere in `app/intake.py`. None of the 5 values, individually or combined, identify a specific person.
- [x] **Telemetry log (`data/telemetry.log`) contains only event names, timestamps, and numeric/enum values — no free text.** Verified against the Card 3.3 spec (`14-Build-Guide-Epic3-Blueprint-UI-v1.md`): `log_event()` writes `{"event": <fixed name>, "timestamp": <float>, **fields}`, and every call site passes only numbers or closed-set strings — `elapsed_seconds`, `duration_seconds`, `prompt_tokens`/`completion_tokens`/`tokens_per_second`, `trust_score` (1–5 int), `net_value` ("Yes"/"No"). **Caveat:** `app/analytics/tracker.py` doesn't exist in the repo yet — Card 3.3 hasn't been built — so this is a design-time commitment against the spec, not a runtime audit of running code. Re-verify this line once Card 3.3 actually lands, in case the real implementation drifts from the spec (e.g. someone adds a free-text "any other feedback?" box to the trust survey later).
- [x] **No account creation, login, or persistent user identifier.** Confirmed by scanning `app/` for `login`, `password`, `email`, `cookie`, `user_id`, and any persistent-identifier pattern — no matches. The only state is Streamlit's own `st.session_state`, which lives in memory for one browser session and isn't tied to an identity or persisted across visits.
- [x] **No third-party analytics service receiving user data.** `requirements.txt` lists only `pandas`, `streamlit`, `chromadb`, `sentence-transformers` — no Mixpanel/Segment/Amplitude/PostHog/Sentry/etc. Confirmed by scanning `app/` and `scripts/` for those names and for generic analytics-SDK patterns — no matches. Telemetry is a local JSON-lines file by design (Card 3.3's own stated reasoning), not a third-party pipeline.

**Confirmed by:** Ash — audited directly against the actual codebase (`app/intake.py`, `app/validators.py`, `requirements.txt`, and the Card 3.3/3.4 specs in `14-Build-Guide-Epic3-Blueprint-UI-v1.md`), not filled in from memory. Since Person A (Gabi) is this card's assigned owner, she should sanity-check this against her own knowledge of what she's built, especially the Card 3.3 caveat above once that card is actually implemented.

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
