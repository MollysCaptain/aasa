# User Research (v2)
*Supersedes the original in one section only. The personas, interview simulation, critical analysis, reality-check, and hypotheses below are genuine discovery work and are carried forward unchanged — they're what correctly drove the pivot. The final "Data Strategy Design" section, however, specified N=50/N=12 sample sizes, a "Human Architect Override Ratio" metric, and Flowise-based logging — all three now contradict decisions made elsewhere (Proposal & Scope v2, Effort-Informed Prioritisation v2). That section is corrected below; everything above it is unchanged from the original document.*

---

## Personas, Interviews, Critical Analysis, and Validation Hypotheses
*(Unchanged from the original — Persona 1 "Scrappy Builder", Persona 2 "Visionary Outsider", Persona 3 "Resourceful Generalist"; the 5 interview questions per persona; the pattern analysis; the reality-check on synthetic-vs-real users; the 3 validation hypotheses; and the structured interview guide. This work correctly identified the "StackPunk" aesthetic as a credibility risk and correctly flagged that synthetic personas are too agreeable — both conclusions still hold and are reflected in the rebuilt prototype and reconciled scope. Refer to the original User Research document for the full text of this section; it is not reproduced again here to avoid duplication.)*

---

## Data Strategy Design (v2 — corrected)

### Part 1: The Most Important Metrics
Corrected to remove one unmeasurable metric and align tooling with the simplified stack (Flowise dropped).

**User Behaviour Metrics**
1. **Form Completion Velocity** — time from first field interaction to submit.
2. **Field Abandonment Rate** — % of users dropping off at a specific field.
3. **Blueprint Export Rate** — % of users who copy/export the final blueprint.
4. **Blueprint Interaction Time** — time spent reading each of the 3 output blocks.

**Business Metrics**
5. **"Consultancy Gap" Match Rate** — % of users whose self-reported budget falls in the bootstrapped-to-mid-tier range.
6. **Compliance-Rule Pass Rate** *(replaces "Human Architect Override Ratio")* — % of generated blueprints where every recommended tool respects the deterministic privacy filter. **This is the corrected metric**: the original required an on-call human architect to grade every output, which a 2-person team cannot resource. This version is fully automatable and just as informative about logic correctness.
7. **Per-Query Cost** — average API cost per generated blueprint, for our own sustainability tracking.

**Satisfaction Metrics**
8. **Trust Score** — post-session 1–5 rating: "How confident are you presenting this to an investor or engineering team?"
9. **Net Value Score** — % of users stating the tool replaced hours/days of manual research.
10. **System Usability Scale (SUS)** — standard 10-item usability questionnaire.

### Part 2: Data Collection Plan

**1. User Actions to Track** — via lightweight in-app session logging (Streamlit session state + a simple event log), not a dedicated third-party product-analytics tool:
- `Form_Start` / `Form_Submit` timestamps.
- `Click_Export_Blueprint` events.
- Scroll/interaction time on each output block.

**2. Micro-Survey Questions** (unchanged from original):
- Quantitative: "Rate the professional trustworthiness of this recommendation." (1 = Unreliable Gimmick, 5 = Highly Professional Guide).
- Qualitative: "What is the single biggest barrier stopping you from using this exact tech stack right now?"

**3. Success vs. Failure Measurements**

| Objective | Success Metric | Failure Metric |
|---|---|---|
| Validate theme trust | ≥75% rate trust ≥4/5 | <50% trust rating; feedback mentions "unprofessional" |
| Validate scope boundary | Blueprint export rate >40% | Low export rate + demands for code generation |
| Validate logic system | Compliance-rule pass rate = 100% *(corrected)* | Any recommended tool violates the privacy filter |

**4. Statistical Sample Sizes — corrected**
The original targeted N=50 completed sessions and N=12 diverse testers. **Neither is achievable by a 2-person team inside a 3-week build-and-test window alongside actual development work**, so both are revised down:
- **Quantitative (form interactions):** as many sessions as we can log during the Week-3 real-user test — realistically single digits to low tens, treated as directional trend data, not a statistically powered sample.
- **Qualitative interviews:** **N = 5–8 diverse real testers**, recruited starting in Week 1 (not Week 3), spread across our three personas. This is a smaller number than originally planned, but it is a number we can actually deliver with real users rather than an aspirational target we'd have quietly missed.

**5. Tools & Methods for Collection — corrected**
- **In-app Python/Streamlit logging** *(replaces "Flowise/Streamlit Loggers")* — captures inputs, outputs, and filter-match results directly, since there is no separate orchestration service to log from once Flowise is dropped.
- **A simple micro-survey component** embedded in the results view for the two survey questions above.
- **Shared Google Sheet/Notion log**, maintained by both students, to manually code qualitative interview themes into prompt/logic patches.
