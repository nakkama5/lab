"""Perception Engine — Streamlit UI."""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import streamlit as st

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent
RUNS_DIR = BASE_DIR / "runs"
RUNS_DIR.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Perception Engine",
    page_icon="🧭",
    layout="wide",
)

# ── Dark theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Palette ──────────────────────────────────────────────────────────────────
   --bg:       #0a0a0a   page background
   --surface:  #141414   card / input background
   --border:   #2a2a2a   subtle borders
   --muted:    #3a3a3a   hover states, secondary surfaces
   --text:     #f0f0f0   primary text
   --sub:      #888888   secondary / captions
   --accent:   #e8d5a0   warm gold accent (buttons, links, focus)
   --accent2:  #b0c4de   steel blue for secondary actions
──────────────────────────────────────────────────────────────────────────── */

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #f0f0f0 !important;
}

/* ── Backgrounds ────────────────────────────────────────────────────────────── */
.stApp { background: #0a0a0a !important; }
section[data-testid="stMainBlockContainer"] {
    background: #0a0a0a !important;
    padding-top: 2rem;
}
section[data-testid="stSidebar"] {
    background: #0f0f0f !important;
    border-right: 1px solid #2a2a2a !important;
}

/* ── All text defaults ────────────────────────────────────────────────────── */
p, li, span, div, label, .stMarkdown {
    color: #f0f0f0 !important;
}

/* ── Cards / bordered containers ─────────────────────────────────────────── */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #141414 !important;
    border-radius: 16px !important;
    border: 1px solid #2a2a2a !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
    padding: 1.5rem !important;
}

/* ── Headers ─────────────────────────────────────────────────────────────── */
h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
    color: #f0f0f0 !important;
}
h2 {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: #f0f0f0 !important;
}
h3 {
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: #f0f0f0 !important;
}
[data-testid="stHeadingWithActionElements"] h2 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #f0f0f0 !important;
}

/* ── Captions ────────────────────────────────────────────────────────────── */
.stCaption, small, [data-testid="stCaptionContainer"] {
    color: #888888 !important;
    font-size: 0.8rem !important;
}

/* ── Primary buttons ────────────────────────────────────────────────────── */
.stButton > button {
    background: #e8d5a0 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 980px !important;
    padding: 0.5rem 1.4rem !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    transition: background 0.15s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #f0e0b0 !important;
    color: #0a0a0a !important;
}
.stButton > button[kind="secondary"] {
    background: #2a2a2a !important;
    color: #f0f0f0 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #3a3a3a !important;
    color: #f0f0f0 !important;
}

/* ── Download buttons ───────────────────────────────────────────────────── */
.stDownloadButton > button {
    background: #2a2a2a !important;
    color: #e8d5a0 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 980px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: #3a3a3a !important;
    color: #f0e0b0 !important;
}

/* ── Text inputs & textareas ────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea {
    border-radius: 10px !important;
    border: 1px solid #2a2a2a !important;
    background: #141414 !important;
    font-size: 0.9rem !important;
    color: #f0f0f0 !important;
    caret-color: #e8d5a0 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #e8d5a0 !important;
    box-shadow: 0 0 0 3px rgba(232,213,160,0.15) !important;
    outline: none !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #555555 !important;
}

/* ── Selectbox ──────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1px solid #2a2a2a !important;
    background: #141414 !important;
    color: #f0f0f0 !important;
}
.stSelectbox svg { fill: #888888 !important; }

/* ── Number input ───────────────────────────────────────────────────────── */
.stNumberInput input {
    background: #141414 !important;
    color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
}

/* ── Expanders ──────────────────────────────────────────────────────────── */
.streamlit-expanderHeader, [data-testid="stExpanderToggleIcon"] {
    background: #141414 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    color: #f0f0f0 !important;
    border: 1px solid #2a2a2a !important;
}
.streamlit-expanderContent {
    background: #0f0f0f !important;
    border: 1px solid #2a2a2a !important;
    border-top: none !important;
}

