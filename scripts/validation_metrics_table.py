"""
Card P.14 -- Validation Metrics Final table.

Combines telemetry_funnel.py (headline metrics + funnel), credible_interval.py
(Beta-posterior CI), and compliance_check.py (regulated-profile pipeline
check) into the one "## Validation Metrics -- Final" table from
17-Build-Guide-Package-Pitch-Week4-v1.md, so the whole table can be
regenerated with a single command instead of copy-pasted by hand from three
separate script outputs.

Run from the repo root. To reproduce the PUBLISHED Card P.14 table you must pass
the window, exactly as with the other two metrics scripts:

    python3 scripts/validation_metrics_table.py --p14

WHY THIS FLAG EXISTS HERE TOO -- found 2026-07-30, P.22
This script was missed when telemetry_funnel.py and credible_interval.py were
hardened on 2026-07-28. It called load_events() with no bounds, accepted no
--since/--until, and printed no warning -- so the one command documented in the
README as regenerating "the whole P.14 results table" silently produced a
DIFFERENT table from the one in the write-up and on the slides:

    published (--p14)      23%->83% export, 94%->100% net value, 4/5->5/5 trust,
    vs. bare run           106 sessions / 18 responses instead of 12 / 8

Same root cause Gabi caught in the funnel script: data/telemetry.log is
append-only, so development runs after the user-test round closed keep inflating
the denominators. This is the third and last script that reads that log.

The compliance row needs the full ML/LLM stack (chroma_store, the
all-MiniLM-L6-v2 model, GROQ_API_KEY) to re-run the live pipeline. If that's
not set up in the current environment, pass --skip-compliance to fall back to
the already-recorded P9 dry-run result instead:

    python3 scripts/validation_metrics_table.py --skip-compliance

Add --markdown to print a pipe-table instead of a plain-text one (handy for
pasting straight into a Build Guide doc).
"""
import argparse
import sys
from pathlib import Path

# Make sure the repo root (this file's parent's parent) is importable
# regardless of where/how this script is invoked from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.telemetry_funnel import (
    P14_SINCE, P14_UNTIL, P14_COMMAND,
    load_events, headline_metrics, funnel, warn_if_unbounded,
)
from scripts.credible_interval import credible_interval

# Known-good P9 dry-run record (PM & Ethics/P9-Backend-Dry-Run-Results-v1.md)
# -- used as a fallback when the live pipeline infra isn't available in the
# current environment. (Path corrected 2026-07-30: this comment said
# "Capstone Plan/Build Guide/", where the file has never lived.)
P9_FALLBACK = [
    ("Profile 2 -- Healthcare/ent/regulated",
     ["aws-bedrock", "aws-platform", "google-cloud", "ibm-watsonx", "ms-dynamics"]),
    ("Profile 3 -- Agriculture/solo/regulated",
     ["azure-platform", "aws-platform", "azure-openai", "aws-bedrock", "google-cloud"]),
]

TRUST_TARGET = 4
NET_VALUE_TARGET = 0.70
EXPORT_RATE_TARGET = 0.40


def compliance_pass_rate(live: bool):
    """Returns (passed, total, details) where details is a list of
    (name, stack, violations)."""
    from app.logic.filter import GOVERNABLE_FOR_REGULATED

    details = []
    if live:
        from scripts.compliance_check import REGULATED_PROFILES
        from app.pipeline import run_pipeline
        for profile in REGULATED_PROFILES:
            result = run_pipeline(dict(profile["inputs"]))
            stack = result["recommended_stack"]
            violations = [t for t in stack if t not in GOVERNABLE_FOR_REGULATED]
            details.append((profile["name"], stack, violations))
    else:
        for name, stack in P9_FALLBACK:
            violations = [t for t in stack if t not in GOVERNABLE_FOR_REGULATED]
            details.append((name, stack, violations))

    passed = sum(1 for _, _, v in details if not v)
    return passed, len(details), details


def met_label(point_ok: bool, ci_lower: float, target: float) -> str:
    if not point_ok:
        return "No"
    if ci_lower < target:
        return "Yes (CI overlaps target)"
    return "Yes"


