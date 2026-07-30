# P.14 — Compile Final Metrics from Telemetry — Results

*Rewritten 2026-07-28 after the final real-user round (8 participants). Every
figure below is computed from `data/telemetry.log`, not transcribed from the
session notes. Reproduce all of it with:*

```bash
python3 scripts/telemetry_funnel.py   --since "2026-07-27 23:00" --until "2026-07-28 01:31"
python3 scripts/credible_interval.py  --since "2026-07-27 23:00" --until "2026-07-28 01:31"
```

Participant details are recorded in
`PM & Ethics/AI-Assisted Stack Architect User Testing (pseudonymised).xlsx`.

> **Note on participant privacy.** Participants agreed to test the product, not to
> be named in a submitted document, so the committed record uses **P1–P8** and
> withholds employer names. The unredacted sheet is held locally by the team and is
> git-ignored. This is **pseudonymisation, not anonymisation** — the free-text
> requirement comments describe each participant's business context closely enough
> that someone who knows the team could plausibly re-identify individuals. They are
> kept because they are the substance of the feedback; the residual risk is stated
> rather than hidden. Nothing in the analysis depends on identity: the telemetry
> cross-check below runs on trust scores and ordering alone.

## Why the numbers are windowed

`data/telemetry.log` is append-only and covers the whole project — our own
development runs, three earlier partial rounds, and the final round — across
several different builds. A bare run of the scripts reports **18 survey
responses over 106 sessions**, which measures nothing cleanly: it averages
feedback on the shipped build together with feedback on builds that had known
defects, and it counts our own testing as if it were user testing.

The `--since "2026-07-27 23:00" --until "2026-07-28 01:31"` window isolates the
final round. **Both bounds are required** — run the shorthand `--p14` and you
cannot get it wrong.

### Why the end bound is not optional

The round closed with its last survey at **01:30:41**. We then carried on using
the app — verifying fixes, reproducing a reported bug, testing the Cloud deploy —
and each of those runs appended a `results_shown` event. Since `export_clicked`
stayed at 10 while `results_shown` climbed from 12 to 18, the export rate the
scripts reported fell from **83% to 56% within a day of this document being
written**, with no survey attached to a single one of the new events.

The published figures were never wrong. What broke was reproducibility: for a
while this file quoted a `--since`-only command that no longer produced the
numbers printed beneath it. **Found by Gabi on 2026-07-28** by running the
documented command instead of trusting the write-up — which is exactly how it
should have been caught, and a reminder that "verified" means nothing unless the
stated command is the one that was verified.

Both scripts now refuse to be quiet about it: any run that isn't the published
window prints a warning naming how many post-round events it just folded in.

### Why the boundaries are defensible rather than arbitrary

1. **Every survey inside the window maps to one recorded participant**, in order, with
   no gaps and no extras (cross-check below). Eight events, eight people.
2. **The start bound doesn't change any published figure.** The last event before
   it is a `form_start` at 22:41 and the first inside is a `form_start` at 23:06
   — only 25 minutes apart, so the cutoff was worth stress-testing. Moving it back
   an hour to 22:00 gives *identical* `results_shown` (12), `export_clicked` (10)
   and `survey_submitted` (8) counts; only the raw `form_start` count moves
   (15 → 17), and no reported metric is derived from it. The two extra
   `form_start` events produced no `results_shown` at all, consistent with
   restarting the app after the UI changes deployed rather than a test session.
3. **The end bound sits one minute after the final survey**, so it captures every
   participant action and nothing that came after. The 16 excluded events contain
   **zero surveys** — that is development traffic, not testing.

The previous survey before this round was at 18:32, over five hours earlier.

## The final round — 8 real participants

