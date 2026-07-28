# Data attribution

This repository redistributes third-party data. This file records what, from
where, and under what licence — because the honest answer changed on 2026-07-28
and the repo's own comments no longer matched what it shipped.

## What is redistributed here

**`chroma_store/` — committed.** It is the Chroma vector database built from the
case dataset below. It is not only embedding vectors: each of the 9,069 chunks
carries metadata copied from the source rows, and the stored documents amount to
roughly **3.1 MB of verbatim case prose** (descriptions and reported outcomes),
plus `title`, `organization`, `industry`, `domain`, `source_url` and
`canonical_tools` for all 3,023 cases.

So this is a redistribution of a substantial portion of the upstream dataset in a
different container — not merely a derived statistical artefact. Calling it
"derived, therefore not redistribution" would be convenient and wrong, so we
don't.

**`data/use-cases.csv` — not committed.** The canonical raw file stays out of the
repo (`.gitignore`). Anyone rebuilding the store fetches their own copy from the
source below.

## Source and licence

- **Dataset:** AI Use-Cases Library
- **Source:** https://github.com/abbasmahdi-ai/ai-use-cases-library
- **Licence:** MIT
- **Citation requested by the upstream README:**

  > AI Use-Cases Library. Retrieved from
  > https://github.com/abbasmahdi-ai/ai-use-cases-library

MIT permits redistribution, including of modified and derived forms, provided the
copyright notice and permission notice travel with it. That is the purpose of this
file, and it is referenced from `README.md`, `.gitignore` and Build Guide 13 so it
is discoverable from wherever someone encounters the data.

## Why the store is committed at all

Streamlit Community Cloud only receives what is in the GitHub repository, and it
cannot rebuild the store there because the raw CSV is excluded. Shipping the
pre-built store is what makes the deployed app function. See Build Guide 36 for
the deployment work and Build Guide 37 for this review.

## On the size of it — do NOT "optimise" this

`chroma_store/chroma.sqlite3` is ~54 MB, which is over GitHub's 50 MB *advisory*
threshold (pushes succeed but print a Git LFS suggestion) and well under the
100 MB hard limit. Two tempting optimisations, both of which make things worse.
Decided 2026-07-28, recorded here so nobody re-litigates it from first principles:

**1. `VACUUM` the SQLite file — don't.** About **14.9 MB of the file is free
pages**, so `VACUUM` really would shrink it to roughly 39 MB and silence the LFS
warning. But the 54 MB blob is **already permanent in git history** (commit
`6f6f025`). Committing a vacuumed copy *adds* a second ~39 MB blob rather than
replacing the first, so every future `git clone` downloads **more**, not less. The
size cost is already paid; the only way to actually reclaim it is rewriting
history with `git filter-repo`, which is not a freeze-week operation and would
break every existing clone and the Cloud deployment's git reference.

**2. Delete the full-text search tables — don't.** Roughly 13 MB is Chroma's
`embedding_fulltext_search_*` index, which this app never queries (it does vector
similarity only, via `collection.query(query_texts=...)`). Removing it would look
like free savings, but those tables are Chroma's own internal schema; dropping
them risks a store that fails to open on a future Chroma version, in exchange for
a saving that — per point 1 — wouldn't shrink clones anyway.

**What to do instead:** nothing. If the size genuinely becomes a problem later,
the real fix is a store built with ids and links but no prose (which would also
resolve the redistribution question above), rebuilt from scratch on a fresh
branch — not an in-place optimisation of this one.

## Other third-party material in this repo

| Material | Where | Licence / basis |
|---|---|---|
| Stack Overflow Developer Survey figures | `scripts/map_stackoverflow_orgsize.py`, `app/logic/cost.py` comments | Aggregate statistics only (adoption rates per org-size band); raw `results.csv` is gitignored |
| Inter, Roboto Mono web fonts | `static/fonts/` | SIL Open Font Licence |
| Vendor pricing figures | `app/logic/pricing.py` | Manually transcribed from public vendor pages, labelled illustrative throughout; no vendor data redistributed |

Our own code and written documents are covered by `LICENSE`.
