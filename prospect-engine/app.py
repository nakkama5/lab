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
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: #f0f0f0 !important;
}
.stApp { background: #0a0a0a !important; }
section[data-testid="stMainBlockContainer"] { background: #0a0a0a !important; padding-top: 2rem; }
p, li, span, div, label, .stMarkdown { color: #f0f0f0 !important; }
h1 { font-size: 1.8rem !important; font-weight: 700 !important; color: #f0f0f0 !important; }
h2 { font-size: 1.3rem !important; font-weight: 600 !important; color: #f0f0f0 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #f0f0f0 !important; }
.stTextInput input, .stTextArea textarea {
    background: #141414 !important; color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important; border-radius: 8px !important;
}
.stButton > button {
    background: #e8d5a0 !important; color: #0a0a0a !important;
    border: none !important; border-radius: 20px !important;
    font-weight: 600 !important; padding: 0.5rem 1.5rem !important;
}
.stButton > button:hover { background: #f0e4b8 !important; }
.stFileUploader { background: #141414 !important; border-radius: 8px !important; border: 1px solid #2a2a2a !important; }
div[data-testid="stMetricValue"] { color: #e8d5a0 !important; font-size: 2rem !important; font-weight: 700 !important; }
.stProgress > div > div { background: #e8d5a0 !important; }
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
        "stage": "input",  # input | researching | scoring | done
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _reset():
    for k in ["research_data", "score_data", "report_md", "report_pdf"]:
        st.session_state[k] = None
    st.session_state["stage"] = "input"
    st.rerun()


def _verdict_color(verdict: str) -> str:
    return {"Go": "#4caf50", "À creuser": "#ff9800", "No-Go": "#f44336"}.get(verdict, "#888")


def _confidence_badge(conf: str) -> str:
    return {
        "found": "✓ données trouvées",
        "partial": "~ données partielles",
        "not_found": "? non disponible en ligne",
    }.get(conf, "")


# ── Voice input component ──────────────────────────────────────────────────────
def _voice_input_widget(key: str, label: str = "Dicter vos notes") -> str:
    """Microphone button using browser Web Speech API + editable text area."""
    st.markdown(f"**{label}**")
    st.caption("Chrome/Edge requis pour la reconnaissance vocale. Cliquez sur 🎤 puis parlez.")

    components_html = f"""
<div style="display:flex; gap:10px; align-items:flex-start; margin-bottom:8px;">
  <button id="mic_btn_{key}" onclick="startRecognition_{key}()"
    style="background:#e8d5a0;color:#0a0a0a;border:none;border-radius:20px;
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

    # Editable text area in Python (user can also type here directly)
    notes = st.text_area(
        "Notes (éditables — le texte dicté apparaît dans la zone ci-dessus, recopiez-le ici si besoin)",
        value=st.session_state.get("analyst_notes", ""),
        height=100,
        key=f"notes_ta_{key}",
        label_visibility="collapsed",
        placeholder="Ce que vous savez déjà du prospect : contacts, historique, projets en cours...",
    )
    return notes


# ── Score display ──────────────────────────────────────────────────────────────
def _show_score(score_data: dict):
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
        bar_color = "#4caf50" if pct >= 0.6 else "#ff9800" if pct >= 0.4 else "#f44336"

        with st.expander(f"**{key}. {name}** — {weighted}/{max_pts} pts  ·  {score_val}/5  ·  _{conf}_"):
            st.markdown(f"**Pondération :** ×{weight}  ·  **Score :** {score_val}/5  ·  **Points :** {weighted}/{max_pts}")
            st.progress(pct)
            st.markdown(justif)

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
            # Extract text from documents
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
            status_text.text("🔍 Collecte des informations publiques...")
            research_data = run_research(
                prospect_name=prospect_name,
                analyst_notes=analyst_notes,
                progress_cb=progress_cb,
            )
            st.session_state["research_data"] = research_data
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
                score_data = run_score(
                    research_data=st.session_state["research_data"],
                    analyst_notes=st.session_state["analyst_notes"],
                )
                st.session_state["score_data"] = score_data
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

        st.markdown(f"## Résultats — {prospect_name}")

        _show_score(score_data)

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
            pdf_bytes = generate_pdf(md, prospect_name)
            st.session_state["report_md"] = md
            st.session_state["report_pdf"] = pdf_bytes

        if st.session_state.get("report_md"):
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                st.download_button(
                    "⬇️ Télécharger PDF",
                    data=st.session_state["report_pdf"],
                    file_name=f"prospect_{prospect_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                )
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


if __name__ == "__main__":
    main()
