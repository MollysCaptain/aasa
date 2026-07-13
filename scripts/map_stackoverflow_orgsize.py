"""
Update C (18-Build-Guide-Updates-Epic1-2-v1.md) — ground app/logic/cost.py's
ASSUMED_SEATS in real survey data instead of hand-picked constants.

Crosstabs the Stack Overflow Developer Survey's OrgSize (QID16) against
AISelect (QID78, "Do you currently use AI tools in your development
process?") to compute a per-band AI-tool-adoption rate, then multiplies that
rate against a still-illustrative base-headcount assumption per band. This is
a seat-utilization PROXY, not a real seats-licensed or spend figure — the
survey has no billing/spend question at all (it's a developer-attitudes
survey). See the guide doc for the full reasoning and the band-mapping
judgment call.

Run directly:  python3 scripts/map_stackoverflow_orgsize.py
Reads:         data/StackOverflow/results.csv (gitignored, not in the repo —
               same third-party-data pattern as data/use-cases.csv)
Prints:        adoption rate + sample size per band, and the final
               ASSUMED_SEATS dict ready to paste into app/logic/cost.py
"""
import pandas as pd

RESULTS_PATH = "data/StackOverflow/results.csv"

# Real OrgSize bracket labels -> our 5 bands. Not a clean 1:1 mapping — the
# survey's bracket boundaries don't line up with ours (solo 1-4 / startup
# 5-49 / smb 50-249 / mid 250-999 / ent 1000+). This is a documented judgment
# call, not a guess — see the guide doc's "Actual mapping and computed
# rates" section for the reasoning.
BAND_MAP = {
    "Just me - I am a freelancer, sole proprietor, etc.": "solo",
    "Less than 20 employees": "startup",
    "20 to 99 employees": "smb",
    "100 to 499 employees": "mid",
    "500 to 999 employees": "mid",
    "1,000 to 4,999 employees": "ent",
    "5,000 to 9,999 employees": "ent",
    "10,000 or more employees": "ent",
    # "I don't know" and blank/NaN are deliberately left unmapped (excluded).
}

# Base, still-illustrative headcount assumption per band (unchanged in spirit
# from the old flat ASSUMED_SEATS — just now scaled by a real adoption rate
# instead of being the final number itself).
BASE_HEADCOUNT = {"solo": 4, "startup": 20, "smb": 150, "mid": 600, "ent": 3000}

YES_VALUES = {
    "Yes, I use AI tools daily",
    "Yes, I use AI tools weekly",
    "Yes, I use AI tools monthly or infrequently",
}
NO_VALUES = {"No, and I don't plan to", "No, but I plan to soon"}


def compute_adoption_rates(results_path: str = RESULTS_PATH) -> dict[str, float]:
    df = pd.read_csv(results_path, usecols=["OrgSize", "AISelect"])
    df["band"] = df["OrgSize"].map(BAND_MAP)

    # Only rows with a mappable band AND a clear Yes/No-type answer count —
    # non-responses are excluded from both numerator and denominator, not
    # treated as "No".
    sub = df[df["AISelect"].isin(YES_VALUES | NO_VALUES) & df["band"].notna()].copy()
    sub["is_yes"] = sub["AISelect"].isin(YES_VALUES)

    rates = {}
    for band in ("solo", "startup", "smb", "mid", "ent"):
        b = sub[sub["band"] == band]
        n = len(b)
        if n < 200:
            # Small-sample risk flagged in the guide's pitfalls list — none of
            # our bands actually hit this in practice, but the check stays in
            # so a future re-run against a different survey year gets warned.
            print(f"WARNING: {band} has only {n} respondents — rate may be noisy")
        rates[band] = round(b["is_yes"].mean(), 4) if n else None
        print(f"{band:8s} n={n:6d}  adoption_rate={rates[band]}")
    return rates


def main():
    rates = compute_adoption_rates()
    print("\nASSUMED_SEATS = {")
    for band in ("solo", "startup", "smb", "mid", "ent"):
        seats = round(BASE_HEADCOUNT[band] * rates[band])
        print(f'    "{band}": {seats},  # {BASE_HEADCOUNT[band]} x {rates[band]}')
    print("}")


if __name__ == "__main__":
    main()
