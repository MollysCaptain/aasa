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
from app.logic.filter import apply_privacy_filter, rank_tools_by_frequency
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


def _to_label(canonical_id: str) -> str:
    """canonical_id -> its human-readable PRICING label, or the id itself if unknown."""
    return PRICING.get(canonical_id, {}).get("label", canonical_id)


def run_pipeline(inputs: dict) -> dict:
    """
    inputs: {"workflow": str, "industry": str, "org_size": str,
             "privacy": str, "budget": float}
    returns: a dict the dashboard (Card 3.1) can render directly.
    """
    # Step 1: retrieve.
    # Card 2.2 stores 3 chunks per case (implementation/outcome/domain), so a
    # single case can legitimately fill several of the top results. Ask for
    # more results than we need (15, not 5) so that after de-duplicating down
    # to unique cases below, we still have a healthy number of distinct cases
    # to rank tools and pull "social proof" references from.
    query_text = f"{inputs['workflow']} in the {inputs['industry']} industry"
    results = _collection.query(query_texts=[query_text], n_results=15)

    # De-duplicate by case_id: keep only the first (best-ranked) chunk per
    # case, so one case can't count as 2-3 pieces of evidence in the ranking
    # below just because it happened to produce multiple matching chunks.
    seen_case_ids = set()
    matched_cases = []
    for meta in results["metadatas"][0]:
        case_id = meta["case_id"]
        if case_id in seen_case_ids:
            continue
        seen_case_ids.add(case_id)
        matched_cases.append({
            "case_id": case_id,
            "organization": meta["organization"],
            "title": meta["title"],
            "industry": meta["industry"],
            "source_url": meta["source_url"],
            "canonical_tools": meta["canonical_tools"].split(",") if meta["canonical_tools"] else [],
            "outcomes": meta["outcomes"],   # NEW — bullet-pointed prose, ready for Epic 3 to render
        })

    # Step 2: privacy filter + rank
    filtered_cases = apply_privacy_filter(matched_cases, inputs["privacy"])
    ranked_tools = rank_tools_by_frequency(filtered_cases, top_n=5)

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
        # Card 3.3 logs this to telemetry once tracker.py exists — see that card.
        "llm_metrics": {
            "duration_seconds": summary["duration_seconds"],
            "prompt_tokens": summary["prompt_tokens"],
            "completion_tokens": summary["completion_tokens"],
            "tokens_per_second": summary["tokens_per_second"],
        },
    }
