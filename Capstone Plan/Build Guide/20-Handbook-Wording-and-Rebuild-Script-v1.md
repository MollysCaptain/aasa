# Handbook Wording Fix + Rebuild Script

*Follow-up to `19-Ash2-Gabi-Integration-and-Band-Fix-v1.md`, prompted by re-clarifying that the Lovable-built prototype is a visualization aid only — the real product is the Streamlit app, as always planned. This doc covers what changed just now: the Handbook wording fix, the new rebuild script, and the honest status of the two items `19-...` left open.*

---

## 1. Handbook wording fix (`AASA-Project-Handbook-v2.md`, §9)

**What was wrong:** §9 ("Prototype changes — honesty pass") described the first prototype's stats as now "**real** (197 curated cases, 24 priced tools, 21 industries — *corrected 2026-07-30: 21, not 15*)" after removing its fabricated testimonials/badges. That's true in the sense that those 197 cases are genuine, sourced deployments rather than invented ones — but the word "real" wasn't distinguishing that from **our actual dataset size (3,023 cases)**, which is what the real Streamlit product retrieves from. Read on its own, that sentence could suggest the prototype's scale matches the product's — the same category of ambiguity as the 197-vs-3,023 discrepancy flagged in the earlier `aasa-proto2.lovable.app` comparison.

**What changed:** added an explicit clarification directly in §9: "real" means genuine/sourced, not that 197 is our dataset's size; the actual retrieval knowledge base is the full 3,023-row `data/use-cases.csv`; the 197-case figure is a small curated slice used only by the standalone HTML/Lovable prototypes, which are visualization aids, not the live pipeline. Also reworded the sentence describing `aasa-prototype.html` to state plainly that it's a static mockup running against the smaller slice, separate from the real Streamlit app in `app/`, which runs the same five-constraint flow against the full dataset via `app/pipeline.py`.

No stats, numbers, or scope were changed — only the wording, to remove the ambiguity.

## 2. New rebuild script: `scripts/rebuild_knowledge_base.py`

`19-...`'s still-open item 2 was that Gabi's "delete your chroma and rebuild it" instruction is actually four steps (delete `chroma_store`, then run `normalise_cases.py` → `chunk_use_cases.py` → `embed_cases.py`, in that order), and doing only part of it either errors (duplicate Chroma ids) or silently rebuilds without her Update A `gemini-api` split actually reflected in the data.

Added `scripts/rebuild_knowledge_base.py`: deletes `chroma_store/` if present, then runs the three scripts in the correct order via `subprocess`, stopping immediately with a clear message if any step fails. Running it is now one command (`python3 scripts/rebuild_knowledge_base.py`) instead of a four-step manual sequence someone could get partially wrong.

**Important — this has not actually been run.** `data/use-cases.csv` (the real 3,023-row dataset) isn't present in this environment — it's gitignored, third-party data that has to be downloaded separately, same as it's always been. The script is ready to run wherever that file (and Chroma's dependencies) already exist — most likely Gabi's or your own local setup. Whoever runs it should see three `=== Running ... ===` sections complete with no errors, ending in "All three steps completed."

## 3. Status of `19-...`'s two open items

Being direct about what could and couldn't actually be "implemented" here:

- **Chroma rebuild** — the *risk of doing it wrong* is fixed (the new script above). The *actual rebuild* is still outstanding and needs to happen on a machine that has `data/use-cases.csv`. This isn't something that can be completed from here.
- **Re-confirming the seat-multiplier sign-off with Gabi** — **resolved.** She reviewed the corrected bands (`18-Build-Guide-Updates-Epic1-2-v1.md`, `scripts/map_stackoverflow_orgsize.py`) and confirmed she still agrees with the 2-3x `ASSUMED_SEATS` increase. No numbers changed as a result.

## 4. Everything else from the Lovable-comparison thread, for the record

Since the point of today's check-in was "did any confusion from introducing the Lovable prototype leak into our real plans or data" — the full account, gathered across this review:

- **Tech stack / build plan:** unchanged throughout. `requirements.txt` still lists Streamlit; every build guide (11-14) and the Handbook still describe the real 3,023-row dataset as the product's retrieval source.
- **The one real leak:** the org-size band boundaries in Update C's write-up (`scripts/map_stackoverflow_orgsize.py`'s comment and `18-...`'s "Band mapping" section) briefly stated the Lovable prototype's bands instead of ours — caught and fixed in `19-...` (commit `8419f31`). No computed numbers changed, only the description.
- **A second, older instance of the same ambiguity**, unrelated to this review's actual cause but same pattern: the Handbook's §9 wording, fixed today (§1 above).
- **Everything actually implemented (Updates A, B, C)** — the `gemini-api` split, the `outcomes` field, and the survey-grounded seat assumptions — used our own existing data and schema, not anything copied from Lovable's implementation; these stand as genuine improvements independent of the prototype comparison that prompted the team to look for them.
- **Everything explicitly rejected** (case-count framing, workflow taxonomy, industry list, org-size bands as user-facing categories) — never implemented, correctly left alone.
