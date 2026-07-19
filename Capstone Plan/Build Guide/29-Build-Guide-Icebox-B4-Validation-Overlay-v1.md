# Build Guide 29 — Icebox B.4: Mainstream Validation Overlay (Stack Overflow survey benchmarks)

*Icebox card `stackpunk #41` · Priority: **Could Have** · Estimated effort: **~2.5–3 days** · Rank: **6 of 7***

*Roadmap NEXT item. The data asset already exists — Gabi's `technology_landscape.csv` (2,017 rows: top-5 tools per Industry × OrgSize group, built from the real 2025 Stack Overflow Developer Survey via `scripts/extract_tech_landscape.py` on the `Gabi` branch — see `19-Gabi-Branch-Integration-Analysis-v1.md`). What does NOT exist yet is the taxonomy mapping between the survey's categories and ours. That mapping layer is most of the effort, and it's why this ranks 6 of 7 despite the data being "done".*

---

## What it does

Adds population-level context under Block A: *"34% of similarly-sized Technology companies report using Azure"* — explicitly labelled as **survey population data, not case-specific evidence**, because the case library has no org-size join key. It answers the trust question "is this recommendation weird, or mainstream?"

## Where the changes go

| File | Change |
|---|---|
| `data/technology_landscape.csv` | Pull from Gabi branch: `git checkout Gabi -- data/technology_landscape.csv` — **it is not on Ash2 today** (verified 2026-07) |
| `data/so_taxonomy_mapping.json` | **New** — hand-built mapping, survey categories → our categories (same pattern as `data/domain_mapping.json`, including a `_meta` block documenting judgment calls) |
| `app/logic/overlay.py` | **New** — load CSV + mapping, `get_benchmark(industry, org_size, tool_ids)` |
| `app/pipeline.py` | Call it, add `benchmarks` key to the returned dict |
| `app/dashboard.py` | Render one caption line per tool in Block A when a benchmark exists |
| `PM & Ethics/Intake-Output-Schema-v1.md` | New optional `benchmarks` output key |

## Step 1 — the mapping layer (the real work)

Three mismatches to resolve, each documented in `so_taxonomy_mapping.json`'s `_meta` like `domain_mapping.json` does:

1. **Industry**: the survey's industry list ≠ our 25 dropdown values. Map survey→ours; many-to-one is fine; anything unmappable maps to `null` and is skipped (fail closed — show no benchmark rather than a wrong one).
2. **OrgSize**: the survey's employee bands ≠ our `solo/startup/smb/mid/ent` keys. `scripts/map_stackoverflow_orgsize.py` already exists on this branch — reuse/extend it rather than writing a second mapper.
3. **Tool names**: survey technology names ≠ our 41 canonical ids. Reuse the alias-map approach from Card 2.1 — a small `SO_TOOL_ALIASES` dict inside the mapping JSON. Expect low overlap (the survey asks about languages/frameworks/clouds, our library is enterprise AI products); **measure the overlap first** (Step 2) before writing any UI.

## Step 2 — feasibility gate (half a day, do before committing to the rest)

Write a throwaway script: load `technology_landscape.csv`, apply the tool alias draft, and print what fraction of our 41 canonical tools ever appear in the survey's top-5 lists. **If fewer than ~8 tools overlap, stop and report back** — the overlay would render for almost no queries and the card should go back to the icebox with that finding written on it. This gate is the cheap version of discovering the problem after 3 days.

## Step 3 — overlay.py

```python
"""
Icebox B.4 — population-level Stack Overflow benchmark overlay.
POPULATION data, not case evidence: the survey tells us what similarly-sized
companies in an industry report using — it says nothing about our matched cases.
Every rendered line must carry that label.
"""
import json, csv
from functools import lru_cache

@lru_cache(maxsize=1)
def _load():
    ...  # read CSV + mapping JSON once; return dict[(industry_key, org_key)] -> {tool_id: pct}

def get_benchmark(industry: str, org_size_key: str, tool_ids: list[str]) -> dict[str, float]:
    """Returns {tool_id: pct_reporting_use} for whichever of tool_ids have
    survey coverage for this (industry, org_size) group. Empty dict = no data
    (unmapped industry, no group row, or no tool overlap) — caller renders nothing."""
```

## Step 4 — pipeline + dashboard

- pipeline.py: `benchmarks = get_benchmark(inputs["industry"], inputs["org_size"], ranked_tools)`, add to return dict.
- dashboard.py, inside `_render_stack_block`'s per-tool loop:

```python
    pct = benchmarks.get(tool_id)
    if pct is not None:
        st.caption(f"📊 {pct:.0f}% of similarly-sized {industry} companies report "
                   f"using this (Stack Overflow 2025 survey — population data, "
                   f"not from our matched cases)")
```

The long label is deliberate; shortening it to "34% use this" would misrepresent survey data as case evidence — exactly the conflation the roadmap warned about.

## Gotchas

- **Fail closed everywhere**: unmapped industry → no line; missing group → no line. Never interpolate across groups.
- `technology_landscape.csv` derives from developer-survey respondents — a Healthcare *company's* stack ≠ Healthcare *developers'* stack. The label copy covers this, but don't oversell it in the demo either.
- Keep the CSV load behind `lru_cache` — intake reruns on every widget interaction.
- License/attribution: the SO survey is ODbL — add attribution to the methodology block while you're in there.

## Verification checklist

- [ ] Step 2 gate passed and the overlap number is written into this doc.
- [ ] Query with a mapped industry → captions render with the full population-data label.
- [ ] Query with an unmappable industry (e.g. "Any industry") → no captions, no error.
- [ ] Numbers spot-checked against the raw CSV for one (industry, size) group.
- [ ] Schema doc updated; methodology block gains the survey attribution; card #41 moved once live-tested.
