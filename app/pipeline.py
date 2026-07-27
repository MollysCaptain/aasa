"""
The single entry point that turns validated form inputs into a blueprint.
Epic 2 is now wired in for real:
  Step 1 (normalise/retrieve) <- Cards 2.1, 2.2
  Step 2 (privacy filter)     <- Card 2.5
  Step 3 (cost)               <- Cards 2.3, 2.4
  Step 4 (LLM summary)        <- Card 2.6
"""
import chromadb
from chromadb.utils import embedding_functions
from app.logic.filter import apply_privacy_filter, apply_vendor_exclusions, rank_tools_by_frequency
from app.logic.cost import estimate_cost, estimate_all_tool_costs
from app.logic.prompt import generate_summary
from app.logic.pricing import PRICING

# Must match the embedding function named in Card 2.2 Step 2's embed_cases.py —
# Chroma needs the same embedding function every time this collection is opened.
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_chroma_client = chromadb.PersistentClient(path="./chroma_store")
_collection = _chroma_client.get_collection("aasa_cases", embedding_function=_embedding_fn)

# Relevance threshold (Card P.16 roadmap fix — retrieval previously had no
# cutoff at all, so an obscure workflow/industry combo would still claim
# "15 real deployments matched" regardless of true relevance).
#
# Chroma's default distance metric is L2 (no hnsw:space set at collection
# creation — see scripts/embed_cases.py), so this value is calibrated
# against REAL measured distances (tests/distancecheck.py), not a guess:
#   - 4 plausible workflow/industry queries topped out at 0.384-0.504
#   - 3 of 4 deliberately absurd queries never got below 0.62
#   - one absurd query ("competitive yodeling championship logistics") had
#     a single coincidentally-close chunk at 0.476 — an accepted edge case;
#     a hard global cutoff can't perfectly separate every possible nonsense
#     query from real ones, but it correctly returns few-to-no matches for
#     the large majority. 0.52 sits just above the highest observed
#     plausible value (0.504) so genuine matches are never false-rejected.
RELEVANCE_THRESHOLD = 0.52


def _to_label(canonical_id: str) -> str:
    """canonical_id -> its human-readable PRICING label, or the id itself if unknown."""
    return PRICING.get(canonical_id, {}).get("label", canonical_id)


def count_exact_matches(cases: list, workflow: str, industry: str) -> int:
    """
    How many of these cases are *actually* the requested industry + workflow?

    Why this exists: retrieval is semantic, so it always returns the nearest
    cases whether or not any case truly matches the request. A full sweep of all
    432 dropdown combinations against the corpus found that 205 of them (47%)
    have ZERO real cases — e.g. there is no "Procurement in Education" deployment
    in the library at all. For those, the pipeline still returns 15 neighbours
    from other industries, which is a defensible design ("here is the closest
    comparable evidence") but only if the UI says so. It previously claimed
    "15 real Education Procurement deployments matched", which was false.

    "Any workflow"/"Any industry" mean no preference, so they impose no
    constraint and cannot make a case a mismatch.
    """
    wf = str(workflow or "").strip().lower()
    ind = str(industry or "").strip().lower()
    wf_any = not wf or wf.startswith("any")
    ind_any = not ind or ind.startswith("any")
    if wf_any and ind_any:
        return len(cases)          # nothing was asked for, so nothing can mismatch
    n = 0
    for c in cases:
        ind_ok = ind_any or str(c.get("industry", "")).strip().lower() == ind
        wf_ok = wf_any or str(c.get("domain", "")).strip().lower() == wf
        if ind_ok and wf_ok:
            n += 1
    return n


