"""
Card 2.1 — Normalise raw tool-name strings into ~24 canonical tool ids.
Run AFTER scripts/validate_use_cases.py and scripts/normalize_domains.py (Step 0)
so this adds canonical_tools on top of an already-validated, domain-normalised file.

Run directly:  python3 scripts/normalise_cases.py
Produces:      data/use-cases.csv, with a new canonical_tools column added in place
               data/unmatched_tools.log   (for weekly review — see Step 5)

Coverage note: settled at 88.7% (target was >=90%). The first pass with the
guide's starter alias map (model/agent-framework focused) only hit 46.8% —
this dataset leans heavily on named cloud/enterprise platforms (Vertex AI,
IBM Watsonx, Azure, AWS, NVIDIA, Perplexity, etc.), so most of the ALIAS_MAP
below beyond the original ~24 ids was added to cover those. What's left
unmatched (see data/unmatched_tools.log) is now almost entirely generic,
vendor-agnostic phrasing with no real product to map to — "AI", "generative
AI", "machine learning", "not specified", "AI agents", "computer vision" —
plus a few one-off bespoke descriptions that mention a vendor name
incidentally (e.g. "on Amazon Kindle hardware") rather than as a named AI
product. Force-mapping these into a canonical tool id would inflate the
coverage number while corrupting the tool-frequency data Cards 2.3/2.5
depend on, so this was deliberately left as the guide's own stated exception
("some rows will genuinely say 'AI' or 'Not specified' with no recoverable
tool") rather than chased further.
"""
import pandas as pd

CSV_PATH = "data/use-cases.csv"  # read AND write — adds a column in place, matching
                                  # the convention Step 0's scripts already use
UNMATCHED_LOG_PATH = "data/unmatched_tools.log"

# canonical_id -> list of lowercase substrings that should map to it.
# Order matters: more specific phrases should come before generic ones
# (e.g. "gemini for workspace" must be checked before bare "gemini").
ALIAS_MAP = {
    "gemini-workspace":  ["gemini for workspace", "gemini in docs", "duet ai"],
    "gemini":            ["gemini", "bard"],
    "chatgpt":           ["chatgpt", "chat gpt"],
    "openai-api":        ["openai api", "gpt-4", "gpt-3.5", "gpt4o", "gpt-4o",
                           "gpt-5", "gpt-3", "openai o1", "openai deep research",
                           "sora", "agents sdk", "realtime api"],
    "azure-openai":      ["azure openai", "azure open ai"],
    "ms-copilot":        ["microsoft copilot", "m365 copilot", "copilot for microsoft 365",
                           "microsoft 365 copilot", "bing chat enterprise"],
    "copilot-studio":    ["copilot studio"],
    "github-copilot":    ["github copilot", "copilot for github"],
    "claude-api":        ["claude api", "anthropic api"],
    "claude":            ["claude", "claude.ai"],
    "aws-bedrock":       ["bedrock", "amazon bedrock"],
    "cohere":            ["cohere"],
    "llama":             ["llama 2", "llama 3", "meta llama", "llama"],
    "huggingface":       ["hugging face", "huggingface", "transformers"],
    "langchain":         ["langchain"],
    "langgraph":         ["langgraph"],
    "crewai":            ["crewai", "crew ai"],
    "autogen":           ["autogen", "ag2"],
    "midjourney":        ["midjourney"],
    "stable-diffusion":  ["stable diffusion", "stability ai"],
    "dalle":             ["dall-e", "dalle"],
    "pinecone":          ["pinecone"],
    "chroma":            ["chromadb", "chroma"],
    "notion-ai":         ["notion ai"],
    "salesforce-einstein": ["einstein copilot", "salesforce einstein"],

    # --- Added after the first coverage pass (46.8%) came in well under the
    # 90% target — the raw data leans heavily on named cloud/enterprise
    # platforms that the original model/agent-framework-focused list above
    # didn't cover at all. These are still specific, named products (not
    # generic technique words like "machine learning" or "RAG" — those stay
    # unmapped on purpose, see JUNK_VALUES and the note below it). ---
    "vertex-ai":         ["vertex ai"],
    "ibm-watsonx":       ["watson", "ibm granite", "ibm research", "ibm ai@scale",
                           "ibm instana"],  # "watson" also matches "watsonx"
                                                       # (watsonx.ai, watsonx assistant,
                                                       # watsonx orchestrate, watsonx.data,
                                                       # watson discovery/studio/nlu/etc.)
    "ibm-cloud":         ["ibm cloud"],
    "google-cloud":      ["google cloud", "bigquery", "google kubernetes engine",
                           "cloud run", "looker", "google workspace", "google vids"],
    "azure-platform":    ["microsoft azure", "azure ai foundry", "azure ai services",
                           "azure cognitive services", "azure machine learning",
                           "azure synapse", "azure databricks", "microsoft fabric",
                           "microsoft sentinel", "microsoft purview", "azure ai search",
                           "azure ai", "azure", "microsoft ai"],
    "aws-platform":      ["amazon sagemaker", "amazon s3", "amazon ec2", "aws lambda",
                           "amazon dynamodb", "amazon redshift", "aws glue",
                           "amazon connect", "amazon lex", "amazon rekognition",
                           "amazon q", "amazon ads", "amazon emr", "amazon alexa",
                           "amazon music", "amazon one", "aws"],
    "nvidia":            ["nvidia", "cuda", "cudnn"],
    "tensorflow":        ["tensorflow"],
    "pytorch":           ["pytorch"],
    "ms365-suite":       ["microsoft 365", "microsoft teams", "sharepoint", "outlook"],
    "ms-dynamics":       ["dynamics 365", "dax copilot"],
    "perplexity":        ["perplexity", "sonar pro", "sonar api"],
    "google-ai":         ["notebooklm", "imagen", "veo", "google ai", "dialogflow",
                           "agentspace", "google distributed cloud", "document ai",
                           "security command center", "google security operations",
                           "code assist"],
    "flowforma":         ["flowforma"],
    "nuance-dragon":     ["dragon medical one"],
}

