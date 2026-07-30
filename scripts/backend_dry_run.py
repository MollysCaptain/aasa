"""
Card P.9 — Full backend dry run harness.

Runs the 3 agreed test profiles through the REAL pipeline end to end
(normalise -> embed/retrieve -> privacy filter -> rank -> cost -> LLM summary),
prints every field of each result, runs a handful of automated sanity checks
straight from P.9's "read the output like a skeptical stranger" list, and
writes a dated results + defect-list markdown you and Gabi finish together.

Run from the repo root, in the environment that has the model cache + GROQ key:

    python scripts/backend_dry_run.py

Needs (same as running the app): a populated ./chroma_store, the
all-MiniLM-L6-v2 embedding model reachable/cached, and GROQ_API_KEY in .env.
It does NOT modify any app code or data — read-only except for writing the
results markdown below.
"""
import io
import sys
import time
import traceback
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

# Running `python scripts/backend_dry_run.py` puts scripts/ on sys.path[0], NOT
# the repo root — so Python looks for an "app" package *inside* scripts/ and
# raises ModuleNotFoundError. Every other script that imports app has this two
# liner (compliance_check.py, credible_interval.py, validation_metrics_table.py,
# eval_prompt.py); this one didn't, so the exact command in its own docstring —
# and the FIRST of the three verification commands in the README — has never
# worked from a clean shell. Added 2026-07-30 (P.22), found by running it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.logic.pricing import PRICING  # noqa: E402

# Where the recorded P.9 result actually lives. Corrected 2026-07-30 (P.22):
# this pointed at "Capstone Plan/Build Guide/", which is where the file was
# generated on 2026-07-21 and NOT where it has lived since the docs were
# reorganised. The path was never updated, so the first run after the move
# silently recreated a stale duplicate in the old folder — found by running the
# script, not by reading it.
RESULTS_PATH = Path("PM & Ethics/P9-Backend-Dry-Run-Results-v1.md")

# The 3 profiles agreed for P.9 (guide 15). Values use the REAL option keys
# from app/data/options.py — note the guide's "Data Analysis" is written here
# as the actual workflow value "Data & Analytics".
PROFILES = [
    {
        "name": "Profile 1 — everyday happy path",
        "why": "Common query, standard posture — the baseline everything else is compared against.",
        "inputs": {"workflow": "Customer Service", "industry": "Technology",
                   "org_size": "startup", "privacy": "standard", "budget": 800},
    },
    {
        "name": "Profile 2 — regulated filter stress test",
        "why": "Regulated posture must strip consumer-only tools (e.g. consumer Gemini) before ranking.",
        "inputs": {"workflow": "Data & Analytics", "industry": "Healthcare",
                   "org_size": "ent", "privacy": "regulated", "budget": 5000},
    },
    {
        "name": "Profile 3 — sparse / graceful-degradation case",
        "why": "Deliberately thin combination — checks the app degrades gracefully, not crashes, on few matches.",
        "inputs": {"workflow": "Facilities & EHS", "industry": "Agriculture",
                   "org_size": "solo", "privacy": "regulated", "budget": 150},
    },
]

CONSUMER_ONLY_IDS = {"gemini"}  # consumer tools the regulated filter must exclude (extend if needed)


def _label(tool_id: str) -> str:
    return PRICING.get(tool_id, {}).get("label", tool_id)


def _fmt_result(result: dict) -> str:
    """Human-readable dump of every field of a run_pipeline() result."""
    out = []
    out.append("RECOMMENDED STACK:")
    for i, t in enumerate(result["recommended_stack"], 1):
        out.append(f"  {i}. {_label(t)}  [{t} · {PRICING.get(t, {}).get('model', '?')}]")
    if not result["recommended_stack"]:
        out.append("  (empty — nothing cleared the filters)")

    cf = result["cost_forecast"]
    out.append("\nCOST FORECAST:")
    p, a = cf.get("primary_api"), cf.get("assistant")
    out.append(f"  primary_api: {p['tool'] if p else None}"
               + (f" — €{p['monthly_eur']}/mo" if p and p.get('monthly_eur') is not None else ""))
    out.append(f"  assistant:   {a['tool'] if a else None}"
               + (f" — €{a['monthly_eur']}/mo" if a and a.get('monthly_eur') is not None else ""))
    out.append(f"  total_monthly_eur: {cf.get('total_monthly_eur')}")
    out.append(f"  budget: {cf.get('budget')}   within_budget: {cf.get('within_budget')}   "
               f"delta: {cf.get('budget_delta_eur')}")

    out.append("\nTOOL COSTS (per ranked tool):")
    for tid, c in result.get("tool_costs", {}).items():
        out.append(f"  {tid}: €{c.get('monthly_eur')} ({c.get('model')})")

    out.append(f"\nMATCHED CASES ({len(result['matched_cases'])}):")
    for c in result["matched_cases"][:8]:
        out.append(f"  - {c.get('organization')} | {c.get('industry')} | "
                   f"tools={c.get('canonical_tools')} | {c.get('source_url')}")
    if len(result["matched_cases"]) > 8:
        out.append(f"  ... (+{len(result['matched_cases']) - 8} more)")

    out.append("\nSUMMARY TEXT:")
    out.append("  " + (result.get("summary_text") or "(none)").replace("\n", "\n  "))

    out.append(f"\nQUERY ECHO: {result.get('query')}")
    out.append(f"PROJECT NAME: {result.get('project_name')!r}")
    out.append(f"LLM METRICS: {result.get('llm_metrics')}")
    return "\n".join(out)


