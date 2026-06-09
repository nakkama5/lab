"""Generate prospect report: Markdown + PDF."""
from __future__ import annotations

from datetime import datetime


VERDICT_EMOJI = {"Go": "✅", "À creuser": "🟡", "No-Go": "❌"}
CONFIDENCE_LABEL = {"found": "✓", "partial": "~", "not_found": "?"}
CONFIDENCE_NOTE = {
    "found": "données trouvées",
    "partial": "données partielles",
    "not_found": "non disponible en ligne",
}


def generate_markdown(
    prospect_name: str,
    research: dict,
    score: dict,
    analyst_notes: str = "",
    request_date: str | None = None,
) -> str:
    if request_date is None:
        request_date = datetime.utcnow().strftime("%d/%m/%Y")

    total = score.get("total", 0)
    verdict = score.get("verdict", "—")
    v_emoji = VERDICT_EMOJI.get(verdict, "")
    scores = score.get("scores", {})
    meta = score.get("criteria_meta", {})
    bonus = score.get("bonus", {})

    lines = []

    # ── PAGE 1 — FICHE SYNTHÉTIQUE ────────────────────────────────────────────
    lines += [
        f"# Fiche Prospect — {prospect_name}",
        "",
        f"**Date de la demande :** {request_date}  ",
        f"**Score global :** {total}/100  ",
        f"**Verdict :** {v_emoji} **{verdict}**",
        "",
    ]

    # Executive summary
    summary = score.get("executive_summary", "")
    if summary:
        lines += [
            "## Résumé exécutif",
            "",
            summary,
            "",
        ]

    # Analyst notes
    if analyst_notes.strip():
        lines += [
            "## Connaissance terrain",
            "",
            analyst_notes.strip(),
            "",
        ]

    # Identity quick facts
    identity = research.get("identity", {})
    if identity.get("summary"):
        lines += [
            "## Identité",
            "",
            f"- **Site :** {identity.get('website', '—')}",
            f"- **Création :** {identity.get('founded', '—')}",
            f"- **Pays :** {identity.get('country', '—')}",
            f"- **Modèle de vente :** {identity.get('sales_model', '—')}",
            f"- **Fourchette de prix :** {identity.get('price_range', '—')}",
            "",
            identity["summary"],
            "",
        ]

    # Scoring boxes (compact for page 1)
    lines += ["## Scores par critère", ""]
    criteria_order = ["A", "B", "C", "D", "E", "F"]
    for key in criteria_order:
        s = scores.get(key, {})
        m = meta.get(key, {})
        score_val = s.get("score", "—")
        weighted = s.get("weighted", "—")
        max_pts = m.get("max", "—")
        name = m.get("name", key)
        conf = CONFIDENCE_LABEL.get(s.get("confidence", ""), "")
        justif = s.get("justification", "")
        conf_note = CONFIDENCE_NOTE.get(s.get("confidence", ""), "")
        lines += [
            f"### {key}. {name} — {weighted}/{max_pts} pts {conf}",
            f"*Score : {score_val}/5 · {conf_note}*",
            "",
            justif,
            "",
        ]

    if bonus.get("applicable"):
        lines += [
            f"### BONUS Personal Branding — +{bonus.get('points', 0)} pts",
            "",
            bonus.get("justification", ""),
            "",
        ]

    # Flags
    green = score.get("green_flags", [])
    red = score.get("red_flags", [])
    if green or red:
        lines += ["## Drapeaux", ""]
        if green:
            lines.append("**Drapeaux Verts ✅**")
            for f in green:
                lines.append(f"- {f}")
            lines.append("")
        if red:
            lines.append("**Drapeaux Rouges 🔴**")
            for f in red:
                lines.append(f"- {f}")
            lines.append("")

    # Next action
    next_action = score.get("next_action", "")
    if next_action:
        lines += ["## Action recommandée", "", f"**{next_action}**", ""]

    # ── PAGE 2 — GRILLE DÉTAILLÉE ─────────────────────────────────────────────
    lines += [
        "---",
        "",
        "# Grille Détaillée — Page 2",
        "",
        f"| Critère | Pond. | Score | Pts | Confiance | Justification |",
        "|---------|-------|-------|-----|-----------|---------------|",
    ]
    for key in criteria_order:
        s = scores.get(key, {})
        m = meta.get(key, {})
        name = m.get("name", key)
        weight = m.get("weight", "—")
        score_val = s.get("score", "—")
        weighted = s.get("weighted", "—")
        max_pts = m.get("max", "—")
        conf = CONFIDENCE_LABEL.get(s.get("confidence", ""), "")
        justif = s.get("justification", "—").replace("|", "/").replace("\n", " ")[:120]
        lines.append(f"| **{key}. {name}** | ×{weight} | {score_val}/5 | {weighted}/{max_pts} | {conf} | {justif} |")

    if bonus.get("applicable"):
        justif_b = bonus.get("justification", "—").replace("|", "/")[:80]
        lines.append(f"| **BONUS Personal Branding** | — | — | +{bonus.get('points',0)} | ✓ | {justif_b} |")

    lines += [
        f"| **TOTAL** | | | **{total}/100** | | **{v_emoji} {verdict}** |",
        "",
    ]

    # Detailed research findings per section
    lines += ["## Détail des Recherches", ""]
    sections = [
        ("financial", "Solidité Financière"),
        ("marketing", "Marketing & Influence"),
        ("team", "Équipe"),
        ("product", "Produit & Concept"),
        ("realism", "Réalisme & Maturité"),
        ("distribution", "Distribution"),
    ]
    for key, label in sections:
        data = research.get(key, {})
        if data:
            conf = CONFIDENCE_NOTE.get(data.get("confidence", ""), "")
            lines += [
                f"### {label} _{conf}_",
                "",
                data.get("summary", "—"),
                "",
            ]

    # Sources
    sources = research.get("sources_used", [])
    if sources:
        lines += ["## Sources", ""]
        for s in sources:
            lines.append(f"- {s}")
        lines.append("")

    lines += [
        "---",
        f"*Rapport généré par Prospect Qualifier · {request_date}*",
    ]

    return "\n".join(lines)


