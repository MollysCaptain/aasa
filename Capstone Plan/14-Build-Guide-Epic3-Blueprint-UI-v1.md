# Build Guide — Epic 3: Actionable Blueprint UI

*Companion to the kanban board (cards 3.1–3.4). Assumes Epic 1 (`app/intake.py`, `app/pipeline.py`) and Epic 2 (real data flowing through `run_pipeline`) are both done — this epic is about *displaying* the real output nicely, exporting it, and measuring whether people trust it.*

---

## Card 3.1 — Render the 3-block layout

**File:** `app/dashboard.py` · **Depends on:** 2.6 · **Effort:** ~1.0 day

### Goal in plain language
Turn the raw dictionary `run_pipeline()` returns into something a non-technical founder can actually read: three clearly separated blocks — the recommended stack (with evidence of how often each tool showed up in real deployments), the cost forecast, and the real case references with clickable source links.

### Step-by-step

**1. Create the file:**

```bash
touch app/dashboard.py
```

**2. Paste this in:**

```python
"""
Card 3.1 — Render the 3-block blueprint layout.
Block A: Recommended AI stack (ranked, evidence-labelled)
Block B: Cost forecast (primary API + assistant, clearly illustrative)
Block C: Real case references (source-linked)
"""
import streamlit as st
from app.logic.pricing import PRICING


def render_blueprint(result: dict):
    st.markdown("## 🧩 Your AI Stack Blueprint")

    _render_stack_block(result["recommended_stack"], result["matched_cases"])
    st.divider()
    _render_cost_block(result["cost_forecast"])
    st.divider()
    _render_case_references_block(result["matched_cases"])
    st.divider()
    st.markdown("### 📝 Summary")
    st.write(result["summary_text"])


def _render_stack_block(ranked_tools: list, matched_cases: list):
    st.markdown("### 1️⃣ Recommended AI Stack")
    if not ranked_tools:
        st.info("No tools cleared the privacy filter for this combination of inputs. "
                 "Try relaxing the privacy posture or broadening the workflow.")
        return

    # Evidence count: how many matched cases mention each tool — this is the
    # "evidence bar" the task card asks for.
    total_cases = max(len(matched_cases), 1)
    for rank, tool_id in enumerate(ranked_tools, start=1):
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        pricing_model = entry.get("model", "unknown")
        evidence_count = sum(1 for c in matched_cases if tool_id in c.get("canonical_tools", []))
        evidence_pct = int(100 * evidence_count / total_cases)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{rank}. {label}**  ·  `{pricing_model}`-priced")
            st.progress(evidence_pct / 100, text=f"Seen in {evidence_count}/{total_cases} matched cases")
        with col2:
            st.caption(pricing_model.upper())


def _render_cost_block(cost_forecast: dict):
    st.markdown("### 2️⃣ Illustrative Cost Forecast")
    st.caption(cost_forecast.get("disclaimer", ""))

    primary = cost_forecast.get("primary_api")
    assistant = cost_forecast.get("assistant")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Primary API**")
        if primary and primary.get("monthly_eur") is not None:
            st.metric(primary["tool"], f"€{primary['monthly_eur']:.2f}/mo")
            st.caption(primary.get("assumption", ""))
        else:
            st.caption("No token-priced tool in the top recommendations.")
    with col2:
        st.markdown("**Assistant / SaaS**")
        if assistant and assistant.get("monthly_eur") is not None:
            st.metric(assistant["tool"], f"€{assistant['monthly_eur']:.2f}/mo")
            st.caption(assistant.get("assumption", ""))
        else:
            st.caption("No seat-priced tool in the top recommendations.")


def _render_case_references_block(matched_cases: list):
    st.markdown("### 3️⃣ Real Case References")
    if not matched_cases:
        st.info("No comparable cases matched — this can happen with very narrow inputs.")
        return

    for case in matched_cases[:4]:  # show up to 4, per the prototype's own convention
        org = case.get("org", "Unknown organisation")
        title = case.get("title", "")
        industry = case.get("industry", "")
        url = case.get("source_url", "")
        with st.container(border=True):
            st.markdown(f"**{org}** — {title}")
            st.caption(industry)
            if url:
                st.markdown(f"[Source]({url})")
```

**3. Wire it into `app/intake.py`.** Replace the temporary `st.json(result)` line from Card 1.4 with:

```python
from app.dashboard import render_blueprint
...
        render_blueprint(result)
```

**4. Run it and test at mobile width.** With `streamlit run app/intake.py` running, open your browser's developer tools (`Cmd+Option+I` on Mac in Chrome), toggle device toolbar, and pick a ~375px-wide phone preset. Check nothing overflows horizontally.

### How to verify this card is done
- Submitting the form shows three clearly-labelled, visually distinct sections in order: Stack → Cost → Case References → Summary.
- Each recommended tool shows an evidence bar (a progress bar), not just a bare name.
- Every case reference has a clickable source link.
- The layout holds up at 375px width with no horizontal scrollbar.

