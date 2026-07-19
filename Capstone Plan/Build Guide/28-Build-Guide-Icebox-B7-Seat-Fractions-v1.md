# Build Guide 28 — Icebox B.7: Workflow-scoped seat-fraction table (replaces Fixed Ceiling Stopgap)

*Icebox card `stackpunk #48` · Priority: **⚠️ WON'T HAVE (board label)** · Estimated effort: **~2 days, mostly research** · Rank: **5 of 7***

*This card was explicitly iceboxed as "Option A" during Update D (see `18-Build-Guide-Updates-Epic1-2-v1.md` and the Icebox card text): the €67,340/mo assistant-cost bug was stopgapped with `SEAT_CEILING = 25`, and the proper fix — scoping seats to the workflow instead of a flat cap — was deferred. Only pick this up if guides 24–27 are done and live-tested. The code change is small; the defensible-numbers research is the actual work.*

---

## The problem being fixed

`app/logic/cost.py` currently does (lines ~39–62):

```python
SEAT_CEILING = 25
...
org_seats = ASSUMED_SEATS.get(org_size_key, ASSUMED_SEATS["startup"])
seats = min(org_seats, SEAT_CEILING)
```

The flat 25-seat cap fixed the company-wide-seats absurdity, but it's wrong in both directions: an enterprise Customer Service deployment (`ent` = 2,377 assumed staff) surely licenses more than 25 seats, and a solo founder's Finance workflow licenses fewer. The honest model: **seats = the fraction of company headcount that actually works in the target workflow**, per workflow.

## Where the changes go

| File | Change |
|---|---|
| `app/logic/cost.py` | Replace `SEAT_CEILING` with `WORKFLOW_SEAT_FRACTION` dict + floor/cap logic; `_cost_for_tool()` and both public functions gain a `workflow` parameter |
| `app/pipeline.py` | Pass `inputs["workflow"]` into `estimate_cost()` / `estimate_all_tool_costs()` |
| `app/dashboard.py` | `_render_methodology_block()` — the "Known limitations" copy **hand-states the 25-seat ceiling**; must be rewritten or it becomes a lie |
| `PM & Ethics/Intake-Output-Schema-v1.md` | Note the changed seat assumption |
| `18-Build-Guide-Updates-Epic1-2-v1.md` | Add a status line: Option A implemented, stopgap retired |

## Step 1 — the research (do this FIRST, with Gabi)

Build an 18-row table (one per `WORKFLOWS` option in `app/data/options.py`, minus "Any workflow") of *what fraction of a company's headcount works in that function*. Anchor on public benchmarks where they exist (e.g. customer-support headcount ratios, IT-staff-per-employee ratios from industry surveys); where no benchmark exists, agree a judgment call and **write the rationale into the dict as a comment** — same convention as `GOVERNABLE_FOR_REGULATED`'s inline justifications in `filter.py`. Starting proposal to argue against, not to accept:

```python
WORKFLOW_SEAT_FRACTION = {
    "Customer Service": 0.12, "Sales": 0.10, "Marketing": 0.05,
    "Finance": 0.05, "HR": 0.03, "Legal & Compliance": 0.02,
    "IT & Platform": 0.06, "Security & Cyber": 0.02, "Data & Analytics": 0.04,
    "R&D & Engineering": 0.15, "Operations & Supply Chain": 0.10,
    "Procurement": 0.02, "Content & Creative": 0.04, "CX & Personalization": 0.04,
    "Process Automation & RPA": 0.03, "Risk & Compliance": 0.02,
    "Training & L&D": 0.02, "Facilities & EHS": 0.02,
    "Any workflow": 0.25,   # no scoping signal — use a broad-adoption fraction
}
SEAT_FLOOR = 3      # below this a seat license discussion is meaningless
SEAT_CAP_FRACTION_SOURCE = "team judgment + public headcount-ratio benchmarks, 2026-07"
```

## Step 2 — cost.py logic

```python
def _cost_for_tool(canonical_id: str, org_size_key: str, workflow: str) -> dict:
    ...
    org_seats = ASSUMED_SEATS.get(org_size_key, ASSUMED_SEATS["startup"])
    fraction = WORKFLOW_SEAT_FRACTION.get(workflow, 0.25)
    seats = max(SEAT_FLOOR, round(org_seats * fraction))
```

Update the returned `disclaimer` string — it currently mentions the fixed ceiling; it should now say seats are scoped to the workflow's share of headcount and remain illustrative. Thread `workflow` through `estimate_cost(...)` and `estimate_all_tool_costs(...)` signatures and their `pipeline.py` call sites (`inputs["workflow"]`).

## Step 3 — re-verify the Update D scenario

The regression test that motivated all of this: **Customer Service / mid / regulated / €1,800 budget**. Under the new table: `481 × 0.12 ≈ 58 seats` — the M365-Copilot-style assistant becomes ~€1,740/mo instead of the ceiling's €750/mo (25 × €30). Still sane, still honest — but numbers move visibly vs. today, so:

- Re-run the exact Update D unit check and record the new figures in this doc.
- Check `prompt.py`'s few-shot examples — if either hardcodes a seat-derived € figure, it's now stale.
- Screenshot before/after for the tutors — this is a good "we replaced a stopgap with a model" story.

## Gotchas

- `estimate_all_tool_costs` (Update E) must use the same seat logic or Block A's per-tool prices will contradict Block B.
- `"Any workflow"` must stay a valid key — users can select it.
- Do NOT delete the `SEAT_CEILING` constant's explanatory comment block wholesale — move the history into this doc or an inline "was: fixed ceiling, see guide 28" note. The €67,340 story is project lore worth keeping findable.

## Verification checklist

- [ ] Update D scenario re-run; new totals recorded here and sane.
- [ ] `ent` + Customer Service no longer caps at 25 seats; `solo` + anything floors at 3.
- [ ] Methodology block copy updated (dashboard.py) — no "25-seat" text remains anywhere (`grep -rn "25" app/dashboard.py`).
- [ ] Schema doc + guide 18 status updated; kanban card #48 moved (or annotated "implemented despite Won't Have — tutor-sprint scope change" if the label stays).
- [ ] Gabi sign-off on the fraction table specifically — same convention as the Update D seat-multiplier confirmation.
