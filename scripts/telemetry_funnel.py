"""
Card P.14 -- Headline metrics + funnel, computed straight from data/telemetry.log.

Formalises the inline snippets already written in
14-Build-Guide-Epic3-Blueprint-UI-v1.md (Cards 3.3 and 3.4) into one reusable
script, so the Week-4 write-up numbers can be regenerated at any time instead
of re-typed from a one-off terminal paste.

Run from the repo root:
    python3 scripts/telemetry_funnel.py
"""
import json
from collections import Counter
from pathlib import Path

LOG_PATH = Path("data/telemetry.log")


def load_events(path: Path = LOG_PATH) -> list[dict]:
    return [json.loads(line) for line in path.open() if line.strip()]


def headline_metrics(events: list[dict]) -> dict:
    """Card 3.3/3.4's per-session numbers: trust-score median, average
    time-to-results, average LLM latency."""
    scores = sorted(e["trust_score"] for e in events if e["event"] == "survey_submitted")
    shows = [e for e in events if e["event"] == "results_shown"]
    llm_calls = [e for e in events if e["event"] == "llm_summary_generated"]

    median_trust = scores[len(scores) // 2] if scores else None
    avg_time_to_results = (sum(e["elapsed_seconds"] for e in shows) / len(shows)
                            if shows else None)
    durations = [e["duration_seconds"] for e in llm_calls]
    avg_llm_latency = sum(durations) / len(durations) if durations else None

    return {
        "trust_scores": scores,
        "trust_score_median": median_trust,
        "completed_sessions": len(shows),
        "avg_time_to_results_s": round(avg_time_to_results, 1) if avg_time_to_results else None,
        "llm_calls": len(durations),
        "avg_llm_latency_s": round(avg_llm_latency, 2) if avg_llm_latency else None,
        "min_llm_latency_s": round(min(durations), 2) if durations else None,
        "max_llm_latency_s": round(max(durations), 2) if durations else None,
    }


def funnel(events: list[dict]) -> dict:
    """Card P.14 step 2 -- three telemetry stages read together, not as three
    independent counts: viewed -> exported -> said they'd use it."""
    counts = Counter(e["event"] for e in events)
    viewed = counts.get("results_shown", 0)
    exported = counts.get("export_clicked", 0)
    surveys = [e for e in events if e["event"] == "survey_submitted"]
    would_use = sum(1 for e in surveys if e.get("net_value") == "Yes")

    return {
        "viewed": viewed,
        "exported": exported,
        "export_rate_pct": round(100 * exported / viewed) if viewed else None,
        "survey_responses": len(surveys),
        "would_use": would_use,
        "would_use_rate_pct": round(100 * would_use / len(surveys)) if surveys else None,
    }


def main():
    events = load_events()
    hm = headline_metrics(events)
    fn = funnel(events)

    print(f"{hm['trust_scores']} -> trust-score median: {hm['trust_score_median']}"
          f" ({len(hm['trust_scores'])} responses)")
    print(f"{hm['completed_sessions']} completed sessions, "
          f"avg time to results: {hm['avg_time_to_results_s']}s")
    print(f"LLM: avg {hm['avg_llm_latency_s']}s over {hm['llm_calls']} calls "
          f"(min {hm['min_llm_latency_s']}, max {hm['max_llm_latency_s']})")
    print(f"Funnel: {fn['viewed']} viewed -> {fn['exported']} exported "
          f"({fn['export_rate_pct']}% of viewers) -> {fn['survey_responses']} survey responses, "
          f"{fn['would_use']} said they'd use it ({fn['would_use_rate_pct']}% of respondents)")


if __name__ == "__main__":
    main()
