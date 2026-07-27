"""
Card P.14 -- Headline metrics + funnel, computed straight from data/telemetry.log.

Formalises the inline snippets already written in
14-Build-Guide-Epic3-Blueprint-UI-v1.md (Cards 3.3 and 3.4) into one reusable
script, so the Week-4 write-up numbers can be regenerated at any time instead
of re-typed from a one-off terminal paste.

Run from the repo root:
    python3 scripts/telemetry_funnel.py
    python3 scripts/telemetry_funnel.py --since "2026-07-27 23:00"

WHY --since EXISTS (added 2026-07-28)
The log is append-only and spans the whole project, so it mixes our own
development runs with real test sessions, across several different builds. Run
bare, it answers "everything that ever happened", which measures nothing
cleanly. The final real-user round (8 participants, the build we submitted) is
isolated with --since; the boundary is defensible because a 5-hour gap separates
that round from the previous activity. Every figure in
PM & Ethics/P14-Validation-Metrics-Final-v1.md is reproducible with the exact
command quoted at the top of that file.
"""
import argparse
import json
import statistics
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("data/telemetry.log")


def load_events(path: Path = LOG_PATH, since: str | None = None) -> list[dict]:
    events = [json.loads(line) for line in path.open() if line.strip()]
    events.sort(key=lambda e: e["timestamp"])
    if since:
        cutoff = datetime.fromisoformat(since).timestamp()
        events = [e for e in events if e["timestamp"] >= cutoff]
    return events


def headline_metrics(events: list[dict]) -> dict:
    """Card 3.3/3.4's per-session numbers: trust-score median, average
    time-to-results, average LLM latency."""
    scores = sorted(e["trust_score"] for e in events if e["event"] == "survey_submitted")
    shows = [e for e in events if e["event"] == "results_shown"]
    llm_calls = [e for e in events if e["event"] == "llm_summary_generated"]

    # Was scores[len(scores)//2], which returns the UPPER of the two middle values
    # at even n rather than the median. It happened to agree at n=5 and at the
    # final round's n=8 (both middle values are 5), but it would have been wrong
    # the moment the two middles differed. statistics.median averages them;
    # displayed as an int when the result is whole, since trust is a 1-5 ordinal.
    median_trust = statistics.median(scores) if scores else None
    if median_trust is not None and float(median_trust).is_integer():
        median_trust = int(median_trust)
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or after this local time — use to "
                         "isolate one test round from development runs")
    args = ap.parse_args()

    events = load_events(since=args.since)
    hm = headline_metrics(events)
    fn = funnel(events)

    if args.since:
        print(f"[window: events from {args.since} onwards — {len(events)} events]")
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
