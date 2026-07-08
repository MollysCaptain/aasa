# Build Guide — Package, Roadmap & Pitch: Week 4

*Companion to the kanban board's cards P.14–P.21. This week turns a working prototype and a pile of test notes into a credible capstone submission: real numbers, honest limitations, and a rehearsed pitch.*

---

## Card P.14 — Compile final metrics from telemetry

**Depends on:** Card P.11 · **Owner:** Person A · **Day:** 22 (Week 4)

### Goal in plain language
Pull every number that actually matters out of `data/telemetry.log` and your survey responses into one clean, small report — this becomes both your "did the hypothesis hold up" evidence and the raw material for the pitch deck's results slide. At n=5-8, *how* you report these numbers matters as much as the numbers themselves — this card reports them as a funnel with honest small-sample framing, not as a set of independent percentages that imply more precision than 5-8 people can actually support.

### Concepts you need first
- **A funnel** reports a sequence of stages (viewed → exported → "would use this") instead of one aggregate number. It shows *where* trust breaks down, not just whether it does — someone who viewed the stack but never exported it tells you something different than someone who exported it but said "no" on the survey.
- **A credible interval** communicates uncertainty around a percentage. "% said yes" implies false precision at n=5-8 (one person flipping their answer swings it by ~15 percentage points); a credible interval like "60-90% likely, based on 6/8 responses" is the honest version of the same finding.

### Step-by-step

1. **Re-use the snippets already written in the Epic 3 guide** (`14-Build-Guide-Epic3-Blueprint-UI-v1.md`) for trust-score median, average time-to-results, and average LLM latency — run them now against your real Week-3 testing data, not test data.

2. **Compute the funnel** — three stages already logged as separate telemetry events, read together instead of independently:

```bash
python3 -c "
import json
from collections import Counter

events = [json.loads(line) for line in open('data/telemetry.log')]
counts = Counter(e['event'] for e in events)

viewed = counts.get('results_shown', 0)
exported = counts.get('export_clicked', 0)
surveys = [e for e in events if e['event'] == 'survey_submitted']
would_use = sum(1 for e in surveys if e.get('net_value') == 'Yes')

print(f'Funnel: {viewed} viewed a blueprint -> {exported} exported it '
      f'({100*exported/viewed:.0f}% of viewers) -> {would_use} said they\'d use it '
      f'({100*would_use/len(surveys):.0f}% of survey respondents)' if viewed and surveys else 'Not enough sessions yet.')
"
```

3. **Add a credible interval around the "would use this" percentage**, instead of reporting it as a bare number. With a small sample, a **Beta-posterior credible interval** (starting from an uninformative prior, Beta(1,1)) is the standard, honest way to express "here's the plausible range, given how little data we have":

```bash
pip install scipy
```

```python
"""
Card P.14 — Beta-posterior credible interval for a small-sample yes/no rate.
Run after real testing: python3 scripts/credible_interval.py
"""
from scipy import stats

def credible_interval(successes: int, total: int, credibility: float = 0.90):
    """
    Beta(1,1) is a uniform, uninformative prior — we're not assuming anything
    about the true rate before seeing data. Posterior after observing the
    data is Beta(1 + successes, 1 + failures); its interval is the honest
    range for the true rate, appropriately wide at small n.
    """
    failures = total - successes
    lower = stats.beta.ppf((1 - credibility) / 2, 1 + successes, 1 + failures)
    upper = stats.beta.ppf(1 - (1 - credibility) / 2, 1 + successes, 1 + failures)
    return lower, upper

# Example: 6 of 8 testers said "yes" to net value.
successes, total = 6, 8
point_estimate = successes / total
lower, upper = credible_interval(successes, total)
print(f"Net value: {point_estimate:.0%} said yes ({successes}/{total}), "
      f"90% credible interval: {lower:.0%}-{upper:.0%}")
```

Report it this way — "6/8 testers (90% credible interval: 36%-88%)" — rather than "75% said yes," which implies a precision the sample can't back up. Do the same for the export rate if you want to state it with the same rigor.

4. **State plainly what this sample size can't support.** Borrow the framing directly: a comparison (e.g. "recommendation format A performed better than B") needs a properly powered study to claim statistically; 5-8 sessions cannot support that kind of claim, only a directional trust/value read. Say so explicitly rather than letting a confident-sounding percentage imply otherwise:

```markdown
**On sample size:** these results are directional evidence from 5-8 real sessions,
not a statistically powered study. A claim like "testers trusted this more than
manual research" would need a proper comparative study (with a control group and
a pre-calculated required sample size) to state with statistical confidence —
out of scope for a 2-person, 4-week capstone. What we can honestly claim is that
these specific testers, using this specific prototype, gave these specific
(reported with credible intervals) responses.
```

