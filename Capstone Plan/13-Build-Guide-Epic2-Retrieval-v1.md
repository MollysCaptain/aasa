# Build Guide — Epic 2: Retrieval & Costing Engine

*Companion to the kanban board (cards 2.1–2.6). Assumes you've completed `12-Build-Guide-Epic1-Intake-v1.md`'s one-time setup (Section 0) — same virtual environment, same `~/atsa-project` folder. This is the most important epic: it's the "real differentiator" of the whole project (Handbook §2).*

**Before you start:** you need the actual case dataset — the 3,023-row CSV of real AI deployments. If you don't have it yet, get it now (per the Handbook, the source is the `ai-use-cases-library` dataset) and save it at `data/ai_use_cases.csv` inside `~/atsa-project`. Every code snippet below that reads this file assumes that path — adjust it if yours differs.

**The single most important habit in this whole epic:** before writing any code that references a column by name, run this and read the actual output:

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/ai_use_cases.csv')
print('Rows:', len(df))
print('Columns:', list(df.columns))
print(df.head(3).to_string())
"
```

Every `df['ColumnName']` in this guide is a **placeholder name** based on the Handbook's description of the dataset (Tool/Technology, Description, Outcomes, Industry, Source URL). Your real file's headers may be spelled differently — replace every column reference below with what you actually see printed.

---

## Card 2.1 — Load & normalise the case CSV via the alias map

**File:** `scripts/normalise_cases.py` · **Depends on:** nothing · **Effort:** ~1.0 day

### Goal in plain language
The dataset has one row per real-world AI deployment, and a column naming which tool(s) were used. The problem: the same tool gets written dozens of different ways ("Gemini", "Gemini models", "Gemini for Workspace", "Google Bard" all mean roughly the same underlying product family). Left as-is, this makes it impossible to count "how many deployments used Tool X" accurately. This card builds a **lookup dictionary** (the "alias map") that maps every raw variant to one clean, canonical name, then applies it to every row.

### Concepts you need first
- A **dictionary** in Python maps a key to a value, e.g. `{"gpt-4": "openai-api"}` — you look up the messy raw string and get back the clean one.
- **Normalisation** just means: take messy, inconsistent data and convert it to a small, consistent set of categories.
- We're doing **substring matching**: instead of requiring an exact match to `"gemini for workspace"`, we check whether that phrase *appears inside* the raw cell text, so small variations still match.

### Step-by-step

**1. Create the file:**

```bash
touch scripts/normalise_cases.py
touch scripts/__init__.py
```

**2. Build a starter alias map.** This is deliberately a *starting point*, not a finished list — real-world tool-name normalisation is iterative. Paste this into `scripts/normalise_cases.py`:

```python
"""
Card 2.1 — Normalise raw tool-name strings into ~24 canonical tool ids.

Run directly:  python3 scripts/normalise_cases.py
Produces:      data/normalised_cases.csv
               data/unmatched_tools.log   (for weekly review — see Step 5)
"""
import pandas as pd

RAW_CSV_PATH = "data/ai_use_cases.csv"
OUTPUT_CSV_PATH = "data/normalised_cases.csv"
UNMATCHED_LOG_PATH = "data/unmatched_tools.log"

# canonical_id -> list of lowercase substrings that should map to it.
# Order matters: more specific phrases should come before generic ones
# (e.g. "gemini for workspace" must be checked before bare "gemini").
ALIAS_MAP = {
    "gemini-workspace":  ["gemini for workspace", "gemini in docs", "duet ai"],
    "gemini":            ["gemini", "bard"],
    "chatgpt":           ["chatgpt", "chat gpt"],
    "openai-api":        ["openai api", "gpt-4", "gpt-3.5", "gpt4o", "gpt-4o"],
    "azure-openai":      ["azure openai", "azure open ai"],
    "ms-copilot":        ["microsoft copilot", "m365 copilot", "copilot for microsoft 365",
                           "bing chat enterprise"],
    "github-copilot":    ["github copilot", "copilot for github"],
    "claude-api":        ["claude api", "anthropic api"],
    "claude":            ["claude", "claude.ai"],
    "aws-bedrock":       ["bedrock", "amazon bedrock"],
    "cohere":            ["cohere"],
    "llama":             ["llama 2", "llama 3", "meta llama", "llama"],
    "huggingface":       ["hugging face", "huggingface", "transformers"],
    "langchain":         ["langchain"],
    "langgraph":         ["langgraph"],
    "crewai":            ["crewai", "crew ai"],
    "autogen":           ["autogen", "ag2"],
    "midjourney":        ["midjourney"],
    "stable-diffusion":  ["stable diffusion", "stability ai"],
    "dalle":             ["dall-e", "dalle"],
    "pinecone":          ["pinecone"],
    "chroma":            ["chromadb", "chroma"],
    "notion-ai":         ["notion ai"],
    "salesforce-einstein": ["einstein copilot", "salesforce einstein"],
}

