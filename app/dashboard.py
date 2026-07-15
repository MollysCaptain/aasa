"""
Card 3.1 — Render the 3-block blueprint layout.
Block A: Recommended AI stack (ranked, evidence-labelled)
Block B: Cost forecast (primary API + assistant, clearly illustrative)
Block C: Real case references (source-linked)
"""
import streamlit as st
from app.logic.pricing import PRICING
from app.export import blueprint_to_text


def render_blueprint(result: dict):
    st.markdown("## 🧩 Your AI Stack Blueprint")

    _render_stack_block(result["recommended_stack"], result["matched_cases"])
    st.divider()
    _render_cost_block(result["cost_forecast"])
    st.divider()
    _render_case_references_block(result["matched_cases"])
    st.divider()
    st.markdown("### 📝 Summary")
    st.write(result["summary_text"])
    st.divider()
    st.markdown("### 📋 Export")
    blueprint_text = blueprint_to_text(result)
    st.code(blueprint_text, language=None)
    st.caption("Hover the code block above and click the copy icon in the top-right corner.")


def _render_stack_block(ranked_tools: list, matched_cases: list):
    st.markdown("### 1️⃣ Recommended AI Stack")
    if not ranked_tools:
        st.info("No tools cleared the privacy filter for this combination of inputs. "
                 "Try relaxing the privacy posture or broadening the workflow.")
        return

    # Evidence count: how many matched cases mention each tool — this is the
    # "evidence bar" the task card asks for.
    total_cases = max(len(matched_cases), 1)
    for rank, tool_id in enumerate(ranked_tools, start=1):
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        pricing_model = entry.get("model", "unknown")
        evidence_count = sum(1 for c in matched_cases if tool_id in c.get("canonical_tools", []))
        evidence_pct = int(100 * evidence_count / total_cases)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{rank}. {label}**  ·  `{pricing_model}`-priced")
            st.progress(evidence_pct / 100, text=f"Seen in {evidence_count}/{total_cases} matched cases")
        with col2:
            st.caption(pricing_model.upper())


def _render_cost_block(cost_forecast: dict):
    st.markdown("### 2️⃣ Illustrative Cost Forecast")
    st.caption(cost_forecast.get("disclaimer", ""))

    primary = cost_forecast.get("primary_api")
    assistant = cost_forecast.get("assistant")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Primary API**")
        if primary and primary.get("monthly_eur") is not None:
            st.metric(primary["tool"], f"€{primary['monthly_eur']:.2f}/mo")
            st.caption(primary.get("assumption", ""))
        else:
            st.caption("No token-priced tool in the top recommendations.")
    with col2:
        st.markdown("**Assistant / SaaS**")
        if assistant and assistant.get("monthly_eur") is not None:
            st.metric(assistant["tool"], f"€{assistant['monthly_eur']:.2f}/mo")
            st.caption(assistant.get("assumption", ""))
        else:
            st.caption("No seat-priced tool in the top recommendations.")


def _render_case_references_block(matched_cases: list):
    st.markdown("### 3️⃣ Real Case References")
    if not matched_cases:
        st.info("No comparable cases matched — this can happen with very narrow inputs.")
        return

    for case in matched_cases[:4]:  # show up to 4, per the prototype's own convention
        org = case.get("organization", "Unknown organisation")
        title = case.get("title", "")
        industry = case.get("industry", "")
        url = case.get("source_url", "")
        outcomes = case.get("outcomes", "")
        with st.container(border=True):
            st.markdown(f"**{org}** — {title}")
            st.caption(industry)
            # "outcomes" is bullet-pointed prose from the dataset's own
            # Outcomes & Benefits column (see 18-Build-Guide-Updates-Epic1-2-v1.md,
            # Update B, for how this got wired through from Card 2.2/pipeline.py).
            # Comparative review of a second prototype (aasa-proto2.lovable.app)
            # showed reported outcomes per case in its trace step — this is our
            # equivalent. Collapsed by default so the block stays scannable at 4 cases.
            if outcomes:
                with st.expander("Reported outcomes"):
                    st.markdown(outcomes)
            if url:
                st.markdown(f"[Source]({url})")