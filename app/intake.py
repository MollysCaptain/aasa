import os
import sys

# --- Make sure the project root is importable ---
# Streamlit's own bootstrap inserts this script's directory (app/) at the
# front of sys.path when you run `streamlit run app/intake.py` — not the
# project root. That means Python looks for "app" *inside* app/ and raises
# `ModuleNotFoundError: No module named 'app'`, even when the terminal's
# working directory is correct. Explicitly adding the project root here
# fixes it regardless of where the command is run from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

import streamlit as st

from app.data.options import ORG_SIZES, PRIVACY_POSTURES, INDUSTRIES, WORKFLOWS
from app.validators import validate_intake
from app.pipeline import run_pipeline
from app.analytics.tracker import log_event
from app.survey_modal import render_trust_survey

# --- Page setup: must be the first Streamlit command in the script ---
st.set_page_config(
    page_title="AASA — AI-Assisted Stack Architect",
    page_icon="🧭",
    layout="centered",
)

# --- Dark, "neo-industrial" styling ---
# st.markdown with unsafe_allow_html=True lets us inject raw CSS.
DARK_CSS = """
<style>
    .stApp {
        background-color: #0f1115;
        color: #e8e9ec;
    }
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        letter-spacing: 0.02em;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
    }
    div[data-baseweb="select"] > div {
        background-color: #1b1e26;
        border-color: #2b2f3a;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.title("🧭 AI-Assisted Stack Architect")
st.caption("Five constraints in. A data-backed blueprint out.")

# --- Card 3.3: mark when this session first opened the form, so we can ---
# --- compute total elapsed time (form open -> results shown) at submit. ---
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = time.time()
    log_event("form_start")

# --- The 5-field form ---
# Options now come from app/data/options.py — real Industry/Workflow values
# derived from the case dataset (Card 2.1 Step 0), not hardcoded placeholders.
with st.form("intake_form"):
    workflow = st.selectbox("Target AI Workflow", WORKFLOWS)
    industry = st.selectbox("Industry", INDUSTRIES)
    org_size_key = st.selectbox(
        "Organisation Size",
        options=list(ORG_SIZES.keys()),
        format_func=lambda k: ORG_SIZES[k],   # shows the friendly label, stores the short key
    )
    privacy_key = st.radio(
        "Data-Privacy Posture",
        options=list(PRIVACY_POSTURES.keys()),
        format_func=lambda k: PRIVACY_POSTURES[k],
        horizontal=True,
        help="Regulated = you handle data subject to HIPAA/GDPR/financial "
             "regulation and need governable, self-hostable tools.",
    )
    budget = st.number_input(
        "Monthly Budget (€)",
        min_value=0, step=50, value=800,
    )

    submitted = st.form_submit_button("Generate my blueprint")

if submitted:
    is_valid, error_message = validate_intake(
        workflow, industry, org_size_key, privacy_key, budget
    )
    if not is_valid:
        st.error(error_message)
    else:
        with st.spinner("Building your blueprint..."):
            result = run_pipeline({
                "workflow": workflow, "industry": industry,
                "org_size": org_size_key, "privacy": privacy_key,
                "budget": budget,
            })
        st.session_state.result = result  # persist across reruns — see note below

        # Card 3.3: form-completion velocity + LLM latency/throughput, logged
        # once per successful submission (not on every rerun, unlike the
        # rendering block below — this branch only runs right after a fresh
        # run_pipeline() call).
        elapsed_seconds = time.time() - st.session_state.form_start_time
        log_event("results_shown", elapsed_seconds=round(elapsed_seconds, 1))
        log_event("llm_summary_generated", **result["llm_metrics"])

# Renders on every rerun as long as a result exists — not gated on `submitted`.
# See Card 1.4's "Why not render inside if submitted:" note for why this matters:
# Streamlit reruns the whole script on every interaction, and once Epic 3 adds
# buttons inside the results view, those reruns would otherwise wipe the blueprint.
if "result" in st.session_state:
    st.success("Blueprint ready — see below.")
    st.json(st.session_state.result)  # Card 3.1 will replace this raw JSON dump with the real 3-block layout

    # Card 3.4: post-generation trust survey. Guide says "right after
    # render_blueprint(...)" — that's Card 3.1, which hasn't landed yet, so
    # this sits right after the st.json placeholder for now instead. Also in
    # this persistent block (not `if submitted:`) so submitting the survey
    # reruns the script without losing the blueprint, same as the export button.
    render_trust_survey()

    # Card 3.3: proxy for the export-click event ahead of Card 3.2's real copy
    # button — Streamlit's native st.code copy icon has no click callback, so
    # an explicit confirmation button is the only way to log a true click.
    # Lives in this block (not inside `if submitted:`) for the same reason
    # the rendering above does: clicking it reruns the script without
    # wiping the blueprint out of session_state.
    if st.button("✅ I've copied my blueprint"):
        log_event("export_clicked")
        st.success("Noted — thanks!")