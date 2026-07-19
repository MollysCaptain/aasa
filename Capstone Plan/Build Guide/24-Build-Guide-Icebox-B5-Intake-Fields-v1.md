# Build Guide 24 — Icebox B.5: Optional "Project name" + "Vendors to exclude" intake fields

*Icebox card `stackpunk #44` · Priority: **Could Have** · Estimated effort: **~0.5 day** · Rank: **1 of 7 (easiest)***

*Post-midterm sprint: tutors asked what Icebox features can land in the final 2 weeks. This is the cheapest — two optional widgets, one filter line, one export echo. No new data, no new dependencies.*

---

## What it does

1. **Project name** (optional free text): purely cosmetic — echoed in the blueprint title and export header so a saved/shared blueprint says whose it is. Pairs with B.6 (saved blueprints need names).
2. **Vendors to exclude** (optional multiselect): user picks tools they refuse to use (existing contract, past bad experience, procurement rule). Excluded tools are stripped before ranking, the same way the privacy filter strips non-governable tools.

## Where the changes go

| File | Change |
|---|---|
| `app/intake.py` | Two new optional widgets inside the existing `st.form("intake_form")`, two new keys in the `run_pipeline({...})` inputs dict |
| `app/validators.py` | **No change** — both fields are optional; do NOT add validation that blocks empty values |
| `app/pipeline.py` | Thread `inputs.get("exclude_tools", [])` into the filter step |
| `app/logic/filter.py` | New `apply_vendor_exclusions()` function (mirror of `apply_privacy_filter`) |
| `app/export.py` | Prepend project name to the header line when present |
| `app/dashboard.py` | Show project name in the `## 🧩 Your AI Stack Blueprint` heading when present |

## Steps

### 1. intake.py — widgets (inside the form, after the budget field, before the submit button)

```python
    with st.expander("Optional: project details"):
        project_name = st.text_input(
            "Project name",
            max_chars=60,
            help="Shown on your blueprint and export — useful if you save or share it.",
        )
        exclude_tools = st.multiselect(
            "Vendors to exclude",
            options=sorted(PRICING.keys(), key=lambda k: PRICING[k]["label"]),
            format_func=lambda k: PRICING[k]["label"],
            help="Tools you can't or won't use. They'll be removed before ranking.",
        )
```

Add `from app.logic.pricing import PRICING` to intake.py's imports. Then add both to the pipeline call:

```python
            result = run_pipeline({
                "workflow": workflow, "industry": industry,
                "org_size": org_size_key, "privacy": privacy_key,
                "budget": budget,
                "project_name": project_name.strip(),
                "exclude_tools": exclude_tools,
            })
```

### 2. filter.py — exclusion function (below `apply_privacy_filter`)

```python
def apply_vendor_exclusions(matched_cases: list[dict], exclude_tools: list[str]) -> list[dict]:
    """B.5 — strip user-excluded tools from each case's canonical_tools,
    exactly like the privacy filter does. Cases stay in the list (they're
    still evidence); only the excluded tool ids stop being rankable."""
    if not exclude_tools:
        return matched_cases
    excluded = set(exclude_tools)
    return [
        {**case, "canonical_tools": [t for t in case["canonical_tools"] if t not in excluded]}
        for case in matched_cases
    ]
```

### 3. pipeline.py — call it right after the privacy filter (line ~66)

```python
    filtered_cases = apply_privacy_filter(matched_cases, inputs["privacy"])
    filtered_cases = apply_vendor_exclusions(filtered_cases, inputs.get("exclude_tools", []))
```

Also pass `project_name` through into the returned dict so dashboard/export can read it:
`"project_name": inputs.get("project_name", "")` in the return block.

### 4. export.py + dashboard.py — echo the name

- export.py header: `title = f"=== AASA Blueprint — {result['project_name']} ===" if result.get("project_name") else "=== AI-Assisted Stack Architect — Blueprint ==="`
- dashboard.py: `st.markdown(f"## 🧩 {result.get('project_name') or 'Your AI Stack Blueprint'}")`
- **Free win (post-Lovable-parity round):** `blueprint_to_markdown()` in export.py
  (guide 26, already implemented) already reads `result.get("project_name")` for its
  title — so the board one-pager picks the name up automatically once you add it to
  the pipeline return dict. Nothing extra to do there.
- **Note:** the pipeline return dict now also carries a display-only `"query"` echo
  (added in the Lovable-parity round — see the schema doc). Keep `project_name` as
  its own top-level key as specced here, NOT inside `query` — `query` is strictly
  the 5 validated pipeline inputs.

## Ordering & gotchas

- Run exclusions **after** the privacy filter, not before — the privacy filter is a hard compliance rule and must always see the full case list; exclusions are a user preference layered on top.
- Empty exclusion list must be a no-op (the early return above).
- Don't let the user exclude everything: if `rank_tools_by_frequency` comes back empty after exclusions, dashboard's Block A already handles an empty stack — verify it shows something sensible rather than crashing (add an `st.info` if not).
- Excluded tools should NOT disappear from Block C's case cards' "Stack used" lines context — those lines only show overlap with the (now exclusion-aware) recommended stack, so this works automatically.

## Verification checklist

- [ ] Submit with both fields empty → identical behaviour to today (regression check).
- [ ] Exclude the current #1 tool → it vanishes from Block A, ranking re-orders, evidence bars still based on total matched cases.
- [ ] Exclude a tool + Regulated posture together → both filters apply.
- [ ] Project name appears in dashboard heading and first line of the copy-export text.
- [ ] `python -m py_compile` on all touched files.
- [ ] Update `PM & Ethics/Intake-Output-Schema-v1.md` — two new optional input keys, one new output key.
- [ ] Move card #44 on the kanban board once live-tested.