/* ── Metrics ────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #141414 !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    border: 1px solid #2a2a2a !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    color: #888888 !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #e8d5a0 !important;
    letter-spacing: -0.03em !important;
}

/* ── Tabs ───────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #141414 !important;
    border-radius: 980px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid #2a2a2a !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 980px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #888888 !important;
    padding: 6px 18px !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #2a2a2a !important;
    color: #f0f0f0 !important;
    box-shadow: none !important;
}

/* ── Alerts / banners ───────────────────────────────────────────────────── */
.stAlert {
    border-radius: 12px !important;
    border: none !important;
}
[data-testid="stAlertContentContainer"] p {
    color: inherit !important;
}
/* Success */
div[data-testid="stAlert"][data-type="success"] {
    background: #0d2010 !important;
    border: 1px solid #1a4020 !important;
}
div[data-testid="stAlert"][data-type="success"] p { color: #6fcf97 !important; }
/* Error */
div[data-testid="stAlert"][data-type="error"] {
    background: #1e0a0a !important;
    border: 1px solid #3d1010 !important;
}
div[data-testid="stAlert"][data-type="error"] p { color: #eb5757 !important; }
/* Info */
div[data-testid="stAlert"][data-type="info"] {
    background: #0a1520 !important;
    border: 1px solid #1a3040 !important;
}
div[data-testid="stAlert"][data-type="info"] p { color: #b0c4de !important; }
/* Warning */
div[data-testid="stAlert"][data-type="warning"] {
    background: #1a1200 !important;
    border: 1px solid #3a2800 !important;
}
div[data-testid="stAlert"][data-type="warning"] p { color: #e8d5a0 !important; }

/* ── Divider ────────────────────────────────────────────────────────────── */
hr {
    border-color: #2a2a2a !important;
    margin: 1.5rem 0 !important;
}

/* ── Progress bar ───────────────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: #e8d5a0 !important;
    border-radius: 980px !important;
}
.stProgress > div > div {
    background: #2a2a2a !important;
    border-radius: 980px !important;
}

/* ── Dataframe ──────────────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #2a2a2a !important;
}
.stDataFrame [data-testid="StyledDataFrameDataCell"] {
    color: #f0f0f0 !important;
}
.stDataFrame [data-testid="StyledDataFrameHeaderCell"] {
    color: #888888 !important;
    background: #141414 !important;
}

/* ── File uploader ──────────────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"] {
    border-radius: 14px !important;
    border: 2px dashed #2a2a2a !important;
    background: #0f0f0f !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span {
    color: #888888 !important;
}

/* ── Checkbox ───────────────────────────────────────────────────────────── */
.stCheckbox label p { color: #f0f0f0 !important; }
.stCheckbox [data-testid="stWidgetLabel"] p { color: #f0f0f0 !important; }

/* ── Radio ──────────────────────────────────────────────────────────────── */
.stRadio label p { color: #f0f0f0 !important; }

/* ── Color picker ───────────────────────────────────────────────────────── */
.stColorPicker label p { color: #f0f0f0 !important; }

/* ── JSON viewer ────────────────────────────────────────────────────────── */
.stJson { background: #0f0f0f !important; border-radius: 10px !important; }

/* ── Spinner ────────────────────────────────────────────────────────────── */
.stSpinner > div { color: #888888 !important; }

/* ── Links ──────────────────────────────────────────────────────────────── */
a { color: #e8d5a0 !important; }
a:hover { color: #f0e0b0 !important; }

/* ── Scrollbar ──────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a3a3a; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "corpus": None,
        "signal_map": None,
        "research_plan": None,
        "evidence_cards": None,
        "dossier": None,
        "deck_spec": None,
        "proposed_tokens": None,
        "run_dir": None,
        "gamma_prompt": None,
        "cycle_report_md": None,
        # Cycle metrics
        "cycle_metrics": {
            "session_start": datetime.utcnow().isoformat(),
            "stages": {},
            "llm_calls": [],
            "web_searches": [],
            "docs_ingested": 0,
            "corpus_chars": 0,
            "questions_derived": 0,
            "evidence_cards_collected": 0,
            "dossier_chars": 0,
            "outputs_generated": [],
            "signal_map_snapshot": None,
        },
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ── Cycle metrics helpers ─────────────────────────────────────────────────────

def _metrics() -> dict:
    return st.session_state.cycle_metrics


def _stage_start(stage: str):
    _metrics()["stages"].setdefault(stage, {})["start"] = datetime.utcnow().isoformat()


def _stage_end(stage: str, success: bool = True, error: str = ""):
    s = _metrics()["stages"].setdefault(stage, {})
    s["end"] = datetime.utcnow().isoformat()
    s["success"] = success
    if error:
        s["error"] = error
    # compute duration
    try:
        from datetime import timezone
        start = datetime.fromisoformat(s["start"])
        end = datetime.fromisoformat(s["end"])
        s["duration_s"] = round((end - start).total_seconds(), 1)
    except Exception:
        pass


# ── Helpers ───────────────────────────────────────────────────────────────────

def _run_dir() -> Path:
    if st.session_state.run_dir is None:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        d = RUNS_DIR / ts
        d.mkdir(parents=True, exist_ok=True)
        st.session_state.run_dir = str(d)
    return Path(st.session_state.run_dir)


def _save_artifact(name: str, content: str | dict | list) -> Path:
    d = _run_dir()
    path = d / name
    if isinstance(content, (dict, list)):
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    return path


def _load_models():
    return {
        "observe": os.environ.get("MODEL_OBSERVE", "claude-sonnet-4-6"),
        "derive": os.environ.get("MODEL_DERIVE", "claude-sonnet-4-6"),
        "research": os.environ.get("MODEL_RESEARCH", "claude-haiku-4-5-20251001"),
        "synthesize": os.environ.get("MODEL_SYNTHESIZE", "claude-sonnet-4-6"),
        "distill": os.environ.get("MODEL_DISTILL", "claude-sonnet-4-6"),
    }


# ── Tab 1: Run ────────────────────────────────────────────────────────────────

def tab_run():
    st.header("Run Pipeline")

    models = _load_models()

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload product documents",
        type=["pptx", "pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        hint_product = st.text_input("Product name (hint)", "")
    with col2:
        hint_sector = st.text_input("Sector (hint)", "")
    with col3:
        hint_tech = st.text_input("Tech core (hint)", "")

    # ── OBSERVE ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 1 · OBSERVE")
    st.caption(f"Prompt: `prompts/observe.md` · Model: `{models['observe']}`")

    if st.button("Run OBSERVE", key="btn_observe"):
        if not uploaded_files:
            st.error("Please upload at least one document.")
        else:
            _stage_start("observe")
            try:
                from src.ingest import ingest_files

                with tempfile.TemporaryDirectory() as tmpdir:
                    paths = []
                    for uf in uploaded_files:
                        p = os.path.join(tmpdir, uf.name)
                        with open(p, "wb") as f:
                            f.write(uf.read())
                        paths.append(p)

                    with st.spinner("Ingesting documents…"):
                        corpus = ingest_files(paths)

                # Prepend hints if provided
                if hint_product or hint_sector or hint_tech:
                    hints = []
                    if hint_product:
                        hints.append(f"Product name: {hint_product}")
                    if hint_sector:
                        hints.append(f"Sector: {hint_sector}")
                    if hint_tech:
                        hints.append(f"Tech core: {hint_tech}")
                    corpus.insert(0, {
                        "source_file": "user_hints",
                        "section": "Hints",
                        "text": "\n".join(hints),
                    })

                st.session_state.corpus = corpus
                _save_artifact("corpus.json", corpus)
                _metrics()["docs_ingested"] = len(uploaded_files)
                _metrics()["corpus_chars"] = sum(len(c.get("text", "")) for c in corpus)
                # snapshot for cycle report (survives page reload)
                _metrics()["signal_map_snapshot"] = None  # will be set after observe

                from src.observe import run_observe
                with st.spinner("Running OBSERVE…"):
                    signal_map = run_observe(corpus, model=models["observe"])

                st.session_state.signal_map = signal_map
                _save_artifact("signal_map.json", signal_map)
                _metrics()["signal_map_snapshot"] = signal_map
                _stage_end("observe", success=True)
                st.success("OBSERVE complete.")
            except Exception as e:
                _stage_end("observe", success=False, error=str(e))
                st.error(f"OBSERVE failed: {e}")
                raise

    if st.session_state.signal_map:
        st.markdown("**Signal Map** (editable):")
        edited_sm = st.text_area(
            "signal_map.json",
            value=json.dumps(st.session_state.signal_map, indent=2, ensure_ascii=False),
            height=300,
            key="ta_signal_map",
        )
        if st.button("Confirm Signal Map", key="btn_confirm_sm"):
            try:
                st.session_state.signal_map = json.loads(edited_sm)
                _save_artifact("signal_map.json", st.session_state.signal_map)
                st.success("Signal map confirmed.")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")

    # ── DERIVE ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 2 · DERIVE")
    st.caption(f"Prompt: `prompts/derive.md` · Model: `{models['derive']}`")

    if st.button("Run DERIVE", key="btn_derive"):
        if not st.session_state.signal_map:
            st.error("Run OBSERVE first.")
        else:
            _stage_start("derive")
            try:
                from src.derive import run_derive
                with st.spinner("Running DERIVE…"):
                    research_plan = run_derive(st.session_state.signal_map, model=models["derive"])
                st.session_state.research_plan = research_plan
                _save_artifact("research_plan.json", research_plan)
                _metrics()["questions_derived"] = len(research_plan.get("questions", []))
                _stage_end("derive", success=True)
                st.success("DERIVE complete.")
            except Exception as e:
                _stage_end("derive", success=False, error=str(e))
                st.error(f"DERIVE failed: {e}")
                raise

    if st.session_state.research_plan:
        st.markdown("**Research Plan** (editable):")
        edited_rp = st.text_area(
            "research_plan.json",
            value=json.dumps(st.session_state.research_plan, indent=2, ensure_ascii=False),
            height=300,
            key="ta_research_plan",
        )
        if st.button("Confirm Research Plan", key="btn_confirm_rp"):
            try:
                st.session_state.research_plan = json.loads(edited_rp)
                _save_artifact("research_plan.json", st.session_state.research_plan)
                st.success("Research plan confirmed.")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")

    # ── RESEARCH ─────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 3 · RESEARCH")
    st.caption(f"Prompt: `prompts/research.md` · Model: `{models['research']}`")

    # Security note before RESEARCH
    st.markdown("""
<div style='background:#0a1520;border-radius:10px;padding:0.6rem 1.1rem;margin-bottom:0.8rem;font-size:0.8rem;color:#b0c4de;border:1px solid #1a3040;'>
🛡️ <strong style="color:#d0e0f0;">Sécurité recherche web</strong> — Les requêtes envoyées au moteur de recherche ne contiennent jamais le nom du produit ni aucune donnée interne. Le nom du produit est remplacé par un terme générique avant chaque recherche.
</div>
""", unsafe_allow_html=True)

    if st.button("Run RESEARCH", key="btn_research"):
        if not st.session_state.research_plan:
            st.error("Run DERIVE first.")
        else:
            _stage_start("research")
            try:
                from src.research import run_research
                questions = st.session_state.research_plan.get("questions", [])
                # Extract product name for query sanitization
                product_name = (st.session_state.signal_map or {}).get("product_name", "")
                progress = st.progress(0)
                cards_all: list[dict] = []
                search_log_all: list[dict] = []
                qa_pairs_all: list[dict] = []

                live_container = st.container()
                with live_container:
                    st.markdown("**Recherches en cours…**")
                    live_placeholder = st.empty()

                live_lines: list[str] = []

                def _on_question_done(question_text: str, search_events: list[dict]):
                    for ev in search_events:
                        q = ev.get("query", "")
                        n = len(ev.get("results", []))
                        flag = " 🛡️" if ev.get("_sanitized") else ""
                        live_lines.append(f"🔍 **{q}**{flag} — {n} résultats")
                        _metrics()["web_searches"].append({
                            "stage": "research",
                            "query": q,
                            "ts": datetime.utcnow().isoformat(),
                        })
                    live_placeholder.markdown("\n\n".join(live_lines[-12:]))

                for i, q in enumerate(questions):
                    with st.spinner(f"Q{i+1}/{len(questions)}: {q.get('question', '')[:70]}…"):
                        partial_plan = {"questions": [q]}
                        result = run_research(
                            partial_plan,
                            model=models["research"],
                            progress_cb=_on_question_done,
                            product_name=product_name,
                        )
                        cards_all.extend(result.get("cards", []))
                        search_log_all.extend(result.get("search_log", []))
                        qa_pairs_all.extend(result.get("qa_pairs", []))
                    progress.progress((i + 1) / len(questions))

                live_placeholder.empty()

                evidence_cards = {"cards": cards_all, "search_log": search_log_all, "qa_pairs": qa_pairs_all}
                st.session_state.evidence_cards = evidence_cards
                _save_artifact("evidence_cards.json", evidence_cards)
                _metrics()["evidence_cards_collected"] = len([c for c in cards_all if not c.get("_raw_source")])
                _stage_end("research", success=True)
                st.success(f"RESEARCH complete — {_metrics()['evidence_cards_collected']} evidence cards, {len(_metrics()['web_searches'])} searches.")
            except Exception as e:
                _stage_end("research", success=False, error=str(e))
                st.error(f"RESEARCH failed: {e}")
                raise

    if st.session_state.evidence_cards:
        cards = st.session_state.evidence_cards.get("cards", [])
        search_log = st.session_state.evidence_cards.get("search_log", [])
        qa_pairs = st.session_state.evidence_cards.get("qa_pairs", [])

        if cards:
            import pandas as pd

            synth_cards = [c for c in cards if not c.get("_raw_source")]
            n_sanitized = sum(1 for e in search_log if e.get("sanitized"))

            st.markdown(
                f"**{len(synth_cards)} evidence cards** · {len(search_log)} requêtes web"
                + (f" · 🛡️ {n_sanitized} requêtes sanitisées" if n_sanitized else "")
            )

            # ── Q&A view — question + réponses structurées ────────────────────
            dim_order = ["market", "technology", "narrative", "regulatory", "adoption", "validation"]
            dim_colors = {
                "market": "#e8d5a0", "technology": "#b0c4de", "narrative": "#c8b0de",
                "regulatory": "#f0b0a0", "adoption": "#b0d4b0", "validation": "#d4c8b0",
            }

            with st.expander("📋 Questions & Réponses par dimension", expanded=True):
                # Group qa_pairs by dimension
                by_dim: dict = {}
                for qa in qa_pairs:
                    d = qa.get("dimension", "market")
                    by_dim.setdefault(d, []).append(qa)

                for dim in dim_order:
                    qas = by_dim.get(dim, [])
                    if not qas:
                        continue
                    color = dim_colors.get(dim, "#e8d5a0")
                    st.markdown(
                        f"<span style='background:{color}22;color:{color};padding:2px 10px;"
                        f"border-radius:6px;font-size:0.75rem;font-weight:600;letter-spacing:0.06em;"
                        f"text-transform:uppercase'>{dim}</span>",
                        unsafe_allow_html=True,
                    )
                    for qa in qas:
                        with st.expander(f"Q · {qa.get('question', '')}", expanded=False):
                            queries = qa.get("queries_fired", [])
                            if queries:
                                st.caption("Requêtes web : " + " · ".join(f"`{q}`" for q in queries))
                            qa_cards = qa.get("cards", [])
                            if qa_cards:
                                for c in qa_cards:
                                    url = c.get("url", "")
                                    src = c.get("source_title", "")
                                    claim = c.get("claim", "")
                                    relevance = c.get("relevance", "")
                                    tag = c.get("tag", "")
                                    src_link = f"[{src}]({url})" if url else src
                                    st.markdown(
                                        f"**{c.get('id','')}** · {src_link}  \n"
                                        f"{claim}"
                                        + (f"  \n*{relevance}*" if relevance else ""),
                                    )
                                    st.caption(f"Tag: {tag} · Dimension: {c.get('dimension','')}")
                                    st.divider()
                            else:
                                st.caption("Aucune evidence card pour cette question.")

            # ── All cards flat table ──────────────────────────────────────────
            with st.expander("Toutes les evidence cards (tableau)"):
                df = pd.DataFrame([
                    {
                        "ID": c.get("id", ""),
                        "Dimension": c.get("dimension", ""),
                        "Tag": c.get("tag", ""),
                        "Claim": c.get("claim", "")[:120],
                        "Source": c.get("source_title", ""),
                        "URL": c.get("url", ""),
                    }
                    for c in synth_cards
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)

    # ── SYNTHESIZE ───────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 4 · SYNTHESIZE")
    st.caption(f"Prompt: `prompts/synthesize.md` · Model: `{models['synthesize']}`")

    if st.button("Run SYNTHESIZE", key="btn_synthesize"):
        if not st.session_state.evidence_cards:
            st.error("Run RESEARCH first.")
        elif not st.session_state.corpus:
            st.error("No corpus available.")
        else:
            _stage_start("synthesize")
            try:
                from src.synthesize import run_synthesize
                with st.spinner("Running SYNTHESIZE…"):
                    dossier = run_synthesize(
                        st.session_state.corpus,
                        st.session_state.evidence_cards,
                        model=models["synthesize"],
                    )
                st.session_state.dossier = dossier
                _save_artifact("dossier.md", dossier)
                _metrics()["dossier_chars"] = len(dossier)
                _stage_end("synthesize", success=True)
                st.success("SYNTHESIZE complete.")
            except Exception as e:
                _stage_end("synthesize", success=False, error=str(e))
                st.error(f"SYNTHESIZE failed: {e}")
                raise

    if st.session_state.dossier:
        with st.expander("Dossier preview", expanded=True):
            st.markdown(st.session_state.dossier)
        if st.download_button(
            "Download dossier.md",
            data=st.session_state.dossier,
            file_name="dossier.md",
            mime="text/markdown",
        ):
            if "dossier" not in _metrics()["outputs_generated"]:
                _metrics()["outputs_generated"].append("dossier")

    # ── DISTILL ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 5 · DISTILL")
    st.caption(f"Prompt: `prompts/distill.md` · Model: `{models['distill']}`")

    if st.button("Run DISTILL", key="btn_distill"):
        if not st.session_state.dossier:
            st.error("Run SYNTHESIZE first.")
        else:
            _stage_start("distill")
            try:
                from src.distill import run_distill
                from src.config_store import load as config_load
                brand_tokens = config_load("brand_tokens")
                deck_layout = config_load("deck_layout")

                with st.spinner("Running DISTILL…"):
                    deck_spec, proposed_tokens = run_distill(
                        st.session_state.dossier,
                        brand_tokens,
                        deck_layout,
                        model=models["distill"],
                    )

                st.session_state.deck_spec = deck_spec
                st.session_state.proposed_tokens = proposed_tokens
                _save_artifact("deck_spec.json", deck_spec)
                _save_artifact("proposed_brand_tokens.json", proposed_tokens)
                _stage_end("distill", success=True)
                st.success("DISTILL complete.")
            except Exception as e:
                _stage_end("distill", success=False, error=str(e))
                st.error(f"DISTILL failed: {e}")
                raise

    if st.session_state.deck_spec:
        with st.expander("Deck Spec JSON"):
            st.json(st.session_state.deck_spec)

        # Proposed tokens comparison
        if st.session_state.proposed_tokens:
            from src.config_store import load as config_load
            current_tokens = config_load("brand_tokens")
            if st.session_state.proposed_tokens != current_tokens:
                st.info("The LLM proposed updated brand tokens. Review and adopt if desired.")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Current tokens**")
                    st.json(current_tokens)
                with col_b:
                    st.markdown("**Proposed tokens**")
                    st.json(st.session_state.proposed_tokens)
                if st.button("Adopt proposed brand tokens", key="btn_adopt_tokens"):
                    from src.config_store import save as config_save
                    config_save("brand_tokens", st.session_state.proposed_tokens)
                    st.success("Brand tokens updated.")

        # PPTX download
        if st.button("Generate & Download .pptx", key="btn_pptx"):
            from src.distill import build_pptx
            from src.config_store import load as config_load
            brand_tokens = config_load("brand_tokens")
            deck_layout = config_load("deck_layout")
            pptx_path = str(_run_dir() / "deck.pptx")
            with st.spinner("Building PPTX…"):
                build_pptx(st.session_state.deck_spec, brand_tokens, deck_layout, pptx_path)
            if "pptx" not in _metrics()["outputs_generated"]:
                _metrics()["outputs_generated"].append("pptx")
            with open(pptx_path, "rb") as f:
                st.download_button(
                    "Download deck.pptx",
                    data=f.read(),
                    file_name="perception_engine_deck.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )

        # Optional Gamma export
        if os.environ.get("GAMMA_API_KEY"):
            if st.button("Export to Gamma", key="btn_gamma"):
                _export_to_gamma()

        # Gamma mega-prompt (always available — no API key needed)
        st.divider()
        st.markdown("#### Generate in Gamma via Claude Code")
        st.caption("No Gamma API key needed — paste this prompt into your Claude Code chat to generate the deck.")

        if st.button("Generate Gamma prompt", key="btn_gamma_prompt"):
            prompt, slide_count = _build_gamma_prompt()
            st.session_state["gamma_prompt"] = prompt
            st.session_state["gamma_slide_count"] = slide_count
            if "gamma_prompt" not in _metrics()["outputs_generated"]:
                _metrics()["outputs_generated"].append("gamma_prompt")

        slide_count = st.session_state.get("gamma_slide_count", 0)
        if slide_count > 20:
            st.warning(
                f"⚠️ **{slide_count} slides detected** — Gamma works best under 20. "
                "Choose how to proceed:"
            )
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("✂️ Trim to 20 slides", key="btn_trim_slides"):
                    trimmed, _ = _build_gamma_prompt(max_slides=20)
                    st.session_state["gamma_prompt"] = trimmed
                    st.session_state["gamma_slide_count"] = 20
                    st.rerun()
            with col_b:
                if st.button("📑 Split into Part 1 + Part 2", key="btn_split_slides"):
                    part1, part2, c1, c2 = _build_gamma_prompt(split=True)
                    st.session_state["gamma_prompt"] = part1
                    st.session_state["gamma_prompt_part2"] = part2
                    st.session_state["gamma_slide_count"] = c1
                    st.rerun()
            with col_c:
                st.button("Keep all slides", key="btn_keep_slides")

        if st.session_state.get("gamma_prompt"):
            if st.session_state.get("gamma_prompt_part2"):
                st.info(f"**Part 1** ({st.session_state.get('gamma_slide_count', '?')} slides) — generate this first in Gamma, then use Part 2 for the second deck.")
                tab1, tab2 = st.tabs(["Part 1", "Part 2"])
                with tab1:
                    st.text_area("Part 1 — paste into Claude Code", value=st.session_state["gamma_prompt"], height=250, key="ta_gamma_p1")
                    st.download_button("Download Part 1", data=st.session_state["gamma_prompt"], file_name="gamma_prompt_part1.txt", mime="text/plain")
                with tab2:
                    st.text_area("Part 2 — paste into Claude Code", value=st.session_state["gamma_prompt_part2"], height=250, key="ta_gamma_p2")
                    st.download_button("Download Part 2", data=st.session_state["gamma_prompt_part2"], file_name="gamma_prompt_part2.txt", mime="text/plain")
            else:
                label = f"Copy this prompt ({slide_count} slides) and paste it into Claude Code ↓" if slide_count else "Copy this prompt and paste it into Claude Code ↓"
                st.text_area(label, value=st.session_state["gamma_prompt"], height=300, key="ta_gamma_prompt")
                st.download_button("Download prompt as .txt", data=st.session_state["gamma_prompt"], file_name="gamma_prompt.txt", mime="text/plain")


def _build_gamma_prompt(max_slides: int | None = None, split: bool = False):
    """Assemble a Gamma generation prompt structured exactly like manual generation.

    Returns:
      - Normal mode: (prompt_str, slide_count)
      - split=True: (part1_str, part2_str, count1, count2)
      - max_slides: truncate slide list to this length
    """
    from src.config_store import load as config_load

    deck_spec = st.session_state.deck_spec or {}

    try:
        brand_tokens = config_load("brand_tokens")
    except Exception:
        brand_tokens = {}

    product = deck_spec.get("product", "")
    taglines = deck_spec.get("taglines") or {}
    micro = deck_spec.get("micro", "")
    elevator = deck_spec.get("elevator", "")
    metrics = deck_spec.get("metrics") or []
    legacy = deck_spec.get("legacy") or []
    evolution = deck_spec.get("evolution") or []
    metaphor = deck_spec.get("metaphor") or {}
    swot = deck_spec.get("swot") or {}
    pillars = deck_spec.get("pillars") or []
    vocab = deck_spec.get("vocab") or []
    manifesto = deck_spec.get("manifesto", "")
    roadmap = deck_spec.get("roadmap") or []
    grapevine = deck_spec.get("grapevine") or []

    palette = brand_tokens.get("palette") or {}
    typography = brand_tokens.get("type") or {}
    brand_rules = brand_tokens.get("rules", "")
    motif = brand_tokens.get("motif", "")

    display_font = typography.get("display", "Georgia") if isinstance(typography, dict) else "Georgia"
    body_font = typography.get("body", "Calibri") if isinstance(typography, dict) else "Calibri"

    # ── Derive neon colors from brand palette ─────────────────────────────────
    # Brand colors are always transcribed into their most VIVID/EMISSIVE form.
    # Never inject muted or matte colors — always push to luminous neon equivalent.
    def _lum(h: str) -> float:
        try:
            h = h.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            return (0.299 * r + 0.587 * g + 0.114 * b) / 255
        except Exception:
            return 0.5

    def _neon_prefix(hex_color: str) -> str:
        """Map a hex color to a vivid emissive descriptor based on hue."""
        try:
            h = hex_color.lstrip("#")
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            mx = max(r, g, b)
            if mx == 0:
                return "electric white"
            # Hue approximation
            if r >= mx and r > g and r > b:
                return "incandescent ember-red" if g < 80 else "radiant amber-orange"
            if g >= mx and g > r and g > b:
                return "electric jade-green" if b > 80 else "luminous acid-green"
            if b >= mx and b > r and b > g:
                return "electric cobalt-blue" if r > 80 else "radiant violet-indigo"
            if r >= mx and g >= mx and r > b and g > b:
                return "radiant amber-gold"
            if r >= mx and b >= mx and r > g and b > g:
                return "electric magenta-rose"
            if g >= mx and b >= mx and g > r and b > r:
                return "electric jade-teal"
            return "luminous white-gold"
        except Exception:
            return "radiant amber-gold"

    palette_entries = [
        (role, val.get("hex", ""), val.get("role", role))
        for role, val in palette.items()
        if isinstance(val, dict) and val.get("hex")
    ]
    palette_entries.sort(key=lambda x: _lum(x[1]))

    if len(palette_entries) >= 2:
        mid = len(palette_entries) // 2
        structure_neon = _neon_prefix(palette_entries[mid][1])
        accent_neon = _neon_prefix(palette_entries[-1][1])
        color_desc = (
            f"Fine emissive lines in {structure_neon} bloom and flare against the darkness, "
            f"with subtle iridescent gradients shimmering at the edges. "
            f"{accent_neon.capitalize()} light reserved for singular focal points — the brightest node, "
            f"the sharpest arc, the one headline that demands attention."
        )
        dominance_desc = (
            f"Near-black dominates the surface; {structure_neon} gives structure; "
            f"{accent_neon} used sparingly for maximum contrast."
        )
    elif len(palette_entries) == 1:
        accent_neon = _neon_prefix(palette_entries[0][1])
        color_desc = f"Fine emissive lines in {accent_neon} bloom and pulse against the darkness."
        dominance_desc = f"Near-black dominates; {accent_neon} provides all light."
    else:
        color_desc = (
            "Fine emissive lines in electric jade-teal and radiant amber-gold bloom and flare against the darkness, "
            "with subtle iridescent gradients shimmering at the edges."
        )
        dominance_desc = "Near-black dominates the surface; jade-teal gives structure; amber-gold reserved for singular focal points."

    visual_style = (
        "Abstract, non-figurative, dynamic and futuristic. "
        "Luminous neon light emitted against a deep near-black field — glowing arcs, "
        "sweeping light trails and constellations of bright pulsing nodes, alive with energy and motion. "
        f"{color_desc} "
        "Glowing circuitry and luminous data-ring motifs suggest an invisible force-field mapped in real time. "
        "High contrast, high colour saturation, cinematic depth of field, soft light bloom, "
        "delicate bokeh, crisp luminous edges, ultra-detailed, high resolution, premium and contemporary. "
        f"{dominance_desc}"
    )
    visual_style_negative = (
        "Never flat, never matte, never dusty, never beige, never earthy, never pastel. "
        "No maps, no typography, no labels, no figuration, no people, no objects, no logos, no text, no recognisable scenes."
    )

    # Always use onyx theme — dark background makes neon light pop
    gamma_theme = "onyx"

    # Build readable color block
    color_lines = []
    for role, val in palette.items():
        if isinstance(val, dict):
            h = val.get("hex", "")
            r = val.get("role", role)
            color_lines.append(f"#{h} = {r}")
    color_summary = " / ".join(color_lines) if color_lines else "no palette"

    # Vocab map
    vocab_map = {}
    for v in vocab:
        k = v.get("from", v.get("from_", ""))
        t = v.get("to", "")
        if k and t:
            vocab_map[k] = t

    def av(text: str) -> str:
        for k, v in vocab_map.items():
            text = text.replace(k, v)
        return text

    strengths = swot.get("strengths") or []
    weaknesses = swot.get("weaknesses") or []
    opportunities = swot.get("opportunities") or []
    threats = swot.get("threats") or []
    gaps = weaknesses + threats

    # ── Build slide content ───────────────────────────────────────────────────
    jargon_rows = deck_spec.get("jargon_rows") or []
    slides: list[str] = []

    # 1. Hero
    slides.append(f"# {product}\n{av(taglines.get('punchy', taglines.get('visionary', '')))}")

    # 2. Outcome promise
    if taglines.get("outcome"):
        slides.append(f"# {av(taglines['outcome'])}\n{av(micro or elevator[:300])}")

    # 3. Elevator pitch (standalone — different angle from outcome)
    if elevator and micro and elevator != micro:
        slides.append(f"# What {av(product)} actually does.\n{av(elevator)}")

    # 4. Context: old world
    if legacy:
        # Split into two slides if enough content
        chunk1 = legacy[:4]
        chunk2 = legacy[4:8]
        slides.append(f"# The world changed. The playbook didn't.\n" + "\n".join(f"- {av(l)}" for l in chunk1))
        if chunk2:
            slides.append(f"# The symptoms are everywhere.\n" + "\n".join(f"- {av(l)}" for l in chunk2))

    # 5. New era
    if evolution:
        chunk1 = evolution[:4]
        chunk2 = evolution[4:8]
        slides.append(f"# {av(taglines.get('visionary', 'The shift has already happened.'))}\n" + "\n".join(f"- {av(e)}" for e in chunk1))
        if chunk2:
            slides.append(f"# What the new era demands.\n" + "\n".join(f"- {av(e)}" for e in chunk2))

    # 6. Metaphor / positioning statement
    if metaphor.get("statement"):
        slides.append(f"# {av(metaphor['statement'])}\n{av(metaphor.get('rationale', ''))}")

    # 7. Proof points (metrics)
    if metrics:
        m_lines = "\n".join(f"- **{m.get('num','')}** — {av(m.get('label',''))}" for m in metrics)
        slides.append(f"# Proof, not promise.\n{m_lines}")

    # 8. Capability table (jargon rows split in batches of 4)
    if jargon_rows:
        for i in range(0, min(len(jargon_rows), 12), 4):
            batch = jargon_rows[i:i+4]
            rows = "\n".join(
                f"| {av(j.get('feature',''))} | {av(j.get('capability',''))} | {av(j.get('benefit',''))} | {j.get('kpi','')} |"
                for j in batch
            )
            slides.append(
                f"# From feature to outcome.\n"
                f"| Feature | Capability | Benefit | KPI |\n|---|---|---|---|\n{rows}"
            )

    # 9. Moat (strengths)
    if strengths:
        s_lines = "\n".join(f"- {av(s)}" for s in strengths)
        slides.append(f"# What no one else can replicate.\n{s_lines}")

    # 10. Gaps / investment case
    if gaps:
        g_lines = "\n".join(f"- {av(g)}" for g in gaps[:6])
        slides.append(f"# The gaps that justify the investment.\nThese are not liabilities — they are the whitespace this roadmap is built to close.\n{g_lines}")

    # 11. Market opportunity
    if opportunities:
        o_lines = "\n".join(f"- {av(o)}" for o in opportunities)
        slides.append(f"# The market is ready. The timing is now.\n{o_lines}")

    # 12. Market signals (grapevine) — two slides if enough
    if grapevine:
        batch1 = grapevine[:4]
        batch2 = grapevine[4:8]
        q_lines = "\n".join(f'> "{av(g.get("desc",""))}" — {g.get("title","")}' for g in batch1)
        slides.append(f"# The signal is there.\n{q_lines}")
        if batch2:
            q_lines2 = "\n".join(f'> "{av(g.get("desc",""))}" — {g.get("title","")}' for g in batch2)
            slides.append(f"# The market is already moving.\n{q_lines2}")

    # 13. Roadmap (one card per phase)
    for r in roadmap:
        pts = "\n".join(f"- {av(pt)}" for pt in r.get("points", []))
        slides.append(f"# {r.get('phase','')} — {av(r.get('name',''))} · {r.get('when','')}\n{pts}")

    # 14. Manifesto — no truncation
    if manifesto:
        slides.append(f"# We believe.\n{av(manifesto)}")

    # 15. Closing CTA
    slides.append(f"# {av(taglines.get('visionary', product))}\n{av(taglines.get('punchy', ''))}\n\nLet's build it together.")

    vocab_lines = "\n".join(f"- {k} → {v}" for k, v in vocab_map.items())
    pillar_lines = "\n".join(
        f"- **{p.get('name','')}**: say «{p.get('do_say','')}», never «{p.get('dont_say','')}»"
        for p in pillars
    )

    # Apply max_slides or split
    if max_slides:
        slides = slides[:max_slides]
    if split:
        mid = len(slides) // 2
        slides_a, slides_b = slides[:mid], slides[mid:]
    else:
        slides_a = slides

    def _make_prompt(slide_list: list[str]) -> str:  # noqa: E306
        dc = "\n\n---\n\n".join(slide_list)
        return f"""Generate a Gamma presentation using the `generate` tool.

**Product:** {product}
**Total slides:** {len(slide_list)} cards (use exactly these --- breaks as card boundaries; set cardSplit to inputTextBreaks)

---

## THEME & VISUAL IDENTITY

**Gamma theme:** `{gamma_theme}` — use `themeId: "onyx"` (dark background is required for the neon effect)

**Image parameters — pass ALL of these exactly:**
- `imageOptions.source` = `aiGenerated`
- `imageOptions.stylePreset` = `custom` (do NOT use any named preset — it overrides the style below)
- `imageOptions.style` = `{visual_style}`
- negative prompt (if supported as a separate field): `{visual_style_negative}`
  If no separate negative prompt field exists, append it to `imageOptions.style`.

**Typography:** display = {display_font} / body = {body_font}

---

## BRAND VOCABULARY (apply everywhere — headlines, body, image prompts)
{vocab_lines if vocab_lines else "(none)"}

## TONE PILLARS
{pillar_lines if pillar_lines else "(none)"}

---

## DECK CONTENT
(Each --- separator = one new card. Pass this as inputText with cardSplit: inputTextBreaks)

{dc}

---

## GENERATION INSTRUCTIONS
- Use `cardSplit: inputTextBreaks` so each --- becomes a separate card
- `themeId`: `onyx` — apply consistently across all cards
- Images: `source=aiGenerated`, `stylePreset=custom`, style as specified above — never use a named stylePreset
- Apply vocabulary swaps in every text element including image prompts
- SWOT is reframed as moat (strengths) + gaps (weaknesses+threats merged) + opportunity — not a 4-quadrant grid
- One roadmap card per phase so each has room to breathe
- Manifesto card: large typographic treatment, minimal imagery
- Closing card: full-bleed, strong visual, CTA prominent
"""

    if split:
        return _make_prompt(slides_a), _make_prompt(slides_b), len(slides_a), len(slides_b)
    return _make_prompt(slides_a), len(slides_a)


def _export_to_gamma():
    """Export dossier to a Gamma presentation."""
    try:
        import requests
        api_key = os.environ.get("GAMMA_API_KEY", "")
        dossier = st.session_state.dossier or ""
        deck_spec = st.session_state.deck_spec or {}
        product = deck_spec.get("product", "Perception Engine Output")
        tagline = (deck_spec.get("taglines") or {}).get("punchy", "")
        prompt_text = f"Create a presentation for: {product}\n{tagline}\n\n{dossier[:2000]}"

        with st.spinner("Sending to Gamma…"):
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            resp = requests.post(
                "https://api.gamma.app/generate",
                headers=headers,
                json={"text": prompt_text},
                timeout=60,
            )
            if resp.ok:
                result = resp.json()
                url = result.get("url", "")
                st.success(f"Gamma presentation created: {url}")
                if url:
                    st.markdown(f"[Open in Gamma]({url})")
            else:
                st.error(f"Gamma API error: {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        st.error(f"Gamma export failed: {e}")


# ── Tab 2: Prompt Studio ──────────────────────────────────────────────────────

def tab_prompt_studio():
    st.header("Prompt Studio")

    from src import prompt_store

    stage = st.selectbox(
        "Stage",
        options=prompt_store.KNOWN_STAGES,
        key="ps_stage",
    )

    current_text = prompt_store.load(stage)
    required = prompt_store.required_placeholders(stage)

    # Required placeholders panel
    if required:
        cols = st.columns(len(required))
        for i, ph in enumerate(required):
            present = ph in current_text
            with cols[i]:
                color = "#6fcf97" if present else "#eb5757"
                st.markdown(
                    f"<span style='color:{color};font-weight:bold'>{ph}</span>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No required placeholders for this stage.")

    new_text = st.text_area(
        f"Prompt: prompts/{stage}.md",
        value=current_text,
        height=400,
        key=f"ps_text_{stage}",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Save", key="ps_save"):
            try:
                prompt_store.save(stage, new_text)
                st.success("Saved.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
    with col2:
        if st.button("Reset to default", key="ps_reset"):
            prompt_store.reset(stage)
            st.success("Reset to default.")
            st.rerun()
    with col3:
        if st.button("Revert", key="ps_revert"):
            st.rerun()
    with col4:
        if st.button("Diff vs default", key="ps_diff"):
            diff = prompt_store.diff_vs_default(stage)
            st.text(diff if diff else "(no differences)")

    # Compiled preview
    with st.expander("Compiled preview"):
        preview_vars = {
            "corpus": "[corpus text would appear here…]",
            "signal_map": '{"product_name": "…"}',
            "question": "Sample research question",
            "evidence_cards": '{"cards": []}',
            "dossier": "[dossier text would appear here…]",
            "deck_schema": "{}",
            "brand_tokens": "{}",
        }
        try:
            compiled = prompt_store.compiled(stage, **preview_vars)
            st.text(compiled[:2000] + ("…" if len(compiled) > 2000 else ""))
        except Exception as e:
            st.warning(f"Preview error: {e}")


# ── Tab 3: Brand Studio ───────────────────────────────────────────────────────

def tab_brand_studio():
    st.header("Brand Studio")

    from src.config_store import load as config_load, save as config_save, reset as config_reset, diff_vs_default

    tokens = config_load("brand_tokens")
    palette = tokens.get("palette", {})
    type_info = tokens.get("type", {"display": "Georgia", "body": "Calibri"})

    st.subheader("Palette")
    updated_palette = {}
    for name, info in palette.items():
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 3])
        with col1:
            hex_val = info.get("hex", "888888")
            # Color picker expects #RRGGBB
            picked = st.color_picker(
                name.capitalize(),
                value=f"#{hex_val}",
                key=f"brand_cp_{name}",
            )
            new_hex = picked.lstrip("#")
        with col2:
            new_hex_input = st.text_input("Hex", value=new_hex, key=f"brand_hex_{name}")
        with col3:
            new_role = st.text_input("Role", value=info.get("role", ""), key=f"brand_role_{name}")
        with col4:
            new_why = st.text_input("Why", value=info.get("why", ""), key=f"brand_why_{name}")
        with col5:
            # Live swatch
            h = new_hex_input.lstrip("#") if new_hex_input else new_hex
            st.markdown(
                f"<div style='background:#{h};height:40px;border-radius:4px;'></div>",
                unsafe_allow_html=True,
            )
        updated_palette[name] = {
            "hex": new_hex_input.lstrip("#") if new_hex_input else new_hex,
            "role": new_role,
            "why": new_why,
        }

    st.subheader("Typography")
    col1, col2 = st.columns(2)
    with col1:
        display_font = st.text_input("Display font", value=type_info.get("display", "Georgia"), key="brand_display_font")
    with col2:
        body_font = st.text_input("Body font", value=type_info.get("body", "Calibri"), key="brand_body_font")

    st.subheader("Rules & Motif")
    rules = st.text_area("Rules", value=tokens.get("rules", ""), key="brand_rules")
    motif = st.text_area("Motif", value=tokens.get("motif", ""), key="brand_motif")

    # Mini preview
    with st.expander("Live mini-preview"):
        ink_hex = updated_palette.get("ink", {}).get("hex", "17120E")
        cream_hex = updated_palette.get("cream", {}).get("hex", "F4EEE2")
        jade_hex = updated_palette.get("jade", {}).get("hex", "2C5D4F")
        saffron_hex = updated_palette.get("saffron", {}).get("hex", "E1A23C")
        st.markdown(f"""
<div style='background:#{ink_hex};padding:24px;border-radius:8px;font-family:{display_font},serif;'>
  <div style='font-size:28px;font-weight:bold;color:#{cream_hex};'>Your Product Name</div>
  <div style='font-size:16px;color:#{saffron_hex};margin-top:8px;'>Punchy tagline here</div>
  <div style='font-size:11px;color:#{cream_hex};margin-top:12px;opacity:0.6;'>micro copy</div>
</div>
<div style='background:#{cream_hex};padding:16px;border-radius:8px;margin-top:8px;font-family:{body_font},sans-serif;'>
  <div style='display:flex;gap:12px;'>
    <div style='background:#{jade_hex};padding:12px;border-radius:4px;text-align:center;flex:1;'>
      <div style='font-size:24px;font-weight:bold;color:#{saffron_hex};'>42%</div>
      <div style='font-size:11px;color:#{cream_hex};'>Sample metric</div>
    </div>
    <div style='background:#{jade_hex};padding:12px;border-radius:4px;text-align:center;flex:1;'>
      <div style='font-size:24px;font-weight:bold;color:#{saffron_hex};'>3×</div>
      <div style='font-size:11px;color:#{cream_hex};'>Efficiency gain</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Save brand tokens", key="brand_save"):
            updated = {
                "palette": updated_palette,
                "type": {"display": display_font, "body": body_font},
                "rules": rules,
                "motif": motif,
            }
            config_save("brand_tokens", updated)
            st.success("Saved.")
    with col2:
        if st.button("Reset to default", key="brand_reset"):
            config_reset("brand_tokens")
            st.success("Reset.")
            st.rerun()
    with col3:
        if st.button("Revert", key="brand_revert"):
            st.rerun()
    with col4:
        if st.button("Diff vs default", key="brand_diff"):
            diff = diff_vs_default("brand_tokens")
            st.text(diff if diff else "(no differences)")


# ── Tab 4: Deck Studio ────────────────────────────────────────────────────────

def tab_deck_studio():
    st.header("Deck Studio")

    from src.config_store import load as config_load, save as config_save, reset as config_reset, validate_layout, diff_vs_default
    from src.section_registry import types as registry_types, count_bounds as reg_bounds

    layout = config_load("deck_layout")
    sections = layout.get("sections", [])

    st.subheader("Sections")

    advanced_mode = st.checkbox("Advanced mode (raw JSON editor)", key="deck_advanced")

    if advanced_mode:
        raw_json = st.text_area(
            "deck_layout.json",
            value=json.dumps(layout, indent=2),
            height=500,
            key="deck_raw_json",
        )
        errors = []
        try:
            parsed = json.loads(raw_json)
            errors = validate_layout(parsed)
            if errors:
                for e in errors:
                    st.error(e)
            else:
                st.success("Layout is valid.")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {e}")

        if st.button("Save (advanced)", key="deck_save_advanced"):
            try:
                parsed = json.loads(raw_json)
                errors = validate_layout(parsed)
                if errors:
                    st.error("Fix errors before saving.")
                else:
                    config_save("deck_layout", parsed)
                    st.success("Saved.")
                    st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
    else:
        # Interactive editor
        updated_sections = []
        for i, section in enumerate(sections):
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 0.5, 2, 2, 1, 1])
                with col1:
                    if st.button("▲", key=f"deck_up_{i}") and i > 0:
                        sections[i], sections[i-1] = sections[i-1], sections[i]
                        config_save("deck_layout", {"sections": sections})
                        st.rerun()
                with col2:
                    if st.button("▼", key=f"deck_dn_{i}") and i < len(sections) - 1:
                        sections[i], sections[i+1] = sections[i+1], sections[i]
                        config_save("deck_layout", {"sections": sections})
                        st.rerun()
                with col3:
                    enabled = st.checkbox(
                        section.get("type", ""),
                        value=section.get("enabled", True),
                        key=f"deck_en_{i}",
                    )
                with col4:
                    title = st.text_input(
                        "Title",
                        value=section.get("title", ""),
                        key=f"deck_title_{i}",
                        label_visibility="collapsed",
                    )
                with col5:
                    bounds = reg_bounds(section.get("type", ""))
                    if bounds is not None:
                        lo, hi = bounds
                        current_count = section.get("count", lo)
                        count = st.number_input(
                            "Count",
                            min_value=lo,
                            max_value=hi,
                            value=int(current_count) if current_count else lo,
                            key=f"deck_count_{i}",
                            label_visibility="collapsed",
                        )
                    else:
                        count = None
                with col6:
                    st.write(f"`{section.get('type', '')}`")

                new_sec = {"type": section.get("type", ""), "enabled": enabled, "title": title}
                if count is not None:
                    new_sec["count"] = count
                updated_sections.append(new_sec)

        # Add section
        st.subheader("Add section")
        known = registry_types()
        existing_types = {s.get("type") for s in sections}
        available = [t for t in known if t not in existing_types]
        if available:
            new_type = st.selectbox("Section type", options=["(select)"] + available, key="deck_new_type")
            if st.button("Add", key="deck_add_btn") and new_type != "(select)":
                bounds = reg_bounds(new_type)
                new_sec = {"type": new_type, "enabled": True, "title": new_type.replace("_", " ").title()}
                if bounds:
                    new_sec["count"] = bounds[0]
                updated_sections.append(new_sec)
                config_save("deck_layout", {"sections": updated_sections})
                st.success(f"Added section: {new_type}")
                st.rerun()
        else:
            st.caption("All known section types are already in the deck.")

        # Preview
        with st.expander("Slide preview"):
            enabled_count = sum(1 for s in updated_sections if s.get("enabled", True))
            st.write(f"**{enabled_count} slides** will be generated:")
            for s in updated_sections:
                if s.get("enabled", True):
                    count_str = f" × {s['count']}" if s.get("count") else ""
                    st.write(f"  • {s.get('title', s.get('type', ''))}{count_str}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Save", key="deck_save"):
                errors = validate_layout({"sections": updated_sections})
                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    config_save("deck_layout", {"sections": updated_sections})
                    st.success("Saved.")
        with col2:
            if st.button("Reset to default", key="deck_reset"):
                config_reset("deck_layout")
                st.success("Reset.")
                st.rerun()
        with col3:
            if st.button("Revert", key="deck_revert"):
                st.rerun()
        with col4:
            if st.button("Diff vs default", key="deck_diff"):
                diff = diff_vs_default("deck_layout")
                st.text(diff if diff else "(no differences)")


# ── Tab 5: Cycle Report ───────────────────────────────────────────────────────

def _build_cycle_report() -> str:
    """Generate a markdown cycle report from session metrics."""
    m = _metrics()
    stages_order = ["observe", "derive", "research", "synthesize", "distill"]
    now = datetime.utcnow().isoformat()

    lines = [
        "# Perception Engine — Cycle Report",
        f"Generated: {now} UTC",
        f"Session started: {m.get('session_start', 'n/a')}",
        "",
        "---",
        "",
        "## Pipeline Summary",
        "",
        "| Stage | Status | Duration |",
        "|-------|--------|----------|",
    ]
    total_duration = 0.0
    for stage in stages_order:
        info = m["stages"].get(stage, {})
        if not info:
            lines.append(f"| {stage.upper()} | — not run — | — |")
            continue
        status = "✅ Success" if info.get("success") else f"❌ Failed: {info.get('error', '')[:60]}"
        dur = info.get("duration_s", "?")
        if isinstance(dur, (int, float)):
            total_duration += dur
            dur_str = f"{dur}s"
        else:
            dur_str = str(dur)
        lines.append(f"| {stage.upper()} | {status} | {dur_str} |")

    lines += [
        f"| **TOTAL** | | **{round(total_duration, 1)}s** |",
        "",
        "---",
        "",
        "## Input Metrics",
        "",
        f"- **Documents ingested:** {m.get('docs_ingested', 0)}",
        f"- **Corpus size:** {m.get('corpus_chars', 0):,} characters",
        "",
        "---",
        "",
        "## Pipeline Metrics",
        "",
        f"- **Research questions derived:** {m.get('questions_derived', 0)}",
        f"- **Web searches executed:** {len(m.get('web_searches', []))}",
        f"- **Evidence cards collected:** {m.get('evidence_cards_collected', 0)}",
        f"- **Dossier size:** {m.get('dossier_chars', 0):,} characters",
        "",
    ]

    # Evidence card breakdown
    ec = st.session_state.get("evidence_cards") or {}
    cards = ec.get("cards", [])
    if cards:
        from collections import Counter
        dim_counts = Counter(c.get("dimension", "unknown") for c in cards)
        tag_counts = Counter(c.get("tag", "unknown") for c in cards)
        lines += [
            "### Evidence Cards by Dimension",
            "",
            "| Dimension | Count |",
            "|-----------|-------|",
        ]
        for dim, cnt in sorted(dim_counts.items()):
            lines.append(f"| {dim} | {cnt} |")
        lines += [
            "",
            "### Evidence Cards by Tag",
            "",
            "| Tag | Count |",
            "|-----|-------|",
        ]
        for tag, cnt in sorted(tag_counts.items()):
            lines.append(f"| {tag} | {cnt} |")
        lines.append("")

    # Web searches list
    searches = m.get("web_searches", [])
    if searches:
        lines += [
            "---",
            "",
            "## Web Searches Executed",
            "",
            "| # | Query | Timestamp |",
            "|---|-------|-----------|",
        ]
        for i, s in enumerate(searches, 1):
            lines.append(f"| {i} | {s.get('query', '')[:80]} | {s.get('ts', '')[:19]} |")
        lines.append("")

    # Outputs
    outputs = m.get("outputs_generated", [])
    lines += [
        "---",
        "",
        "## Outputs Generated",
        "",
    ]
    output_labels = {
        "dossier": "Brand Dossier (dossier.md)",
        "pptx": "PPTX Deck (deck.pptx)",
        "gamma_prompt": "Gamma Mega-Prompt (gamma_prompt.txt)",
    }
    if outputs:
        for o in outputs:
            lines.append(f"- ✅ {output_labels.get(o, o)}")
    else:
        lines.append("- (none yet)")
    lines.append("")

    # Signal map summary — read from metrics snapshot (survives reload)
    sm = m.get("signal_map_snapshot") or st.session_state.get("signal_map") or {}
    if sm:
        lines += [
            "---",
            "",
            "## Signal Map Summary",
            "",
            f"- **Product:** {sm.get('product_name', '')}",
            f"- **Sector:** {sm.get('sector', '')}",
            f"- **Core:** {sm.get('product_core', '')}",
            f"- **Signals detected:** {len(sm.get('signals', []))}",
            f"- **Metrics captured:** {len(sm.get('metrics', []))}",
            f"- **Tensions identified:** {len(sm.get('tensions', []))}",
            f"- **Catalysts identified:** {len(sm.get('catalysts', []))}",
            f"- **Strategic intent:** {sm.get('strategic_intent', '')}",
            "",
        ]

    # Q&A research log
    ec = st.session_state.get("evidence_cards") or {}
    qa_pairs = ec.get("qa_pairs", [])
    if qa_pairs:
        lines += [
            "---",
            "",
            "## Research Q&A Log",
            "",
        ]
        for qa in qa_pairs:
            lines += [
                f"### {qa.get('question_id','')} · [{qa.get('dimension','')}] {qa.get('question','')}",
                "",
            ]
            queries = qa.get("queries_fired", [])
            if queries:
                lines.append(f"**Queries fired:** {' · '.join(f'`{q}`' for q in queries)}")
                lines.append("")
            qa_cards = qa.get("cards", [])
            if qa_cards:
                lines.append(f"**{len(qa_cards)} evidence cards:**")
                lines.append("")
                for c in qa_cards:
                    url = c.get("url", "")
                    src = c.get("source_title", "")
                    src_link = f"[{src}]({url})" if url else src
                    lines.append(f"- **{c.get('id','')}** · {src_link}: {c.get('claim','')}")
                    if c.get("relevance"):
                        lines.append(f"  *{c['relevance']}*")
            else:
                lines.append("*No evidence cards collected for this question.*")
            lines.append("")

    # Deck spec summary
    ds = st.session_state.get("deck_spec") or {}
    if ds:
        lines += [
            "---",
            "",
            "## Deck Spec Summary",
            "",
            f"- **Product:** {ds.get('product', '')}",
            f"- **Roadmap phases:** {len(ds.get('roadmap', []))}",
            f"- **SWOT items:** {sum(len(ds.get('swot', {}).get(k, [])) for k in ['strengths','weaknesses','opportunities','threats'])}",
            f"- **Tone pillars:** {len(ds.get('pillars', []))}",
            f"- **Vocab swaps:** {len(ds.get('vocab', []))}",
            f"- **Grapevine items:** {len(ds.get('grapevine', []))}",
            "",
        ]

    lines += [
        "---",
        "",
        "*This report was generated automatically by Perception Engine.*",
        "*Share it with Claude Code to get optimization suggestions for your next run.*",
    ]

    return "\n".join(lines)


def tab_cycle_report():
    st.header("Cycle Report")
    st.caption("Usage statistics and pipeline metrics for this session. Share with Claude Code to optimize future runs.")

    m = _metrics()
    stages_order = ["observe", "derive", "research", "synthesize", "distill"]

    # ── Quick stats ──────────────────────────────────────────────────────────
    completed = sum(1 for s in stages_order if m["stages"].get(s, {}).get("success"))
    total_dur = sum(
        m["stages"][s].get("duration_s", 0)
        for s in stages_order
        if isinstance(m["stages"].get(s, {}).get("duration_s"), (int, float))
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Stages completed", f"{completed}/5")
    col2.metric("Total duration", f"{round(total_dur)}s")
    col3.metric("Web searches", len(m.get("web_searches", [])))
    col4.metric("Evidence cards", m.get("evidence_cards_collected", 0))
    col5.metric("Outputs", len(m.get("outputs_generated", [])))

    st.divider()

    # ── Stage timeline ───────────────────────────────────────────────────────
    st.subheader("Stage Timeline")
    for stage in stages_order:
        info = m["stages"].get(stage, {})
        if not info:
            st.markdown(f"**{stage.upper()}** — not run")
            continue
        ok = info.get("success", False)
        dur = info.get("duration_s", "?")
        icon = "✅" if ok else "❌"
        err = f" · error: {info.get('error','')[:80]}" if not ok else ""
        st.markdown(f"{icon} **{stage.upper()}** · {dur}s{err}")

    st.divider()

    # ── Evidence breakdown ───────────────────────────────────────────────────
    ec = st.session_state.get("evidence_cards") or {}
    cards = ec.get("cards", [])
    if cards:
        import pandas as pd
        from collections import Counter
        st.subheader("Evidence Cards")
        col_a, col_b = st.columns(2)
        with col_a:
            dim_data = Counter(c.get("dimension", "unknown") for c in cards)
            st.markdown("**By dimension**")
            st.dataframe(
                pd.DataFrame(dim_data.items(), columns=["Dimension", "Count"]).sort_values("Count", ascending=False),
                use_container_width=True, hide_index=True,
            )
        with col_b:
            tag_data = Counter(c.get("tag", "unknown") for c in cards)
            st.markdown("**By tag**")
            st.dataframe(
                pd.DataFrame(tag_data.items(), columns=["Tag", "Count"]).sort_values("Count", ascending=False),
                use_container_width=True, hide_index=True,
            )

    # ── Web searches ─────────────────────────────────────────────────────────
    searches = m.get("web_searches", [])
    if searches:
        import pandas as pd
        st.subheader("Web Searches")
        st.dataframe(
            pd.DataFrame(searches)[["stage", "query", "ts"]].rename(columns={"ts": "timestamp"}),
            use_container_width=True, hide_index=True,
        )

    st.divider()

    # ── Generate & download report ───────────────────────────────────────────
    st.subheader("Export Report")
    if st.button("Generate cycle report", key="btn_cycle_report"):
        st.session_state["cycle_report_md"] = _build_cycle_report()
        _save_artifact("cycle_report.md", st.session_state["cycle_report_md"])

    if st.session_state.get("cycle_report_md"):
        st.markdown(st.session_state["cycle_report_md"])
        st.download_button(
            "Download cycle_report.md",
            data=st.session_state["cycle_report_md"],
            file_name="cycle_report.md",
            mime="text/markdown",
            key="dl_cycle_report",
        )
        st.info("Tip: paste this report into Claude Code and ask for optimization suggestions based on the metrics.")


# ── Main ──────────────────────────────────────────────────────────────────────

def _clear_session():
    """Wipe all pipeline data from session and disk."""
    import shutil
    keys_to_clear = [
        "corpus", "signal_map", "research_plan", "evidence_cards",
        "dossier", "deck_spec", "proposed_tokens", "run_dir",
        "gamma_prompt", "cycle_report_md",
    ]
    for k in keys_to_clear:
        st.session_state[k] = None
    # Reset metrics
    st.session_state.cycle_metrics = {
        "session_start": datetime.utcnow().isoformat(),
        "stages": {},
        "llm_calls": [],
        "web_searches": [],
        "docs_ingested": 0,
        "corpus_chars": 0,
        "questions_derived": 0,
        "evidence_cards_collected": 0,
        "dossier_chars": 0,
        "outputs_generated": [],
    }
    # Delete run artifacts from disk
    try:
        if RUNS_DIR.exists():
            shutil.rmtree(RUNS_DIR)
            RUNS_DIR.mkdir(exist_ok=True)
    except Exception:
        pass


def main():
    col_title, col_clear = st.columns([8, 1])
    with col_title:
        st.title("🧭 Perception Engine")
        st.caption("Brand-intelligence pipeline · OBSERVE → DERIVE → RESEARCH → SYNTHESIZE → DISTILL")
    with col_clear:
        st.markdown("<div style='padding-top:1.4rem'></div>", unsafe_allow_html=True)
        if st.button("Clear session", key="btn_clear_session", help="Efface toutes les données de la session et du disque"):
            _clear_session()
            st.success("Session effacée.")
            st.rerun()

    # Confidentiality notice
    st.markdown("""
<div style='background:#1a1200;border-radius:12px;padding:0.6rem 1.1rem;margin-bottom:1rem;font-size:0.8rem;color:#e8d5a0;border:1px solid #3a2800;'>
🔒 <strong style="color:#f0e0b0;">Confidentialité</strong> — Les données uploadées restent dans cette session et sont supprimées à sa fermeture. Utilisez <em>Clear session</em> pour effacer immédiatement.
</div>
""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Run", "Prompt Studio", "Brand Studio", "Deck Studio", "Cycle Report"])

    with tab1:
        tab_run()
    with tab2:
        tab_prompt_studio()
    with tab3:
        tab_brand_studio()
    with tab4:
        tab_deck_studio()
    with tab5:
        tab_cycle_report()


if __name__ == "__main__":
    main()
