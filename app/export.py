"""
Card 3.2 — Turn the blueprint dict into a plain-text block the user can copy.
Icebox B.8 (Build Guide 34) adds a PDF render of the same content.
"""
from app.logic.pricing import PRICING

# B.8 — character handling for the PDF path. Switched from fpdf2 to reportlab
# (2026-07-27); reportlab needs far less replacing, verified by rendering:
#   - It draws "—", "–", "·", "•", "✓" and "→" correctly (fpdf2 raised on all
#     of those except "·"), so they're left alone.
#   - Its base-14 Courier/Helvetica metrics have NO Euro glyph, so "€" is
#     silently DROPPED — worse than an error, because a cost line would read
#     "Primary API: 875.00/mo". Hence "€" -> "EUR ".
#   - Codepoints it can't map render as a black box (seen with the U+2011
#     non-breaking hyphen the LLM summary sometimes emits), so those are mapped.
# Applied to the PDF path ONLY — the on-screen copy block, the .md export and
# the saved JSON keep the original characters.
_PDF_CHAR_MAP = {
    "€": "EUR ",
    "‑": "-",              # U+2011 non-breaking hyphen -> black box in reportlab
    "≪": "<<", "≫": ">>",
    "⚠": "!",
}


def _pdf_safe(text: str) -> str:
    """Replace only the characters reportlab's standard fonts can't draw."""
    for bad, good in _PDF_CHAR_MAP.items():
        text = text.replace(bad, good)
    return text


def blueprint_to_text(result: dict) -> str:
    # B.5 (Build Guide 24) — echo the optional project name in the header.
    if result.get("project_name"):
        lines = [f"=== AASA Blueprint — {result['project_name']} ===", ""]
    else:
        lines = ["=== AI-Assisted Stack Architect — Blueprint ===", ""]

    lines.append("RECOMMENDED STACK:")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"  {rank}. {label}")
    lines.append("")

    cost = result["cost_forecast"]
    lines.append("COST FORECAST (illustrative):")
    if cost.get("primary_api") and cost["primary_api"].get("monthly_eur") is not None:
        lines.append(f"  Primary API: €{cost['primary_api']['monthly_eur']:.2f}/mo")
    if cost.get("assistant") and cost["assistant"].get("monthly_eur") is not None:
        lines.append(f"  Assistant:   €{cost['assistant']['monthly_eur']:.2f}/mo")
    lines.append(f"  ({cost.get('disclaimer', '')})")
    lines.append("")

    lines.append("REAL CASE REFERENCES:")
    for case in result["matched_cases"][:4]:
        org = case.get("organization", "Unknown organisation")
        url = case.get("source_url", "")
        lines.append(f"  - {org} ({url})")
    lines.append("")

    lines.append("SUMMARY:")
    lines.append(result.get("summary_text", ""))

    return "\n".join(lines)


def blueprint_to_markdown(result: dict) -> str:
    """Icebox B.1 (Build Guide 26) — board-ready plain-language one-pager.
    Deliberately non-technical: no tool ids, no token math, no jargon.
    Audience is the 'Visionary Outsider' persona — a non-technical CEO
    forwarding this to their board unedited."""
    cost = result["cost_forecast"]
    name = result.get("project_name") or "AI stack proposal"
    lines = [f"# {name}", ""]

    lines.append("## What we recommend")
    for rank, tool_id in enumerate(result["recommended_stack"], start=1):
        label = PRICING.get(tool_id, {}).get("label", tool_id)
        lines.append(f"{rank}. **{label}**")
    lines.append("")

    lines.append("## What it costs (illustrative)")
    total = cost.get("total_monthly_eur")
    if total is not None:
        lines.append(f"Estimated **€{total:,.0f} per month** across the core services.")
    else:
        lines.append("Costs for this stack are usage-based — there is no fixed "
                     "monthly figure to quote. Budget against actual usage.")
    if cost.get("budget") is not None and cost.get("within_budget") is not None:
        if cost["within_budget"]:
            lines.append(f"This fits the stated budget of €{cost['budget']:,.0f}/mo "
                         f"with €{cost['budget_delta_eur']:,.0f}/mo to spare.")
        else:
            lines.append(f"⚠️ This exceeds the stated budget of €{cost['budget']:,.0f}/mo "
                         f"by €{abs(cost['budget_delta_eur']):,.0f}/mo — see caveats.")
    lines.append("")

    lines.append("## Why these tools")
    lines.append(f"Chosen from real, source-linked deployments by comparable "
                 f"organisations — {len(result['matched_cases'])} matched cases, "
                 f"top references below.")
    for case in result["matched_cases"][:3]:
        lines.append(f"- {case.get('organization', 'Unknown')} — {case.get('source_url', '')}")
    lines.append("")

    lines.append("## Summary")
    lines.append(result.get("summary_text", ""))
    lines.append("")

    lines.append("## Caveats — read before committing budget")
    lines.append("- Prices come from a hand-curated table and are **illustrative**, "
                 "not quotes. Verify with vendors before signing anything.")
    lines.append("- Seat counts are assumptions from survey medians, capped for "
                 "single-workflow use — your real headcount will differ.")
    lines.append("- Compliance filtering is a directional shortlist, **not a certification**.")
    return "\n".join(lines)


def blueprint_to_pdf(result: dict) -> bytes:
    """
    Icebox B.8 (Build Guide 34) — the blueprint as a shareable PDF, via reportlab.

    Deliberately a plain monospaced layout: the same content as
    blueprint_to_text(), in a container a non-technical stakeholder can forward
    or drop into a board pack. Returns raw bytes for st.download_button.

    Uses platypus (SimpleDocTemplate) so page breaks are handled for us, and
    Preformatted so the ranked list and cost columns stay aligned like the
    on-screen code block. Lines are hard-wrapped to the frame width first —
    Preformatted does NOT wrap, and the case-reference URLs are long enough to
    run off the page otherwise.
    """
    import io
    import textwrap
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Preformatted, Spacer

    body = _pdf_safe(blueprint_to_text(result))
    heading = _pdf_safe(result.get("project_name") or "Your AI Stack Blueprint")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
        title=f"AASA Blueprint — {heading}", author="AASA",
    )
    mono = ParagraphStyle("aasa_mono", fontName="Courier", fontSize=8.5, leading=11.5)
    h1 = ParagraphStyle("aasa_h1", fontName="Helvetica-Bold", fontSize=14,
                        leading=18, spaceAfter=8)
    note = ParagraphStyle("aasa_note", fontName="Helvetica-Oblique", fontSize=8,
                          leading=11, textColor="#555555")

    max_chars = max(20, int(doc.width / stringWidth("M", "Courier", 8.5)))
    wrapped = []
    for line in body.split("\n"):
        wrapped.extend(
            textwrap.wrap(line, max_chars, subsequent_indent="    ",
                          break_long_words=True, break_on_hyphens=False) or [""]
        )

    doc.build([
        Paragraph(heading, h1),
        Preformatted("\n".join(wrapped), mono),
        Spacer(1, 10),
        # Footer disclaimer — mirrors the in-app honesty line. Keep it.
        Paragraph("Directional only. Pricing is illustrative and may be out of date; "
                  "compliance filtering is a shortlist, not certification. "
                  "Generated by AASA, a 4-week student prototype.", note),
    ])
    return buf.getvalue()