"""RESEARCH stage: gather evidence cards via web search."""
from __future__ import annotations

import json
import re
import sys
from typing import Callable

from src import llm, prompt_store
from src.schemas import EvidenceCards


# Words that signal internal/confidential data leaking into a search query
_CONFIDENTIAL_PATTERNS = re.compile(
    r"\b(internal|proprietary|confidential|secret|private|our product|our client|"
    r"our company|our platform|we are|we have|we built|our team)\b",
    re.IGNORECASE,
)


def _sanitize_query(query: str, product_name: str = "") -> str:
    """Remove confidential signals from a web search query.

    Strips the product name (replaced with generic 'platform') and any
    internal-sounding phrases before the query hits the web.
    """
    q = query
    # Remove product name
    if product_name:
        q = re.sub(re.escape(product_name), "platform", q, flags=re.IGNORECASE)
    # Flag and strip confidential phrases
    if _CONFIDENTIAL_PATTERNS.search(q):
        print(f"[research] SECURITY: sanitized confidential phrase from query: {query!r}", file=sys.stderr)
        q = _CONFIDENTIAL_PATTERNS.sub("", q).strip()
    return q.strip()


def run_research(
    research_plan: dict,
    model: str | None = None,
    progress_cb: Callable[[str, list[dict]], None] | None = None,
    product_name: str = "",
) -> dict:
    """Run RESEARCH stage. Returns evidence_cards dict with search_log and qa_pairs.

    progress_cb(question_text, search_events) called after each question.
    product_name is used to sanitize queries so the product name never
    appears verbatim in a public web search.
    """
    if model is None:
        model = llm.MODEL_RESEARCH

    system = prompt_store.load("common")
    all_cards: list[dict] = []
    search_log: list[dict] = []
    qa_pairs: list[dict] = []   # [{question_id, question, dimension, cards, queries_fired}]
    seen_urls: set[str] = set()
    card_counter = 1

    questions = research_plan.get("questions", [])
    for question_data in questions:
        question_text = question_data.get("question", "")
        question_id = question_data.get("id", "Q?")
        dimension = question_data.get("dimension", "market")

        # Build prompt — question only, no internal data
        user = prompt_store.compiled("research", question=question_text)

        try:
            raw_text, search_events = llm.call_with_web_search_full(
                system=system,
                user=user,
                model=model,
                max_tokens=4096,
            )
        except Exception as e:
            print(f"[research] Failed for question {question_id}: {e}", file=sys.stderr)
            continue

        # Sanitize actual queries that were fired
        for ev in search_events:
            original = ev.get("query", "")
            ev["query"] = _sanitize_query(original, product_name)
            if ev["query"] != original:
                ev["_sanitized"] = True

        if progress_cb:
            progress_cb(question_text, search_events)

        for ev in search_events:
            search_log.append({
                "question_id": question_id,
                "question": question_text,
                "query": ev.get("query", ""),
                "results": ev.get("results", []),
                "sanitized": ev.get("_sanitized", False),
            })

        # Parse JSON cards
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

        all_search_urls = [r for ev in search_events for r in ev.get("results", [])]
        question_cards: list[dict] = []

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
            question_cards.append(card_data)

        # Raw source reference cards
        for r in all_search_urls:
            rurl = r.get("url", "")
            if not rurl or rurl in seen_urls:
                continue
            seen_urls.add(rurl)
            ref = {
                "id": f"E{card_counter}",
                "dimension": dimension,
                "claim": r.get("snippet", ""),
                "source_title": r.get("title", ""),
                "url": rurl,
                "tag": "SECTORAL",
                "question_id": question_id,
                "_raw_source": True,
            }
            all_cards.append(ref)
            card_counter += 1

        qa_pairs.append({
            "question_id": question_id,
            "dimension": dimension,
            "question": question_text,
            "queries_fired": [ev.get("query", "") for ev in search_events],
            "cards": question_cards,
        })

    validated = EvidenceCards(cards=all_cards)
    return {**validated.model_dump(), "search_log": search_log, "qa_pairs": qa_pairs}
