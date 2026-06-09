"""Prospect Qualifier — Streamlit UI."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="Prospect Qualifier",
    page_icon="🔍",
    layout="wide",
)

# ── Dark theme CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Base */
html, body { background: #0a0a0a !important; color: #f0f0f0 !important; }
.stApp, .stApp > div, section[data-testid="stMainBlockContainer"],
[data-testid="block-container"] {
    background: #0a0a0a !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* All text white */
p, li, span, div, label, td, th, caption,
.stMarkdown, .stMarkdown p, .stMarkdown li,
[class*="css"], [data-testid*="stMarkdown"],
[data-testid="stText"], [data-testid="stCaption"],
.stCaption, .stCaption p,
[data-testid="stMetricLabel"], [data-testid="stMetricDelta"],
[data-testid="stExpander"] p, [data-testid="stExpander"] span,
[data-testid="stExpander"] div, [data-testid="stExpander"] label,
.streamlit-expanderHeader, .streamlit-expanderContent,
[data-testid="stExpanderToggleIcon"],
[data-baseweb="tab"] span, [data-baseweb="tab-list"] span,
.stTabs [role="tab"], .stTabs [role="tablist"],
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderFile"] span,
small, .small { color: #f0f0f0 !important; }

h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] { color: #f0f0f0 !important; }
h1 { font-size: 1.8rem !important; font-weight: 700 !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
input[type="text"], textarea {
    background: #141414 !important;
    color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}
.stTextInput label, .stTextArea label, .stSelectbox label,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
    color: #f0f0f0 !important;
}
input::placeholder, textarea::placeholder { color: #666 !important; }

/* Buttons: gold bg, black text */
.stButton > button, .stDownloadButton > button {
    background: #4caf50 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #6abf69 !important;
    color: #0a0a0a !important;
}
.stButton > button:disabled { opacity: 0.4 !important; }

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background: #141414 !important;
    border: 1px dashed #2a2a2a !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #f0f0f0 !important; }

/* Metrics */
[data-testid="stMetricValue"] {
    color: #4caf50 !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] { color: #aaa !important; }

/* Progress */
.stProgress > div > div { background: #4caf50 !important; }
[data-testid="stProgressBar"] > div { background: #1e1e1e !important; }

/* Expanders */
[data-testid="stExpander"] {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpanderToggleIcon"] { color: #f0f0f0 !important; }
.streamlit-expanderHeader { color: #f0f0f0 !important; background: #111 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0a0a0a !important;
    border-bottom: 1px solid #222 !important;
}
.stTabs [data-baseweb="tab"] {
    background: #0a0a0a !important;
    color: #888 !important;
    border-radius: 4px 4px 0 0 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #4caf50 !important; }
.stTabs [aria-selected="true"] {
    color: #4caf50 !important;
    border-bottom: 2px solid #4caf50 !important;
    background: #0a0a0a !important;
}
.stTabs [data-baseweb="tab-panel"] { background: #0a0a0a !important; }

/* Info / warning / error boxes */
[data-testid="stAlert"], .stAlert { background: #1a1a1a !important; }
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color: #f0f0f0 !important; }
.element-container [data-testid="stInfo"] { border-left-color: #4caf50 !important; }

/* Divider */
hr { border-color: #222 !important; }

/* Spinner */
[data-testid="stSpinner"] p, [data-testid="stSpinner"] span { color: #f0f0f0 !important; }

/* JSON viewer */
[data-testid="stJson"] { background: #111 !important; color: #f0f0f0 !important; }

/* Sidebar (just in case) */
[data-testid="stSidebar"] { background: #0d0d0d !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "research_data": None,
        "score_data": None,
        "report_md": None,
        "report_pdf": None,
        "prospect_name": "",
        "analyst_notes": "",
        "stage": "input",
        "cycle_session_start": None,
        "cycle_research_start": None,
        "cycle_research_end": None,
        "cycle_score_start": None,
        "cycle_score_end": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _reset():
    # Only reset app-managed keys, never widget keys (Streamlit raises if you set those)
    app_keys = [
        "research_data", "score_data", "report_md", "report_pdf",
        "prospect_name", "analyst_notes", "stage",
        "cycle_session_start", "cycle_research_start", "cycle_research_end",
        "cycle_score_start", "cycle_score_end",
    ]
    for k in app_keys:
        st.session_state[k] = None
    st.session_state["stage"] = "input"
    st.session_state["prospect_name"] = ""
    st.session_state["analyst_notes"] = ""
    st.rerun()


def _verdict_color(verdict: str) -> str:
    return {"Go": "#4caf50", "À creuser": "#ff9800", "No-Go": "#f44336"}.get(verdict, "#888")


def _confidence_badge(conf: str) -> str:
    return {
        "found": "✓ données trouvées",
        "partial": "~ données partielles",
        "not_found": "? non disponible en ligne",
    }.get(conf, "")


def _fmt_duration(start: datetime | None, end: datetime | None) -> str:
    if not start or not end:
        return "—"
    secs = (end - start).total_seconds()
    if secs < 60:
        return f"{secs:.0f}s"
    return f"{secs // 60:.0f}m {secs % 60:.0f}s"


# ── Voice input component ──────────────────────────────────────────────────────
def _voice_input_widget(key: str, label: str = "Dicter vos notes") -> str:
    st.markdown(f"**{label}**")
    st.caption("Chrome/Edge requis pour la reconnaissance vocale. Cliquez sur 🎤 puis parlez.")

    components_html = f"""