def run_pipeline(inputs: dict) -> dict:
    """
    inputs: {"workflow": str, "industry": str, "org_size": str,
             "privacy": str, "budget": float,
             # Icebox B.5 (Build Guide 24) — both optional:
             "project_name": str, "exclude_tools": list[str]}
    returns: a dict the dashboard (Card 3.1) can render directly.
    """
    # Step 1: retrieve.
    # Card 2.2 stores 3 chunks per case (implementation/outcome/domain), so a
    # single case can legitimately fill several of the top results. Ask for
    # more results than we need (15, not 5) so that after de-duplicating down
    # to unique cases below, we still have a healthy number of distinct cases
    # to rank tools and pull "social proof" references from.
    # "Any workflow"/"Any industry" are UI conveniences meaning "no preference" —
    # they are NOT values in the corpus. Interpolating them raw produced the
    # literal query "Any workflow in the Any industry industry", which is what the
    # default form state sent before this fix. Drop the unspecified half instead,
    # and fall back to a neutral corpus-wide phrase if the user specified neither.
    _wf = "" if str(inputs["workflow"]).lower().startswith("any") else inputs["workflow"]
    _ind = "" if str(inputs["industry"]).lower().startswith("any") else inputs["industry"]
    if _wf and _ind:
        query_text = f"{_wf} in the {_ind} industry"
    elif _wf:
        query_text = _wf
    elif _ind:
        query_text = f"AI adoption in the {_ind} industry"
    else:
        query_text = "enterprise AI adoption"
    results = _collection.query(query_texts=[query_text], n_results=15)

    # De-duplicate by case_id: keep only the first (best-ranked) chunk per
    # case, so one case can't count as 2-3 pieces of evidence in the ranking
    # below just because it happened to produce multiple matching chunks.
    seen_case_ids = set()
    matched_cases = []
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        # Relevance filter — skip anything past RELEVANCE_THRESHOLD before it
        # ever reaches ranking, cost, or the LLM summary.
        if dist > RELEVANCE_THRESHOLD:
            continue
        case_id = meta["case_id"]
        if case_id in seen_case_ids:
            continue
        seen_case_ids.add(case_id)
        matched_cases.append({
            "case_id": case_id,
            "organization": meta["organization"],
            "title": meta["title"],
            "industry": meta["industry"],
            "domain": meta.get("domain", ""),   # NEW — needed to tell a true
                                                # industry+workflow match from a
                                                # nearest-neighbour one (see
                                                # count_exact_matches below)
            "source_url": meta["source_url"],
            "canonical_tools": meta["canonical_tools"].split(",") if meta["canonical_tools"] else [],
            "outcomes": meta["outcomes"],   # NEW — bullet-pointed prose, ready for Epic 3 to render
            "distance": round(dist, 3),    # NEW — raw relevance score, carried through in case a
                                            # future card wants to surface it (e.g. Block C's "why:" line)
        })

    # Step 2: privacy filter + user vendor exclusions (B.5) + rank.
    # Order matters: privacy is a hard rule and sees everything; exclusions
    # are a preference applied on top of the already-compliant list.
    filtered_cases = apply_privacy_filter(matched_cases, inputs["privacy"])
    filtered_cases = apply_vendor_exclusions(filtered_cases, inputs.get("exclude_tools", []))
    ranked_tools = rank_tools_by_frequency(filtered_cases, top_n=5)

    # --- No-match guard (Ash4, fix 1 of 3 for the relevance threshold) --------
    # RELEVANCE_THRESHOLD can legitimately filter EVERYTHING out — that's the
    # point for a nonsense query. Without this guard the run continued with an
    # empty stack and still called the LLM with "Matched cases: 0", i.e. asked a
    # model to write a recommendation with no evidence behind it. That is the
    # exact failure mode this architecture exists to prevent (deterministic
    # first, model last, never inventing), so we short-circuit instead: return a
    # fully-formed result with no_match=True, no LLM call, and a plain factual
    # sentence written by us. The UI renders an honest empty state from this.
    if not ranked_tools:
        return {
            "recommended_stack": [],
            "cost_forecast": estimate_cost([], inputs["org_size"], inputs["budget"]),
            "tool_costs": {},
            "matched_cases": filtered_cases,   # may be non-empty but tool-less
            "summary_text": (
                "No comparable deployments in the case library were close enough "
                "to this combination of workflow and industry, so there is no "
                "evidence-backed stack to recommend. Try a broader workflow or a "
                "related industry — this is a deliberate limit, not an error: "
                "AASA only recommends tools it can point to real deployments for."
            ),
            "query": {
                "workflow": inputs["workflow"],
                "industry": inputs["industry"],
                "org_size": inputs["org_size"],
                "privacy": inputs["privacy"],
            },
            "project_name": inputs.get("project_name", ""),
            # No model was called, so there are no real metrics to report. Zeros
            # (not fabricated numbers) keep Card 3.3's telemetry schema intact.
            "llm_metrics": {"duration_seconds": 0.0, "prompt_tokens": 0,
                            "completion_tokens": 0, "tokens_per_second": None},
            "no_match": True,
            # Why it was empty — lets the UI explain the real cause rather than
            # blaming the privacy filter for a relevance miss.
            "no_match_reason": ("privacy_filter" if matched_cases and not filtered_cases
                                else "no_relevant_cases"),
            "exact_match_count": count_exact_matches(
                filtered_cases, inputs["workflow"], inputs["industry"]),
        }

    # Step 3: cost
    # Update D: budget is now actually passed through — previously it was
    # captured on the intake form and validated but never read again, so the
    # forecast could come back many multiples over budget with no flag at all.
    cost_forecast = estimate_cost(ranked_tools, inputs["org_size"], inputs["budget"])

    # Update E (Card 3.1 UI): per-tool costs for every ranked tool, not just the
    # winning primary_api/assistant pair — lets Block A show a price under each
    # recommendation instead of just the pricing-model label.
    tool_costs = estimate_all_tool_costs(ranked_tools, inputs["org_size"])

    # Step 4: summary.
    # Card 2.6 was tested by feeding generate_summary raw canonical ids
    # (e.g. "ms-copilot") — the model doesn't reliably translate those to
    # human-readable names on its own (its few-shot example does, but real
    # ids outside that example leaked through verbatim during Card 2.6
    # eval). Cost/ranking logic above still keys everything by canonical id
    # (that's what pricing.py/filter.py expect), so only build label-ified
    # copies for the two things that get read by the LLM.
    ranked_tool_labels = [_to_label(t) for t in ranked_tools]
    cost_forecast_for_prompt = {
        "primary_api": {**cost_forecast["primary_api"], "tool": _to_label(cost_forecast["primary_api"]["tool"])}
                        if cost_forecast["primary_api"] else None,
        "assistant": {**cost_forecast["assistant"], "tool": _to_label(cost_forecast["assistant"]["tool"])}
                     if cost_forecast["assistant"] else None,
        "disclaimer": cost_forecast["disclaimer"],
        # Update D — pass the budget-fit fields through too, so Card 2.6 can
        # honestly flag an over-budget forecast instead of describing it neutrally.
        "total_monthly_eur": cost_forecast["total_monthly_eur"],
        "budget": cost_forecast["budget"],
        "within_budget": cost_forecast["within_budget"],
        "budget_delta_eur": cost_forecast["budget_delta_eur"],
    }
    summary = generate_summary(ranked_tool_labels, cost_forecast_for_prompt, filtered_cases, inputs["privacy"])

    return {
        "recommended_stack": ranked_tools,
        "cost_forecast": cost_forecast,
        "tool_costs": tool_costs,
        "matched_cases": filtered_cases,
        "summary_text": summary["text"],
        # Lovable-parity UI round — echo the query so the dashboard can render
        # the status-chip row, the "DIRECTIONAL ONLY" banner, and the per-case
        # "why:" lines without re-deriving what was asked. Display-only.
        "query": {
            "workflow": inputs["workflow"],
            "industry": inputs["industry"],
            "org_size": inputs["org_size"],
            "privacy": inputs["privacy"],
        },
        # Icebox B.5 — kept top-level (NOT inside query: query is strictly the
        # 5 validated pipeline inputs; this is a display-only cosmetic field).
        "project_name": inputs.get("project_name", ""),
        # Ash4: present on both paths so the UI can branch on one key.
        "no_match": False,
        # Ash4 (post-sweep): how many of matched_cases are TRULY this industry +
        # workflow, as opposed to nearest-neighbour cases from elsewhere. 205 of
        # the 432 dropdown combinations have no real cases at all, so the banner
        # must not claim "N real X Y deployments" without checking this first.
        "exact_match_count": count_exact_matches(
            filtered_cases, inputs["workflow"], inputs["industry"]),
        # Card 3.3 logs this to telemetry once tracker.py exists — see that card.
        "llm_metrics": {
            "duration_seconds": summary["duration_seconds"],
            "prompt_tokens": summary["prompt_tokens"],
            "completion_tokens": summary["completion_tokens"],
            "tokens_per_second": summary["tokens_per_second"],
        },
    }
