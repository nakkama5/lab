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
    """Convert text to latin-1 safe for fpdf2 built-in fonts.
    Replaces common Unicode typographic chars with ASCII equivalents first."""
    _REPLACEMENTS = {
        "—": "--",   # em dash
        "–": "-",    # en dash
        "‘": "'",    # left single quote
        "’": "'",    # right single quote
        "“": '"',    # left double quote
        "”": '"',    # right double quote
        "…": "...",  # ellipsis
        "•": "-",    # bullet
        "·": "-",    # middle dot
        "€": "EUR",  # euro sign
        "×": "x",    # multiplication sign
        "→": "->",   # arrow right
        " ": " ",    # non-breaking space
        "​": "",     # zero-width space
        " ": " ",    # thin space
        "°": " deg", # degree sign
        "æ": "ae",   # æ
        "œ": "oe",   # œ
    }
    for ch, repl in _REPLACEMENTS.items():
        text = text.replace(ch, repl)
    # Strip remaining non-latin-1 chars (emojis, etc.) with '?'
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _strip_md(text: str) -> str:
    """Strip markdown bold/italic/code markers from text."""
    import re
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return text


def generate_pdf(markdown_text: str, prospect_name: str) -> bytes:
    """Generate a PDF from the markdown report using fpdf2.
    Single-column layout, no header line, full content parity with markdown."""
    from fpdf import FPDF

    W = 175  # effective text width (A4 210mm - 18mm left - 17mm right)

    class PDF(FPDF):
        def header(self):
            pass  # no running header

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 7)
            self.set_text_color(150, 150, 150)
            self.cell(W, 8, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(18, 18, 17)
    pdf.add_page()

    def put(style: str, size: int, r: int, g: int, b: int, text: str,
            h: float = 5.5, fill: bool = False, indent: float = 0):
        """Render a safe, stripped line of text."""
        safe = _safe_text(_strip_md(text))
        if not safe.strip():
            return
        pdf.set_font("Helvetica", style, size)
        pdf.set_text_color(r, g, b)
        w = W - indent
        if indent:
            pdf.set_x(18 + indent)
        if fill:
            pdf.set_fill_color(235, 235, 235)
        pdf.multi_cell(w, h, safe, border=0, align="L", fill=fill, new_x="LMARGIN", new_y="NEXT")

    def render_table(rows: list[list[str]]):
        """Render markdown table rows as indented text blocks."""
        if not rows:
            return
        for row in rows:
            if not row:
                continue
            # First cell = criterion label, rest = values
            label = _safe_text(_strip_md(row[0]))
            values = " | ".join(_safe_text(_strip_md(c)) for c in row[1:])
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(30, 30, 30)
            pdf.set_x(18)
            pdf.multi_cell(W, 5, label, border=0, align="L", new_x="LMARGIN", new_y="NEXT")
            if values.strip():
                pdf.set_font("Helvetica", "", 8)
                pdf.set_text_color(70, 70, 70)
                pdf.set_x(22)
                pdf.multi_cell(W - 4, 4.5, values, border=0, align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

    lines = markdown_text.split("\n")
    i = 0
    table_rows: list[list[str]] = []
    in_table = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        i += 1

        # Detect table rows
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            # Skip separator rows like |---|---|
            if all(set(c) <= {"-", ":", " "} for c in cells):
                continue
            in_table = True
            table_rows.append(cells)
            continue
        else:
            if in_table:
                render_table(table_rows)
                table_rows = []
                in_table = False

        if not stripped:
            pdf.ln(2)
        elif stripped.startswith("# "):
            put("B", 16, 10, 10, 10, stripped[2:], h=9)
            pdf.ln(3)
        elif stripped.startswith("## "):
            pdf.ln(1)
            put("B", 12, 20, 20, 20, stripped[3:], h=7, fill=True)
            pdf.ln(2)
        elif stripped.startswith("### "):
            put("B", 10, 40, 40, 40, stripped[4:], h=6)
            pdf.ln(1)
        elif stripped.startswith("---"):
            pdf.set_draw_color(190, 190, 190)
            pdf.line(18, pdf.get_y(), 193, pdf.get_y())
            pdf.ln(4)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            put("", 9, 50, 50, 50, "  - " + stripped[2:], h=5, indent=3)
        elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
            put("I", 8, 100, 100, 100, stripped.strip("*"), h=5)
        else:
            put("", 9, 50, 50, 50, stripped, h=5)

    # Flush any trailing table
    if in_table and table_rows:
        render_table(table_rows)

    output = pdf.output()
    if isinstance(output, bytearray):
        return bytes(output)
    return output
