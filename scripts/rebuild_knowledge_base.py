"""
One-command rebuild of the retrieval knowledge base, added per
19-Ash2-Gabi-Integration-and-Band-Fix-v1.md's still-open item: Gabi's
"delete your chroma and rebuild it" instruction is actually four steps, and
running only the last one (or skipping the delete) either errors out
(duplicate Chroma ids) or silently rebuilds without her Update A gemini-api
split actually reflected in the data. This script runs the correct sequence
every time so it can't be done partially by accident.

Run directly:  python3 scripts/rebuild_knowledge_base.py

Requires (not included in this repo — see 13-Build-Guide-Epic2-Retrieval-v1.md
and 18-Build-Guide-Updates-Epic1-2-v1.md for how to obtain each):
  - data/use-cases.csv              (the 3,023-row real case dataset)
  - data/StackOverflow/results.csv  (only needed if app/logic/cost.py's
                                      ASSUMED_SEATS are being recomputed too —
                                      not required just to rebuild Chroma)

Does NOT require network access beyond what each individual script already
needs (the HuggingFace embedding model download, on first run only).
"""
import shutil
import subprocess
import sys
from pathlib import Path

CHROMA_PATH = Path("./chroma_store")
SOURCE_CSV = Path("./data/use-cases.csv")

# Order matters: normalise_cases.py rewrites data/use-cases.csv's
# canonical_tools column in place (this is where Update A's gemini-api split
# actually takes effect); chunk_use_cases.py reads that column to build
# chunk metadata; embed_cases.py embeds the chunks into Chroma. Running these
# out of order, or skipping the first two, silently rebuilds Chroma without
# picking up upstream data changes.
STEPS = [
    "scripts/normalise_cases.py",
    "scripts/chunk_use_cases.py",
    "scripts/embed_cases.py",
]


def main():
    # Refuse to delete anything we can't rebuild.
    #
    # Added 2026-07-28. chroma_store/ is now COMMITTED to the repo (Build Guide 36)
    # so the Streamlit Cloud deploy has a vector store, while data/use-cases.csv
    # stays gitignored. That combination turned this script into a trap: a fresh
    # clone has the store but not the source CSV, so the old flow deleted a
    # working, committed store and then failed at step 1 with FileNotFoundError,
    # leaving the app broken with no obvious way back. Check first, delete second.
    if not SOURCE_CSV.exists():
        print(f"REFUSING TO RUN — {SOURCE_CSV} not found.\n")
        print("This script deletes chroma_store/ and rebuilds it from that CSV.")
        print("The CSV is deliberately gitignored (third-party dataset), so a fresh")
        print("clone does not have it — but the store IS committed and already works.\n")
        print("Nothing has been deleted. You probably don't need this script at all:")
        print("  - just running the app?      -> streamlit run app/intake.py")
        print("  - really need to rebuild?    -> download the CSV to data/use-cases.csv")
        print("                                 https://github.com/abbasmahdi-ai/ai-use-cases-library")
        print("  - already lost the store?    -> git checkout -- chroma_store")
        return 1

    if CHROMA_PATH.exists():
        print(f"Deleting existing {CHROMA_PATH} ...")
        print("  (committed to git — restore with 'git checkout -- chroma_store' if this fails)")
        shutil.rmtree(CHROMA_PATH)
    else:
        print(f"No existing {CHROMA_PATH} found — nothing to delete.")

    for step in STEPS:
        print(f"\n=== Running {step} ===")
        result = subprocess.run([sys.executable, step])
        if result.returncode != 0:
            print(f"\n{step} failed (exit code {result.returncode}) — stopping. "
                  f"Fix the error above before re-running; earlier steps' output "
                  f"(e.g. data/use-cases.csv's canonical_tools column) is already "
                  f"on disk, so re-running this script from the top is safe once "
                  f"the problem is fixed.")
            sys.exit(result.returncode)

    print("\nAll three steps completed. chroma_store/ has been rebuilt from "
          "scratch with the current data/use-cases.csv.")


if __name__ == "__main__":
    # sys.exit(main() or 0) rather than a bare main(): the guard above returns 1
    # when the source CSV is missing, and a bare call would discard that and exit 0,
    # reporting success for a run that deliberately did nothing.
    sys.exit(main() or 0)
