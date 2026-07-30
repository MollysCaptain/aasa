# P.9 — Full Backend Dry Run — Results
*Generated 2026-07-21 by `scripts/backend_dry_run.py`. Read every section below with Gabi, then complete the defect list at the end.*

## Profile 1 — everyday happy path
_Common query, standard posture — the baseline everything else is compared against._

**Inputs:** `{'workflow': 'Customer Service', 'industry': 'Technology', 'org_size': 'startup', 'privacy': 'standard', 'budget': 800}`

```
RECOMMENDED STACK:
  1. IBM watsonx (Assistant/AI/Orchestrate)  [ibm-watsonx · seat]
  2. Microsoft Azure (AI/ML services)  [azure-platform · compute]
  3. Azure OpenAI Service  [azure-openai · token]
  4. Gemini (consumer)  [gemini · seat]
  5. Amazon Bedrock  [aws-bedrock · token]

COST FORECAST:
  primary_api: azure-openai — €43.75/mo
  assistant:   ibm-watsonx — €2240.0/mo
  total_monthly_eur: 2283.75
  budget: 800   within_budget: False   delta: -1483.75

TOOL COSTS (per ranked tool):
  ibm-watsonx: €2240.0 (seat)
  azure-platform: €None (compute)
  azure-openai: €43.75 (token)
  gemini: €0.0 (seat)
  aws-bedrock: €35.0 (token)

MATCHED CASES (15):
  - IBM | Technology | tools=['ibm-watsonx'] | https://www.ibm.com/case-studies/ibm-salesforce
  - Capacity | Cross-Industry | tools=['azure-platform'] | https://www.microsoft.com/en/customers/story/24201-capacity-azure-phi
  - IBM | Cross-Industry | tools=['ibm-watsonx'] | https://www.ibm.com/think/topics/artificial-intelligence-business-use-cases
  - IBM Software Support | Technology | tools=['ibm-watsonx'] | https://www.ibm.com/case-studies/ibm-software-support
  - Computer Gross | Technology | tools=['ibm-watsonx'] | https://www.ibm.com/case-studies/computer-gross
  - Replicant | Cross-Industry | tools=['gemini'] | https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders#powering-data-management-platform-with-google-cloud-ai-and-bigquery
  - ServiceTitan | Professional Services | tools=['azure-openai', 'azure-platform'] | https://www.microsoft.com/en/customers/story/1777780179509111168-servicetitan-azure-machine-learning-national-government-en-united-states
  - MacStadium | Technology | tools=['aws-bedrock', 'ibm-watsonx'] | https://www.ibm.com/case-studies/macstadium
  ... (+7 more)

SUMMARY TEXT:
  Based on 15 comparable deployments, the recommended stack uses IBM watsonx (Assistant/AI/Orchestrate) together with Azure OpenAI Service. The forecasted monthly cost is €2283.75, with Azure OpenAI Service at €43.75 and IBM watsonx at €2240. This exceeds your €800 budget by €1483.75. A smaller pilot group or a lower‑cost alternative could help bring the spend within budget.

QUERY ECHO: {'workflow': 'Customer Service', 'industry': 'Technology', 'org_size': 'startup', 'privacy': 'standard'}
PROJECT NAME: ''
LLM METRICS: {'duration_seconds': 1.36, 'prompt_tokens': 1101, 'completion_tokens': 442, 'tokens_per_second': 325.0}
```

**Automated checks:**
- PASS — total (2283.75) == primary+assistant (2283.75)
- PASS — within_budget flag matches total vs budget
- PASS — summary mentions only ranked tools (possible extras: none)

## Profile 2 — regulated filter stress test
_Regulated posture must strip consumer-only tools (e.g. consumer Gemini) before ranking._

**Inputs:** `{'workflow': 'Data & Analytics', 'industry': 'Healthcare', 'org_size': 'ent', 'privacy': 'regulated', 'budget': 5000}`

