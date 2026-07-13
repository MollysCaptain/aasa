# Capstone Project Proposal: User Research (AI Stack Architect Prototype Feedback)

**Document Version:** V1  
**Date:** July 12, 2026  
**Line Spacing:** 1.25  

## 1. User Persona Framework

To ground the prototype evaluations, three core target personas are established to represent distinct segments of the market experiencing the "Consultancy Gap."

### Persona 1: The "Scrappy Builder" (Technical Founder)
*   **Job Title:** Founder & Lead Engineer (Early-stage startup)
*   **Daily Workflow:** ~70% coding, 20% recruiting/fundraising, 10% researching infrastructure (AWS, Reddit, YouTube).
*   **Psychological Drivers:** Fears technical debt; wants correctness but avoids over-engineering the MVP.
*   **Decision-making Process:** Data-driven but time-poor; seeks benchmarks yet struggles to adapt them.
*   **Biggest Frustrations:** Wastes days comparing Serverless vs. Containers vs. Managed DBs without clarity on cost or scale.
*   **Secret Motivation:** Wants recognition as a technical powerhouse but would trade architecture research time for product development.

### Persona 2: The "Visionary Outsider" (Non-Technical CEO)
*   **Job Title:** CEO / Founder (Non-Technical)
*   **Daily Workflow:** Sales, investor relations, strategy, and overseeing a small team of contractors/employees.
*   **Psychological Drivers:** Urgency and risk aversion. Needs rapid progress but fears hidden technical failures or surprise costs.
*   **Decision-making Process:** Trust-based. Prefers clear Yes/No guidance and dislikes nuanced "it depends" answers.
*   **Biggest Frustrations:** Feeling trapped by technical complexity and hearing "it's complicated" without clear cost/time trade-offs.
*   **Secret Motivation:** Wants enough tech understanding to avoid looking ignorant to investors but mainly seeks a trusted expert or tool to give the green light.

### Persona 3: The "Resourceful Generalist" (SMB Head of Product)
*   **Job Title:** Head of Product / Early Eng. Manager (SMB)
*   **Daily Workflow:** Bridges marketing wants and dev limits; manages a 3–5 person team.
*   **Psychological Drivers:** Pragmatism and Efficiency. Needs to keep projects moving while staying under budget.
*   **Decision-making Process:** Pragmatic, "good enough" choices that meet core needs; prioritizes time to market.
*   **Biggest Frustrations:** The "Consultancy Gap"—can't afford $20k consultants but can't rely on generic free advice.
*   **Secret Motivation:** To be the hero who saves money while delivering a professional product and proves strategic business-tech judgment.

---

## 2. Structured Interview Responses

### Question 1: "Walk me through your first impression of this prototype"
*   **The Scrappy Builder (Technical Founder):** Immediate visual layouts are highly engaging, skipping the tedious "blank canvas" phase and saving manual mapping time in Miro or Excalidraw. However, the core baseline instinct is to stress-test the integration points. Technical feasibility is highly prioritized over surface novelty, raising skepticism about component depth regarding rate limits, data privacy, and scaling cost implications.
*   **The Visionary Outsider (Non-Technical CEO):** The initial layout feels highly empowering by bridging the communication gap. It converts a natural language description into a concrete artifact to show investors or technical co-founders. However, an immediate hesitation occurs regarding technical debt, leading to an urgent need for plain-English explanations rather than architectural jargon.
*   **The Resourceful Generalist (SMB Head of Product):** First impression reveals an efficient scoping tool that accelerates cross-functional discovery and alignment workshops. The immediate hesitation rests on customization and constraints; the tool must accommodate legacy databases and compliance policies rather than assuming a completely clean-slate, greenfield stack.

### Question 2: "What would make you choose this over current alternatives?"
*   **The Scrappy Builder (Technical Founder):** Will pivot away from whiteboarding or forum browsing if the tool provides deterministic execution and deep context. The tipping point requires moving past surface-level blocks to deliver actual API payloads, configurations, and direct documentation links, alongside dynamic token cost, latency, and rate-limit math.
*   **The Visionary Outsider (Non-Technical CEO):** Will choose this tool over expensive consultancy fees or blind agency trust if it acts as a reliable interpreter. The deciding factor is a clear "Business Translation Layer" outlining exact monthly hosting costs, realistic build timelines, and standardized investor-ready blueprints.
*   **The Resourceful Generalist (SMB Head of Product):** Spends too much time in text-heavy alignment meetings. Will switch to this prototype if it resolves the "Consultancy Gap" by providing collaborative, multi-variable iteration—enabling a team to toggle architectural choices and immediately observe timeline and budget dependencies.