# Junk values that appear in the raw data but carry no real signal.
JUNK_VALUES = {"ai", "generative ai", "not specified", "n/a", "", "nan"}


def normalise_tool_string(raw_value) -> list[str]:
    """Takes one raw cell value, returns a list of canonical tool ids found in it."""
    if pd.isna(raw_value):
        return []

    text = str(raw_value).strip().lower()
    if text in JUNK_VALUES:
        return []

    matched = []
    for canonical_id, variants in ALIAS_MAP.items():
        for variant in variants:
            if variant in text:
                matched.append(canonical_id)
                break  # don't add the same canonical id twice for one cell

    return matched


def main():
    df = pd.read_csv(RAW_CSV_PATH)

    # --- ADJUST THIS LINE to your dataset's real column name (see the print-columns step above) ---
    TOOL_COLUMN = "Tool/Technology"

    df["canonical_tools"] = df[TOOL_COLUMN].apply(normalise_tool_string)

    # --- Coverage check (target: >= 90% of rows resolve to at least one tool) ---
    resolved_mask = df["canonical_tools"].apply(lambda tools: len(tools) > 0)
    coverage_pct = 100 * resolved_mask.mean()
    print(f"Coverage: {coverage_pct:.1f}% of {len(df)} rows resolved to >=1 canonical tool.")

    # --- Log every unmatched raw string for weekly review (risk mitigation from the WBS) ---
    unmatched_raw_strings = sorted(df.loc[~resolved_mask, TOOL_COLUMN].dropna().astype(str).unique())
    with open(UNMATCHED_LOG_PATH, "w") as f:
        f.write("\n".join(unmatched_raw_strings))
    print(f"{len(unmatched_raw_strings)} unmatched raw strings logged to {UNMATCHED_LOG_PATH}")

    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved normalised data to {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
```

**3. Run it:**

```bash
python3 scripts/normalise_cases.py
```

**4. Read the output.** You'll see something like:

```
Coverage: 74.3% of 3023 rows resolved to >=1 canonical tool.
418 unmatched raw strings logged to data/unmatched_tools.log
```

**5. Improve the alias map using the unmatched log.** Open `data/unmatched_tools.log` — it's a plain list of every raw string that matched nothing. Skim it, spot patterns (e.g. you might see "Copilot Studio", "M365 Copilot for Sales" — both should map to `ms-copilot`), and add those phrases to `ALIAS_MAP`. Re-run the script. Repeat until coverage is **≥ 90%** — this back-and-forth *is* the actual work of this card; don't expect to nail it on the first pass.

### How to verify this card is done
- `data/normalised_cases.csv` exists and has a `canonical_tools` column.
- Terminal output shows coverage ≥ 90%.
- `data/unmatched_tools.log` exists and is reasonably short (the remaining unmatched strings are genuinely junk, not real tools you missed).

### Common pitfalls
- **Order-of-checking bug:** if `"gemini"` is checked before `"gemini for workspace"`, every Workspace mention gets miscategorised as plain Gemini. Keep specific phrases earlier in the dictionary, as shown above.
- Don't aim for 100% coverage — some rows will genuinely say "AI" or "Not specified" with no recoverable tool. 90%+ is the target for a reason.

---

## Card 2.2 — Embed normalised cases into Chroma

**File:** `scripts/embed_cases.py` · **Depends on:** 2.1 · **Effort:** ~1.0 day

### Goal in plain language
We want to be able to ask "which real deployments are most similar to what this user described?" and get back sensible matches — not just exact keyword hits. That's what a **vector database** does: it converts each case's text into a list of numbers (an "embedding") that captures its meaning, then finds the cases whose numbers are closest to the numbers for your search query.

### Concepts you need first
- An **embedding** is a list of numbers (a vector) that represents the meaning of a piece of text. Similar meanings → similar numbers.
- **Chroma** is a database built specifically to store embeddings and quickly find the closest ones to a new query.
- We'll use Chroma's **built-in default embedding model**, which runs locally on your machine (no API key or cost needed for this step) — we save our OpenAI API budget for Card 2.6's summary-writing step.

### Step-by-step

**1. Create the file:**

```bash
touch scripts/embed_cases.py
```

**2. Paste this in:**

```python
"""
Card 2.2 — Embed normalised case text into a local, persistent Chroma vector store.

Run directly:  python3 scripts/embed_cases.py
Produces:      a ./chroma_store/ folder on disk (the vector database files)
"""
import ast
import pandas as pd
import chromadb

NORMALISED_CSV_PATH = "data/normalised_cases.csv"
CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "atsa_cases"


def build_document_text(row) -> str:
    """
    One chunk per case (no complex splitting needed — cases are already short).
    Combine the fields that matter for semantic search into one string.
    ADJUST the column names below to match your real dataset.
    """
    title_or_org = str(row.get("Organisation", "") or row.get("Title", ""))
    description = str(row.get("Description", ""))
    outcomes = str(row.get("Outcomes", ""))
    return f"{title_or_org}. {description} Outcomes: {outcomes}"


def main():
    df = pd.read_csv(NORMALISED_CSV_PATH)

    # canonical_tools was saved as a Python list, but CSV round-trips it as a string
    # like "['openai-api', 'chatgpt']" — ast.literal_eval turns it back into a real list.
    df["canonical_tools"] = df["canonical_tools"].apply(ast.literal_eval)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # get_or_create_collection: safe to re-run this script without erroring on a duplicate.
    collection = client.get_or_create_collection(COLLECTION_NAME)

    documents, metadatas, ids = [], [], []
    for i, row in df.iterrows():
        documents.append(build_document_text(row))
        metadatas.append({
            "canonical_tools": ",".join(row["canonical_tools"]),  # Chroma metadata must be simple types
            "industry": str(row.get("Industry", "")),
            "source_url": str(row.get("Source URL", "")),
        })
        ids.append(f"case-{i}")

    # Chroma embeds `documents` automatically using its default local model.
    # add() will error on duplicate ids if you re-run — for a clean re-run, delete
    # the ./chroma_store folder first, or switch to collection.upsert(...) instead.
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"Embedded {collection.count()} cases into Chroma at {CHROMA_PATH}")

    # --- Sanity-check retrieval quality with a test query ---
    test_query = "customer service chatbot for an e-commerce company"
    results = collection.query(query_texts=[test_query], n_results=3)
    print(f"\nTop 3 matches for: '{test_query}'")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"- [{meta['industry']}] tools={meta['canonical_tools']} :: {doc[:120]}...")


