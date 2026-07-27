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

### Week 2 Ethics Checkpoint — Data Minimisation (Card P.4)
**Date:** 2026-07-17  **Owner:** Person B (Ash)

- [x] **Two free-text fields now exist — Week 1's "no `st.text_input` anywhere" no longer holds.** `app/intake.py` gained an optional "Project name" input (B.5, `max_chars=60`), and `app/saved_blueprints.py` a "Name" input for a saved blueprint (B.6). Both are optional cosmetic labels. A user could type PII (their name, company) into them, but: they're never required; never sent to the LLM (`generate_summary()` doesn't receive them); never written to telemetry (verified next item); and only ever surface back to the same user — in their own on-screen blueprint, downloaded export, or downloaded saved-blueprint JSON. The free text never leaves the user's machine and never reaches a model. Suggested mitigation to consider: add help text — "no need to enter personal or company-identifying info."
- [x] **Telemetry re-audited against the now-built `app/analytics/tracker.py`** (Week 1 flagged this as a design-time commitment because the file didn't exist yet — that caveat is now resolved). All 8 `log_event()` call sites pass only event names + numeric/enum values, no free text: `form_start` (no fields), `results_shown` (`elapsed_seconds` float), `llm_summary_generated` (duration + token counts), `export_clicked`, `onepager_downloaded`, `scaffold_downloaded`, `blueprint_saved` (all no fields), `survey_submitted` (`trust_score` int 1–5, `net_value` "Yes"/"No"). **Critically: neither the project name nor the saved-blueprint name is passed to any `log_event` call** — free text cannot reach `data/telemetry.log`.
- [x] **New client-side data artifacts (B.6) stay on the user's own machine.** Saved blueprints live in `st.session_state` for one browser session only. "Export all (.json)" downloads that data to a file the user holds; "Import (.json)" reads a user-supplied file. The exported JSON contains the result dict (including any free-text project name), but **nothing is stored server-side and it's tied to no account.** The board one-pager (.md) and .env scaffold are likewise generated in-browser and downloaded — and the scaffold deliberately leaves every API-key value blank, so it never captures secrets.
- [x] **Still no account, login, or persistent identifier.** Re-scanned `app/` — B.5/B.6 added no `user_id`/login/cookie/email pattern. The only state remains in-memory `st.session_state`, not tied to an identity or persisted across visits.
- [x] **Still a local JSON-lines telemetry file (`data/telemetry.log`) — no third-party analytics service.** No Mixpanel/Segment/Amplitude/PostHog/Sentry added; telemetry remains a local file by design.
- [ ] **One third-party call does remain: the Google Fonts `@import`** (`@import url('https://fonts.googleapis.com/...')` in `app/intake.py`). This makes each user's browser request fonts from Google, which exposes the user's IP address to Google (a standard but GDPR-relevant detail). It carries no app data and no user input — it's a font request, not a data pipeline. If strict data-minimisation is wanted, self-hosting the two font files removes the third-party call entirely. Left unchecked because it's a genuine open decision, not a confirmed clean item.

**Confirmed by:** Ash — audited directly against the actual codebase (`app/intake.py`, `app/saved_blueprints.py`, `app/analytics/tracker.py`, all `log_event` call sites, `app/logic/prompt.py`), not filled in from memory. Since Person A (Gabi) built the retrieval/telemetry side, she should sanity-check items 2 and 3 against what she implemented — especially that no free text ever gets appended to the telemetry log.

## Week 3: Stakeholder Consultation & Accessibility — *Owner: Student B*
**Focus:** Inclusion
- **Action:** Run the 5–8 real-user test sessions (see Proposal & Scope v2 — moved up from a Week-3-only sprint to avoid collision with development). Specifically include a non-technical founder and a non-native English speaker to test clarity and jargon.
- **Milestone:** Feedback logged and any confusing wording patched before the pitch.

### Week 3 Ethics Checkpoint — Data Minimisation (Card P.4)
**Date:** 2026-07-24  **Owner:** Person B (Ash)

- [x] **Week 2's one open item is now closed — no third-party font request.** Week 2 left the Google Fonts `@import` unchecked (it made each user's browser call `fonts.googleapis.com`, exposing their IP to Google). Both fonts are now **self-hosted**: `static/fonts/` holds the Inter and Roboto Mono `.woff2` files and `app/intake.py`'s CSS serves them from the app itself via `@font-face`. Re-scanned `app/` and `.streamlit/` — no `googleapis`/`gstatic`/`@import` calls remain (the only `googleapis` hit is a code comment in `filter.py`, not a request). So a user's browser no longer contacts Google to render the page. The Material icons on the results tabs are bundled with Streamlit and served locally too — not a third-party call.
- [x] **The Week-3 UI overhaul added only in-memory layout state — no new data is collected.** The sidebar collapse/expand and form-reset work introduced these `st.session_state` keys: `sidebar_open`, `_user_collapsed`, `build_open`, `form_nonce`, `_blueprint_just_saved`. All are booleans/integers that control what's shown on screen. None is a user identifier, none is written to telemetry, none is sent anywhere, and none survives a page refresh.
- [x] **Form fields are now keyed widgets, but the PII picture is unchanged.** To make the new "Clear resets the form" behaviour work, the five constraints plus the optional Project name / Vendors-to-exclude now have widget keys (`in_*_<nonce>`). Still: only the five validated constraints (workflow, industry, size, privacy, budget) flow into the pipeline; the optional **Project name free text is echoed only to the user's own on-screen/exported blueprint and is NOT passed to the LLM** (verified — `generate_summary()` in `app/pipeline.py` receives tool labels, cost, cases and privacy only, never `project_name`) **nor to telemetry.** Clear now wipes these fields entirely.
- [x] **Telemetry re-audited — same shape as Week 2, still free-text-free.** All `log_event()` call sites pass only event names + numeric/enum values: `form_start`, `results_shown` (elapsed_seconds float), `llm_summary_generated` (duration + token counts), `export_clicked`, `onepager_downloaded`, `scaffold_downloaded`, `blueprint_saved`, `survey_submitted` (trust_score int, net_value "Yes"/"No"). The UI-v2 work added **no** new telemetry events and passes **no** free text. Still a local JSON-lines file (`data/telemetry.log`), no third-party analytics.
- [x] **New Week-3 analysis scripts (Card P.14) read data, they don't collect it.** `scripts/telemetry_funnel.py` and `scripts/credible_interval.py` read the existing local `data/telemetry.log` to compute aggregate metrics; `scripts/compliance_check.py` re-runs the existing pipeline. They run on our machine as dev/reporting tools, not in the user flow, and introduce no new data collection or network call of their own (`credible_interval.py` just uses scipy locally).
- [ ] **New outbound *links* in the results — user-initiated, no app data sent, but worth noting.** Block A now hyperlinks each recommended tool to its official vendor homepage (41 URLs in `pricing.py`), alongside the existing case "Source" links. These open in a new tab (`rel="noopener"`). Clicking navigates the user's browser to a third-party site — standard web behaviour — and transmits none of the user's inputs or app data; nothing leaves the page unless the user chooses to click. Left unchecked only because a click does send a normal `Referer` header to the vendor (revealing the user came from the app); a `referrerpolicy="no-referrer"` on the links would close even that if we want to be strict.
- [x] **Still no account, login, or persistent identifier, and no new outbound HTTP in the app.** Re-scanned `app/` — no `requests`/`urllib`/`httpx`, no `user_id`/login/cookie/email pattern. State remains in-memory `st.session_state`, tied to no identity. The only external call at runtime is the unchanged Card 2.6 LLM summary (query = workflow + industry, no free text).

**Confirmed by:** Ash — audited directly against the current `Ash3-update` code (`app/intake.py`, `app/dashboard.py`, `app/saved_blueprints.py`, `app/analytics/tracker.py` and every `log_event` call site, `app/pipeline.py`, `static/fonts/`, the P.14 scripts), not from memory. Since Person A (Gabi) owns the retrieval/telemetry side and built the P.14 scripts, she should sanity-check items 4 and 5 — especially that no free text is ever appended to the telemetry log and that her scripts only read it locally.

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
