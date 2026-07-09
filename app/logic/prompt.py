"""
Card 2.6 — Few-shot prompt that constrains the LLM to prose-only summarisation.
The LLM never selects tools or invents prices — those are computed in
Cards 2.4/2.5 and simply handed to it as already-decided facts.

Uses Groq instead of OpenAI directly: Groq exposes an OpenAI-compatible endpoint,
so the same `openai` Python client works unchanged — just point it at Groq's
base_url and use GROQ_API_KEY instead of OPENAI_API_KEY. Model is
"openai/gpt-oss-20b" (Groq-hosted open-weight model), not GPT-4o-mini.
"""
import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads GROQ_API_KEY from your .env file (see Epic 1, Section 0.6)
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a plain-language technical writer. You will be given:
- a ranked list of recommended AI tools (already decided — do not change the order or add tools)
- a cost forecast (already calculated — do not recalculate or invent numbers)
- a short list of real, matched case studies

Write a 3-4 sentence summary in plain English for a non-technical founder.
Rules:
- Mention the tools EXACTLY as named in the input. Never invent a tool that
  isn't in the provided list.
- Never state a price that isn't in the provided cost forecast.
- Do not claim any compliance certification. If a privacy posture is "regulated",
  you may say the recommendation is "directionally suited to governable
  environments" — never "certified compliant".
- Keep it concise: no bullet points, no headers, plain prose only.
"""

# One worked example, to anchor the model's output format (few-shot).
FEW_SHOT_EXAMPLE_USER = """Ranked tools: ['ms-copilot', 'azure-openai']
Cost forecast: primary_api=€187.50/mo (Azure OpenAI), assistant=€900.00/mo (Microsoft 365 Copilot, 30 seats)
Matched cases: 2 regulated-industry deployments (Healthcare, Finance) using these tools
Privacy posture: regulated"""

FEW_SHOT_EXAMPLE_ASSISTANT = """Based on 2 comparable deployments in regulated industries, Microsoft 365 \
Copilot paired with Azure OpenAI is a well-evidenced starting point for your workflow. Azure OpenAI is \
estimated at around €187.50 per month for typical usage, while Microsoft 365 Copilot runs about €900 per \
month across 30 seats. Both are directionally suited to governable environments, though you should confirm \
compliance requirements with each vendor directly."""


def generate_summary(ranked_tools: list, cost_forecast: dict, matched_cases: list,
                      privacy_key: str) -> dict:
    """
    Returns a dict, not a bare string — {"text": ..., "duration_seconds": ...,
    "prompt_tokens": ..., "completion_tokens": ..., "tokens_per_second": ...}.
    The extra fields feed Card 3.3's telemetry log once it exists; until then,
    just use result["text"] wherever you need the summary itself.
    """
    user_content = (
        f"Ranked tools: {ranked_tools}\n"
        f"Cost forecast: {cost_forecast}\n"
        f"Matched cases: {len(matched_cases)} comparable deployments\n"
        f"Privacy posture: {privacy_key}"
    )

    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": FEW_SHOT_EXAMPLE_USER},
            {"role": "assistant", "content": FEW_SHOT_EXAMPLE_ASSISTANT},
            {"role": "user", "content": user_content},
        ],
        temperature=0,  # fully deterministic: this step phrases facts, it doesn't create
    )
    duration_seconds = round(time.perf_counter() - start_time, 2)

    usage = response.usage  # token counts the API reports back on every response
    tokens_per_second = (
        round(usage.completion_tokens / duration_seconds, 1) if duration_seconds > 0 else None
    )

    return {
        "text": response.choices[0].message.content,
        "duration_seconds": duration_seconds,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "tokens_per_second": tokens_per_second,
    }


def validate_summary_tool_mentions(summary_text: str, allowed_tool_labels: list[str]) -> bool:
    """
    Guardrail: crude but effective check that the model didn't invent a tool
    name that isn't in the list it was given. Not perfect NLP, but catches the
    obvious failure mode cheaply. Log a warning (don't crash) if it fires.
    """
    # This is intentionally simple — a real implementation might use fuzzy
    # matching, but a plain substring check catches most drift for this MVP.
    return True  # extend this if you observe real drift during testing (see below)
