"""Prompt file management with versioning."""
from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
DEFAULTS_DIR = PROMPTS_DIR / "defaults"
HISTORY_DIR = PROMPTS_DIR / ".history"

REQUIRED_PLACEHOLDERS: dict[str, list[str]] = {
    "observe": ["{corpus}"],
    "derive": ["{signal_map}"],
    "research": ["{question}"],
    "synthesize": ["{corpus}", "{evidence_cards}"],
    "distill": ["{dossier}", "{deck_schema}", "{brand_tokens}"],
    "common": [],
}

KNOWN_STAGES = list(REQUIRED_PLACEHOLDERS.keys())


def _prompt_path(stage: str) -> Path:
    return PROMPTS_DIR / f"{stage}.md"


def _default_path(stage: str) -> Path:
    return DEFAULTS_DIR / f"{stage}.md"


def load(stage: str) -> str:
    """Read the current prompt for the given stage."""
    path = _prompt_path(stage)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def save(stage: str, text: str) -> None:
    """Validate placeholders, archive old version, write new prompt."""
    required = REQUIRED_PLACEHOLDERS.get(stage, [])
    missing = [p for p in required if p not in text]
    if missing:
        raise ValueError(
            f"Prompt for '{stage}' is missing required placeholders: {missing}"
        )

    # Archive old version
    path = _prompt_path(stage)
    if path.exists():
        archive_dir = HISTORY_DIR / stage
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(path, archive_dir / f"{timestamp}.md")

    path.write_text(text, encoding="utf-8")


def reset(stage: str) -> None:
    """Copy default prompt over current prompt."""
    default = _default_path(stage)
    if not default.exists():
        raise FileNotFoundError(f"Default prompt not found: {default}")
    shutil.copy2(default, _prompt_path(stage))


def compiled(stage: str, **vars: str) -> str:
    """Return common.md + stage prompt with vars substituted."""
    common_text = load("common")
    stage_text = load(stage)
    combined = common_text.strip() + "\n\n" + stage_text
    for key, value in vars.items():
        combined = combined.replace("{" + key + "}", value)
    return combined


def required_placeholders(stage: str) -> list[str]:
    """Return the required placeholders for a stage."""
    return list(REQUIRED_PLACEHOLDERS.get(stage, []))


def diff_vs_default(stage: str) -> str:
    """Return a simple text diff between current and default prompt."""
    import difflib
    current = load(stage)
    try:
        default_text = _default_path(stage).read_text(encoding="utf-8")
    except FileNotFoundError:
        return "(no default available)"
    lines_current = current.splitlines(keepends=True)
    lines_default = default_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines_default, lines_current, fromfile="default", tofile="current"))
    return "".join(diff) if diff else "(no differences)"
