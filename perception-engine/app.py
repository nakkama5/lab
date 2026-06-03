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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


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

            from src.observe import run_observe
            with st.spinner("Running OBSERVE…"):
                signal_map = run_observe(corpus, model=models["observe"])

            st.session_state.signal_map = signal_map
            _save_artifact("signal_map.json", signal_map)
            st.success("OBSERVE complete.")

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
            from src.derive import run_derive
            with st.spinner("Running DERIVE…"):
                research_plan = run_derive(st.session_state.signal_map, model=models["derive"])
            st.session_state.research_plan = research_plan
            _save_artifact("research_plan.json", research_plan)
            st.success("DERIVE complete.")

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
            from src.research import run_research
            questions = st.session_state.research_plan.get("questions", [])
            progress = st.progress(0)
            cards_all: list[dict] = []
            for i, q in enumerate(questions):
                with st.spinner(f"Researching Q{i+1}/{len(questions)}: {q.get('question', '')[:60]}…"):
                    partial_plan = {"questions": [q]}
                    result = run_research(partial_plan, model=models["research"])
                    cards_all.extend(result.get("cards", []))
                progress.progress((i + 1) / len(questions))

            evidence_cards = {"cards": cards_all}
            st.session_state.evidence_cards = evidence_cards
            _save_artifact("evidence_cards.json", evidence_cards)
            st.success(f"RESEARCH complete — {len(cards_all)} evidence cards collected.")

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
            from src.synthesize import run_synthesize
            with st.spinner("Running SYNTHESIZE…"):
                dossier = run_synthesize(
                    st.session_state.corpus,
                    st.session_state.evidence_cards,
                    model=models["synthesize"],
                )
            st.session_state.dossier = dossier
            _save_artifact("dossier.md", dossier)
            st.success("SYNTHESIZE complete.")

    if st.session_state.dossier:
        with st.expander("Dossier preview", expanded=True):
            st.markdown(st.session_state.dossier)
        st.download_button(
            "Download dossier.md",
            data=st.session_state.dossier,
            file_name="dossier.md",
            mime="text/markdown",
        )

    # ── DISTILL ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Step 5 · DISTILL")
    st.caption(f"Prompt: `prompts/distill.md` · Model: `{models['distill']}`")

    if st.button("Run DISTILL", key="btn_distill"):
        if not st.session_state.dossier:
            st.error("Run SYNTHESIZE first.")
        else:
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
            st.success("DISTILL complete.")

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


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.title("🧭 Perception Engine")
    st.caption("Internal brand-intelligence pipeline · Ingest → OBSERVE → DERIVE → RESEARCH → SYNTHESIZE → DISTILL")

    tab1, tab2, tab3, tab4 = st.tabs(["Run", "Prompt Studio", "Brand Studio", "Deck Studio"])

    with tab1:
        tab_run()
    with tab2:
        tab_prompt_studio()
    with tab3:
        tab_brand_studio()
    with tab4:
        tab_deck_studio()


if __name__ == "__main__":
    main()
