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

## Other third-party material in this repo

| Material | Where | Licence / basis |
|---|---|---|
| Stack Overflow Developer Survey figures | `scripts/map_stackoverflow_orgsize.py`, `app/logic/cost.py` comments | Aggregate statistics only (adoption rates per org-size band); raw `results.csv` is gitignored |
| Inter, Roboto Mono web fonts | `static/fonts/` | SIL Open Font Licence |
| Vendor pricing figures | `app/logic/pricing.py` | Manually transcribed from public vendor pages, labelled illustrative throughout; no vendor data redistributed |

Our own code and written documents are covered by `LICENSE`.