```
RECOMMENDED STACK:
  1. Amazon Bedrock  [aws-bedrock · token]
  2. AWS (SageMaker/S3/EC2/etc.)  [aws-platform · compute]
  3. Google Cloud Platform  [google-cloud · compute]
  4. IBM watsonx (Assistant/AI/Orchestrate)  [ibm-watsonx · seat]
  5. Microsoft Dynamics 365  [ms-dynamics · seat]

COST FORECAST:
  primary_api: aws-bedrock — €3500.0/mo
  assistant:   ibm-watsonx — €3500.0/mo
  total_monthly_eur: 7000.0
  budget: 5000   within_budget: False   delta: -2000.0

TOOL COSTS (per ranked tool):
  aws-bedrock: €3500.0 (token)
  aws-platform: €None (compute)
  google-cloud: €None (compute)
  ibm-watsonx: €3500.0 (seat)
  ms-dynamics: €2375.0 (seat)

MATCHED CASES (13):
  - Highmark Health | Healthcare | tools=['google-cloud'] | https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders#intelligence-system-for-healthcare-analytics-and-insights
  - EkaCare | Healthcare | tools=['aws-bedrock'] | https://aws.amazon.com/solutions/case-studies/generative-ai-ekacare/?did=cr_card&trk=cr_card
  - Shanghai Changjiang Science and Technology Development | Healthcare | tools=['ibm-watsonx'] | https://www.ibm.com/case-studies/shanghai-changjiang-science-and-technology-development-co-ltd
  - SolutionHealth | Healthcare | tools=['ms-dynamics', 'nuance-dragon'] | https://www.microsoft.com/en/customers/story/22439-solutionhealth-azure
  - AWS | Healthcare | tools=['aws-bedrock', 'aws-platform'] | https://aws.amazon.com/health/solutions/health-data-portfolio/
  - Merck & Co., Inc. | Healthcare | tools=['aws-bedrock', 'aws-platform'] | https://aws.amazon.com/blogs/industries/executive-conversations-the-promise-of-generative-ai-for-the-commercial-pharma-value-chain/?did=cr_card&trk=cr_card
  - Healthfirst | Healthcare | tools=['aws-platform'] | https://youtu.be/XpFNznmRoQ0?did=cr_card&trk=cr_card
  - Mayo Clinic | Healthcare | tools=['vertex-ai'] | https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders#accelerating-information-retrieval-from-clinical-data
  ... (+5 more)

SUMMARY TEXT:
  Based on 13 comparable deployments in regulated industries, the combination of Amazon Bedrock, AWS (SageMaker/S3/EC2/etc.), Google Cloud Platform, IBM watsonx (Assistant/AI/Orchestrate), and Microsoft Dynamics 365 offers a robust, directionally suited to governable environments solution. The forecasted monthly cost is €7,000, with Amazon Bedrock at €3,500 and IBM watsonx at €3,500, which exceeds your €5,000 budget by €2,000. A smaller pilot group or a lower‑cost alternative could help bring the spend within budget. This recommendation aligns with the privacy posture of regulated environments.

QUERY ECHO: {'workflow': 'Data & Analytics', 'industry': 'Healthcare', 'org_size': 'ent', 'privacy': 'regulated'}
PROJECT NAME: ''
LLM METRICS: {'duration_seconds': 1.62, 'prompt_tokens': 1108, 'completion_tokens': 751, 'tokens_per_second': 463.6}
```

**Automated checks:**
- PASS — regulated filter: consumer-only tools in stack = none
- PASS — total (7000.0) == primary+assistant (7000.0)
- PASS — within_budget flag matches total vs budget
- PASS — summary mentions only ranked tools (possible extras: none)

## Profile 3 — sparse / graceful-degradation case
_Deliberately thin combination — checks the app degrades gracefully, not crashes, on few matches._

**Inputs:** `{'workflow': 'Facilities & EHS', 'industry': 'Agriculture', 'org_size': 'solo', 'privacy': 'regulated', 'budget': 150}`

