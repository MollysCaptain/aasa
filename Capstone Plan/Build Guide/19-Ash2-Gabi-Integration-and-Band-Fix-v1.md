# Ash2: Gabi Integration + Org-Size Band Fix

*Records what changed when Gabi's completed Update A/B/C work (from `18-Build-Guide-Updates-Epic1-2-v1.md`) was brought into `Ash2`, the one real problem found during that review, and the fix applied. Companion to `18-Build-Guide-Updates-Epic1-2-v1.md` itself, which has the corrected text inline — this doc is the "what happened and why" record.*

---

## 1. What was merged into Ash2

`Ash2`'s tip was a direct ancestor of `Gabi`'s tip, so bringing Gabi's work in was a clean fast-forward — no conflicts, nothing to resolve. This brought in:

- **Update A** — `gemini-api` added as its own canonical id (`scripts/normalise_cases.py`, `app/logic/pricing.py`), plus a governability decision for it in `app/logic/filter.py` (excluded from `GOVERNABLE_FOR_REGULATED`, same "fails closed until confirmed" treatment as `perplexity`/`flowforma`) — a sensible addition beyond the original errata doc's scope, not something we asked for but a correct catch.
- **Update B** — `Outcomes & Benefits` carried through `scripts/chunk_use_cases.py` → `scripts/embed_cases.py` → `app/pipeline.py`'s `matched_cases`, exactly as specified.
- **Update C** — `app/logic/cost.py`'s `ASSUMED_SEATS` replaced with values grounded in the real Stack Overflow Developer Survey response data (`data/StackOverflow/results.csv`, obtained and correctly gitignored — not committed), via new `scripts/map_stackoverflow_orgsize.py`. `ASSUMED_TOKEN_VOLUME_MM` deliberately left as a hand-picked constant, with a comment explaining why (no equivalent survey question exists).

All three were verified against our own spec and matched, with real numbers behind Update C: adoption rates of 77.8%-82.0% across bands (all from healthy sample sizes, smallest n=1,321), producing a roughly 2-3x increase in `ASSUMED_SEATS` versus the old flat constants (e.g. `ent`: 800 → 2,377 seats).

## 2. The problem found: wrong org-size bands in the write-up

Both `scripts/map_stackoverflow_orgsize.py`'s `BAND_MAP` comment and `18-Build-Guide-Updates-Epic1-2-v1.md`'s "Band mapping" section described our org-size bands as:

> solo 1-4 / startup 5-49 / smb 50-249 / mid 250-999 / ent 1000+

Checked directly against `app/data/options.py`'s `ORG_SIZES` (unchanged throughout this whole chain) — our real bands are:

> solo 1-4 / startup 5-20 / smb 21-200 / mid 201-1,000 / ent 1,000+

The bands in the write-up are `aasa-proto2.lovable.app`'s boundaries — the exact discrepancy flagged as point 4 in the original comparative-prototype review, which the team explicitly decided *not* to adopt ("Ignore"). It reads like whoever drafted this section pulled the wrong reference bands rather than checking `options.py` directly.

**What this did and didn't affect:** the actual `BAND_MAP` dict — which real survey bracket (`"Less than 20 employees"`, `"20 to 99 employees"`, etc.) gets assigned to which band key — was not built from the wrong bands; checked against our *real* bands, it holds up about as well as it held up against the wrong ones. The clearest imprecision either way: the survey's `"100 to 499 employees"` bracket straddles our own `smb`/`mid` boundary (200/201), so respondents with 100-200 employees get folded into `mid` here even though they'd count as `smb` under our own definition. That's a disclosed limitation of working with fixed survey brackets, not something introduced by this fix — it exists regardless of which band scheme the write-up claimed. No adoption rates or `ASSUMED_SEATS` numbers changed as a result of this fix; only the prose/comment describing the bands was wrong.

## 3. Fix applied (commit `8419f31` on `Ash2`)

Two files, documentation-only:

- `scripts/map_stackoverflow_orgsize.py` — `BAND_MAP`'s comment corrected to state the real bands, with a note flagging that an earlier draft had the Lovable prototype's bands instead.
- `Capstone Plan/Build Guide/18-Build-Guide-Updates-Epic1-2-v1.md` — the "Band mapping" section's intro sentence corrected the same way, plus an honest note about the `100-499` bracket straddling our `smb`/`mid` boundary (replacing the old, now-inaccurate comparison to "the same imprecision the Lovable prototype's limitations text owns up to," which was itself based on the wrong bands).

No numeric values, adoption rates, or `ASSUMED_SEATS` entries were touched — this was purely correcting the written description to match what `app/data/options.py` actually defines.

## 4. Still open — not resolved by this fix

- **Re-confirm the "confirmed and approved" sign-off.** The guide doc's Update C section notes the 2-3x `ASSUMED_SEATS` increase was "flagged to Gabi before implementing, decision: proceed" — that review happened while the write-up (and possibly her own understanding) had the wrong bands stated. Worth a quick check with her that the decision still holds now that the bands are correctly described, even though the underlying `BAND_MAP` assignments themselves didn't need to change.
- **Chroma rebuild still required before any of this is live**, per her original message. Because Update A changed what `scripts/normalise_cases.py` writes into `data/use-cases.csv`'s `canonical_tools` column, and Update B added a new `outcomes` field to chunk metadata, the correct rebuild sequence is: delete `./chroma_store`, then re-run `scripts/normalise_cases.py` → `scripts/chunk_use_cases.py` → `scripts/embed_cases.py` in that order — not just re-running the embed step alone, since `embed_cases.py` uses `collection.add()` (not `upsert`) with deterministic `chunk-{i}` ids and will hit the documented "duplicate ID" error if the store isn't cleared first.

## 5. Verification performed

- Confirmed `Ash2`'s pre-merge tip was a strict git ancestor of `Gabi`'s tip (`git merge-base --is-ancestor`) before fast-forwarding — nothing was overwritten or lost.
- Diffed Gabi's two update commits (`8c43ed1`, `42c188c`) file-by-file against the original errata doc's spec before merging.
- Confirmed `data/StackOverflow/results.csv`, `data/use-cases.csv`, and `chroma_store/` are still correctly absent from version control (gitignored, not committed) on the merged branch.
- Confirmed `app/data/options.py`'s `ORG_SIZES` directly, rather than trusting either write-up's restated version of it.
- Confirmed the post-fix `Ash2` working tree is clean and `Gabi`'s own branch ref was left untouched throughout.