5. **Compute the compliance-rule pass rate** — this one isn't from telemetry, it's from re-running your Card 2.5 privacy filter against every "regulated" test profile you used across Cards P.9–P.11, and checking none of them let a consumer-only tool through:

```bash
python3 -c "
from app.logic.filter import apply_privacy_filter, rank_tools_by_frequency, GOVERNABLE_FOR_REGULATED

# Paste in every regulated-posture test case you actually ran during P.9-P.11.
test_cases = [
    {'canonical_tools': ['chatgpt', 'azure-openai']},
    {'canonical_tools': ['gemini', 'ms-copilot']},
    # ... add every real regulated run you tested
]

filtered = apply_privacy_filter(test_cases, 'regulated')
ranked = rank_tools_by_frequency(filtered, top_n=10)
violations = [t for t in ranked if t not in GOVERNABLE_FOR_REGULATED]
pass_rate = 100 if not violations else 0
print(f'Compliance-rule pass rate: {pass_rate}% (violations: {violations or \"none\"})')
"
```

6. **Assemble one summary table** — this is the artifact this card actually produces:

```markdown
## Validation Metrics — Final

| Metric | Target | Actual | 90% Credible Interval | Met? |
|---|---|---|---|---|
| Trust score (median) | ≥4/5 | ___ | — (ordinal, not a rate) | ___ |
| Net value (% yes) | ≥70% | ___ | ___ – ___ | ___ |
| Blueprint export rate | ≥40% | ___ | ___ – ___ | ___ |
| Compliance-rule pass rate | 100% | ___ | — (deterministic, not sampled) | ___ |
| Avg. LLM latency | — (informational) | ___ s | — | — |
| Sample size | 5-8 real testers | ___ | *not powered for comparative claims — see note above* | — |
```

### How to verify this card is done
- Every row in the table above has a real, computed number — not a placeholder or an estimate.
- The funnel (viewed → exported → would-use) is reported as a sequence, not three independent stats.
- Both rate-based metrics (net value, export rate) carry a credible interval, not a bare percentage.
- The write-up includes the explicit "what this sample size can't support" statement.
- If any target was missed, that's written down plainly (e.g., "trust score 3.5/5, below target") rather than reworded to sound like it passed — this is the same honesty standard the whole reconciled document set is built on.

---

## Card P.15 — Freeze feature scope

**Depends on:** Card P.12 · **Owner:** Person B · **Day:** 22 (Week 4)

### Goal in plain language
Formally stop adding anything new. From this point, the only code changes allowed are fixes for things that are actually broken — not "one more small improvement." This single decision is what protects the rest of Week 4's packaging time.

### Step-by-step

1. **Open the kanban board together** and look at every card still in "To Do" or "In Progress."
2. **For each one, ask: is this a Must-Have that's broken, or a Should/Could-Have that's merely unfinished?** Move anything in the second category straight to the Icebox column — it's now explicitly out of scope for this submission, not "still in progress."
3. **Say the freeze out loud to each other and write it down** — e.g., a one-line note in your changelog: "Feature freeze declared [date]. Only critical-bug fixes permitted from here."
4. **If you have a mentor or bootcamp point of contact**, this is a reasonable moment to tell them where the project landed, especially if any Should-Have got cut — better they hear it from you now than notice it's simply missing later.

### How to verify this card is done
- The kanban board's "To Do"/"In Progress" columns contain only genuine bug-fix work, if anything.
- A dated freeze note exists.

---

## Card P.16 — Write up known limitations

**Depends on:** Card P.14 · **Owner:** Joint · **Day:** 23 (Week 4)

### Goal in plain language
Turn every gap you already know about into an honestly-labelled "Known Limitations / Roadmap" section — this is what separates a credible capstone from one that quietly hopes nobody asks hard questions.

### Step-by-step

