"""
Card P.14 -- Headline metrics + funnel, computed straight from data/telemetry.log.

Formalises the inline snippets already written in
14-Build-Guide-Epic3-Blueprint-UI-v1.md (Cards 3.3 and 3.4) into one reusable
script, so the Week-4 write-up numbers can be regenerated at any time instead
of re-typed from a one-off terminal paste.

Run from the repo root. To reproduce the PUBLISHED Card P.14 figures you must
pass BOTH bounds — this exact command:

    python3 scripts/telemetry_funnel.py --since "2026-07-27 23:00" \
                                        --until "2026-07-28 01:31"

WHY BOTH BOUNDS EXIST
The log is append-only and spans the whole project, so it mixes our own
development runs with real test sessions across several builds. Run bare it
answers "everything that ever happened", which measures nothing cleanly.

--since alone is NOT enough, and this bit us. The final real-user round closed
with its last survey at 2026-07-28 01:30:41. We then kept using the app —
verifying fixes, reproducing a reported bug, testing the Cloud deploy — and every
one of those runs appended a results_shown event. Because "exported" stayed at 10
while "viewed" kept climbing, the reported export rate fell from the published
83% (10/12) to 56% (10/18) within a day, with no survey attached to any of the
new events. A published headline figure had silently stopped reproducing.

Caught by Gabi on 2026-07-28 by running the documented command rather than
trusting the write-up. --until freezes the round so the figures hold no matter
how much the app is used afterwards.

If you run this without both bounds, it will tell you so and print how many
post-round events it just folded in.
"""
import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("data/telemetry.log")

# The frozen window the published Card P.14 figures are computed over: the final
# 8-participant round, opened before the first participant session and closed
# immediately after the last survey (01:30:41). Defined here so the scripts, the
# warning text and the write-up can never drift apart — if this ever needs to
# change, change it here and re-run both scripts.
P14_SINCE = "2026-07-27 23:00"
P14_UNTIL = "2026-07-28 01:31"
P14_COMMAND = f'--since "{P14_SINCE}" --until "{P14_UNTIL}"'


def warn_if_unbounded(events: list[dict], since: str | None, until: str | None) -> None:
    """
    Say so, loudly, when a run cannot reproduce the published figures.

    The failure this prevents: someone runs the script with --since only (or
    nothing), reads the funnel, and quietly believes a number that disagrees with
    the write-up and the deck. Counting the post-round events makes the cause
    obvious instead of leaving them to diff two outputs.
    """
    if since == P14_SINCE and until == P14_UNTIL:
        return
    cutoff = datetime.fromisoformat(P14_UNTIL).timestamp()
    after = [e for e in events if e["timestamp"] > cutoff]
    # sys.argv[0], not __file__ — this helper is shared with credible_interval.py,
    # so hardcoding this file's path would tell the reader to run the wrong script.
    invoked = Path(sys.argv[0]).name or "telemetry_funnel.py"
    print("!" * 74)
    print("NOT the published Card P.14 window — these numbers will not match the")
    print("write-up or the pitch deck. For the published figures run:")
    print(f"    python3 scripts/{invoked} --p14")
    print(f"    (equivalent to: {P14_COMMAND})")
    if after:
        kinds = Counter(e["event"] for e in after)
        surveys = kinds.get("survey_submitted", 0)
        print(f"\nThis run includes {len(after)} event(s) recorded AFTER the round closed"
              f" ({P14_UNTIL}),")
        print(f"including {kinds.get('results_shown', 0)} results_shown and {surveys}"
              " survey_submitted.")
        if not surveys:
            print("No surveys among them, so that is development/QA traffic inflating")
            print("the 'viewed' denominator — it is not additional user testing.")
    print("!" * 74 + "\n")


def load_events(path: Path = LOG_PATH, since: str | None = None,
                until: str | None = None) -> list[dict]:
    events = [json.loads(line) for line in path.open() if line.strip()]
    events.sort(key=lambda e: e["timestamp"])
    if since:
        events = [e for e in events
                  if e["timestamp"] >= datetime.fromisoformat(since).timestamp()]
    if until:
        events = [e for e in events
                  if e["timestamp"] <= datetime.fromisoformat(until).timestamp()]
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
    ap = argparse.ArgumentParser(
        epilog=f'Published Card P.14 figures: {P14_COMMAND}')
    ap.add_argument("--since", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or after this local time — use to "
                         "isolate one test round from development runs")
    ap.add_argument("--until", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or before this local time — required "
                         "as well as --since, or later development runs drift into "
                         "a closed round and change the reported rates")
    ap.add_argument("--p14", action="store_true",
                    help=f"shorthand for the published window ({P14_COMMAND})")
    args = ap.parse_args()

    since, until = args.since, args.until
    if args.p14:
        since, until = P14_SINCE, P14_UNTIL

    # Warn against the FULL log, before filtering, so the post-round count is real.
    warn_if_unbounded(load_events(), since, until)

    events = load_events(since=since, until=until)
    hm = headline_metrics(events)
    fn = funnel(events)

    if since or until:
        print(f"[window: {since or 'start'} .. {until or 'end'} — {len(events)} events]")
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
