"""Small config helpers for prototype scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON or YAML config file."""

    config_path = Path(path)
    text = config_path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        data = _load_yaml(text, config_path, exc)
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must contain a top-level object.")
    return data


def ensure_dir(path: str | Path) -> Path:
    """Create and return a directory path."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _load_yaml(text: str, config_path: Path, json_error: json.JSONDecodeError) -> dict[str, Any]:
    try:
        import yaml
    except ImportError as exc:
        return _load_simple_yaml(text, config_path)
    data = yaml.safe_load(text)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{config_path} must contain a top-level mapping.") from json_error
    return data


def _load_simple_yaml(text: str, config_path: Path) -> dict[str, Any]:
    """Parse the small top-level YAML subset used by local configs."""

    data: dict[str, Any] = {}
    current_list_key: str | None = None
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise ValueError(f"{config_path}:{line_number} has a list item without a key")
            data[current_list_key].append(_parse_scalar(line[4:].strip()))
            continue
        current_list_key = None
        if line.startswith(" "):
            raise ValueError(f"{config_path}:{line_number} uses unsupported nested YAML")
        if ":" not in line:
            raise ValueError(f"{config_path}:{line_number} is not a key/value line")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            data[key] = []
            current_list_key = key
        else:
            data[key] = _parse_scalar(value)
    return data


def _parse_scalar(value: str) -> Any:
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value.strip("\"'")
