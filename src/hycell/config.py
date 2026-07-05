"""Small config helpers for dependency-free prototype scripts.

The project stores early `.yaml` configs as YAML-compatible JSON so the first
toy pipeline can run with only the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON/YAML-compatible config file."""

    config_path = Path(path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{config_path} must be JSON syntax or YAML-compatible JSON for now."
        ) from exc
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must contain a top-level object.")
    return data


def ensure_dir(path: str | Path) -> Path:
    """Create and return a directory path."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
