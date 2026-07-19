"""
Card 3.2 — Turn the blueprint dict into a plain-text block the user can copy.
"""
from app.logic.pricing import PRICING


def blueprint_to_text(result: dict) -> str:
    lines = ["=== AI-Assisted Stack Architect — Blueprint ===", ""]

    lines.append("RECOMMENDED STACK:")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"  {rank}. {label}")
    lines.append("")

    cost = result["cost_forecast"]
    lines.append("COST FORECAST (illustrative):")
    if cost.get("primary_api") and cost["primary_api"].get("monthly_eur") is not None:
        lines.append(f"  Primary API: €{cost['primary_api']['monthly_eur']:.2f}/mo")
    if cost.get("assistant") and cost["assistant"].get("monthly_eur") is not None:
        lines.append(f"  Assistant:   €{cost['assistant']['monthly_eur']:.2f}/mo")
    lines.append(f"  ({cost.get('disclaimer', '')})")
    lines.append("")

    lines.append("REAL CASE REFERENCES:")
    for case in result["matched_cases"][:4]:
        org = case.get("organization", "Unknown organisation")
        url = case.get("source_url", "")
        lines.append(f"  - {org} ({url})")
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(result.get("summary_text", ""))

    return "\n".join(lines)


def blueprint_to_markdown(result: dict) -> str:
    """Icebox B.1 (Build Guide 26) — board-ready plain-language one-pager.
    Deliberately non-technical: no tool ids, no token math, no jargon.
    Audience is the 'Visionary Outsider' persona — a non-technical CEO
    forwarding this to their board unedited."""
    cost = result["cost_forecast"]
    name = result.get("project_name") or "AI stack proposal"
    lines = [f"# {name}", ""]

    lines.append("## What we recommend")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"{rank}. **{label}**")
    lines.append("")

    lines.append("## What it costs (illustrative)")
    total = cost.get("total_monthly_eur")
    if total is not None:
        lines.append(f"Estimated **€{total:,.0f} per month** across the core services.")
    else:
        lines.append("Costs for this stack are usage-based — there is no fixed "
                     "monthly figure to quote. Budget against actual usage.")
    if cost.get("budget") is not None and cost.get("within_budget") is not None:
        if cost["within_budget"]:
            lines.append(f"This fits the stated budget of €{cost['budget']:,.0f}/mo "
                         f"with €{cost['budget_delta_eur']:,.0f}/mo to spare.")
        else:
            lines.append(f"⚠️ This exceeds the stated budget of €{cost['budget']:,.0f}/mo "
                         f"by €{abs(cost['budget_delta_eur']):,.0f}/mo — see caveats.")
    lines.append("")

    lines.append("## Why these tools")
    lines.append(f"Chosen from real, source-linked deployments by comparable "
                 f"organisations — {len(result['matched_cases'])} matched cases, "
                 f"top references below.")
    for case in result["matched_cases"][:3]:
        lines.append(f"- {case.get('organization', 'Unknown')} — {case.get('source_url', '')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(result.get("summary_text", ""))
    lines.append("")

    lines.append("## Caveats — read before committing budget")
    lines.append("- Prices come from a hand-curated table and are **illustrative**, "
                 "not quotes. Verify with vendors before signing anything.")
    lines.append("- Seat counts are assumptions from survey medians, capped for "
                 "single-workflow use — your real headcount will differ.")
    lines.append("- Compliance filtering is a directional shortlist, **not a certification**.")
    return "\n".join(lines)