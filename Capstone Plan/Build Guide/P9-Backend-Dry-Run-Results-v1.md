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

## Defect list (fill in together)

| # | Severity | Description | Owner | Fix-before-Week-3? |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## Go / no-go for Week 3
- [ ] All 3 profiles ran and output read by both people
- [ ] Profile 2 regulated filter confirmed excluding consumer tools
- [ ] 5–8 real testers confirmed scheduled (Card P.2)
- [ ] Decision recorded: **on track / not on track** for Week 3 — _(write it here)_