"""Config file management with versioning."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from src.section_registry import is_known, count_bounds as registry_count_bounds

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DEFAULTS_DIR = CONFIG_DIR / "defaults"
HISTORY_DIR = CONFIG_DIR / ".history"


def _config_path(name: str) -> Path:
    return CONFIG_DIR / f"{name}.json"


def _default_path(name: str) -> Path:
    return DEFAULTS_DIR / f"{name}.json"


def load(name: str) -> dict:
    """Read config/<name>.json and return as dict."""
    path = _config_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    """Validate, archive old version, write new config."""
    path = _config_path(name)
    if path.exists():
        archive_dir = HISTORY_DIR / name
        archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(path, archive_dir / f"{timestamp}.json")

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def reset(name: str) -> None:
    """Copy default config over current config."""
    default = _default_path(name)
    if not default.exists():
        raise FileNotFoundError(f"Default config not found: {default}")
    shutil.copy2(default, _config_path(name))


def validate_layout(data: dict) -> list[str]:
    """Validate deck_layout data. Returns list of error strings."""
    errors: list[str] = []
    sections = data.get("sections", [])
    if not isinstance(sections, list):
        errors.append("'sections' must be a list")
        return errors

    for i, section in enumerate(sections):
        stype = section.get("type", "")
        if not is_known(stype):
            errors.append(f"Section {i}: unknown type '{stype}'")
            continue

        bounds = registry_count_bounds(stype)
        if bounds is not None:
            count = section.get("count")
            if count is not None:
                lo, hi = bounds
                if not (lo <= int(count) <= hi):
                    errors.append(
                        f"Section {i} ('{stype}'): count {count} out of bounds [{lo}, {hi}]"
                    )

    return errors


def diff_vs_default(name: str) -> str:
    """Return a simple text diff between current and default config."""
    import difflib
    current_text = json.dumps(load(name), indent=2)
    try:
        default_text = json.dumps(json.loads(_default_path(name).read_text(encoding="utf-8")), indent=2)
    except FileNotFoundError:
        return "(no default available)"
    lines_c = current_text.splitlines(keepends=True)
    lines_d = default_text.splitlines(keepends=True)
    diff = list(difflib.unified_diff(lines_d, lines_c, fromfile="default", tofile="current"))
    return "".join(diff) if diff else "(no differences)"
