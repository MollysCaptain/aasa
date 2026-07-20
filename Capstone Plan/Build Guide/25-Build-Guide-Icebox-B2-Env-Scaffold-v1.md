# Build Guide 25 — Icebox B.2: One-click code boilerplate generator (.env scaffold)

*Icebox card `stackpunk #39` · Priority: **Could Have** · Estimated effort: **~1 day** · Rank: **2 of 7***

*This is the Lovable prototype's "Copy .env scaffold" button. Pure string templating from data we already have — no network calls, no new dependencies.*

---

## ⚡ Implementation status — IMPLEMENTED (Lovable-parity UI round), live test pending

Shipped on `Ash2` together with the Lovable-parity UI changes, with **one deviation
from the spec below**: the scaffold does not live in an expander below the Export
block. It lives in a **`st.popover("⚙️ .env scaffold")` inside the new action-button
row** (`_render_action_row()` in `app/dashboard.py`, rendered right after the Export
code block, next to the board-one-pager download and the Clear button) — matching
the Lovable prototype's button-row layout, which didn't exist yet when this guide
was written. Everything else landed as specced: `app/logic/scaffold.py` is verbatim
Step 1, the popover contains the caption + `st.code` + `st.download_button` from
Step 2, and the optional `log_event("scaffold_downloaded")` telemetry is wired.

Unit-verified (sandbox): known tools get their snippets, unknown tools hit the
model-typed fallback, no KeyError. **Still open — the live checklist below** (the
sandbox can't run Streamlit): mixed-stack render, download, copy icon, then move
card #39.

---

## What it does

Given the recommended stack, generate a copy-pasteable starter scaffold: a `.env` block with the right API-key variable names for token-billed tools, install/setup one-liners for OSS tools, and honest comment lines for seat-billed SaaS ("this is a subscription, not an API — nothing to configure here"). Rendered in an expander below the Export block, with copy (`st.code`) and download (`st.download_button`).

## Where the changes go

| File | Change |
|---|---|
| `app/logic/scaffold.py` | **New file** — snippet map + `build_scaffold()` |
| `app/dashboard.py` | New `_render_scaffold_block()` called from `render_blueprint()` after the Export section |

No pipeline/filter/cost changes. The function takes `result["recommended_stack"]` as-is.

## Steps

### 1. New `app/logic/scaffold.py`

```python
"""
Icebox B.2 — starter-config scaffold for the recommended stack.
Templated text only: we never claim these are complete setup docs,
just the correct env-var names and first commands.
"""
from app.logic.pricing import PRICING

# Hand-written snippets for tools where a scaffold is meaningful.
# Keyed by canonical tool id. Anything not listed falls through to
# a comment line built from its PRICING "model" type.
SNIPPETS = {
    "openai-api":   'OPENAI_API_KEY=""            # https://platform.openai.com/api-keys',
    "azure-openai": 'AZURE_OPENAI_API_KEY=""\nAZURE_OPENAI_ENDPOINT=""   # from your Azure resource',
    "claude-api":   'ANTHROPIC_API_KEY=""          # https://console.anthropic.com',
    "gemini-api":   'GOOGLE_API_KEY=""             # https://aistudio.google.com/apikey',
    "aws-bedrock":  'AWS_ACCESS_KEY_ID=""\nAWS_SECRET_ACCESS_KEY=""\nAWS_REGION="eu-central-1"',
    "vertex-ai":    'GOOGLE_APPLICATION_CREDENTIALS="service-account.json"\nGCP_PROJECT_ID=""',
    "ibm-watsonx":  'WATSONX_API_KEY=""\nWATSONX_PROJECT_ID=""',
    "cohere":       'COHERE_API_KEY=""',
    "huggingface":  'HF_TOKEN=""                   # https://huggingface.co/settings/tokens',
    "langchain":    "# pip install langchain      — framework, no key of its own",
    "chroma":       "# pip install chromadb       — local vector store, no key needed",
    "llama":        "# Self-hosted open-weight model — see https://llama.com for downloads",
    "tensorflow":   "# pip install tensorflow",
    "pytorch":      "# pip install torch",
}

_FALLBACK_BY_MODEL = {
    "token":   "# {label}: token-billed API — check the vendor console for your key variable",
    "seat":    "# {label}: per-seat SaaS subscription — configured in the vendor admin panel, not in code",
    "compute": "# {label}: compute-billed platform — provisioned in the cloud console, not via .env",
    "free":    "# {label}: free / self-hosted — see vendor docs for install",
}


def build_scaffold(recommended_stack: list[str]) -> str:
    lines = [
        "# --- AASA starter scaffold (illustrative, verify against vendor docs) ---",
        "# Generated from your recommended stack. Keys left blank on purpose.",
        "",
    ]
    for tool_id in recommended_stack:
        entry = PRICING.get(tool_id, {})
        label = entry.get("label", tool_id)
        lines.append(f"# {label}")
        snippet = SNIPPETS.get(tool_id)
        if snippet is None:
            template = _FALLBACK_BY_MODEL.get(entry.get("model"), "# {label}: see vendor docs")
            snippet = template.format(label=label)
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines)
```

### 2. dashboard.py — render block

Add import `from app.logic.scaffold import build_scaffold`, then in `render_blueprint()` directly after the Export `st.code(...)` / `render_copy_confirmation()` lines:

```python
    with st.expander("⚙️ Starter .env scaffold"):
        scaffold_text = build_scaffold(result["recommended_stack"])
        st.caption("Copy-paste starting point — variable names only, keys left blank.")
        st.code(scaffold_text, language="bash")
        st.download_button(
            "Download .env scaffold", scaffold_text,
            file_name="aasa-scaffold.env", mime="text/plain",
        )
```

Optional: `log_event("scaffold_downloaded")` wired to the download button's return value, matching Card 3.3's telemetry pattern.

## Gotchas

- **Never invent key names you're not sure of.** Everything in `SNIPPETS` above should be double-checked against the vendor's docs during implementation; anything uncertain belongs in the fallback comment form instead. A wrong-but-plausible env var name is worse than an honest "check the console".
- Keep it inside an expander — the blueprint page is already long, and this is developer-facing content in a stakeholder-facing flow.
- `st.download_button` inside `render_blueprint()` is safe with the existing session-state pattern (results render on every rerun), but do NOT put it inside the intake `st.form` — Streamlit forbids download buttons in forms.

## Verification checklist

- [ ] Run a query whose stack mixes token + seat + free tools → each gets the right snippet type. *(live test — Ash)*
- [x] A tool with no `SNIPPETS` entry falls back to the model-typed comment, never a KeyError. *(unit-tested in sandbox)*
- [ ] Download produces a well-formed text file; copy icon works on the code block. *(live test — Ash)*
- [x] `py_compile` on both files. *(app boot still needs the live run)*
- [x] Update `PM & Ethics/Intake-Output-Schema-v1.md` only if you add anything to the pipeline output — nothing scaffold-specific was added (the `query` key documented there came from the UI round, not this card).
- [ ] Move card #39 on the board once live-tested.
