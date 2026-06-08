"""RESEARCH stage: web due diligence on a prospect."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from src import llm

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def run_research(
    prospect_name: str,
    analyst_notes: str = "",
    model: str | None = None,
    progress_cb=None,
) -> dict:
    """Run web research on the prospect. Returns structured research dict."""
    if model is None:
        model = llm.MODEL_RESEARCH

    system = _load("common")

    notes_block = ""
    if analyst_notes.strip():
        notes_block = f"\nNOTES TERRAIN (informations déjà connues sur ce prospect) :\n{analyst_notes.strip()}\n"

    user = (
        _load("research")
        .replace("{prospect_name}", prospect_name)
        .replace("{analyst_notes_block}", notes_block)
    )

    print(f"[researcher] Starting research for: {prospect_name}", file=sys.stderr)

    try:
        raw_text, search_events = llm.call_with_web_search_full(
            system=system,
            user=user,
            model=model,
            max_tokens=8192,
        )
    except Exception as e:
        print(f"[researcher] Research failed: {e}", file=sys.stderr)
        raise

    print(f"[researcher] Searches fired: {len(search_events)}", file=sys.stderr)

    if progress_cb:
        progress_cb(search_events)

    try:
        data = llm.parse_json(raw_text)
    except Exception:
        data = {"prospect_name": prospect_name, "raw_text": raw_text}

    data["_search_events"] = search_events
    data["_searches_count"] = len(search_events)
    return data