def _auto_checks(profile: dict, result: dict) -> list[str]:
    """P.9 step-3 checks, expressed as automated assertions. Returns a list of
    'PASS/FAIL — message' strings (FAIL is a candidate defect, not a crash)."""
    checks = []
    stack = result["recommended_stack"]
    cf = result["cost_forecast"]

    # 1. Regulated posture must exclude consumer-only tools.
    if profile["inputs"]["privacy"] == "regulated":
        leaked = [t for t in stack if t in CONSUMER_ONLY_IDS]
        checks.append(("PASS" if not leaked else "FAIL")
                      + f" — regulated filter: consumer-only tools in stack = {leaked or 'none'}")

    # 2. Cost is one primary API + one assistant, and total is their sum (not a
    #    combined-everything figure).
    p, a = cf.get("primary_api"), cf.get("assistant")
    parts = [x["monthly_eur"] for x in (p, a) if x and x.get("monthly_eur") is not None]
    expected = round(sum(parts), 2) if parts else None
    checks.append(("PASS" if cf.get("total_monthly_eur") == expected else "FAIL")
                  + f" — total ({cf.get('total_monthly_eur')}) == primary+assistant ({expected})")

    # 3. Budget flag is internally consistent.
    if cf.get("budget") is not None and cf.get("total_monthly_eur") is not None:
        want = cf["total_monthly_eur"] <= cf["budget"]
        checks.append(("PASS" if cf.get("within_budget") == want else "FAIL")
                      + f" — within_budget flag matches total vs budget")

    # 4. Summary must not invent a tool outside the ranked list. Soft check:
    #    flag any OTHER known tool label that appears in the summary but isn't ranked.
    summary = (result.get("summary_text") or "").lower()
    ranked_labels = {_label(t).lower() for t in stack}
    intruders = [PRICING[t]["label"] for t in PRICING
                 if PRICING[t]["label"].lower() in summary and PRICING[t]["label"].lower() not in ranked_labels]
    checks.append(("PASS" if not intruders else "REVIEW")
                  + f" — summary mentions only ranked tools (possible extras: {intruders or 'none'})")
    return checks


def main():
    # Imported here so an import-time failure (e.g. missing model/collection)
    # is caught and reported cleanly rather than crashing at module load.
    from app.pipeline import run_pipeline

    md = [f"# P.9 — Full Backend Dry Run — Results",
          f"*Generated {date.today().isoformat()} by `scripts/backend_dry_run.py`. "
          f"Read every section below with Gabi, then complete the defect list at the end.*", ""]

    for profile in PROFILES:
        header = f"## {profile['name']}"
        print("\n" + "=" * 78)
        print(header)
        print(profile["why"])
        print(f"INPUTS: {profile['inputs']}")
        md += [header, f"_{profile['why']}_", "", f"**Inputs:** `{profile['inputs']}`", ""]
        try:
            t0 = time.time()
            result = run_pipeline(dict(profile["inputs"]))
            dump = _fmt_result(result)
            checks = _auto_checks(profile, result)
            print(dump)
            print("\nAUTOMATED CHECKS:")
            for c in checks:
                print("  " + c)
            print(f"\n(elapsed {time.time()-t0:.1f}s)")
            md += ["```", dump, "```", "", "**Automated checks:**",
                   *[f"- {c}" for c in checks], ""]
        except Exception:
            tb = traceback.format_exc()
            print("!!! PROFILE FAILED !!!\n" + tb)
            md += ["**⚠️ THIS PROFILE FAILED TO RUN:**", "```", tb, "```", ""]

    md += ["## Defect list (fill in together)", "",
           "| # | Severity | Description | Owner | Fix-before-Week-3? |",
           "|---|---|---|---|---|",
           "| 1 | | | | |", "| 2 | | | | |", "| 3 | | | | |", "",
           "## Go / no-go for Week 3",
           "- [ ] All 3 profiles ran and output read by both people",
           "- [ ] Profile 2 regulated filter confirmed excluding consumer tools",
           "- [ ] 5–8 real testers confirmed scheduled (Card P.2)",
           "- [ ] Decision recorded: **on track / not on track** for Week 3 — _(write it here)_"]

    # Refuse to clobber the recorded result. Added 2026-07-30 (P.22), same
    # refuse-first idiom as scripts/rebuild_knowledge_base.py.
    #
    # RESULTS_PATH is a COMMITTED document that ends in a defect list and a
    # go/no-go decision meant to be filled in by hand. Now that the path is
    # correct, a bare run would overwrite whatever a human wrote there with a
    # blank template — losing exactly the part of the document that isn't
    # reproducible. Everything above has already been printed to stdout, so
    # declining to write costs nothing.
    print("\n" + "=" * 78)
    if RESULTS_PATH.exists() and "--overwrite" not in sys.argv:
        print(f"NOT written — {RESULTS_PATH} already exists.\n")
        print("That file is committed and its defect list / go-no-go section is")
        print("filled in by hand, so overwriting it would replace human judgement")
        print("with a blank template. The full run output is above.\n")
        print("If you do want to regenerate it (e.g. after a pipeline change):")
        print("    python scripts/backend_dry_run.py --overwrite")
        print("...and check `git diff` before committing, so you can see exactly")
        print("which numbers moved and confirm nothing hand-written was lost.")
        return 0

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text("\n".join(md), encoding="utf-8")
    print(f"Results written to: {RESULTS_PATH}")
    print("Review `git diff` before committing — the defect list is now blank.")


if __name__ == "__main__":
    sys.exit(main())
