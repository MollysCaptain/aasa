"""
Card 3.1 — Render the 3-block blueprint layout.
Block A: Recommended AI stack (ranked, evidence-labelled)
Block B: Cost forecast (primary API + assistant, clearly illustrative)
Block C: Real case references (source-linked)
"""
import streamlit as st
from app.logic.pricing import PRICING
from app.logic.scaffold import build_scaffold
from app.export import blueprint_to_text, blueprint_to_markdown, blueprint_to_pdf
from app.survey_modal import render_copy_confirmation
from app.saved_blueprints import render_save_button
from app.analytics.tracker import log_event

def _clear_blueprint():
    """Clear's on_click callback. v2.6: bumps form_nonce so the intake widgets
    (keyed in_<name>_<nonce> in intake.py) get fresh keys next run and reset to
    their DEFAULTS — the reliable reset for widgets inside an st.form, where
    simply deleting the keys doesn't work (the frontend retains the values).
    Also drops the result and reopens the sidebar with the form expanded."""
    st.session_state.pop("result", None)
    st.session_state["form_nonce"] = st.session_state.get("form_nonce", 0) + 1
    st.session_state["sidebar_open"] = True
    st.session_state["_user_collapsed"] = False
    st.session_state["build_open"] = True


def render_blueprint(result: dict):
    # B.5 (Build Guide 24) — optional project name replaces the generic title.
    # Restyle round: emojis dropped from all blueprint headings (team decision,
    # Lovable-parity) — the theme carries the visual identity now.
    st.markdown(f"## {result.get('project_name') or 'Your AI Stack Blueprint'}")

    # Status chips + directional banner stay ABOVE the tabs — they're the
    # at-a-glance summary (matched-case count, regulated notice, budget fit) and
    # should be visible no matter which tab is open. UI-v2f: chips row back on
    # top, banner directly beneath it (order restored per feedback).
    _render_status_chips(result)
    _render_directional_banner(result)

    # UI-v2e: Clear moved up here, right-aligned just above the tab bar (was in
    # the Export action row). Popping "result" + rerun returns to the empty
    # state. B.6 note: it pops "result" ONLY — it never touches
    # st.session_state.saved_blueprints, so clearing the view keeps saved work.
    _, clear_col = st.columns([5, 1])
    with clear_col:
        # Ash3-update v2.5: Clear now resets the intake form to defaults too, via
        # an on_click callback (reliable widget-reset pattern — no st.rerun here).
        st.button("Clear", key="clear_result", on_click=_clear_blueprint)

    # Change 2 (UI-v2 · reduce-scroll): the blueprint used to be six sections
    # stacked down one long column (Stack → Cost → Cases → Summary → Export →
    # How it works), separated by dividers — the main cause of the "everything
    # on one page / endless scrolling" tutor feedback. They're now tabs, so the
    # whole blueprint fits one screen and the user picks what to look at.
    # Nothing about the blocks themselves changed — each _render_* function is
    # called exactly as before, just inside its tab. Remaining widget keys
    # (case_count, clear_result, copy_confirm) are unchanged, so session state
    # and the DARK_CSS class hooks keep working.
    # UI-v2b: Material icons (Streamlit's built-in :material/: set — no emoji,
    # consistent with the team's de-emoji styling) + prominence CSS in
    # intake.py's DARK_CSS make the tab bar clearly the primary navigation.
    # NOTE: :material/...: labels need a Streamlit build that renders Material
    # Symbols in tab labels (the project's current build does). If they ever
    # show as literal ":material/..." text, the Streamlit version is too old.
    tab_stack, tab_cost, tab_cases, tab_summary, tab_export, tab_how = st.tabs(
        [
            ":material/layers: 1 · Stack",
            ":material/payments: 2 · Cost",
            ":material/library_books: 3 · Cases",
            ":material/summarize: Summary",
            ":material/download: Export",
            ":material/help: How it works",
        ]
    )

    with tab_stack:
        _render_stack_block(result["recommended_stack"], result["matched_cases"],
                            result["tool_costs"])
    with tab_cost:
        _render_cost_block(result["cost_forecast"])
    with tab_cases:
        # Ash3-update: keyed container caps the reading width (CSS in intake.py)
        # so the case cards don't stretch full-bleed in wide layout.
        with st.container(key="aasa_prose_cases"):
            _render_case_references_block(result["matched_cases"], result["recommended_stack"],
                                          result.get("query", {}))
    with tab_summary:
        with st.container(key="aasa_prose_summary"):
            st.markdown("### Summary")
            st.write(result["summary_text"])
    with tab_export:
        st.markdown("### Export")
        blueprint_text = blueprint_to_text(result)
        st.caption("Hover the code block below and click the copy icon in the top-right corner.")
        st.code(blueprint_text, language=None)
        _render_action_row(result)
    with tab_how:
        with st.container(key="aasa_prose_how"):
            _render_methodology_block()


