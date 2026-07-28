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
#
# READ THIS BEFORE "FIXING" THE NUMBERS ABOVE (updated 2026-07-27) --------------
# The org-size band LABELS changed after the first real user-test session
# (1-10 / 11-100 / 101-200 / 201-1,000 / 1,000+), so the base headcounts quoted
# above — 4 / 20 / 150 / 600 / 3000 — no longer correspond to the band edges.
# The values were deliberately NOT re-derived, for a reason worth stating:
#
#   what these numbers represent is the size of the TEAM ADOPTING THE AI STACK,
#   not the size of the organisation.
#
# Someone asking AASA for a stack is speccing it for a team, and that team is a
# small fraction of the company at every band above solo. 16 seats inside an
# 11-100 person company is a realistic adopting team; 82 (the band top x
# adoption rate) would describe near-total company rollout, which is not the
# question the product answers. SEAT_CEILING below already encodes exactly this
# reasoning for the larger bands — this comment simply makes it the stated basis
# for the whole seat side rather than an after-the-fact cap.
#
# Consequence to keep in view: the survey figures above now ground the ADOPTION
# RATE only, not the headcount. The headcounts are our judgement. Do not describe
# the seat side as fully survey-derived in the write-up.
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
#
# WHY THIS SCALES WHEN SEATS DO NOT (documented 2026-07-27) ---------------------
# Seats are capped at SEAT_CEILING because a licence is per person and the
# adopting team stays small. Token spend is not per person — it tracks how much
# work is pushed through the API, and that does grow with the organisation even
# when the team driving it doesn't: larger retrieval corpora, more documents per
# run, longer context, batch and scheduled jobs, more integrations calling the
# same endpoint. So a 25-person team at an enterprise can legitimately consume
# far more tokens than a 16-person team at a startup.
#
# Being straight about the weakness: that argument justifies the DIRECTION of the
# scaling, not its size. The spread here is 500x solo-to-enterprise (EUR 8.75 vs
# EUR 4,375/mo on a GPT-4o-class API), and nothing in our evidence fixes the
# multiplier at 500x rather than 50x. It is the single least-grounded number in
# the cost model, and because the primary-API figure is usually token-priced it
# is also the most prominent number on the Cost tab. Recorded in
# PM & Ethics/Known-Limitations-v1.md rather than quietly left in the code.
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


def estimate_all_tool_costs(recommended_tools: list[str], org_size_key: str) -> dict:
    """
    Update E (Card 3.1 UI support) — unlike estimate_cost()'s "one primary API +
    one assistant, never the sum" rule, this costs EVERY tool in the ranked list,
    keyed by canonical id. Block A uses this to show a per-tool monthly price
    instead of just the two winning picks. Reuses _cost_for_tool() exactly as-is
    (same seat ceiling, same token-volume assumption, same illustrative caveats)
    — this is a display convenience for browsing the ranked list, not a second
    pricing model, and it does not change what estimate_cost() decides is the
    blueprint's headline primary_api/assistant pair.
    """
    return {tool_id: _cost_for_tool(tool_id, org_size_key) for tool_id in recommended_tools}