### Question 3: "What's the most confusing or frustrating part?"
*   **The Scrappy Builder (Technical Founder):** Frustrated by the "Black Box" nature of automated stack selections if the underlying rationale isn't fully transparent. Hallucinated parameters, outdated configurations, or breaking syntax errors transform a time-saving concept into a tedious debugging chore.
*   **The Visionary Outsider (Non-Technical CEO):** Hits a steep "Jargon Cliff" where high-level descriptions give way to complex infrastructure terms (e.g., idempotency, webhooks, ingress). The visual inability to determine if moving a component breaks the system breeds deep user anxiety.
*   **The Resourceful Generalist (SMB Head of Product):** Suffers from the "Greenfield Fallacy," struggling to enforce strict real-world workspace rules (e.g., AWS only, strict on-premise constraints). The boundary between abstract brainstorming and literal infrastructure-as-code deployment currently feels awkwardly blurred.

### Question 4: "What's missing that you expected to see?"
*   **The Scrappy Builder (Technical Founder):** Expected a one-click Infrastructure-as-Code (IaC) export engine (e.g., Terraform, Pulumi), robust version control for parallel branching architectures, and built-in automated security alerts to call out exposed public gateways.
*   **The Visionary Outsider (Non-Technical CEO):** Expected a highly prominent, interactive monthly burn rate calculator and a conversational AI co-pilot chat overlay to explain infrastructure logic on the fly. Also missing is an executive "Pitch Mode" to easily download investor-ready presentation sheets.
*   **The Resourceful Generalist (SMB Head of Product):** Expected a comprehensive pre-existing tech stack inventory setting page, seamless Product Requirement Document (PRD) synchronization to connect diagram modules to product features, and a clear engineering task hand-off framework mapped to Jira or Linear.

### Question 5: "Would you recommend this to others like you?"
*   **The Scrappy Builder (Technical Founder):** Recommends the tool purely for rapid validation loops and escaping structural cold starts. Warns technical peers to treat the output like a rough draft, verify compliance barriers independently, and look directly past aesthetic styling to focus entirely on the output logic blocks.
*   **The Visionary Outsider (Non-Technical CEO):** Hesitates to broadly recommend it if the theme compromises professional credibility or board trust. However, if the interface leans directly into clean, authoritative cost transparency, it transforms into an absolute lifesaver for non-technical leaders looking to bypass heavy agency fees.
*   **The Resourceful Generalist (SMB Head of Product):** Strongly recommends this to product heads isolated in the "Consultancy Gap." It delivers a tailored, multi-variable optimization environment that factors in small-team skill caps and tight marketing budgets, acting as an essential tool for strategic business-tech planning.

---

## 3. Pattern Analysis & Critical Analysis

### 3.1 Pattern Synthesis

| Dimension | 💻 The Scrappy Builder | 📈 The Visionary Outsider | 🛠️ The Resourceful Generalist |
| :--- | :--- | :--- | :--- |
| **Primary Driver** | Technical accuracy; avoiding long-term technical debt. | Risk aversion; ensuring cash flow and investor alignment. | Pragmatism; maximizing time-to-market with a small team. |
| **Output Desired** | Deterministic code filters, data states, and API benchmarks. | A plain-English, downloadable PDF financial summary for the board. | An integration risk matrix measuring team skill caps. |
| **Evaluation Focus** | Focused deeply on the logic, data models, and schemas. | Focused on visual trust, corporate stability, and cost boundaries. | Focused on the practical translation between business and engineering limits. |

### 3.2 Core Strengths vs. Red Flags
*   **Core Strengths (Why they choose it):** Unrivaled speed compresses traditional two-week research loops into an automated 2-minute workflow. Pragmatic multi-variable calculations respect strict user constraints over generic provider advice.
*   **Red Flags (Why they abandon it):** Visual gimmickry can severely degrade professional trust with stakeholders or investors if it compromises authority. Additionally, any soft-match errors that violate binary, strict compliance rules (e.g., HIPAA/GDPR) pose an unacceptable liability risk.

