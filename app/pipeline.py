"""
The single entry point that turns validated form inputs into a blueprint.
Each numbered step below is a placeholder — Epic 2 cards replace them in order:
  Step 1 (normalise/retrieve) <- Cards 2.1, 2.2
  Step 2 (privacy filter)     <- Card 2.5
  Step 3 (cost)               <- Cards 2.3, 2.4
  Step 4 (LLM summary)        <- Card 2.6
"""
import time


def run_pipeline(inputs: dict) -> dict:
    """
    inputs: {"workflow": str, "industry": str, "org_size": str,
             "privacy": str, "budget": float}
    returns: a dict the dashboard (Card 3.1) can render directly.
    """
    # --- Step 1: retrieve comparable cases (placeholder) ---
    # Real version (Card 2.2) will query the Chroma vector store here.
    matched_cases = []

    # --- Step 2: privacy filter (placeholder) ---
    # Real version (Card 2.5) removes ungovernable tools when inputs["privacy"] == "regulated".
    filtered_cases = matched_cases

    # --- Step 3: cost forecast (placeholder) ---
    # Real version (Cards 2.3-2.4) looks up the pricing table and computes an estimate.
    cost_forecast = {"primary_api_monthly": None, "assistant_monthly": None}

    # --- Step 4: LLM summary (placeholder) ---
    # Real version (Card 2.6) calls the model with a few-shot prompt.
    summary_text = (
        "This is a placeholder blueprint. Once Epic 2 is wired up, this will "
        "be a real, evidence-backed recommendation."
    )

    time.sleep(1)  # simulates work so the loading spinner (Step 3 below) is visible

    return {
        "recommended_stack": [],       # Card 3.1 renders this as Block A
        "cost_forecast": cost_forecast,  # Card 3.1 renders this as Block B
        "matched_cases": filtered_cases,  # Card 3.1 renders this as Block C
        "summary_text": summary_text,
    }
