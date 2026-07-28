# 37 — Ash6: review of the Cloud deploy fixes, and what this branch changes

**Branch:** `Ash6` (from `main`) · **Date:** 2026-07-28 · **Reviewer:** Ash
**Reviewing:** Gabi's Build Guide 36 (`chroma_store` path, hero stats, telemetry)
**For:** Gabi — please review before merging to `main`

---

## Verdict on the deploy work: all three fixes are correct

I verified each one against the committed store rather than taking the guide's
word for it.

| Fix | Verified how | Result |
|---|---|---|
| **1 — `GROQ_API_KEY` via Cloud Secrets** | Read the code path in `app/logic/prompt.py` | Correct. Root-level Cloud secrets populate `os.environ`, so `os.environ["GROQ_API_KEY"]` works unchanged. No code change was needed and none was made. |
| **2 — CWD-independent `chroma_store` path** | Traced `Path(__file__).resolve().parent.parent` from `app/pipeline.py` | Correct — resolves to the repo root. The CWD diagnosis is right, and I grepped `app/` for other bare relative paths: **this was the only one**, so there is no second instance of this bug waiting. |
| **3 — hero stats from store metadata** | Queried `chroma_store/chroma.sqlite3` directly | **Numbers verified identical to the old CSV-based counts:** 3,023 distinct `case_id`, 24 distinct `industry`, 41 from `PRICING`. |

I also checked the committed store is the *right* store, not a stale or partial
build:

```
9,069 embeddings · collection "aasa_cases"
18 distinct domains    — matches WORKFLOWS exactly, no drift either direction
24 distinct industries — matches INDUSTRIES exactly, no drift either direction
37 distinct canonical_tools — all 37 resolve to a PRICING entry, zero orphans
```

**On "check my LLM isn't hallucinating wildly":** I can't answer that
behaviourally without calling the deployed model. What I can confirm is that the
machinery preventing it is untouched — `app/logic/prompt.py`, `filter.py`,
`cost.py` and `pricing.py` are **byte-identical** to the reviewed `Ash4`
versions, and `app/pipeline.py` differs only in the two path lines. The model
still receives an already-final ranked list at `temperature=0`, with the
empty-summary fallback in place. If a summary looks wrong on Cloud it won't be
these changes; check whether `summary_fallback_used` is appearing in telemetry.

Also closing your open question: **`185ec95` (Dev Container) is fine.** Standard
Codespaces `python:1-3.11-bookworm` image, `postAttachCommand` runs
`streamlit run app/intake.py`, matches `.python-version` 3.11.3. No Cloud impact.
And your read on the `torchvision` traceback is right — Streamlit's file watcher
probing a lazy import. Not a crash.

---

## What this branch changes, and why

Three problems, all side effects of making Cloud work rather than mistakes in the
deploy itself.

### 1. `data/telemetry.log` — put back under version control

`git rm --cached data/telemetry.log` resolved the gitignored-yet-tracked
contradiction, but resolved it the wrong way. That file is the **sole evidence**
behind every Card P.14 figure in the write-up and the pitch deck — trust median
5/5, net value 100%, export rate 83% — and behind the participant-by-participant
provenance cross-check that makes Card P.11 auditable. Both metrics scripts read
it directly:

```
$ python3 scripts/telemetry_funnel.py
FileNotFoundError: 'data/telemetry.log'
```

Untracked, no published number could be reproduced by anyone but the machine that
produced it. For a submission whose central claim is "we computed this from
logged behaviour, not impressions", that's the wrong thing to lose.

**Changed:** restored the file (413 lines, unchanged content — same blob
`01db0aed` that was removed) and **removed the ignore rule entirely** rather than
force-adding, so there's no hidden `-f` required next time. The `.gitignore` now
carries a block explaining why this one file is deliberately tracked, including
that it holds no personal data by design (event names, timestamps,
numeric/enum values — no identifier, no free text).

**Verified:** the bounded P.14 window reproduces exactly — 8 surveys, trust
median 5, 12 viewed, 10 exported.

> If you untracked it for a Cloud reason I couldn't see from the repo, say so and
> I'll move the evidence somewhere else instead — but it can't just be absent.

### 2. The data-distribution rationale now matches what the repo does

Committing `chroma_store/` is the pragmatic call and I'm not proposing we revert
it. But the guide's framing — "a derived artifact, not a raw redistribution" —
doesn't survive inspection. I looked inside:

```
chroma:document   9,069 rows   ~3.1 MB of verbatim case prose
plus per-chunk: title, organization, outcomes, source_url, industry, domain
```

