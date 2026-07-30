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
    # Order and labels revised 2026-07-27 on first-real-user feedback: Summary
    # leads (the reader wants the answer in prose before the detail), then Cost —
    # the tester's next question was always "what does it cost" — then Stack,
    # Cases, Export, How it works. The "1 · / 2 · / 3 ·" numbering is gone from
    # both the tabs and the section headings: it implied a fixed reading order
    # that no longer matches the layout, and read as steps to complete.
    tab_summary, tab_cost, tab_stack, tab_cases, tab_export, tab_how = st.tabs(
        [
            ":material/summarize: Summary",
            ":material/payments: Cost",
            ":material/layers: Stack",
            ":material/library_books: Cases",
            ":material/download: Export",
            ":material/help: How it works",
        ]
    )

    with tab_summary:
        with st.container(key="aasa_prose_summary"):
            st.markdown("### Summary")
            st.write(result["summary_text"])
    with tab_cost:
        _render_cost_block(result["cost_forecast"])
    with tab_stack:
        _render_stack_block(result["recommended_stack"], result["matched_cases"],
                            result["tool_costs"], result.get("no_match_reason"),
                            result.get("cost_forecast"))
    with tab_cases:
        # Ash3-update: keyed container caps the reading width (CSS in intake.py)
        # so the case cards don't stretch full-bleed in wide layout.
        with st.container(key="aasa_prose_cases"):
            _render_case_references_block(result["matched_cases"], result["recommended_stack"],
                                          result.get("query", {}))
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
    # Ash4: don't announce "0 real X Y deployments matched" as if it were a
    # finding — on the no-match path the banner explains the limit instead.
    if result.get("no_match"):
        st.markdown(
            '<div class="aasa-banner"><b>NO EVIDENCE MATCH</b> — nothing in the '
            "case library was close enough to these inputs, so no stack is "
            "recommended. AASA only recommends tools it can trace to real "
            "deployments.</div>",
            unsafe_allow_html=True,
        )
        return
    # Ash4 (post-sweep): this line used to read "{n} real {industry} {workflow}
    # deployments matched" unconditionally. Retrieval is semantic, so it always
    # returns the nearest cases — and a full sweep of all 432 dropdown
    # combinations found that a large minority of them have ZERO cases in the
    # corpus (185 of 432, 43%, recounted 2026-07-30 against the committed store;
    # the sweep of 2026-07-27 said 205/47% before Gabi rebuilt the store on the
    # 28th — see PM Work/16-P22). For those the sentence was simply false: it
    # named an industry/workflow pair
    # that has no deployments at all. Returning the closest comparable evidence
    # is still useful, so we keep doing it — but we say which one it is.
    context = _evidence_sentence(query, n, result.get("exact_match_count"))
    st.markdown(
        f'<div class="aasa-banner"><b>DIRECTIONAL ONLY</b> — {context}'
        "Pricing is illustrative and compliance filtering is a shortlist, not "
        "certification. Verify before you commit budget.</div>",
        unsafe_allow_html=True,
    )


