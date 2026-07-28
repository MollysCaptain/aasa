# AASA — AI-Assisted Stack Architect

<!-- Repo renamed from "stackpunk" to "aasa" on 2026-07-28. Historical references
     to the stackpunk repo remain in the Build Guide documents on purpose: they
     describe where work actually came from at the time and shouldn't be rewritten
     as if the rename had always been true. -->


Give AASA five constraints. It retrieves comparable real-world AI
implementations, ranks the models, APIs and frameworks they used, and estimates a
monthly cost against your budget — with every recommendation traceable to a real
source.

**Honest scope:** this is a 4-week, 2-person student capstone prototype. Pricing
is a small hand-built, illustrative table; compliance filtering is a directional
shortlist, **not** certification. No accounts, no data stored.

---

## What it does

You choose five constraints — **target AI workflow, industry, organisation size,
data-privacy posture, monthly budget** — and get a three-block blueprint:

1. **Recommended AI stack** — ranked by how often each tool appears in comparable
   real deployments, with a per-tool evidence bar and a one-line rationale.
2. **Cost forecast** — an illustrative monthly estimate (primary API + assistant),
   flagged against your budget.
3. **Real case references** — the actual deployments behind the recommendation,
   with their reported outcomes and source URLs.

Plus a copyable/downloadable export, a `.env` starter scaffold, and
session-scoped saved blueprints.

**Grounded in 3,023 real AI-deployment cases · 41 tools priced · 24 industries.**

## How it works

```
5 constraints → semantic retrieval (Chroma + all-MiniLM-L6-v2)
              → privacy filter (deterministic hard rule)
              → user vendor exclusions
              → frequency ranking (plain counting, no manual weighting)
              → cost engine (token / seat / usage models)
              → LLM writes the summary paragraph only
              → 3-block blueprint with source links
```

The LLM is the **last and smallest** step: by the time it runs, the tools and
prices are already decided by deterministic Python. It never invents a tool or a
price.

## Requirements

- **Python 3.11** (see `.python-version`)
- A **Groq API key** (for the LLM summary step)
- A few hundred MB of free disk for the embedding model + vector store

## Setup

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd aasa

# 2. Create and activate a virtual environment
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo 'GROQ_API_KEY=your-key-here' > .env

```

**That's it — the app runs after step 4.** The vector store is committed to the
repo, so there is no build step to complete first.

### Do NOT run `rebuild_knowledge_base.py` unless you mean to

It is not part of setup, and running it casually will break your working copy.
The script starts with `shutil.rmtree("./chroma_store")` — it deletes the
committed store, then rebuilds it from `data/use-cases.csv`, which is **not** in
this repo. Without that CSV you end up with no store and a non-functioning app.

It refuses to delete anything if the CSV is missing, so a mistaken run is
recoverable — but if you did lose the store, `git checkout -- chroma_store` brings
it back.

You only need it if you are changing the embedding model, the chunking strategy,
or the underlying dataset. In that case:

```bash
# 1. Get the source dataset (MIT-licensed, not committed here)
#    Save it as data/use-cases.csv
#    https://github.com/abbasmahdi-ai/ai-use-cases-library

# 2. Rebuild (normalise → chunk → embed; several minutes)
python scripts/rebuild_knowledge_base.py
```

First run also downloads the `all-MiniLM-L6-v2` embedding model from HuggingFace,
so it needs internet and a few hundred MB of disk.

### What a fresh clone will and won't have

| Path | In the repo? | Why |
|---|---|---|
| `chroma_store/` | **Yes** (~52 MB) | Streamlit Cloud can only use what's committed, and can't rebuild it there. Contains verbatim source case text — see [`docs/data-attribution.md`](docs/data-attribution.md) |
| `data/telemetry.log` | **Yes** | Card P.14's validation figures are computed from it; the metrics scripts read it directly. No personal data by design |
| `data/use-cases.csv` | No | Someone else's raw dataset — fetch your own copy |
| `data/use_cases_chunks.jsonl` | No | Intermediate build artefact |
| `.env`, `.venv` | No | Secrets and local environment |

Nothing in the "No" column indicates a broken checkout.

## Run

```bash
streamlit run app/intake.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

## Project layout

