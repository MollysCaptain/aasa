# 📑 Schema – AI Use Cases Library

This file defines the schema for `data/use-cases.csv` (downloaded separately — see
[`13-Build-Guide-Epic2-Retrieval-v1.md`](../../Capstone%20Plan/Build%20Guide/13-Build-Guide-Epic2-Retrieval-v1.md)
for the source, license, and citation).

**Verified against the actual v2.0 dataset (3,023 cases, updated January 2026)
via `pd.read_csv('data/use-cases.csv').columns`** — not against the upstream
repo's own `data/schema.md`, which still describes an older version of the
file and is out of date on two points (see the correction notes below).

---

## Columns & Definitions

| Column | Description | Example |
|---|---|---|
| **CaseID** | Unique identifier for the use case. Format: `aicase-00001`–`aicase-99999` (final/in-review, 5-digit), `aicase-x0001`–`aicase-x9999` (excluded, 4-digit). Enforced locally by `CASEID_PATTERN` in [`scripts/validate_use_cases.py`](../../scripts/validate_use_cases.py) — there's no local copy of upstream's `CASEID_POLICY.md`, so that script is the source of truth in this repo. | `aicase-01542` |
| **Organization** | Name of the company, institution, or entity implementing AI. | `Siemens Energy` |
| **Use Case Title** | Concise, descriptive title (not marketing language). | `AI-powered inspection with NVIDIA Triton` |
| **Description** | Short summary of the problem, solution, and outcome. | `Siemens used NVIDIA Triton for computer vision to automate safety inspections.` |
| **Org Industry** | The industry of the organization (not vendor). | `Energy & Utilities` |
| **Use Case Industry** | The primary industry impacted by the use case (can differ from Org Industry if cross-sector). | `Manufacturing` |
| **Subindustry Tags** | Optional tags to refine the industry (comma-separated). | `Hospitals, MedTech` |
| **Use Case Domain** | The functional domain where AI is applied. Must match the 18 canonical domains in [`data/domain_mapping.json`](../domain_mapping.json) — there's no local copy of upstream's `docs/taxonomy.md`, so that mapping (built from the raw values actually seen in the dataset) is what this project validates against. | `Operations & Supply Chain` |
| **Tool/Technology** | **Singular column name** — the dataset's own `data/schema.md` still says `Tools/Technologies` (plural), but the real column is singular. AI models, APIs, platforms, frameworks, or infrastructure used. **Semicolon-delimited**, not comma-delimited (e.g. `"OpenAI's Whisper API ; GPT-4 ; GPT-4 Vision"`). | `NVIDIA Triton Inference Server ; TensorFlow` |
| **Outcomes & Benefits** | Tangible results or advantages. In practice this is **bullet-pointed prose** (`•`-prefixed lines), not a short semicolon-separated tag list as the upstream doc implies. | `• Cost Reduction — cut inspection labor by 40%` |
| **Source URL** | Direct link to the original case study / reference. | `https://www.nvidia.com/en-us/customer-stories/siemens-energy-simplifies-safety-inspections/` |
| **Source (Publisher)** | Who published the case study — e.g. the vendor's own blog (`Microsoft`, `AWS`, `Google`), not the organization the case is about. **Missing entirely from the upstream `data/schema.md`**; confirmed via the upstream README's "Note on Vendor Presence" section, which distinguishes `Tool/Technology` mentions (vendor products used) from `Source (Publisher)` (who wrote up the case). | `NVIDIA` |

---

## Formatting Rules
- **Consistency**: Use sentence case for titles and descriptions.
- **No hype**: Avoid marketing language like "revolutionary" or "cutting-edge."
- **Domain taxonomy**: Use the canonical domains in `data/domain_mapping.json` for `Use Case Domain`. There's no local, enforced taxonomy for `Org Industry` / `Use Case Industry` / `Subindustry Tags` — those are free text in the raw data.
- **Multiple values**: `Subindustry Tags` — comma-separated. `Tool/Technology` — semicolon-separated. `Outcomes & Benefits` — bullet-pointed lines, not comma/semicolon tags.
- **URLs**: Must be valid and publicly accessible.

---

## File Variants

Only the final dataset is used in this project:
- `data/use-cases.csv` → the 3,023-case final dataset (gitignored — download your own copy per the citation note in the build guide, don't commit it here).

Upstream also publishes `in-review/` (78 cases) and `excluded/` (720 cases) datasets for background on the curation process, but neither is used or present in this repo.

---

## Notes
- Each case should be **self-contained** (no missing critical fields). Upstream reports 99.97% completeness across the 3,023 cases.
- This file was originally hand-copied from the upstream repo's `data/schema.md` and inherited its errors (`Tools/Technologies` plural, no `Source` column). Both are corrected above after re-verifying directly against the real CSV — see `23-Gabi-Branch-Epic2-Verified-v1.md` for the fuller writeup of how the error was found.
- If you ever pull a fresh copy of the dataset and something looks different, re-verify with `print(pd.read_csv('data/use-cases.csv').columns)` rather than trusting this file (or upstream's own docs) blindly.

---

## License & Citation

Released under MIT and CC-BY-4.0. Free to use, share, and adapt with attribution:

```
AI Use Cases Library. (2026).
Retrieved from https://github.com/abbasmahdi-ai/ai-use-cases-library
```
