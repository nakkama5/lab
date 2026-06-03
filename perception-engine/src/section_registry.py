"""Registry of deck section types with metadata."""
from __future__ import annotations
from typing import Optional

REGISTRY: dict[str, dict] = {
    "cover": {
        "fields": ["product", "taglines", "micro", "elevator"],
        "count_bounds": None,
    },
    "metrics": {
        "fields": ["metrics"],
        "count_bounds": (3, 5),
    },
    "legacy_evolution": {
        "fields": ["legacy", "evolution"],
        "count_bounds": (3, 6),
    },
    "jargon_to_value": {
        "fields": ["jargon_rows"],
        "count_bounds": (2, 6),
    },
    "swot": {
        "fields": ["swot"],
        "count_bounds": (4, 4),
    },
    "metaphor": {
        "fields": ["metaphor"],
        "count_bounds": None,
    },
    "palette": {
        "fields": [],
        "count_bounds": None,
    },
    "tone_pillars": {
        "fields": ["pillars"],
        "count_bounds": (2, 4),
    },
    "vocab": {
        "fields": ["vocab"],
        "count_bounds": (3, 8),
    },
    "taglines": {
        "fields": ["taglines"],
        "count_bounds": None,
    },
    "manifesto": {
        "fields": ["manifesto"],
        "count_bounds": None,
    },
    "roadmap": {
        "fields": ["roadmap"],
        "count_bounds": (2, 4),
    },
    "grapevine": {
        "fields": ["grapevine"],
        "count_bounds": (2, 4),
    },
    "closing": {
        "fields": ["product", "taglines"],
        "count_bounds": None,
    },
}


def types() -> list[str]:
    """Return all registered section types."""
    return list(REGISTRY.keys())


def required_fields(section_type: str) -> list[str]:
    """Return required fields for a section type."""
    return list(REGISTRY.get(section_type, {}).get("fields", []))


def count_bounds(section_type: str) -> Optional[tuple[int, int]]:
    """Return (min, max) count bounds or None."""
    return REGISTRY.get(section_type, {}).get("count_bounds")


def is_known(section_type: str) -> bool:
    """Return True if section type is in the registry."""
    return section_type in REGISTRY