1. **List every limitation you already know about** — you don't need to discover new ones, you need to write down what you've already learned while building:
   - Pricing is illustrative and manually curated, not live-synced (Card 2.3).
   - Privacy filtering is directional guidance, not a compliance certification (Card 2.5).
   - The dataset skews toward enterprise-productivity tools (Card P.8's model card).
   - There's no organisation-size join key in the case data — Org Size is a separate, user-stated taxonomy.
   - Validation sample size is 5–8 real testers, not a statistically representative study.
   - Any Minor issues deliberately deferred back in Card P.12.
2. **Write each one as: what it is → why it exists → what would fix it (roadmap item).** This structure shows judgement, not just a list of flaws.
3. **Put a visible version of this in the product itself** (a "Known limitations" note near the results, in plain language) — not just buried in a project document only graders will read.

### Template

```markdown
## Known Limitations

| Limitation | Why | Roadmap fix |
|---|---|---|
| Pricing is illustrative, not live | Manually curated 24-tool table (see Card 2.3) | Month 2: scheduled periodic sync against vendor pages |
| Privacy filter is directional, not certified | No governance authority backs the tool classification | Would need legal/compliance review, out of scope for a 2-person capstone |
| Dataset skews toward enterprise productivity tools | Reflects real-world case frequency in the source library | Document transparently (done — see model card); could diversify sources later |
| No org-size join to case data | Source dataset has no such field | Would require a different/joined dataset |
| Small sample validation (5-8 testers) | Realistic for a 2-person, 4-week team | Larger N in a post-capstone iteration. Rates are reported with credible intervals (Card P.14), and no comparative ("A beat B") claim is made, since that would require a properly powered study this team size/timeline can't run. |
```

### How to verify this card is done
- The table exists in a project doc AND a plain-language version is visible in the actual running app.

---

## Card P.17 — Draft the 10-slide pitch outline

**Depends on:** Card P.16 · **Owner:** Person B · **Day:** 24 (Week 4)

### Goal in plain language
Before touching slide design, decide what each slide is *for* in one sentence. An outline-first approach stops you from discovering on Day 27 that two slides say the same thing and a critical one is missing.

### Step-by-step

1. **Write the "so what" of each slide before any bullet points** — one sentence per slide describing the single point a viewer should walk away with.
2. **Use this 10-slide structure**, mapped to the Proposal's required sections (Problem → Solution → Architecture → Real Test Results → Risk Management → Roadmap):

```markdown
1. Title — project name, one-line value, both names.
2. Problem — the "Consultancy Gap": resource-constrained founders can't afford
   real AI-stack advice and default to scattered forum research.
3. Solution — ATSA in one sentence + a screenshot of the 3-block output.
4. How it works (Architecture) — the Card P.5 pipeline diagram.
5. Data foundation — 3,023 real deployments, the normalisation challenge (2,511 → 24 tools), honestly labelled as a retrieval corpus, not a compliance authority.
6. Real test results — the Card P.14 metrics table.
7. What we heard (qualitative) — 2-3 real, anonymised quotes from testing.
8. Risk management — the top 2-3 risks you actually mitigated (e.g. dropping Flowise to remove webhook risk; the privacy filter running before the LLM).
9. Known limitations & roadmap — the Card P.16 table, condensed.
10. Close / roadmap ask — what "Next" and "Future" look like (see 07-Roadmap-v2.md), and any specific ask (feedback, next steps).
```

3. **Write this outline as plain text first** (a markdown list, like above) — don't open a slide tool until both of you agree the outline is right.

### How to verify this card is done
- A one-sentence "so what" exists for every slide, and neither of you can point to two slides making the same point.

---

## Card P.18 — Prepare architecture & results slide content

**Depends on:** Card P.14 · **Owner:** Person A · **Day:** 24 (Week 4)

### Goal in plain language
Turn the outline's Slide 4 (Architecture) and Slide 6 (Real Test Results) into actual content — the diagram, the numbers, and the annotations that make them read clearly at a glance, without narration.

### Step-by-step

1. **Slide 4 — Architecture:** take the Mermaid diagram exported back in Card P.5 and add short (3–6 word) captions next to each stage explaining *why* it's built that way, not just what it does — e.g. "Filter before LLM → compliance is deterministic code, not a model guess."
2. **Slide 6 — Real Test Results:** take the metrics table from Card P.14 and turn it into a simple visual (a small bar per metric against its target line works well, or just a clean table — don't over-design this for a 2-person team's time budget). Keep the credible intervals on the slide, not just the point estimates — "6/8 said yes (90% CI: 36-88%)" reads as more credible to a technical audience than a bare "75%," and it pre-empts the obvious "isn't that a really small sample?" question in Q&A.
3. **Write the dataset stats you'll actually say out loud** — 3,023 cases, 2,511 raw tool-name variants normalised to ~24 canonical tools, ≥90% coverage — pull these from your own Card 2.1 terminal output, not from memory (numbers drift when people misremember them under pitch-day nerves).
4. **Hand both pieces to Person B** so they land in the deck before Card P.19's checklist.

### How to verify this card is done
- The architecture slide's diagram and captions exist as one exportable image or slide-ready content.
- The results slide's numbers are copy-pasted from your actual Card P.14 output, not retyped from memory.

---

## Card P.19 — Ethics: final responsible-AI checklist

**Depends on:** Card P.17 · **Owner:** Joint · **Day:** 26 (Week 4)

### Goal in plain language
This project's own history includes a first prototype with fabricated testimonials, fake certifications, and invented review counts — all removed in the v2 reconciliation. This card is the final, deliberate check that nothing like that has crept back in anywhere, including the new pitch deck.

### Step-by-step

1. **Go through the prototype AND the deck together**, checking each item below out loud — don't split this one up; a second set of eyes is the entire point.

```markdown
## Final Responsible-AI Checklist

- [ ] No fabricated testimonials, named customers, or review counts anywhere (product or deck).
- [ ] No fake certification badges (SOC 2, ISO 27001, "AWS/Google Partner," etc.).
- [ ] No invented press mentions or "featured in" claims.
- [ ] Every pricing figure shown carries an "illustrative / verify on vendor page" label.
- [ ] Every compliance/privacy claim uses "directionally suited to governable environments," never "certified compliant."
- [ ] Every real case reference's source URL actually works — click every single one and confirm the link is live.
- [ ] Deck metrics (Card P.14 table) match the actual telemetry numbers, not rounded-up or optimistic versions.
- [ ] Any deferred/known limitation is stated plainly in the deck, not omitted to look more finished.
```

2. **Click every source link** in your case references — this specific check catches a common, boring failure mode (a copy-paste typo in a URL) that undermines the entire "traceable evidence" pitch if a grader clicks a dead link.
3. **If you find anything**, fix it immediately — this checklist exists specifically to run right before rehearsal, with enough time left to correct issues.

### How to verify this card is done
- Every box above is checked, by both of you, together.

---

## Card P.20 — Pitch rehearsal

**Depends on:** Card P.19 · **Owner:** Joint · **Day:** 27 (Week 4)

### Goal in plain language
The first time you say your pitch out loud together should not be in front of the graders. A full, timed run-through surfaces awkward transitions, sections that run long, and facts you fumble under pressure — while you still have a day to fix it.

### Step-by-step

1. **Confirm your actual time limit** (check your bootcamp's capstone guidelines — don't assume; if unspecified, a 10-slide deck typically runs 8-10 minutes plus Q&A).
2. **Assign speaking sections** — a natural split is Person A on architecture/data/results (slides 4-6), Person B on problem/solution/roadmap (slides 1-3, 8-10) — but pick whatever plays to each person's strengths and comfort.
3. **Run through twice, fully timed, without stopping to fix things mid-run** — treat it like the real thing both times, note issues, fix them *between* runs, not during.
4. **Get one outside listener if at all possible** — a friend, another cohort member, anyone who hasn't seen the project — and ask them the same two questions afterward: "what was the actual solution, in your own words?" and "what confused you?" If they can't restate the solution accurately, that's a real signal about the deck, not the audience.
5. **Tighten to fit the time limit** — cutting content is normal and healthy; a rehearsed 9-minute pitch beats an unrehearsed 12-minute one every time.

### How to verify this card is done
- Two full timed run-throughs completed, both within the actual time limit.
- At least one piece of outside feedback gathered and acted on.

---

## Card P.21 — Final consistency pass & submit

**Depends on:** Card P.20 · **Owner:** Joint · **Day:** 28 (Week 4)

### Goal in plain language
The entire point of the Handbook v2 reconciliation was making sure no two documents in the submission contradict each other. This final pass confirms that's still true after a month of edits, and then actually submits the work.

### Step-by-step

1. **Walk through the Handbook's own document set table (§11)** as your checklist — for each file, do a quick skim asking "does anything in here contradict what we actually built or decided this week?" Pay special attention to numbers (effort estimates, coverage percentages, metric targets) that might have drifted from what actually happened.
2. **Specifically re-check these common drift points**:
   - Does the pitch deck's metrics slide match Card P.14's actual computed numbers?
   - Does the "known limitations" section match across the product UI, the docs, and the deck?
   - Do any docs still reference a feature that got cut during the Card P.15 freeze?
3. **Back up everything** — commit to a git repository if you're using one, or at minimum copy the whole project folder somewhere safe outside your working machine (a cloud drive, an external drive).
4. **Submit through whatever channel your bootcamp specifies**, and confirm receipt (a confirmation email, an LMS status change, or a direct message to your mentor) — don't consider this card done until you have positive confirmation the submission went through.

### How to verify this card is done
- Every document in the set has been skimmed this week, not just assumed to still be accurate.
- A backup of the full project exists outside your primary working machine.
- You have explicit confirmation the submission was received.

---

## Week 4 — Done Checklist
- [ ] Final metrics table compiled with real numbers.
- [ ] Feature freeze declared and logged.
- [ ] Known Limitations table written and visible in-product.
- [ ] 10-slide pitch outline agreed before any slide design started.
- [ ] Architecture and results slide content prepared from real diagrams/numbers.
- [ ] Final responsible-AI checklist fully passed, including every source link clicked.
- [ ] Two full timed rehearsals completed, plus outside feedback.
- [ ] Final consistency pass done and submission confirmed.

**This completes all 21 PM, Ethics & Pitch cards** — combined with the 14 build cards from Epics 1–3, every card on the kanban board now has a step-by-step path from "no prior knowledge" to "done."
