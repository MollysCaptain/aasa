# 32 — Build Guide: UI-v2 (Reduce-Scroll + Restyle) — what's done + what's left for you & Gabi

**Branch:** `Ash3`
**Trigger:** Week-3 stakeholder check-in — tutors said the product is good but
(a) everything sat on one long page with too much scrolling, and then, on the
live build, gave follow-up feedback on the tab bar, the accent font, and the
Recommended AI Stack section.
**Overall scope:** layout / styling / static-data only across three passes. No
pipeline, cost, filtering, prompt, or export *logic* was touched. All widget
keys (`stack_filter`, `case_count`, `clear_result`, `copy_confirm`, `save_bp_*`,
`bp_import*`) are unchanged, so session state keeps working exactly as before.

**Commits on `Ash3` (in order):**

| Commit | Pass | Summary |
|---|---|---|
| `0d87479` | UI-v2 | Sidebar form, tabbed blueprint, collapsing hero |
| `69e2201` | UI-v2b | Roboto Mono accent font + prominent Material-icon tabs |
| `04c9352` | UI-v2b | Roboto Mono SemiBold (600) for accent text |
| `647c2b0` | UI-v2c | Block A: single orange price tag + hyperlinked tool names |

Files touched across all passes: `app/intake.py`, `app/dashboard.py`,
`app/logic/pricing.py`, `.streamlit/config.toml`, and `static/fonts/`
(Roboto Mono woff2 added, JetBrains Mono woff2 removed).

---

## Pass 1 — UI-v2 (reduce scrolling) · commit `0d87479`

**Change 1 — intake form moved into the sidebar.** `app/intake.py`. The
five-field form (plus the "Optional: project details" expander) now renders
inside `with st.sidebar:`, under a "Build a blueprint" heading. The
saved-blueprints panel (`render_saved_panel()`) is called at the end of that
block so it sits beneath the form. The main column is now free for the blueprint,
so results are no longer stacked below a full-width form.

**Change 2 — blueprint split into tabs.** `app/dashboard.py`,
`render_blueprint()`. The six sections that used to stack down one column
separated by `st.divider()` are now `st.tabs`: **Stack · Cost · Cases · Summary ·
Export · How it works**. The status chips and the "DIRECTIONAL ONLY" banner stay
*above* the tabs as the at-a-glance line. The Export code block, the action row
(Save / Download / .env scaffold / Clear) and the copy-confirmation button live
in the **Export** tab; the methodology, known-limitations and "About this data"
content lives in **How it works**.

**Change 3 — hero collapses after first result.** `app/intake.py`. The tall hero
renders only when there is no blueprint yet (`if "result" not in
st.session_state:`). Once a result is on screen, only the compact top bar remains.
The success line was reworded to "Blueprint ready — explore the tabs below."

*Not included from the original proposal:* **wide layout** (change 4) — left as an
optional taste call (see Optional polish below).

---

## Pass 2 — UI-v2b (font + prominent tabs) · commits `69e2201`, `04c9352`

Follow-up to live feedback on the tab bar and the monospace accent font.

**Prominent, iconified tabs.** `app/dashboard.py` tab labels now carry a Material
icon each (`:material/layers:` Stack, `:material/payments:` Cost,
`:material/library_books:` Cases, `:material/summarize:` Summary,
`:material/download:` Export, `:material/help:` How it works) — Streamlit's
built-in icon set, **not emoji** (consistent with the earlier de-emoji decision).
Prominence CSS in `app/intake.py`'s `DARK_CSS` makes the tab bar larger, bold,
uppercase mono, with the active tab in indigo and a 3px indigo underline. *(This
completes what Pass 1 had listed as the optional "tab-bar theming" item.)*

**Roboto Mono replaces JetBrains Mono.** Every monospace accent (chips,
DIRECTIONAL-ONLY banner, uppercase micro-labels, metric numbers, brand/badge,
hero stats, `why:` lines, the tab bar, and `codeFont` in `config.toml`) now uses
Roboto Mono — more legible at small sizes, still distinct from Inter. Vendored
self-hosted via `@fontsource` into `static/fonts/roboto-mono-latin-{400,600,700}-normal.woff2`
(OFL); the old JetBrains Mono files were removed. This preserves the
no-Google-Fonts privacy decision (Card P.4).

**SemiBold (600) accent weight.** All Roboto Mono accent text is `font-weight:
600`; the tab bar stays Bold (700). Required vendoring the 600 weight file.

---

## Pass 3 — UI-v2c (Recommended AI Stack section) · commit `647c2b0`

Three changes to Block A, all in `_render_stack_block()` (`app/dashboard.py`) plus
supporting CSS/data:

1. **One-font price tag.** Was a mono `seat` code span + plain-font `-priced`; now
   a single styled token via `_PRICE_TAG_LABELS`. Wording (team decision):
   `token-priced` / `seat-priced` / **`usage-based`** (was "compute") /
   **`open source`** (was "free").
