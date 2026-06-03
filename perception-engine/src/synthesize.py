"""SYNTHESIZE stage: produce executive dossier markdown."""
from __future__ import annotations

import json

from src import llm, prompt_store
from src.ingest import corpus_to_text


def run_synthesize(corpus: list[dict], evidence_cards: dict, model: str | None = None) -> str:
    """Run SYNTHESIZE stage. Returns dossier as markdown string."""
    if model is None:
        model = llm.MODEL_SYNTHESIZE

    corpus_text = corpus_to_text(corpus)
    evidence_text = json.dumps(evidence_cards, ensure_ascii=False, indent=2)

    system = prompt_store.load("common")
    user = prompt_store.compiled(
        "synthesize",
        corpus=corpus_text,
        evidence_cards=evidence_text,
    )

    dossier = llm.call(system=system, user=user, model=model, max_tokens=8192)
    return dossier