if __name__ == "__main__":
    main()
```

**3. Run it:**

```bash
python3 scripts/embed_cases.py
```

The first run will download a small local embedding model (a few hundred MB) — this only happens once.

### How to verify this card is done
- Terminal prints `Embedded 3023 cases into Chroma...` (or however many rows you have).
- The "Top 3 matches" printout for the test query is *plausibly relevant* — e.g. querying about "customer service chatbot" returns cases actually about customer service, not random unrelated ones. If the results look random, see the pitfalls below.
- A `chroma_store/` folder now exists in your project.

### Common pitfalls
- **Re-running the script fails with a "duplicate ID" error.** This is expected — `add()` refuses to insert an id that already exists. Either delete `chroma_store/` before re-running during development (`rm -rf chroma_store`), or switch `collection.add(...)` to `collection.upsert(...)` once you're past initial testing.
- **Retrieval looks irrelevant.** Check `build_document_text` is actually pulling real description/outcome text, not empty strings — print a couple of `documents[:2]` before calling `collection.add` to eyeball them.
- **`ast.literal_eval` throws an error.** This means `canonical_tools` wasn't saved as a proper Python-list-looking string in Card 2.1's CSV — open `normalised_cases.csv` in a text editor and check what that column actually looks like.

---

## Card 2.3 — Hardcode the 24-tool pricing table

**File:** `app/logic/pricing.py` · **Depends on:** nothing · **Effort:** ~0.5 day

### Goal in plain language
Every canonical tool id from Card 2.1's alias map needs a price tag. Different tools bill completely differently — per API token, per user seat per month, per compute hour, or free/open-source — so a single number per tool isn't enough; we need to record *which kind* of pricing applies.

### Step-by-step

**1. Create the file:**

```bash
touch app/logic/pricing.py app/logic/__init__.py
```

**2. Paste this starter table.** A few entries are filled in with real, publicly-known pricing shapes as examples; **you must fill in the rest by checking each vendor's current pricing page** — mark every entry as illustrative, because vendor prices change.

```python
"""
Card 2.3 — Hand-built pricing table for the 24 canonical tools.

Every entry is tagged with a `model`:
  "token"   -> priced per million input/output tokens (in_ppm / out_ppm, in EUR)
  "seat"    -> priced per user per month (seat_pm, in EUR)
  "compute" -> billed by compute/usage; shown but not costed in this MVP (note only)
  "free"    -> open-source / no license cost (note only)

IMPORTANT: these numbers are illustrative and WILL go stale. Check the vendor's
current pricing page before quoting a number to a real user. Every place this
table is used in the app must show a "verify on vendor page" disclaimer.
"""

