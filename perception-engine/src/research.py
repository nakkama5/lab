"""RESEARCH stage: gather evidence cards via web search."""
from __future__ import annotations

import json
from typing import Callable

from src import llm, prompt_store
from src.schemas import EvidenceCards


def run_research(
    research_plan: dict,
    model: str | None = None,
    progress_cb: Callable[[str, list[dict]], None] | None = None,
) -> dict:
    """Run RESEARCH stage. Returns evidence_cards dict with search_log.

    progress_cb(question_text, search_events) called after each question
    so the UI can display live search queries and sources.
    """
    if model is None:
        model = llm.MODEL_RESEARCH

    system = prompt_store.load("common")
    all_cards: list[dict] = []
    search_log: list[dict] = []
    seen_urls: set[str] = set()
    card_counter = 1

    questions = research_plan.get("questions", [])
    for question_data in questions:
        question_text = question_data.get("question", "")
        question_id = question_data.get("id", "Q?")
        dimension = question_data.get("dimension", "market")

        user = prompt_store.compiled("research", question=question_text)

        try:
            raw_text, search_events = llm.call_with_web_search_full(
                system=system,
                user=user,
                model=model,
                max_tokens=4096,
            )
        except Exception as e:
            print(f"[research] Failed for question {question_id}: {e}")
            continue

        # Notify UI with live search events
        if progress_cb:
            progress_cb(question_text, search_events)

        # Log searches
        for ev in search_events:
            search_log.append({
                "question_id": question_id,
                "question": question_text,
                "query": ev.get("query", ""),
                "results": ev.get("results", []),
            })

        # Parse JSON cards from raw_text
        try:
            raw = llm.parse_json(raw_text)
        except Exception:
            raw = {}

        if isinstance(raw, dict):
            cards = raw.get("cards", [])
        elif isinstance(raw, list):
            cards = raw
        else:
            cards = []

        # Attach sources from search results to cards that lack a URL
        all_search_urls = [
            r for ev in search_events for r in ev.get("results", [])
        ]

        for card_data in cards:
            url = card_data.get("url", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)

            card_data["id"] = f"E{card_counter}"
            card_counter += 1
            if not card_data.get("question_id"):
                card_data["question_id"] = question_id
            if not card_data.get("dimension"):
                card_data["dimension"] = dimension

            all_cards.append(card_data)

        # Also surface raw search results as lightweight reference cards
        # (deduplicated, distinct from LLM-synthesised cards)
        for r in all_search_urls:
            rurl = r.get("url", "")
            if not rurl or rurl in seen_urls:
                continue
            seen_urls.add(rurl)
            all_cards.append({
                "id": f"E{card_counter}",
                "dimension": dimension,
                "claim": r.get("snippet", ""),
                "source_title": r.get("title", ""),
                "url": rurl,
                "tag": "SECTORAL",
                "question_id": question_id,
                "_raw_source": True,
            })
            card_counter += 1

    result = {"cards": all_cards, "search_log": search_log}
    validated = EvidenceCards(cards=all_cards)
    return {**validated.model_dump(), "search_log": search_log}
