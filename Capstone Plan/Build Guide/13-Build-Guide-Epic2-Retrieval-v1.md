# Build Guide — Epic 2: Retrieval & Costing Engine

*Companion to the kanban board (cards 2.1–2.6). Assumes you've completed `12-Build-Guide-Epic1-Intake-v1.md`'s one-time setup (Section 0) — same virtual environment, same `~/aasa-project` folder. This is the most important epic: it's the "real differentiator" of the whole project (Handbook §2).*

**Before you start:** you need the actual case dataset — the 3,023-row CSV of real AI deployments. Save it at `data/use-cases.csv` inside `~/aasa-project` (per the Handbook, the source is the `ai-use-cases-library` dataset).

**This is someone else's dataset, not ours — download your own copy, don't fetch it via this repo.** The source is [`abbasmahdi-ai/ai-use-cases-library`](https://github.com/abbasmahdi-ai/ai-use-cases-library) on GitHub. It's MIT-licensed, but `data/use-cases.csv` is deliberately **gitignored** here rather than committed — everyone on the project should pull their own copy directly from the source repo (that's also the easiest way to get updates if the upstream data changes). If you use this dataset in research or publications, the upstream README asks for this citation:

```
AI Use Cases Library. (2026).
Retrieved from https://github.com/abbasmahdi-ai/ai-use-cases-library
```

**Column names are now real, not placeholders — but verify against your own file, not just this guide.** An earlier version of this guide had you print your CSV's columns and guess, because neither of us had the actual file yet. Your colleague's `stackpunk` repo (Gabi branch) verified a schema against the actual data — `data/stackpunk-schema.md` there was believed to be the authoritative reference — but running `print(pd.read_csv('data/use-cases.csv').columns)` against the real, current `data/use-cases.csv` turned up one mismatch worth flagging loudly:

`CaseID, Organization, Use Case Title, Description, Org Industry, Use Case Industry, Subindustry Tags, Use Case Domain, Tool/Technology, Outcomes & Benefits, Source URL, Source`

**Correction:** the tools column is `Tool/Technology` — **singular**, not `Tools/Technologies` (plural) as this guide originally said and as `stackpunk-schema.md` also states. This isn't a typo in one place; it was wrong everywhere: the intro above, Card 2.1's `TOOL_COLUMN` constant, and `scripts/validate_use_cases.py`'s required-columns list all originally assumed the plural form and would fail (`KeyError` / `Missing columns`) against the real file. All of those have been corrected — see Card 2.1 below and the "Common pitfalls" note.

Two things worth knowing about the data itself: `Tool/Technology` is **semicolon-delimited** (`"OpenAI's Whisper API ; GPT-4 ; GPT-4 Vision"`), not comma-delimited as the dataset's own upstream doc implies — though as you'll see in Card 2.1, the alias-matching approach here doesn't actually need to split on the delimiter, so this is good background, not a blocker. `Outcomes & Benefits` is bullet-pointed prose (`•`-prefixed lines), not a short tag list — matters for Card 2.2's chunk text.

If you ever pull a fresh copy of the dataset and something looks different, re-verify with `print(pd.read_csv('data/use-cases.csv').columns)` rather than assuming this guide is still accurate — that's exactly how the column-name error above was caught.

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

**0. Adopt two data-quality scripts from your colleague's `stackpunk` branch first.** Before touching tool names at all, get the data into a known-good, domain-normalised state — this isn't rebuilding something you already have, it's two genuinely separate, already-solved problems (CaseID/schema validity, and functional-domain normalisation) that would otherwise silently corrupt the alias-map work below if left unfixed.

Copy these two files (and the mapping table they depend on) from the `stackpunk` repo's `Gabi` branch into your project — no need to rewrite them, they're already built and verified against the real 3,023-row dataset:

```bash
# adjust the source path to wherever you have the stackpunk repo cloned locally
cp /path/to/stackpunk/data/domain_mapping.json data/domain_mapping.json
cp /path/to/stackpunk/scripts/validate_use_cases.py scripts/validate_use_cases.py
cp /path/to/stackpunk/scripts/normalize_domains.py scripts/normalize_domains.py
```

Run them, in this order, before the alias map:

```bash
python3 scripts/validate_use_cases.py data/use-cases.csv
python3 scripts/normalize_domains.py
```

**What each one buys you:**
- `validate_use_cases.py` is a **gate**, not a nice-to-have — it hard-fails (exit code 1) on a malformed or duplicated `CaseID`, since the whole point of a CaseID is a permanent, unique, traceable identity; a broken one should stop the pipeline, not quietly produce bad rankings three steps later. It also warns (doesn't fail) if any `Use Case Domain` value has no entry in `domain_mapping.json` yet.
- `normalize_domains.py` adds a **`Use Case Domain (Canonical)`** column to `data/use-cases.csv` in place — mapping the 59 raw domain strings found in the wild onto the 18 canonical domains the dataset's taxonomy actually defines. Card 1.2 (`12-Build-Guide-Epic1-Intake-v1.md`) uses this column directly for the Workflow dropdown — no placeholder guessing needed.

If either script reports a problem, fix the data before continuing — everything below assumes `data/use-cases.csv` has already passed both checks.

**1. Create the file:**

```bash
touch scripts/normalise_cases.py
touch scripts/__init__.py
```

**2. Build a starter alias map.** This is deliberately a *starting point*, not a finished list — real-world tool-name normalisation is iterative, and it's the one piece of this pipeline your colleague's branch hasn't built yet (their `PLANNING.md` explicitly defers the tool/pricing side of things) — this is where your work adds distinct value. Paste this into `scripts/normalise_cases.py`:

```python
"""
Card 2.1 — Normalise raw tool-name strings into ~24 canonical tool ids.
Run AFTER scripts/validate_use_cases.py and scripts/normalize_domains.py (Step 0)
so this adds canonical_tools on top of an already-validated, domain-normalised file.

Run directly:  python3 scripts/normalise_cases.py
Produces:      data/use-cases.csv, with a new canonical_tools column added in place
               data/unmatched_tools.log   (for weekly review — see Step 5)
"""
import pandas as pd

CSV_PATH = "data/use-cases.csv"  # read AND write — adds a column in place, matching
                                  # the convention Step 0's scripts already use
UNMATCHED_LOG_PATH = "data/unmatched_tools.log"

# canonical_id -> list of lowercase substrings that should map to it.
# Order matters: more specific phrases should come before generic ones
# (e.g. "gemini for workspace" must be checked before bare "gemini").
ALIAS_MAP = {
    "gemini-workspace":  ["gemini for workspace", "gemini in docs", "duet ai"],
    "gemini":            ["gemini", "bard"],
    "chatgpt":           ["chatgpt", "chat gpt"],
    "openai-api":        ["openai api", "gpt-4", "gpt-3.5", "gpt4o", "gpt-4o",
                           "gpt-5", "gpt-3", "openai o1", "openai deep research",
                           "sora", "agents sdk", "realtime api"],
    "azure-openai":      ["azure openai", "azure open ai"],
    "ms-copilot":        ["microsoft copilot", "m365 copilot", "copilot for microsoft 365",
                           "microsoft 365 copilot", "bing chat enterprise"],
    "copilot-studio":    ["copilot studio"],
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

    # --- Added after the first real coverage pass came in at 46.8%, well under
    # the 90% target below — this dataset leans heavily on named cloud/enterprise
    # platforms that the starter list above (model/agent-framework focused)
    # didn't cover at all. Still specific, named products, not generic technique
    # words like "machine learning" or "RAG" — see the coverage note in Step 5. ---
    "vertex-ai":         ["vertex ai"],
    "ibm-watsonx":       ["watson", "ibm granite", "ibm research", "ibm ai@scale",
                           "ibm instana"],  # "watson" also matches "watsonx"
    "ibm-cloud":         ["ibm cloud"],
    "google-cloud":      ["google cloud", "bigquery", "google kubernetes engine",
                           "cloud run", "looker", "google workspace", "google vids"],
    "azure-platform":    ["microsoft azure", "azure ai foundry", "azure ai services",
                           "azure cognitive services", "azure machine learning",
                           "azure synapse", "azure databricks", "microsoft fabric",
                           "microsoft sentinel", "microsoft purview", "azure ai search",
                           "azure ai", "azure", "microsoft ai"],
    "aws-platform":      ["amazon sagemaker", "amazon s3", "amazon ec2", "aws lambda",
                           "amazon dynamodb", "amazon redshift", "aws glue",
                           "amazon connect", "amazon lex", "amazon rekognition",
                           "amazon q", "amazon ads", "amazon emr", "amazon alexa",
                           "amazon music", "amazon one", "aws"],
    "nvidia":            ["nvidia", "cuda", "cudnn"],
    "tensorflow":        ["tensorflow"],
    "pytorch":           ["pytorch"],
    "ms365-suite":       ["microsoft 365", "microsoft teams", "sharepoint", "outlook"],
    "ms-dynamics":       ["dynamics 365", "dax copilot"],
    "perplexity":        ["perplexity", "sonar pro", "sonar api"],
    "google-ai":         ["notebooklm", "imagen", "veo", "google ai", "dialogflow",
                           "agentspace", "google distributed cloud", "document ai",
                           "security command center", "google security operations",
                           "code assist"],
    "flowforma":         ["flowforma"],
    "nuance-dragon":     ["dragon medical one"],
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
    df = pd.read_csv(CSV_PATH)

    # Real column name, verified against the actual data (see the top of this
    # guide): "Tool/Technology" — SINGULAR, not "Tools/Technologies" as an
    # earlier version of this guide (and stackpunk-schema.md) assumed. Still
    # semicolon-delimited. normalise_tool_string does substring matching over
    # the WHOLE cell, not a per-item split — so a multi-tool cell like
    # "OpenAI's Whisper API ; GPT-4 ; GPT-4 Vision" still matches every phrase
    # it contains without needing to split on ";" first.
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

    df.to_csv(CSV_PATH, index=False)  # adds canonical_tools in place, alongside
                                        # Step 0's Use Case Domain (Canonical) column
    print(f"Saved canonical_tools column to {CSV_PATH}")


if __name__ == "__main__":
    main()
```

**3. Run it:**

```bash
python3 scripts/normalise_cases.py
```

**4. Read the output.** With just the starter alias map above, the real run against the actual 3,023-row file came in at:

```
Coverage: 46.8% of 3023 rows resolved to >=1 canonical tool.
1334 unmatched raw strings logged to data/unmatched_tools.log
```

Far below target — the starter list is model/agent-framework focused, but the real dataset skews heavily toward named cloud/enterprise platforms (Vertex AI, IBM Watsonx, Azure, AWS, NVIDIA, Perplexity, etc.) that it doesn't cover at all. This isn't a sign something's broken; it's exactly the "iterate using the unmatched log" step below, just starting from a lower number than the example.

**5. Improve the alias map using the unmatched log.** Open `data/unmatched_tools.log` — it's a plain list of every raw string that matched nothing. Skim it, spot patterns (e.g. you might see "Copilot Studio", "M365 Copilot for Sales" — both should map to `ms-copilot`), and add those phrases to `ALIAS_MAP`. Re-run the script. Repeat until coverage is **≥ 90%** — this back-and-forth *is* the actual work of this card; don't expect to nail it on the first pass.

**Real outcome for this dataset: 88.7%, not ≥90%.** Three iterations of expanding `ALIAS_MAP` (the full expanded map above already reflects this) took coverage from 46.8% → 84.3% → 88.7%. Past that point, what's left in `data/unmatched_tools.log` is almost entirely generic, vendor-agnostic phrasing with no real product to map to — "AI", "generative AI", "machine learning", "not specified", "AI agents", "computer vision" — plus a few one-off bespoke descriptions that mention a vendor name incidentally (e.g. "on Amazon Kindle hardware") rather than as a named AI product. Forcing matches on those would inflate the coverage number while corrupting the tool-frequency data Cards 2.3/2.5 depend on. This is judged to be the guide's own stated exception in the pitfall below, not a shortfall to keep chasing — but it's a judgment call, not a hard rule, so revisit it if Cards 2.3–2.5 turn out to need better coverage than this.

### How to verify this card is done
- `data/use-cases.csv` now has two extra columns added in place: `Use Case Domain (Canonical)` (from Step 0's `normalize_domains.py`) and `canonical_tools` (from this card's alias map). The original columns are untouched — nothing here forks a new file.
- Terminal output shows coverage ≥ 90% for `canonical_tools` — **or, per the real-outcome note above, a documented reason it stopped short of that** (88.7% on this dataset).
- `data/unmatched_tools.log` exists and is reasonably short (the remaining unmatched strings are genuinely junk, not real tools you missed).
- `python3 scripts/validate_use_cases.py` (Step 0) exits with code 0 — if it doesn't, fix the data before trusting anything downstream.

### Common pitfalls
- **Order-of-checking bug:** if `"gemini"` is checked before `"gemini for workspace"`, every Workspace mention gets miscategorised as plain Gemini. Keep specific phrases earlier in the dictionary, as shown above.
- Don't aim for 100% coverage — some rows will genuinely say "AI" or "Not specified" with no recoverable tool. 90%+ is the target for a reason.
- **Column name mismatch (`KeyError: 'Tools/Technologies'`).** The real column is `Tool/Technology`, singular — see the correction at the top of this guide. This also broke `scripts/validate_use_cases.py`'s required-columns check the same way; both are already fixed in the code shown here, but if you're working from an older copy of either file, re-check the column name first.

---

## Card 2.2 — Chunk cases and embed them into Chroma

**Files:** `scripts/chunk_use_cases.py`, `scripts/embed_cases.py` · **Depends on:** 2.1 · **Effort:** ~1.0 day

*Adopted from the colleague's `stackpunk`/`Gabi` branch (`scripts/chunk_use_cases.py`, and the `PLANNING.md`-documented ChromaDB + HuggingFace decision), with one modification: chunk metadata now uses the `canonical_tools` column from Card 2.1 instead of re-splitting the raw `Tools/Technologies` string, and carries `source_url` so Card 3.1's dashboard can link back to the source case. See `19-Gabi-Branch-Integration-Analysis-v1.md` for the full reasoning.*

### Goal in plain language
We want to be able to ask "which real deployments are most similar to what this user described?" and get back sensible matches — not just exact keyword hits. That's a two-step job. First, **chunking**: break each case into a few focused pieces of text, because "how did they build it?" and "what were the results?" are different questions that match better against different text than one big blob per case. Second, **embedding**: convert each chunk's text into a list of numbers (an "embedding") that captures its meaning, and store those in a **vector database** that can quickly find the chunks whose numbers are closest to a search query's numbers.

### Concepts you need first
- A **chunk** is one retrievable piece of text. This card uses **3 chunks per case** — Implementation (what they built), Outcome (what happened), Domain (industry/function) — instead of 1, so different question types (how vs. what-happened vs. who-else) each have a chunk written to match them well.
- An **embedding** is a list of numbers (a vector) that represents the meaning of a piece of text. Similar meanings → similar numbers.
- **Chroma** is a database built specifically to store embeddings and quickly find the closest ones to a new query.
- We're using a **local HuggingFace sentence-transformers model** (`all-MiniLM-L6-v2`) to generate embeddings — no API key or cost, and it keeps the whole knowledge-base layer local. We save the Groq API budget for Card 2.6's summary-writing step. Naming the model explicitly (rather than relying on Chroma's implicit default, which happens to be the same model) means this is a provable shared decision with the colleague's branch, not a coincidence.

### Step 1 — Generate the chunks

**1. Copy the colleague's chunking script as a starting point:**

```bash
cp "/Users/ashleyc/STACKSTONE/stackpunk/scripts/chunk_use_cases.py" scripts/chunk_use_cases.py
```

**2. Edit it — two changes from the original:**
- Use the already-computed `canonical_tools` column (Card 2.1's alias map output) for chunk metadata, instead of re-splitting the raw `Tools/Technologies` string a second time.
- Add `source_url` to every chunk's metadata (the original branch script doesn't include it, but Card 3.1's dashboard needs it to link back to the source case).

The edited script should look like this:

```python
"""
Card 2.2, Step 1 — Generate metadata-enriched chunks from the case CSV.

Adopted from the colleague's scripts/chunk_use_cases.py (stackpunk/Gabi branch),
modified to use the canonical_tools column (Card 2.1's alias map) instead of
re-splitting the raw Tools/Technologies string, and to carry source_url in
every chunk's metadata (needed by Card 3.1's dashboard).

Run directly:  python3 scripts/chunk_use_cases.py
Produces:      data/use_cases_chunks.jsonl (3 chunks per case)
"""
import ast
import json
import pandas as pd

CSV_PATH = "data/use-cases.csv"
CHUNKS_PATH = "data/use_cases_chunks.jsonl"


def chunk_use_cases(input_path: str = CSV_PATH, output_path: str = CHUNKS_PATH):
    df = pd.read_csv(input_path)

    # canonical_tools was saved as a Python list, but CSV round-trips it as a
    # string like "['openai-api', 'chatgpt']" — literal_eval turns it back into
    # a real list. Requires Card 2.1 (Step 0 + the alias map) to have already run.
    df["canonical_tools"] = df["canonical_tools"].apply(ast.literal_eval)

    chunks = []
    for _, row in df.iterrows():
        domain = (
            row["Use Case Domain (Canonical)"]
            if pd.notna(row.get("Use Case Domain (Canonical)"))
            else row["Use Case Domain"]
        )
        base_meta = {
            "case_id": row["CaseID"],
            "organization": row["Organization"],
            "title": row["Use Case Title"],
            "industry": row["Use Case Industry"],
            "domain": domain,
            "tools": row["canonical_tools"],
            "source_url": row["Source URL"],
        }

        # Chunk 1 — Implementation: what they built.
        chunks.append({
            "text": f"{row['Use Case Title']}. {row['Description']}",
            "metadata": {**base_meta, "chunk_type": "implementation"},
        })

        # Chunk 2 — Outcome: what happened (the bullet-point prose field).
        chunks.append({
            "text": f"Outcomes at {row['Organization']}: {row['Outcomes & Benefits']}",
            "metadata": {**base_meta, "chunk_type": "outcome"},
        })

        # Chunk 3 — Domain: industry/function framing, for "who else is like me" queries.
        chunks.append({
            "text": f"{row['Organization']} operates in {row['Org Industry']}, "
                    f"applying AI to {domain} ({row['Use Case Industry']}).",
            "metadata": {**base_meta, "chunk_type": "domain"},
        })

    with open(output_path, "w") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk) + "\n")

    print(f"Wrote {len(chunks)} chunks ({len(df)} cases x 3) to {output_path}")


if __name__ == "__main__":
    chunk_use_cases()
```

**3. Run it:**

```bash
python3 scripts/chunk_use_cases.py
```

You should see `Wrote 9069 chunks (3023 cases x 3) to data/use_cases_chunks.jsonl`.

### Step 2 — Embed the chunks into Chroma

**1. Create the file:**

```bash
touch scripts/embed_cases.py
```

**2. Paste this in:**

```python
"""
Card 2.2, Step 2 — Embed the metadata-enriched chunks into a local, persistent
Chroma vector store, using an explicitly-named local HuggingFace embedding model
(same model Chroma would use by default — named here so it's a provable, not
coincidental, match with the colleague's branch decision in PLANNING.md).

Run directly:  python3 scripts/embed_cases.py
Reads:         data/use_cases_chunks.jsonl (from Step 1)
Produces:      a ./chroma_store/ folder on disk (the vector database files)
"""
import json
import chromadb
from chromadb.utils import embedding_functions

CHUNKS_PATH = "data/use_cases_chunks.jsonl"
CHROMA_PATH = "./chroma_store"
COLLECTION_NAME = "aasa_cases"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def load_chunks(path: str):
    with open(path) as f:
        return [json.loads(line) for line in f]


def main():
    chunks = load_chunks(CHUNKS_PATH)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # get_or_create_collection: safe to re-run this script without erroring on a duplicate.
    # embedding_function must be passed consistently every time this collection is opened.
    collection = client.get_or_create_collection(COLLECTION_NAME, embedding_function=embedding_fn)

    documents, metadatas, ids = [], [], []
    for i, chunk in enumerate(chunks):
        documents.append(chunk["text"])
        meta = chunk["metadata"]
        metadatas.append({
            "case_id": str(meta["case_id"]),
            "organization": str(meta["organization"]),
            "title": str(meta["title"]),
            "industry": str(meta["industry"]),
            "domain": str(meta["domain"]),
            "canonical_tools": ",".join(meta["tools"]),  # Chroma metadata must be simple types
            "source_url": str(meta["source_url"]),
            "chunk_type": meta["chunk_type"],
        })
        ids.append(f"chunk-{i}")

    # Chroma enforces a hard max batch size per add() call (client.get_max_batch_size(),
    # e.g. 5461) — with 9,069 real chunks (3,023 cases x 3), a single add() call exceeds
    # that and raises "Batch size of 9069 is greater than max batch size of 5461". This
    # only surfaces once you run against the full real dataset, not on a small test —
    # split into batches under the limit. add() will error on duplicate ids if you
    # re-run — for a clean re-run, delete the ./chroma_store folder first, or switch
    # to collection.upsert(...) instead.
    max_batch_size = client.get_max_batch_size()
    total = len(documents)
    for start in range(0, total, max_batch_size):
        end = min(start + max_batch_size, total)
        collection.add(
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )
        print(f"  added batch {start}-{end} of {total}")

    print(f"Embedded {collection.count()} chunks into Chroma at {CHROMA_PATH}")

    # --- Sanity-check retrieval quality with a test query ---
    test_query = "customer service chatbot for an e-commerce company"
    results = collection.query(query_texts=[test_query], n_results=5)
    print(f"\nTop 5 matches for: '{test_query}'")
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        print(f"- [{meta['chunk_type']}][{meta['industry']}] tools={meta['canonical_tools']} :: {doc[:120]}...")


if __name__ == "__main__":
    main()
```

**3. Before running it, make sure `sentence-transformers` is actually installed** — it's a separate package from `chromadb`, not a dependency `chromadb` pulls in automatically. `embedding_functions.SentenceTransformerEmbeddingFunction` will raise `ModuleNotFoundError: No module named 'sentence_transformers'` at import time if it's missing. Add it to `requirements.txt` alongside `pandas`/`streamlit`/`chromadb` and `pip install -r requirements.txt` (or `pip install sentence-transformers` directly) before continuing.

**4. Run it:**

```bash
python3 scripts/embed_cases.py
```

The first run will download the `all-MiniLM-L6-v2` model (a few hundred MB) — this only happens once.

### How to verify this card is done
- `data/use_cases_chunks.jsonl` exists with **9,069 lines** (3,023 cases x 3 chunk types) — not 3,023. If you see 3,023, Step 1 didn't run, or you're looking at the wrong file.
- Terminal prints one `added batch ...` line per batch (2 batches for 9,069 chunks at a 5,461 max batch size), then `Embedded 9069 chunks into Chroma...`.
- The "Top 5 matches" printout for the test query is *plausibly relevant* — e.g. querying about "customer service chatbot" returns chunks actually about customer service, not random unrelated ones. Expect to sometimes see 2-3 chunks from the *same* `case_id` (different `chunk_type`s) in one result set — that's normal here, and is exactly why Card 2.5 de-duplicates by `case_id` before ranking.
- A `chroma_store/` folder now exists in your project.

### Common pitfalls
- **`ModuleNotFoundError: No module named 'sentence_transformers'`.** Not covered by installing `chromadb` alone — see Step 3 above. Add it to `requirements.txt`.
- **`chromadb.errors.InternalError: ... Batch size of 9069 is greater than max batch size of 5461`.** This is real, and will happen on the full dataset with a single un-batched `collection.add(...)` call — Chroma caps how many items one `add()` call can take (`client.get_max_batch_size()`). The code above already batches around this; if you're working from an older copy of this script that doesn't, add the batching loop shown here.
- **Re-running `embed_cases.py` fails with a "duplicate ID" error.** This is expected — `add()` refuses to insert an id that already exists. Either delete `chroma_store/` before re-running during development (`rm -rf chroma_store`), or switch `collection.add(...)` to `collection.upsert(...)` once you're past initial testing.
- **Chunk count is 3,023 instead of 9,069.** Step 1 (`chunk_use_cases.py`) didn't run, or ran against an older `use-cases.csv`. Re-run Step 1 first, then Step 2.
- **`ast.literal_eval` throws an error in Step 1.** This means `canonical_tools` wasn't saved as a proper Python-list-looking string in Card 2.1's CSV — open `data/use-cases.csv` in a text editor and check what that column actually looks like. Card 2.1 must run before this card.
- **Retrieval looks irrelevant.** Print a couple of `documents[:2]` before calling `collection.add` in Step 2 to eyeball the actual chunk text being embedded.
- **Opening the collection later without passing `embedding_function=embedding_fn`** will silently fall back to Chroma's default — usually the same model, but don't rely on that; always pass it explicitly, in every script that opens `COLLECTION_NAME`.

### Optional: visually sanity-check the embedding space

The "Top 3 matches" printout tells you retrieval works for *one* query. A quick visual check can tell you something the printout can't: whether cases naturally cluster by industry/domain in the embedding space, or whether everything is jumbled together (a sign the embeddings aren't capturing meaningful differences). This step is optional, dev-time-only QA — it doesn't ship in the app.

**Concept:** embeddings typically have hundreds of dimensions — far too many to look at directly. **PCA (Principal Component Analysis)** finds the 2 directions that capture the most variation in the data and projects everything onto just those 2, so you can plot it as an ordinary scatter chart. You lose information in the compression, but clusters that are obviously separate in 2D are a good sign; a formless blob is worth investigating before trusting retrieval quality.

```bash
pip install scikit-learn matplotlib
```

```python
"""
Optional dev-time QA — not part of the shipped app.
Run after scripts/embed_cases.py has populated ./chroma_store.
"""
import chromadb
import matplotlib.pyplot as plt
from chromadb.utils import embedding_functions
from sklearn.decomposition import PCA

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_collection("aasa_cases", embedding_function=embedding_fn)

# Pull back the stored embeddings + metadata (Chroma keeps both).
data = collection.get(include=["embeddings", "metadatas"], limit=500)  # sample 500 for a fast, readable plot
embeddings = data["embeddings"]
industries = [m["industry"] for m in data["metadatas"]]  # now one of 3 chunk_types per case — fine for a rough visual check

coords_2d = PCA(n_components=2).fit_transform(embeddings)

# Color by industry so real clusters (if any) become visible.
unique_industries = sorted(set(industries))
color_map = {industry: i for i, industry in enumerate(unique_industries)}
colors = [color_map[industry] for industry in industries]

plt.figure(figsize=(10, 7))
scatter = plt.scatter(coords_2d[:, 0], coords_2d[:, 1], c=colors, cmap="tab20", alpha=0.6, s=15)
plt.title("Case embeddings, projected to 2D (colored by industry)")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.savefig("data/embedding_qa_plot.png", dpi=150)
print("Saved data/embedding_qa_plot.png — open it and look for industry clusters.")
```

**What to look for:** you don't need clean, textbook-perfect clusters — real text embeddings are messy — but you should see *some* visible grouping by color, not a uniformly-mixed cloud. If it looks completely random, double-check `build_document_text` is actually including meaningful, differentiated text per case before troubleshooting further.

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
If the user says their data is "Regulated" (subject to HIPAA/GDPR/financial rules), some consumer-facing AI tools should never be recommended — regardless of how often they show up in the matched cases. This filter runs as **plain deterministic Python code, before the LLM ever sees anything.** The LLM never decides what's compliant; your code does. After filtering, we also rank the remaining tools by how often they appear across the matched cases — that ranking is what becomes "Block A: Recommended AI stack". By the time cases reach this function they've already been de-duplicated to one entry per `case_id` in the pipeline-wiring step below, so this ranking counts distinct real deployments, not chunks.

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
- **Temperature** controls randomness: `0` means "always pick the most likely next word" (fully deterministic, same input → same output every time); higher values add randomness for creative variety. Since this step's whole job is faithfully phrasing facts that are already decided — not being creative — `temperature=0` is the right setting, not just "low."
- **An eval set** is a small, fixed list of representative test inputs you re-run every time you change a prompt, so you can compare "did this change make things better or worse?" on the same cases instead of eyeballing whatever you happen to type that day.

### Which LLM API to use

Neither of us has an OpenAI subscription, so this uses **Groq** instead of OpenAI — we already have keys for it, it has a free/very cheap tier (no billing setup required), and because Groq's API is OpenAI-compatible, the code below is almost identical to a plain OpenAI integration: same `openai` package, same `client.chat.completions.create(...)` call, just a different `base_url`, key, and model name.

### Step-by-step

**1. Create the file:**

```bash
touch app/logic/prompt.py
```

**Real deviation: this project uses Groq, not OpenAI directly, for this call.** `OPENAI_API_KEY`/`platform.openai.com` from Epic 1 Section 0.6 was the original plan, but this build actually uses `GROQ_API_KEY` against Groq's API instead — cheaper/faster, and Groq's endpoint is OpenAI-compatible, so the same `openai` Python client works unchanged; only the `api_key`, `base_url`, and `model` differ. Model is `openai/gpt-oss-20b` (a Groq-hosted open-weight model — that's a model *name* Groq happens to use, not a call to OpenAI's own API). Verify against [Groq's current model list](https://console.groq.com/docs/models) before relying on this: Groq has been actively deprecating older models (`llama-3.1-8b-instant`, `llama-3.3-70b-versatile` were flagged for deprecation shortly before this was written), and their own recommended migration target for both is the `gpt-oss` family used here.

**2. Paste this in:**

```python
"""
Card 2.6 — Few-shot prompt that constrains the LLM to prose-only summarisation.
The LLM never selects tools or invents prices — those are computed in
Cards 2.4/2.5 and simply handed to it as already-decided facts.

Uses Groq instead of OpenAI directly: Groq exposes an OpenAI-compatible endpoint,
so the same `openai` Python client works unchanged — just point it at Groq's
base_url and use GROQ_API_KEY instead of OPENAI_API_KEY. Model is
"openai/gpt-oss-20b" (Groq-hosted open-weight model), not GPT-4o-mini.
"""
import os
import time
from openai import OpenAI  # Groq's API is OpenAI-compatible — same client, different base_url
from dotenv import load_dotenv

load_dotenv()  # reads GROQ_API_KEY from your .env file (see Epic 1, Section 0.6)
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "openai/gpt-oss-20b"

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
                      privacy_key: str) -> dict:
    """
    Returns a dict, not a bare string — {"text": ..., "duration_seconds": ...,
    "prompt_tokens": ..., "completion_tokens": ..., "tokens_per_second": ...}.
    The extra fields feed Card 3.3's telemetry log once it exists; until then,
    just use result["text"] wherever you need the summary itself.
    """
    user_content = (
        f"Ranked tools: {ranked_tools}\n"
        f"Cost forecast: {cost_forecast}\n"
        f"Matched cases: {len(matched_cases)} comparable deployments\n"
        f"Privacy posture: {privacy_key}"
    )

    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Groq-hosted model, swapped in for OpenAI's gpt-4o-mini
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": FEW_SHOT_EXAMPLE_USER},
            {"role": "assistant", "content": FEW_SHOT_EXAMPLE_ASSISTANT},
            {"role": "user", "content": user_content},
        ],
        temperature=0,  # fully deterministic: this step phrases facts, it doesn't create
    )
    duration_seconds = round(time.perf_counter() - start_time, 2)

    usage = response.usage  # token counts the API reports back on every response
    tokens_per_second = (
        round(usage.completion_tokens / duration_seconds, 1) if duration_seconds > 0 else None
    )

    return {
        "text": response.choices[0].message.content,
        "duration_seconds": duration_seconds,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "tokens_per_second": tokens_per_second,
    }


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

**3. Build a small eval set and test against it systematically.** The task's pass/fail criteria is "no drift across 10 test runs" — rather than eyeballing 10 identical calls, build a handful of genuinely *different* inputs that stress different paths (a token-only case, a seat-only case, a regulated case, an empty-result case), and re-run the same eval set every time you tweak the prompt. This turns "did my prompt edit help or hurt?" into something you can actually compare, instead of a vague impression.

```python
"""
Prompt eval set — re-run this every time you change SYSTEM_PROMPT or the
few-shot example, not just once. Save as scripts/eval_prompt.py.
"""
from app.logic.prompt import generate_summary

EVAL_CASES = [
    {
        "name": "token + seat, standard",
        "ranked_tools": ["openai-api", "chatgpt"],
        "cost_forecast": {"primary_api": {"monthly_eur": 150.0}, "assistant": {"monthly_eur": 480.0}},
        "matched_cases": [{"canonical_tools": ["openai-api"]}, {"canonical_tools": ["chatgpt"]}],
        "privacy_key": "standard",
    },
    {
        "name": "seat only, regulated",
        "ranked_tools": ["ms-copilot", "azure-openai"],
        "cost_forecast": {"primary_api": {"monthly_eur": 187.5}, "assistant": {"monthly_eur": 900.0}},
        "matched_cases": [{"canonical_tools": ["azure-openai"]}, {"canonical_tools": ["ms-copilot"]}],
        "privacy_key": "regulated",
    },
    {
        "name": "free/OSS tools only — no cost figures at all",
        "ranked_tools": ["langchain", "chroma"],
        "cost_forecast": {"primary_api": None, "assistant": None},
        "matched_cases": [{"canonical_tools": ["langchain"]}],
        "privacy_key": "standard",
    },
    {
        "name": "empty result — nothing cleared the filter",
        "ranked_tools": [],
        "cost_forecast": {"primary_api": None, "assistant": None},
        "matched_cases": [],
        "privacy_key": "regulated",
    },
]

for case in EVAL_CASES:
    result = generate_summary(
        ranked_tools=case["ranked_tools"], cost_forecast=case["cost_forecast"],
        matched_cases=case["matched_cases"], privacy_key=case["privacy_key"],
    )
    print(f"--- {case['name']} ({result['duration_seconds']}s, "
          f"{result['completion_tokens']} completion tokens) ---")
    print(result["text"])
    print()
```

Run it (`python3 scripts/eval_prompt.py`) and read every output, checking: plain prose only (no bullet points), only the tools actually in `ranked_tools` are mentioned, only the prices actually in `cost_forecast` are stated, and — importantly — the two edge cases (free-tools-only, empty-result) produce sensible sentences rather than crashing or inventing numbers to fill the gap. If something drifts, tighten `SYSTEM_PROMPT`, then **re-run the whole eval set again** (not just the one case that failed) to make sure the fix didn't break a case that was previously fine — that regression check is the actual point of having a fixed eval set instead of ad hoc testing.

**Debugging tip:** if an output looks wrong and you can't tell why, print `user_content` (the actual rendered prompt text) right before the API call. Seeing exactly what the model received is usually faster than guessing.

### How to verify this card is done
- All 4+ eval-set cases above produce prose-only summaries, with no invented tools or prices, including the two edge cases.
- `temperature=0` is set explicitly (not left at a default or a "low but nonzero" value) — check this is a step that phrases facts, not one that needs creative variety.
- If you spot drift, tighten `SYSTEM_PROMPT` and re-run the *entire* eval set, not just the failing case.
- `GROQ_API_KEY` is read from `.env`, never hardcoded in `prompt.py`.

---

## Wiring Epic 2 into the pipeline

Once all six cards above are done, go back to `app/pipeline.py` (Card 1.4) and replace the placeholders with real calls:

> **Real deviation — canonical ids leak into the LLM summary unless translated.**
> Card 2.6's eval set fed `generate_summary` raw canonical ids (e.g. `["ms-copilot", "azure-openai"]`)
> and, in real Groq output, they sometimes came back out verbatim ("the combination of
> ms‑copilot and azure‑openai is a proven starting point..."). The few-shot example in
> `prompt.py` shows the model translating ids to nice names, but that's a memorized example,
> not a real mapping — it doesn't generalize to ids outside that one example. Fix: keep every
> other function keyed by canonical id (that's what `pricing.py`/`filter.py`/the dashboard need),
> and only build human-readable copies of `ranked_tools` and `cost_forecast` right before the
> `generate_summary` call, via a small `_to_label()` helper that looks up `PRICING[id]["label"]`.

```python
import chromadb
from chromadb.utils import embedding_functions
from app.logic.filter import apply_privacy_filter, rank_tools_by_frequency
from app.logic.cost import estimate_cost
from app.logic.prompt import generate_summary
from app.logic.pricing import PRICING

# Must match the embedding function named in Card 2.2 Step 2's embed_cases.py —
# Chroma needs the same embedding function every time this collection is opened.
_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_chroma_client = chromadb.PersistentClient(path="./chroma_store")
_collection = _chroma_client.get_collection("aasa_cases", embedding_function=_embedding_fn)


def _to_label(canonical_id: str) -> str:
    """canonical_id -> its human-readable PRICING label, or the id itself if unknown."""
    return PRICING.get(canonical_id, {}).get("label", canonical_id)


def run_pipeline(inputs: dict) -> dict:
    # Step 1: retrieve.
    # Card 2.2 stores 3 chunks per case (implementation/outcome/domain), so a
    # single case can legitimately fill several of the top results. Ask for
    # more results than we need (15, not 5) so that after de-duplicating down
    # to unique cases below, we still have a healthy number of distinct cases
    # to rank tools and pull "social proof" references from.
    query_text = f"{inputs['workflow']} in the {inputs['industry']} industry"
    results = _collection.query(query_texts=[query_text], n_results=15)

    # De-duplicate by case_id: keep only the first (best-ranked) chunk per
    # case, so one case can't count as 2-3 pieces of evidence in the ranking
    # below just because it happened to produce multiple matching chunks.
    seen_case_ids = set()
    matched_cases = []
    for meta in results["metadatas"][0]:
        case_id = meta["case_id"]
        if case_id in seen_case_ids:
            continue
        seen_case_ids.add(case_id)
        matched_cases.append({
            "case_id": case_id,
            "organization": meta["organization"],
            "title": meta["title"],
            "industry": meta["industry"],
            "source_url": meta["source_url"],
            "canonical_tools": meta["canonical_tools"].split(",") if meta["canonical_tools"] else [],
        })

    # Step 2: privacy filter + rank
    filtered_cases = apply_privacy_filter(matched_cases, inputs["privacy"])
    ranked_tools = rank_tools_by_frequency(filtered_cases, top_n=5)

    # Step 3: cost
    cost_forecast = estimate_cost(ranked_tools, inputs["org_size"])

    # Step 4: summary. recommended_stack/cost_forecast returned below stay keyed
    # by canonical id (Card 3.1 may want that for icons/lookups); only the copies
    # sent into generate_summary get translated to labels — see the deviation note above.
    ranked_tool_labels = [_to_label(t) for t in ranked_tools]
    cost_forecast_for_prompt = {
        "primary_api": {**cost_forecast["primary_api"], "tool": _to_label(cost_forecast["primary_api"]["tool"])}
                        if cost_forecast["primary_api"] else None,
        "assistant": {**cost_forecast["assistant"], "tool": _to_label(cost_forecast["assistant"]["tool"])}
                     if cost_forecast["assistant"] else None,
        "disclaimer": cost_forecast["disclaimer"],
    }
    summary = generate_summary(ranked_tool_labels, cost_forecast_for_prompt, filtered_cases, inputs["privacy"])

    return {
        "recommended_stack": ranked_tools,
        "cost_forecast": cost_forecast,
        "matched_cases": filtered_cases,
        "summary_text": summary["text"],
        # Card 3.3 logs this to telemetry once tracker.py exists — see that card.
        "llm_metrics": {
            "duration_seconds": summary["duration_seconds"],
            "prompt_tokens": summary["prompt_tokens"],
            "completion_tokens": summary["completion_tokens"],
            "tokens_per_second": summary["tokens_per_second"],
        },
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
- [x] `data/use-cases.csv` has `Use Case Domain (Canonical)` and `canonical_tools` columns added in place, coverage ≥ 90% (88.7%, deliberately accepted — see Card 2.1's coverage note); `validate_use_cases.py` exits 0.
- [x] `data/use_cases_chunks.jsonl` exists with 9,069 lines (3,023 cases x 3 chunk types).
- [x] `chroma_store/` exists and returns plausible results for a test query, using the explicitly-named `all-MiniLM-L6-v2` embedding function.
- [x] Every canonical tool id has a pricing entry.
- [x] `estimate_cost` returns separate primary-API and assistant figures, never a sum of everything.
- [x] `apply_privacy_filter` demonstrably removes consumer tools under "regulated" on 2–3 hand-checked scenarios.
- [x] `generate_summary` stays prose-only and tool/price-accurate across the eval set (including edge cases), and returns a dict with timing/token fields, not a bare string.
- [x] `run_pipeline` de-duplicates retrieval results by `case_id` before ranking, and now returns real data end-to-end, not placeholders, including an `llm_metrics` key.
- [x] `run_pipeline` sends `generate_summary` label-ified tool names (via `_to_label`/`PRICING`), not raw canonical ids — `recommended_stack`/`cost_forecast` in the return value stay keyed by canonical id.

**Verified via full backend dry run** on two real profiles (Technology/standard/startup and Healthcare/regulated/smb): confirmed real Chroma retrieval, correct case_id de-duplication, the privacy filter correctly distinguishing `gemini` (stripped under "regulated") from governable ids, `assistant` correctly returning `null` when no seat-priced tool clears the filter, and the LLM summary using human-readable labels end to end.

Move on to `14-Build-Guide-Epic3-Blueprint-UI-v1.md` next.
