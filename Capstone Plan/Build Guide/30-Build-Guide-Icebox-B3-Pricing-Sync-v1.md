# Build Guide 30 — Icebox B.3: Pricing sync (design sketch — NOT a sprint task)

*Icebox card `stackpunk #40` · Priority: **🚫 WON'T HAVE (board label — deliberate)** · Estimated effort: **4d+ even in reduced form** · Rank: **7 of 7 (hardest)***

*Read this doc as a design sketch, not a to-do. "Live/continuous pricing scraping" was scoped out in the Effort-Informed Prioritisation Matrix ("unnecessary complexity; a manually curated table is sufficient and honestly labelled illustrative") and the Roadmap v2 explicitly re-scoped the NEXT-phase version down to **periodic sync** — vendor pricing pages change infrequently enough that scheduled checks beat real-time scraping on every axis: effort, fragility, and honesty. This guide documents that periodic-sync design so it's ready if the project continues past the capstone. If someone is tempted to build this during the final 2 weeks: don't — guides 24–27 all deliver more user value per day.*

---

## Why not live scraping (for the record)

1. **Fragility**: 41 tools ≈ 30+ distinct vendor pricing pages, each a differently-structured, frequently-redesigned marketing page. Parsers rot in weeks.
2. **Wrong problem**: our pricing is *deliberately* labelled illustrative everywhere (Block B, exports, methodology block). Real-time precision would invite users to treat it as quotable — the opposite of the product's honesty posture.
3. **Effort**: the 4d+ matrix estimate assumed a handful of vendors; at 41 tools it's worse.

## The design that would actually work (periodic sync)

### Architecture

```
GitHub Action (cron: weekly)
  └─ scripts/pricing_sync.py
       ├─ for each tool in PRICE_SOURCES: fetch pricing page (plain GET, no JS)
       ├─ extract candidate prices (regex per source, NOT DOM parsing)
       ├─ diff against app/logic/pricing.py current values
       └─ write pricing_sync_report.md + open a PR / issue if drift detected
Human (Ash or Gabi)
  └─ reviews the diff, updates pricing.py BY HAND, commits
```

The human stays in the loop on purpose: the deliverable is a **drift report**, not an auto-updating table. Auto-writing `pricing.py` from scraped text is how a parsing glitch becomes a €0.00/mo recommendation in production.

### Components

1. **`PRICE_SOURCES` registry** (new `scripts/pricing_sources.py`): per tool id — pricing-page URL, a regex or two for the expected price pattern, and the unit it should match (`in_ppm`/`out_ppm`/`seat_pm`). Start with the ~13 token+seat tools that actually drive `estimate_cost()`; compute/free tools don't need sync at all.
2. **`scripts/pricing_sync.py`**: fetch → extract → compare with a tolerance (flag only >5% drift or extraction failure) → emit markdown report listing: tool, stored value, found value, page URL, action needed. Extraction failures are report lines, never crashes.
3. **Scheduler**: GitHub Actions cron (weekly, Monday morning) committing the report to `data/pricing_sync/` and opening an issue when non-empty. No server, no infra cost.
4. **`pricing.py` provenance**: add a `"verified"` date field per entry (e.g. `"verified": "2026-07"`) so the app can honestly caption how fresh each price is — cheap to add now, valuable independent of sync ever existing.

### The one piece worth doing THIS sprint (~1 hour, optional)

Item 4 alone: add `verified` dates to the 13 token/seat entries in `PRICING` and render "prices last verified 2026-07" in Block B's caption. Zero scraping, immediate honesty win, and it's the foundation the sync design plugs into later.

## If someone builds it anyway — gotchas

- Respect robots.txt and rate-limit (one request/vendor/run; it's weekly, this is trivially polite).
- Several vendors (AWS, Azure, GCP) publish machine-readable price lists/APIs — for those, use the API and skip HTML entirely; the regex approach is only for SaaS marketing pages.
- Prices are region/currency-dependent — our table is EUR-denominated with USD sources in places; the sync must compare like-for-like or every run flags false drift. Record the currency assumption per source in the registry.
- Never let the Action modify `app/` — report-only, PR-gated, human-merged.

## Verification checklist (for the future implementer)

- [ ] Dry-run the sync script locally against 3 sources; report reads correctly for: match, drift, extraction failure.
- [ ] Action runs green on cron and on manual dispatch; issue opens only on non-empty drift.
- [ ] `pricing.py` untouched by automation in all cases.
- [ ] Card #40 stays Won't Have for the capstone; if the "verified date" mini-item ships, note it on the card rather than moving it.