```
RECOMMENDED STACK:
  1. Microsoft Azure (AI/ML services)  [azure-platform · compute]
  2. AWS (SageMaker/S3/EC2/etc.)  [aws-platform · compute]
  3. Azure OpenAI Service  [azure-openai · token]
  4. Amazon Bedrock  [aws-bedrock · token]
  5. Google Cloud Platform  [google-cloud · compute]

COST FORECAST:
  primary_api: azure-openai — €8.75/mo
  assistant:   None
  total_monthly_eur: 8.75
  budget: 150   within_budget: True   delta: 141.25

TOOL COSTS (per ranked tool):
  azure-platform: €None (compute)
  aws-platform: €None (compute)
  azure-openai: €8.75 (token)
  aws-bedrock: €7.0 (token)
  google-cloud: €None (compute)

MATCHED CASES (15):
  - KWS | Agriculture | tools=['aws-bedrock'] | https://aws.amazon.com/solutions/case-studies/generative-ai-adastra-kws/?did=cr_card&trk=cr_card
  - FarmByte | Agriculture | tools=['aws-platform'] | https://aws.amazon.com/solutions/case-studies/farmbyte/?did=cr_card&trk=cr_card
  - Avanade | Agriculture | tools=['azure-platform'] | https://ukstories.microsoft.com/features/now-thanks-to-ai-we-really-can-talk-to-the-trees/
  - AgriConnect | Agriculture | tools=['azure-platform'] | https://news.microsoft.com/source/asia/2025/02/27/harvesting-hope-with-agriconnect-how-ai-is-uplifting-filipino-farmers/
  - Bosch SDS | Energy & Utilities | tools=['google-cloud'] | https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders#building-an-ai-based-cognition-engine-for-sustainability-and-energy-management
  - Atlante | Energy & Utilities | tools=['aws-bedrock'] | https://aws.amazon.com/solutions/case-studies/atlante-generative-ai/?did=cr_card&trk=cr_card
  - Siemens Energy | Energy & Utilities | tools=['aws-platform', 'nvidia'] | https://www.nvidia.com/en-us/customer-stories/siemens-energy-simplifies-safety-inspections-with-nvidia-triton-inference-server/
  - ITC | Agriculture | tools=[] | https://www.microsoft.com/en-in/aifirstmovers/itc
  ... (+7 more)

SUMMARY TEXT:
  Based on 15 comparable deployments, Azure OpenAI Service is a proven, low‑cost option that fits comfortably within your €150 monthly budget, with a forecast of just €8.75 per month. The forecast is well below the budget, leaving room for future expansion. This recommendation is directionally suited to governable environments, though you should verify current pricing and compliance requirements with the vendor. If you need additional AI/ML services, Microsoft Azure (AI/ML services), AWS (SageMaker/S3/EC2/etc.), Amazon Bedrock, and Google Cloud Platform are also available options.

QUERY ECHO: {'workflow': 'Facilities & EHS', 'industry': 'Agriculture', 'org_size': 'solo', 'privacy': 'regulated'}
PROJECT NAME: ''
LLM METRICS: {'duration_seconds': 1.39, 'prompt_tokens': 1043, 'completion_tokens': 996, 'tokens_per_second': 716.5}
```

**Automated checks:**
- PASS — regulated filter: consumer-only tools in stack = none
- PASS — total (8.75) == primary+assistant (8.75)
- PASS — within_budget flag matches total vs budget
- PASS — summary mentions only ranked tools (possible extras: none)

## Defect list

> **Completed retrospectively on 2026-07-30, during the Card P.22 pass. Read that
> before reading the table.**
>
> This section and the go/no-go below were left as blank templates on 2026-07-21.
> The three profiles were run and read — Week 3 went ahead on the strength of them —
> but the written record of *what was found* was never filled in, and it stayed
> blank through two consistency passes. It only surfaced when P.22 ran the script
> again and read the file it produced.
>
> Two rules were applied so this is a record and not a reconstruction:
>
> 1. **Nothing is listed that isn't visible in the output above or evidenced in a
>    dated commit.** Every row cites where to check it. No defect has been invented
>    to make the table look thorough, and none has been softened.
> 2. **Nothing is backdated.** Where a defect was found later than this run, the row
>    says when, by whom, and — more importantly — whether the evidence for it was
>    already sitting in this document. For D1 it was.
>
> The €68,433.75/mo budget bug is deliberately **not** listed. It was real and
> serious, but it was found and fixed on 2026-07-16 (Update D, Build Guide 18;
> verified in Build Guide 21) — five days *before* this run. Claiming it here would
> be the easiest way to make a retrospective defect list look productive, which is
> exactly why it isn't.

