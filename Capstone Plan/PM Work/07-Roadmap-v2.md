# Post-Pivot Product Roadmap (v2)
*Supersedes the original Roadmap. Fixes: replaces the Flowise-based pipeline with the simplified Python/Chroma stack; corrects claims about live pricing/scraping to match what's actually feasible; keeps ambition in the roadmap rather than the MVP promise.*

## NOW (Weeks 1–3): The Core Validation MVP
- **Guided AI Intake Form:** Streamlit UI capturing organisation size, industry, target workflow, privacy posture, and budget.
- **Retrieval & Matching Engine:** a Python pipeline (Chroma vector store, no external orchestration tool) performing semantic search over the 3,023-case library, normalised tool names, and a hardcoded 24-tool pricing table.
- **3-Block Results Display:** matched AI stack, illustrative cost forecast, real case references with source links.
- **Telemetry & Micro-Surveys:** completion velocity, blueprint export/copy rate, and a post-session trust score.

## NEXT (Month 2): Trust, Freshness & Developer Utility
- **Dynamic Pricing Sync:** move from the hardcoded table to scheduled pricing checks against vendor pages (not real-time scraping — vendor pricing pages change infrequently enough that a periodic sync is sufficient and lower-risk).
- **Plain-Language Financial Export:** a downloadable one-page cost summary a non-technical founder can share with their board.
- **Mainstream Validation Overlay:** population-level Stack Overflow survey benchmarks as supporting context (e.g. "X% of similarly-sized companies report using Y") — explicitly labelled as population-level, not case-specific, since the case library has no org-size join key. The concrete asset for this already exists: the colleague's `stackpunk`/`Gabi` branch built `data/technology_landscape.csv` (2,017 rows, top-5 tools per Industry x OrgSize group from the real 2025 Stack Overflow Developer Survey, via `scripts/extract_tech_landscape.py`) — confirmed in `19-Gabi-Branch-Integration-Analysis-v1.md` as a Month 2 item, not MVP scope. Whoever picks this up will still need to build a mapping layer between the survey's own Industry/OrgSize categories and this app's taxonomy before joining it to case-library output.
- **One-Click Code Boilerplate:** generates starter config for the recommended stack.

## FUTURE (Month 3+): System Autonomy & Ecosystem Expansion
- **Autonomous Data Pipeline:** scheduled ingestion of new open-source AI use cases into the vector store.
- **Full Stack Expansion:** reintroducing general infrastructure logic (databases, hosting, compute) — explicitly **not** in the capstone MVP, added here as the honest long-term vision our original Pitch conflated with the 4-week scope.
- **Skill-Gap Testing:** a module comparing a team's existing familiarity against a recommended stack to flag adoption risk.

## What changed from v1
Every Flowise reference has been replaced with the simplified Python/Chroma pipeline (see Proposal & Scope v2). The "dynamic pricing" NEXT item is now scoped as periodic sync rather than live scraping, since our effort matrix already correctly flagged continuous scraping as too complex for this team size — this roadmap now agrees with that call instead of contradicting it.