### Common pitfalls
- If `matched_cases` dictionaries don't actually contain `org`/`title`/`source_url` keys yet (Card 2.2's Chroma metadata may only include `canonical_tools`/`industry`/`source_url` as built in Epic 2's guide), go back to `app/pipeline.py`'s Step 1 and make sure you're also pulling `org`, `title`, and `source_url` out of the Chroma metadata into each case dict — add whichever fields Card 3.1 needs to the `metadatas` list back in `scripts/embed_cases.py`, then re-run that script.

---

## Card 3.2 — Clipboard export handler

**File:** `app/export.py` · **Depends on:** 3.1 · **Effort:** ~0.5 day

### Goal in plain language
Let the user copy the whole blueprint as plain text so they can paste it into a Slack message, email, or doc to share with their team — without needing to screenshot the app.

### Step-by-step

**1. Create the file:**

```bash
touch app/export.py
```

**2. Paste this in:**

```python
"""
Card 3.2 — Turn the blueprint dict into a plain-text block the user can copy.
"""
from app.logic.pricing import PRICING


def blueprint_to_text(result: dict) -> str:
    lines = ["=== AI Stack Architect — Blueprint ===", ""]

    lines.append("RECOMMENDED STACK:")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"  {rank}. {label}")
    lines.append("")

    cost = result["cost_forecast"]
    lines.append("COST FORECAST (illustrative):")
    if cost.get("primary_api") and cost["primary_api"].get("monthly_eur") is not None:
        lines.append(f"  Primary API: €{cost['primary_api']['monthly_eur']:.2f}/mo")
    if cost.get("assistant") and cost["assistant"].get("monthly_eur") is not None:
        lines.append(f"  Assistant:   €{cost['assistant']['monthly_eur']:.2f}/mo")
    lines.append(f"  ({cost.get('disclaimer', '')})")
    lines.append("")

    lines.append("REAL CASE REFERENCES:")
    for case in result["matched_cases"][:4]:
        org = case.get("org", "Unknown organisation")
        url = case.get("source_url", "")
        lines.append(f"  - {org} ({url})")
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(result.get("summary_text", ""))

    return "\n".join(lines)
```

**3. Add a copy button to `app/dashboard.py`.** Streamlit (1.30+) has a built-in way to make text copyable: showing it in a code block gives the user a hover-to-copy icon for free, with no extra JavaScript. Add this at the end of `render_blueprint`:

```python
from app.export import blueprint_to_text
...
    st.markdown("### 📋 Export")
    blueprint_text = blueprint_to_text(result)
    st.code(blueprint_text, language=None)
    st.caption("Hover the code block above and click the copy icon in the top-right corner.")
```

> **If your Streamlit version is older** and `st.code` doesn't show a copy icon, fall back to a manual-select box instead — this is the "manual-select fallback" the risk notes call for:
> ```python
> st.text_area("Select all (Cmd/Ctrl+A) and copy (Cmd/Ctrl+C):", blueprint_text, height=200)
> ```

### How to verify this card is done
- After generating a blueprint, a plain-text version of it is visible and copyable — test it by actually pasting it into a Notes app or email draft and checking it reads sensibly.
- Test on at least one other browser if possible — the fallback text area should work everywhere even if the native copy icon doesn't.

---

## Card 3.3 — Session telemetry

**File:** `app/analytics/tracker.py` · **Depends on:** 1.4 · **Effort:** ~0.5 day

### Goal in plain language
We want two numbers by the end of testing: how long it takes someone to go from opening the form to seeing results (form completion velocity), and where in the form people give up (field abandonment). For a 2-person team with no analytics budget, a simple local log file is enough — no external analytics service needed.

### Step-by-step

**1. Create the file:**

```bash
touch app/analytics/tracker.py app/analytics/__init__.py
```

**2. Paste this in:**

```python
"""
Card 3.3 — Lightweight local event log. Appends one JSON line per event to
data/telemetry.log — "trend only" metrics, per the Handbook's metric list,
not a dashboard-grade analytics pipeline.
"""
import json
import time
from pathlib import Path

LOG_PATH = Path("data/telemetry.log")
LOG_PATH.parent.mkdir(exist_ok=True)


def log_event(event_name: str, **fields):
    """
    event_name examples used across this project:
      "form_start", "field_changed", "form_submit", "results_shown",
      "export_clicked", "survey_submitted"
    """
    entry = {"event": event_name, "timestamp": time.time(), **fields}
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
```

**3. Wire it into `app/intake.py`.** Streamlit's `st.session_state` persists values across reruns within one browser session — use it to record when the form was first opened, so you can compute total elapsed time at submit:

```python
from app.analytics.tracker import log_event

# Near the top of intake.py, before the form:
if "form_start_time" not in st.session_state:
    st.session_state.form_start_time = time.time()
    log_event("form_start")
```

