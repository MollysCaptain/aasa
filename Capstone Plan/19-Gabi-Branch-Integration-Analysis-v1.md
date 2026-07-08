# stackpunk/Gabi Branch — Analysis & Integration Plan

*Analysis of https://github.com/MollysCaptain/stackpunk/tree/Gabi against the reconciled ATSA planning set (Handbook v2, kanban board, build guides 12–18). Written after reading every file on the branch — not a guess from the repo name.*

---

## What's actually on the branch

| File | What it is |
|---|---|
| `PLANNING.md` | A live progress log — this is the most current, most trustworthy file on the branch. Shows real completed work: data audit, schema correction, domain normalisation, chunking, tech-landscape extraction. |
| `MVP-Scoping.md` | An **older** MVP scoping doc — still describes Flowise, a 3-person team, and a 15–20 tool pricing matrix. This predates (and conflicts with) your Handbook v2. |
| `data/ChatGPT_plan.md` | A brainstorm/plan (apparently ChatGPT-assisted) describing a *rules-based scoring engine* + architecture templates + Stack Overflow survey, as a third possible design direction. |
| `data/schema.md` | The **upstream** (unmodified) schema doc from the source `ai-use-cases-library` repo. |
| `data/stackpunk-schema.md` | Your colleague's own, **verified-against-real-data** schema doc — corrects several things the upstream doc gets wrong. This is the most reliable column reference either of you has. |
| `data/use-cases.csv` | The real 3,023-row case dataset (matches the "3,023 real AI deployments" your Handbook already cites — same dataset, now actually in hand). |
| `data/domain_mapping.json` + `scripts/normalize_domains.py` | Normalises the raw `Use Case Domain` column (59 raw values) to 18 canonical domains, adding a `Use Case Domain (Canonical)` column to the CSV. All 3,023 rows resolved. |
| `data/technology_landscape.csv` + `scripts/extract_tech_landscape.py` | Processes the real **2025 Stack Overflow Developer Survey** into top-5-tool-per-Industry-x-OrgSize rankings (2,017 rows, 135 groups) — AI models, databases, and platforms. |
| `data/templates.json` | 10 hardcoded "architecture templates" (Standard RAG, Predictive Maintenance, Agentic Workflow, Customer Support Bot, etc.), each with a named component list. |
| `data/use_cases_chunks.jsonl` | 9,069 chunks — **3 chunks per case** (Implementation / Outcome / Domain), not 1, via `scripts/chunk_use_cases.py`. |
| `scripts/validate_use_cases.py` | A schema + CaseID-policy validator (format, uniqueness) with hard-fail/warning distinctions — genuinely useful, and something your own plan doesn't currently have. |

---

## The good news: real, ready-to-reuse overlap

Your Epic 2 build guide (`13-Build-Guide-Epic2-Retrieval-v1.md`) was written with **placeholder column names**, because neither of us had the actual CSV yet — it explicitly told you to print the real columns and adjust. Your colleague already did that work, for real, and it's more thorough than a placeholder-swap:

- **Real column names, confirmed**: `CaseID, Organization, Use Case Title, Description, Org Industry, Use Case Industry, Subindustry Tags, Use Case Domain, Tools/Technologies, Outcomes & Benefits, Source URL, Source`. Card 2.1's `TOOL_COLUMN = "Tool/Technology"` placeholder should become `"Tools/Technologies"`, and — important — it's **semicolon-delimited (`" ; "`)**, not comma-delimited as you might otherwise have guessed. `Outcomes & Benefits` is bullet-pointed prose (`•`-prefixed lines), not a clean tag list — matters for Card 2.2's `build_document_text`.
- **Card 1.2's dropdown problem is already solved.** The Epic 1 guide had you stub `INDUSTRIES_PLACEHOLDER`/`WORKFLOWS_PLACEHOLDER` with a note to "derive dynamically later." Your colleague already built exactly that: `domain_mapping.json` maps all 59 raw domain strings to 18 canonical domains, applied to all 3,023 rows via `normalize_domains.py`. Use `Use Case Domain (Canonical)` for the Workflow dropdown and `Use Case Industry` for Industry — no placeholder needed.
- **`validate_use_cases.py` is a free upgrade.** It checks CaseID format/uniqueness (hard fail) and flags domain values with no mapping entry (warning) — worth running as a gate *before* Card 2.1's tool-alias step, so a malformed dataset doesn't silently produce a bad alias map.
- **The dataset is confirmed real and matches what the Handbook cites** — same 3,023 rows, same "Consultancy Gap" framing, same source repo family (`../ai-use-cases-library/`, with its own `CASEID_POLICY.md` and `docs/taxonomy.md`).

---

## Real conflicts — these need a joint decision, not a silent merge

