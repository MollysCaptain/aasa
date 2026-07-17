"""
Card 3.1 — Render the 3-block blueprint layout.
Block A: Recommended AI stack (ranked, evidence-labelled)
Block B: Cost forecast (primary API + assistant, clearly illustrative)
Block C: Real case references (source-linked)
"""
import streamlit as st
from app.logic.pricing import PRICING
from app.export import blueprint_to_text
from app.survey_modal import render_copy_confirmation


def render_blueprint(result: dict):
    st.markdown("## 🧩 Your AI Stack Blueprint")

    _render_stack_block(result["recommended_stack"], result["matched_cases"], result["tool_costs"])
    st.divider()
    _render_cost_block(result["cost_forecast"])
    st.divider()
    _render_case_references_block(result["matched_cases"], result["recommended_stack"])
    st.divider()
    st.markdown("### 📝 Summary")
    st.write(result["summary_text"])
    st.divider()
    st.markdown("### 📋 Export")
    blueprint_text = blueprint_to_text(result)
    st.caption("Hover the code block below and click the copy icon in the top-right corner.")
    st.code(blueprint_text, language=None)
    render_copy_confirmation()
    st.divider()
    _render_methodology_block()


# Update E — fallback text for the grey caption when a tool has no monthly_eur
# figure at all (compute/free-priced, or missing a pricing entry outright).
# token/seat tools always have a monthly_eur (see _cost_for_tool()), so this
# only ever applies to compute/free/unknown.
_PRICE_FALLBACK_LABELS = {
    "compute": "Pay-as-you-go",
    "free": "Free / Self-hosted",
}

# Toggle options for Block A (Update E) — maps the displayed pill label to the
# PRICING "model" value it filters on. "Recommended" (the default) shows the
# full ranked list, unfiltered, exactly as before this update.
_STACK_FILTER_OPTIONS = {
    "Recommended": None,
    "Token": "token",
    "Seat": "seat",
    "Compute": "compute",
    "Free": "free",
}


def _render_stack_block(ranked_tools: list, matched_cases: list, tool_costs: dict):
    st.markdown("### 1️⃣ Recommended AI Stack")
    if not ranked_tools:
        st.info("No tools cleared the privacy filter for this combination of inputs. "
                 "Try relaxing the privacy posture or broadening the workflow.")
        return

    filter_label = st.radio(
        "Filter by pricing type", list(_STACK_FILTER_OPTIONS.keys()),
        horizontal=True, key="stack_filter", label_visibility="collapsed",
    )
    filter_model = _STACK_FILTER_OPTIONS[filter_label]

    if filter_model is None:
        visible_tools = ranked_tools
    else:
        visible_tools = [t for t in ranked_tools if PRICING.get(t, {}).get("model") == filter_model]

    if not visible_tools:
        st.info(f"None of the current recommendations are {filter_label.lower()}-priced. "
                 "Try a different filter or \"Recommended\" for the full list.")
        return

    # Evidence count: how many matched cases mention each tool — this is the
    # "evidence bar" the task card asks for. Denominator stays the total matched
    # case count regardless of which filter is active, so the percentage always
    # reflects real-world evidence, not just evidence within the filtered subset.
    total_cases = max(len(matched_cases), 1)
    for rank, tool_id in enumerate(visible_tools, start=1):
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        pricing_model = entry.get("model", "unknown")
        evidence_count = sum(1 for c in matched_cases if tool_id in c.get("canonical_tools", []))
        evidence_pct = int(100 * evidence_count / total_cases)

        cost_entry = tool_costs.get(tool_id, {})
        monthly = cost_entry.get("monthly_eur")
        if monthly is not None:
            price_label = f"€{monthly:.2f}/mo"
        else:
            price_label = _PRICE_FALLBACK_LABELS.get(pricing_model, "Pricing unavailable")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{rank}. {label}**  ·  `{pricing_model}`-priced")
            st.progress(evidence_pct / 100, text=f"Seen in {evidence_count}/{total_cases} matched cases")
        with col2:
            st.caption(price_label)


def _render_cost_block(cost_forecast: dict):
    st.markdown("### 2️⃣ Cost Forecast")
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


# Update F — count-toggle options for Block C. "All" is handled as None (no
# slice limit) rather than a literal len(matched_cases), since that length
# varies per query. NOTE: this toggle only affects the on-screen display —
# app/export.py's plain-text export deliberately stays fixed at 4 regardless
# of what's selected here, so the exported blueprint is always predictable.
_CASE_COUNT_OPTIONS = {"4": 4, "8": 8, "All": None}


