# 36 — Build Guide: Streamlit Community Cloud deploy fixes

**Branch:** `main` · **Date:** 2026-07-28 · **Owner:** Gabi (with Claude)
**Status:** Deployed and loading past both crashes below; re-verify the full
flow (Block A/B/C, PDF export, saved blueprints) live on Cloud before treating
this as fully signed off.

## Context

The repo was renamed `stackpunk` → `aasa` on GitHub (redirects handle old
`git clone`/`fetch`/`push` URLs automatically, but local remotes were updated
anyway with `git remote set-url origin git@github.com:MollysCaptain/aasa.git`
to avoid confusion). Deploying the renamed app to Streamlit Community Cloud
(`https://aasa-app.streamlit.app`, deployed from `main`) surfaced three
separate problems that don't show up when running locally, because local dev
has files on disk that a fresh Cloud clone of the repo does not.

## Fix 1 — `GROQ_API_KEY` via Streamlit Secrets

Locally, `app/logic/prompt.py` calls `load_dotenv()` then reads
`os.environ["GROQ_API_KEY"]`. Cloud has no `.env` file (and never should —
it's gitignored). Streamlit Community Cloud's **Secrets** (app Settings →
Secrets, TOML format) expose any root-level key as a real environment
variable, not just via `st.secrets`, so entering:

```
GROQ_API_KEY = "your-actual-key"
```

in the Secrets box works with the existing code unchanged — `os.environ[...]`
finds it exactly like it does locally. No code change needed for this one.

## Fix 2 — `chromadb.errors.NotFoundError` on every page load

**Symptom:** app crashed immediately with `NotFoundError` on
`_chroma_client.get_collection("aasa_cases", ...)` in `app/pipeline.py`.

**Root cause (two layered issues):**

1. `chroma_store/` was gitignored — deliberately, since Card 2.2 treats it as
   large, fully-regenerable binary data derived from `data/use-cases.csv`
   (MIT-licensed source dataset). Regenerable is true for local dev, but Cloud
   only ever gets what's in the GitHub repo, so it had no vector store at all.
2. After committing `chroma_store/` (removing the `.gitignore` line — fine
   under MIT, this is a derived artifact, not a raw redistribution of the
   source dataset), the *exact same error* persisted. Local and Cloud both run
   `chromadb==1.5.9` (checked directly, so it isn't a version mismatch). The
   real cause: `app/pipeline.py` opened the store with a bare relative path,
   `chromadb.PersistentClient(path="./chroma_store")`. That resolves against
   the process's current working directory, which is only guaranteed to be
   the repo root locally (because that's where you happen to run
   `streamlit run` from) — not guaranteed on Cloud. A relative path pointing
   at the wrong CWD doesn't error, it just silently opens/creates an *empty*
   store at that location, so `get_collection` correctly reports "not found."

**Fix:** anchor the path to the file's own location instead of CWD:

```python
_CHROMA_STORE_PATH = Path(__file__).resolve().parent.parent / "chroma_store"
_chroma_client = chromadb.PersistentClient(path=str(_CHROMA_STORE_PATH))
```

**Side effects worth knowing about:**
- `chroma_store/chroma.sqlite3` is ~52 MB — under GitHub's 100 MB hard limit
  but over its 50 MB *recommended* limit, so `git push` prints a Git LFS
  suggestion warning. That's advisory only; the push still succeeds.
- `data/telemetry.log` was found tracked in git *despite* already being listed
  in `.gitignore` (twice, a leftover duplicate line) — the well-known git
  gotcha that `.gitignore` only stops *new* untracked files from being added,
  it does nothing for a file already tracked. Fixed with
  `git rm --cached data/telemetry.log` (kept locally, just untracked going
  forward). This was the same "gitignored-yet-tracked" contradiction Ash's
  handover doc flagged as outstanding.

## Fix 3 — `FileNotFoundError` on `data/use-cases.csv`

**Symptom:** after Fix 2, the app still crashed on every load —
`FileNotFoundError` in `app/intake.py`'s `_hero_stats()`, which opened
`data/use-cases.csv` directly to compute the hero banner's case/industry
counts.

**Root cause:** same shape as Fix 2's first layer. `data/use-cases.csv` is the
raw third-party dataset and is *intentionally* gitignored — the comment in
`.gitignore` says people should download their own copy rather than get it via
this repo, which reads as a deliberate distribution decision, not just a size
concern. Unlike `chroma_store`, this file was **not** committed to fix this.

**Fix:** `_hero_stats()` now computes the same three numbers (case count,
priced-tool count, industry count) from `chroma_store`'s already-committed
metadata (`case_id` and `industry` are stored on every chunk) instead of
opening the raw CSV. Keeps the function's original intent — real numbers
computed from live data, never hardcoded — without needing the excluded file
on Cloud at all.

## Noise to ignore in the Cloud logs

Every deploy prints a `ModuleNotFoundError: No module named 'torchvision'`
traceback from `transformers.models.zoedepth...`. This is Streamlit's own file
watcher probing `transformers`' submodules for hot-reload purposes and hitting
a lazy import it doesn't need — harmless, caught internally, **not** the cause
of any crash. Don't chase this if it shows up again; check the *rest* of the
log for the actual traceback below it.

## Outstanding

- Full click-through of the deployed app (Block A/B/C, PDF export, saved
  blueprints, all three privacy postures) hasn't been re-verified live on
  Cloud since these fixes — only the two crash points above were confirmed
  resolved.
- `main` picked up an unrelated `Added Dev Container Folder` commit
  (`185ec95`) from a merge during this work; worth a quick look to confirm
  it's not something that also needs a Cloud-specific fix.