def build_rows(live_compliance: bool, since: str | None = None,
               until: str | None = None):
    events = load_events(since=since, until=until)
    hm = headline_metrics(events)
    fn = funnel(events)

    nv_lower, nv_upper = credible_interval(fn["would_use"], fn["survey_responses"])
    ex_lower, ex_upper = credible_interval(fn["exported"], fn["viewed"])

    passed, total, details = compliance_pass_rate(live_compliance)
    compliance_pct = round(100 * passed / total) if total else None

    trust_median = hm["trust_score_median"] or 0
    nv_rate = (fn["would_use_rate_pct"] or 0) / 100
    ex_rate = (fn["export_rate_pct"] or 0) / 100

    rows = [
        ("Trust score (median)", f"≥{TRUST_TARGET}/5", f"{hm['trust_score_median']}/5",
         "— (ordinal, not a rate)",
         "Yes" if trust_median >= TRUST_TARGET else "No"),
        ("Net value (% yes)", f"≥{NET_VALUE_TARGET:.0%}",
         f"{fn['would_use_rate_pct']}% ({fn['would_use']}/{fn['survey_responses']})",
         f"{nv_lower:.0%}–{nv_upper:.0%}",
         met_label(nv_rate >= NET_VALUE_TARGET, nv_lower, NET_VALUE_TARGET)),
        ("Blueprint export rate", f"≥{EXPORT_RATE_TARGET:.0%}",
         f"{fn['export_rate_pct']}% ({fn['exported']}/{fn['viewed']})",
         f"{ex_lower:.0%}–{ex_upper:.0%}",
         met_label(ex_rate >= EXPORT_RATE_TARGET, ex_lower, EXPORT_RATE_TARGET)),
        ("Compliance-rule pass rate", "100%",
         f"{compliance_pct}% ({passed}/{total} regulated profiles)",
         "— (deterministic)",
         "Yes" if compliance_pct == 100 else "No"),
        ("Avg. LLM latency", "— (informational)",
         f"{hm['avg_llm_latency_s']}s ({hm['llm_calls']} calls)", "—", "—"),
        ("Sample size", "5–8 real testers",
         f"{hm['completed_sessions']} sessions / {fn['survey_responses']} survey responses",
         "not powered for comparative claims", "—"),
    ]
    return rows, details


def print_plain(rows):
    headers = ["Metric", "Target", "Actual", "90% Credible Interval", "Met?"]
    table = [headers] + [list(map(str, r)) for r in rows]
    widths = [max(len(row[i]) for row in table) for i in range(5)]

    def fmt(row):
        return " | ".join(row[i].ljust(widths[i]) for i in range(5))

    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for row in table[1:]:
        print(fmt(row))


def print_markdown(rows):
    headers = ["Metric", "Target", "Actual", "90% Credible Interval", "Met?"]
    print("| " + " | ".join(headers) + " |")
    print("|" + "|".join(["---"] * 5) + "|")
    for r in rows:
        print("| " + " | ".join(str(c) for c in r) + " |")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=f"Published Card P.14 table: {P14_COMMAND}")
    parser.add_argument("--skip-compliance", action="store_true",
                         help="Use the recorded P9 dry-run result instead of "
                              "re-running the live pipeline.")
    parser.add_argument("--markdown", action="store_true",
                         help="Print as a markdown pipe-table instead of plain text.")
    parser.add_argument("--since", metavar="'YYYY-MM-DD HH:MM'",
                         help="only count events at or after this local time")
    parser.add_argument("--until", metavar="'YYYY-MM-DD HH:MM'",
                         help="only count events at or before this local time — "
                              "required as well as --since, or later development "
                              "runs drift into a closed round")
    parser.add_argument("--p14", action="store_true",
                         help=f"shorthand for the published window ({P14_COMMAND})")
    args = parser.parse_args()

    since, until = args.since, args.until
    if args.p14:
        since, until = P14_SINCE, P14_UNTIL

    # Warn against the FULL log, before filtering, so the post-round count is real.
    warn_if_unbounded(load_events(), since, until)

    rows, details = build_rows(live_compliance=not args.skip_compliance,
                               since=since, until=until)
    if since or until:
        print(f"[window: {since or 'start'} .. {until or 'end'}]\n")

    print("Compliance check detail:")
    for name, stack, violations in details:
        status = "PASS" if not violations else "FAIL"
        print(f"  {name}: {status} (violations: {violations or 'none'})")
    print()

    if args.markdown:
        print_markdown(rows)
    else:
        print_plain(rows)


if __name__ == "__main__":
    main()
