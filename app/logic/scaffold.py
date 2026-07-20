"""
Icebox B.2 (Build Guide 25) — starter-config scaffold for the recommended stack.
Templated text only: we never claim these are complete setup docs,
just the correct env-var names and first commands.
"""
from app.logic.pricing import PRICING

# Hand-written snippets for tools where a scaffold is meaningful.
# Keyed by canonical tool id. Anything not listed falls through to
# a comment line built from its PRICING "model" type. Every key name
# below was checked against the vendor's own docs at time of writing —
# if unsure about a new entry, use the fallback form instead: a
# wrong-but-plausible env var name is worse than an honest "check the console".
SNIPPETS = {
    "openai-api":   'OPENAI_API_KEY=""            # https://platform.openai.com/api-keys',
    "azure-openai": 'AZURE_OPENAI_API_KEY=""\nAZURE_OPENAI_ENDPOINT=""   # from your Azure resource',
    "claude-api":   'ANTHROPIC_API_KEY=""          # https://console.anthropic.com',
    "gemini-api":   'GOOGLE_API_KEY=""             # https://aistudio.google.com/apikey',
    "aws-bedrock":  'AWS_ACCESS_KEY_ID=""\nAWS_SECRET_ACCESS_KEY=""\nAWS_REGION="eu-central-1"',
    "vertex-ai":    'GOOGLE_APPLICATION_CREDENTIALS="service-account.json"\nGCP_PROJECT_ID=""',
    "ibm-watsonx":  'WATSONX_API_KEY=""\nWATSONX_PROJECT_ID=""',
    "cohere":       'COHERE_API_KEY=""',
    "huggingface":  'HF_TOKEN=""                   # https://huggingface.co/settings/tokens',
    "langchain":    "# pip install langchain      — framework, no key of its own",
    "chroma":       "# pip install chromadb       — local vector store, no key needed",
    "llama":        "# Self-hosted open-weight model — see https://llama.com for downloads",
    "tensorflow":   "# pip install tensorflow",
    "pytorch":      "# pip install torch",
}

_FALLBACK_BY_MODEL = {
    "token":   "# {label}: token-billed API — check the vendor console for your key variable",
    "seat":    "# {label}: per-seat SaaS subscription — configured in the vendor admin panel, not in code",
    "compute": "# {label}: compute-billed platform — provisioned in the cloud console, not via .env",
    "free":    "# {label}: free / self-hosted — see vendor docs for install",
}


def build_scaffold(recommended_stack: list[str]) -> str:
    lines = [
        "# --- AASA starter scaffold (illustrative, verify against vendor docs) ---",
        "# Generated from your recommended stack. Keys left blank on purpose.",
        "",
    ]
    for tool_id in recommended_stack:
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        lines.append(f"# {label}")
        snippet = SNIPPETS.get(tool_id)
        if snippet is None:
            template = _FALLBACK_BY_MODEL.get(entry.get("model"), "# {label}: see vendor docs")
            snippet = template.format(label=label)
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines)
