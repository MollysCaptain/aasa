# 33 — Build Guide: Ash3-update (wide-layout refinements from Gabi's feedback)

**Branch:** `Ash3-update` (off `Ash3-wide`, which keeps `layout="wide"`) · **Commit:** `66721d7`
**Trigger:** Gabi's feedback after trying the centered (`Ash3`) and wide
(`Ash3-wide`) versions — she preferred the wide look but flagged readability,
wanted a wider sidebar, and asked about mobile.
**Scope:** styling / UX only. No pipeline, cost, filtering, prompt, export, or
data logic touched.

## Branch map (three UI variants now exist)

| Branch | Layout | Notes |
|---|---|---|
| `Ash3` | centered | The version the team was happy with |
| `Ash3-wide` | wide | One-line `layout="wide"` variant for A/B |
| `Ash3-update` | wide + refinements | **This branch** — wide, but readable |

`Ash3-update` is the "best of both" Gabi and I discussed: wide look, narrow-style
readability.

## What changed (all in commit `66721d7`)

**1. Sidebar auto-width.** `app/intake.py`. On the empty state (no blueprint
yet) the sidebar renders wide (`34rem`) so the form and its labels have room;
once a blueprint exists it drops back to Streamlit's default width so the
results get the space. Implemented as conditional CSS gated on
`"result" in st.session_state`, injected just after `DARK_CSS`. **Clear** removes
the result, so the wide sidebar returns on the next run.
*Caveat:* the width uses `!important` to beat Streamlit's own sidebar width,
which limits manual drag-resize while the wide rule is active — an accepted
trade for the requested automatic behaviour. The `section[data-testid="stSidebar"]`
selector is Streamlit-internal; re-check after any Streamlit upgrade.

**2. Prose width cap (keeps wide legible).** `app/dashboard.py` +
`app/intake.py`. The **Summary**, **Real Case References**, and **How it works**
tab contents are each wrapped in a keyed `st.container()`
(`aasa_prose_summary`, `aasa_prose_cases`, `aasa_prose_how`); `DARK_CSS` caps
them via the matching `.st-key-*` classes (`72ch` for Summary/Cases, `52rem` for
How-it-works so its three columns stay comfortable). **Block A (Stack)** and
**Block B (Cost)** are deliberately left unwrapped and keep the full page width,
as do the tabs — so structured/columnar content spreads out while long lines of
body text stay at a readable measure.

**3. Saved blueprints → expander.** `app/saved_blueprints.py`. The sidebar
saved-blueprints panel now lives in a collapsible `st.expander`
("★ Saved blueprints (N)"), expanded only when something is saved, to cut the
sidebar's height and the scrolling Gabi mentioned.

## Verification done here

`python3 -m py_compile` passes for all three files. `st.container(key=...)` is
supported in the installed Streamlit (1.59.2), and the `.st-key-<key>` class
convention is the same one the existing button CSS already relies on. The app
was **not** run (no `chroma_store` / model / `GROQ_API_KEY` here), so a live
render is still required.

## QA items (live run required, on a machine with the full stack)

- [ ] **Sidebar auto-width:** wide on first load; collapses to default after
  Generate; returns to wide after Clear. Confirm the form/labels look right at
  `34rem` (tune the value if needed) and that the collapse (hamburger) still works.
- [ ] **Readability:** Summary / Cases / How-it-works read at a comfortable
  width in wide layout; Stack and Cost still use the full width. Adjust the
  `72ch` / `52rem` caps if they feel off.
- [ ] **Saved-blueprints expander:** opens/closes, save → appears, load/import/
  export all still work.
- [ ] **📱 Mobile check (NEW — Gabi's question).** Open on a real phone (or a
  narrow browser viewport / dev-tools device mode). Verify: the sidebar collapses
  behind the hamburger and is reachable; the six-tab bar wraps or scrolls
  acceptably; the four-button Export action row stacks rather than overflowing;
  the hero stats table and the chips row don't overflow horizontally; the
  prose caps don't cause awkward narrow columns on small screens. Capture
  findings + screenshots. (Tracked as its own Icebox card — see chat.)

## Rollback
Single commit (`66721d7`) on its own branch; delete the branch or revert the
commit to drop these refinements with no effect on `Ash3` / `Ash3-wide`.
