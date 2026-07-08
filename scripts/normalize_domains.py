import pandas as pd
import json
import os


def normalize_domains(csv_path='data/use-cases.csv', mapping_path='data/domain_mapping.json'):
    """Add a 'Use Case Domain (Canonical)' column to use-cases.csv, mapping the
    raw 'Use Case Domain' values (59 distinct strings observed, ~22% outside
    the 18-value taxonomy) onto the canonical domains defined in
    ../ai-use-cases-library/docs/taxonomy.md.

    The raw column is left untouched — this adds a column, it doesn't
    overwrite one — so nothing is lost and the mapping's judgment calls
    (documented in domain_mapping.json's "ambiguous_judgment_calls") stay
    auditable/revisable.
    """
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
    if not os.path.exists(mapping_path):
        print(f"Error: {mapping_path} not found.")
        return

    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping_config = json.load(f)
    mapping = mapping_config['mapping']
    canonical_domains = set(mapping_config['_meta']['canonical_domains'])

    df = pd.read_csv(csv_path)

    unmapped = set(df['Use Case Domain'].dropna().unique()) - set(mapping.keys())
    if unmapped:
        print(f"Warning: {len(unmapped)} raw domain value(s) have no mapping entry "
              f"and will be left blank in the canonical column. Add them to "
              f"{mapping_path}:")
        for val in sorted(unmapped):
            print(f"  - {val!r}")

    df['Use Case Domain (Canonical)'] = df['Use Case Domain'].map(mapping)

    # Sanity check: every value we did map should land in the canonical set.
    mapped_values = set(df['Use Case Domain (Canonical)'].dropna().unique())
    bad_targets = mapped_values - canonical_domains
    if bad_targets:
        print(f"Warning: mapping produced value(s) not in the canonical taxonomy list: "
              f"{bad_targets}")

    df.to_csv(csv_path, index=False)

    total = df['Use Case Domain'].notna().sum()
    still_missing = df['Use Case Domain (Canonical)'].isna().sum() - df['Use Case Domain'].isna().sum()
    print(f"Successfully added 'Use Case Domain (Canonical)' to {csv_path}.")
    print(f"{total - still_missing}/{total} rows with a domain now have a canonical mapping "
          f"({still_missing} unmapped).")


if __name__ == "__main__":
    normalize_domains()
