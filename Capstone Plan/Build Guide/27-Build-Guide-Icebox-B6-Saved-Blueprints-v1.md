# Build Guide 27 — Icebox B.6: "Saved blueprints" client-side persistence panel

*Icebox card `stackpunk #45` · Priority: **Could Have** · Estimated effort: **~1.5 days** · Rank: **4 of 7***

*The Lovable prototype's "★ Save blueprint" button. The honest constraint this guide exists to document: **Streamlit session state does not survive a page refresh**, so "persistence" needs to be scoped carefully before anyone promises it in a demo.*

---

## What it does

Save the current blueprint under a name; a sidebar panel lists saved blueprints; clicking one re-renders it without re-running the pipeline. Export-all/import gives real cross-session persistence via a JSON file the *user* keeps — honest about the fact that we store nothing server-side ("No accounts, no data stored", per the prototype's own hero copy).

## Persistence options — decide before building

| Option | Survives refresh? | Effort | Verdict |
|---|---|---|---|
| A. `st.session_state` list | ❌ (session only) | trivial | **Build this** — right for a demo |
| B. + JSON download / upload | ✅ (user keeps the file) | +half day | **Build this too** — honest persistence |
| C. Browser localStorage via custom component | ✅ | high (new JS component or `streamlit-local-storage` dep) | Skip — icebox-the-icebox |
| D. Server-side file/db | ✅ | medium | Skip — contradicts "no data stored" promise |

## Where the changes go

| File | Change |
|---|---|
| `app/survey_modal.py` or **new** `app/saved_blueprints.py` | New module preferred — `render_save_button()`, `render_saved_panel()` |
| `app/intake.py` | Call `render_saved_panel()` (sidebar) near the top; results section gains the save button call |
| `app/dashboard.py` | No structural change — `render_blueprint(result)` already takes any result dict, saved or fresh |

## Steps

### 1. New `app/saved_blueprints.py`

```python
"""
Icebox B.6 — save/reload blueprints. Session-scoped by design (Option A+B):
we keep nothing server-side; export-to-JSON is the user's own persistence.
"""
import json
import time
import streamlit as st
from app.analytics.tracker import log_event


def _store() -> list:
    if "saved_blueprints" not in st.session_state:
        st.session_state.saved_blueprints = []
    return st.session_state.saved_blueprints


def render_save_button(result: dict):
    default_name = result.get("project_name") or f"Blueprint {len(_store()) + 1}"
    with st.popover("★ Save blueprint"):
        name = st.text_input("Name", value=default_name, key="save_bp_name")
        if st.button("Save", key="save_bp_go"):
            _store().append({"name": name, "saved_at": time.strftime("%H:%M"), "result": result})
            log_event("blueprint_saved")
            st.success(f"Saved '{name}' — see sidebar.")


def render_saved_panel():
    saved = _store()
    with st.sidebar:
        st.markdown("### ★ Saved blueprints")
        if not saved:
            st.caption("Nothing saved yet this session.")
        for i, item in enumerate(saved):
            if st.button(f"{item['name']}  ·  {item['saved_at']}", key=f"load_bp_{i}"):
                st.session_state.result = item["result"]
                st.rerun()
        if saved:
            st.download_button(
                "Export all (.json)",
                json.dumps([{**s, "result": s["result"]} for s in saved], default=str),
                file_name="aasa-saved-blueprints.json", mime="application/json",
            )
        uploaded = st.file_uploader("Import (.json)", type="json", key="bp_import")
        if uploaded is not None and st.button("Load imported", key="bp_import_go"):
            st.session_state.saved_blueprints = json.load(uploaded)
            st.rerun()
        st.caption("Saved blueprints live in this browser session only — "
                   "export the JSON to keep them.")
```

### 2. intake.py wiring

- Top of the script (after `st.set_page_config`): `render_saved_panel()`.
- In the results section (`if "result" in st.session_state:`), call `render_save_button(st.session_state.result)` right after `render_blueprint(...)`.

## Gotchas

- **Loading a saved blueprint overwrites `st.session_state.result`** — that's the intended mechanic (the existing render-on-every-rerun pattern from Card 1.4 does the rest), but it means the "current" unsaved result is gone. Acceptable for MVP; note it in the demo script.
- `st.popover` needs Streamlit ≥1.31 — check the installed version; fall back to an expander if older.
- The `result` dict contains everything including `matched_cases` — a few saved blueprints are fine in memory, but don't loop-save hundreds (no cap needed for MVP, just don't build an auto-save).
- Imported JSON is user-supplied: wrap `json.load` in try/except and `st.error` on garbage rather than stack-tracing.
- Buttons in the sidebar trigger full reruns — keys must be stable (`load_bp_{i}`) or Streamlit will duplicate widgets.

## Verification checklist

- [ ] Save two blueprints from two different queries; both listed; loading each re-renders the right one instantly (no pipeline re-run — watch the spinner absence).
- [ ] Export JSON → hard-refresh the page (state gone) → import the file → both blueprints restored.
- [ ] Corrupt JSON import → friendly error, no crash.
- [ ] Telemetry event fires on save.
- [ ] `py_compile`; move card #45 once live-tested. Demo-day tip: pre-save 2–3 good blueprints at the start of the session.
