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