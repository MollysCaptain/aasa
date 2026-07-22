# P.14 — Compile Final Metrics from Telemetry — Results

*Generated 2026-07-21, computed from `data/telemetry.log` (post-dedup, post-merge into `main`) via `scripts/telemetry_funnel.py` and `scripts/credible_interval.py`. Compliance-rule evidence drawn from `P9-Backend-Dry-Run-Results-v1.md`'s real pipeline output (see note below).*

## Headline metrics

```
[2, 3, 3, 4, 4] -> trust-score median: 3 (5 responses)
14 completed sessions, avg time to results: 381.6s
LLM: avg 1.51s over 14 calls (min 0.82, max 3.29)
```

## Funnel

```
Funnel: 14 viewed -> 7 exported (50% of viewers) -> 5 survey responses, 4 said they'd use it (80% of respondents)
```

Read as a sequence, not three independent stats: of everyone who saw a blueprint, half went on to export it; of the smaller group who then filled out the survey, 4 of 5 said they'd use it.

## Credible intervals (Beta(1,1) prior, 90%)

```
Net value: 80% (4/5), 90% credible interval: 42%-94%
Blueprint export rate: 50% (7/14), 90% credible interval: 30%-70%
```

Both intervals are wide — expected at n=5-8 — and both include the target rate, but the lower bounds (42% and 30%) sit well below the ≥70%/≥40% targets. Read the point estimates as encouraging, not confirmed.

## Compliance-rule pass rate

`scripts/compliance_check.py` re-runs the real pipeline (`app.pipeline.run_pipeline` → Card 2.5's `apply_privacy_filter` + `rank_tools_by_frequency`) for every regulated-posture profile tested, and checks the output against the full `GOVERNABLE_FOR_REGULATED` allowlist — stricter than `backend_dry_run.py`'s own sanity check, which only tests against a narrow `CONSUMER_ONLY_IDS = {"gemini"}` proxy set.

**Note on how this was verified:** the script itself needs the same ML infra as `backend_dry_run.py` (a populated `chroma_store`, the `all-MiniLM-L6-v2` model, `GROQ_API_KEY`) to actually call the live pipeline. Rather than re-run it in an environment without that stack installed, this result is drawn from `P9-Backend-Dry-Run-Results-v1.md`'s already-committed output — the real pipeline's actual recorded result for these exact regulated queries — cross-checked against the current, full `GOVERNABLE_FOR_REGULATED` set (not just eyeballed):

| Profile | Recommended stack | Violations |
|---|---|---|
| Profile 2 — Healthcare/ent/regulated | aws-bedrock, aws-platform, google-cloud, ibm-watsonx, ms-dynamics | none |
| Profile 3 — Agriculture/solo/regulated | azure-platform, aws-platform, azure-openai, aws-bedrock, google-cloud | none |

**Compliance-rule pass rate: 100% (2/2 regulated profiles).**

Re-run `python3 scripts/compliance_check.py` (from a machine with the full stack installed) any time you want a fresh, live re-verification instead of relying on the P9 record.

## Validation Metrics — Final

| Metric | Target | Actual | 90% Credible Interval | Met? |
|---|---|---|---|---|
| Trust score (median) | ≥4/5 | 3/5 | — (ordinal, not a rate) | **No** |
| Net value (% yes) | ≥70% | 80% (4/5) | 42%–94% | Yes (point estimate; CI overlaps target) |
| Blueprint export rate | ≥40% | 50% (7/14) | 30%–70% | Yes (point estimate; CI overlaps target) |
| Compliance-rule pass rate | 100% | 100% (2/2 regulated profiles) | — (deterministic) | Yes |
| Avg. LLM latency | — (informational) | 1.51s (14 calls) | — | — |
| Sample size | 5–8 real testers | 14 sessions / 5 survey responses | *not powered for comparative claims — see note below* | — |

**Trust score misses target and is stated plainly, not reworded to sound like it passed:** median 3/5 against a ≥4/5 target.

## On sample size

These results are directional evidence from a handful of real sessions, not a statistically powered study. A claim like "testers trusted this more than manual research" would need a proper comparative study (with a control group and a pre-calculated required sample size) to state with statistical confidence — out of scope for a 2-person, 4-week capstone. What we can honestly claim is that these specific testers, using this specific prototype, gave these specific (reported with credible intervals) responses.

Two further honesty notes specific to this dataset:
- `data/telemetry.log` has no user identifier, so "14 completed sessions" and "5 survey responses" are not necessarily 14 and 5 distinct people — someone can submit the form multiple times in one sitting. The 5 survey responses are the best available proxy for distinct testers, since the survey is meant to be answered once per person.
- Card P.11 (real-user testing, this card's dependency) was still showing "In Progress" on the kanban board as of this week's research — this telemetry may represent partial rather than fully complete real-user testing. Worth confirming with the team before treating this as the final dataset.

## Scripts

- `scripts/telemetry_funnel.py` — trust-score median, avg time-to-results, avg LLM latency, and the 3-stage funnel.
- `scripts/credible_interval.py` — Beta-posterior 90% credible interval, run against net value and export rate.
- `scripts/compliance_check.py` — re-runs the real pipeline against every regulated profile and checks output against `GOVERNABLE_FOR_REGULATED`; needs the full ML/LLM stack to execute live.