<div style="display:flex; gap:10px; align-items:flex-start; margin-bottom:8px;">
  <button id="mic_btn_{key}" onclick="startRecognition_{key}()"
    style="background:#4caf50;color:#0d0d0d;border:none;border-radius:20px;
           padding:8px 18px;font-weight:600;cursor:pointer;font-size:14px;">
    🎤 Parler
  </button>
  <span id="mic_status_{key}" style="color:#888;font-size:13px;padding-top:8px;">Prêt</span>
</div>
<textarea id="transcript_{key}" rows="4"
  style="width:100%;background:#141414;color:#f0f0f0;border:1px solid #2a2a2a;
         border-radius:8px;padding:10px;font-family:Inter,sans-serif;font-size:14px;
         resize:vertical;"
  placeholder="Tapez ou dictez ce que vous savez du prospect..."></textarea>
<script>
function startRecognition_{key}() {{
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {{
    document.getElementById('mic_status_{key}').textContent = '⚠️ Non supporté (utiliser Chrome/Edge)';
    return;
  }}
  const r = new SpeechRecognition();
  r.lang = 'fr-FR';
  r.continuous = true;
  r.interimResults = true;
  document.getElementById('mic_status_{key}').textContent = '🔴 Enregistrement...';
  document.getElementById('mic_btn_{key}').textContent = '⏹ Stop';
  document.getElementById('mic_btn_{key}').onclick = () => r.stop();
  r.onresult = (e) => {{
    let final = '';
    for (let i = 0; i < e.results.length; i++) {{
      if (e.results[i].isFinal) final += e.results[i][0].transcript + ' ';
    }}
    if (final) {{
      document.getElementById('transcript_{key}').value += final;
    }}
  }};
  r.onend = () => {{
    document.getElementById('mic_status_{key}').textContent = '✓ Terminé';
    document.getElementById('mic_btn_{key}').textContent = '🎤 Parler';
    document.getElementById('mic_btn_{key}').onclick = () => startRecognition_{key}();
  }};
  r.onerror = (e) => {{
    document.getElementById('mic_status_{key}').textContent = '⚠️ Erreur: ' + e.error;
    document.getElementById('mic_btn_{key}').textContent = '🎤 Parler';
    document.getElementById('mic_btn_{key}').onclick = () => startRecognition_{key}();
  }};
  r.start();
}}
</script>
"""
    st.components.v1.html(components_html, height=160)

    notes = st.text_area(
        "Notes",
        value=st.session_state.get("analyst_notes", ""),
        height=100,
        key=f"notes_ta_{key}",
        label_visibility="collapsed",
        placeholder="Ce que vous savez déjà du prospect : contacts, historique, projets en cours...",
    )
    return notes


# ── Score display ──────────────────────────────────────────────────────────────
def _show_score(score_data: dict, research_data: dict | None = None):
    total = score_data.get("total", 0)
    verdict = score_data.get("verdict", "—")
    v_color = _verdict_color(verdict)
    scores = score_data.get("scores", {})
    meta = score_data.get("criteria_meta", {})
    bonus = score_data.get("bonus", {})

    # Header metrics
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.metric("Score global", f"{total}/100")
    with col2:
        st.markdown(
            f"<div style='padding:12px 0'><span style='background:{v_color};color:white;"
            f"padding:8px 20px;border-radius:20px;font-weight:700;font-size:1.1rem;'>"
            f"{verdict}</span></div>",
            unsafe_allow_html=True,
        )
    with col3:
        summary = score_data.get("executive_summary", "")
        if summary:
            st.info(summary)

    st.progress(min(total / 100, 1.0))
    st.caption("< 40 → No-Go  ·  40–70 → À creuser  ·  > 70 → Go")

    st.divider()

    # Criteria grid
    st.subheader("Détail par critère")
    criteria_order = ["A", "B", "C", "D", "E", "F"]

    # Map criteria to research section keys
    criteria_research_map = {
        "A": "financial",
        "B": "marketing",
        "C": "team",
        "D": "product",
        "E": "realism",
        "F": "distribution",
    }

    for key in criteria_order:
        s = scores.get(key, {})
        m = meta.get(key, {})
        score_val = s.get("score", 0)
        weighted = s.get("weighted", 0)
        max_pts = m.get("max", 0)
        name = m.get("name", key)
        weight = m.get("weight", 1)
        conf = _confidence_badge(s.get("confidence", ""))
        justif = s.get("justification", "—")
        pct = (score_val / 5) if score_val else 0

        with st.expander(f"**{key}. {name}** — {weighted}/{max_pts} pts  ·  {score_val}/5  ·  _{conf}_"):
            st.markdown(f"**Pondération :** ×{weight}  ·  **Score :** {score_val}/5  ·  **Points :** {weighted}/{max_pts}")
            st.progress(pct)
            st.markdown(f"**Justification :** {justif}")

            # Details appendix: research findings for this criterion
            if research_data:
                research_key = criteria_research_map.get(key)
                rdata = research_data.get(research_key, {}) if research_key else {}
                if rdata and isinstance(rdata, dict):
                    st.markdown("---")
                    st.markdown("**Données de recherche**")
                    r_conf = _confidence_badge(rdata.get("confidence", ""))
                    if r_conf:
                        st.caption(r_conf)
                    r_summary = rdata.get("summary", "")
                    if r_summary:
                        st.markdown(r_summary)
                    # Sub-criteria details if available
                    details = rdata.get("details", {})
                    if details and isinstance(details, dict):
                        for sub_key, sub_val in details.items():
                            if sub_val:
                                st.markdown(f"- **{sub_key}** : {sub_val}")
                    evidence = rdata.get("evidence", [])
                    if evidence:
                        st.markdown("**Éléments de preuve :**")
                        for ev in evidence[:5]:
                            st.markdown(f"  - {ev}")

    if bonus.get("applicable"):
        with st.expander(f"**BONUS Personal Branding** — +{bonus.get('points', 0)} pts"):
            st.markdown(bonus.get("justification", "—"))

    st.divider()

    # Flags
    col_g, col_r = st.columns(2)
    with col_g:
        st.markdown("**✅ Drapeaux Verts**")
        for f in score_data.get("green_flags", []):
            st.markdown(f"- {f}")
    with col_r:
        st.markdown("**🔴 Drapeaux Rouges**")
        for f in score_data.get("red_flags", []):
            st.markdown(f"- {f}")

    next_action = score_data.get("next_action", "")
    if next_action:
        st.divider()
        st.markdown(f"**Action recommandée :** {next_action}")


# ── Cycle Report tab ───────────────────────────────────────────────────────────
def _show_cycle_report():
    st.subheader("📊 Cycle Report")
    st.caption("Métriques d'exécution de la dernière analyse")

    session_start = st.session_state.get("cycle_session_start")
    r_start = st.session_state.get("cycle_research_start")
    r_end = st.session_state.get("cycle_research_end")
    s_start = st.session_state.get("cycle_score_start")
    s_end = st.session_state.get("cycle_score_end")

    if not session_start:
        st.info("Aucune analyse effectuée dans cette session.")
        return

    # Export txt button
    def _build_cycle_txt() -> str:
        lines = [f"CYCLE REPORT — {st.session_state.get('prospect_name', '—')}",
                 f"Session : {session_start.strftime('%Y-%m-%d %H:%M:%S') if session_start else '—'}",
                 f"Durée recherche : {_fmt_duration(r_start, r_end)}",
                 f"Durée scoring : {_fmt_duration(s_start, s_end)}", ""]
        r_data = st.session_state.get("research_data") or {}
        evts = r_data.get("_search_events", [])
        lines.append(f"REQUÊTES WEB ({len(evts)})")
        for i, ev in enumerate(evts, 1):
            lines.append(f"  {i}. {ev.get('query', '')}")
        lines.append("")
        s_data = st.session_state.get("score_data") or {}
        if s_data:
            lines.append(f"SCORE : {s_data.get('total', '—')}/100 — {s_data.get('verdict', '—')}")
            for key in ["A", "B", "C", "D", "E", "F"]:
                s = s_data.get("scores", {}).get(key, {})
                m = s_data.get("criteria_meta", {}).get(key, {})
                lines.append(f"  {key}. {m.get('name', key)} : {s.get('score', '—')}/5 — {s.get('weighted', '—')}/{m.get('max', '—')} pts")
        return "\n".join(lines)

    st.download_button(
        "⬇️ Exporter Cycle Report (.txt)",
        data=_build_cycle_txt(),
        file_name=f"cycle_report_{st.session_state.get('prospect_name', 'prospect').replace(' ', '_')}.txt",
        mime="text/plain",
    )

    prospect_name = st.session_state.get("prospect_name", "—")
    stage = st.session_state.get("stage", "input")
    research_data = st.session_state.get("research_data") or {}
    score_data = st.session_state.get("score_data") or {}

    # Timing overview
    st.markdown("### ⏱ Chronologie")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Démarrage session", session_start.strftime("%H:%M:%S") if session_start else "—")
    with col2:
        st.metric("Durée recherche", _fmt_duration(r_start, r_end))
    with col3:
        st.metric("Durée scoring", _fmt_duration(s_start, s_end))
    with col4:
        total_start = r_start or session_start
        total_end = s_end or r_end
        st.metric("Durée totale", _fmt_duration(total_start, total_end))

    st.divider()

    # Search events
    search_events = research_data.get("_search_events", [])
    st.markdown(f"### 🌐 Recherches web — {len(search_events)} requêtes")
    if search_events:
        for i, ev in enumerate(search_events, 1):
            q = ev.get("query", "")
            results = ev.get("results", [])
            st.markdown(f"**{i}.** `{q}`")
            if results:
                for r in results[:2]:
                    title = r.get("title", "")
                    url = r.get("url", "")
                    if title:
                        st.caption(f"   → {title}" + (f" — {url}" if url else ""))
    else:
        st.caption("Aucune requête enregistrée.")

    st.divider()

    # Score breakdown
    if score_data:
        st.markdown("### 🎯 Récapitulatif du score")
        total = score_data.get("total", 0)
        verdict = score_data.get("verdict", "—")
        v_color = _verdict_color(verdict)

        col_s, col_v = st.columns([1, 2])
        with col_s:
            st.metric("Score final", f"{total}/100")
        with col_v:
            st.markdown(
                f"<span style='background:{v_color};color:white;padding:6px 16px;"
                f"border-radius:16px;font-weight:700;'>{verdict}</span>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        scores = score_data.get("scores", {})
        meta = score_data.get("criteria_meta", {})
        rows = []
        for key in ["A", "B", "C", "D", "E", "F"]:
            s = scores.get(key, {})
            m = meta.get(key, {})
            rows.append({
                "Critère": f"{key}. {m.get('name', key)}",
                "Score": f"{s.get('score', '—')}/5",
                "Points": f"{s.get('weighted', '—')}/{m.get('max', '—')}",
                "Confiance": _confidence_badge(s.get("confidence", "")),
            })
        # Render as markdown table
        st.markdown("| Critère | Score | Points | Confiance |")
        st.markdown("|---------|-------|--------|-----------|")
        for r in rows:
            st.markdown(f"| {r['Critère']} | {r['Score']} | {r['Points']} | {r['Confiance']} |")

        bonus = score_data.get("bonus", {})
        if bonus.get("applicable"):
            st.markdown(f"| BONUS Personal Branding | — | +{bonus.get('points', 0)} | ✓ |")
        st.markdown(f"| **TOTAL** | | **{total}/100** | **{verdict}** |")

    st.divider()

    # Session metadata
    st.markdown("### 🔧 Métadonnées")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"**Prospect :** {prospect_name}")
        has_notes = bool(st.session_state.get("analyst_notes", ""))
        st.markdown(f"**Notes terrain :** {'Oui' if has_notes else 'Non'}")
    with col_m2:
        st.markdown(f"**Statut :** {stage}")
        keys_present = [k for k in ["research_data", "score_data", "report_md", "report_pdf"]
                        if st.session_state.get(k)]
        st.markdown(f"**Données disponibles :** {', '.join(keys_present) or '—'}")


# ── Main app ───────────────────────────────────────────────────────────────────
def main():
    # Header
    col_title, col_reset = st.columns([5, 1])
    with col_title:
        st.title("🔍 Prospect Qualifier")
        st.caption("Due diligence automatisée · Matrice Go/No-Go · Fiche prospect")
    with col_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Nouvelle analyse", key="btn_reset"):
            _reset()

    stage = st.session_state.get("stage", "input")

    # ── INPUT ──────────────────────────────────────────────────────────────────
    if stage == "input":
        st.markdown("### Prospect à analyser")

        col_name, col_empty = st.columns([2, 1])
        with col_name:
            prospect_name = st.text_input(
                "Nom du prospect / de la marque",
                value=st.session_state.get("prospect_name", ""),
                placeholder="ex: Maison Margiela, Byredo, une marque niche...",
                key="input_name",
            )

        st.markdown("### Documents (optionnel)")
        uploaded = st.file_uploader(
            "Déposez des fichiers sur le prospect (briefs, emails, présentations...)",
            accept_multiple_files=True,
            type=["pdf", "txt", "docx", "md"],
            key="file_upload",
        )

        st.markdown("### Notes terrain")
        analyst_notes = _voice_input_widget("main", "Ce que vous savez déjà du prospect")

        st.divider()

        can_run = bool(prospect_name.strip())
        if not can_run:
            st.caption("Entrez au minimum le nom du prospect pour lancer l'analyse.")

        if st.button("🚀 Lancer l'analyse", disabled=not can_run, key="btn_run"):
            doc_text = ""
            if uploaded:
                from src.ingest import load_files
                corpus = load_files(uploaded)
                doc_text = "\n\n".join(c.get("text", "") for c in corpus)

            full_notes = analyst_notes.strip()
            if doc_text:
                full_notes = (full_notes + "\n\n" + doc_text).strip() if full_notes else doc_text

            st.session_state["prospect_name"] = prospect_name.strip()
            st.session_state["analyst_notes"] = full_notes
            st.session_state["stage"] = "researching"
            st.session_state["cycle_session_start"] = datetime.utcnow()
            st.rerun()

    # ── RESEARCH ───────────────────────────────────────────────────────────────
    elif stage == "researching":
        prospect_name = st.session_state["prospect_name"]
        analyst_notes = st.session_state["analyst_notes"]

        st.markdown(f"### Recherche en cours sur **{prospect_name}**...")

        search_placeholder = st.empty()
        progress_bar = st.progress(0.0)
        status_text = st.empty()

        searches_done = []

        def progress_cb(events):
            for ev in events:
                q = ev.get("query", "")
                if q:
                    searches_done.append(q)
            search_placeholder.markdown(
                "**Recherches effectuées :**\n" +
                "\n".join(f"- `{q}`" for q in searches_done[-10:])
            )
            progress_bar.progress(min(len(searches_done) / 20, 0.8))

        try:
            from src.researcher import run_research
            st.session_state["cycle_research_start"] = datetime.utcnow()
            status_text.text("🔍 Collecte des informations publiques...")
            research_data = run_research(
                prospect_name=prospect_name,
                analyst_notes=analyst_notes,
                progress_cb=progress_cb,
            )
            st.session_state["research_data"] = research_data
            st.session_state["cycle_research_end"] = datetime.utcnow()
            progress_bar.progress(0.9)
            status_text.text("✓ Recherche terminée")
            st.session_state["stage"] = "scoring"
            st.rerun()
        except Exception as e:
            st.error(f"Erreur lors de la recherche : {e}")
            if st.button("Réessayer"):
                st.rerun()

    # ── SCORING ────────────────────────────────────────────────────────────────
    elif stage == "scoring":
        prospect_name = st.session_state["prospect_name"]
        st.markdown(f"### Calcul du score pour **{prospect_name}**...")

        with st.spinner("Analyse et scoring en cours..."):
            try:
                from src.scorer import run_score
                st.session_state["cycle_score_start"] = datetime.utcnow()
                score_data = run_score(
                    research_data=st.session_state["research_data"],
                    analyst_notes=st.session_state["analyst_notes"],
                )
                st.session_state["score_data"] = score_data
                st.session_state["cycle_score_end"] = datetime.utcnow()
                st.session_state["stage"] = "done"
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors du scoring : {e}")
                if st.button("Réessayer"):
                    st.session_state["stage"] = "researching"
                    st.rerun()

    # ── RESULTS ────────────────────────────────────────────────────────────────
    elif stage == "done":
        prospect_name = st.session_state["prospect_name"]
        score_data = st.session_state["score_data"]
        research_data = st.session_state["research_data"]

        tab_analyse, tab_cycle = st.tabs(["🔍 Analyse", "📊 Cycle Report"])

        with tab_analyse:
            st.markdown(f"## Résultats — {prospect_name}")

            _show_score(score_data, research_data)

            # Generate report
            st.divider()
            st.subheader("📄 Rapport")

            if st.button("Générer le rapport complet", key="btn_report"):
                from src.reporter import generate_markdown, generate_pdf
                md = generate_markdown(
                    prospect_name=prospect_name,
                    research=research_data,
                    score=score_data,
                    analyst_notes=st.session_state["analyst_notes"],
                    request_date=datetime.utcnow().strftime("%d/%m/%Y"),
                )
                st.session_state["report_md"] = md
                try:
                    pdf_bytes = generate_pdf(md, prospect_name)
                    st.session_state["report_pdf"] = pdf_bytes
                except Exception as pdf_err:
                    st.error(f"Erreur PDF : {pdf_err}")
                    st.session_state["report_pdf"] = None

            if st.session_state.get("report_md"):
                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    if st.session_state.get("report_pdf"):
                        st.download_button(
                            "⬇️ Télécharger PDF",
                            data=st.session_state["report_pdf"],
                            file_name=f"prospect_{prospect_name.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                        )
                    else:
                        st.caption("PDF non disponible")
                with col_dl2:
                    st.download_button(
                        "⬇️ Télécharger Markdown",
                        data=st.session_state["report_md"],
                        file_name=f"prospect_{prospect_name.replace(' ', '_')}.md",
                        mime="text/markdown",
                    )

                with st.expander("Aperçu du rapport"):
                    st.markdown(st.session_state["report_md"])

            # Raw data (debug)
            with st.expander("Données brutes (debug)"):
                st.json(score_data)
                st.json({k: v for k, v in research_data.items() if not k.startswith("_")})

        with tab_cycle:
            _show_cycle_report()


if __name__ == "__main__":
    main()
