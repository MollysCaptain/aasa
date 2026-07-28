# Capstone Project Pitch (v2)
### Project: AI-Assisted Stack Architect (AASA)
*Supersedes the original Pitch. Scope corrected from "general tech stack" to AI-specific, per lecturer feedback and verification of the source dataset.*

## Problem Statement
- When adopting AI, organisations face a paralysing array of model, API, and framework choices. Picking the wrong one leads to wasted budget, compliance exposure, and painful migrations later.
- Companies currently rely on expensive consultants or subjective forum advice.
- There is no lightweight, evidence-backed system that maps a company's constraints to AI tools that comparable real organisations have actually deployed successfully.

**Scope correction from v1:** our original pitch described a general software/cloud/database architect. We are narrowing to an **AI-Assisted Stack Architect** — models, APIs, model platforms, and agent frameworks only — because that is what our knowledge base actually contains, and because a 4-week, 2-person team cannot responsibly cover general infrastructure too.

## Users
- **Startup founders & product leads** who need an AI adoption shortlist without a consultant's budget.
- **Non-technical CEOs** who need a plain-English, cost-aware "what should we use" answer to bring to investors.
- **Technical leads / PMs** who want to sanity-check an AI tool choice against real-world precedent before committing engineering time.

## AI Method
- **Retrieval-Augmented Generation (RAG):** a vector store of real, sourced AI deployments is retrieved by workflow/industry; an LLM only ever writes the summary prose, never invents the tools or prices.
- **Deterministic filtering before generation:** a hard Python filter applies compliance/privacy posture *before* anything is ranked, so the LLM cannot override it.
- **Frequency-ranked recommendation:** tools are ranked by how often comparable real organisations used them, not by vendor bias — this is measurable and auditable.

## Data (corrected — this is the most important change from v1)
We inspected the source repository directly rather than assuming its shape:
- **`abbasmahdi-ai/ai-use-cases-library`** is one clean CSV of **3,023 fully-populated rows** (not "3,000+ raw markdown files" as we first assumed). Every case has a description, outcome, industry, tool list, and source URL.
- The real data-engineering effort is **tool-name normalisation**: the raw data contains 2,511 distinct tool strings for 3,023 rows (e.g. "Gemini", "Gemini in Docs", "Gemini for Google Workspace" all mean one thing). We built a 41-tool canonical alias map.
- **We add a small, hand-built pricing table ourselves** (41 tools), since the repo has no pricing data. It distinguishes **per-token APIs** (OpenAI, Anthropic, Gemini APIs) from **per-seat SaaS** (Microsoft 365 Copilot, ChatGPT Enterprise) — treating these the same, as our original pitch implicitly did, would produce nonsense cost estimates.
- **Optionally**, Stack Overflow Developer Survey data (`AIModelsHaveWorkedWith`, `OrgSize`, `Industry`) can add *population-level* usage-by-company-size context. There is no shared key to the case library, so this cannot filter individual cases — only inform general commentary ("X% of similarly-sized orgs report using Y").

## Why This
- Existing options are either static (blog posts, fixed decision trees) or biased (vendor documentation).
- Our system is differentiated by **traceability**: every recommendation links back to a real, sourced deployment and its reported outcome — not a black-box score.
- It turns a multi-day research loop into a ~2-minute, evidence-backed shortlist.

## Honest boundaries (new section, in response to feedback)
- Pricing is illustrative and manually curated, not a live feed.
- Compliance filtering is directional — a shortlist, not a certification.
- The dataset skews toward enterprise productivity AI (Gemini/Workspace, Copilot); our recommendations reflect that real adoption pattern rather than an idealised agent-framework landscape.
