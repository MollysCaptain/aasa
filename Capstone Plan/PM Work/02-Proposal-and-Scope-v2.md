# Capstone Project Proposal & Scope (v2)
### AI-Assisted Stack Architect (AASA)
*Supersedes the original Proposal & Scope. Fixes: (1) it listed 3 roles ("Student A/B/C") for a 2-person team, (2) it built the plan around Flowise, adding an integration/webhook risk we can remove entirely, (3) it assumed a data-cleaning task that the real dataset doesn't require.*

## Team structure — corrected to 2 roles for 2 people
1. **Student A — Data & Logic Architect:** tool-name normalisation, embeddings, deterministic filters, cost parser, prompt design.
2. **Student B — UI, Validation & PM Lead:** Streamlit interface, telemetry, user recruiting & testing, timeline/risk tracking, pitch deck.

Both share testing analysis and rehearsal. (v1 split this across three invented roles that don't map to a 2-person team — that inconsistency is now fixed everywhere, including the Ethical Action Plan.)

## Week 1: Guardrails & Data Foundation
1. **Draft the Project Charter** (Days 1–2): 1-page scope statement — AI stack only, no general infrastructure, no code generation, no compliance certification claims. Start recruiting 5–8 real test users now (moved up from Week 3 to avoid the scheduling collision identified in feedback).
2. **Define the Input/Output Schema** (Days 3–4): 5 inputs (Workflow, Industry, Org size, Privacy posture, Budget) → 3 output blocks (Stack, Cost, Case References).
3. **Normalise the case data** (Days 5–7): the source is one clean 3,023-row CSV — parsing is trivial. The actual work is building the tool-name alias map (2,511 raw variants → 41 canonical tools) and the accompanying pricing table (per-token vs per-seat vs compute-billed).

## Week 2: Logic System
1. **Map the pipeline** (Days 8–9): input → deterministic privacy filter → evidence-ranked retrieval → cost calculation → LLM summary. Diagrammed in Miro/Mermaid.
2. **Write the deterministic rule matrix** (Days 10–11): e.g. `IF privacy == 'regulated' THEN restrict to governable platforms`. This runs in plain Python before the LLM ever sees the request.
3. **Engineer the system prompt** (Days 12–14): few-shot prompt constrains the LLM to formatting/prose only — it does not select tools or compute prices.

## Week 3: Build the MVP and Test It
**Stack simplified from v1:** Streamlit UI → Python logic → local Chroma vector store → one LLM call for summary text. **Flowise is dropped** — for a filter→retrieve→prompt pipeline, plain Python is simpler to build and debug live, and removes the webhook/cross-origin risk the original Technical Work Breakdown flagged.
1. **Assemble the pipeline** (Days 15–17): embed the normalised case data into Chroma; wire the deterministic filter and ranking.
2. **Build the UI** (Days 18–19): 5-field form → 3-block output.
3. **Test with real users** (Days 20–21): 5–8 real testers (not the original N=50/N=12 targets, which weren't achievable by 2 people in this window). Log failures, patch prompts/rules immediately.

## Week 4: Package, Roadmap, Pitch
1. Document known limitations as roadmap items (illustrative pricing, directional compliance, dataset skew).
2. Define the KPI set we can actually measure as 2 people (see Effort-Informed Prioritisation v2 for the corrected metric list).
3. Build and rehearse a 10-slide pitch: Problem → Solution → Architecture → Real Test Results → Risk Management → Roadmap.

## Scope boundary (unchanged principle, now enforced consistently across all documents)
Grading rewards Project Management Rigor (30%) over Prototype Execution (20%). A well-scoped, honestly-documented, compliant system beats an impressive-looking one that overclaims or hallucinates. This version removes every place our own work had drifted from that principle.
