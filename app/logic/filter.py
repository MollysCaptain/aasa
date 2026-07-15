"""
Card 2.5 — Deterministic privacy filter + frequency-based tool ranking.
This is directional guidance, NOT a compliance certification — say so in the UI.
"""
from collections import Counter

# Tools considered governable enough for regulated data: self-hostable, on-prem
# capable, or backed by an enterprise data-processing agreement. Consumer-only
# tools are excluded when privacy == "regulated".
GOVERNABLE_FOR_REGULATED = {
    "azure-openai", "aws-bedrock", "claude-api", "ms-copilot", "gemini-workspace",
    "langchain", "langgraph", "crewai", "autogen", "llama", "huggingface",
    "chroma", "salesforce-einstein",

    # --- Added to cover Card 2.1's expanded ALIAS_MAP (see
    # 13-Build-Guide-Epic2-Retrieval-v1.md's Card 2.1 coverage note) — without
    # this, every one of these would be silently stripped out under "regulated"
    # even though most clearly meet the criteria above. ---
    "vertex-ai", "ibm-watsonx", "ibm-cloud", "google-cloud", "azure-platform",
    "aws-platform",          # enterprise cloud platforms — all offer DPAs/HIPAA BAAs
    "nvidia", "tensorflow", "pytorch",  # self-hostable by definition
    "ms365-suite", "ms-dynamics",       # enterprise Microsoft products with DPAs
    "nuance-dragon",          # Dragon Medical One is purpose-built for HIPAA healthcare use

    # Deliberately NOT added — each covers a mix of consumer and enterprise
    # products under one canonical id (unlike e.g. gemini vs. gemini-workspace,
    # which the starter map already splits), so there's no clean signal that a
    # match here is the enterprise-grade version. Fails closed until someone
    # either splits these into separate ids or confirms the DPA/compliance
    # posture of the underlying products:
    #   "perplexity"  — Perplexity Enterprise (arguably governable) vs. plain
    #                   consumer Perplexity/Sonar API, same canonical id
    #   "google-ai"   — mixes enterprise API products (Dialogflow, Document AI)
    #                   with consumer-facing tools (NotebookLM, Imagen, Veo)
    #   "flowforma"   — plausibly governable (markets itself at regulated
    #                   industries) but not independently verified here
    #   "gemini-api"  — added in the Epic 1/2 updates doc (Update A) for the
    #                   standalone Gemini Developer API (generativelanguage.
    #                   googleapis.com / AI Studio), which historically has
    #                   different data-handling terms than the Vertex-AI-hosted
    #                   Gemini (already covered, and governable, under
    #                   "vertex-ai"). Same ambiguity class as "perplexity" —
    #                   fails closed until the DPA terms of this specific
    #                   surface are independently confirmed.
}


def apply_privacy_filter(matched_cases: list[dict], privacy_key: str) -> list[dict]:
    """
    matched_cases: list of dicts, each with a "canonical_tools" list
                    (this is what Card 2.2's Chroma query results should be
                    reshaped into before calling this function).
    Returns the same list, but with non-governable tools stripped out of each
    case's canonical_tools when privacy_key == "regulated". Standard posture
    passes every case through unchanged.
    """
    if privacy_key != "regulated":
        return matched_cases

    filtered = []
    for case in matched_cases:
        allowed_tools = [t for t in case["canonical_tools"] if t in GOVERNABLE_FOR_REGULATED]
        filtered.append({**case, "canonical_tools": allowed_tools})
    return filtered


def rank_tools_by_frequency(filtered_cases: list[dict], top_n: int = 5) -> list[str]:
    """
    Counts how many matched (and filtered) cases mention each canonical tool,
    returns the top_n tool ids, most-frequent first. This ranking — not the
    LLM — decides what appears in Block A of the blueprint.
    """
    counter = Counter()
    for case in filtered_cases:
        for tool_id in case["canonical_tools"]:
            counter[tool_id] += 1
    return [tool_id for tool_id, _count in counter.most_common(top_n)]
