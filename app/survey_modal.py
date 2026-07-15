"""
Card 3.4 — Post-generation 1-5 trust rating.
Uses a plain inline form (simpler and more reliable across Streamlit versions
than a true modal dialog) placed right below the blueprint.
"""
import streamlit as st
from app.analytics.tracker import log_event


def render_trust_survey():
    if st.button("✅ I've copied my blueprint"):
        log_event("export_clicked")
        st.success("Noted — thanks!")

    st.markdown("### 🙋 Feedback")

    with st.form("trust_survey_form"):
        trust_score = st.slider(
            "How much do you trust this recommendation?",
            min_value=1, max_value=5, value=3,
            help="1 = not at all, 5 = completely",
        )
        net_value = st.radio(
            "Did this save you research time you'd otherwise spend on forums/Google?",
            ["Yes", "No"],
            horizontal=True,
        )
        survey_submitted = st.form_submit_button("Submit feedback")

    if survey_submitted:
        log_event("survey_submitted", trust_score=trust_score, net_value=net_value)
        st.success("Thanks — this helps us validate the project.")