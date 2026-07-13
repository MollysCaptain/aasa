"""
Card 2.2, Step 1 — Generate metadata-enriched chunks from the case CSV.

Adopted from the colleague's scripts/chunk_use_cases.py (stackpunk/Gabi branch),
modified to use the canonical_tools column (Card 2.1's alias map) instead of
re-splitting the raw Tools/Technologies string, and to carry source_url in
every chunk's metadata (needed by Card 3.1's dashboard).

Run directly:  python3 scripts/chunk_use_cases.py
Produces:      data/use_cases_chunks.jsonl (3 chunks per case)
"""
import ast
import json
import pandas as pd

CSV_PATH = "data/use-cases.csv"
CHUNKS_PATH = "data/use_cases_chunks.jsonl"


def chunk_use_cases(input_path: str = CSV_PATH, output_path: str = CHUNKS_PATH):
    df = pd.read_csv(input_path)

    # canonical_tools was saved as a Python list, but CSV round-trips it as a
    # string like "['openai-api', 'chatgpt']" — literal_eval turns it back into
    # a real list. Requires Card 2.1 (Step 0 + the alias map) to have already run.
    df["canonical_tools"] = df["canonical_tools"].apply(ast.literal_eval)

    chunks = []
    for _, row in df.iterrows():
        domain = (
            row["Use Case Domain (Canonical)"]
            if pd.notna(row.get("Use Case Domain (Canonical)"))
            else row["Use Case Domain"]
        )
        base_meta = {
            "case_id": row["CaseID"],
            "organization": row["Organization"],
            "title": row["Use Case Title"],
            "industry": row["Use Case Industry"],
            "domain": domain,
            "tools": row["canonical_tools"],
            "source_url": row["Source URL"],
            "outcomes": row["Outcomes & Benefits"],   # NEW — needed for Epic 3's trace display
        }

        # Chunk 1 — Implementation: what they built.
        chunks.append({
            "text": f"{row['Use Case Title']}. {row['Description']}",
            "metadata": {**base_meta, "chunk_type": "implementation"},
        })

        # Chunk 2 — Outcome: what happened (the bullet-point prose field).
        chunks.append({
            "text": f"Outcomes at {row['Organization']}: {row['Outcomes & Benefits']}",
            "metadata": {**base_meta, "chunk_type": "outcome"},
        })

        # Chunk 3 — Domain: industry/function framing, for "who else is like me" queries.
        chunks.append({
            "text": f"{row['Organization']} operates in {row['Org Industry']}, "
                    f"applying AI to {domain} ({row['Use Case Industry']}).",
            "metadata": {**base_meta, "chunk_type": "domain"},
        })

    with open(output_path, "w") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"Wrote {len(chunks)} chunks ({len(df)} cases x 3) to {output_path}")


if __name__ == "__main__":
    chunk_use_cases()