```
[3, 4, 4, 5, 5, 5, 5, 5] -> trust-score median: 5 (8 responses)
12 completed sessions, avg time to results: 372.3s
LLM: avg 1.34s over 12 calls (min 0.57, max 2.62)
Funnel: 12 viewed -> 10 exported (83% of viewers) -> 8 survey responses,
        8 said they'd use it (100% of respondents)

Net value:             100% (8/8),  90% credible interval: 72%-99%
Blueprint export rate:  83% (10/12), 90% credible interval: 59%-93%
```

### Time-to-results: report the median, not the mean

The script prints the mean, which is the misleading figure here. Both, so the
reader can judge:

| Statistic | Value | |
|---|---|---|
| **Median** | **114s (1.9 min)** | what a typical session took |
| Mean | 372s (6.2 min) | inflated by three long sessions |
| Outliers | 576s, 1,287s and 1,617s | participant opened the form, returned later |
| Range | 58s – 1,617s | |

*Corrected 2026-07-30 (P.22): the two long sessions were quoted as 1,287s and
1,618s. The true values are 1,286.6s and 1,616.8s, so the second rounds to
**1,617**, and there is a **third** session over 500s (576.7s) that the "two
outliers" wording did not account for. Recomputed straight from the 12 windowed
`elapsed_seconds` values.*

The distribution is heavily right-skewed at n=12, so the mean describes nobody.
**The product's `~2 min TO BLUEPRINT` hero stat is the median**, which is the
correct statistic for a typical-user claim — and it is stated here alongside the
mean rather than in place of it.

This is worth flagging because we briefly got it wrong in the other direction: a
consistency pass compared the hero against the *mean*, called it an over-claim,
and the number was changed to "~5 min" — which matched neither statistic. Reverted
2026-07-28. See P.21 finding 2.

### Provenance — every response ties to one recorded participant

Trust scores in the spreadsheet match the telemetry events **in order**, with no
gaps and no extras. This is the check that makes the dataset auditable rather
than asserted:

| # | Participant | Role | Telemetry `trust_score` | Time |
|---|---|---|---|---|
| 1 | P1 | Head of Customer Success | 5 | 23:45:31 |
| 2 | P2 | Head of Global IT | 5 | 00:40:15 |
| 3 | P3 | IT Technology Specialist | 4 | 00:43:50 |
| 4 | P4 | Talent Acquisition Lead | 5 | 00:48:32 |
| 5 | P5 | Senior Customer Success Manager | 4 | 00:52:02 |
| 6 | P6 | Recruiter | 3 | 01:02:00 |
| 7 | P7 | Software Test Developer | 5 | 01:14:13 |
| 8 | P8 | Customer Feedback Specialist | 5 | 01:30:41 |

**8 survey events in the window, 8 participants, all aligned.** Card P.11's
requirement — *"real `survey_submitted` entries with actual `trust_score` values
from real people, not test data"* — is satisfied and independently checkable.

### Who the participants were

Drawn from the recorded session sheet, because who tested matters as much as the
scores:

- **Organisations:** 7 real companies across payments, music rights, HR tech, coaching, food delivery, e-commerce parts and climate software — none of them ours. Named employers are withheld (see the note below).
- **Seniority:** 3 heads of function, 5 specialist/IC roles.
- **Org-size bands exercised:** Start-up, Small-Medium Business, Mid-Market (×2), Enterprise (×4).
- **Privacy posture:** 5 regulated, 3 standard.
- **Budgets:** €300 to €20,000/month.
- **Workflows:** Sales, IT & Platform, Data & Analytics, HR (×2), CX & Personalization, R&D & Engineering, Customer Service.
- **Vendor exclusions:** used by 8 of 8 — every participant excluded at least one vendor, which is the first real evidence that B.5 matters to users rather than being a nice-to-have.
- **Non-native English speakers: 5 of 8** (P1, P4, P6, P7, P8).

That last point closes a gap we had previously written up as unmet: Card P.13
asked for at least one non-native English speaker, and this round had five, in
real working conditions rather than simulated.

## Validation Metrics — Final