| Path | What's in it |
|---|---|
| `app/intake.py` | Entry point — theme/CSS, sidebar intake form, page assembly |
| `app/pipeline.py` | The single `run_pipeline()` that turns inputs into a blueprint |
| `app/dashboard.py` | The three-block blueprint UI (tabbed) |
| `app/logic/` | `filter.py` (privacy + ranking), `cost.py`, `pricing.py`, `prompt.py`, `scaffold.py` |
| `app/export.py` | Text / markdown blueprint exports |
| `app/saved_blueprints.py` | Session-scoped save + JSON import/export |
| `app/analytics/tracker.py` | Local JSON-lines event log (no third-party analytics) |
| `data/` | Alias/unmatched logs, domain mapping, local telemetry log (the raw case CSV is not committed) |
| `chroma_store/` | Committed Chroma vector store — 3,023 embedded cases, 9,069 chunks |
| `tests/distancecheck.py` | Relevance-threshold regression sweep over all 432 input combinations |
| `scripts/` | Knowledge-base rebuild, dry-run harness, validation-metric scripts |
| `docs/model-card.md` | Dataset bias & skew disclosure |
| `PM & Ethics/` | Charter, scope, ethics action plan, known limitations |
| `Capstone Plan/` | Build guides and PM working documents |

## Useful scripts

```bash
python scripts/backend_dry_run.py          # run 3 test profiles end-to-end
python tests/distancecheck.py --full       # relevance-threshold regression sweep (432 pairs)
python scripts/compliance_check.py         # regulated-posture filter check
python scripts/telemetry_funnel.py  --p14  # headline metrics + funnel  (Card P.14)
python scripts/credible_interval.py --p14  # small-sample credible intervals

python scripts/rebuild_knowledge_base.py   # DESTRUCTIVE — deletes and rebuilds
                                           # chroma_store/. Needs the source CSV.
                                           # See the setup warning above.
```

All of these read local data or re-run the pipeline — none sends anything
anywhere. The first three are the ones to run after a change to verify nothing
regressed; `distancecheck.py --full` is the one that catches retrieval breaking
silently.

**`--p14` is not optional on the two metrics scripts.** `data/telemetry.log` is
append-only, so every later run of the app adds events. Without the flag you get
the whole log — including development traffic recorded after the user-test round
closed — and the funnel disagrees with the published figures (56% export rate
instead of 83%). `--p14` pins the frozen window the write-up uses. Run them
without it and they'll warn you.

## Privacy & ethics

- **No accounts, no login, no persistent identifier.** State lives in one browser
  session only.
- **No PII collected** — the five constraints are dropdowns/number inputs. The
  optional project name is a free-text label that never reaches the LLM or the
  telemetry log.
- **Telemetry is a local JSON-lines file** (`data/telemetry.log`) — event names and
  numbers only, no third-party analytics service.
- **Fonts are self-hosted** (`static/fonts/`) so no user's browser calls a
  third-party font CDN.
- Dataset bias is disclosed in-product and in `docs/model-card.md`.

Weekly data-minimisation audits are recorded in
`PM & Ethics/Ethical-Action-Plan-v2.md`.

## Known limitations

Summarised in-app (the *How it works* tab) and in full in
`PM & Ethics/Known-Limitations-v1.md` — including illustrative pricing,
directional compliance filtering, the dataset's enterprise skew, and the small
validation sample.

## Data & licence

Case data comes from the open, MIT-licensed
[AI Use-Cases Library](https://github.com/abbasmahdi-ai/ai-use-cases-library).

**This repo redistributes that data.** The committed `chroma_store/` is not only
embedding vectors — its chunk metadata carries the source dataset's titles,
organisations, outcomes and ~3.1 MB of verbatim case prose. MIT permits this with
attribution, so the attribution, licence and requested citation are recorded in
[`docs/data-attribution.md`](docs/data-attribution.md). The raw
`data/use-cases.csv` is still not committed — fetch your own copy from the source.

Seat/usage assumptions reference the Stack Overflow Developer Survey (aggregate
adoption rates only; the raw response file is not committed). Vendored fonts
(Inter, Roboto Mono) are OFL-licensed. Our own code and documents: see `LICENSE`.

## Team

A 2-person bootcamp capstone: **Gabi** (retrieval, data pipeline, telemetry) and
**Ash** (UI, product/PM, ethics documentation).