This is the same scope-drift problem your Handbook v2 already solved once *within* your own document set (§0's change log). It's now happening *across* the two of you, which is normal for a 2-person team working in parallel — but it needs the same explicit reconciliation, not an assumption that one side's version quietly wins.

**1. Two different MVP scoping documents exist, and they contradict each other.** Gabi's `MVP-Scoping.md` still specifies Flowise, a 3-person team (Person A/B/C), and a 15–20 tool pricing matrix — all three of which your Handbook v2 explicitly dropped (§0, rows 1, 7). If this doc and your Handbook both get submitted as-is, the submission contradicts itself exactly the way the original v1 draft did. **Someone needs to tell your colleague the Handbook v2 is the current plan of record — or the two of you need to jointly decide otherwise** — before more code gets built on either assumption.

**2. Two different recommendation mechanisms are implied.** Your build guides implement retrieval (Chroma vector search) + deterministic frequency ranking. `ChatGPT_plan.md` sketches a manual points-based **scoring engine** instead (e.g., "Manufacturing +5 Predictive Maintenance," "Many PDFs +10 RAG") paired with the 10 static `templates.json` architectures. No scoring script exists yet on the branch — this is still a design intention, not committed code — which makes now the right moment to pick one mechanism, not build both in parallel and reconcile later.

**3. A real third data source has been added: the Stack Overflow 2025 Developer Survey.** This is genuinely valuable — it's exactly the **"NEXT (Month 2): Mainstream Validation Overlay"** item in `07-Roadmap-v2.md`, already built ahead of schedule. But it also doesn't join cleanly to anything you already have: `technology_landscape.csv`'s `Industry` values (e.g. `"Banking/Financial Services"`) and `OrgSize` bands (e.g. `"1,000 to 4,999 employees"`) don't match either the case library's industry taxonomy or your app's own 5-band org-size taxonomy (`solo/startup/smb/mid/ent`). Using it means building a second mapping layer — the same "no free join key" caution your Handbook already raised once, now applying to a new pairing.

**4. A bigger output shape is implied.** `ChatGPT_plan.md`'s UI is 5 pages (questionnaire → recommended use cases → architecture diagram → roadmap → technology landscape) versus your reconciled 3-block blueprint. That's a materially larger build than the ~9.5-day effort budget your Handbook and kanban board are built around.

---

## Concrete integration plan — assuming the Handbook v2 stays the plan of record

*(State this assumption to your colleague explicitly rather than treating it as settled — see "Recommended next step" below.)*

| Kanban card | What changes |
|---|---|
| **2.1** — normalise tool names | Real column is `Tools/Technologies`, split on `"; "` (not comma). Run `validate_use_cases.py` first as a data-quality gate. |
| **1.2** — dropdown options | Retire the placeholder/derive-later split in the Epic 1 guide. Use `Use Case Domain (Canonical)` (18 values, already mapped) for Workflow, and `Use Case Industry` for Industry — both ready today. |
| **2.2** — embed cases into Chroma | Joint decision needed: keep the Epic 2 guide's 1-chunk-per-case approach, or adopt Gabi's 3-chunks-per-case (`use_cases_chunks.jsonl`, 9,069 chunks — implementation/outcome/domain views). If adopting the latter, `embed_cases.py` ingests that file directly instead of building `build_document_text` from scratch. |
| **2.4/2.5/2.6** — cost, filter, prompt | No overlap on the Gabi branch yet — these build guides apply unchanged once 2.1 is pointed at the real column. |
| *(new, Icebox)* — Mainstream Validation Overlay | `technology_landscape.csv` is real and valuable, but it's a Month-2 roadmap item per `07-Roadmap-v2.md`, not MVP scope — recommend one Icebox card referencing it rather than pulling it into the 4-week sprint without a scope conversation. |
| *(not yet integrated)* — `templates.json` | Belongs to the scoring-engine design direction, not the retrieval+ranking one already built. Don't wire it in without Conflict #2 above being resolved first — flag it as a Future-phase idea for now. |

---

## Recommended next step

Before either of you builds further on top of this, run a short joint session — structurally the same move as Card P.1/P.3 (charter + schema sign-off), just applied across both branches this time:

1. **Agree which scoping doc is current** — Handbook v2, or a merged version that also captures the Stack Overflow survey work.
2. **Agree the recommendation mechanism** — retrieval+ranking (already built), the scoring engine (sketched, not built), or a hybrid.
3. **Agree whether the Stack Overflow tech-landscape data ships in the MVP or moves to the roadmap.**

Catching this now, with two branches that have diverged for maybe a few days, is a lot cheaper than catching it in Week 3 with two much larger, incompatible codebases — which is the exact lesson your own Handbook v2 change log already paid for once.
