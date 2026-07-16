"""
Card 2.4 — Estimate monthly cost for a shortlist of recommended tools.
Deliberately estimates ONE primary API + ONE assistant tool, never the sum of everything.
"""
from app.logic.pricing import PRICING, ILLUSTRATIVE_DISCLAIMER

# Seat-count assumption per org-size band — used only for seat-priced tools.
# Was a flat hand-picked constant per band; now grounded in the Stack Overflow
# Developer Survey (data/StackOverflow/results.csv, QID16/OrgSize x QID78/
# AISelect), computed by scripts/map_stackoverflow_orgsize.py. This is a
# seat-UTILIZATION PROXY (base headcount assumption x real AI-tool-adoption
# rate for that org-size band) — the survey has no billing/seats-licensed
# question at all, so this still isn't a real headcount lookup, just a less
# arbitrary one. See 18-Build-Guide-Updates-Epic1-2-v1.md, Update C, for the
# full band-mapping reasoning and source numbers.
#   solo:    4 headcount x 0.7782 adoption rate (n=1,321) = 3
#   startup: 20 headcount x 0.8203 adoption rate (n=4,306) = 16
#   smb:     150 headcount x 0.8199 adoption rate (n=5,215) = 123
#   mid:     600 headcount x 0.8018 adoption rate (n=6,731) = 481
#   ent:     3000 headcount x 0.7922 adoption rate (n=8,548) = 2377
ASSUMED_SEATS = {
    "solo": 3, "startup": 16, "smb": 123, "mid": 481, "ent": 2377,
}

# Fixed Ceiling Stopgap (Update D — decided with Gabi after a live test surfaced a
# €67,340/mo "assistant" figure for a Customer-Service-only query at "mid").
# ASSUMED_SEATS above is grounded in FULL-COMPANY headcount x adoption rate —
# realistic for "the whole company adopts this," but every query uses that same
# org-size seat count regardless of how narrow the requested workflow is, so a
# single-department ask (e.g. "Customer Service") gets costed as if the entire
# company rolled the tool out. We don't have per-workflow headcount-share data to
# scope this properly (that fuller fix — a workflow-fraction table — is Option A,
# left for a future card; see 18-Build-Guide-Updates-Epic1-2-v1.md, Update D).
# As an immediate stopgap, cap the seat count used for costing at a flat ceiling
# representing a plausible single-workflow team size, regardless of org-size band.
# This is a rough, hand-picked judgment call — not survey-derived, same caveat as
# ASSUMED_TOKEN_VOLUME_MM below. Bands already below the ceiling (solo, startup)
# are unaffected; smb/mid/ent are capped down to it.
SEAT_CEILING = 25

# Rough monthly token-volume assumption (in millions of tokens) per org-size band —
# used only for token-priced tools. Split roughly 3:1 input:output, a common ratio.
# NOTE: unlike ASSUMED_SEATS above, this one is NOT survey-derived — the Stack
# Overflow survey has no token/usage-volume question of any kind to ground it
# against (checked as part of Update C). Still a hand-picked illustrative
# constant; don't assume it shares the same evidentiary basis as the seat side.
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
        org_seats = ASSUMED_SEATS.get(org_size_key, ASSUMED_SEATS["startup"])
        seats = min(org_seats, SEAT_CEILING)
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


def estimate_cost(recommended_tools: list[str], org_size_key: str, budget: float | None = None) -> dict:
    """
    recommended_tools: ranked list of canonical tool ids (best match first).
    Picks the first token-priced tool as the "primary API" and the first
    seat-priced tool as the "assistant" — this is the "one + one, not the sum" rule.

    budget: the user's stated monthly budget in EUR (Update D). Optional — pass
    None (the default) for ad-hoc/test calls that don't have one; in that case
    total_monthly_eur is still computed but within_budget/budget_delta_eur stay
    None rather than guessing. This function only compares the total against the
    budget and reports the result — it never drops or swaps tools to force a fit,
    since the ranked list is Card 2.5's decision, not this card's.
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

    costed_amounts = [
        c["monthly_eur"] for c in (primary_api, assistant)
        if c is not None and c["monthly_eur"] is not None
    ]
    total_monthly_eur = round(sum(costed_amounts), 2) if costed_amounts else None

    within_budget = None
    budget_delta_eur = None
    if budget is not None and total_monthly_eur is not None:
        within_budget = total_monthly_eur <= budget
        budget_delta_eur = round(budget - total_monthly_eur, 2)  # negative when over budget

    return {
        "primary_api": primary_api,
        "assistant": assistant,
        "disclaimer": ILLUSTRATIVE_DISCLAIMER,
        "total_monthly_eur": total_monthly_eur,
        "budget": budget,
        "within_budget": within_budget,
        "budget_delta_eur": budget_delta_eur,
    }