def _safe_text(text: str) -> str:
    """Sanitize text to cp1252 (Windows-1252) for fpdf2 built-in fonts.
    cp1252 covers all French accented chars (é, è, à, ç, ù, etc.)."""
    return text.encode("cp1252", errors="replace").decode("cp1252")


def generate_pdf(markdown_text: str, prospect_name: str) -> bytes:
    """Generate a PDF from the markdown report using fpdf2."""
    from fpdf import FPDF

    PAGE_W = 180  # effective width (A4 210mm - 15mm left - 15mm right)

    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(100, 100, 100)
            self.cell(PAGE_W, 8, _safe_text(f"Prospect Qualifier — {prospect_name}"), align="R")
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(15, self.get_y(), 195, self.get_y())
            self.ln(3)

        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(PAGE_W, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 20, 15)
    pdf.add_page()

    for line in markdown_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            pdf.ln(2)
            continue
        try:
            if stripped.startswith("# "):
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_text_color(10, 10, 10)
                pdf.multi_cell(PAGE_W, 8, _safe_text(stripped[2:]))
                pdf.ln(2)
            elif stripped.startswith("## "):
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_text_color(30, 30, 30)
                pdf.set_fill_color(240, 240, 240)
                pdf.multi_cell(PAGE_W, 7, _safe_text(stripped[3:]), border=0, align="L", fill=True)
                pdf.ln(1)
            elif stripped.startswith("### "):
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(PAGE_W, 6, _safe_text(stripped[4:]))
            elif stripped.startswith("---"):
                pdf.set_draw_color(180, 180, 180)
                pdf.line(15, pdf.get_y(), 195, pdf.get_y())
                pdf.ln(4)
            elif stripped.startswith("- ") or stripped.startswith("* "):
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(PAGE_W, 5, _safe_text("  * " + stripped[2:]))
            elif stripped.startswith("|"):
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if all(set(c) <= {"-", ":"} for c in cells):
                    continue  # skip separator rows
                row_text = "  |  ".join(cells[:4])
                pdf.set_font("Courier", "", 8)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(PAGE_W, 5, _safe_text(row_text))
            elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(PAGE_W, 5, _safe_text(stripped.strip("*")))
            else:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(50, 50, 50)
                pdf.multi_cell(PAGE_W, 5, _safe_text(stripped))
        except Exception:
            pass  # skip any line that fails to render

    output = pdf.output()
    if isinstance(output, bytearray):
        return bytes(output)
    return output
