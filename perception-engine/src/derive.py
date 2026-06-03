"""DERIVE stage: produce research_plan from signal_map."""
from __future__ import annotations

import json

from src import llm, prompt_store
from src.schemas import ResearchPlan


def run_derive(signal_map: dict, model: str | None = None) -> dict:
    if model is None:
        model = llm.MODEL_DERIVE

    signal_map_text = json.dumps(signal_map, ensure_ascii=False)
    system = prompt_store.load("common")
    user = prompt_store.compiled("derive", signal_map=signal_map_text)

    raw = llm.call_json(system=system, user=user, model=model, max_tokens=4096)

    validated = ResearchPlan.model_validate(raw)
    return validated.model_dump()
