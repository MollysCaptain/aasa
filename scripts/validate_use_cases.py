import pandas as pd
import json
import os
import re
import sys

# CaseID format per CASEID_POLICY.md (../ai-use-cases-library/CASEID_POLICY.md):
#   Standard: aicase-00001 -> aicase-99999 (5-digit zero-padded, Final/In-Review)
#   Excluded: aicase-x0001 -> aicase-x9999 (4-digit zero-padded, Excluded)
CASEID_PATTERN = re.compile(r'^aicase-(\d{5}|x\d{4})$')

DOMAIN_MAPPING_PATH = 'data/domain_mapping.json'


def _validate_case_ids(df):
    """Check CaseID format and uniqueness per CASEID_POLICY.md.

    Format violations and duplicates are treated as hard failures (like
    missing columns), not warnings, since CaseIDs exist specifically to
    give every case a permanent, unique, traceable identity — the policy
    explicitly calls that out as the point of the field. A malformed or
    duplicated CaseID breaks that contract, unlike a null in a
    descriptive column, which just means that record is incomplete.
    """
    ok = True
    case_ids = df['CaseID'].dropna()

    bad_format = case_ids[~case_ids.str.match(CASEID_PATTERN)]
    if not bad_format.empty:
        print(f"❌ {len(bad_format)} CaseID(s) don't match the aicase-##### / "
              f"aicase-x#### format: {bad_format.tolist()[:10]}"
              f"{' ...' if len(bad_format) > 10 else ''}")
        ok = False

    dupes = case_ids[case_ids.duplicated(keep=False)]
    if not dupes.empty:
        print(f"❌ {dupes.nunique()} duplicated CaseID(s) found (CaseIDs must be "
              f"unique and are never reused): {sorted(dupes.unique())[:10]}"
              f"{' ...' if dupes.nunique() > 10 else ''}")
        ok = False

    # x-prefixed IDs are reserved for the Excluded dataset. Their presence
    # in a Final/In-Review file is rare-but-allowed per policy (a case can
    # keep its x-prefix if it's later reinstated), so this is a warning to
    # double-check, not a failure.
    x_prefixed = case_ids[case_ids.str.match(r'^aicase-x\d{4}$', na=False)]
    if not x_prefixed.empty:
        print(f"⚠️ {len(x_prefixed)} CaseID(s) use the Excluded-format 'x' prefix "
              f"in this file — allowed for reinstated cases per policy, but worth "
              f"double-checking: {x_prefixed.tolist()[:10]}"
              f"{' ...' if len(x_prefixed) > 10 else ''}")

    if ok and dupes.empty and bad_format.empty:
        print(f"✅ All {len(case_ids)} CaseIDs are well-formed and unique.")

    return ok


def _validate_domain_mapping(df, mapping_path=DOMAIN_MAPPING_PATH):
    """Flag Use Case Domain values with no entry in data/domain_mapping.json.

    This is informational, not a failure: an unmapped value usually just
    means the data picked up a new domain label since the mapping was
    built (e.g. a fresh pull from upstream), and scripts/normalize_domains.py
    needs an update — not that this file is broken.
    """
    if 'Use Case Domain' not in df.columns:
        return
    if not os.path.exists(mapping_path):
        print(f"⚠️ {mapping_path} not found — skipping domain mapping check.")
        return

    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)['mapping']

    unmapped = sorted(set(df['Use Case Domain'].dropna().unique()) - set(mapping.keys()))
    if unmapped:
        print(f"⚠️ {len(unmapped)} Use Case Domain value(s) have no entry in "
              f"{mapping_path} and won't get a canonical mapping until it's "
              f"updated: {unmapped[:10]}{' ...' if len(unmapped) > 10 else ''}")
    else:
        print(f"✅ Every Use Case Domain value has a mapping entry in {mapping_path}.")


def validate_use_cases(csv_path):
    df = pd.read_csv(csv_path)

    # Required columns from data/schema.md
    required_columns = [
        "CaseID", "Organization", "Use Case Title", "Description",
        "Org Industry", "Use Case Industry", "Subindustry Tags",
        "Use Case Domain", "Tool/Technology", "Outcomes & Benefits",
        "Source URL"
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        print(f"❌ Missing columns in {csv_path}: {missing_cols}")
        return False

    # Check for nulls in critical columns
    critical_cols = ["CaseID", "Use Case Title", "Org Industry", "Use Case Domain"]
    null_counts = df[critical_cols].isnull().sum()

    for col, count in null_counts.items():
        if count > 0:
            print(f"⚠️ Column '{col}' has {count} null values.")

    print(f"✅ {csv_path} contains all required columns.")

    case_ids_ok = _validate_case_ids(df)
    _validate_domain_mapping(df)

    return case_ids_ok

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else 'data/use-cases.csv'
    result = validate_use_cases(path)
    sys.exit(0 if result else 1)
