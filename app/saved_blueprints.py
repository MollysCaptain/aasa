"""
Icebox B.6 (Build Guide 27) — save/reload blueprints. Session-scoped by design
(guide's Option A+B): we keep nothing server-side; export-to-JSON is the user's
own persistence. A hard page refresh clears the session list — that's honest,
not a bug, and the sidebar caption says so.
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
    """Lives in dashboard.py's _render_action_row(), first column — matching
    the Lovable prototype's '★ Save blueprint' placement."""
    default_name = result.get("project_name") or f"Blueprint {len(_store()) + 1}"
    with st.popover("★ Save blueprint"):
        name = st.text_input(
            "Name", value=default_name, key="save_bp_name",
            help="A label for your own reference. No need to enter personal "
                 "or company-identifying information.",
        )
        if st.button("Save", key="save_bp_go"):
            _store().append({
                "name": name.strip() or default_name,
                "saved_at": time.strftime("%H:%M"),
                "result": result,
            })
            log_event("blueprint_saved")
            st.success(f"Saved — see sidebar.")


def render_saved_panel():
    saved = _store()
    with st.sidebar:
        st.markdown("### ★ Saved blueprints")
        if not saved:
            st.caption("Nothing saved yet this session.")
        for i, item in enumerate(saved):
            if st.button(f"{item['name']}  ·  {item['saved_at']}", key=f"load_bp_{i}"):
                # Loading overwrites the current (possibly unsaved) result —
                # intended mechanic; the render-on-every-rerun pattern from
                # Card 1.4 re-renders the loaded blueprint with no pipeline run.
                st.session_state.result = item["result"]
                st.rerun()
        if saved:
            st.download_button(
                "Export all (.json)",
                json.dumps(saved, default=str),
                file_name="aasa-saved-blueprints.json",
                mime="application/json",
            )
        uploaded = st.file_uploader("Import (.json)", type="json", key="bp_import")
        if uploaded is not None and st.button("Load imported", key="bp_import_go"):
            try:
                data = json.load(uploaded)
                # Minimal shape check — user-supplied file, fail friendly.
                assert isinstance(data, list)
                assert all(isinstance(x, dict) and "result" in x and "name" in x
                           for x in data)
            except (json.JSONDecodeError, AssertionError, UnicodeDecodeError):
                st.error("That file doesn't look like an AASA blueprint export.")
            else:
                st.session_state.saved_blueprints = data
                st.rerun()
        st.caption("Saved blueprints live in this browser session only — "
                   "export the JSON to keep them.")