| # | Severity | Description | Owner | Fix-before-Week-3? |
|---|---|---|---|---|
| **D1** | **High** | **The output above contains the evidence for the project's worst disclosure defect, and nobody reading it noticed.** Profile 3 is *Facilities & EHS in Agriculture* — a pair with exactly **1** real case in the whole 3,023-case corpus. It returned "MATCHED CASES (15)". Of the 8 printed, **exactly one is a true match**: Avanade (Facilities & EHS, Agriculture, `azure-platform`). Of the rest, KWS, FarmByte, AgriConnect and ITC are Agriculture but a different workflow (R&D, Operations ×2, Customer Service); Bosch SDS, Atlante and Siemens Energy are Facilities & EHS but **Energy & Utilities**. At the time the UI banner said "*N* real {industry} {workflow} deployments matched" — so it announced **15** where **1** was true, and as later measured the same sentence was false for **185 of 432** selectable pairs. The three automated checks all PASSed, because none of them asks whether the evidence is what the user asked for.<br><br>Two details that make this sharper rather than softer: the *ranking* was sound — `azure-platform`, the single genuinely-matching case's tool, came out **#1** — so the product was recommending well and describing its evidence badly, which is harder to spot than being wrong outright. And the profile was chosen precisely as the "*deliberately thin / graceful-degradation*" case, meaning the harness aimed a test at exactly this weakness and the reviewer read the PASS lines instead of the evidence. | Ash | **Missed.** Not found until 2026-07-27 (Card Ash4, Build Guide 35), by calibrating the relevance threshold rather than by re-reading this file. Fixed then: `pipeline.py` carries `domain` per case and returns `exact_match_count`, and the banner distinguishes real matches from nearest-comparable ones. |
| **D2** | **Medium** | **A "fits your budget" verdict computed from a partial stack.** Profile 3 recommends 5 tools; **3 return `€None (compute)`** and are shown but never costed (`app/logic/cost.py:113` — by design, per the technical work breakdown). `total_monthly_eur: 8.75` is the primary API *only*: even `aws-bedrock`'s own €7.00 per-tool figure is excluded, because the forecast is primary + assistant rather than the sum of the stack. So `within_budget: True` against €150 is arithmetically correct and materially incomplete. The automated check "total == primary+assistant" **cannot** catch this, because it defines the total the same way the code does — it tests internal consistency, not coverage. | Joint | **No — accepted as design, disclosure gap closed.** The behaviour is documented (`Intake-Output-Schema-v1.md`, Build Guide 22) and the per-tool table shows `€None` honestly. What P.9 should have flagged is that the *check* was tautological. Recorded in `Known-Limitations-v1.md`. |
| **D3** | **Low** | **A case with no tools is presented as evidence.** `ITC \| Agriculture \| tools=[]` occupies one of Profile 3's 15 evidence slots. It contributed nothing to the ranking — it has no canonical tools to count — yet it appears in Block C as a real case reference. This is the visible end of the 88.7% alias-coverage figure: 341 of 3,023 cases resolve to no canonical tool, and they remain eligible as evidence. Still present in the 2026-07-30 re-run, so this is current, not historical. | Gabi | **No.** Cosmetic and honest (the case is real and its industry is shown correctly), but it dilutes the evidence block. Filtering zero-tool cases out of Block C is a one-line change and is **not** being made under the P.15 freeze. Logged as a known limitation instead. |
| **D4** | **Process** | **The three profiles never exercise Mid-Market.** They use `startup`, `ent` and `solo`. `mid` (201–1,000) is the only band untested — and it is the band the €68,433.75 budget bug surfaced in. That bug predates this run, so P.9 didn't miss it; but a "skeptical stranger" harness that skips a whole org-size band was luckier than it was rigorous. | Joint | **No.** Adding a 4th profile is a change to a verification script (P.15 category 2, permitted) but it was judged too late to be worth the churn on the last day. Recorded here so the gap is visible rather than implied to be covered. |
| **D5** | **Medium** | **The summary's hedging is not stable across runs.** On 2026-07-21 Profile 3's summary closed with "*you should verify current pricing and compliance requirements with the vendor*". The 2026-07-30 re-run of the same profile closed with "*You can proceed with confidence knowing that similar deployments have succeeded in regulated industries*" — on a profile with 1 exact case. Different builds and different LLM calls, so this is inherent to generated prose rather than a regression, but it means the caution a user sees is a coin-flip. | Ash | **Partly, later.** The prompt forbids inventing tools and prices and that holds; it does not constrain confidence language. Mitigated after this run by the banner (D1) and the DIRECTIONAL ONLY label carrying the caveat deterministically, so the summary is no longer the only thing warning the user. Prompt-level constraint on confidence wording is Icebox. |

