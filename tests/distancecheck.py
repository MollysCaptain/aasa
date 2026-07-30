"""
Relevance-threshold calibration sweep (Ash4).

Gabi/Claudia's original version compared 4 plausible queries against 4
deliberately absurd ones — the right idea, and the nonsense controls are what
make it work. This version widens it, because 8 data points is too small to
trust a threshold with.

--- What the first --full run taught us (2026-07-27) ----------------------------

The sweep reported FAIL: 5 of 432 real combinations returned nothing at 0.52.
Cross-checking those 5 against the corpus showed all five have **zero cases** —
there is no "Procurement in Education" deployment in the library at all. So the
empty result was CORRECT, and the FAIL verdict was wrong: it assumed anything
selectable in the dropdowns must have evidence behind it. It doesn't. A large
minority of the 432 combinations have no cases whatsoever.

That count is a property of the corpus, not of this script, so it MOVES whenever
the store is rebuilt — and it did. The 2026-07-27 sweep reported 205 of 432
(47%). Recounted on 2026-07-30 against the store Gabi committed on the 28th for
the Cloud deploy, it is **185 of 432 (43%)** — the rebuild populated 20 more
pairs. Do not quote either number from memory; the run prints the live figure on
the "Pairs WITH real cases" line, and that line is the only authority. See
Capstone Plan/PM Work/16-P22-Final-Consistency-Pass-v1.md.

So this script now separates the two situations that matter, because only one of
them is a bug:

  * WRONGLY EMPTY — the corpus HAS cases for this pair, but the threshold
    rejected them all. This is a real regression and fails the run.
  * CORRECTLY EMPTY — the corpus has no cases for this pair, so returning
    nothing is the honest answer. Reported for visibility, not a failure.

The margin figure is kept but demoted: with distributions that overlap (the
nonsense floor sits *below* the genuine ceiling) no single global cutoff can
cleanly separate real from absurd, so a thin margin is expected rather than
alarming. See PM & Ethics/Known-Limitations-v1.md.

Run from the repo root, in the environment that has ./chroma_store and the
all-MiniLM-L6-v2 model cached:

    python tests/distancecheck.py              # sampled sweep (~40 real pairs)
    python tests/distancecheck.py --full       # every workflow x industry pair
    python tests/distancecheck.py --threshold 0.55

Read-only: it queries the collection, writes nothing, and calls no LLM.
Exit code 0 = safe, 1 = a pair WITH evidence returns nothing.
"""
import argparse
import collections
import random
import statistics
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


def case_population(collection) -> "collections.Counter":
    """
    (domain, industry) -> number of distinct real cases, read from the collection
    itself so it can never drift from what was actually embedded.

    This is what lets us tell "the threshold broke a real query" apart from
    "there is genuinely nothing here to find".
    """
    got = collection.get(include=["metadatas"])
    seen, pop = set(), collections.Counter()
    for m in got["metadatas"]:
        cid = m.get("case_id")
        if cid in seen:
            continue          # 3 chunks per case — count each case once
        seen.add(cid)
        pop[(str(m.get("domain", "")).strip().lower(),
             str(m.get("industry", "")).strip().lower())] += 1
    return pop


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

    # Corpus population, so an empty result can be judged instead of assumed bad.
    pop = case_population(collection)
    populated_pairs = sum(1 for w, i in pairs if pop[(w.lower(), i.lower())] > 0)
    print(f"Pairs WITH real cases: {populated_pairs} of {len(pairs)} tested "
          f"({len(pairs) - populated_pairs} have no cases at all)\n")

    # --- real queries: which return NOTHING, and is that correct or a bug?
    real_scores, kept_counts = [], []
    wrongly_empty, correctly_empty = [], []
    for w, i in pairs:
        q = f"{w} in the {i} industry"
        dists = collection.query(query_texts=[q], n_results=15)["distances"][0]
        best = min(dists)
        kept = sum(1 for d in dists if d <= args.threshold)
        n_cases = pop[(w.lower(), i.lower())]
        real_scores.append((best, kept, q, n_cases))
        kept_counts.append(kept)
        if kept == 0:
            (wrongly_empty if n_cases > 0 else correctly_empty).append((best, q, n_cases))

    real_scores.sort(reverse=True)          # worst (largest best-distance) first
    print("REAL QUERIES — the 8 closest to the threshold (the risky end):")
    for best, kept, q, n_cases in real_scores[:8]:
        if kept == 0:
            flag = ("   <-- EMPTY, BUG (corpus has %d case(s))" % n_cases
                    if n_cases else "   <-- empty, correct (no cases exist)")
        else:
            flag = ""
        print(f"  best={best:.3f}  kept={kept:2d}/15  cases={n_cases:4d}  {q}{flag}")

    worst_real = real_scores[0][0]
    margin = args.threshold - worst_real
    print(f"\n  worst genuine best-distance : {worst_real:.3f}")
    print(f"  threshold                   : {args.threshold:.3f}")
    print(f"  MARGIN                      : {margin:+.3f}   (informational — see"
          " module docstring; overlap means a thin margin is expected)")
    # statistics.median, not sorted(...)[len//2] — the latter returns the UPPER of
    # the two middle values at even n. It agreed here (median is 15 either way) but
    # it is the same bug telemetry_funnel.py was fixed for, and leaving one copy of
    # it alive makes that fix note only half true.
    print(f"  chunks kept per real query  : min={min(kept_counts)} "
          f"median={statistics.median(kept_counts):g} max={max(kept_counts)}")

    print(f"\n  EMPTY + evidence exists (BUG) : {len(wrongly_empty)}")
    for best, q, n_cases in wrongly_empty:
        print(f"      {best:.3f}  {q}   ({n_cases} real case(s) rejected)")
    print(f"  EMPTY + no evidence (correct)  : {len(correctly_empty)}")
    for best, q, _ in correctly_empty:
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
    # Only ONE thing fails this run: a pair that HAS evidence returning nothing.
    # A pair with no evidence returning nothing is the product working correctly.
    print("\n" + "=" * 74)
    ok = not wrongly_empty
    if wrongly_empty:
        print(f"FAIL — {len(wrongly_empty)} combination(s) have real cases in the corpus")
        print(f"       but return NOTHING at {args.threshold}. That is evidence being")
        print("       thrown away. Raise the threshold above the worst value listed,")
        print("       or add a floor (always keep the top-k nearest chunks).")
    else:
        print(f"PASS — every combination that has evidence returns it (threshold "
              f"{args.threshold}).")
    if correctly_empty:
        print(f"NOTE — {len(correctly_empty)} combination(s) return nothing because the")
        print("       corpus genuinely has no cases for them. This is the no-match")
        print("       guard behaving correctly, not a failure. Users see the honest")
        print("       empty state rather than unrelated cases.")
    if leaked:
        print(f"NOTE — {len(leaked)} nonsense query/queries still return chunks. One global")
        print("       cutoff cannot separate every absurd query from every real one;")
        print("       accepted and recorded in Known-Limitations.")
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
