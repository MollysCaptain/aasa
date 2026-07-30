"""
Card P.14 -- Beta-posterior credible interval for a small-sample yes/no rate.

At n=5-8, a bare percentage implies false precision (one person flipping
their answer swings the rate by ~15-20 points). A Beta(1,1) uninformative
prior gives the honest range for the true rate instead.

To reproduce the PUBLISHED Card P.14 intervals, pass BOTH bounds — or use the
--p14 shorthand:

    python3 scripts/credible_interval.py --p14

--since alone is not enough. The export rate is measured against results_shown,
and the log is append-only: development runs after the round closed keep pushing
that denominator up (published 83% -> 56% within a day of the write-up). The
window constants are imported from telemetry_funnel.py so the two scripts can
never disagree about which window the published figures use.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from scipy import stats

# Single source of truth for the published window, the warning text and the event
# loader — see telemetry_funnel.py. Imported rather than duplicated so the two
# scripts cannot drift apart and quote different windows for the same figures.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.telemetry_funnel import (  # noqa: E402
    P14_SINCE, P14_UNTIL, P14_COMMAND, load_events, warn_if_unbounded,
)

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
    ap = argparse.ArgumentParser(
        epilog=f"Published Card P.14 figures: {P14_COMMAND}")
    ap.add_argument("--since", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or after this local time")
    ap.add_argument("--until", metavar="'YYYY-MM-DD HH:MM'",
                    help="only count events at or before this local time — required "
                         "as well as --since; without it the export-rate denominator "
                         "keeps growing with later development runs")
    ap.add_argument("--p14", action="store_true",
                    help=f"shorthand for the published window ({P14_COMMAND})")
    args = ap.parse_args()

    since, until = args.since, args.until
    if args.p14:
        since, until = P14_SINCE, P14_UNTIL

    # Same warning as telemetry_funnel.py, from the same shared helper: the export
    # rate is the figure this drift actually moves, so it matters most here.
    warn_if_unbounded(load_events(), since, until)

    events = load_events(since=since, until=until)
    if since or until:
        print(f"[window: {since or 'start'} .. {until or 'end'} — {len(events)} events]")
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