# --- Lovable-parity UI round: status chips + banner -------------------------
# Mirrors the second prototype's (aasa-proto2.lovable.app) chip row under the
# action buttons: matched-case count, regulated-filter notice, budget fit.
# Styling classes (.aasa-chip / -ok / -warn, .aasa-banner) live in intake.py's
# DARK_CSS block, which is injected before this ever renders.

def _render_status_chips(result: dict):
    query = result.get("query", {})
    cost = result["cost_forecast"]

    chips = [f'<span class="aasa-chip">{len(result["matched_cases"])} MATCHED CASES</span>']
    if query.get("privacy") == "regulated":
        chips.append('<span class="aasa-chip">REGULATED POSTURE · '
                     'SENSITIVE VENDORS FILTERED</span>')
    if cost.get("budget") is not None and cost.get("within_budget") is not None:
        if cost["within_budget"]:
            chips.append('<span class="aasa-chip aasa-chip-ok">WITHIN BUDGET</span>')
        else:
            chips.append('<span class="aasa-chip aasa-chip-warn">OVER BUDGET</span>')
    st.markdown(" ".join(chips), unsafe_allow_html=True)


def _render_directional_banner(result: dict):
    query = result.get("query", {})
    n = len(result["matched_cases"])
    context = ""
    if query.get("industry") and query.get("workflow"):
        context = f"{n} real {query['industry']} {query['workflow']} deployments matched. "
    st.markdown(
        f'<div class="aasa-banner"><b>DIRECTIONAL ONLY</b> — {context}'
        "Pricing is illustrative and compliance filtering is a shortlist, not "
        "certification. Verify before you commit budget.</div>",
        unsafe_allow_html=True,
    )


# --- Lovable-parity UI round: action row (guides 25 + 26 + 27) --------------
# UI-v2e: four EQUAL columns for even spacing. Clear moved out (now above the
# tabs); "I've copied my blueprint" moved in where Clear used to be.

def _render_action_row(result: dict):
    col0, col1, col2, col3 = st.columns(4)
    with col0:
        render_save_button(result)
    with col1:
        # B.8: one "Download" popover holding both formats, so adding the PDF
        # didn't need a 5th column (the labels are already tight at the 440px
        # sidebar width).
        with st.popover("Download"):
            st.caption("Same blueprint, two formats.")
            if st.download_button(
                "Markdown (.md)",
                blueprint_to_markdown(result),
                file_name="aasa-cost-onepager.md",
                mime="text/markdown",
            ):
                log_event("onepager_downloaded")

            # B.8 hardening: st.download_button needs its bytes up-front, so the
            # PDF is built on every rerun — which means ANY failure in there
            # (reportlab not installed, an odd character, a bad result dict) would
            # otherwise crash the whole blueprint view, not just this button.
            # Degrade to a disabled button + a reason instead. The .md export
            # above is unaffected either way.
            try:
                pdf_bytes = blueprint_to_pdf(result)
            except ModuleNotFoundError:
                pdf_bytes, pdf_error = None, (
                    "PDF export needs the `reportlab` package. Run "
                    "`pip install -r requirements.txt`, then restart the app."
                )
            except Exception as exc:                     # noqa: BLE001 - see comment above
                pdf_bytes, pdf_error = None, f"PDF could not be generated ({type(exc).__name__})."

            if pdf_bytes is not None:
                if st.download_button(
                    "PDF (.pdf)",
                    pdf_bytes,
                    file_name="aasa-blueprint.pdf",
                    mime="application/pdf",
                ):
                    log_event("pdf_downloaded")
            else:
                st.button("PDF (.pdf)", disabled=True, key="pdf_unavailable")
                st.caption(pdf_error)
    with col2:
        with st.popover(".env scaffold"):
            scaffold_text = build_scaffold(result["recommended_stack"])
            st.caption("Copy-paste starting point — variable names only, keys left blank.")
            st.code(scaffold_text, language="bash")
            if st.download_button(
                "Download .env scaffold", scaffold_text,
                file_name="aasa-scaffold.env", mime="text/plain",
            ):
                log_event("scaffold_downloaded")
    with col3:
        render_copy_confirmation()


