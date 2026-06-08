"""SCORE stage: fill the qualification matrix from research data."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from src import llm

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

CRITERIA_META = {
    "A": {"name": "Solidité Financière",          "weight": 4, "max": 20},
    "B": {"name": "Potentiel Marketing & Influence", "weight": 4, "max": 20},
    "C": {"name": "Crédibilité de l'Équipe",      "weight": 3, "max": 15},
    "D": {"name": "Cohérence du Projet",           "weight": 3, "max": 15},
    "E": {"name": "Réalisme des Attentes",         "weight": 2, "max": 10},
    "F": {"name": "Réseau de Distribution",        "weight": 2, "max": 10},
}


def _load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def run_score(
    research_data: dict,
    analyst_notes: str = "",
    model: str | None = None,
) -> dict:
    """Score the prospect based on research. Returns scored matrix dict."""
    if model is None:
        model = llm.MODEL_SYNTHESIZE  # Sonnet for scoring — needs judgment

    system = _load("common")

    # Strip internal keys before passing to LLM
    clean = {k: v for k, v in research_data.items() if not k.startswith("_")}
    research_json = json.dumps(clean, ensure_ascii=False, indent=2)

    user = (
        _load("score")
        .replace("{research_data}", research_json)
        .replace("{analyst_notes}", analyst_notes.strip() or "(aucune note additionnelle)")
    )

    print("[scorer] Scoring prospect...", file=sys.stderr)

    try:
        raw = llm.call_json(system=system, user=user, model=model, max_tokens=4096)
    except Exception as e:
        print(f"[scorer] Scoring failed: {e}", file=sys.stderr)
        raise

    # Validate and fix weighted scores
    scores = raw.get("scores", {})
    total = 0
    for key, meta in CRITERIA_META.items():
        if key in scores:
            s = scores[key]
            score = max(1, min(5, int(s.get("score", 1))))
            s["score"] = score
            s["weighted"] = score * meta["weight"]
            total += s["weighted"]

    bonus = raw.get("bonus", {})
    if bonus.get("applicable"):
        total += 10
        bonus["points"] = 10
    else:
        bonus["points"] = 0

    raw["total"] = min(total, 100)

    # Ensure verdict matches total
    t = raw["total"]
    if t < 40:
        raw["verdict"] = "No-Go"
        raw["verdict_color"] = "red"
    elif t <= 70:
        raw["verdict"] = "À creuser"
        raw["verdict_color"] = "orange"
    else:
        raw["verdict"] = "Go"
        raw["verdict_color"] = "green"

    raw["criteria_meta"] = CRITERIA_META
    print(f"[scorer] Score: {raw['total']}/100 — {raw['verdict']}", file=sys.stderr)
    return raw
