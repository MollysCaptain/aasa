# 32 — Build Guide: UI-v2 (Reduce-Scroll) — what's done + what's left for you & Gabi

**Branch:** `Ash3` · **Commit:** `0d87479` ("UI-v2 (reduce-scroll): sidebar form, tabbed blueprint, collapsing hero")
**Trigger:** Week-3 stakeholder check-in feedback — tutors said the product is
good but the single long page means too much scrolling.
**Scope of the commit:** layout-only refactor of `app/intake.py` and
`app/dashboard.py`. No pipeline, cost, filtering, prompt, export, or data logic
was touched. All widget keys (`stack_filter`, `case_count`, `clear_result`,
`copy_confirm`, `save_bp_*`, `bp_import*`) and every `DARK_CSS` class hook are
unchanged, so session state and theming keep working exactly as before.

---

## What was implemented (already committed — no action needed)

**Change 1 — intake form moved into the sidebar.** `app/intake.py`. The
five-field form (plus the "Optional: project details" expander) now renders
inside `with st.sidebar:`, under a "Build a blueprint" heading. The
saved-blueprints panel (`render_saved_panel()`) is called at the end of that
block so it sits beneath the form in the sidebar. The main column is now free
for the blueprint, so results are no longer stacked below a full-width form.

**Change 2 — blueprint split into tabs.** `app/dashboard.py`,
`render_blueprint()`. The six sections that used to stack down one column
separated by `st.divider()` are now `st.tabs`: **1 · Stack · 2 · Cost ·
3 · Cases · Summary · Export · How it works**. The status chips and the
"DIRECTIONAL ONLY" banner stay *above* the tabs as the at-a-glance line. The
Export code block, the action row (Save / Download / .env scaffold / Clear) and
the copy-confirmation button live in the **Export** tab; the methodology,
known-limitations and "About this data" content lives in **How it works**.

**Change 3 — hero collapses after first result.** `app/intake.py`. The tall
hero panel now renders only when there is no blueprint yet
(`if "result" not in st.session_state:`). Once a result is on screen, only the
compact top bar remains, so the user isn't pushed down the page. The success
line was reworded to "Blueprint ready — explore the tabs below."

**Verification done here:** `python3 -m py_compile app/intake.py
app/dashboard.py` passes, and both files parse cleanly (`ast.parse`). The app
itself was **not** run — this environment has no `chroma_store`, embedding
model, or `GROQ_API_KEY`, so a live render needs to happen on your machine
(next section).

---

## What's left for you & Gabi

### 1. Live visual QA (required before merge) — you or Gabi
Run the app on a machine with the full stack (populated `./chroma_store`, the
`all-MiniLM-L6-v2` model cached, `GROQ_API_KEY` in `.env`):

```
streamlit run app/intake.py
```

Check specifically:

- The form is usable in the narrower sidebar. Watch the **Data-Privacy Posture**
  radio (`horizontal=True`) and the **Generate my blueprint** button — if the
  radio wraps awkwardly or the button label wraps, note it for the polish pass
  below.
- Generating a blueprint moves focus to the main column; the hero disappears and
  the six tabs appear. Click every tab.
- Inside tabs, the **Filter by pricing type** (Stack) and **Show 4/8/All**
  (Cases) radios still work, and **Save / Download (.md) / .env scaffold /
  Clear** in the Export tab all behave. **Clear** should empty the current view
  but *not* the saved list.
- Save a blueprint, confirm it appears in the sidebar beneath the form, reload
  it, and confirm the tabs re-render without re-running the pipeline.
- The feedback form still renders below the tabs after a result.

### 2. Sidebar-form UX sign-off — Gabi
Moving the form into the sidebar changes the first-run feel (the form is no
longer the centre of the empty state). This was flagged in the commit as worth a
deliberate look. Confirm with Gabi that the sidebar placement is what we want, or
whether the empty state should keep a centred form until the first submit.

### 3. Optional polish (nice-to-have, not blocking) — you
These were deliberately **left out** of the commit because they're either a
judgement call or best done with the app running in front of you:

- **Wide layout** (my original "change 4"). `app/intake.py` line ~29,
  `st.set_page_config(layout="centered")` → `"wide"`. With the form in the
  sidebar a wide main column lets the Stack/Cost/Cases blocks use horizontal
  space. Left off because it's a taste call and changes the whole feel — try it
  and see. (This is set in code, not in `.streamlit/config.toml`.)
- **Tab-bar theming.** `st.tabs` renders with Streamlit's default tab styling,
  which won't match the indigo/mono theme out of the box. If it looks off, add a
  `[data-baseweb="tab-list"] / [data-baseweb="tab"]` block to `DARK_CSS` in
  `app/intake.py`. Verify the `data-baseweb` selectors against the Streamlit
  version in use (the existing CSS notes 1.59.2) — re-check after any upgrade.
- **Sidebar width / radio wrap.** If the privacy radio or budget input feel
  cramped, either drop `horizontal=True` on the privacy radio or set a sidebar
  width. Only worth doing if QA in step 1 shows a real problem.

### 4. Fresh stakeholder screenshots — you or Gabi
The Week-3 deck's UI screenshots are now out of date. After QA, grab new
before/after shots (long-scroll page vs. sidebar + tabs) for the next check-in —
they're the most direct evidence that the tutor feedback was actioned.

### 5. Kanban + merge — you
- Move the UI-v2 Icebox card (details below, in chat) to **In Progress** now and
  **Done** once QA passes.
- Open the PR from `Ash3` and merge once Gabi has signed off on the sidebar
  placement.

---

## Rollback
Everything is in one commit (`0d87479`) touching only two files. If the sidebar
form doesn't land well, reverting that single commit restores the previous
one-page layout with no other side effects.
