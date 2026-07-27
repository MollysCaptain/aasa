"""
Relevance-threshold calibration sweep (Ash4, fix 3 of 3).

Gabi/Claudia's original version compared 4 plausible queries against 4
deliberately absurd ones — the right idea, and the nonsense controls are what
make it work. This version keeps that design and widens it, because 8 data
points is too small to trust a threshold with:

    plausible max observed = 0.504   vs   RELEVANCE_THRESHOLD = 0.52
    -> a 0.016 margin, calibrated on 4 of several hundred possible
       workflow x industry combinations.

If a real user's combination lands above the threshold they get ZERO results, so
the number that actually matters is not "does it reject nonsense" but "how close
does the WORST GENUINE query get to the cutoff". This script measures that and
fails loudly if any real combination would come back empty.

Run from the repo root, in the environment that has ./chroma_store and the
all-MiniLM-L6-v2 model cached:

    python tests/distancecheck.py              # sampled sweep (~40 real pairs)
    python tests/distancecheck.py --full       # every workflow x industry pair
    python tests/distancecheck.py --threshold 0.55

Read-only: it queries the collection, writes nothing, and calls no LLM.
Exit code 0 = safe, 1 = at least one genuine combination returns nothing.
"""
import argparse
import random
import sys

import chromadb
from chromadb.utils import embedding_functions

sys.path.insert(0, ".")
from app.data.options import INDUSTRIES, WORKFLOWS          # noqa: E402
from app.pipeline import RELEVANCE_THRESHOLD                # noqa: E402

# Deliberately absurd queries — the control group. Extended from the original 4.
# These SHOULD be rejected; any that slip under the cutoff are the honest cost
# of a single global threshold.
NONSENSE = [
    "quantum toaster repair scheduling for underwater basket weavers",
    "medieval calligraphy pricing for pet grooming salons",
    "competitive yodeling championship logistics",
    "haunted lighthouse tour guide certification",
    "artisanal sock puppet theatre seating arrangements",
    "time-travel insurance underwriting for garden gnomes",
    "synchronised interpretive dance for forklift operators",
    "wizard hat structural engineering compliance",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true",
                    help="test every workflow x industry pair (slow but complete)")
    ap.add_argument("--sample", type=int, default=40,
                    help="how many real pairs to sample when not --full (default 40)")
    ap.add_argument("--threshold", type=float, default=RELEVANCE_THRESHOLD,
                    help=f"threshold to evaluate (default: pipeline's {RELEVANCE_THRESHOLD})")
    ap.add_argument("--seed", type=int, default=42, help="sampling seed, for reproducibility")
    args = ap.parse_args()

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_store")
    collection = client.get_collection("aasa_cases", embedding_function=embedding_fn)

    # "Any workflow"/"Any industry" are UI conveniences, not real corpus values.
    workflows = [w for w in WORKFLOWS if not str(w).lower().startswith("any")]
    industries = [i for i in INDUSTRIES if not str(i).lower().startswith("any")]
    pairs = [(w, i) for w in workflows for i in industries]
    total_pairs = len(pairs)
    if not args.full:
        random.Random(args.seed).shuffle(pairs)
        pairs = pairs[:args.sample]

    print(f"Threshold under test : {args.threshold}")
    print(f"Real pairs           : {len(pairs)} of {total_pairs} possible "
          f"({'FULL sweep' if args.full else f'random sample, seed {args.seed}'})")
    print(f"Nonsense controls    : {len(NONSENSE)}\n")

    # --- real queries: how many would return NOTHING, and how tight is the margin?
    real_scores, would_be_empty, kept_counts = [], [], []
    for w, i in pairs:
        q = f"{w} in the {i} industry"
        dists = collection.query(query_texts=[q], n_results=15)["distances"][0]
        best = min(dists)
        kept = sum(1 for d in dists if d <= args.threshold)
        real_scores.append((best, kept, q))
        kept_counts.append(kept)
        if kept == 0:
            would_be_empty.append((best, q))

    real_scores.sort(reverse=True)          # worst (largest best-distance) first
    print("REAL QUERIES — the 8 closest to the threshold (the risky end):")
    for best, kept, q in real_scores[:8]:
        flag = "   <-- WOULD RETURN NOTHING" if kept == 0 else ""
        print(f"  best={best:.3f}  kept={kept:2d}/15  {q}{flag}")

    worst_real = real_scores[0][0]
    margin = args.threshold - worst_real
    print(f"\n  worst genuine best-distance : {worst_real:.3f}")
    print(f"  threshold                   : {args.threshold:.3f}")
    print(f"  MARGIN                      : {margin:+.3f}"
          + ("   (NEGATIVE = genuine queries rejected)" if margin < 0 else ""))
    print(f"  chunks kept per real query  : min={min(kept_counts)} "
          f"median={sorted(kept_counts)[len(kept_counts)//2]} max={max(kept_counts)}")
    print(f"  real queries with 0 results : {len(would_be_empty)}/{len(pairs)}")
    for best, q in would_be_empty:
        print(f"      {best:.3f}  {q}")

    # --- nonsense controls: how many are correctly rejected?
    print("\nNONSENSE CONTROLS:")
    leaked = []
    for q in NONSENSE:
        dists = collection.query(query_texts=[q], n_results=15)["distances"][0]
        best = min(dists)
        kept = sum(1 for d in dists if d <= args.threshold)
        if kept:
            leaked.append((best, kept, q))
        status = "rejected" if kept == 0 else f"LEAKED {kept} chunk(s)"
        print(f"  best={best:.3f}  {status:18s} {q}")
    print(f"\n  fully rejected: {len(NONSENSE) - len(leaked)}/{len(NONSENSE)}")

    # --- verdict
    print("\n" + "=" * 74)
    ok = True
    if would_be_empty:
        ok = False
        print(f"FAIL — {len(would_be_empty)} genuine combination(s) return NOTHING at "
              f"{args.threshold}.")
        print("       Raise the threshold above the worst value above, or add a floor")
        print("       (always keep the top-k nearest chunks), before shipping this.")
    elif margin < 0.02:
        print(f"MARGINAL — nothing is rejected today, but only {margin:.3f} separates the")
        print("           worst genuine query from the cutoff. Re-run with --full before")
        print("           shipping; a single unlucky combination flips this to FAIL.")
    else:
        print(f"PASS — no genuine combination is rejected (margin {margin:.3f}).")
    if leaked:
        print(f"NOTE — {len(leaked)} nonsense query/queries still return chunks. One global")
        print("       cutoff cannot separate every absurd query from every real one;")
        print("       accepted and recorded in Known-Limitations.")
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
