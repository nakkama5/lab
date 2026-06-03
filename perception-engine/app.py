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
            "stages": {},       # stage -> {start, end, duration_s, success, error}
            "llm_calls": [],    # [{stage, model, input_tokens, output_tokens, cost_usd, ts}]
            "web_searches": [], # [{stage, query, ts}]
            "docs_ingested": 0,
            "corpus_chars": 0,
            "questions_derived": 0,
            "evidence_cards_collected": 0,
            "dossier_chars": 0,
            "outputs_generated": [],  # ["pptx", "gamma_prompt", "dossier"]
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

                from src.observe import run_observe
                with st.spinner("Running OBSERVE…"):
                    signal_map = run_observe(corpus, model=models["observe"])

                st.session_state.signal_map = signal_map
                _save_artifact("signal_map.json", signal_map)
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

    if st.button("Run RESEARCH", key="btn_research"):
        if not st.session_state.research_plan:
            st.error("Run DERIVE first.")
        else:
            _stage_start("research")
            try:
                from src.research import run_research
                questions = st.session_state.research_plan.get("questions", [])
                progress = st.progress(0)
                cards_all: list[dict] = []
                for i, q in enumerate(questions):
                    with st.spinner(f"Researching Q{i+1}/{len(questions)}: {q.get('question', '')[:60]}…"):
                        partial_plan = {"questions": [q]}
                        result = run_research(partial_plan, model=models["research"])
                        cards_all.extend(result.get("cards", []))
                        # track web searches
                        for sq in q.get("queries", []):
                            _metrics()["web_searches"].append({
                                "stage": "research",
                                "query": sq,
                                "ts": datetime.utcnow().isoformat(),
                            })
                    progress.progress((i + 1) / len(questions))

                evidence_cards = {"cards": cards_all}
                st.session_state.evidence_cards = evidence_cards
                _save_artifact("evidence_cards.json", evidence_cards)
                _metrics()["evidence_cards_collected"] = len(cards_all)
                _stage_end("research", success=True)
                st.success(f"RESEARCH complete — {len(cards_all)} evidence cards collected.")
            except Exception as e:
                _stage_end("research", success=False, error=str(e))
                st.error(f"RESEARCH failed: {e}")
                raise

    if st.session_state.evidence_cards:
        cards = st.session_state.evidence_cards.get("cards", [])
        if cards:
            import pandas as pd
            df = pd.DataFrame([
                {
                    "ID": c.get("id", ""),
                    "Claim": c.get("claim", "")[:100],
                    "Source": c.get("source_title", ""),
                    "URL": c.get("url", ""),
                    "Tag": c.get("tag", ""),
                    "Dimension": c.get("dimension", ""),
                }
                for c in cards
            ])
            st.dataframe(df, use_container_width=True)

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
            st.session_state["gamma_prompt"] = _build_gamma_prompt()
            if "gamma_prompt" not in _metrics()["outputs_generated"]:
                _metrics()["outputs_generated"].append("gamma_prompt")
        if st.session_state.get("gamma_prompt"):
            st.text_area(
                "Copy this prompt and paste it into Claude Code ↓",
                value=st.session_state["gamma_prompt"],
                height=300,
                key="ta_gamma_prompt",
            )
            st.download_button(
                "Download prompt as .txt",
                data=st.session_state["gamma_prompt"],
                file_name="gamma_prompt.txt",
                mime="text/plain",
            )