(add `import time` at the top of `intake.py` if it's not already there.)

Inside the `if submitted:` / valid-form branch, right after the pipeline call succeeds:

```python
elapsed_seconds = time.time() - st.session_state.form_start_time
log_event("results_shown", elapsed_seconds=round(elapsed_seconds, 1))
```

And log the export click inside `render_blueprint` — but since that click happens via the copy icon (which Streamlit doesn't give you a callback for), log the export *section being shown* instead as a reasonable proxy, or add an explicit "I copied this" button if you want a true click event:

```python
if st.button("✅ I've copied my blueprint"):
    log_event("export_clicked")
    st.success("Noted — thanks!")
```

### How to verify this card is done
- After a few form submissions, `data/telemetry.log` contains one JSON line per event, each with a timestamp.
- You can compute a rough "form completion velocity" by reading the log:

```bash
python3 -c "
import json
starts, shows = [], []
for line in open('data/telemetry.log'):
    e = json.loads(line)
    if e['event'] == 'form_start': starts.append(e)
    if e['event'] == 'results_shown': shows.append(e)
print(f'{len(shows)} completed sessions')
if shows:
    avg = sum(e['elapsed_seconds'] for e in shows) / len(shows)
    print(f'Average time to results: {avg:.1f}s')
"
```

### Common pitfalls
- Don't try to build field-level abandonment tracking with fine-grained JS event hooks — that's over-engineering for a 2-person, 4-week MVP. Session-state + a log line at submit is what the Technical Work Breakdown explicitly scoped ("reduced telemetry granularity vs. a dedicated tool — acceptable trade-off").

---

## Card 3.4 — Post-generation trust survey

**File:** `app/survey_modal.py` · **Depends on:** 3.1 · **Effort:** ~0.5 day

### Goal in plain language
Right after someone sees their blueprint, ask one simple question: "How much do you trust this recommendation?" on a 1–5 scale. This single number, averaged across your 5–8 real testers, is your headline validation metric (target: ≥4/5 median).

### Step-by-step

**1. Create the file:**

```bash
touch app/survey_modal.py
```

**2. Paste this in:**

```python
"""
Card 3.4 — Post-generation 1-5 trust rating.
Uses a plain inline form (simpler and more reliable across Streamlit versions
than a true modal dialog) placed right below the blueprint.
"""
import streamlit as st
from app.analytics.tracker import log_event


def render_trust_survey():
    st.markdown("### 🙋 Quick check")
    with st.form("trust_survey_form"):
        trust_score = st.slider(
            "How much do you trust this recommendation?",
            min_value=1, max_value=5, value=3,
            help="1 = not at all, 5 = completely",
        )
        net_value = st.radio(
            "Did this save you research time you'd otherwise spend on forums/Google?",
            ["Yes", "No"],
            horizontal=True,
        )
        survey_submitted = st.form_submit_button("Submit feedback")

    if survey_submitted:
        log_event("survey_submitted", trust_score=trust_score, net_value=net_value)
        st.success("Thanks — this helps us validate the project.")
```

**3. Wire it into `app/intake.py`**, right after `render_blueprint(result)`:

```python
from app.survey_modal import render_trust_survey
...
        render_blueprint(result)
        render_trust_survey()
```

### How to verify this card is done
- After generating a blueprint, the trust-survey form appears immediately below it.
- Submitting it appends a `survey_submitted` event (with `trust_score` and `net_value`) to `data/telemetry.log`.
- Closing the browser tab *before* submitting the survey does **not** crash anything — this is an accepted, non-blocking gap per the task's own risk note ("missed submissions if a user closes the tab early — acceptable, not a blocker metric").

### Computing your headline metrics after testing
Once you've run real sessions (Week 3, Day 20 in the action plan), pull the numbers:

```bash
python3 -c "
import json
scores = []
for line in open('data/telemetry.log'):
    e = json.loads(line)
    if e['event'] == 'survey_submitted':
        scores.append(e['trust_score'])
scores.sort()
if scores:
    median = scores[len(scores)//2]
    print(f'{len(scores)} responses. Trust scores: {scores}. Median: {median}')
"
```

---

## Epic 3 — Done Checklist
- [ ] The 3-block layout renders real data from the full pipeline, with evidence bars and clickable source links.
- [ ] A copy-able plain-text export of the full blueprint is visible below the blocks.
- [ ] Every form-start and results-shown event is appended to `data/telemetry.log` with a timestamp.
- [ ] The trust survey appears after every blueprint and logs `trust_score` + `net_value`.
- [ ] You can compute average time-to-results and median trust score directly from the log file, with no external analytics tool.

**At this point, all 14 build cards are complete and wired together end-to-end** — form → validated inputs → retrieval → privacy filter → ranking → cost → LLM summary → 3-block display → export → telemetry → trust survey. This is the point in the 4-week action plan where Week 3's "wire full pipeline; polish 3-block output; telemetry" milestone is done, and you're ready for real user testing.
