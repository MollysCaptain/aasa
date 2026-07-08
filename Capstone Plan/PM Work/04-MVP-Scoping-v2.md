# MVP Scoping (v2)
### AI Stack Architect (ATSA)
*Supersedes the original MVP Scoping. Fixes: replaces Flowise with a simpler Python pipeline; corrects the dataset description; makes the cost model seat/token-aware; consolidates learning goals to 2 people.*

## 1. MVP Goal
Build a functional AI Stack Advisor that retrieves comparable real-world AI deployments from a curated 3,023-case knowledge base and returns data-backed model/API/framework recommendations with an illustrative cost forecast. User-focused goal: bridge the "Consultancy Gap" for resource-constrained founders and product leads. Learning focus: structuring a normalisation + retrieval pipeline and a seat/token-aware pricing schema.

## 2. Core Hypothesis
"Founders and product leads will trust an automated AI-stack recommendation if it is grounded in traceable real-world deployments and paired with an honest, plain-language cost estimate."

## 3. MVP Core Components (Must-Haves)
- **Guided AI Intake:** a clean 5-field form — Target AI Workflow, Industry, Organisation Size, Data-Privacy Posture, Monthly Budget.
- **Retrieval & Matching Logic:** a Python pipeline (no Flowise) that normalises tool names, applies a deterministic privacy filter, retrieves comparable cases from a local Chroma vector store, and ranks tools by real-world frequency.
- **3-Block Blueprint:**
  1. Recommended AI stack (ranked, evidence-labelled, seat/token/compute tagged).
  2. Cost forecast (one primary API + one assistant, not a sum of everything — clearly marked illustrative).
  3. Real case references (organisation, outcome, source link).

## 4. Later Features (Should Have / Nice to Have)
- **Should Have:** downloadable plain-English cost summary.
- **Nice to Have:** one-click boilerplate config generation for the recommended stack.

## 5. Individual Learning Goals — corrected to 2 people
- **Student A (Data & Logic):** building a tool-name normalisation map and embedding pipeline; structuring a pricing schema that distinguishes per-seat SaaS from per-token APIs (a distinction our first draft missed).
- **Student B (UI & Validation):** designing a scannable 3-block output; running real user tests and tracking trust/value telemetry.

## Deliverable Summary
The ATSA MVP is a specialised AI-tool advisor. Five constraints feed a Python retrieval pipeline that searches a curated, normalised set of 3,023 real AI deployments, ranks tools by real adoption frequency, and estimates cost against a hand-built pricing table that correctly separates seat-based and token-based pricing. The output is a traceable, source-linked blueprint — not a black box.

## Project Q&A (updated)

**1. What's the MVP we can build and test in 3 weeks?**
A Streamlit app backed by a Python script and a local Chroma vector store — no separate orchestration service. It retrieves matching cases, applies deterministic privacy filtering, ranks tools, computes cost, and calls one LLM for the final summary text only.

**2. What hypothesis does this test?**
Whether grounding recommendations in real deployment evidence plus honest cost estimates reduces the "black box" trust problem our user research surfaced — without us needing to claim false certifications or authority to earn that trust.

**3. Must-haves vs optional.**
Must-have: normalisation + retrieval, 5-field intake, 3-block output. Optional (post-MVP): live pricing sync, general infrastructure recommendations, boilerplate export.

**4. What stack should we use, given our strengths?**
Streamlit (frontend) + plain Python (logic/filtering/costing) + Chroma (local vector store) + one LLM API call for summarisation. This is simpler than our original Flowise-based plan and removes an integration risk we had flagged ourselves.

**5. Learning goals per member** — see §5 above.
