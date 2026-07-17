# Build Guide — Epic 3 UI Updates Verification

*Companion to Updates E/F/G in `22-Build-Guide-Updates-Epic3-v1.md`, which has the full technical writeup. This doc is just the handful of steps that need a live running app or a visual/copy judgment call — better done by Ash directly than described secondhand, same pattern as `21-Build-Guide-Budget-Fix-Verification-v1.md`.*

---

## 1. Re-test Block A's toggle and per-tool pricing live

1. Pull the latest `Ash2` branch and start Streamlit.
2. Run any query that returns a mix of pricing models in the top 5 (a Regulated/Mid-Market query in a well-covered industry, e.g. Energy & Utilities or Technology, should reliably do it based on prior tests).
3. Confirm the grey caption under each tool now shows a price, "Pay-as-you-go" for compute-billed tools, or "Free / Self-hosted" for OSS tools — not the repeated model-name text.
4. Click through all five toggle options (Recommended / Token / Seat / Compute / Free). Confirm the list actually filters, the evidence-bar percentages stay based on total matched cases (not the filtered subset), and a filter with zero matches shows the info message rather than an empty block or an error.

## 2. Re-test Block C's toggle and "Stack used" line live

1. On the same result, confirm the 4/8/All toggle actually changes how many case references are shown, and that "All" doesn't error out on a query with fewer than 8 matched cases.
2. Confirm each case now shows a "Stack used: ..." line above its source link, and that it lists only tool(s) that also appear in the current Recommended AI Stack — not the case's full raw tool list. A case with no overlap should simply omit the line, not show it empty.
3. Copy the exported blueprint text (the code block at the bottom) and confirm it still shows exactly 4 case references regardless of what the on-screen toggle is set to — this was a deliberate decision (see Update F), not an oversight, so it's worth double-checking it actually landed that way.

## 3. Visually review the new "How the recommendation is made" section

1. Confirm it renders between the Export code block and the Feedback section, not somewhere else.
2. Check the 3-column layout (Retrieve / Rank & price / Trace) reads cleanly at your screen width, and the "Known limitations" bullet list renders as an actual bulleted list, not raw Markdown text.
3. Read through the copy once for accuracy — it's hand-written, not computed from live data, so if the dataset size, coverage percentage, or seat-ceiling number ever changes, this section won't update itself and someone will need to edit it directly in `app/dashboard.py`'s `_render_methodology_block()`.

## 4. Board/checklist housekeeping

Once the above passes, update the Epic 3 checklist line in `14-Build-Guide-Epic3-Blueprint-UI-v1.md` (currently marked `- [ ]`, live-test pending) and Update E/F/G's "Status" lines in `22-Build-Guide-Updates-Epic3-v1.md` to reflect the confirmed live test, the same way Update D's status was updated after your last round of testing. Update the kanban board too, per the usual pattern.