2. **Orange tag.** The tag uses `#e0872f` (the project's prior brand orange) via a
   new **scoped** `.aasa-price-tag` class in `DARK_CSS` — deliberately *not* the
   global `code` rule, which also styles the `.env`/export code blocks, so the
   colour change stays contained to Block A.
3. **Hyperlinked names.** Each recommendation's name links to the tool's official
   site (`target="_blank" rel="noopener"`), with a plain-span fallback when a URL
   is absent. A `"url"` field was added to **all 41 tools** in
   `app/logic/pricing.py` (official homepages — illustrative/product-root, verify
   like the prices). `a.aasa-stack-name` CSS keeps the linked name green and only
   underlines on hover.

---

## Verification done here (all passes)

`python3 -m py_compile` passes for `app/intake.py`, `app/dashboard.py`,
`app/logic/pricing.py`; all 41 pricing entries confirmed to carry an `https` URL;
the SemiBold weight audit confirmed `font-weight: 600` on every accent selector
(tab bar 700). The app was **not** run — this environment has no `chroma_store`,
embedding model, or `GROQ_API_KEY`, so a live render must happen on your machine.

---

## What's left for you & Gabi

### 1. Live visual QA (required before merge) — you or Gabi
Run on a machine with the full stack (populated `./chroma_store`, the
`all-MiniLM-L6-v2` model cached, `GROQ_API_KEY` in `.env`):

```
streamlit run app/intake.py
```

Check:

- **Layout:** form usable in the sidebar; watch the **Data-Privacy Posture** radio
  (`horizontal=True`) and **Generate my blueprint** button for awkward wrapping.
  Generating a blueprint collapses the hero and shows the six tabs — click each.
- **Tabs:** Material icons render as icons (if they show as literal
  `:material/...` text, the Streamlit build is too old); active tab is indigo with
  the underline; labels are bold uppercase mono.
- **Font:** accents are Roboto Mono SemiBold (not the old JetBrains look, not a
  system-mono fallback); the Export / .env code blocks are also Roboto Mono.
- **Block A:** price tag is one orange token with the new wording — confirm a
  *free* tool (e.g. LangChain/Chroma) shows **"open source"** and a *compute* tool
  (e.g. a cloud platform) shows **"usage-based"**; each tool name is a green link
  that opens the correct official site in a new tab; spot-check several of the 41
  URLs actually resolve.
- **Regressions:** the Stack pricing-type and Cases 4/8/All radios still work;
  Save / Download / .env scaffold / Clear behave (Clear empties the view, not the
  saved list); the feedback form still renders below the tabs.

### 2. Sidebar-form UX sign-off — Gabi
Moving the form into the sidebar changes the first-run feel (the form is no longer
the centre of the empty state). Confirm the sidebar placement is what we want, or
whether the empty state should keep a centred form until first submit.

### 3. Optional polish (nice-to-have, not blocking) — you
- **Wide layout.** `app/intake.py` ~line 29, `st.set_page_config(layout="centered")`
  → `"wide"`. With the sidebar form, a wide main column lets the Stack/Cost/Cases
  blocks use horizontal space. Taste call — try it and see. (Set in code, not in
  `.streamlit/config.toml`.)
- **Sidebar width / radio wrap.** If the privacy radio or budget input feel
  cramped, drop `horizontal=True` on the privacy radio or set a sidebar width.
  Only if QA shows a real problem.
- **URL maintenance.** The 41 vendor URLs are homepages and will drift; they're
  illustrative and covered by the in-product "verify on vendor page" disclaimers,
  but worth a periodic recheck (a natural companion to the planned pricing sync,
  Icebox B.3 / guide 30).

### 4. Fresh stakeholder screenshots — you or Gabi
The Week-3 deck's UI screenshots are now out of date. After QA, grab new
before/after shots (long-scroll page vs. sidebar + tabs + restyled Block A) for
the next check-in.

### 5. Kanban + merge — you
- Create the consolidated **UI-v2** Icebox card (details provided in chat), move it
  to **In Progress** now and **Done** once QA passes.
- Open the PR from `Ash3` and merge once Gabi has signed off on the sidebar
  placement.

---

## Selector / version caveats
`DARK_CSS` styles the tab bar via `button[data-baseweb="tab"]` /
`div[data-baseweb="tab-highlight"]`, and buttons via `data-testid` selectors.
These are Streamlit-internal and version-sensitive (the CSS notes Streamlit
1.59.2) — re-check them after any Streamlit upgrade. Material icons in tab labels
likewise need a Streamlit build recent enough to render `:material/...:`.

## Rollback
The four UI-v2 commits (`0d87479`, `69e2201`, `04c9352`, `647c2b0`) are additive
and touch only the files listed above. Reverting them restores the previous
one-page layout, JetBrains Mono font, and plain Block A with no other side effects.
The Roboto Mono woff2 files can then be deleted from `static/fonts/`.