# Update E — fallback text for the grey caption when a tool has no monthly_eur
# figure at all (compute/free-priced, or missing a pricing entry outright).
# token/seat tools always have a monthly_eur (see _cost_for_tool()), so this
# only ever applies to compute/free/unknown.
_PRICE_FALLBACK_LABELS = {
    "compute": "Pay-as-you-go",
    "free": "Free / Self-hosted",
}

# UI-v2c — display text for the orange pricing-model tag in Block A. Rendered
# as one styled token (no separate "-priced" add-on). Team wording decision:
# "open source" (not "free-priced") and "usage-based" (not "compute-priced");
# token/seat keep the "-priced" form. Falls back to "<model>-priced" for any
# unexpected model value.
_PRICE_TAG_LABELS = {
    "token": "token-priced",
    "seat": "seat-priced",
    "compute": "usage-based",
    "free": "open source",
}

# Lovable-parity UI round — hand-written one-line rationales for the tools that
# most often reach Block A (mirrors the prototype's per-tool "why:" line, e.g.
# "why: Regulated industries that already run on IBM and need audit trails.").
# Anything not listed falls back to an evidence-count template, so this dict
# never needs to be complete — only helpful. Keep each under ~90 chars.
TOOL_RATIONALE = {
    "azure-platform":   "Enterprise default where Microsoft is already the IT estate.",
    "azure-openai":     "OpenAI models with Azure's enterprise governance and DPAs.",
    "aws-platform":     "Broadest managed-service catalogue for teams already on AWS.",
    "aws-bedrock":      "Multi-model API behind AWS security and compliance tooling.",
    "google-cloud":     "Strong data/ML tooling for teams in the Google ecosystem.",
    "vertex-ai":        "Managed Gemini + custom-model hosting with enterprise controls.",
    "gemini":           "Fast, low-friction assistant adoption inside Google Workspace.",
    "gemini-workspace": "Workspace-native assistant with enterprise data-handling terms.",
    "gemini-api":       "Direct Gemini API access for custom builds on a budget.",
    "ms-copilot":       "Assistant embedded in the Office apps staff already use daily.",
    "ms365-suite":      "Productivity backbone AI features attach to with zero migration.",
    "openai-api":       "De-facto standard general-purpose LLM API; largest ecosystem.",
    "claude-api":       "Long-context, safety-focused API popular for text-heavy work.",
    "ibm-watsonx":      "Regulated industries that already run on IBM and need audit trails.",
    "nvidia":           "The compute layer under nearly every serious in-house AI build.",
    "huggingface":      "Open-model hub for teams that want control without vendor lock-in.",
    "langchain":        "Most common glue framework in real retrieval/agent deployments.",
    "chroma":           "Lightweight local vector store — no infra, no data leaves the box.",
    "llama":            "Open weights for teams that must self-host for privacy or cost.",
    "salesforce-einstein": "CRM-native AI where Salesforce already owns the pipeline.",
    "github-copilot":   "Fastest-payback seat licence for any team that writes code.",
}


def _why_for_tool(tool_id: str, evidence_count: int, total_cases: int) -> str:
    rationale = TOOL_RATIONALE.get(tool_id)
    if rationale:
        return rationale
    return (f"Used by {evidence_count} of {total_cases} comparable deployments "
            "in your matched cases.")


def _render_stack_block(ranked_tools: list, matched_cases: list, tool_costs: dict):
    st.markdown("### 1 · Recommended AI Stack")
    if not ranked_tools:
        st.info("No tools cleared the privacy filter for this combination of inputs. "
                 "Try relaxing the privacy posture or broadening the workflow.")
        return

    # UI-v2e: the pricing-type filter toggle (Recommended/Token/Seat/Compute/Free)
    # was removed per feedback — always show the full ranked recommendation.
    visible_tools = ranked_tools

    # Evidence count: how many matched cases mention each tool — this is the
    # "evidence bar" the task card asks for. Denominator is the total matched
    # case count, so the percentage reflects real-world evidence.
    total_cases = max(len(matched_cases), 1)
    for rank, tool_id in enumerate(visible_tools, start=1):
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        pricing_model = entry.get("model", "unknown")
        tool_url = entry.get("url")   # UI-v2c — official homepage, if known
        price_tag = _PRICE_TAG_LABELS.get(pricing_model, f"{pricing_model}-priced")
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
            # Tool name in green (.aasa-stack-name). UI-v2c: the whole name is a
            # hyperlink to the tool's official site when we have a URL (falls
            # back to a plain span otherwise), and the pricing-model tag is now
            # one orange .aasa-price-tag token ("seat-priced" / "token-priced" /
            # "usage-based" / "open source" — single font, no split "-priced"
            # add-on) so it reads as one unit and stands apart from the name.
            if tool_url:
                name_html = (f'<a class="aasa-stack-name" href="{tool_url}" '
                             f'target="_blank" rel="noopener">{rank}. {label}</a>')
            else:
                name_html = f'<span class="aasa-stack-name">{rank}. {label}</span>'
            st.markdown(
                f'{name_html}  ·  <span class="aasa-price-tag">{price_tag}</span>',
                unsafe_allow_html=True,
            )
            # Lovable-parity UI round — per-tool "why:" rationale line.
            st.markdown(
                f'<span class="aasa-why">why:</span> '
                f'{_why_for_tool(tool_id, evidence_count, total_cases)}',
                unsafe_allow_html=True,
            )
            st.progress(evidence_pct / 100, text=f"Seen in {evidence_count}/{total_cases} matched cases")
        with col2:
            st.caption(price_label)