| Metric | Target | Actual | 90% Credible Interval | Met? |
|---|---|---|---|---|
| Trust score (median) | ≥4/5 | **5/5** | — (ordinal, not a rate) | **Yes** |
| Net value (% yes) | ≥70% | **100% (8/8)** | 72%–99% | Yes |
| Blueprint export rate | ≥40% | **83% (10/12)** | 59%–93% | Yes |
| Compliance-rule pass rate | 100% | 100% (2/2 regulated profiles) | — (deterministic) | Yes |
| Avg. LLM latency | — (informational) | 1.34s (12 calls) | — | — |
| Sample size | 5–8 real testers | 8 participants / 12 sessions | *not powered for comparative claims* | Yes |

**All four targets are met.** That is a genuine result and also the claim most
likely to be challenged, so the next two sections say plainly what it does and
does not support.

## The trust score went from 3/5 to 5/5 — why, honestly

The previously published figure was a median of **3/5 against a ≥4/5 target,
recorded as a miss**. It is now 5/5. Two things changed at once, and we cannot
separate their contributions:

1. **The build changed.** The earlier round tested a version that, among other
   things, announced *"N real \<industry\> \<workflow\> deployments matched"* for
   input combinations with no matching cases at all (corrected 2026-07-27, see
   Build Guide 35), had no relevance cutoff, ordered the case list without
   explaining unmatched cases, and used org-size bands testers told us they
   didn't fit.
2. **The people changed.** Different participants, recruited differently.

So this is **not** a measured before/after improvement, and we do not present it
as one. Claiming "our fixes raised trust from 3 to 5" would require the same
people testing both builds, which did not happen. What we can say: the earlier
round surfaced specific defects, those defects were fixed and the fixes are
individually documented and dated, and the participants who tested the fixed
build reported high trust.

## On sample size and recruitment

Directional evidence from 8 real sessions, not a statistically powered study.

- **Credible intervals are the honest reading.** Net value is 100% (8/8) but its
  90% interval runs 72%–99% — a single "No" would move the point estimate 12.5
  points. Export rate's interval spans 59%–93%. Report the intervals, not the
  point estimates alone.
- **Recruitment bias is real and undisclosed nowhere else, so it is stated
  here:** all 8 participants are professional contacts of the team. They had no
  incentive to be harsh, and two work at the same employer as each other. This is
  convenience sampling, and a friendly sample plausibly inflates trust scores.
  A neutral round would need recruits with no relationship to us.
- **No comparative claim.** "Testers trusted this more than manual research"
  needs a control group and a pre-calculated sample size. Out of scope, and not
  asserted anywhere in the submission.
- **Sessions ≠ people, still.** Telemetry has no user identifier by deliberate
  privacy choice (Card P.4), so the 12 `results_shown` events are not 12 distinct
  people — several participants generated more than one blueprint. The **8
  survey responses** are the reliable participant count here, and unusually for
  this project they are independently corroborated by the session sheet.
- **The 10 exports came from 9 sessions, not 10.** Added 2026-07-30 (P.22). Two
  `export_clicked` events sit 2 seconds apart in one session (01:30:35 and
  01:30:37) — a double-click, not two decisions. The 83% headline is arithmetically
  correct as an event count (10 exports / 12 views) and is left as published, but
  measured as *sessions that exported* it is 9/12 = **75%**. The "sessions ≠
  people" caveat below was previously applied only to the denominator; applying it
  to the numerator too is the honest treatment, and 75% still clears the ≥40%
  target comfortably.
- **One session generated no survey.** Between 00:52:48 and 00:55:35 a session
  generated, saved, exported and downloaded a PDF without submitting the survey.
  It is counted in the 12 viewed and the 10 exported, and not in the 8 responses
  — which is the correct treatment, and is why export rate is measured against
  viewers rather than respondents.

## Compliance-rule pass rate