# Junk values that appear in the raw data but carry no real signal.
JUNK_VALUES = {"ai", "generative ai", "not specified", "n/a", "", "nan"}


def normalise_tool_string(raw_value) -> list[str]:
    """Takes one raw cell value, returns a list of canonical tool ids found in it."""
    if pd.isna(raw_value):
        return []

    text = str(raw_value).strip().lower()
    if text in JUNK_VALUES:
        return []

    matched = []
    for canonical_id, variants in ALIAS_MAP.items():
        for variant in variants:
            if variant in text:
                matched.append(canonical_id)
                break  # don't add the same canonical id twice for one cell

    return matched


def main():
    df = pd.read_csv(CSV_PATH)

    # Real column name, verified against the actual data: "Tool/Technology"
    # (singular) — NOT "Tools/Technologies" as the upstream schema doc and an
    # earlier draft of this guide assumed. Still semicolon-delimited
    # (" ; "), but normalise_tool_string does substring matching over the
    # WHOLE cell, not a per-item split — so a multi-tool cell like
    # "OpenAI's Whisper API ; GPT-4 ; GPT-4 Vision" still matches every
    # phrase it contains without needing to split on ";" first.
    TOOL_COLUMN = "Tool/Technology"

    df["canonical_tools"] = df[TOOL_COLUMN].apply(normalise_tool_string)

    # --- Coverage check (target: >= 90% of rows resolve to at least one tool) ---
    resolved_mask = df["canonical_tools"].apply(lambda tools: len(tools) > 0)
    coverage_pct = 100 * resolved_mask.mean()
    print(f"Coverage: {coverage_pct:.1f}% of {len(df)} rows resolved to >=1 canonical tool.")

    # --- Log every unmatched raw string for weekly review (risk mitigation from the WBS) ---
    unmatched_raw_strings = sorted(df.loc[~resolved_mask, TOOL_COLUMN].dropna().astype(str).unique())
    with open(UNMATCHED_LOG_PATH, "w") as f:
        f.write("\n".join(unmatched_raw_strings))
    print(f"{len(unmatched_raw_strings)} unmatched raw strings logged to {UNMATCHED_LOG_PATH}")

    df.to_csv(CSV_PATH, index=False)  # adds canonical_tools in place, alongside
                                        # Step 0's Use Case Domain (Canonical) column
    print(f"Saved canonical_tools column to {CSV_PATH}")


if __name__ == "__main__":
    main()
