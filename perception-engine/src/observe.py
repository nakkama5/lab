"""OBSERVE stage: extract signal_map from corpus."""
from __future__ import annotations

import json

from src import llm, prompt_store
from src.ingest import corpus_to_text
from src.schemas import SignalMap


def run_observe(corpus: list[dict], model: str | None = None) -> dict:
    """Run OBSERVE stage. Returns signal_map dict validated against SignalMap."""
    if model is None:
        model = llm.MODEL_OBSERVE

    corpus_text = corpus_to_text(corpus)
    system = prompt_store.load("common")
    user = prompt_store.compiled("observe", corpus=corpus_text)

    raw = llm.call_json(system=system, user=user, model=model, max_tokens=4096)

    # Coerce common LLM variations before validating
    if isinstance(raw, dict):
        # singular → plural aliases
        for singular, plural in [("tension", "tensions"), ("catalyst", "catalysts"),
                                  ("signal", "signals"), ("metric", "metrics")]:
            if singular in raw and plural not in raw:
                raw[plural] = raw.pop(singular)
        # wrap bare strings in lists
        for field in ("tensions", "catalysts"):
            if isinstance(raw.get(field), str):
                raw[field] = [raw[field]] if raw[field] else []

    validated = SignalMap.model_validate(raw)
    return validated.model_dump()
