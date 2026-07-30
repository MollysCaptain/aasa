# Outcome Goals (v2)
*Supersedes the original. Fix: the "Teachable" bullet named Flowise specifically as the learning tool, contradicting the decision (Proposal & Scope v2) to drop Flowise in favour of a plain Python + Chroma pipeline. Corrected below — no other change needed, as the outcome target itself was already sound.*

## Outcome & Learning Goal
In 3 weeks, startup founders and SMB product managers will receive automated, data-backed AI application stack blueprints, resulting in over 75% rating the recommendations as more trustworthy and cost-transparent than manual forum research. In the same time, our team will learn to parse, normalise, embed, and query a real-world 3,023-case knowledge base, hybridised with a hand-built pricing table that correctly distinguishes per-seat and per-token pricing, using a lightweight Python + local vector-store pipeline (no low-code orchestration platform).

## Breakdown Checklist
- **Time-bound:** Explicitly set for a 3-week build-and-test sprint within the 4-week timeline.
- **User-focused:** Targets resource-constrained founders and product leads stuck in the "Consultancy Gap".
- **Measurable:** Aiming for a verifiable trust threshold of >75%, assessed against 5–8 real test users (corrected — see Proposal & Scope v2 for why the original N=50/N=12 targets weren't realistic for a 2-person, 4-week team).

> **How this target was actually measured — added 2026-07-30 (P.22).** The ">75%
> rating the recommendations as more trustworthy" wording above was written before
> the survey instrument existed, and **no document reports a 75% figure**, because
> that is not what we ended up measuring. The shipped micro-survey asks for a
> 1–5 trust rating, so the operational target became **median ≥ 4/5** — which is
> what the Charter, the Handbook and the P.14 results table all use, and what
> `scripts/validation_metrics_table.py` evaluates. The final round returned a
> median of **5/5** (n=8).
>
> Recording this rather than quietly rewriting the goal: a reader checking the
> success criteria against the results would otherwise find a target with no
> result against it. The equivalent restatement is that **7 of 8** respondents
> rated trust ≥4/5 (**88%**), which does clear >75% — but the median is the figure
> we report, because at n=8 a percentage implies precision we do not have.
> `03b-User-Research-v2.md` and `08-Effort-Informed-Prioritisation-v2.md` carry
> the same ">75%" phrasing and should be read against this note.
- **Teachable:** Focuses on the core engineering skills required to clean and normalise a messy real-world taxonomy (2,511 raw tool strings → 41 canonical tools), tune vector retrieval, and enforce deterministic rules ahead of an LLM call — **using plain Python and a local Chroma vector store, not Flowise.**
