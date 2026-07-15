"""
Card 2.3 — Hand-built pricing table for the canonical tools.

Every entry is tagged with a `model`:
  "token"   -> priced per million input/output tokens (in_ppm / out_ppm, in EUR)
  "seat"    -> priced per user per month (seat_pm, in EUR)
  "compute" -> billed by compute/usage; shown but not costed in this MVP (note only)
  "free"    -> open-source / no license cost (note only)

IMPORTANT: these numbers are illustrative and WILL go stale. Check the vendor's
current pricing page before quoting a number to a real user. Every place this
table is used in the app must show a "verify on vendor page" disclaimer.
"""

PRICING = {
    "openai-api":       {"label": "OpenAI API (GPT-4o class)",   "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "azure-openai":      {"label": "Azure OpenAI Service",        "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "claude-api":        {"label": "Anthropic Claude API",        "kind": "LLM API",              "model": "token", "in_ppm": 3.0,  "out_ppm": 15.0},
    "aws-bedrock":       {"label": "Amazon Bedrock",               "kind": "LLM API",              "model": "token", "in_ppm": 2.0,  "out_ppm": 8.0},
    "cohere":            {"label": "Cohere API",                   "kind": "LLM API",              "model": "token", "in_ppm": 1.5,  "out_ppm": 6.0},
    "chatgpt":           {"label": "ChatGPT Enterprise",           "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 60.0},
    "ms-copilot":        {"label": "Microsoft 365 Copilot",        "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 30.0},
    "github-copilot":    {"label": "GitHub Copilot Business",      "kind": "Coding assistant",     "model": "seat",  "seat_pm": 19.0},
    "gemini":            {"label": "Gemini (consumer)",            "kind": "AI assistant",         "model": "seat",  "seat_pm": 0.0},
    "gemini-workspace":  {"label": "Gemini for Google Workspace",  "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 20.0},
    "gemini-api":        {"label": "Google Gemini API",            "kind": "LLM API",              "model": "token", "in_ppm": 1.25, "out_ppm": 5.0, "note": "Illustrative; Gemini has multiple tiered models with different per-token rates — verify against the specific model before quoting."},
    "claude":            {"label": "Claude.ai (consumer/Pro)",     "kind": "AI assistant",         "model": "seat",  "seat_pm": 18.0},
    "notion-ai":         {"label": "Notion AI",                    "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 8.0},
    "salesforce-einstein": {"label": "Salesforce Einstein Copilot", "kind": "AI assistant (SaaS)", "model": "seat",  "seat_pm": 50.0},
    "midjourney":        {"label": "Midjourney",                   "kind": "Image generation",     "model": "seat",  "seat_pm": 10.0},
    "dalle":             {"label": "DALL-E (via OpenAI API)",      "kind": "Image generation",     "model": "token", "in_ppm": 0.0,  "out_ppm": 0.0},  # priced per-image, not per-token — flag for manual review
    "stable-diffusion":  {"label": "Stable Diffusion",             "kind": "Image generation (OSS)", "model": "free", "note": "free / self-hosted; compute cost only"},
    "llama":             {"label": "Llama (Meta, self-hosted)",   "kind": "Open-weight LLM",       "model": "free", "note": "free / open weights; compute cost only"},
    "huggingface":       {"label": "Hugging Face (hosted inference)", "kind": "Model hosting",     "model": "compute", "note": "usage-billed; varies by model size"},
    "langchain":         {"label": "LangChain",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "langgraph":         {"label": "LangGraph",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "crewai":            {"label": "CrewAI",                       "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "autogen":           {"label": "AutoGen / AG2",                "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "pinecone":          {"label": "Pinecone",                     "kind": "Vector database",       "model": "compute", "note": "usage-billed; free tier available"},
    "chroma":            {"label": "Chroma (self-hosted)",         "kind": "Vector database (OSS)", "model": "free", "note": "free / open source; compute cost only"},

    # --- Added to cover Card 2.1's expanded ALIAS_MAP (the coverage push from
    # 46.8% to 88.7% added ~16 canonical ids beyond the guide's original starter
    # list — see 13-Build-Guide-Epic2-Retrieval-v1.md's Card 2.1 coverage note).
    # Same "illustrative, verify on vendor page" caveat applies to all of these. ---
    "copilot-studio":    {"label": "Microsoft Copilot Studio",     "kind": "Agent builder (SaaS)", "model": "seat",  "seat_pm": 200.0, "note": "priced per-message-pack in reality, not flat seat — flag for manual review"},
    "vertex-ai":         {"label": "Google Vertex AI",             "kind": "LLM API / ML platform", "model": "token", "in_ppm": 1.25, "out_ppm": 5.0},
    "ibm-watsonx":       {"label": "IBM watsonx (Assistant/AI/Orchestrate)", "kind": "AI platform (SaaS)", "model": "seat", "seat_pm": 140.0, "note": "IBM's real pricing is usage/resource-unit based, not flat seat — flag for manual review"},
    "ibm-cloud":         {"label": "IBM Cloud",                    "kind": "Cloud platform",        "model": "compute", "note": "usage-billed; varies by service"},
    "google-cloud":      {"label": "Google Cloud Platform",        "kind": "Cloud platform",        "model": "compute", "note": "usage-billed; varies by service (BigQuery, GKE, Cloud Run, etc.)"},
    "azure-platform":    {"label": "Microsoft Azure (AI/ML services)", "kind": "Cloud platform",     "model": "compute", "note": "usage-billed; varies by service"},
    "aws-platform":      {"label": "AWS (SageMaker/S3/EC2/etc.)",  "kind": "Cloud platform",         "model": "compute", "note": "usage-billed; varies by service"},
    "nvidia":            {"label": "NVIDIA AI Enterprise / GPUs",  "kind": "Compute hardware/platform", "model": "compute", "note": "hardware + licensing cost; highly variable"},
    "tensorflow":        {"label": "TensorFlow",                   "kind": "ML framework (OSS)",    "model": "free", "note": "free / open source; compute cost only"},
    "pytorch":           {"label": "PyTorch",                      "kind": "ML framework (OSS)",    "model": "free", "note": "free / open source; compute cost only"},
    "ms365-suite":       {"label": "Microsoft 365 (Teams/SharePoint/Outlook)", "kind": "Productivity suite (SaaS)", "model": "seat", "seat_pm": 12.5},
    "ms-dynamics":       {"label": "Microsoft Dynamics 365",       "kind": "CRM/ERP (SaaS)",         "model": "seat",  "seat_pm": 95.0},
    "perplexity":        {"label": "Perplexity Enterprise / Sonar API", "kind": "AI search / LLM API", "model": "seat", "seat_pm": 40.0, "note": "Sonar API usage is actually token-billed, separate from the Enterprise seat product — flag for manual review"},
    "google-ai":         {"label": "Google AI products (NotebookLM/Imagen/Veo/etc.)", "kind": "AI assistant / model", "model": "seat", "seat_pm": 0.0, "note": "mostly bundled into Google Workspace/Cloud rather than sold standalone — flag for manual review"},
    "flowforma":         {"label": "FlowForma",                    "kind": "Workflow automation (SaaS)", "model": "seat", "seat_pm": 25.0},
    "nuance-dragon":     {"label": "Nuance Dragon Medical One",    "kind": "Speech recognition (SaaS)", "model": "seat", "seat_pm": 99.0},
}

ILLUSTRATIVE_DISCLAIMER = (
    "Pricing shown is illustrative and may be out of date. "
    "Always verify current pricing on the vendor's official page before budgeting."
)