def _evidence_sentence(query: dict, n: int, exact: int | None) -> str:
    """
    One honest sentence about what the N matched cases actually are.

    exact is None only for blueprints saved before this field existed — in that
    case we say nothing rather than guess, because the old claim may be wrong.
    """
    industry, workflow = query.get("industry"), query.get("workflow")
    if not (industry and workflow):
        return ""
    ind_any = str(industry).lower().startswith("any")
    wf_any = str(workflow).lower().startswith("any")

    if exact is None:
        return f"{n} comparable deployments matched. "

    # No constraint given, so "exact match" is not a meaningful claim.
    if ind_any and wf_any:
        return f"{n} deployments matched from across the whole case library. "
    scope = (f"{industry} " if not ind_any else "") + ("" if wf_any else f"{workflow} ")

    if exact == 0:
        return (f"No direct {scope}deployments in the library — showing the "
                f"{n} closest comparable deployments from adjacent industries. ")
    if exact < n:
        return (f"{exact} real {scope}deployments matched, plus {n - exact} "
                "closest comparable from adjacent industries. ")
    return f"{n} real {scope}deployments matched. "


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
            # (fpdf2 not installed, an odd character, a bad result dict) would
            # otherwise crash the whole blueprint view, not just this button.
            # Degrade to a disabled button + a reason instead. The .md export
            # above is unaffected either way.
            try:
                pdf_bytes = blueprint_to_pdf(result)
            except ModuleNotFoundError:
                pdf_bytes, pdf_error = None, (
                    "PDF export needs the `fpdf2` package. Run "
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


def _costed_tool_ids(cost_forecast: dict | None) -> set:
    """
    Which tool ids actually appear in the Cost tab.

    The cost block deliberately prices ONE primary API + ONE assistant, never the
    whole stack — so most recommended tools carry no figure there. Testers read
    that as an inconsistency ("why is this priced and that isn't?"), so Block A
    now marks the two that are. Ids here are canonical (pipeline builds the
    label-ified copies separately, only for the LLM prompt).
    """
    if not cost_forecast:
        return set()
    ids = set()
    for slot in ("primary_api", "assistant"):
        entry = cost_forecast.get(slot)
        if entry and entry.get("tool"):
            ids.add(entry["tool"])
    return ids


def _render_stack_block(ranked_tools: list, matched_cases: list, tool_costs: dict,
                        no_match_reason: str | None = None,
                        cost_forecast: dict | None = None):
    st.markdown("### Recommended AI Stack")
    if not ranked_tools:
        # Ash4 (fix 2 of 3): say the RIGHT reason. This used to always blame the
        # privacy filter, which became actively misleading once the relevance
        # threshold could empty the list for a completely different reason.
        if no_match_reason == "no_relevant_cases":
            st.info("No deployments in the case library were close enough to this "
                    "combination of workflow and industry, so there is no "
                    "evidence-backed stack to show. Try a broader workflow or a "
                    "related industry.\n\n"
                    "This is a deliberate limit: AASA only recommends tools it can "
                    "point to real deployments for.")
        elif no_match_reason == "privacy_filter":
            st.info("Comparable deployments were found, but none of their tools are "
                    "governable enough for a regulated posture — so nothing cleared "
                    "the privacy filter. Try the standard posture to see what those "
                    "teams actually used.")
        else:
            st.info("No tools are available for this combination of inputs. Try "
                    "relaxing the privacy posture, removing a vendor exclusion, or "
                    "broadening the workflow.")
        return

    # UI-v2e: the pricing-type filter toggle (Recommended/Token/Seat/Compute/Free)
    # was removed per feedback — always show the full ranked recommendation.
    visible_tools = ranked_tools

    # Evidence count: how many matched cases mention each tool — this is the
    # "evidence bar" the task card asks for. Denominator is the total matched
    # case count, so the percentage reflects real-world evidence.
    total_cases = max(len(matched_cases), 1)
    costed_ids = _costed_tool_ids(cost_forecast)
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

        # The two tools carried into the Cost tab get a tinted row. Keyed
        # container -> CSS in intake.py's DARK_CSS (same .st-key- mechanism the
        # prose-width caps use). A text marker goes alongside the tint, because
        # a background colour alone is invisible to anyone not distinguishing it.
        is_costed = tool_id in costed_ids
        row = st.container(key=f"aasa_costed_row_{rank}") if is_costed else st.container()
        with row:
            _render_stack_row(rank, tool_id, label, tool_url, price_tag, price_label,
                              evidence_count, total_cases, matched_cases, is_costed)


def _render_stack_row(rank, tool_id, label, tool_url, price_tag, price_label,
                      evidence_count, total_cases, matched_cases, is_costed):
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
        # Was a static st.progress bar reading "Seen in N/M matched cases".
        # First-real-user feedback: the count invites the obvious next
        # question — WHICH cases? — and the bar couldn't answer it. Now an
        # expander that names them, with the source link for each, so the
        # evidence is one click away instead of a tab away. (Clicking through
        # to the Cases tab isn't possible: st.tabs has no programmatic
        # selection, so the cases are listed here in full instead.)
        _render_evidence_dropdown(tool_id, label, evidence_count, total_cases,
                                  matched_cases)
    with col2:
        st.caption(price_label)
        if is_costed:
            st.caption("↑ in cost forecast")


def _render_evidence_dropdown(tool_id: str, label: str, evidence_count: int,
                              total_cases: int, matched_cases: list):
    """The cases behind one recommendation, named rather than just counted."""
    pct = int(100 * evidence_count / max(total_cases, 1))
    if not evidence_count:
        # Can happen under a regulated posture: the tool is ranked from the
        # unfiltered set but every case citing it had its tools stripped.
        st.caption(f"Seen in 0/{total_cases} matched cases")
        return

    # Sorted, not just filtered — the caption below promises "best match first",
    # so the order has to be guaranteed here rather than inherited from upstream.
    using = sorted((c for c in matched_cases if tool_id in c.get("canonical_tools", [])),
                   key=lambda c: c.get("distance", float("inf")))
    with st.expander(f"Seen in {evidence_count}/{total_cases} matched cases  ·  {pct}%"):
        st.progress(pct / 100)
        st.caption(f"The deployments below are the evidence for recommending {label}. "
                   "Best match first.")
        for case in using:
            org = case.get("organization", "Unknown organisation")
            title = case.get("title", "")
            industry = case.get("industry", "")
            url = case.get("source_url", "")
            line = f"**{org}** — {title}" if title else f"**{org}**"
            st.markdown(line)
            bits = [b for b in (industry, f"[source]({url})" if url else "") if b]
            if bits:
                st.caption("  ·  ".join(bits))


def _render_cost_block(cost_forecast: dict):
    st.markdown("### Cost Forecast")
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


def _no_overlap_reason(case_tools: list, query: dict) -> str:
    """
    Why this case shows no "Stack used:" line — stated, not left blank.

    A case can be the closest semantic match and still share no tool with the
    recommendation, for three different reasons. The first user test showed that
    leaving this implicit reads as "this is a poor match", which is wrong: the
    case is still real evidence that comparable deployments exist.

    We can detect whether any tools survive, and whether the posture is
    regulated. We cannot tell a privacy-stripped case from a vendor-excluded one
    here (exclusions aren't echoed in `query`), so the wording covers both rather
    than guessing at one.
    """
    if case_tools:
        # Tools survived, they're just not in the top five.
        return ("Used different tools to the recommendation — matched on workflow "
                "and industry.")
    if query.get("privacy") == "regulated":
        return ("Its tools were filtered out by your regulated posture, so it "
                "doesn't feed the ranking — still a real comparable deployment.")
    return ("No tool in this case maps to our priced catalogue, so it doesn't feed "
            "the ranking — still a real comparable deployment.")


def _render_case_references_block(matched_cases: list, ranked_tools: list, query: dict):
    st.markdown("### Real Case References")
    if not matched_cases:
        st.info("No comparable cases matched — this can happen with very narrow inputs.")
        return

    count_label = st.radio(
        "Show", list(_CASE_COUNT_OPTIONS.keys()),
        horizontal=True, key="case_count", label_visibility="collapsed",
    )
    limit = _CASE_COUNT_OPTIONS[count_label]

    # Two-tier ordering, added after the first real user-test session.
    #
    # Distance alone was already correct — retrieval returns nearest-first and
    # every downstream step preserves it — but the tester read the top case as a
    # POOR match because it carried no "Stack used:" line. That line only appears
    # when a case shares a tool with the recommended stack, and a case can be the
    # closest semantic match while sharing nothing: its tools may have been
    # stripped by the privacy filter or a vendor exclusion, may not resolve to our
    # priced catalogue at all (tool-name coverage is 88.7%), or may simply be
    # different tools to the top five.
    #
    # So: cases that actually evidence the recommendation come first, each tier
    # still sorted nearest-first. The silent gap that caused the misreading is
    # also now filled in — every case without the line says why (see below).
    # Sorting alone would have hidden the information; the explanation is the
    # part that fixes the misreading.
    def _order_key(case):
        backs_recommendation = any(t in case.get("canonical_tools", []) for t in ranked_tools)
        return (0 if backs_recommendation else 1, case.get("distance", float("inf")))

    ordered_cases = sorted(matched_cases, key=_order_key)
    visible_cases = ordered_cases if limit is None else ordered_cases[:limit]
    st.caption("Closest matches first, with cases that back the recommended stack above "
               "those that don't.")

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
            else:
                # The gap that caused the misreading in the first user test. An
                # absent "Stack used:" line looked like a bad match, when it
                # actually means one of three specific things — so say which.
                st.caption(_no_overlap_reason(case_tools, query))
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