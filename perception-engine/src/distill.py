"""DISTILL stage: produce deck_spec and brand_tokens from dossier."""
from __future__ import annotations

import json
from pathlib import Path

from src import llm, prompt_store
from src.schemas import DeckSpec, BrandTokens

# deck_spec schema as string for the prompt
DECK_SCHEMA = json.dumps({
    "product": "string",
    "taglines": {"outcome": "", "visionary": "", "punchy": ""},
    "micro": "", "elevator": "",
    "metrics": [{"num": "", "label": ""}],
    "legacy": ["", ""], "evolution": ["", ""],
    "jargon_rows": [{"feature": "", "capability": "", "benefit": "", "kpi": ""}],
    "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
    "metaphor": {"statement": "", "rationale": ""},
    "pillars": [{"name": "", "do_say": "", "dont_say": ""}],
    "vocab": [{"from": "", "to": ""}],
    "manifesto": "",
    "grapevine": [{"title": "", "desc": ""}],
    "roadmap": [{"phase": "", "name": "", "when": "", "points": ["", "", ""]}],
}, ensure_ascii=False)


def run_distill(
    dossier: str,
    brand_tokens: dict,
    deck_layout: dict,
    model: str | None = None,
) -> tuple[dict, dict]:
    """Run DISTILL stage.

    Returns (deck_spec, proposed_brand_tokens) as dicts.
    """
    if model is None:
        model = llm.MODEL_DISTILL

    brand_tokens_text = json.dumps(brand_tokens, ensure_ascii=False)
    system = prompt_store.load("common")

    # Ask LLM to produce a JSON object with both deck_spec and brand_tokens keys
    combined_schema = json.dumps({
        "deck_spec": json.loads(DECK_SCHEMA),
        "brand_tokens": {
            "palette": {
                "color_name": {
                    "hex": "6-digit hex",
                    "role": "string",
                    "why": "string",
                }
            },
            "type": {"display": "font name", "body": "font name"},
            "rules": "string",
            "motif": "string",
        },
    }, ensure_ascii=False)

    user = prompt_store.compiled(
        "distill",
        dossier=dossier,
        deck_schema=combined_schema,
        brand_tokens=brand_tokens_text,
    )

    raw = llm.call_json(system=system, user=user, model=model, max_tokens=8192)

    # Extract deck_spec and brand_tokens from response
    if isinstance(raw, dict) and "deck_spec" in raw:
        deck_spec_raw = raw["deck_spec"]
        proposed_tokens_raw = raw.get("brand_tokens", brand_tokens)
    else:
        # LLM returned just the deck_spec
        deck_spec_raw = raw
        proposed_tokens_raw = brand_tokens

    # Validate deck_spec
    # Handle vocab items: LLM may use "from" key which conflicts with Python keyword
    vocab_items = deck_spec_raw.get("vocab", [])
    normalized_vocab = []
    for item in vocab_items:
        if isinstance(item, dict):
            normalized_vocab.append({
                "from": item.get("from", item.get("from_", "")),
                "to": item.get("to", ""),
            })
    if normalized_vocab:
        deck_spec_raw["vocab"] = normalized_vocab

    validated_deck = DeckSpec(**deck_spec_raw)
    deck_spec_out = validated_deck.model_dump()

    # Restore "from" key (pydantic may serialize as "from_")
    if "vocab" in deck_spec_out:
        for item in deck_spec_out["vocab"]:
            if "from_" in item:
                item["from"] = item.pop("from_")

    # Validate brand tokens
    try:
        validated_tokens = BrandTokens(**proposed_tokens_raw)
        tokens_out = validated_tokens.model_dump()
    except Exception:
        tokens_out = brand_tokens

    return deck_spec_out, tokens_out


def build_pptx(
    deck_spec: dict,
    brand_tokens: dict,
    deck_layout: dict,
    output_path: str,
) -> None:
    """Build the PPTX file from deck_spec, brand_tokens, and layout."""
    from src.pptx_render import render_deck
    render_deck(deck_spec, brand_tokens, deck_layout, output_path)