def _render_case_references_block(matched_cases: list, ranked_tools: list):
    st.markdown("### 3️⃣ Real Case References")
    if not matched_cases:
        st.info("No comparable cases matched — this can happen with very narrow inputs.")
        return

    count_label = st.radio(
        "Show", list(_CASE_COUNT_OPTIONS.keys()),
        horizontal=True, key="case_count", label_visibility="collapsed",
    )
    limit = _CASE_COUNT_OPTIONS[count_label]
    visible_cases = matched_cases if limit is None else matched_cases[:limit]

    for case in visible_cases:
        org = case.get("organization", "Unknown organisation")
        title = case.get("title", "")
        industry = case.get("industry", "")
        url = case.get("source_url", "")
        outcomes = case.get("outcomes", "")
        case_tools = case.get("canonical_tools", [])
        # Update F — "Stack used": only the tool(s) this case shares with the
        # CURRENT recommended_stack, not its full raw tool list, so the line
        # visibly ties this case back to the specific recommendation it's
        # evidence for (rather than every tool the case happened to mention).
        # Kept in recommended_stack's rank order for readability. Omitted
        # entirely if there's no overlap, rather than showing an empty line.
        used_tools = [t for t in ranked_tools if t in case_tools]
        with st.container(border=True):
            st.markdown(f"**{org}** — {title}")
            st.caption(industry)
            # "outcomes" is bullet-pointed prose from the dataset's own
            # Outcomes & Benefits column (see 18-Build-Guide-Updates-Epic1-2-v1.md,
            # Update B, for how this got wired through from Card 2.2/pipeline.py).
            # Comparative review of a second prototype (aasa-proto2.lovable.app)
            # showed reported outcomes per case in its trace step — this is our
            # equivalent. Collapsed by default so the block stays scannable.
            if outcomes:
                with st.expander("Reported outcomes"):
                    st.markdown(outcomes)
            if used_tools:
                used_labels = ", ".join(PRICING.get(t, {}).get("label", t) for t in used_tools)
                st.caption(f"Stack used: {used_labels}")
            if url:
                st.markdown(f"[Source]({url})")


def _render_methodology_block():
    """
    Update G — "How the recommendation is made," inserted between Export and
    Feedback (see render_blueprint()). Static, hand-written content — mirrors
    the structure of a comparable section in a second prototype
    (aasa-proto2.lovable.app) that was reviewed during Epic 1/2, but written
    with our own real pipeline facts and dataset numbers, not copied from theirs.
    """
    st.markdown("### 🔍 How the recommendation is made")
    st.caption(
        "No black box. The pipeline is deterministic filtering and evidence-ranking "
        "first — the LLM only ever writes the summary paragraph; it never invents "
        "the tools or the prices."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**01 · Retrieve**")
        st.caption(
            "Your workflow and industry select comparable real deployments from a "
            "curated library of 3,023 real-world AI case studies, via semantic "
            "search over a Chroma vector store. Your privacy posture applies a "
            "deterministic hard filter before anything is ranked."
        )
    with col2:
        st.markdown("**02 · Rank & price**")
        st.caption(
            "Tool names are normalised against real case data (88.7% of cases "
            "resolve to a canonical tool id) and cross-referenced against a "
            "hand-built pricing table that distinguishes per-seat SaaS from "
            "per-token APIs, usage-billed platforms, and free/self-hosted tools."
        )
    with col3:
        st.markdown("**03 · Trace**")
        st.caption(
            "Every recommended tool links back to the real cases that used it, "
            "with their reported outcomes and original source URLs, so you can "
            "verify the evidence yourself rather than take the summary's word for it."
        )

    with st.container(border=True):
        st.markdown("**Known limitations (what this MVP does not do)**")
        st.markdown(
            "- Pricing is manually curated and illustrative — it is not a live feed "
            "and may be out of date. Always confirm on the vendor's own pricing page.\n"
            "- Compliance filtering is *directional*. AASA does not certify HIPAA, "
            "GDPR, or SOC 2 fitness — treat the \"regulated\" filter as a shortlist, "
            "not a sign-off.\n"
            "- The case library reflects real-world adoption patterns, which skew "
            "toward large-scale enterprise deployments — narrower or newer use cases "
            "may be underrepresented.\n"
            "- Seat and usage assumptions are grounded in population-level survey "
            "data (Stack Overflow Developer Survey), not a per-case or per-company "
            "headcount lookup — see the Cost Forecast disclaimer for the same caveat."
        )