"""
Card P.14 -- Beta-posterior credible interval for a small-sample yes/no rate.

At n=5-8, a bare percentage implies false precision (one person flipping
their answer swings the rate by ~15-20 points). A Beta(1,1) uninformative
prior gives the honest range for the true rate instead.

Run after real testing: python3 scripts/credible_interval.py
"""
import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from scipy import stats

LOG_PATH = Path("data/telemetry.log")


def credible_interval(successes: int, total: int, credibility: float = 0.90):
    """
    Posterior after observing the data is Beta(1 + successes, 1 + failures);
    its interval is the honest range for the true rate, appropriately wide
    at small n.
    """
    failures = total - successes
    lower = stats.beta.ppf((1 - credibility) / 2, 1 + successes, 1 + failures)
    upper = stats.beta.ppf(1 - (1 - credibility) / 2, 1 + successes, 1 + failures)
    return lower, upper


def report(label: str, successes: int, total: int, credibility: float = 0.90):
    if total == 0:
        print(f"{label}: no data yet.")
        return
    point_estimate = successes / total
    lower, upper = credible_interval(successes, total, credibility)
    print(f"{label}: {point_estimate:.0%} ({successes}/{total}), "
          f"{credibility:.0%} credible interval: {lower:.0%}-{upper:.0%}")


def main():
    # --since mirrors scripts/telemetry_funnel.py — the log spans the whole
    # project and several builds, so a bare run pools development runs with real
    # sessions. See that script's docstring for why the final round is windowed.
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or after this local time")
    args = ap.parse_args()

    events = [json.loads(line) for line in LOG_PATH.open() if line.strip()]
    events.sort(key=lambda e: e["timestamp"])
    if args.since:
        cutoff = datetime.fromisoformat(args.since).timestamp()
        events = [e for e in events if e["timestamp"] >= cutoff]
        print(f"[window: events from {args.since} onwards — {len(events)} events]")
    counts = Counter(e["event"] for e in events)
    surveys = [e for e in events if e["event"] == "survey_submitted"]

    # Net value: survey respondents who said "Yes" to net value.
    would_use = sum(1 for e in surveys if e.get("net_value") == "Yes")
    report("Net value", would_use, len(surveys))

    # Export rate: viewers (results_shown) who went on to export.
    viewed = counts.get("results_shown", 0)
    exported = counts.get("export_clicked", 0)
    report("Blueprint export rate", exported, viewed)


if __name__ == "__main__":
    main()