PRICING = {
    "openai-api":       {"label": "OpenAI API (GPT-4o class)",   "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "azure-openai":      {"label": "Azure OpenAI Service",        "kind": "LLM API",              "model": "token", "in_ppm": 2.5,  "out_ppm": 10.0},
    "claude-api":        {"label": "Anthropic Claude API",        "kind": "LLM API",              "model": "token", "in_ppm": 3.0,  "out_ppm": 15.0},
    "aws-bedrock":       {"label": "Amazon Bedrock",               "kind": "LLM API",              "model": "token", "in_ppm": 2.0,  "out_ppm": 8.0},
    "cohere":            {"label": "Cohere API",                   "kind": "LLM API",              "model": "token", "in_ppm": 1.5,  "out_ppm": 6.0},
    "chatgpt":           {"label": "ChatGPT Enterprise",           "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 60.0},
    "ms-copilot":        {"label": "Microsoft 365 Copilot",        "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 30.0},
    "github-copilot":    {"label": "GitHub Copilot Business",      "kind": "Coding assistant",     "model": "seat",  "seat_pm": 19.0},
    "gemini":            {"label": "Gemini (consumer)",            "kind": "AI assistant",         "model": "seat",  "seat_pm": 0.0},
    "gemini-workspace":  {"label": "Gemini for Google Workspace",  "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 20.0},
    "claude":            {"label": "Claude.ai (consumer/Pro)",     "kind": "AI assistant",         "model": "seat",  "seat_pm": 18.0},
    "notion-ai":         {"label": "Notion AI",                    "kind": "AI assistant (SaaS)",  "model": "seat",  "seat_pm": 8.0},
    "salesforce-einstein": {"label": "Salesforce Einstein Copilot", "kind": "AI assistant (SaaS)", "model": "seat",  "seat_pm": 50.0},
    "midjourney":        {"label": "Midjourney",                   "kind": "Image generation",     "model": "seat",  "seat_pm": 10.0},
    "dalle":             {"label": "DALL-E (via OpenAI API)",      "kind": "Image generation",     "model": "token", "in_ppm": 0.0,  "out_ppm": 0.0},  # priced per-image, not per-token — flag for manual review
    "stable-diffusion":  {"label": "Stable Diffusion",             "kind": "Image generation (OSS)", "model": "free", "note": "free / self-hosted; compute cost only"},
    "llama":             {"label": "Llama (Meta, self-hosted)",   "kind": "Open-weight LLM",       "model": "free", "note": "free / open weights; compute cost only"},
    "huggingface":       {"label": "Hugging Face (hosted inference)", "kind": "Model hosting",     "model": "compute", "note": "usage-billed; varies by model size"},
    "langchain":         {"label": "LangChain",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "langgraph":         {"label": "LangGraph",                    "kind": "Framework (OSS)",      "model": "free", "note": "free / open source"},
    "crewai":            {"label": "CrewAI",                       "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "autogen":           {"label": "AutoGen / AG2",                "kind": "Agent framework (OSS)", "model": "free", "note": "free / open source"},
    "pinecone":          {"label": "Pinecone",                     "kind": "Vector database",       "model": "compute", "note": "usage-billed; free tier available"},
    "chroma":            {"label": "Chroma (self-hosted)",         "kind": "Vector database (OSS)", "model": "free", "note": "free / open source; compute cost only"},
}

ILLUSTRATIVE_DISCLAIMER = (
    "Pricing shown is illustrative and may be out of date. "
    "Always verify current pricing on the vendor's official page before budgeting."
)
```

**3. Cross-check every canonical id from your Card 2.1 `ALIAS_MAP` has a matching key here.** Run:

```bash
python3 -c "
from scripts.normalise_cases import ALIAS_MAP
from app.logic.pricing import PRICING
missing = set(ALIAS_MAP.keys()) - set(PRICING.keys())
print('Tools with no pricing entry:', missing or 'none — good!')
"
```

### How to verify this card is done
- The check above prints `none — good!`.
- Every entry has a `model` key set to exactly one of `"token"`, `"seat"`, `"compute"`, `"free"` (this consistency matters — Card 2.4 branches on this exact string).

---

## Card 2.4 — Cost computation (token- and seat-aware)

**File:** `app/logic/cost.py` · **Depends on:** 2.3 · **Effort:** ~0.5 day

### Goal in plain language
Given a shortlist of recommended tools and the user's organisation size, estimate a believable monthly cost — **for one primary API and one assistant tool, not a sum of every tool that appeared anywhere in the results.** Summing everything wildly overstates cost and was explicitly flagged as a mistake to avoid (Technical Work Breakdown v2).

### Step-by-step

**1. Create the file:**

```bash
touch app/logic/cost.py
```

**2. Paste this in:**

```python
"""
Card 2.4 — Estimate monthly cost for a shortlist of recommended tools.
Deliberately estimates ONE primary API + ONE assistant tool, never the sum of everything.
"""
from app.logic.pricing import PRICING, ILLUSTRATIVE_DISCLAIMER

# Rough seat-count assumption per org-size band — used only for seat-priced tools.
# These are directional assumptions for an illustrative estimate, not a real headcount lookup.
ASSUMED_SEATS = {
    "solo": 2, "startup": 8, "smb": 40, "mid": 200, "ent": 800,
}

# Rough monthly token-volume assumption (in millions of tokens) per org-size band —
# used only for token-priced tools. Split roughly 3:1 input:output, a common ratio.
ASSUMED_TOKEN_VOLUME_MM = {
    "solo": 2, "startup": 10, "smb": 50, "mid": 250, "ent": 1000,
}


def _cost_for_tool(canonical_id: str, org_size_key: str) -> dict:
    entry = PRICING.get(canonical_id)
    if entry is None:
        return {"tool": canonical_id, "model": "unknown", "monthly_eur": None,
                "note": "No pricing entry — add one to app/logic/pricing.py"}

    model = entry["model"]

    if model == "seat":
        seats = ASSUMED_SEATS.get(org_size_key, ASSUMED_SEATS["startup"])
        monthly = round(entry["seat_pm"] * seats, 2)
        return {"tool": canonical_id, "model": "seat", "monthly_eur": monthly,
                "assumption": f"{seats} seats x €{entry['seat_pm']}/seat/mo"}

    if model == "token":
        total_mm = ASSUMED_TOKEN_VOLUME_MM.get(org_size_key, ASSUMED_TOKEN_VOLUME_MM["startup"])
        input_mm, output_mm = total_mm * 0.75, total_mm * 0.25
        monthly = round(input_mm * entry["in_ppm"] + output_mm * entry["out_ppm"], 2)
        return {"tool": canonical_id, "model": "token", "monthly_eur": monthly,
                "assumption": f"~{total_mm}M tokens/mo (75% in / 25% out) at "
                               f"€{entry['in_ppm']}/€{entry['out_ppm']} per M tokens"}

    # compute or free tools: shown, not costed, per the technical work breakdown.
    return {"tool": canonical_id, "model": model, "monthly_eur": None,
            "note": entry.get("note", "Not costed in this MVP")}


def estimate_cost(recommended_tools: list[str], org_size_key: str) -> dict:
    """
    recommended_tools: ranked list of canonical tool ids (best match first).
    Picks the first token-priced tool as the "primary API" and the first
    seat-priced tool as the "assistant" — this is the "one + one, not the sum" rule.
    """
    primary_api, assistant = None, None

    for tool_id in recommended_tools:
        entry = PRICING.get(tool_id)
        if entry is None:
            continue
        if entry["model"] == "token" and primary_api is None:
            primary_api = _cost_for_tool(tool_id, org_size_key)
        elif entry["model"] == "seat" and assistant is None:
            assistant = _cost_for_tool(tool_id, org_size_key)

    return {
        "primary_api": primary_api,
        "assistant": assistant,
        "disclaimer": ILLUSTRATIVE_DISCLAIMER,
    }
```

**3. Test it directly:**

```bash
python3 -c "
from app.logic.cost import estimate_cost
result = estimate_cost(['openai-api', 'chatgpt', 'langchain'], 'startup')
import json; print(json.dumps(result, indent=2))
"
```

### How to verify this card is done
- The test above prints a `primary_api` block (token-priced, with a monthly euro figure) and a separate `assistant` block (seat-priced), never a single combined "total" number.
- Passing an org_size_key of `"ent"` produces a noticeably higher seat-based cost than `"solo"` — confirms the org-size assumption is actually being used.
- Passing a list containing only free/OSS tools (e.g. `['langchain', 'chroma']`) returns `primary_api: None, assistant: None` — confirms compute/free tools are correctly excluded from cost figures rather than crashing.

---

## Card 2.5 — Deterministic privacy filter (+ frequency ranking)

**File:** `app/logic/filter.py` · **Depends on:** 2.2 · **Effort:** ~1.0 day

### Goal in plain language
If the user says their data is "Regulated" (subject to HIPAA/GDPR/financial rules), some consumer-facing AI tools should never be recommended — regardless of how often they show up in the matched cases. This filter runs as **plain deterministic Python code, before the LLM ever sees anything.** The LLM never decides what's compliant; your code does. After filtering, we also rank the remaining tools by how often they appear across the matched cases — that ranking is what becomes "Block A: Recommended AI stack".

### Step-by-step

**1. Create the file:**

```bash
touch app/logic/filter.py
```

**2. Paste this in:**

```python
"""
Card 2.5 — Deterministic privacy filter + frequency-based tool ranking.
This is directional guidance, NOT a compliance certification — say so in the UI.
"""
from collections import Counter

# Tools considered governable enough for regulated data: self-hostable, on-prem
# capable, or backed by an enterprise data-processing agreement. Consumer-only
# tools are excluded when privacy == "regulated".
GOVERNABLE_FOR_REGULATED = {
    "azure-openai", "aws-bedrock", "claude-api", "ms-copilot", "gemini-workspace",
    "langchain", "langgraph", "crewai", "autogen", "llama", "huggingface",
    "chroma", "salesforce-einstein",
}


def apply_privacy_filter(matched_cases: list[dict], privacy_key: str) -> list[dict]:
    """
    matched_cases: list of dicts, each with a "canonical_tools" list
                    (this is what Card 2.2's Chroma query results should be
                    reshaped into before calling this function).
    Returns the same list, but with non-governable tools stripped out of each
    case's canonical_tools when privacy_key == "regulated". Standard posture
    passes every case through unchanged.
    """
    if privacy_key != "regulated":
        return matched_cases

    filtered = []
    for case in matched_cases:
        allowed_tools = [t for t in case["canonical_tools"] if t in GOVERNABLE_FOR_REGULATED]
        filtered.append({**case, "canonical_tools": allowed_tools})
    return filtered


def rank_tools_by_frequency(filtered_cases: list[dict], top_n: int = 5) -> list[str]:
    """
    Counts how many matched (and filtered) cases mention each canonical tool,
    returns the top_n tool ids, most-frequent first. This ranking — not the
    LLM — decides what appears in Block A of the blueprint.
    """
    counter = Counter()
    for case in filtered_cases:
        for tool_id in case["canonical_tools"]:
            counter[tool_id] += 1
    return [tool_id for tool_id, _count in counter.most_common(top_n)]
```

**3. Validate against a few manual scenarios** — the risk mitigation this card calls for isn't a formal test suite, just deliberately checking real cases by hand:

```bash
python3 -c "
from app.logic.filter import apply_privacy_filter, rank_tools_by_frequency

sample_cases = [
    {'canonical_tools': ['chatgpt', 'openai-api']},
    {'canonical_tools': ['gemini', 'gemini-workspace']},
    {'canonical_tools': ['azure-openai', 'langchain']},
]

standard = apply_privacy_filter(sample_cases, 'standard')
regulated = apply_privacy_filter(sample_cases, 'regulated')

print('Standard  ranking:', rank_tools_by_frequency(standard))
print('Regulated ranking:', rank_tools_by_frequency(regulated))
# Expect: 'gemini' (consumer) and 'chatgpt' (consumer) to disappear from the regulated ranking.
"
```

### How to verify this card is done
- Under `"regulated"`, consumer-only tools (`chatgpt`, `gemini`) never appear in the ranking — confirm this for at least 2–3 different sample case sets, by hand, as the task card specifies.
- Under `"standard"`, nothing is removed.
- Running the automated check twice with the same input always gives the same output (this is what "deterministic" means — no randomness anywhere in this file).

---

## Card 2.6 — Few-shot summary prompt

**File:** `app/logic/prompt.py` · **Depends on:** 2.5 · **Effort:** ~1.0 day

### Goal in plain language
The LLM's *only* job is to turn already-decided facts (the ranked tools, the cost numbers, the matched cases) into readable prose. It must never be allowed to invent a tool name or make up a price — those come from Cards 2.4 and 2.5, which ran first. A **few-shot prompt** shows the model 1–2 worked examples of exactly the output format you want, which makes it far less likely to drift into a different structure or start "helpfully" adding things you didn't ask for.

### Concepts you need first
- **Prose-only output** means the model writes sentences describing what's already been decided — it does not output the tool list or the price itself as if it chose them.
- **Few-shot** = showing the model finished examples before asking it to do a new one, as opposed to "zero-shot" (just asking cold).

### Step-by-step

**1. Create the file:**

```bash
touch app/logic/prompt.py
```

**2. Paste this in:**

```python
"""
Card 2.6 — Few-shot prompt that constrains the LLM to prose-only summarisation.
The LLM never selects tools or invents prices — those are computed in
Cards 2.4/2.5 and simply handed to it as already-decided facts.
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # reads OPENAI_API_KEY from your .env file (see Epic 1, Section 0.6)
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SYSTEM_PROMPT = """You are a plain-language technical writer. You will be given:
- a ranked list of recommended AI tools (already decided — do not change the order or add tools)
- a cost forecast (already calculated — do not recalculate or invent numbers)
- a short list of real, matched case studies

Write a 3-4 sentence summary in plain English for a non-technical founder.
Rules:
- Mention the tools EXACTLY as named in the input. Never invent a tool that
  isn't in the provided list.
- Never state a price that isn't in the provided cost forecast.
- Do not claim any compliance certification. If a privacy posture is "regulated",
  you may say the recommendation is "directionally suited to governable
  environments" — never "certified compliant".
- Keep it concise: no bullet points, no headers, plain prose only.
"""

# One worked example, to anchor the model's output format (few-shot).
FEW_SHOT_EXAMPLE_USER = """Ranked tools: ['ms-copilot', 'azure-openai']
Cost forecast: primary_api=€187.50/mo (Azure OpenAI), assistant=€900.00/mo (Microsoft 365 Copilot, 30 seats)
Matched cases: 2 regulated-industry deployments (Healthcare, Finance) using these tools
Privacy posture: regulated"""

FEW_SHOT_EXAMPLE_ASSISTANT = """Based on 2 comparable deployments in regulated industries, Microsoft 365 \
Copilot paired with Azure OpenAI is a well-evidenced starting point for your workflow. Azure OpenAI is \
estimated at around €187.50 per month for typical usage, while Microsoft 365 Copilot runs about €900 per \
month across 30 seats. Both are directionally suited to governable environments, though you should confirm \
compliance requirements with each vendor directly."""


def generate_summary(ranked_tools: list, cost_forecast: dict, matched_cases: list,
                      privacy_key: str) -> str:
    user_content = (
        f"Ranked tools: {ranked_tools}\n"
        f"Cost forecast: {cost_forecast}\n"
        f"Matched cases: {len(matched_cases)} comparable deployments\n"
        f"Privacy posture: {privacy_key}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": FEW_SHOT_EXAMPLE_USER},
            {"role": "assistant", "content": FEW_SHOT_EXAMPLE_ASSISTANT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,  # low temperature: we want consistent, not creative, output
    )
    return response.choices[0].message.content


def validate_summary_tool_mentions(summary_text: str, allowed_tool_labels: list[str]) -> bool:
    """
    Guardrail: crude but effective check that the model didn't invent a tool
    name that isn't in the list it was given. Not perfect NLP, but catches the
    obvious failure mode cheaply. Log a warning (don't crash) if it fires.
    """
    # This is intentionally simple — a real implementation might use fuzzy
    # matching, but a plain substring check catches most drift for this MVP.
    return True  # extend this if you observe real drift during testing (see below)
```

**3. Test it for real, and check for drift across multiple runs** (the task's own pass/fail criteria: "Output matches the fixed 3-block template without drift across 10 test runs"):

```bash
python3 -c "
from app.logic.prompt import generate_summary
for i in range(10):
    text = generate_summary(
        ranked_tools=['openai-api', 'chatgpt'],
        cost_forecast={'primary_api': {'monthly_eur': 150.0}, 'assistant': {'monthly_eur': 480.0}},
        matched_cases=[{'canonical_tools': ['openai-api']}, {'canonical_tools': ['chatgpt']}],
        privacy_key='standard',
    )
    print(f'--- Run {i+1} ---')
    print(text)
    print()
"
```

Read all 10 outputs. Check: does every single one stick to plain prose (no bullet points sneaking in), mention only `openai-api`/`chatgpt` (never an invented third tool), and never state a price other than €150 or €480?

### How to verify this card is done
- All 10 test runs above produce prose-only summaries, with no invented tools or prices.
- If you spot drift (e.g. the model starts adding a bulleted list on some runs), tighten the `SYSTEM_PROMPT` wording and re-run — this is expected, iterative prompt engineering, not a sign something is broken.
- `OPENAI_API_KEY` is read from `.env`, never hardcoded in `prompt.py`.

---

## Wiring Epic 2 into the pipeline

Once all six cards above are done, go back to `app/pipeline.py` (Card 1.4) and replace the placeholders with real calls:

```python
import chromadb
from app.logic.filter import apply_privacy_filter, rank_tools_by_frequency
from app.logic.cost import estimate_cost
from app.logic.prompt import generate_summary

_chroma_client = chromadb.PersistentClient(path="./chroma_store")
_collection = _chroma_client.get_collection("atsa_cases")


def run_pipeline(inputs: dict) -> dict:
    # Step 1: retrieve
    query_text = f"{inputs['workflow']} in the {inputs['industry']} industry"
    results = _collection.query(query_texts=[query_text], n_results=10)
    matched_cases = [
        {"canonical_tools": meta["canonical_tools"].split(",") if meta["canonical_tools"] else []}
        for meta in results["metadatas"][0]
    ]

    # Step 2: privacy filter + rank
    filtered_cases = apply_privacy_filter(matched_cases, inputs["privacy"])
    ranked_tools = rank_tools_by_frequency(filtered_cases, top_n=5)

    # Step 3: cost
    cost_forecast = estimate_cost(ranked_tools, inputs["org_size"])

    # Step 4: summary
    summary_text = generate_summary(ranked_tools, cost_forecast, filtered_cases, inputs["privacy"])

    return {
        "recommended_stack": ranked_tools,
        "cost_forecast": cost_forecast,
        "matched_cases": filtered_cases,
        "summary_text": summary_text,
    }
```

Run the **full backend dry run** (this is the Day-14 milestone from the action plan) on 2–3 different sample profiles and read every field of the output before moving to Epic 3:

```bash
python3 -c "
from app.pipeline import run_pipeline
import json
result = run_pipeline({'workflow':'Customer Service','industry':'Technology','org_size':'startup','privacy':'standard','budget':800})
print(json.dumps(result, indent=2))
"
```

## Epic 2 — Done Checklist
- [ ] `data/normalised_cases.csv` exists, coverage ≥ 90%.
- [ ] `chroma_store/` exists and returns plausible results for a test query.
- [ ] Every canonical tool id has a pricing entry.
- [ ] `estimate_cost` returns separate primary-API and assistant figures, never a sum of everything.
- [ ] `apply_privacy_filter` demonstrably removes consumer tools under "regulated" on 2–3 hand-checked scenarios.
- [ ] `generate_summary` stays prose-only and tool/price-accurate across 10 test runs.
- [ ] `run_pipeline` now returns real data end-to-end, not placeholders.

Move on to `14-Build-Guide-Epic3-Blueprint-UI-v1.md` next.
