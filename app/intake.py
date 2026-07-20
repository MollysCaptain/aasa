import os
import sys
import time

# --- Make sure the project root is importable ---
# Streamlit's own bootstrap inserts this script's directory (app/) at the
# front of sys.path when you run `streamlit run app/intake.py` — not the
# project root. That means Python looks for "app" *inside* app/ and raises
# `ModuleNotFoundError: No module named 'app'`, even when the terminal's
# working directory is correct. Explicitly adding the project root here
# fixes it regardless of where the command is run from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from app.data.options import ORG_SIZES, PRIVACY_POSTURES, INDUSTRIES, WORKFLOWS
from app.logic.pricing import PRICING
from app.validators import validate_intake
from app.pipeline import run_pipeline
from app.dashboard import render_blueprint
from app.analytics.tracker import log_event
from app.survey_modal import render_feedback_form
from app.saved_blueprints import render_saved_panel

# --- Page setup: must be the first Streamlit command in the script ---
st.set_page_config(
    page_title="AASA — AI-Assisted Stack Architect",
    page_icon="🧭",
    layout="centered",
)

# --- Dark, "neo-industrial" styling ---
# st.markdown with unsafe_allow_html=True lets us inject raw CSS.
# Lovable-parity UI round: grid background, orange accent, and the shared
# classes (.aasa-chip, .aasa-banner, .aasa-why, hero styles) that
# app/dashboard.py's chip row / banner / "why:" lines rely on — keep this
# block as the single home for all custom classes.
DARK_CSS = """
<style>
    /* Font decision v3 (2026-07): Inter for UI text, JetBrains Mono for the
       monospace accents (stat numbers, chips, micro-labels). Loaded from
       Google Fonts at runtime — every font-family below carries a system
       fallback stack, so an offline demo degrades gracefully to system fonts
       instead of breaking. @import must be the first rule in this block. */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    .stApp {
        background-color: #0f1115;
        color: #e8e9ec;
        background-image:
            linear-gradient(rgba(43, 47, 58, 0.35) 1px, transparent 1px),
            linear-gradient(90deg, rgba(43, 47, 58, 0.35) 1px, transparent 1px);
        background-size: 48px 48px;
    }
    /* Headings: sans-serif (font decision v2 — the app's default sans, same
       as the hero headline the team endorsed), cream, testid-scoped +
       !important so Streamlit's own theme styles can't override the color. */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    h1, h2, h3 {
        color: #f5f1ea !important;
        letter-spacing: 0.02em;
    }
    /* Buttons — Lovable style: dark fill, orange border/text, orange fill on
       hover. Container-scoped on purpose so number-input +/- steppers are NOT
       hit. data-testid selectors verified on Streamlit 1.59.2 — re-check
       after any Streamlit upgrade. */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stPopover"] > div > button,
    [data-testid="stFileUploader"] button {
        background-color: transparent;
        color: #818cf8;
        border: 1px solid #818cf8;
        border-radius: 2px;
        padding: 0.5em 1em;
        letter-spacing: 0.05em;
        white-space: nowrap;   /* stop labels wrapping mid-word ("Clea/r") in narrow columns */
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stPopover"] > div > button:hover,
    [data-testid="stFileUploader"] button:hover {
        background-color: #818cf8;
        color: #0f1115;
        border-color: #818cf8;
    }
    /* Semantic button colors — Streamlit puts a .st-key-<key> class on any
       keyed widget's container, so these target exactly one button each.
       Same red/green as the OVER/WITHIN BUDGET chips, for consistency.
       !important + explicit background: Streamlit's own focus/active styles
       fill a clicked button with the theme primaryColor (indigo), which
       otherwise wins over a border-only override. */
    .st-key-clear_result button,
    .st-key-clear_result button:focus,
    .st-key-clear_result button:active {
        background-color: transparent !important;
        color: #d9534f !important;
        border-color: #d9534f !important;
    }
    .st-key-clear_result button:hover {
        background-color: #d9534f !important;
        color: #0f1115 !important;
        border-color: #d9534f !important;
    }
    .st-key-copy_confirm button,
    .st-key-copy_confirm button:focus,
    .st-key-copy_confirm button:active {
        background-color: transparent !important;
        color: #5fb39c !important;
        border-color: #5fb39c !important;
    }
    .st-key-copy_confirm button:hover {
        background-color: #5fb39c !important;
        color: #0f1115 !important;
        border-color: #5fb39c !important;
    }
    /* Intake form reads as a panel, like the hero */
    [data-testid="stForm"] {
        border: 1px solid #2b2f3a;
        background-color: rgba(15, 17, 21, 0.85);
        padding: 1.6em 1.8em;
        border-radius: 0;
    }
    /* Widget labels -> uppercase micro-labels, Lovable style */
    [data-testid="stWidgetLabel"] p {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.72rem;
        color: #9aa4b2;
    }
    /* Block B metrics -> match the hero stat numbers */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        color: #818cf8;
    }
    [data-testid="stMetricLabel"] p {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-size: 0.72rem;
        color: #9aa4b2;
    }
    /* Inline code spans (the `compute`-priced tags) */
    code {
        color: #818cf8;
        background-color: #1b1e26;
    }
    /* Dividers + alerts onto the panel palette */
    hr { border-color: #2b2f3a; }
    [data-testid="stAlert"] {
        background-color: #1b1e26;
        color: #9aa4b2;
    }
    div[data-baseweb="select"] > div {
        background-color: #1b1e26;
        border-color: #2b2f3a;
    }
    /* --- top bar --- */
    .aasa-brand {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        color: #e8e9ec;
        font-size: 1.05rem;
        letter-spacing: 0.08em;
    }
    .aasa-brand .sub { color: #6b7480; font-size: 0.85rem; }
    .aasa-badge {
        float: right;
        border: 1px solid #818cf8;
        color: #818cf8;
        padding: 3px 12px;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
    }
    /* --- hero --- */
    .aasa-hero {
        border: 1px solid #2b2f3a;
        padding: 1.6em 1.8em;
        margin: 0.8em 0 1.6em 0;
        background-color: rgba(15, 17, 21, 0.85);
    }
    .aasa-eyebrow {
        color: #818cf8;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.18em;
    }
    .aasa-hero h1 {
        font-size: 2.4rem;
        line-height: 1.15;
        margin: 0.35em 0 0.4em 0;
        color: #f5f1ea;
    }
    .aasa-hero h1 .accent { color: #818cf8; }
    .aasa-hero p { color: #9aa4b2; max-width: 46em; }
    .aasa-stat-num {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 1.7rem;
        color: #f5f1ea;
        font-weight: bold;
    }
    .aasa-stat-label {
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.68rem;
        color: #6b7480;
        letter-spacing: 0.1em;
    }
    .aasa-scope {
        border-left: 2px solid #2b2f3a;
        padding-left: 1em;
        margin-top: 1.2em;
        color: #6b7480;
        font-size: 0.85rem;
    }
    .aasa-scope a { color: #818cf8; }
    /* --- blueprint chips / banner / why lines (rendered by dashboard.py) --- */
    .aasa-chip {
        display: inline-block;
        border: 1px solid #818cf8;
        color: #818cf8;
        padding: 2px 10px;
        margin: 0 6px 6px 0;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.06em;
    }
    .aasa-chip-ok   { border-color: #5fb39c; color: #5fb39c; }
    .aasa-chip-warn { border-color: #d9534f; color: #d9534f; }
    .aasa-banner {
        border-left: 3px solid #818cf8;
        background-color: #1b1e26;
        padding: 0.6em 1em;
        margin: 0.4em 0 1em 0;
        color: #9aa4b2;
        font-size: 0.9rem;
    }
    .aasa-banner b {
        color: #818cf8;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        letter-spacing: 0.08em;
    }
    .aasa-why {
        color: #818cf8;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        font-size: 0.85rem;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# Icebox B.6 (Build Guide 27) — sidebar panel listing this session's saved
# blueprints, with JSON export/import. Rendered on every rerun so loads work
# from anywhere; the matching Save button lives in dashboard.py's action row.
render_saved_panel()


# --- Hero stats, computed at load (not hardcoded) ---------------------------
# The Lovable prototype's hero hardcodes its early numbers (197 cases / 24
# tools / 21 industries, from the pre-pivot curated subset). Ours are computed
# from the live knowledge base + pricing table so they can never drift from
# reality: 3,023 cases / 41 priced tools / 24 industries as of this writing.
@st.cache_data
def _hero_stats() -> tuple[int, int, int]:
    import csv as _csv
    from app.logic.pricing import PRICING as _pricing
    n_cases = 0
    industries = set()
    with open("data/use-cases.csv", newline="", encoding="utf-8") as f:
        for row in _csv.DictReader(f):
            n_cases += 1
            industries.add(row["Use Case Industry"])
    return n_cases, len(_pricing), len(industries)


_n_cases, _n_tools, _n_industries = _hero_stats()

# --- Top bar ---
st.markdown(
    '<div class="aasa-brand">⊞ <b>AASA</b> '
    '<span class="sub">AI-Assisted Stack Architect</span>'
    '<span class="aasa-badge">PROTOTYPE · DEMO DATA</span></div>',
    unsafe_allow_html=True,
)

# --- Hero / intro ---
st.markdown(
    f"""
    <div class="aasa-hero">
        <div class="aasa-eyebrow">CAPSTONE MVP · GROUNDED IN {_n_cases:,} REAL AI DEPLOYMENTS</div>
        <h1>Match your constraints to <span class="accent">what teams like yours
        actually shipped.</span></h1>
        <p>Give AASA five constraints. It retrieves comparable real-world AI
        implementations, ranks the models, APIs and frameworks they used, and
        estimates a monthly cost against your budget — with every recommendation
        traceable to a real source.</p>
        <table style="border: none; margin-top: 0.8em;"><tr>
            <td style="border: none; padding-right: 2.5em;">
                <div class="aasa-stat-num">{_n_cases:,}</div>
                <div class="aasa-stat-label">CURATED REAL CASES</div></td>
            <td style="border: none; padding-right: 2.5em;">
                <div class="aasa-stat-num">{_n_tools}</div>
                <div class="aasa-stat-label">TOOLS PRICED</div></td>
            <td style="border: none; padding-right: 2.5em;">
                <div class="aasa-stat-num">{_n_industries}</div>
                <div class="aasa-stat-label">INDUSTRIES COVERED</div></td>
            <td style="border: none;">
                <div class="aasa-stat-num">~2 min</div>
                <div class="aasa-stat-label">TO BLUEPRINT</div></td>
        </tr></table>
        <div class="aasa-scope">Honest scope: this is a 4-week student prototype.
        Cases come from the open
        <a href="https://github.com/abbasmahdi-ai/ai-use-cases-library"
        target="_blank">AI Use-Cases Library</a> (MIT); pricing is a small
        hand-built, illustrative table. No accounts, no data stored — the
        numbers below are directional, not advice.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Near the top of intake.py, before the form:
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

    # Icebox B.5 (Build Guide 24) — both optional; deliberately NOT validated
    # in validate_intake, so leaving them empty changes nothing.
    with st.expander("Optional: project details"):
        project_name = st.text_input(
            "Project name",
            max_chars=60,
            help="Shown on your blueprint and export — useful if you save or share it.",
        )
        exclude_tools = st.multiselect(
            "Vendors to exclude",
            options=sorted(PRICING.keys(), key=lambda k: PRICING[k]["label"]),
            format_func=lambda k: PRICING[k]["label"],
            help="Tools you can't or won't use. They'll be removed before ranking.",
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
                # B.5 — optional extras
                "project_name": project_name.strip(),
                "exclude_tools": exclude_tools,
            })
        elapsed_seconds = time.time() - st.session_state.form_start_time
        log_event("results_shown", elapsed_seconds=round(elapsed_seconds, 1))

# Card 2.6's generate_summary (via run_pipeline) now returns timing/token data
# alongside the summary text — log it here so you have real latency/throughput
# numbers, not just "it felt slow," if performance ever comes up during testing.
        log_event("llm_summary_generated", **result["llm_metrics"])
        st.session_state.result = result  # persist across reruns — see note below

# Renders on every rerun as long as a result exists — not gated on `submitted`.
# See Card 1.4's "Why not render inside if submitted:" note for why this matters:
# Streamlit reruns the whole script on every interaction, and once Epic 3 adds
# buttons inside the results view, those reruns would otherwise wipe the blueprint.
if "result" in st.session_state:
    st.success("Blueprint ready — see below.")
    render_blueprint(st.session_state.result)
    render_feedback_form()