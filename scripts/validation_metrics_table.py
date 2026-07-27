"""
Card P.14 -- Validation Metrics Final table.

Combines telemetry_funnel.py (headline metrics + funnel), credible_interval.py
(Beta-posterior CI), and compliance_check.py (regulated-profile pipeline
check) into the one "## Validation Metrics -- Final" table from
17-Build-Guide-Package-Pitch-Week4-v1.md, so the whole table can be
regenerated with a single command instead of copy-pasted by hand from three
separate script outputs.

Run from the repo root:
    python3 scripts/validation_metrics_table.py

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

from scripts.telemetry_funnel import load_events, headline_metrics, funnel
from scripts.credible_interval import credible_interval

# Known-good P9 dry-run record (Capstone Plan/Build Guide/
# P9-Backend-Dry-Run-Results-v1.md) -- used as a fallback when the live
# pipeline infra isn't available in the current environment.
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


def build_rows(live_compliance: bool):
    events = load_events()
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-compliance", action="store_true",
                         help="Use the recorded P9 dry-run result instead of "
                              "re-running the live pipeline.")
    parser.add_argument("--markdown", action="store_true",
                         help="Print as a markdown pipe-table instead of plain text.")
    args = parser.parse_args()

    rows, details = build_rows(live_compliance=not args.skip_compliance)

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
