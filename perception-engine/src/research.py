"""RESEARCH stage: gather evidence cards via web search."""
from __future__ import annotations

import json

from src import llm, prompt_store
from src.schemas import EvidenceCards, EvidenceCard


def run_research(research_plan: dict, model: str | None = None) -> dict:
    """Run RESEARCH stage. Returns evidence_cards dict."""
    if model is None:
        model = llm.MODEL_RESEARCH

    system = prompt_store.load("common")
    all_cards: list[dict] = []
    seen_urls: set[str] = set()
    card_counter = 1

    questions = research_plan.get("questions", [])
    for question_data in questions:
        question_text = question_data.get("question", "")
        question_id = question_data.get("id", "Q?")
        dimension = question_data.get("dimension", "market")

        user = prompt_store.compiled("research", question=question_text)

        try:
            raw = llm.call_json_with_web_search(
                system=system,
                user=user,
                model=model,
                max_tokens=4096,
            )
        except Exception as e:
            print(f"[research] Failed for question {question_id}: {e}")
            continue

        # Handle both {"cards": [...]} and [...] responses
        if isinstance(raw, dict):
            cards = raw.get("cards", [])
        elif isinstance(raw, list):
            cards = raw
        else:
            cards = []

        for card_data in cards:
            url = card_data.get("url", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            # Ensure required fields
            card_data["id"] = f"E{card_counter}"
            card_counter += 1
            if not card_data.get("question_id"):
                card_data["question_id"] = question_id
            if not card_data.get("dimension"):
                card_data["dimension"] = dimension

            all_cards.append(card_data)

    result = {"cards": all_cards}
    # Validate
    validated = EvidenceCards(**result)
    return validated.model_dump()
