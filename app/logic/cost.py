"""
Card 2.4 — Estimate monthly cost for a shortlist of recommended tools.
Deliberately estimates ONE primary API + ONE assistant tool, never the sum of everything.
"""
from app.logic.pricing import PRICING, ILLUSTRATIVE_DISCLAIMER

# Rough seat-count assumption per org-size band — used only for seat-priced tools.
# These are directional assumptions for an illustrative estimate, not a real headcount lookup.
ASSUMED_SEATS = {
    "solo": 2, "startup": 8, "smb": 40, "mid": 200, "ent": 800,
}

# Rough monthly token-volume assumption (in millions of tokens) per org-size band —
# used only for token-priced tools. Split roughly 3:1 input:output, a common ratio.
ASSUMED_TOKEN_VOLUME_MM = {
    "solo": 2, "startup": 10, "smb": 50, "mid": 250, "ent": 1000,
}


def _cost_for_tool(canonical_id: str, org_size_key: str) -> dict:
    entry = PRICING.get(canonical_id)
    if entry is None:
        return {"tool": canonical_id, "model": "unknown", "monthly_eur": None,
                "note": "No pricing entry — add one to app/logic/pricing.py"}

    model = entry["model"]

    if model == "seat":
        seats = ASSUMED_SEATS.get(org_size_key, ASSUMED_SEATS["startup"])
        monthly = round(entry["seat_pm"] * seats, 2)
        return {"tool": canonical_id, "model": "seat", "monthly_eur": monthly,
                "assumption": f"{seats} seats x €{entry['seat_pm']}/seat/mo"}

    if model == "token":
        total_mm = ASSUMED_TOKEN_VOLUME_MM.get(org_size_key, ASSUMED_TOKEN_VOLUME_MM["startup"])
        input_mm, output_mm = total_mm * 0.75, total_mm * 0.25
        monthly = round(input_mm * entry["in_ppm"] + output_mm * entry["out_ppm"], 2)
        return {"tool": canonical_id, "model": "token", "monthly_eur": monthly,
                "assumption": f"~{total_mm}M tokens/mo (75% in / 25% out) at "
                               f"€{entry['in_ppm']}/€{entry['out_ppm']} per M tokens"}

    # compute or free tools: shown, not costed, per the technical work breakdown.
    return {"tool": canonical_id, "model": model, "monthly_eur": None,
            "note": entry.get("note", "Not costed in this MVP")}


def estimate_cost(recommended_tools: list[str], org_size_key: str) -> dict:
    """
    recommended_tools: ranked list of canonical tool ids (best match first).
    Picks the first token-priced tool as the "primary API" and the first
    seat-priced tool as the "assistant" — this is the "one + one, not the sum" rule.
    """
    primary_api, assistant = None, None

    for tool_id in recommended_tools:
        entry = PRICING.get(tool_id)
        if entry is None:
            continue
        if entry["model"] == "token" and primary_api is None:
            primary_api = _cost_for_tool(tool_id, org_size_key)
        elif entry["model"] == "seat" and assistant is None:
            assistant = _cost_for_tool(tool_id, org_size_key)

    return {
        "primary_api": primary_api,
        "assistant": assistant,
        "disclaimer": ILLUSTRATIVE_DISCLAIMER,
    }
