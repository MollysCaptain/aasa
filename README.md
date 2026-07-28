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

# 5. Get the case dataset — NOT in this repo, see note below
#    Download use-cases.csv from the source and save it as data/use-cases.csv
#    https://github.com/abbasmahdi-ai/ai-use-cases-library

# 6. Build the vector store (one-off, takes a few minutes)
python scripts/rebuild_knowledge_base.py
```

### Why steps 5 and 6 exist (the two things a fresh clone will not have)

**`data/use-cases.csv` is deliberately not committed.** It's someone else's
MIT-licensed dataset, so everyone pulls their own copy from
[`abbasmahdi-ai/ai-use-cases-library`](https://github.com/abbasmahdi-ai/ai-use-cases-library)
rather than us redistributing it — that's also how you get upstream updates. See
Build Guide 13 for the citation the upstream README asks for. **Step 6 fails
without it**, because `normalise_cases.py` reads and rewrites this file first.

**`./chroma_store` is not committed either** — it's ~68 MB of binary vector data
that doesn't belong in git. Step 6 rebuilds it (normalise → chunk → embed), and
the first run also downloads the `all-MiniLM-L6-v2` embedding model from
HuggingFace, so it needs internet and a few hundred MB of disk.

Both absences are expected in a fresh clone, not signs of a broken checkout. If
you already have a working copy elsewhere, copying `data/use-cases.csv` across is
faster than re-downloading — `rebuild_knowledge_base.py` is safe to run against an
already-normalised CSV.

> **Note if you're checking whether a clone is complete:** `.env`, `.venv`,
> `chroma_store/`, `data/use-cases.csv` and `data/use_cases_chunks.jsonl` are all
> gitignored and will always be missing. `data/telemetry.log` **is** tracked
> despite appearing in `.gitignore` — Card P.14's validation figures are computed
> from it, so it has to travel with the repo.

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
| `data/` | Case library CSV, alias/unmatched logs, local telemetry log |
| `scripts/` | Knowledge-base rebuild, dry-run harness, validation-metric scripts |
| `docs/model-card.md` | Dataset bias & skew disclosure |
| `PM & Ethics/` | Charter, scope, ethics action plan, known limitations |
| `Capstone Plan/` | Build guides and PM working documents |

## Useful scripts

```bash
python scripts/rebuild_knowledge_base.py   # (re)build the Chroma vector store
python scripts/backend_dry_run.py          # run 3 test profiles end-to-end
python scripts/telemetry_funnel.py         # headline metrics + funnel from telemetry
python scripts/credible_interval.py        # small-sample credible intervals
python scripts/compliance_check.py         # regulated-posture filter check
```

The last four read local data or re-run the pipeline — none sends anything
anywhere.

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
Seat/usage assumptions reference the Stack Overflow Developer Survey. Vendored
fonts (Inter, Roboto Mono) are OFL-licensed. See `LICENSE`.

## Team

A 2-person bootcamp capstone: **Gabi** (retrieval, data pipeline, telemetry) and
**Ash** (UI, product/PM, ethics documentation).