### What this run actually proved

Worth stating alongside the defects, because the harness did do its job in one respect:

- **The regulated filter demonstrably works, and this output is the proof.** Profile 1 (standard posture) ranks `gemini` — a consumer tool — at position 4. Profile 2 and Profile 3 (both regulated) contain no consumer tool at all. Same corpus, same ranking code, only the posture differs. That is a cleaner demonstration than the automated PASS line, which merely reports the absence.
- All three profiles completed end to end with no exception, in 1.36–1.62s of LLM time each (1.36 / 1.62 / 1.39).
- Cost arithmetic is internally consistent in all three, and the over-budget cases (Profiles 1 and 2) both state the overage plainly in prose rather than glossing it.

### The pattern, recorded because it repeated

D1 is the third instance on this project of the same failure: **the measurement ran correctly and the check around it was wrong.** `distancecheck.py` returned an accurate sweep and an incorrect FAIL verdict; the documented P.14 command was missing its end bound; here, three automated checks PASSed on output that contained a false user-facing claim, and the PASSes are what the reviewer's eye went to. A check that can only confirm what the code already believes will pass forever. See `Capstone Plan/PM Work/16-P22-Final-Consistency-Pass-v1.md`.

## Go / no-go for Week 3

*Recorded retrospectively 2026-07-30. The decision itself was taken on 2026-07-21 —
Week 3 proceeded — so what follows documents what was decided and on what basis,
not a meeting held after the fact.*

- [x] **All 3 profiles ran** — output above, no exceptions, all automated checks PASS.
- [ ] **Output read by both people** — *left unticked deliberately.* It was read, and the work that followed reflects it, but only Ash and Gabi can attest to that and neither did so at the time. Ticking it now on the strength of an inference would be the one thing this document shouldn't do. **Ash/Gabi: tick if you can both confirm it.**
- [x] **Profile 2 regulated filter confirmed excluding consumer tools** — confirmed twice over: `gemini` ranks 4th under standard posture and is absent from both regulated profiles, and `scripts/compliance_check.py` returns 2/2 (100%) as of 2026-07-30.
- [x] **5–8 real testers confirmed scheduled (Card P.2)** — met and exceeded: 8 participants tested on 2026-07-27/28. Results in `P14-Validation-Metrics-Final-v1.md`.
- [x] **Decision recorded: on track for Week 3.** Taken 2026-07-21 on the basis that all three profiles ran clean, the regulated filter provably worked, and cost arithmetic was consistent. **That decision was right on the evidence available and was made against an incomplete reading of it** — D1 was sitting in this output and went unseen for six days. The honest summary is: on track, and the go/no-go was easier to pass than it should have been, because every check in the harness could only confirm what the code already assumed.