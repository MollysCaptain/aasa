# Build Guide Updates — Epics 1 & 2

*Errata/addendum to `12-Build-Guide-Epic1-Intake-v1.md` and `13-Build-Guide-Epic2-Retrieval-v1.md`. Both epics are marked Done on the kanban board, so rather than rewrite the original cards (which double as the historical build record), the concrete edits below live here. Apply them the next time you touch the affected file — none of this blocks anything currently working.*

**Why this doc exists:** after reviewing a second prototype iteration built on Lovable (`aasa-proto2.lovable.app`) and its research feedback report, three genuine, low-risk improvement opportunities came out of the comparison — all inside code that's already shipped in Epic 1/2. Team decision: items covering brand-new scope (optional intake fields, saved-blueprints panel) went to the Icebox as new cards (2.7, 3.5); the three items below are edits to *existing* files, not new scope, so they're documented here instead.

---

## Update A — Vendor/pricing coverage audit (Card 2.1 / 2.3)

**Files:** `scripts/normalise_cases.py`, `app/logic/pricing.py`, `app/logic/filter.py`

### What prompted this
The Lovable prototype's Case Library page displays raw vendor tags per case (`openai-api`, `chatgpt`, `sagemaker`, `bedrock`, `watsonx`, `anthropic-api`, `vertex-ai`, `gemini-api`, `llama`, `azure-ai-foundry`, `nvidia-ai-ent`, among others). Worth checking whether our own `ALIAS_MAP` (Card 2.1) and `PRICING` dict (Card 2.3) actually cover all of these.

### Finding: no real coverage gap
Checked each tag against the current `ALIAS_MAP` in `scripts/normalise_cases.py`:

| Their tag | Resolves to our canonical id via | Priced in `pricing.py`? |
|---|---|---|
| `openai-api`, `chatgpt` | direct match | Yes |
| `sagemaker` | `"amazon sagemaker"` substring → `aws-platform` | Yes (compute, usage-billed note) |
| `bedrock` | `"bedrock"` substring → `aws-bedrock` | Yes (token) |
| `watsonx` | `"watson"` substring → `ibm-watsonx` | Yes (seat) |
| `anthropic-api` | `"anthropic api"` substring → `claude-api` | Yes (token) |
| `vertex-ai` | direct match | Yes (token) |
| `llama` | direct match | Yes (free/self-hosted) |
| `azure-ai-foundry` | `"azure ai foundry"` substring → `azure-platform` | Yes (compute) |
| `nvidia-ai-ent` | `"nvidia"` substring → `nvidia` | Yes (compute) |

Everything resolves. No new `ALIAS_MAP` entries or `PRICING` rows are required just to cover what the prototype displays.

### One real nuance worth fixing: `gemini-api` vs. consumer Gemini
The prototype tags at least one case `gemini-api` — implying paid, token-billed API usage — but our `ALIAS_MAP` only has a bare `"gemini"` entry (`["gemini", "bard"]`), which is priced in `pricing.py` as **consumer/seat, €0/seat/month**. A case that actually used the paid Gemini API would currently be normalised and priced as if it were the free consumer app — understating cost, the same category of problem `vertex-ai` was added to solve for the other Google product.

**Fix — add a new canonical id, checked before the generic one** (same "specific-before-generic" ordering rule Card 2.1 already documents for `gemini-workspace` vs. `gemini`):

In `scripts/normalise_cases.py`, add above the existing `"gemini"` line:

```python
ALIAS_MAP = {
    "gemini-workspace":  ["gemini for workspace", "gemini in docs", "duet ai"],
    "gemini-api":        ["gemini api", "gemini pro api", "gemini 1.5 pro api",
                           "generative language api"],
    "gemini":            ["gemini", "bard"],
    ...
```

