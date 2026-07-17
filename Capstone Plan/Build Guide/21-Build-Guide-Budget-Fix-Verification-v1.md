# Build Guide — Budget Fix Verification & Follow-Ups

*Companion to Update D in `18-Build-Guide-Updates-Epic1-2-v1.md`, which has the full technical writeup (root causes, decision, implementation, unit-level verification). This doc is just the handful of steps that need a live app, a design judgment call, or repo/board access outside this session — better done by Ash directly than described secondhand.*

---

## 1. Re-test the original scenario in the live Streamlit app — DONE

**Confirmed by Ash:** re-ran the exact reported scenario in a running Streamlit session; the numbers came back very close to what the unit-level fix predicted (a low-thousands total, not tens of thousands), and the summary text disclosed the over-budget result plainly. Steps taken, for the record:

1. Pull the latest `Ash2` branch, rebuild the chroma store if you haven't already this session (`python3 scripts/rebuild_knowledge_base.py`), and start Streamlit as usual.
2. Re-enter the exact scenario that surfaced this bug: **Customer Service** workflow, **Mid-Market (201–1,000 people)** org size, **Energy & Utilities** industry, **Regulated** privacy posture, **€1,800/month** budget.
3. Confirm the Cost Forecast block now shows a combined total in the low thousands (unit tests predict ≈€4,046.88/mo: €546.88 primary API + €3,500.00 assistant, though your live ranked tools may differ slightly run to run), **not** the original €68,433.75/mo.
4. Confirm the summary paragraph now explicitly says the forecast exceeds the budget and by roughly how much, rather than describing the numbers as if nothing were wrong.
5. Optionally re-test one in-budget scenario (e.g. a smaller org size or a higher budget) to confirm the summary correctly says it fits, without over-emphasizing it.

If anything reads oddly (phrasing, tone, a number that looks off), that's a prompt-wording tweak in `app/logic/prompt.py`, not a re-do of the underlying fix.

---

## 2. Re-render the pipeline diagram image

`PM & Ethics/pipeline-diagram.mmd` now has a new `Within stated budget?` decision node after the cost-estimation step. The `.mmd` source is updated, but `PM & Ethics/Mermaid-Diagram.png` is a static export of the old version and needs re-generating from whatever tool you used originally (Mermaid Live Editor, VS Code's Mermaid preview extension, etc.) — this session's sandbox doesn't have a Mermaid renderer installed, so the image itself couldn't be regenerated here.

---

## 3. Sanity-check the `SEAT_CEILING` judgment call

`app/logic/cost.py`'s new `SEAT_CEILING = 25` (a flat cap on assumed seats, applied uniformly regardless of org-size band — see Update D for why) is a hand-picked stopgap, not derived from any dataset. Worth a quick gut-check with Gabi after step 1's live test: does 25 seats feel like a plausible size for a single-workflow team (e.g. "Customer Service") at a mid-market or enterprise org, or should it be tuned up or down? This number can be changed in one place (`app/logic/cost.py`) without touching anything else.

---

## 4. Decide on Option A (workflow-fraction table) as future scope

Update D implemented Option B (Fixed Ceiling Stopgap) as the immediate fix. Option A — scoping the seat assumption per workflow rather than a single flat ceiling — would be more accurate but needs either real data or a documented per-workflow judgment call, and wasn't attempted here. If it's worth pursuing later, it'd be a new Icebox card (similar to how 2.7/3.5 were added after the Lovable comparison) rather than a change to Update D's already-decided scope.

---

## 5. Board/checklist housekeeping

Per the usual pattern on this project: once step 1's live re-test passes, update the kanban board and the build-guide checklist yourself to reflect Update D as done, the same way past cards' completion has been tracked.
