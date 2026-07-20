# Model / Dataset Card — AASA Case Library

*Card P.8 (bias & dataset-skew model card). Written per the template in
`Capstone Plan/Build Guide/15-Build-Guide-PM-Ethics-Week1-2-v1.md`, filled with
real figures computed from `data/use-cases.csv`, not generic placeholders.*

**Version:** v1 · **Dated:** 2026-07-20 · **Owner:** Person A (Gabi), supported by Person B (Ash)

---

**Dataset:** 3,023 real AI-deployment case rows (13 columns), sourced from the
open, MIT-licensed [AI Use-Cases Library](https://github.com/abbasmahdi-ai/ai-use-cases-library)
(see Handbook §2). Each row carries a description, reported outcome, and a
source URL. Cases were aggregated from public vendor case-study libraries
(Google, Microsoft, AWS, IBM, NVIDIA, OpenAI, Anthropic) plus press coverage.

**Intended use:** retrieval of *comparable real-world AI deployments* to ground
tool recommendations in evidence — **not** a statistically representative survey
of "all AI adoption," and not compliance certification or financial advice.

## Known limitations / bias (measured, not assumed)

- **Tool coverage skews to enterprise cloud & productivity AI.** The five most
  frequent canonical tools account for **45% of all tool mentions**: Microsoft
  Azure (580 cases), Google Gemini (406), Azure OpenAI (353), Google Cloud
  (326), AWS (283). Agent-framework tooling (LangChain / CrewAI-style)
  sometimes assumed to dominate "AI adoption" is comparatively rare here. AASA's
  recommendations reflect this real-world adoption pattern, not an idealised or
  evenly-weighted landscape.

- **Industry concentration.** Cases span **24 industries**, but the top three —
  Technology (492), Financial Services (371), Healthcare (347) — make up **40%
  of all rows**. Queries in thinner-represented industries have less evidence
  behind them.

- **Coverage is 88.7%, not 100%.** 2,682 of 3,023 rows resolved to at least one
  canonical tool via the alias map; the remaining ~11% (and 257 unmatched raw
  tool strings, logged in `data/unmatched_tools.log`) are tracked, not hidden,
  but do not contribute to ranking.

- **No organisation-size field exists in the case data.** Recommendations are
  **not** filtered by company size. "Organisation Size" in the app is a
  separate, user-stated taxonomy used only for the illustrative cost estimate,
  never for matching cases.

- **Ranking reflects adoption frequency in this dataset, not "best tool for
  every situation."** It is evidence of what comparable organisations have
  used — not a guarantee of fit for your specific context.

## Fairness consideration

Because ranking is frequency-based and the data skews toward large-company
tools, **smaller or newer vendors are systematically under-recommended even
when well-suited** to a given case. This is disclosed to users in-product (the
"About this data" note near the results), not hidden.

## Verification — the ranking is genuinely frequency-based

The credibility of this card depends on the ranking being real counts, not a
manual reorder. Confirmed against the code: `rank_tools_by_frequency()` in
`app/logic/filter.py` is a plain `collections.Counter` over the matched,
privacy-filtered cases returning `counter.most_common(top_n)` — no manual
weighting, boosting, or hand-reordering anywhere in the ranking path.

## What we do to mitigate

- The skew is disclosed, not corrected away — "correcting" it would mean
  inventing evidence the dataset doesn't contain.
- Every recommendation links back to the real cases behind it (source URLs), so
  users can judge the evidence themselves.
- Pricing is labelled illustrative and compliance filtering is labelled
  directional throughout the UI.

*To refresh the figures in this card after a data update, re-run the counts in
`scripts/backend_dry_run.py`'s data or a quick `value_counts()` over
`data/use-cases.csv` — this card is hand-maintained and will not update itself.*
