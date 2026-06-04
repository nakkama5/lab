"""DERIVE stage: produce research_plan from signal_map."""
from __future__ import annotations

import json
import sys

from src import llm, prompt_store
from src.schemas import ResearchPlan


def run_derive(signal_map: dict, model: str | None = None) -> dict:
    if model is None:
        model = llm.MODEL_DERIVE

    signal_map_text = json.dumps(signal_map, ensure_ascii=False)
    system = prompt_store.load("common")
    user = prompt_store.compiled("derive", signal_map=signal_map_text)

    raw = llm.call_json(system=system, user=user, model=model, max_tokens=4096)

    print(f"[derive] raw keys: {list(raw.keys()) if isinstance(raw, dict) else type(raw)}", file=sys.stderr)

    validated = ResearchPlan.model_validate(raw)
    n = len(validated.questions)
    print(f"[derive] questions validated: {n}", file=sys.stderr)
    if n == 0:
        print(f"[derive] WARNING: 0 questions — raw response was: {json.dumps(raw)[:500]}", file=sys.stderr)

    return validated.model_dump()