Sample stored document: *"Improving India's critical care infrastructure. In
India, the critical care infrastructure faces significant challenges…"* — the
dataset's own text, verbatim. Meanwhile `.gitignore` still told readers everyone
should get the data from source "rather than get it via this repo."

MIT permits redistribution **with attribution**, so this is a licensing-hygiene
and internal-consistency fix, not a legal problem:

- **New:** `docs/data-attribution.md` — states plainly what is redistributed,
  from where, under what licence, with the citation the upstream README asks for.
  It explicitly rejects the "derived, therefore not redistribution" framing,
  because that would be convenient and wrong.
- **`.gitignore`** — both comment blocks rewritten. The `chroma_store` block says
  it's committed *deliberately*, why, and that it carries source prose. The CSV
  block says what that rule does and doesn't achieve now.
- **Build Guide 13** — dated update note under "Before you start", so anyone
  reading the original instruction isn't misled.
- **README "Data & licence"** — states the repo redistributes the data and links
  the attribution.
- **`Known-Limitations-v1.md`** — new row disclosing it, including the cleaner
  long-term fix (a store with ids and links but no prose) and why that wasn't a
  freeze-week change.

### 3. The README was actively wrong, and setup destroyed the app

My own text, written before the deploy change, had become false:

| README claim | Reality after Build Guide 36 |
|---|---|
| "`./chroma_store` is not committed either" | It is committed |
| "`data/telemetry.log` **is** tracked" | It had been untracked |
| `data/` holds "Case library CSV … local telemetry log" | Neither was present |

Worse: Setup steps 5–6 told a fresh cloner to download the CSV and run
`rebuild_knowledge_base.py`. That script opens with
`shutil.rmtree("./chroma_store")` — so **following the README deleted the shipped
store**, and without the CSV it couldn't be rebuilt. A new contributor who
followed the instructions ended up with a broken app.

**Changed:**

- Setup now ends at step 4 with "the app runs after step 4" — because it does.
- A "**Do NOT run `rebuild_knowledge_base.py` unless you mean to**" section
  explaining what it deletes, when you'd actually want it, and how to recover
  (`git checkout -- chroma_store`).
- A "What a fresh clone will and won't have" table, so a missing file can be
  checked against a list instead of guessed at.
- Project layout gains `chroma_store/` and `tests/distancecheck.py`; the `data/`
  row is corrected.
- Useful scripts reordered so the verification scripts come first and the
  destructive one is labelled as such.

**And a code guard, because docs alone don't stop this.**
`scripts/rebuild_knowledge_base.py` now checks for `data/use-cases.csv`
**before** deleting anything, and exits 1 with recovery instructions if it's
missing. Also changed `main()` → `sys.exit(main() or 0)`, since a bare `main()`
discarded the return code and would have reported success for a run that
deliberately did nothing.

Tested live on a clone without the CSV: guard fires, exit code 1, nothing deleted.

---

## Files changed on `Ash6`

| File | Change |
|---|---|
| `data/telemetry.log` | Restored to tracking (content unchanged) |
| `.gitignore` | Telemetry rule removed + explained; `chroma_store` and CSV rationales rewritten |
| `docs/data-attribution.md` | **New** — MIT attribution for the redistributed data |
| `README.md` | Setup rewritten, destructive-script warning, clone-contents table, layout + licence sections |
| `scripts/rebuild_knowledge_base.py` | Pre-flight guard, real exit code |
| `Capstone Plan/Build Guide/13-...-Epic2-Retrieval-v1.md` | Dated update note on what the CSV rule now means |
| `PM & Ethics/Known-Limitations-v1.md` | New disclosure row |
| `Capstone Plan/Build Guide/37-...` | This document |

**No application code changed.** `app/` is untouched on this branch — the deploy
fixes stand exactly as you wrote them.

---

## Still outstanding

Your own item, unchanged and still the main gap: **the full click-through on
Cloud** — Block A/B/C, PDF export, saved blueprints, all three privacy postures —
hasn't been done since the fixes. Two things I'd add to that pass:

- **Confirm the hero renders 3,023 / 41 / 24** rather than zeros. The numbers are
  right in the store; what's unverified is `_hero_stats()` reading them on Cloud.
- **Confirm the self-hosted fonts load.** `enableStaticServing = true` is set, but
  if Cloud serves them differently the browser falls back to Google Fonts — which
  would quietly break the no-third-party-request claim in Card P.4 and on the
  ethics slide.

Two smaller notes, no action taken:

- `_hero_stats()` pulls all 9,069 metadata rows on cold start, including the
  `outcomes` text. `@st.cache_data` means once per session, so it's fine — just
  expect a slower first paint on Cloud.
- It imports the private `_collection` from `app.pipeline`. Works; slightly
  coupled. Not worth changing at freeze.