### 3.3 Reality Check (Human Messiness Gaps)
*   **Idealized Architecture Acceptance:** In practice, real-world users rarely respect abstract scope boundaries cleanly and will aggressively push for direct source-code generation rather than simple blueprint layout maps.
*   **Irrational Decision-Making:** Real humans are highly influenced by personal developer fatigue, historical brand comfort, and emotional aversion to specific interfaces, defying purely logical data parameters.
*   **The Speed vs. Autonomy Paradox:** Technical founders inherently harbor strong stack protective biases. They will spend prolonged periods deliberately trying to trick or stress-test an automated model to gauge baseline intelligence before accepting its guidance.

---

## 4. Empirical Validation Priorities & User Testing Guide

### 4.1 High-Priority Research Hypotheses
*   **Hypothesis 1 (The Trust Threshold):** A non-technical founder will instinctively reject a generated technical layout unless it directly flags mainstream social proof or market validation markers (e.g., "Used by Stripe/Airbnb") alongside architectural nodes.
*   **Hypothesis 2 (The Scope Pushback):** Technical founders will experience immediate drop-off and tool frustration unless a structural schematic is coupled with an instantaneous, one-click export to workable boilerplate repository scaffolding.
*   **Hypothesis 3 (The Aesthetic Distraction):** Creative design flourishes and layout styling will induce immediate abandonment if essential technical data outputs require more than two scroll actions or expansions to fully scan.

### 4.2 Target User Testing Protocol
1.  **Section 1: Testing Synthetic Scope Assumptions:** Probe human expectations by tracking real reactions to static layout modules. Ask: *"When scanning this generated blueprint, what is the exact subsequent action you feel compelled to take?"* or *"Which blueprint block delivers zero standalone value to your workflow?"*
2.  **Section 2: Uncovering Latent Emotional Vulnerabilities:** Dig into irrational business biases. Ask: *"What infrastructure ecosystem do you absolutely refuse to utilize even if raw benchmarks prove it optimizes your monthly runway, and why?"*
3.  **Section 3: Verifying Historic Real-World Behaviors:** Isolate true actions from future intentions. Ask: *"Walk me through the exact open tabs, duration, and friction points experienced the last time you finalized a core system architecture decision manually."*
4.  **Section 4: Forcing Behavioral Inconsistencies:** Uncover accurate prioritizations. Ask: *"If a proposed framework reduces your running costs by 50% but delays your time-to-market window by two months, how do you proceed?"*

---

## 5. Data Strategy & Success Matrix

### 5.1 Ten Critical Project Metrics
1.  **Form Completion Velocity:** Total elapsed time from initial user parameter input to blueprint request execution.
2.  **Field Abandonment Rate:** Granular drop-off percentages tracked against high-friction inputs like compliance rules.
3.  **Blueprint Export Rate:** The absolute percentage of user sessions that engage in sharing, saving, or copying a schema output.
4.  **Blueprint Interaction Time:** Total duration users spend expanding, reading, or analyzing individual architectural nodes.
5.  **Consultancy Gap Match Rate:** The percentage of active platform users showcasing actual small-to-medium business budget caps.
6.  **Human Architect Override Ratio:** Discrepancy rate where verified industry experts flag an AI-generated layout as incorrect.
7.  **Per-Query Token Efficiency:** Financial and environmental cost metric calculating data overhead per layout generated.
8.  **Trust-to-Branding Score:** Quantified user evaluation ranking visual professionalism and authority on a 1–5 scale.
9.  **Net Value Score (NVS):** Percentage of active users confirming the platform successfully replaced manual research workflows.
10. **System Usability Scale (SUS):** Standardized post-test layout scoring measuring overall accessibility and visual clutter.

### 5.2 Collection Infrastructure Plan

| Objective | Success Metric Baseline | Failure Metric Threshold |
| :--- | :--- | :--- |
| **Validate Theme Trust** | Greater than 75% of total test users rate layout trustworthiness at &ge; 4/5. | Less than 50% trust ratings paired with qualitative terms like "unprofessional" or "gimmick." |
| **Validate Scope Boundary** | Blueprint Export Rate holds above a steady 40% target across all user sessions. | Depressed export metrics matched with high user feedback demanding direct code creation. |
| **Validate Logic System** | Human expert or grading architect layout override metrics remain below 15%. | Override thresholds exceed 25%, indicating systematic compliance or structural recommendation errors. |

**Sample Sizes Required for Capstone MVP:** Quantitative analytics will prioritize **N = 50 completed user sessions** to isolate recurring interaction and drop-off trends. Qualitative user testing maps a baseline target of **N = 12 deeply documented human interviews** split evenly across all three primary personas (4 Builders, 4 Visionaries, 4 Generalists) to capture 80% of latent interface or architectural trust blockers.
