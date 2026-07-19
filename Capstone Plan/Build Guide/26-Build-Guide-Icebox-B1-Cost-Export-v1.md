# Build Guide 26 — Icebox B.1: Plain-language cost export (1-pager for boards)

*Icebox card `stackpunk #38` · Priority: **Could Have** · Estimated effort: **~1–1.5 days** · Rank: **3 of 7***

*Roadmap NEXT item ("Plain-Language Financial Export") and the Lovable prototype's "EXECUTIVE PDF" / "Pitch brief (.md)" buttons. Persona target: the Visionary Outsider — a non-technical CEO who needs board-ready cost clarity, not a token-price table.*

---

## ⚡ Implementation status — MARKDOWN VERSION IMPLEMENTED (Lovable-parity UI round), PDF stretch open

Shipped on `Ash2` together with the Lovable-parity UI changes:

- `blueprint_to_markdown()` landed in `app/export.py` as specced in Step 1, plus
  one extra guard the spec implied but didn't spell out: the budget lines only
  render when **both** `budget` *and* `within_budget` are non-None.
- **Deviation from Step 2**: the download button doesn't sit alone after the
  Export `st.code(...)` — it's the first button in the new action row
  (`_render_action_row()` in `app/dashboard.py`), labelled
  "📄 Board one-pager (.md)", alongside the .env-scaffold popover (guide 25) and
  a Clear button. `log_event("onepager_downloaded")` telemetry is wired.
- `project_name` falls back to "AI stack proposal" — B.5 (guide 24) isn't built
  yet, so every export currently uses the fallback title. Once B.5 lands, the
  name flows in with no change needed here.
- **Step 3 (PDF) not done** — still a stretch item; the Lovable "EXECUTIVE PDF"
  button therefore has no counterpart yet, only the .md.

Unit-verified (sandbox): within-budget ("to spare"), over-budget ("exceeds…⚠️"),
and no-fixed-total ("usage-based") variants all render correctly. **Still open —
the live checklist below**, especially the persona read-through, then move card #38.

---

## What it does

A downloadable one-pager, written in plain English, that a founder can forward to their board unedited: what we'd run, what it costs per month, whether it fits the stated budget, and what the caveats are. Markdown first (guaranteed, zero dependencies); PDF as a stretch step.

## Where the changes go

| File | Change |
|---|---|
| `app/export.py` | New `blueprint_to_markdown(result)` alongside the existing `blueprint_to_text` |
| `app/dashboard.py` | `st.download_button` for the .md next to the existing Export block |
| `requirements.txt` | Only if you do the PDF stretch (`fpdf2`) |

## Steps

### 1. export.py — `blueprint_to_markdown()`

Build it from the same `result` dict `blueprint_to_text` already consumes — every field below already exists (`cost_forecast` carries `total_monthly_eur`, `within_budget`, `budget_delta_eur`, `budget` since Update D):

```python
def blueprint_to_markdown(result: dict) -> str:
    """Icebox B.1 — board-ready plain-language one-pager. Deliberately
    non-technical: no tool ids, no token math, no jargon."""
    cost = result["cost_forecast"]
    name = result.get("project_name") or "AI stack proposal"
    lines = [f"# {name}", ""]

    lines.append("## What we recommend")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"{rank}. **{label}**")
    lines.append("")

    lines.append("## What it costs (illustrative)")
    total = cost.get("total_monthly_eur")
    if total is not None:
        lines.append(f"Estimated **€{total:,.0f} per month** across the core services.")
    if cost.get("budget") is not None:
        if cost.get("within_budget"):
            lines.append(f"This fits the stated budget of €{cost['budget']:,.0f}/mo "
                         f"with €{cost['budget_delta_eur']:,.0f}/mo to spare.")
        else:
            lines.append(f"⚠️ This exceeds the stated budget of €{cost['budget']:,.0f}/mo "
                         f"by €{abs(cost['budget_delta_eur']):,.0f}/mo — see caveats.")
    lines.append("")

    lines.append("## Why these tools")
    lines.append(f"Chosen from real, source-linked deployments by comparable "
                 f"organisations — {len(result['matched_cases'])} matched cases, "
                 f"top references below.")
    for case in result["matched_cases"][:3]:
        lines.append(f"- {case.get('organization', 'Unknown')} — {case.get('source_url', '')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(result.get("summary_text", ""))
    lines.append("")

    lines.append("## Caveats — read before committing budget")
    lines.append("- Prices come from a hand-curated table and are **illustrative**, "
                 "not quotes. Verify with vendors before signing anything.")
    lines.append("- Seat counts are assumptions from survey medians, capped for "
                 "single-workflow use — your real headcount will differ.")
    lines.append("- Compliance filtering is a directional shortlist, **not a certification**.")
    return "\n".join(lines)
```

Tone rules for whoever edits the copy later: no canonical tool ids, no "token/PPM" vocabulary, every number carries its caveat. The whole point of this artifact vs. the existing export is the audience.

### 2. dashboard.py — download button

In `render_blueprint()` immediately after the existing Export `st.code(...)`:

```python
    st.download_button(
        "📄 Download board one-pager (.md)",
        blueprint_to_markdown(result),
        file_name="aasa-cost-onepager.md",
        mime="text/markdown",
    )
```

(Import `blueprint_to_markdown` alongside the existing `blueprint_to_text` import.) Add `log_event("onepager_downloaded")` if wiring telemetry.

### 3. Stretch — PDF

Only if the markdown lands with time to spare: `pip install fpdf2`, then a ~30-line `markdown_to_pdf()` that renders the same lines with `FPDF.multi_cell` (skip proper md parsing — write headings/body directly from the same builder function refactored to return structured sections). Do **not** reach for heavier converters (pandoc/weasyprint) — deployment target is a plain `streamlit run`, keep the dependency footprint tiny.

## Gotchas

- `total_monthly_eur` can be `None` when neither a token-priced nor seat-priced tool is in the stack (all-compute/free stacks) — the `if total is not None` guard above matters; add a fallback sentence ("Costs for this stack are usage-based — no fixed monthly figure").
- `budget_delta_eur` is negative when over budget (Update D convention) — hence `abs()` in the over-budget line.
- Depends on B.5's `project_name` only optionally (`result.get(...)` with fallback) — safe to build in either order.

## Verification checklist

- [x] Over-budget query → ⚠️ line with correct delta; within-budget query → "to spare" line. *(unit-tested in sandbox with both variants)*
- [x] All-free/compute stack → no crash, fallback sentence renders. *(unit-tested via `total_monthly_eur=None`)*
- [ ] Open the downloaded .md in a renderer — headings, bold, bullets all valid. *(live test — Ash)*
- [ ] Read it once as the persona: would a non-technical CEO understand every sentence? *(judgment call — Ash)*
- [x] `py_compile` passed. — [ ] Move card #38 on the board once live-tested.