In `app/logic/pricing.py`, add a matching entry (token-priced, same shape as `vertex-ai`'s):

```python
    "gemini-api":        {"label": "Google Gemini API", "kind": "LLM API", "model": "token",
                           "in_ppm": 1.25, "out_ppm": 5.0, "note": "Illustrative; Gemini has multiple tiered models with different per-token rates — verify against the specific model before quoting."},
```

### How to verify
- Re-run `python3 scripts/normalise_cases.py`, confirm coverage % doesn't drop (it should hold or improve slightly — this only reclassifies rows that previously matched bare `"gemini"`). Verified: coverage held exactly at 88.7%.
- `python3 -c "from scripts.normalise_cases import ALIAS_MAP; from app.logic.pricing import PRICING; print(set(ALIAS_MAP) - set(PRICING))"` should print `set()`, matching Card 2.3's existing cross-check. Verified: both files still import cleanly and the diff is `set()` in both directions.
- Spot-check `data/unmatched_tools.log` doesn't newly include any Gemini-related string (would indicate the new phrase list needs adjusting). Verified: zero Gemini-related strings in the log after re-running.

### Extra: `app/logic/filter.py` also needed a decision
Every canonical id needs an explicit governability call in Card 2.5's `GOVERNABLE_FOR_REGULATED` set — the guide didn't mention `filter.py` for this update, but a new id can't be left unaddressed there without silently (and undocumentedly) defaulting to "not governable." Added `gemini-api` to the documented-exclusion list alongside `perplexity`/`google-ai`/`flowforma`: the standalone Gemini Developer API (AI Studio / `generativelanguage.googleapis.com`) has historically had different data-handling terms than the Vertex-AI-hosted Gemini (already covered, and governable, under `vertex-ai`) — same "fails closed until independently confirmed" reasoning as the other three.

### Note: this update was lost once already
The first implementation of this update (and Update B) was made directly in the working directory but never committed before a `git reset --hard` (resetting branch `Gabi` to match `main`) silently discarded it. Reapplied identically from the assistant's conversation history. **Lesson: commit each update to `Gabi` as soon as it's verified, before touching branches again** — uncommitted changes don't survive a hard reset, and git gives no warning when this happens.

---

## Update B — Carry `Outcomes & Benefits` into case metadata (Card 2.2 / pipeline wiring)

**Files:** `scripts/chunk_use_cases.py`, `scripts/embed_cases.py`, `app/pipeline.py`

### What prompted this
The Lovable prototype's "03 Trace" step shows reported outcomes per matched case, not just organization/title/industry/source. Our dataset already has this — `Outcomes & Benefits` (bullet-pointed prose, 99.97% complete per `data/AICaseStudy/schema.md`) — and Card 2.2 already reads it today, but only to build the "outcome" chunk's *embedding text*. The field is never copied into chunk metadata, so it's discarded after embedding and isn't available to `app/pipeline.py` or, eventually, the dashboard.

*(The dashboard-display half of this — actually showing outcomes in the UI — is Epic 3 scope, Card 3.1, which hasn't started yet. See the direct edit to `14-Build-Guide-Epic3-Blueprint-UI-v1.md` on this branch for that half. This section only covers making the data available.)*

### Step 1 — `scripts/chunk_use_cases.py`: add `outcomes` to `base_meta`

```python
        base_meta = {
            "case_id": row["CaseID"],
            "organization": row["Organization"],
            "title": row["Use Case Title"],
            "industry": row["Use Case Industry"],
            "domain": domain,
            "tools": row["canonical_tools"],
            "source_url": row["Source URL"],
            "outcomes": row["Outcomes & Benefits"],   # NEW — needed for Epic 3's trace display
        }
```

### Step 2 — `scripts/embed_cases.py`: carry it into Chroma metadata

```python
        metadatas.append({
            "case_id": str(meta["case_id"]),
            "organization": str(meta["organization"]),
            "title": str(meta["title"]),
            "industry": str(meta["industry"]),
            "domain": str(meta["domain"]),
            "canonical_tools": ",".join(meta["tools"]),
            "source_url": str(meta["source_url"]),
            "outcomes": str(meta["outcomes"]),   # NEW
            "chunk_type": meta["chunk_type"],
        })
```

### Step 3 — `app/pipeline.py`: add it to the `matched_cases` dict

In `run_pipeline()`'s Step 1 loop (currently lines 55–62):

```python
        matched_cases.append({
            "case_id": case_id,
            "organization": meta["organization"],
            "title": meta["title"],
            "industry": meta["industry"],
            "source_url": meta["source_url"],
            "canonical_tools": meta["canonical_tools"].split(",") if meta["canonical_tools"] else [],
            "outcomes": meta["outcomes"],   # NEW — bullet-pointed prose, ready for Epic 3 to render
        })
```

### Common pitfalls
- **Re-embedding required.** Chroma's `collection.add()` won't retroactively add a field to already-embedded records. After Steps 1–2, either delete `./chroma_store` and re-run both scripts from scratch, or switch `embed_cases.py` to `collection.upsert(...)` (already flagged as an option in Card 2.2's own pitfalls list) so existing chunk ids get their metadata replaced in place.
- `Outcomes & Benefits` is bullet-pointed prose, potentially a few hundred characters — fine for Chroma metadata (no size limit issue at this scale), but don't feed it raw into `app/logic/prompt.py`'s few-shot prompt without checking token budget if it's ever wired into Card 2.6's LLM call (it isn't currently — the LLM only sees `len(matched_cases)`, not their content — no change needed there).

### How to verify
- After re-running Steps 1–2, `python3 -c "..."` a `collection.get(limit=1, include=['metadatas'])` call and confirm the returned metadata dict has a non-empty `outcomes` key. Verified: real bullet-pointed outcome text present.
- A manual `run_pipeline(...)` call's `matched_cases[0]` should now contain an `outcomes` string alongside the existing five keys. Verified: confirmed on a live Technology/standard/startup dry run.

### Note: this update was lost once already
Same as Update A above — the first implementation was uncommitted when `Gabi` was hard-reset to `main`, discarding it. Reapplied identically. Commit as soon as both updates are verified, before any further branch operations.

---

## Update C — Ground cost assumptions in the Stack Overflow survey (Card 2.4)

**File:** `app/logic/cost.py`

### What prompted this
The Lovable prototype's stated limitations note that its "company-size usage patterns are population-level (from the Stack Overflow survey), not per-case." Our `app/logic/cost.py` currently uses flat, hand-picked constants per org-size band (`ASSUMED_SEATS`, `ASSUMED_TOKEN_VOLUME_MM`) with no data source behind them at all — worth checking if we can do better, since `data/StackOverflow/schema.csv` is already sitting in the repo.

### Important finding before proposing a fix
`data/StackOverflow/schema.csv` (147 rows, 102 unique question ids) is **only the survey's question schema — the question text and ids, not any actual respondent data.** The real response file, `data/StackOverflow/results.csv`, is already named in `.gitignore` (line 221) but wasn't present in the repo when this doc was first written — it needed to be downloaded separately, the same pattern already established for `data/use-cases.csv`. **Update: `results.csv` has since been obtained** (49,191 rows) — see "Actual mapping and computed rates" below for the real numbers. The plan as originally written follows first, for the historical record.

The most directly relevant question is **`QID16` / `OrgSize`**: *"Approximately how many people are employed by your employer?"* — a multiple-choice headcount-bracket question. There's no direct "monthly AI token spend" or "seats licensed" question in the schema (this is a developer-attitudes survey, not a billing survey), so the honest use of this data is as a **seat-utilization proxy** — cross-tabbing `OrgSize` against `QID78`/`AISelect` ("Do you currently use AI tools in your development process?") and `QID85`/`AIAgents` — not a literal per-seat cost figure. Don't overclaim precision here; the illustrative disclaimer in `pricing.py` still applies.

### Proposed approach, once `results.csv` is available

**1. Map the survey's `OrgSize` brackets onto our own 5 bands.** The survey's brackets won't line up 1:1 with `app/data/options.py`'s `ORG_SIZES` (`solo`/`startup`/`smb`/`mid`/`ent`) — this is the same band-mismatch risk flagged in the Lovable prototype's own limitations text, just on our side now. Build an explicit mapping dict (e.g. `scripts/map_stackoverflow_orgsize.py`) once the real bracket labels are known from `results.csv`'s `OrgSize` column values — don't guess the labels from the schema alone.

**2. Compute a per-band "active AI tool usage rate"** — the fraction of respondents in each mapped band who answered "Yes" (or equivalent) to `AISelect`/`AIAgents`.

**3. Replace the flat constants in `app/logic/cost.py`** with the computed rate multiplied against a still-illustrative base-seat assumption, e.g.:

```python
# Was: ASSUMED_SEATS = {"solo": 2, "startup": 8, "smb": 40, "mid": 200, "ent": 800}
# Becomes: base headcount assumption x AI-tool-adoption rate from the Stack
# Overflow survey (data/StackOverflow/results.csv, QID16 x QID78), computed by
# scripts/map_stackoverflow_orgsize.py and pasted in here as a comment showing
# the source numbers — same "illustrative, not a real headcount lookup" caveat
# still applies; this just grounds the multiplier in real survey data instead
# of a guess.
ASSUMED_SEATS = {
    "solo": round(4 * ADOPTION_RATE["solo"]),
    "startup": round(20 * ADOPTION_RATE["startup"]),
    "smb": round(150 * ADOPTION_RATE["smb"]),
    "mid": round(600 * ADOPTION_RATE["mid"]),
    "ent": round(3000 * ADOPTION_RATE["ent"]),
}
```

(Exact numbers to be filled in once `results.csv` is downloaded and the crosstab is run — don't hardcode placeholder figures into the real file.)

### Actual mapping and computed rates (now that `results.csv` is available)

**Real `OrgSize` bracket labels** (not guessable from `schema.csv` alone, per the pitfall above): `"Just me - I am a freelancer, sole proprietor, etc."`, `"Less than 20 employees"`, `"20 to 99 employees"`, `"100 to 499 employees"`, `"500 to 999 employees"`, `"1,000 to 4,999 employees"`, `"5,000 to 9,999 employees"`, `"10,000 or more employees"`, plus `"I don't know"` and blank (both excluded from the crosstab).

**Band mapping — a genuine judgment call, documented rather than hidden**, since the survey's bracket boundaries don't line up with our solo(1-4)/startup(5-49)/smb(50-249)/mid(250-999)/ent(1000+) bands:

| Our band | Survey bracket(s) mapped to it |
|---|---|
| `solo` | "Just me - I am a freelancer, sole proprietor, etc." |
| `startup` | "Less than 20 employees" |
| `smb` | "20 to 99 employees" |
| `mid` | "100 to 499 employees" + "500 to 999 employees" (combined) |
| `ent` | "1,000 to 4,999" + "5,000 to 9,999" + "10,000 or more" (combined) |

None of these are exact fits (e.g. "Less than 20" technically overlaps `solo`'s 1-4 range too), but this is the closest reasonable single-bracket-per-band assignment, and it's the same imprecision the Lovable prototype's own limitations text already owns up to for its side of this problem.

**Adoption rate** = fraction of respondents in each mapped band answering "Yes" to `AISelect` ("Do you currently use AI tools in your development process?"), among those who gave a Yes/No-type answer (non-responses excluded from both numerator and denominator):

| Band | Respondents (n) | Adoption rate |
|---|---|---|
| solo | 1,321 | 77.8% |
| startup | 4,306 | 82.0% |
| smb | 5,215 | 82.0% |
| mid | 6,731 | 80.2% |
| ent | 8,548 | 79.2% |

All five bands have healthy sample sizes (>1,300 each) — no small-sample noise risk to flag here. Rates are fairly flat across bands (78-82%), so most of the differentiation between bands in the final numbers comes from the base-headcount assumption, not the adoption rate.

**Final `ASSUMED_SEATS`**, using the base headcounts from the code sample above (4/20/150/600/3000) x these rates:

| Band | Old flat value | New survey-grounded value |
|---|---|---|
| solo | 2 | 3 |
| startup | 8 | 16 |
| smb | 40 | 123 |
| mid | 200 | 481 |
| ent | 800 | 2,377 |

This is a real, roughly 2-3x increase across every band — flagged to Gabi before implementing, decision: proceed with these numbers as-is.

**4. `ASSUMED_TOKEN_VOLUME_MM` has no equivalent survey question to ground it against** (no token/usage-volume question exists in the schema) — leave as a hand-picked illustrative constant, but add a code comment saying so explicitly, so a future reader doesn't assume it's survey-derived when only the seat side is.

### Common pitfalls
- Don't skip straight to writing the crosstab code against `schema.csv` — it has no response rows, so any script run against it alone will produce nothing meaningful.
- Keep `ILLUSTRATIVE_DISCLAIMER` in `pricing.py` unchanged — grounding the seat multiplier in survey data doesn't make the cost forecast a real quote.
- If `results.csv` turns out to have too few respondents in a given `OrgSize` bracket for a stable rate (small-sample risk, same concern already documented in `17-Build-Guide-Package-Pitch-Week4-v1.md`'s trust-survey methodology), say so in a code comment rather than silently using a noisy number.

### How to verify
- `data/StackOverflow/results.csv` exists locally (gitignored, not committed) and loads with `pd.read_csv`. Verified: 49,191 rows.
- The crosstab script (`scripts/map_stackoverflow_orgsize.py`) prints an adoption rate between 0 and 1 for each of the 5 mapped bands. Verified: 0.7782/0.8203/0.8199/0.8018/0.7922 for solo/startup/smb/mid/ent.
- `estimate_cost(['ms-copilot'], 'ent')` produces a different (likely higher, given real enterprise AI-adoption rates) seat count than the current flat `800` — confirms the new numbers are actually wired in, not just computed and discarded. Verified: 2,377 seats, €71,310/mo (was 800 seats, €24,000/mo under the old flat constant).

**Status: implemented and verified.** `scripts/map_stackoverflow_orgsize.py` created; `app/logic/cost.py`'s `ASSUMED_SEATS` replaced with the survey-grounded values and a comment showing the source numbers; `ASSUMED_TOKEN_VOLUME_MM` left unchanged with an explicit "not survey-derived" comment added, per point 4 above.
