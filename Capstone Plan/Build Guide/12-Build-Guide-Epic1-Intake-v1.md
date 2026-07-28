# Build Guide — Epic 1: Intelligent Intake & Profile Contextualisation

*Companion to the kanban board (cards 1.1–1.4) and `11-4-Week-Action-Plan-v1.md`. Written for someone who has never built a Python app before. Follow the sections in order — each card builds on the one before it.*

Every code block in this guide is complete and runnable — you can copy it exactly. Where a value depends on your real dataset (which you don't have loaded yet), the guide tells you exactly how to find the real value instead of guessing.

---

## 0. One-Time Project Setup

Do this once, before starting Card 1.1. Everything after this section assumes it's done.

### 0.1 Install Python

1. Open **Terminal** (press `Cmd + Space`, type "Terminal", hit Enter).
2. Check if Python is already installed: type `python3 --version` and press Enter.
   - If you see something like `Python 3.11.x` or higher, you're set — skip to 0.2.
   - If you see an error or a version below 3.10, install Python from [python.org/downloads](https://www.python.org/downloads/) (download the macOS installer, run it, click through the defaults).

### 0.2 Create the project folder

In Terminal, run these commands one at a time (press Enter after each):

```bash
mkdir -p ~/aasa-project/app/data
mkdir -p ~/aasa-project/app/logic
mkdir -p ~/aasa-project/app/analytics
mkdir -p ~/aasa-project/scripts
cd ~/aasa-project
```

**What just happened:** `mkdir -p` creates a folder (and any parent folders it needs). `cd` moves your Terminal "into" that folder — every command you type from now on happens inside `~/aasa-project` unless you say otherwise. You now have this structure:

```
aasa-project/
├── app/
│   ├── intake.py         ← Card 1.1
│   ├── validators.py     ← Card 1.3
│   ├── pipeline.py       ← Card 1.4
│   ├── dashboard.py      ← Card 3.1 (later)
│   ├── export.py         ← Card 3.2 (later)
│   ├── survey_modal.py   ← Card 3.4 (later)
│   ├── data/
│   │   └── options.py    ← Card 1.2
│   ├── logic/            ← Epic 2 files go here (later)
│   └── analytics/
│       └── tracker.py    ← Card 3.3 (later)
└── scripts/               ← Epic 2 one-off scripts go here (later)
```

You don't need to create the empty `.py` files yet — each card below tells you exactly when to create its file.

### 0.3 Create and activate a virtual environment

A **virtual environment** is an isolated box that holds only the packages this project needs, so they don't clash with anything else on your computer.

```bash
python3 -m venv venv
source venv/bin/activate
```

**What just happened:** the first line creates the box (a folder called `venv`). The second line "steps into" it. You'll know it worked because your Terminal prompt now starts with `(venv)`. **You must run `source venv/bin/activate` every time you open a new Terminal window to work on this project** — it doesn't stay on permanently.

### 0.4 Install the packages the whole project needs

With `(venv)` showing in your prompt, run:

```bash
pip install streamlit pandas chromadb openai python-dotenv
```

This installs:
- **streamlit** — turns a Python script into a web app (used in Epic 1 and 3).
- **pandas** — reads and manipulates the CSV of AI deployment cases (Epic 2).
- **chromadb** — the local vector database used for retrieval (Epic 2).
- **openai** — calls the LLM for the summary text (Epic 2, Card 2.6). Despite the name, this is the package we use to call **Groq** — Groq's API is OpenAI-compatible, so the same package works.
- **python-dotenv** — safely loads secret API keys from a file instead of hardcoding them.

This will take a minute or two. If you see a wall of text ending in something like `Successfully installed ...`, it worked.

### 0.5 Freeze your dependencies

```bash
pip freeze > requirements.txt
```

This writes every installed package + version into `requirements.txt`, so anyone (including future-you) can recreate the exact same setup with `pip install -r requirements.txt`.

### 0.6 Get an API key and store it safely

Card 2.6 needs to call an LLM. Neither of us has an OpenAI subscription, so this project uses **Groq** instead of OpenAI — same idea, and Groq's API is OpenAI-compatible, but with a free/very cheap tier and no billing setup required. To get a key:

1. Go to [console.groq.com/keys](https://console.groq.com/keys), sign up/log in, create a key, copy it. No billing details needed.
2. Back in Terminal, create a secrets file:

```bash
touch .env
echo "GROQ_API_KEY=paste-your-key-here" >> .env
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
```

**Never paste your API key directly into a `.py` file or share it in chat/screenshots.** The `.gitignore` lines mean that if you ever push this project to GitHub, the key and the virtual-environment folder won't be uploaded.

### 0.7 Sanity-check Streamlit works

Create a throwaway test file:

```bash
echo 'import streamlit as st
st.title("Hello, AASA!")' > test_app.py
streamlit run test_app.py
```

Your browser should open automatically to `http://localhost:8501` showing "Hello, AASA!" in large text. If it does, Streamlit works — close the browser tab, go back to Terminal, press `Ctrl + C` to stop the app, and delete the test file: `rm test_app.py`.

**You're now ready for Card 1.1.**

---

## Card 1.1 — Render input controls & dark-mode CSS grid

**File:** `app/intake.py` · **Depends on:** nothing · **Effort:** ~0.5 day

### Goal in plain language
Build the page the user sees first: a dark-themed form with 5 boxes to fill in (their AI workflow, industry, company size, privacy needs, and budget). At this stage we're only building the *look* — the dropdown lists will be wired up properly in Card 1.2, and the "what happens when you click Submit" logic comes in Cards 1.3–1.4. For now, every field can use placeholder options.

### Concepts you need first
- **Streamlit** turns a plain Python script into a web page. Every time you call a Streamlit function like `st.text_input(...)`, it draws a widget on the page.
- **Widgets** are the interactive boxes: text boxes, dropdowns, number inputs, buttons.
- Streamlit re-runs your *entire script from top to bottom* every time the user interacts with something. This feels strange at first but is the core mental model — don't fight it.

### Step-by-step

**1. Create the file.**

```bash
touch app/intake.py
```

**2. Open it in any text editor** (VS Code is free and beginner-friendly: [code.visualstudio.com](https://code.visualstudio.com)). If you have VS Code installed, you can open the whole project folder with:

```bash
code ~/aasa-project
```

**3. Paste this starter code into `app/intake.py`:**

```python
import streamlit as st

# --- Page setup: must be the first Streamlit command in the script ---
st.set_page_config(
    page_title="AASA — AI-Assisted Stack Architect",
    page_icon="🧭",
    layout="centered",
)

# --- Dark, "neo-industrial" styling ---
# st.markdown with unsafe_allow_html=True lets us inject raw CSS.
DARK_CSS = """
<style>
    .stApp {
        background-color: #0f1115;
        color: #e8e9ec;
    }
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        letter-spacing: 0.02em;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
    }
    div[data-baseweb="select"] > div {
        background-color: #1b1e26;
        border-color: #2b2f3a;
    }
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.title("🧭 AI-Assisted Stack Architect")
st.caption("Five constraints in. A data-backed blueprint out.")

# --- The 5-field form ---
# Placeholder options for now — Card 1.2 replaces the hardcoded lists below
# with real ones derived from the case dataset.
with st.form("intake_form"):
    workflow = st.selectbox(
        "Target AI Workflow",
        ["Customer Service", "Content Generation", "Coding Assistant",
         "Data Analysis", "CX & Personalization"],  # placeholder — Card 1.2
    )
    industry = st.selectbox(
        "Industry",
        ["Technology", "Healthcare", "Retail", "Finance", "Any industry"],  # placeholder
    )
    org_size = st.selectbox(
        "Organisation Size",
        ["Solo / Pre-seed (1–4)", "Startup (5–20)", "SMB (21–200)",
         "Mid-Market (201–1000)", "Enterprise (1000+)"],
    )
    privacy = st.radio(
        "Data-Privacy Posture",
        ["Standard", "Regulated"],
        horizontal=True,
        help="Regulated = you handle data subject to HIPAA/GDPR/financial "
             "regulation and need governable, self-hostable tools.",
    )
    budget = st.number_input(
        "Monthly Budget (€)",
        min_value=0, step=50, value=800,
    )

    submitted = st.form_submit_button("Generate my blueprint")

if submitted:
    # Card 1.3 will replace this with real validation.
    # Card 1.4 will replace this with a real pipeline call.
    st.write("Form submitted — validation and pipeline wiring come next.")
    st.json({
        "workflow": workflow,
        "industry": industry,
        "org_size": org_size,
        "privacy": privacy,
        "budget": budget,
    })
```

**4. Run it:**

```bash
streamlit run app/intake.py
```

### How to verify this card is done
- The browser opens with a dark page titled "🧭 AI-Assisted Stack Architect".
- All 5 fields render without errors and without text being cut off.
- Clicking "Generate my blueprint" shows the JSON of what you typed/selected.
- Resize your browser window narrower (or open dev tools and simulate a phone width, ~375px) — the form should still be fully readable with no horizontal scrollbar. If something overflows, add `layout="centered"` (already set above) and avoid putting widgets side-by-side in columns for this MVP.

### Common pitfalls
- **"set_page_config must be called first"** error → make sure `st.set_page_config(...)` is the very first Streamlit call in the file, before even the CSS.
- Nothing happens when you save the file → Streamlit doesn't auto-reload by default in older versions; click the "Rerun" button that appears top-right, or press `R`.
- Page looks unstyled → check you didn't accidentally delete `unsafe_allow_html=True`.

---

## Card 1.2 — Map Org Size / Industry to dropdown options

**File:** `app/data/options.py` · **Depends on:** 1.1 · **Effort:** ~0.5 day

### Goal in plain language
Card 1.1 used hardcoded, made-up dropdown lists. This card replaces the guesswork with (a) a small fixed taxonomy for Organisation Size — which doesn't exist in the case dataset at all, so we're defining our own sensible bands — and (b) real Industry / Workflow lists **pulled from your actual dataset**, not invented.

### Why Organisation Size is hand-built, not derived
The 3,023-case dataset has no organisation-size column to join against (verified in the Handbook, §2). So Org Size is *our own* taxonomy, used only to help contextualise the user's situation for the LLM summary later — not to filter the case data.

### Step-by-step

**1. Create the file:**

```bash
touch app/data/options.py
```

**2. Add the fixed Org Size taxonomy** — paste this into `app/data/options.py`:

```python
"""
Static and derived dropdown option lists for the intake form.
Org sizes are our own taxonomy (no such field exists in the case dataset).
Industries / workflows are derived from the real dataset once you have it —
see the instructions below Step 3.
"""

ORG_SIZES = {
    "solo": "Solo / Pre-seed (1-10 people)",
    "startup": "Startup (11-100 people)",
    "smb": "Small-Medium Business (101-200 people)",
    "mid": "Mid-Market (201-1,000 people)",
    "ent": "Enterprise (1,000+ people)",
}
# Bands revised 2026-07-27 after the first real user-test session (the original
# 1-4 / 5-20 / 21-200 ranges left a gap testers fell into). If you change these
# ranges again, re-derive cost.py's ASSUMED_SEATS and ASSUMED_TOKEN_VOLUME_MM —
# they are sized against the band widths. See Build Guide 18, Update C.

PRIVACY_POSTURES = {
    "standard": "Standard",
    "regulated": "Regulated (HIPAA / GDPR / financial data)",
}
```

**3. Derive your dataset's real Industry and Workflow values.**

This used to require a placeholder-list stopgap because the real column names and a clean categorisation weren't available yet. They are now: the colleague's branch (`stackpunk`/`Gabi`) already normalised the domain data for real — see `19-Gabi-Branch-Integration-Analysis-v1.md` for the full story. Concretely, that means running **Card 2.1's Step 0** first (`scripts/validate_use_cases.py` then `scripts/normalize_domains.py` against `data/use-cases.csv`) — see `13-Build-Guide-Epic2-Retrieval-v1.md` — which adds a `Use Case Domain (Canonical)` column (18 clean values, no near-duplicate spellings) to sit alongside the existing `Use Case Industry` column. There's no need to hand-invent a dropdown list or wait on a placeholder: once Step 0 has run, both dropdowns can be derived directly from the real data, no guessing involved.

Don't have `data/use-cases.csv` yet? It's a third-party, MIT-licensed dataset (not ours), intentionally gitignored rather than committed here — download your own copy from [`abbasmahdi-ai/ai-use-cases-library`](https://github.com/abbasmahdi-ai/ai-use-cases-library) on GitHub. See `13-Build-Guide-Epic2-Retrieval-v1.md`'s "Before you start" section for the license/citation details.

Run this **one-off** snippet in Terminal to pull the real lists:

```bash
python3 -c "
import pandas as pd
df = pd.read_csv('data/use-cases.csv')
print('Industries:', sorted(df['Use Case Industry'].dropna().unique()))
print()
print('Workflows (canonical domains):', sorted(df['Use Case Domain (Canonical)'].dropna().unique()))
"
```

Paste the two printed lists into `options.py`, replacing the old placeholder block from Step 2:

```python
# Derived from the real dataset — see Card 2.1 Step 0 (13-Build-Guide-Epic2-Retrieval-v1.md).
# Re-run the snippet above and update these two lists if the underlying data ever changes.
INDUSTRIES = ["Any industry"] + ["Technology", "Healthcare", ...]        # paste your real, printed list here
WORKFLOWS = ["Any workflow"] + ["Customer Service", "Content Generation", ...]  # paste the 18 canonical domains here
```

("Any industry" / "Any workflow" are added by hand as an explicit "no preference" option — they won't appear in the printed list since they're not real data values.)

**4. Wire the new options into Card 1.1.** Open `app/intake.py` and change the import at the top plus the two `selectbox` calls:

```python
from app.data.options import ORG_SIZES, PRIVACY_POSTURES, INDUSTRIES, WORKFLOWS
```

```python
workflow = st.selectbox("Target AI Workflow", WORKFLOWS)
industry = st.selectbox("Industry", INDUSTRIES)
org_size_key = st.selectbox(
    "Organisation Size",
    options=list(ORG_SIZES.keys()),
    format_func=lambda k: ORG_SIZES[k],   # shows the friendly label, stores the short key
)
privacy_key = st.radio(
    "Data-Privacy Posture",
    options=list(PRIVACY_POSTURES.keys()),
    format_func=lambda k: PRIVACY_POSTURES[k],
    horizontal=True,
)
```

`format_func` is a Streamlit feature that lets the dropdown *display* a friendly label ("Enterprise (1,000+ people)") while your code *receives* the short internal key (`"ent"`) — which is what the rest of the pipeline should work with.

### How to verify this card is done
- Running `streamlit run app/intake.py` shows the same form, but the dropdown values now come from `options.py`, not hardcoded inline lists.
- Selecting "Enterprise (1,000+ people)" and submitting shows `org_size_key` as `"ent"` in the debug JSON, not the long label.
- `INDUSTRIES` and `WORKFLOWS` match the real unique values from `data/use-cases.csv` after Card 2.1 Step 0 has run — no invented categories, and `WORKFLOWS` has exactly 18 real values (+ "Any workflow").

### Common pitfalls
- `ModuleNotFoundError: No module named 'app'` → run Streamlit from the project root (`~/aasa-project`), not from inside `app/`. Also create an empty `app/__init__.py` and `app/data/__init__.py` file so Python treats these as importable packages: `touch app/__init__.py app/data/__init__.py`.
- `KeyError: 'Use Case Domain (Canonical)'` → Card 2.1 Step 0 hasn't been run yet against `data/use-cases.csv`. Run `validate_use_cases.py` then `normalize_domains.py` first (see `13-Build-Guide-Epic2-Retrieval-v1.md`).
- If you genuinely need to unblock the Card 1.1 UI *before* Card 2.1 Step 0 is done, it's fine to temporarily hardcode a short list in Step 3 and swap in the real `INDUSTRIES`/`WORKFLOWS` once Step 0 has run — just don't ship the hardcoded version.

---

## Card 1.3 — Frontend validation

**File:** `app/validators.py` · **Depends on:** 1.2 · **Effort:** ~0.5 day

### Goal in plain language
Before we hand the form's data to the backend, catch obvious problems: did the user leave a field on some meaningless default, or type a budget that isn't a real number? A clear inline message beats a confusing crash three steps later.

### Step-by-step

**1. Create the file:**

```bash
touch app/validators.py
```

**2. Write a single, pure function that takes the form's values and returns a pass/fail result.** "Pure" means: given the same inputs, it always returns the same output, and it doesn't print anything or touch the screen itself — that's the caller's job. This makes it easy to test on its own, separate from Streamlit.

```python
"""
Validation rules for the 5-field intake form.
Returns (is_valid: bool, error_message: str) — error_message is "" when valid.
"""

def validate_intake(workflow: str, industry: str, org_size_key: str,
                     privacy_key: str, budget) -> tuple[bool, str]:
    if not workflow or not workflow.strip():
        return False, "Please select a target AI workflow."

    if not industry or not industry.strip():
        return False, "Please select an industry."

    if not org_size_key:
        return False, "Please select your organisation size."

    if privacy_key not in ("standard", "regulated"):
        return False, "Please choose a data-privacy posture."

    # Budget must be a real, non-negative number.
    try:
        budget_value = float(budget)
    except (TypeError, ValueError):
        return False, "Monthly budget must be a number."

    if budget_value <= 0:
        return False, "Monthly budget must be greater than zero."

    return True, ""
```

**3. Wire it into `app/intake.py`.** Add the import at the top:

```python
from app.validators import validate_intake
```

Replace the `if submitted:` block at the bottom of `intake.py` with:

```python
if submitted:
    is_valid, error_message = validate_intake(
        workflow, industry, org_size_key, privacy_key, budget
    )
    if not is_valid:
        st.error(error_message)
    else:
        st.success("Looks good — ready for the pipeline (Card 1.4).")
        st.json({
            "workflow": workflow, "industry": industry,
            "org_size": org_size_key, "privacy": privacy_key,
            "budget": budget,
        })
```

### How to test this without even opening the browser
This is a good moment to learn a habit that pays off for the rest of the project: **test a function directly in Terminal before trusting it inside the app.**

```bash
python3 -c "
from app.validators import validate_intake
print(validate_intake('Customer Service', 'Technology', 'startup', 'standard', 800))   # expect (True, '')
print(validate_intake('', 'Technology', 'startup', 'standard', 800))                    # expect (False, '...workflow')
print(validate_intake('Customer Service', 'Technology', 'startup', 'standard', 'abc'))  # expect (False, '...number')
print(validate_intake('Customer Service', 'Technology', 'startup', 'standard', -5))      # expect (False, '...greater than zero')
"
```

If all four lines print what the comment says, the card is done — before you even touch the UI.

### Common pitfalls
- Streamlit's `number_input` already restricts input to numbers in most cases, so the "not a number" test matters more if you ever swap that widget for a plain text box — keep the check anyway; defensive code doesn't hurt.
- Don't validate inside the Streamlit widgets themselves (e.g., don't try to disable the submit button) — for the MVP, validate *after* submit and show `st.error`. Simpler, and it's what the task card specifies ("halted with a clear inline message").

---

## Card 1.4 — Direct pipeline call (in-process, no webhook)

**File:** `app/pipeline.py` · **Depends on:** 1.3 · **Effort:** ~0.5 day

### Goal in plain language
Once the form is valid, something needs to actually do the work: normalise the request, search the case library, filter, cost it out, and summarise it. In a more complex system that "something" might be a separate service you call over the network (a **webhook**) — but here, everything runs in the same Python process, so it's just a normal function call. This card creates that function as a placeholder that Epic 2's real logic will slot into later, and adds a loading spinner so the user knows something is happening.

### Concepts you need first
- A **webhook** is when your app sends a request over the network (like calling a website) to a separate service and waits for a reply. It adds failure points: network timeouts, authentication, serialization bugs.
- An **in-process function call** is just calling a Python function that lives in the same program. No network involved — if it fails, you get a normal Python error you can debug directly, not a mysterious timeout.

### Step-by-step

**1. Create the file:**

```bash
touch app/pipeline.py
```

**2. Write a placeholder pipeline function.** This is intentionally a stub — Cards 2.1–2.6 will fill in the real steps one at a time. Building the "shape" of the function now means each Epic 2 card only has to fill in one section later, instead of you writing one giant function all at once.

```python
"""
The single entry point that turns validated form inputs into a blueprint.
Each numbered step below is a placeholder — Epic 2 cards replace them in order:
  Step 1 (normalise/retrieve) <- Cards 2.1, 2.2
  Step 2 (privacy filter)     <- Card 2.5
  Step 3 (cost)               <- Cards 2.3, 2.4
  Step 4 (LLM summary)        <- Card 2.6
"""
import time


def run_pipeline(inputs: dict) -> dict:
    """
    inputs: {"workflow": str, "industry": str, "org_size": str,
             "privacy": str, "budget": float}
    returns: a dict the dashboard (Card 3.1) can render directly.
    """
    # --- Step 1: retrieve comparable cases (placeholder) ---
    # Real version (Card 2.2) will query the Chroma vector store here.
    matched_cases = []

    # --- Step 2: privacy filter (placeholder) ---
    # Real version (Card 2.5) removes ungovernable tools when inputs["privacy"] == "regulated".
    filtered_cases = matched_cases

    # --- Step 3: cost forecast (placeholder) ---
    # Real version (Cards 2.3-2.4) looks up the pricing table and computes an estimate.
    cost_forecast = {"primary_api_monthly": None, "assistant_monthly": None}

    # --- Step 4: LLM summary (placeholder) ---
    # Real version (Card 2.6) calls the model with a few-shot prompt.
    summary_text = (
        "This is a placeholder blueprint. Once Epic 2 is wired up, this will "
        "be a real, evidence-backed recommendation."
    )

    time.sleep(1)  # simulates work so the loading spinner (Step 3 below) is visible

    return {
        "recommended_stack": [],       # Card 3.1 renders this as Block A
        "cost_forecast": cost_forecast,  # Card 3.1 renders this as Block B
        "matched_cases": filtered_cases,  # Card 3.1 renders this as Block C
        "summary_text": summary_text,
    }
```

**3. Wire it into `app/intake.py`** with a loading state. Add the import:

```python
from app.pipeline import run_pipeline
```

Update the `else` branch (the valid-form case) from Card 1.3:

```python
    else:
        with st.spinner("Building your blueprint..."):
            result = run_pipeline({
                "workflow": workflow, "industry": industry,
                "org_size": org_size_key, "privacy": privacy_key,
                "budget": budget,
            })
        st.session_state.result = result  # persist across reruns — see note below
```

Then, **outside and below** the `if submitted:` block entirely (not nested inside it), add:

```python
# Renders on every rerun as long as a result exists — not gated on `submitted`.
# See "Why not render inside if submitted:" below for why this matters.
if "result" in st.session_state:
    st.success("Blueprint ready — see below.")
    st.json(st.session_state.result)  # Card 3.1 will replace this raw JSON dump with the real 3-block layout
```

> **Why not just render inside `if submitted:`?** Streamlit reruns your *entire script* on every single interaction — not just on form submit. Once Epic 3 adds buttons *inside* the results view (the clipboard-export button in Card 3.2, the trust-survey submit button in Card 3.4), clicking either of those triggers a rerun too. On that rerun, `submitted` goes back to `False` (it's only `True` on the run immediately after the form's own submit button was clicked) — so if the blueprint only renders inside `if submitted:`, the *entire blueprint disappears* the instant someone clicks export or answers the survey. Storing the result in `st.session_state` and rendering from there, in a separate check that doesn't depend on `submitted`, means the blueprint stays on screen no matter what else gets clicked inside it. This is the same `st.session_state` pattern used for `st.session_state.tasks` in a typical Streamlit task-board example — state that needs to survive a rerun always goes in `st.session_state`, never in a plain local variable.

### How to verify this card is done
- Submitting a valid form shows a brief "Building your blueprint..." spinner (thanks to `time.sleep(1)` — remove that line once Epic 2's real steps are slow enough on their own) followed by the placeholder JSON result.
- **Add a temporary throwaway button** below the JSON (e.g. `st.button("test rerun")`) and click it. The JSON result should **stay visible** — if it disappears, the result got rendered inside `if submitted:` instead of the separate `if "result" in st.session_state:` check. Delete the throwaway button once this passes.
- `run_pipeline` is a plain function you can call from a Python shell with no Streamlit running at all — this proves there's no hidden network dependency:

```bash
python3 -c "
from app.pipeline import run_pipeline
print(run_pipeline({'workflow':'Customer Service','industry':'Technology','org_size':'startup','privacy':'standard','budget':800}))
"
```

### Common pitfalls
- Don't reach for `requests`, webhooks, or any HTTP call here — if you find yourself wanting to `import requests` in this file, stop; that's exactly the risk this card exists to remove.
- Keep `run_pipeline`'s input/output shape (the dict keys above) stable — Epic 2 and Epic 3 cards both depend on it staying consistent.

---

## Epic 1 — Done Checklist
- [X] `streamlit run app/intake.py` renders a dark 5-field form with no errors.
- [X] Dropdown options come from `app/data/options.py`, not hardcoded inline lists.
- [X] Submitting an incomplete/invalid form shows a clear inline error and does not proceed.
- [X] Submitting a valid form shows a loading spinner, then a result — with no network calls involved.
- [X] The result is stored in `st.session_state` and rendered outside `if submitted:` — clicking any other button on the page doesn't make it disappear.
- [X] All four card files exist: `app/intake.py`, `app/data/options.py`, `app/validators.py`, `app/pipeline.py`.

Move on to `13-Build-Guide-Epic2-Retrieval-v1.md` next — it fills in the real logic behind `run_pipeline`.