`scripts/compliance_check.py` re-runs the real pipeline (`app.pipeline.run_pipeline`
→ Card 2.5's `apply_privacy_filter` + `rank_tools_by_frequency`) for every
regulated-posture profile tested, and checks the output against the full
`GOVERNABLE_FOR_REGULATED` allowlist — stricter than `backend_dry_run.py`'s own
sanity check, which only tests against a narrow `CONSUMER_ONLY_IDS = {"gemini"}`
proxy set.

**Note on how this was verified:** the script needs the same ML infra as
`backend_dry_run.py` (a populated `chroma_store`, the `all-MiniLM-L6-v2` model,
`GROQ_API_KEY`) to call the live pipeline. This result is drawn from
`P9-Backend-Dry-Run-Results-v1.md`'s already-committed output — the real
pipeline's actual recorded result for these exact regulated queries —
cross-checked against the current, full `GOVERNABLE_FOR_REGULATED` set:

| Profile | Recommended stack | Violations |
|---|---|---|
| Profile 2 — Healthcare/ent/regulated | aws-bedrock, aws-platform, google-cloud, ibm-watsonx, ms-dynamics | none |
| Profile 3 — Agriculture/solo/regulated | azure-platform, aws-platform, azure-openai, aws-bedrock, google-cloud | none |

**Compliance-rule pass rate: 100% (2/2 regulated profiles).**

Worth noting that **5 of the 8 participants chose the regulated posture**, so the
compliance path was exercised far more heavily by real users than by our own dry
run. Those live runs were not individually checked against the allowlist —
`compliance_check.py` covers the two recorded profiles only, and that is the
scope of the 100% claim.

## Superseded: the earlier round (n=5)

Kept rather than deleted, because the earlier numbers appear in committed
documents and the record should show what changed:

| Metric | Earlier round (n=5, earlier build) | Final round (n=8, submitted build) |
|---|---|---|
| Trust median | 3/5 — **missed** ≥4/5 | 5/5 — met |
| Net value | 80% (4/5), CI 42%–94% | 100% (8/8), CI 72%–99% |
| Export rate | 50% (7/14), CI 30%–70% | 83% (10/12), CI 59%–93% |
| Avg. LLM latency | 1.51s (14 calls) | 1.34s (12 calls) |

The two rounds are **not pooled.** Pooling would average feedback across builds
with materially different behaviour and would bury the earlier miss. The final
round is the headline because it is the build being submitted; the earlier round
is the reason several of the fixes exist.

## Scripts

**Three** scripts read `data/telemetry.log`, and all three need `--p14` to
reproduce anything published here. `--since` on its own is **not** enough — see
"Why the end bound is not optional" above.

- `scripts/telemetry_funnel.py --p14` — trust-score median, avg time-to-results, avg LLM latency, 3-stage funnel.
- `scripts/credible_interval.py --p14` — Beta(1,1)-posterior 90% credible interval for net value and export rate.
- `scripts/validation_metrics_table.py --p14` — regenerates the whole table at the top of this document in one command.
- `scripts/compliance_check.py` — re-runs the real pipeline against every regulated profile and checks output against `GOVERNABLE_FOR_REGULATED`; needs the full ML/LLM stack to execute live. Reads no telemetry, so no window applies.

*Fixed 2026-07-30 (P.22): this section listed two log-reading scripts and
described `--since` as sufficient. `validation_metrics_table.py` was missing
from the list entirely **and** had no window support at all — it called
`load_events()` bare, so the one command the README advertises as regenerating
"the whole P.14 results table" silently produced a different table (23% export,
94% net value, 4/5 trust, 106 sessions). It now takes `--since/--until/--p14`
and warns on an unbounded run like the other two, and `--p14` reproduces this
document's table exactly.*

*Fixed while writing this up:* `telemetry_funnel.py`'s median was
`scores[len(scores)//2]`, which returns the upper of the two middle values at
even n rather than the median. It agreed with the true median at n=5 and at this
round's n=8 (both middle values are 5), so no published figure was ever wrong —
but it would have been the first time the two middles differed.
