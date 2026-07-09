"""
Prompt eval set — re-run this every time you change SYSTEM_PROMPT or the
few-shot example, not just once.
"""
import os
import sys

# Running this as `python3 scripts/eval_prompt.py` puts scripts/'s own directory
# on sys.path[0], not the project root — so Python looks for "app" *inside*
# scripts/ and raises ModuleNotFoundError. Same root cause as the Streamlit
# ModuleNotFoundError fixed in app/intake.py; same fix, applied here since this
# is the only script under scripts/ that imports from the app package.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logic.prompt import generate_summary

EVAL_CASES = [
    {
        "name": "token + seat, standard",
        "ranked_tools": ["openai-api", "chatgpt"],
        "cost_forecast": {"primary_api": {"monthly_eur": 150.0}, "assistant": {"monthly_eur": 480.0}},
        "matched_cases": [{"canonical_tools": ["openai-api"]}, {"canonical_tools": ["chatgpt"]}],
        "privacy_key": "standard",
    },
    {
        "name": "seat only, regulated",
        "ranked_tools": ["ms-copilot", "azure-openai"],
        "cost_forecast": {"primary_api": {"monthly_eur": 187.5}, "assistant": {"monthly_eur": 900.0}},
        "matched_cases": [{"canonical_tools": ["azure-openai"]}, {"canonical_tools": ["ms-copilot"]}],
        "privacy_key": "regulated",
    },
    {
        "name": "free/OSS tools only — no cost figures at all",
        "ranked_tools": ["langchain", "chroma"],
        "cost_forecast": {"primary_api": None, "assistant": None},
        "matched_cases": [{"canonical_tools": ["langchain"]}],
        "privacy_key": "standard",
    },
    {
        "name": "empty result — nothing cleared the filter",
        "ranked_tools": [],
        "cost_forecast": {"primary_api": None, "assistant": None},
        "matched_cases": [],
        "privacy_key": "regulated",
    },
]

for case in EVAL_CASES:
    result = generate_summary(
        ranked_tools=case["ranked_tools"], cost_forecast=case["cost_forecast"],
        matched_cases=case["matched_cases"], privacy_key=case["privacy_key"],
    )
    print(f"--- {case['name']} ({result['duration_seconds']}s, "
          f"{result['completion_tokens']} completion tokens) ---")
    print(result["text"])
    print()