def _render_cost_block(cost_forecast: dict):
    st.markdown("### 2 · Cost Forecast")
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


def _render_case_references_block(matched_cases: list, ranked_tools: list, query: dict):
    st.markdown("### 3 · Real Case References")
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
            # Lovable-parity UI round — per-case "why:" line explaining what this
            # case has in common with the query. Built only from facts we can
            # verify (industry equality, stack overlap); the semantic-match
            # fallback is honest about being a similarity match, not a claim.
            why_bits = []
            if industry and query.get("industry") and \
                    industry.strip().lower() == query["industry"].strip().lower():
                why_bits.append(f"same industry as yours ({industry})")
            if used_tools:
                why_bits.append("deployed tool(s) from your recommended stack")
            if not why_bits:
                workflow = query.get("workflow", "your workflow")
                why_bits.append(f'closest semantic match to "{workflow}" deployments')
            st.markdown(
                f'<span class="aasa-why">why:</span> {" · ".join(why_bits)}',
                unsafe_allow_html=True,
            )
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
    st.markdown("### How the recommendation is made")
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
        st.markdown("**Known limitations at this stage** (what a 4-week MVP does not do *yet*)")
        st.caption(
            "These are current constraints of an early prototype — several ease as "
            "the case library and pricing data grow (see the roadmap)."
        )
        st.markdown(
            "- **At this stage**, pricing is manually curated and illustrative — it is "
            "not a live feed and may be out of date, so always confirm on the vendor's "
            "own pricing page. A periodic pricing sync is planned.\n"
            "- **In this version**, compliance filtering is a *directional* shortlist — "
            "AASA does not certify HIPAA, GDPR, or SOC 2 fitness, so treat the "
            "\"regulated\" filter as a starting point, not a sign-off.\n"
            "- The case library **currently** reflects real-world adoption patterns, "
            "which skew toward large-scale enterprise deployments. As the library grows, "
            "coverage of narrower and newer use cases improves.\n"
            "- Seat and usage assumptions are **currently** grounded in population-level "
            "survey data (Stack Overflow Developer Survey), not a per-case or per-company "
            "headcount lookup — a workflow-scoped refinement is already proposed. See the "
            "Cost Forecast disclaimer for the same caveat."
        )

    # Card P.8 — "About this data" bias/dataset-skew disclosure, surfaced
    # in-product (not just filed in docs/model-card.md). Visibility is the point.
    with st.expander("ℹ️ About this data — bias & dataset skew"):
        st.markdown(
            "AASA ranks tools by how often they appear in a library of **3,023 "
            "real AI deployments** — so recommendations reflect *real-world "
            "adoption*, not an even sample of every tool.\n\n"
            "- The data **skews toward enterprise cloud & productivity AI**: the "
            "top 5 tools (Azure, Gemini, Azure OpenAI, Google Cloud, AWS) make up "
            "**~45% of all tool mentions**. Smaller or newer vendors are "
            "systematically under-recommended even when well-suited.\n"
            "- Cases span **24 industries**, but Technology, Financial Services & "
            "Healthcare alone are **~40% of the data** — thinner industries have "
            "less evidence behind them.\n"
            "- There is **no organisation-size field** in the case data; Org Size "
            "affects only the illustrative cost, never which cases match.\n\n"
            "Full details, figures, and fairness notes are in the project's "
            "**model card** (`docs/model-card.md`)."
        )