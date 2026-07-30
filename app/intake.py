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

_SIDEBAR_WIDTH = 440    # px — open-sidebar width floor (drag wider allowed; ~midpoint of 340-540)

# --- Page setup: must be the first Streamlit command in the script ---
st.set_page_config(
    page_title="AASA — AI-Assisted Stack Architect",
    page_icon="🧭",
    # Wide layout (from the Ash3-wide variant): with the form in the sidebar,
    # the main column and the Stack/Cost/Cases columns use the full page width.
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar open/closed is OUR state, driven by CSS (Ash3-update v2.2) ------
# Streamlit's initial_sidebar_state is only honoured on the first page load, not
# on reruns (confirmed live — two attempts via the API left the sidebar tiny and
# never collapsed/expanded on Generate/Save). So we manage open/closed ourselves:
# a session flag decides whether CSS shows the sidebar (fixed width) or hides it
# (display:none), and we render our own "Edit Builder" control to reopen it
# (Streamlit's native >> chevron only appears for its own collapse state, which
# we don't use). This is CSS — the same mechanism that reliably set the sidebar
# width earlier in the project.
#   - open  -> sidebar shown at 540px           (empty state, after Save/Clear)
#   - closed -> sidebar hidden, reopen button    (after Generate)
st.session_state.setdefault("sidebar_open", True)

# --- Dark, "neo-industrial" styling ---
# st.markdown with unsafe_allow_html=True lets us inject raw CSS.
# Lovable-parity UI round: grid background, orange accent, and the shared
# classes (.aasa-chip, .aasa-banner, .aasa-why, hero styles) that
# app/dashboard.py's chip row / banner / "why:" lines rely on — keep this
# block as the single home for all custom classes.
DARK_CSS = """
<style>
    /* Font decision v5 (2026-07): Inter for UI text, Roboto Mono for the
       monospace accents (labels, chips, code tags, "why:" lines, tab bar).
       v5 replaced JetBrains Mono with Roboto Mono after Week-3 tutor feedback
       — more legible at small sizes while staying distinct from Inter. v5.1
       set most Roboto Mono accent text (everything below except the tab bar,
       which stays Bold/700) to SemiBold/600 instead of Regular/400 — team
       decision after seeing the live render. Both families are SELF-HOSTED
       from static/fonts/ instead of Google Fonts, so
       no user's browser makes a third-party request (closes the IP-exposure
       caveat from the Week 2 data-minimisation checkpoint). Files are
       OFL-licensed, vendored via @fontsource. Served by Streamlit's static
       file server (enableStaticServing in .streamlit/config.toml) at the
       app/static/ URL path. Every font-family below still carries a system
       fallback stack, so if static serving is ever off the app degrades
       gracefully instead of breaking. */
    @font-face { font-family: 'Inter'; font-weight: 400; font-display: swap;
        src: url('app/static/fonts/inter-latin-400-normal.woff2') format('woff2'); }
    @font-face { font-family: 'Inter'; font-weight: 600; font-display: swap;
        src: url('app/static/fonts/inter-latin-600-normal.woff2') format('woff2'); }
    @font-face { font-family: 'Inter'; font-weight: 700; font-display: swap;
        src: url('app/static/fonts/inter-latin-700-normal.woff2') format('woff2'); }
    @font-face { font-family: 'Roboto Mono'; font-weight: 400; font-display: swap;
        src: url('app/static/fonts/roboto-mono-latin-400-normal.woff2') format('woff2'); }
    @font-face { font-family: 'Roboto Mono'; font-weight: 600; font-display: swap;
        src: url('app/static/fonts/roboto-mono-latin-600-normal.woff2') format('woff2'); }
    @font-face { font-family: 'Roboto Mono'; font-weight: 700; font-display: swap;
        src: url('app/static/fonts/roboto-mono-latin-700-normal.woff2') format('woff2'); }

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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.85rem;   /* UI-v2d: bumped from 0.72rem — form + Feedback labels were hard to read */
        color: #9aa4b2;
    }
    /* v2.7: intake-form field titles in the indigo accent (per feedback).
       Scoped to the sidebar (higher specificity beats the grey rule above) so
       the Feedback form + metric labels in the main area stay grey. */
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #818cf8; }
    /* Block B metrics -> match the hero stat numbers */
    [data-testid="stMetricValue"] {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        color: #818cf8;
    }
    [data-testid="stMetricLabel"] p {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
    /* UI-v2h: hide Streamlit's "Press Enter to submit form" / "Press Enter to
       apply" helper under text/number inputs — it's noise here, since the form
       is submitted with the Generate button, not Enter. */
    [data-testid="InputInstructions"] { display: none; }
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-size: 1.7rem;
        color: #f5f1ea;
        font-weight: 600;
    }
    .aasa-stat-label {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
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
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        letter-spacing: 0.08em;
    }
    .aasa-stack-name {
        color: #5fb39c;
        font-weight: 700;
        font-size: 1.05rem;
    }
    /* UI-v2c: when the stack name is a link to the tool's site, keep it green
       (Streamlit's default link colour would otherwise turn it blue) and only
       underline on hover so it doesn't look like body-copy link text. */
    a.aasa-stack-name, a.aasa-stack-name:link, a.aasa-stack-name:visited {
        color: #5fb39c;
        text-decoration: none;
    }
    a.aasa-stack-name:hover { text-decoration: underline; }
    /* UI-v2c: pricing-model tag — orange + mono so it separates from the green
       stack name. Own class (not the global `code` rule, which also styles the
       .env scaffold + export code blocks) so the colour change stays scoped. */
    .aasa-price-tag {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        color: #e0872f;
        background-color: #1b1e26;
        padding: 1px 6px;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
    }
    .aasa-why {
        color: #818cf8;
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        font-size: 0.95rem;   /* UI-v2d: bumped from 0.85rem for legibility */
    }
    /* --- Blueprint tabs (UI-v2b) — more prominent per Week-3 tutor feedback.
       Bigger, uppercase mono labels with clear spacing; the selected tab and
       its underline go indigo so the current section is obvious. baseweb
       selectors verified on the project's Streamlit build — re-check after any
       Streamlit upgrade (same caveat as the button selectors above). The
       Material icons themselves come from the tab labels in dashboard.py. */
    button[data-baseweb="tab"] {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.92rem;
        font-weight: 700;
        padding: 12px 18px;
        color: #9aa4b2;
    }
    button[data-baseweb="tab"] * { font-size: 0.92rem; }   /* size the icon glyph with the label */
    div[data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid #2b2f3a; }
    button[data-baseweb="tab"]:hover { color: #e8e9ec; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #818cf8; }
    div[data-baseweb="tab-highlight"] { background-color: #818cf8; height: 3px; }
    /* Ash3-update: cap the reading width of the prose-heavy tab sections so the
       wide layout stays legible (long lines of body text are hard to read).
       Block A (Stack) and Block B (Cost) are NOT wrapped, so their columns /
       metrics keep the full page width. Keys set via st.container(key=...) in
       dashboard.py -> Streamlit emits a matching .st-key-<key> class. */
    .st-key-aasa_prose_summary, .st-key-aasa_prose_cases { max-width: 72ch; }
    /* First-real-user feedback: the Cost tab prices only ONE primary API + ONE
       assistant, so most recommendations show no figure there and testers read
       that as inconsistent. These two rows in the Stack tab get a subtle lift off
       the page background (plus an "in cost forecast" caption, since colour alone
       is not an accessible signal). Substring match on the key so it applies to
       whichever ranks happen to be the costed ones. */
    [class*="st-key-aasa_costed_row_"] {
        background: #181B22;
        border-left: none;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.35rem;
    }
    .st-key-aasa_prose_how { max-width: 52rem; }   /* wider: keeps the 3 "how" columns comfortable */
    /* Ash3-update v2.2: we manage the sidebar open/closed ourselves (see below),
       so hide Streamlit's native collapse (<<) and expand (>>) controls to keep
       our state and the UI in sync. Our own "Edit Builder" button reopens
       the sidebar when it's hidden. */
    [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"] {
        display: none !important;
    }
    /* Style our custom sidebar controls (keyed st.buttons) — mono, top-left. */
    .st-key-reopen_sidebar button, .st-key-collapse_sidebar button {
        font-family: 'Roboto Mono', 'Courier New', monospace;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# --- Apply the sidebar open/closed state via CSS + a custom reopen control ---
# DERIVE the effective open/closed state so Clear and Save reliably bring the
# sidebar back (the raw flag alone proved flaky in testing). Force open when:
#   - there's no blueprint (empty state — the form must be visible; covers Clear)
#   - a save just happened (so the new saved blueprint is visible; covers Save)
# Otherwise use the flag (Generate sets it False to collapse; the reopen button
# and Clear/Save set it True).
_sidebar_open = st.session_state.get("sidebar_open", True)
# Force open (covers Clear -> empty state, and Save) UNLESS the user explicitly
# clicked Collapse — that lets the ≪ Collapse button work even in the empty
# state, where otherwise "no result" would force the sidebar back open.
if not st.session_state.get("_user_collapsed", False):
    if ("result" not in st.session_state) or st.session_state.get("_blueprint_just_saved"):
        _sidebar_open = True
st.session_state.sidebar_open = _sidebar_open

if _sidebar_open:
    # min-width (NOT a fixed width): Streamlit applies the sidebar width as an
    # inline style from a resizable React component, so a fixed `width:!important`
    # blocked dragging. min-width sets the open width but still lets the user drag
    # the sidebar WIDER (it just can't be dragged narrower than this).
    st.markdown(
        f"<style>section[data-testid='stSidebar']{{min-width:{_SIDEBAR_WIDTH}px !important;}}</style>",
        unsafe_allow_html=True,
    )
    # Our own collapse control (native << is hidden by DARK_CSS), top-left.
    if st.button("≪  Collapse", key="collapse_sidebar"):
        st.session_state.sidebar_open = False
        st.session_state["_user_collapsed"] = True
        st.rerun()
else:
    # Hide the whole sidebar; the main column reflows to full width. The reopen
    # button below is the only way back in (native chevron is hidden by DARK_CSS).
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none !important;}</style>",
        unsafe_allow_html=True,
    )
    if st.button("≫  Edit Builder", key="reopen_sidebar"):
        st.session_state.sidebar_open = True
        st.session_state["_user_collapsed"] = False
        st.session_state["build_open"] = True   # reopening shows the form expanded
        st.rerun()

# Icebox B.6 (Build Guide 27) — the saved-blueprints panel is a sidebar panel.
# Change 1 (UI-v2 · reduce-scroll) moved the intake form into the sidebar too,
# so render_saved_panel() is now called *after* the form (further down) to keep
# the form on top and the saved list beneath it. It still renders on every
# rerun so loads work from anywhere.


# --- Hero stats, computed at load (not hardcoded) ---------------------------
# The Lovable prototype's hero hardcodes its early numbers (197 cases / 24
# tools / 21 industries, from the pre-pivot curated subset). Ours are computed
# from the live knowledge base + pricing table so they can never drift from
# reality: 3,023 cases / 41 priced tools / 24 industries as of this writing.
@st.cache_data
def _hero_stats() -> tuple[int, int, int]:
    # Was: read data/use-cases.csv directly. That file is the raw third-party
    # dataset and is intentionally gitignored (see .gitignore), so it doesn't
    # exist on Streamlit Community Cloud — this crashed every page load there
    # with FileNotFoundError. chroma_store/ *is* committed (Card P.16/Cloud
    # deploy fix) and its metadata already carries case_id + industry for
    # every embedded case, so we can get the same real, live-computed numbers
    # from there instead, without needing the raw CSV at runtime at all.
    from app.logic.pricing import PRICING as _pricing
    from app.pipeline import _collection as _coll
    all_meta = _coll.get(include=["metadatas"])["metadatas"]
    case_ids = {m["case_id"] for m in all_meta}
    industries = {m["industry"] for m in all_meta}
    return len(case_ids), len(_pricing), len(industries)


_n_cases, _n_tools, _n_industries = _hero_stats()

# --- Top bar ---
st.markdown(
    '<div class="aasa-brand">⊞ <b>AASA</b> '
    '<span class="sub">AI-Assisted Stack Architect</span>'
    '<span class="aasa-badge">PROTOTYPE · DEMO DATA</span></div>',
    unsafe_allow_html=True,
)

# --- Hero / intro ---
# Change 3 (UI-v2 · reduce-scroll): the full hero is ~one screen tall. Show it
# only before a blueprint exists — once results are on screen the compact top
# bar above is enough, and the user is no longer forced to scroll past the hero
# to reach their own blueprint. The top bar (above) still renders on every run.
if "result" not in st.session_state:
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
                <!-- ~2 min is the MEDIAN time-to-results from the real user-test
                     round (114s over 12 sessions). It briefly read ~5 min, changed
                     on the basis of the MEAN (372s) — but the mean is dragged up by
                     two sessions of 1,287s and 1,617s where someone left the form
                     open. For "how long does this take a typical user", the median
                     is the right statistic and ~2 min is the honest number.
                     Reverted 2026-07-28; both figures are reported in the P.14
                     write-up so nothing is hidden. Recompute with:
                     scripts/telemetry_funnel.py --p14 -->
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

# --- Sidebar: intake form + saved blueprints -------------------------------
# Change 1 (UI-v2 · reduce-scroll): the 5-field form now lives in the sidebar.
# This frees the main column for the blueprint, so results are no longer stacked
# beneath a full-width form and the user isn't forced to scroll past the intake
# to reach (or re-read) their result. The form stays visible for re-runs.
# render_saved_panel() is called at the END of this block so the saved list
# sits beneath the form in the sidebar (it targets st.sidebar internally).
with st.sidebar:
    # form_start_time drives Card 3.3's time-to-results telemetry — set once
    # per session, before the form renders.
    if "form_start_time" not in st.session_state:
        st.session_state.form_start_time = time.time()
        log_event("form_start")

    # Ash3-update v2.4: the form now lives in a "Build a blueprint" expander, like
    # the Saved-blueprints panel. build_open drives its expanded state — open by
    # default, but auto-collapsed right after a Save (set in saved_blueprints.py)
    # so the freshly-saved blueprint below becomes the focus. Reopen/Clear set it
    # back open.
    # Ash3-update v2.5: the expander key includes _build_open so it REMOUNTS when
    # that flag flips — otherwise Streamlit ignores `expanded` changes on rerun
    # and the "collapse on Save" wouldn't take effect.
    # v2.6: widget keys are suffixed with a form_nonce. Clear bumps the nonce
    # (dashboard.py) so the widgets get brand-new keys and reset to their
    # DEFAULTS — deleting the old keys wasn't enough for widgets inside an
    # st.form (the frontend retains their values). Reading the returned values
    # (workflow, industry, ...) is unaffected; only the keys change.
    _build_open = st.session_state.get("build_open", True)
    _fn = st.session_state.get("form_nonce", 0)
    with st.expander("Build a blueprint", expanded=_build_open, key=f"build_exp_{_build_open}"):
        # Options come from app/data/options.py — real Industry/Workflow values
        # derived from the case dataset (Card 2.1 Step 0), not hardcoded.
        with st.form("intake_form"):
            workflow = st.selectbox("Target AI Workflow", WORKFLOWS, key=f"in_workflow_{_fn}")
            industry = st.selectbox("Industry", INDUSTRIES, key=f"in_industry_{_fn}")
            org_size_key = st.selectbox(
                "Organisation Size",
                options=list(ORG_SIZES.keys()),
                format_func=lambda k: ORG_SIZES[k],   # friendly label, stores the short key
                key=f"in_org_size_{_fn}",
            )
            privacy_key = st.radio(
                "Data-Privacy Posture",
                options=list(PRIVACY_POSTURES.keys()),
                format_func=lambda k: PRIVACY_POSTURES[k],
                horizontal=True,
                # Reworded 2026-07-27 after the first real user-test session:
                # the old text defined "Regulated" only, leaving the reader to
                # infer "Standard" by elimination, and never said what actually
                # changes in the output. Both options are now defined, and the
                # consequence is stated so the choice is informed.
                help=(
                    "**Standard** — normal business data, no sector-specific rules. "
                    "All tools in the library stay eligible.\n\n"
                    "**Regulated** — you handle data covered by HIPAA, GDPR or "
                    "financial regulation (patient records, EU personal data, "
                    "payment or account data). Tools we could not classify as "
                    "governable — self-hostable, or offering enterprise data "
                    "controls — are filtered out before ranking, so you may see "
                    "fewer recommendations.\n\n"
                    "This is a directional shortlist, not a compliance "
                    "certification. Verify with your own legal review."
                ),
                key=f"in_privacy_{_fn}",
            )
            budget = st.number_input(
                "Monthly Budget (€)",
                min_value=0, step=50, value=800,
                key=f"in_budget_{_fn}",
            )

            # Icebox B.5 (Build Guide 24) — both optional; deliberately NOT
            # validated in validate_intake, so leaving them empty changes nothing.
            # NB: rendered inline (not in a nested expander) — Streamlit forbids
            # an expander inside the "Build a blueprint" expander above.
            st.caption("Optional — leave blank to skip")
            project_name = st.text_input(
                "Project name",
                max_chars=60,
                help="Shown on your blueprint and export — useful if you save or share it. "
                     "No need to enter personal or company-identifying information.",
                key=f"in_project_name_{_fn}",
            )
            exclude_tools = st.multiselect(
                "Vendors to exclude",
                options=sorted(PRICING.keys(), key=lambda k: PRICING[k]["label"]),
                format_func=lambda k: PRICING[k]["label"],
                help="Tools you can't or won't use. They'll be removed before ranking.",
                key=f"in_exclude_tools_{_fn}",
            )

            submitted = st.form_submit_button("Generate my blueprint")

    # Saved-blueprints panel (B.6) — rendered beneath the form, still in sidebar.
    render_saved_panel()

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
#
# NOTE: this used to be followed by a second, duplicate elapsed_seconds/
# log_event("results_shown")/log_event("llm_summary_generated") block — a
# merge-conflict artifact from 960cf01 ("Merge main into Gabi and resolve
# conflicts") where both sides of the merge had independently added the same
# Card 3.3 logging code. It double-logged every results_shown and
# llm_summary_generated event (confirmed live in data/telemetry.log — 6 of 20
# results_shown events were exact back-to-back duplicates), which understates
# Card P.14's funnel rates by roughly half. Removed — log each event once.
        log_event("llm_summary_generated", **result["llm_metrics"])
        st.session_state.result = result  # persist across reruns — see note below
        # Ash3-update v2.2: hide the sidebar so the fresh blueprint gets the whole
        # screen; the "Edit Builder" button (top-left) reopens it.
        st.session_state.sidebar_open = False
        # UI-v2 fix: rerun immediately so the hero's "result not in
        # st.session_state" gate (above) re-evaluates with the result now set.
        # Without this, on the submit run the hero had already rendered before
        # result existed, so it lingered beside the blueprint until the next
        # interaction. The results_shown/llm_summary_generated events above are
        # logged once, before this rerun, so telemetry is unaffected.
        st.rerun()

# Renders on every rerun as long as a result exists — not gated on `submitted`.
# See Card 1.4's "Why not render inside if submitted:" note for why this matters:
# Streamlit reruns the whole script on every interaction, and once Epic 3 adds
# buttons inside the results view, those reruns would otherwise wipe the blueprint.
if "result" in st.session_state:
    st.success("Blueprint ready — explore the tabs below.")
    render_blueprint(st.session_state.result)
    render_feedback_form()