"""
Card P.14 -- Compliance-rule pass-rate check.

Re-runs the REAL pipeline (app.pipeline.run_pipeline -> Card 2.5's
apply_privacy_filter + rank_tools_by_frequency) for every regulated-posture
profile actually tested during P.9-P.11, and checks that no tool outside
GOVERNABLE_FOR_REGULATED ever reached the recommended stack.

This is stricter than scripts/backend_dry_run.py's own sanity check, which
only tests against a narrow CONSUMER_ONLY_IDS = {"gemini"} proxy set. Here we
check against the full, real allowlist the app actually enforces in
app/logic/filter.py.

Run from the repo root (needs the same infra as backend_dry_run.py: a
populated ./chroma_store, the all-MiniLM-L6-v2 model cached, GROQ_API_KEY set):

    python3 scripts/compliance_check.py
"""
from app.logic.filter import GOVERNABLE_FOR_REGULATED

# Every regulated-posture profile actually run during P.9-P.11 (see
# Capstone Plan/Build Guide/P9-Backend-Dry-Run-Results-v1.md). Profile 1 is
# "standard" posture and is not a regulated test case, so it's excluded here.
REGULATED_PROFILES = [
    {
        "name": "Profile 2 -- regulated filter stress test (Healthcare/ent)",
        "inputs": {"workflow": "Data & Analytics", "industry": "Healthcare",
                   "org_size": "ent", "privacy": "regulated", "budget": 5000},
    },
    {
        "name": "Profile 3 -- sparse / graceful-degradation case (Agriculture/solo)",
        "inputs": {"workflow": "Facilities & EHS", "industry": "Agriculture",
                   "org_size": "solo", "privacy": "regulated", "budget": 150},
    },
]


def main():
    from app.pipeline import run_pipeline

    results = []
    for profile in REGULATED_PROFILES:
        result = run_pipeline(dict(profile["inputs"]))
        stack = result["recommended_stack"]
        violations = [t for t in stack if t not in GOVERNABLE_FOR_REGULATED]
        status = "PASS" if not violations else "FAIL"
        print(f"{profile['name']}: {status}")
        print(f"  stack: {stack}")
        print(f"  violations: {violations or 'none'}")
        results.append((profile["name"], status, violations))

    passed = sum(1 for _, status, _ in results if status == "PASS")
    pass_rate = round(100 * passed / len(results)) if results else None
    print(f"\nCompliance-rule pass rate across {len(results)} regulated test "
          f"profiles: {pass_rate}%")


if __name__ == "__main__":
    main()
