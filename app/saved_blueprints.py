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


@st.dialog("Save blueprint")
def _save_blueprint_dialog(result: dict):
    """The name-entry pop-up. UI-v2f: this is now an st.dialog (modal) instead of
    an st.popover — a popover can't be closed programmatically, so it lingered
    open after Save and a second click re-saved the same name. A dialog closes
    reliably on st.rerun(), which we call right after saving."""
    default_name = result.get("project_name") or f"Blueprint {len(_store()) + 1}"
    name = st.text_input(
        "Name", value=default_name, key="save_bp_name",
        help="A label for your own reference. No need to enter personal "
             "or company-identifying information.",
    )
    if st.button("Save", key="save_bp_go"):
        _store().append({
            "name": name.strip() or default_name,
            "saved_at": time.strftime("%H:%M"),   # stored for export; no longer shown in the list
            "result": result,
        })
        log_event("blueprint_saved")
        # Flag drives the green confirmation under the Save button (below), and
        # st.rerun() closes this dialog + refreshes the sidebar list in one go.
        st.session_state["_blueprint_just_saved"] = True
        # Ash3-update v2: reopen the sidebar (420px) so the user sees the newly
        # saved blueprint in the (now expanded) list.
        st.session_state["_sidebar_next"] = 420
        st.rerun()


def render_save_button(result: dict):
    """Lives in dashboard.py's _render_action_row(), first column — matching
    the Lovable prototype's '★ Save blueprint' placement. Opens the save dialog;
    shows a one-shot 'Blueprint saved!' confirmation beneath the button after a
    successful save."""
    if st.button("★ Save blueprint", key="save_bp_open"):
        _save_blueprint_dialog(result)
    if st.session_state.pop("_blueprint_just_saved", False):
        st.success("Blueprint saved!")


def render_saved_panel():
    saved = _store()
    # Ash3-update: the panel now lives in a collapsible expander (was rendered
    # inline) to cut the sidebar's height / scrolling. Expanded by default only
    # when there's something saved to see; collapsed on the empty state.
    with st.sidebar:
        with st.expander(f"★ Saved blueprints ({len(saved)})", expanded=bool(saved)):
            if not saved:
                st.caption("Nothing saved yet this session.")
            for i, item in enumerate(saved):
                # UI-v2e: save-time (HH:MM) dropped from the label — blueprints
                # are already distinguished by name/number, so it added little.
                if st.button(f"{item['name']}", key=f"load_bp_{i}"):
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