def _build_gamma_prompt() -> str:
    """Assemble a full Gamma generation prompt with brand tokens and card structure."""
    from src.config_store import load as config_load

    deck_spec = st.session_state.deck_spec or {}
    dossier = st.session_state.dossier or ""

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

    # ── Brand identity block ──────────────────────────────────────────────────
    palette = brand_tokens.get("palette") or {}
    typography = brand_tokens.get("type") or {}
    brand_rules = brand_tokens.get("rules", "")
    motif = brand_tokens.get("motif", "")

    color_lines = []
    for role, val in palette.items():
        if isinstance(val, dict):
            hex_val = val.get("hex", "")
            role_desc = val.get("role", role)
            why = val.get("why", "")
            color_lines.append(f"  - #{hex_val} ({role_desc}){': ' + why if why else ''}")
        else:
            color_lines.append(f"  - {role}: {val}")

    display_font = typography.get("display", "Georgia") if isinstance(typography, dict) else "Georgia"
    body_font = typography.get("body", "Calibri") if isinstance(typography, dict) else "Calibri"

    # Build visual style from motif + brand rules
    visual_style = motif or "premium editorial"
    if brand_rules:
        visual_style += f". {brand_rules[:300]}"

    # ── Vocabulary swap dict for inline use ───────────────────────────────────
    vocab_map = {}
    for v in vocab:
        k = v.get("from", v.get("from_", ""))
        t = v.get("to", "")
        if k and t:
            vocab_map[k] = t

    def apply_vocab(text: str) -> str:
        for k, v in vocab_map.items():
            text = text.replace(k, v)
        return text

    # ── SWOT reframed (not raw quadrant) ─────────────────────────────────────
    strengths = swot.get("strengths") or []
    weaknesses = swot.get("weaknesses") or []
    opportunities = swot.get("opportunities") or []
    threats = swot.get("threats") or []
    gaps = weaknesses + threats  # merge into "strategic gaps"

    # ── Card-by-card structure ────────────────────────────────────────────────
    cards = []

    # Card 1 — Cover
    cards.append(f"""---CARD: Cover---
Title: {product}
Subtitle: {taglines.get('punchy', taglines.get('visionary', ''))}
Visual: full-bleed hero image, style: {visual_style}""")

    # Card 2 — The Hook (outcome tagline)
    if taglines.get("outcome"):
        cards.append(f"""---CARD: The Hook---
Headline: {apply_vocab(taglines['outcome'])}
Body: {apply_vocab(micro or elevator[:200])}
Visual: abstract mood image evoking transformation, style: {visual_style}""")

    # Card 3 — The Problem (legacy)
    if legacy:
        legacy_text = "\n".join(f"- {apply_vocab(l)}" for l in legacy[:4])
        cards.append(f"""---CARD: The Old Playbook (What Broke)---
Headline: The world changed. The playbook didn't.
Body:
{legacy_text}
Visual: muted, desaturated image suggesting stagnation or complexity""")

    # Card 4 — The Shift (evolution)
    if evolution:
        evo_text = "\n".join(f"- {apply_vocab(e)}" for e in evolution[:4])
        cards.append(f"""---CARD: The New Operating System---
Headline: {apply_vocab(taglines.get('visionary', 'The shift has already happened.'))}
Body:
{evo_text}
Visual: bold, bright, forward-motion image, style: {visual_style}""")

    # Card 5 — Elevator pitch
    if elevator:
        cards.append(f"""---CARD: What It Is---
Headline: {apply_vocab(product)} in one paragraph
Body: {apply_vocab(elevator)}
Visual: clean product/platform illustration or icon grid""")

    # Card 6 — Core metaphor
    if metaphor.get("statement"):
        cards.append(f"""---CARD: The Core Metaphor---
Headline: {apply_vocab(metaphor['statement'])}
Body: {apply_vocab(metaphor.get('rationale', ''))}
Visual: image literalising the metaphor, style: {visual_style}""")

    # Card 7 — Metrics
    if metrics:
        metric_lines = "\n".join(f"- **{m.get('num','')}** — {apply_vocab(m.get('label',''))}" for m in metrics)
        cards.append(f"""---CARD: The Numbers That Matter---
Headline: Proof, not promise.
Body:
{metric_lines}
Visual: data-driven graphic or large-number typographic layout""")

    # Card 8 — Proprietary moat (strengths reframed)
    if strengths:
        moat_text = "\n".join(f"- {apply_vocab(s)}" for s in strengths[:4])
        cards.append(f"""---CARD: The Proprietary Moat---
Headline: What no one else can replicate.
Body:
{moat_text}
Visual: fortress or precision-craft image, style: {visual_style}""")

    # Card 9 — Strategic gaps (weaknesses+threats reframed as investment thesis)
    if gaps:
        gaps_text = "\n".join(f"- {apply_vocab(g)}" for g in gaps[:4])
        cards.append(f"""---CARD: Strategic Gaps — Why They Make the Case---
Headline: The gaps that justify the investment.
Body: These are not liabilities. They are the whitespace this roadmap is built to close.
{gaps_text}
Visual: tension/contrast image — light breaking through""")

    # Card 10 — Opportunity (from SWOT)
    if opportunities:
        opp_text = "\n".join(f"- {apply_vocab(o)}" for o in opportunities[:4])
        cards.append(f"""---CARD: The Opportunity Window---
Headline: The market is ready. The timing is now.
Body:
{opp_text}
Visual: open horizon or expansive landscape, style: {visual_style}""")

    # Card 11 — Social proof / grapevine
    if grapevine:
        proof_text = "\n".join(f'> "{apply_vocab(g["desc"])}" — {g["title"]}' for g in grapevine[:3])
        cards.append(f"""---CARD: What the Market Is Already Saying---
Headline: The signal is there.
Body:
{proof_text}
Visual: subtle editorial collage or quote typography""")

    # Cards 12–N — Roadmap (one card per phase)
    for r in roadmap:
        pts = "\n".join(f"- {apply_vocab(pt)}" for pt in r.get("points", [])[:4])
        cards.append(f"""---CARD: {r.get('phase','')} — {apply_vocab(r.get('name',''))} ({r.get('when','')})---
Body:
{pts}
Visual: timeline or progress graphic""")

    # Card — Manifesto
    if manifesto:
        cards.append(f"""---CARD: Manifesto---
Headline: We believe.
Body: {apply_vocab(manifesto[:600])}
Visual: full-bleed typographic statement, style: {visual_style}""")

    # Card — Closing
    cards.append(f"""---CARD: Closing---
Headline: {apply_vocab(taglines.get('visionary', product))}
Subhead: {apply_vocab(taglines.get('punchy', ''))}
CTA: Let's build it together.
Visual: full-bleed closing image, style: {visual_style}""")

    # ── Assemble full prompt ──────────────────────────────────────────────────
    vocab_swap_lines = "\n".join(f"  {k} → {v}" for k, v in vocab_map.items())
    pillar_lines = "\n".join(
        f"  - {p.get('name','')}: SAY «{p.get('do_say','')}» / NEVER SAY «{p.get('dont_say','')}»"
        for p in pillars
    )
    color_block = "\n".join(color_lines) if color_lines else "  (no palette defined)"
    cards_block = "\n\n".join(cards)

    prompt = f"""Generate a Gamma presentation for: {product}

Use the `generate` tool (mcp__e2a76a26-c84d-46b0-a627-996cea47643c__generate).

═══════════════════════════════════════
BRAND IDENTITY — apply to every card
═══════════════════════════════════════
Primary font (display/titles): {display_font}
Body font: {body_font}
Color palette:
{color_block}
Visual motif / image style: {visual_style}

VOCABULARY — always use these terms (never the legacy term):
{vocab_swap_lines if vocab_swap_lines else "  (none defined)"}

TONE PILLARS — follow strictly:
{pillar_lines if pillar_lines else "  (none defined)"}

═══════════════════════════════════════
DECK STRUCTURE — one card per section
Use explicit card breaks so Gamma renders each as a separate slide.
═══════════════════════════════════════

{cards_block}

═══════════════════════════════════════
GENERATION RULES
═══════════════════════════════════════
- Each ---CARD--- block = one Gamma card/slide. Do not merge cards.
- Apply brand colors to backgrounds and accents throughout.
- Use {display_font} for all headlines, {body_font} for body text.
- Generate images using the custom style: {visual_style}
- Do NOT use generic stock-photo presets — use the custom image style above.
- Apply vocabulary swaps everywhere (including image prompts and alt text).
- Keep tone pillars in mind for every word choice.
- The SWOT is reframed (moat + strategic gaps + opportunity), not a raw 4-quadrant grid.
"""
    return prompt


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
                color = "green" if present else "red"
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

    # Signal map summary
    sm = st.session_state.get("signal_map") or {}
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
            "",
        ]

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

def main():
    st.title("🧭 Perception Engine")
    st.caption("Internal brand-intelligence pipeline · Ingest → OBSERVE → DERIVE → RESEARCH → SYNTHESIZE → DISTILL")

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
