"""
Card 2.3 — Hand-built pricing table for the canonical tools.

Every entry is tagged with a `model`:
  "token"   -> priced per million input/output tokens (in_ppm / out_ppm, in EUR)
  "seat"    -> priced per user per month (seat_pm, in EUR)
  "compute" -> billed by compute/usage; shown but not costed in this MVP (note only)
  "free"    -> open-source / no license cost (note only)

Every entry also carries a "url": the tool's official homepage, linked from
Block A (UI-v2c). Illustrative/product-root links — like the prices, verify
against the vendor before relying; sites do get restructured.

IMPORTANT: these numbers are illustrative and WILL go stale. Check the vendor's
current pricing page before quoting a number to a real user. Every place this
table is used in the app must show a "verify on vendor page" disclaimer.
"""

PRICING = {
    "openai-api":       {"url": "https://platform.openai.com", "label": "OpenAI API (GPT-4o class)",   "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "azure-openai":      {"url": "https://azure.microsoft.com/products/ai-services/openai-service", "label": "Azure OpenAI Service",        "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "claude-api":        {"url": "https://www.anthropic.com/api", "label": "Anthropic Claude API",        "kind": "LLM API",              "model": "token", "in_ppm": 3.0,  "out_ppm": 15.0},
    "aws-bedrock":       {"url": "https://aws.amazon.com/bedrock/", "label": "Amazon Bedrock",               "kind": "LLM API",              "model": "token", "in_ppm": 2.0,  "out_ppm": 8.0},
    "cohere":            {"url": "https://cohere.com", "label": "Cohere API",                   "kind": "LLM API",              "model": "token", "in_ppm": 1.5,  "out_ppm": 6.0},
    "chatgpt":           {"url": "https://openai.com/chatgpt/enterprise/", "label": "ChatGPT Enterprise",           "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 60.0},
    "ms-copilot":        {"url": "https://www.microsoft.com/microsoft-365/copilot", "label": "Microsoft 365 Copilot",        "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 30.0},
    "github-copilot":    {"url": "https://github.com/features/copilot", "label": "GitHub Copilot Business",      "kind": "Coding assistant",     "model": "seat",  "seat_pm": 19.0},
    "gemini":            {"url": "https://gemini.google.com", "label": "Gemini (consumer)",            "kind": "AI assistant",         "model": "seat",  "seat_pm": 0.0},
    "gemini-workspace":  {"url": "https://workspace.google.com/solutions/ai/", "label": "Gemini for Google Workspace",  "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 20.0},
    "gemini-api":        {"url": "https://ai.google.dev", "label": "Google Gemini API",            "kind": "LLM API",              "model": "token", "in_ppm": 1.25, "out_ppm": 5.0, "note": "Illustrative; Gemini has multiple tiered models with different per-token rates — verify against the specific model before quoting."},
    "claude":            {"url": "https://claude.ai", "label": "Claude.ai (consumer/Pro)",     "kind": "AI assistant",         "model": "seat",  "seat_pm": 18.0},
    "notion-ai":         {"url": "https://www.notion.so/product/ai", "label": "Notion AI",                    "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 8.0},
    "salesforce-einstein": {"url": "https://www.salesforce.com/products/einstein/", "label": "Salesforce Einstein Copilot", "kind": "AI assistant (SaaS)", "model": "seat",  "seat_pm": 50.0},
    "midjourney":        {"url": "https://www.midjourney.com", "label": "Midjourney",                   "kind": "Image generation",     "model": "seat",  "seat_pm": 10.0},
    "dalle":             {"url": "https://openai.com/dall-e-3", "label": "DALL-E (via OpenAI API)",      "kind": "Image generation",     "model": "token", "in_ppm": 0.0,  "out_ppm": 0.0},  # priced per-image, not per-token — flag for manual review
    "stable-diffusion":  {"url": "https://stability.ai", "label": "Stable Diffusion",             "kind": "Image generation (OSS)", "model": "free", "note": "free / self-hosted; compute cost only"},
    "llama":             {"url": "https://www.llama.com", "label": "Llama (Meta, self-hosted)",   "kind": "Open-weight LLM",       "model": "free", "note": "free / open weights; compute cost only"},
    "huggingface":       {"url": "https://huggingface.co", "label": "Hugging Face (hosted inference)", "kind": "Model hosting",     "model": "compute", "note": "usage-billed; varies by model size"},
    "langchain":         {"url": "https://www.langchain.com", "label": "LangChain",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "langgraph":         {"url": "https://www.langchain.com/langgraph", "label": "LangGraph",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "crewai":            {"url": "https://www.crewai.com", "label": "CrewAI",                       "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "autogen":           {"url": "https://microsoft.github.io/autogen/", "label": "AutoGen / AG2",                "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "pinecone":          {"url": "https://www.pinecone.io", "label": "Pinecone",                     "kind": "Vector database",       "model": "compute", "note": "usage-billed; free tier available"},
    "chroma":            {"url": "https://www.trychroma.com", "label": "Chroma (self-hosted)",         "kind": "Vector database (OSS)", "model": "free", "note": "free / open source; compute cost only"},

    # --- Added to cover Card 2.1's expanded ALIAS_MAP (the coverage push from
    # 46.8% to 88.7% added ~16 canonical ids beyond the guide's original starter
    # list — see 13-Build-Guide-Epic2-Retrieval-v1.md's Card 2.1 coverage note).
    # Same "illustrative, verify on vendor page" caveat applies to all of these. ---
    "copilot-studio":    {"url": "https://www.microsoft.com/microsoft-copilot/microsoft-copilot-studio", "label": "Microsoft Copilot Studio",     "kind": "Agent builder (SaaS)", "model": "seat",  "seat_pm": 200.0, "note": "priced per-message-pack in reality, not flat seat — flag for manual review"},
    "vertex-ai":         {"url": "https://cloud.google.com/vertex-ai", "label": "Google Vertex AI",             "kind": "LLM API / ML platform", "model": "token", "in_ppm": 1.25, "out_ppm": 5.0},
    "ibm-watsonx":       {"url": "https://www.ibm.com/watsonx", "label": "IBM watsonx (Assistant/AI/Orchestrate)", "kind": "AI platform (SaaS)", "model": "seat", "seat_pm": 140.0, "note": "IBM's real pricing is usage/resource-unit based, not flat seat — flag for manual review"},
    "ibm-cloud":         {"url": "https://www.ibm.com/cloud", "label": "IBM Cloud",                    "kind": "Cloud platform",        "model": "compute", "note": "usage-billed; varies by service"},
    "google-cloud":      {"url": "https://cloud.google.com", "label": "Google Cloud Platform",        "kind": "Cloud platform",        "model": "compute", "note": "usage-billed; varies by service (BigQuery, GKE, Cloud Run, etc.)"},
    "azure-platform":    {"url": "https://azure.microsoft.com", "label": "Microsoft Azure (AI/ML services)", "kind": "Cloud platform",     "model": "compute", "note": "usage-billed; varies by service"},
    "aws-platform":      {"url": "https://aws.amazon.com", "label": "AWS (SageMaker/S3/EC2/etc.)",  "kind": "Cloud platform",         "model": "compute", "note": "usage-billed; varies by service"},
    "nvidia":            {"url": "https://www.nvidia.com/en-us/ai-data-science/", "label": "NVIDIA AI Enterprise / GPUs",  "kind": "Compute hardware/platform", "model": "compute", "note": "hardware + licensing cost; highly variable"},
    "tensorflow":        {"url": "https://www.tensorflow.org", "label": "TensorFlow",                   "kind": "ML framework (OSS)",    "model": "free", "note": "free / open source; compute cost only"},
    "pytorch":           {"url": "https://pytorch.org", "label": "PyTorch",                      "kind": "ML framework (OSS)",    "model": "free", "note": "free / open source; compute cost only"},
    "ms365-suite":       {"url": "https://www.microsoft.com/microsoft-365", "label": "Microsoft 365 (Teams/SharePoint/Outlook)", "kind": "Productivity suite (SaaS)", "model": "seat", "seat_pm": 12.5},
    "ms-dynamics":       {"url": "https://www.microsoft.com/dynamics-365", "label": "Microsoft Dynamics 365",       "kind": "CRM/ERP (SaaS)",         "model": "seat",  "seat_pm": 95.0},
    "perplexity":        {"url": "https://www.perplexity.ai", "label": "Perplexity Enterprise / Sonar API", "kind": "AI search / LLM API", "model": "seat", "seat_pm": 40.0, "note": "Sonar API usage is actually token-billed, separate from the Enterprise seat product — flag for manual review"},
    "google-ai":         {"url": "https://ai.google", "label": "Google AI products (NotebookLM/Imagen/Veo/etc.)", "kind": "AI assistant / model", "model": "seat", "seat_pm": 0.0, "note": "mostly bundled into Google Workspace/Cloud rather than sold standalone — flag for manual review"},
    "flowforma":         {"url": "https://www.flowforma.com", "label": "FlowForma",                    "kind": "Workflow automation (SaaS)", "model": "seat", "seat_pm": 25.0},
    "nuance-dragon":     {"url": "https://www.nuance.com/healthcare.html", "label": "Nuance Dragon Medical One",    "kind": "Speech recognition (SaaS)", "model": "seat", "seat_pm": 99.0},
}

ILLUSTRATIVE_DISCLAIMER = (
    "Pricing shown is illustrative and may be out of date. "
    "Always verify current pricing on the vendor's official page before budgeting."
)
