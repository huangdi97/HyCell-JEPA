"""Deterministic toy single-cell perturbation data generation."""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Any, Iterable

METADATA_COLUMNS = [
    "cell_id",
    "action",
    "action_label",
    "timepoint",
    "cell_system",
    "culture",
    "species",
    "is_toy",
]


def generate_toy_cells(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate deterministic HDF-like toy single-cell expression rows."""

    seed = int(config.get("seed", 0))
    rng = random.Random(seed)
    genes = _require_list(config, "genes")
    baseline = _require_mapping(config, "baseline_expression")
    actions = _require_mapping(config, "actions")
    action_effects = config.get("action_effects", {})
    timepoints = _require_list(config, "timepoints")
    timepoint_effect_scale = _require_mapping(config, "timepoint_effect_scale")
    cells_per_group = int(config.get("cells_per_action_timepoint", 1))
    noise = float(config.get("noise", 0.0))
    context = dict(config.get("context", {}))

    rows: list[dict[str, Any]] = []
    for action_name, action_info in actions.items():
        effects = action_effects.get(action_name, {})
        for timepoint in timepoints:
            scale = float(timepoint_effect_scale[timepoint])
            for replicate in range(cells_per_group):
                row: dict[str, Any] = {
                    "cell_id": f"toy_{action_name}_{timepoint}_{replicate:03d}",
                    "action": action_name,
                    "action_label": str(action_info.get("label", action_name)),
                    "timepoint": timepoint,
                    "cell_system": context.get("cell_system", "toy_hdf"),
                    "culture": context.get("culture", "toy"),
                    "species": context.get("species", "human_toy"),
                    "is_toy": str(bool(context.get("is_toy", True))).lower(),
                }
                for gene in genes:
                    base = float(baseline[gene])
                    effect = float(effects.get(gene, 0.0)) * scale
                    jitter = rng.uniform(-noise, noise)
                    row[gene] = round(max(0.0, base + effect + jitter), 4)
                rows.append(row)
    return rows


def toy_cell_columns(config: dict[str, Any]) -> list[str]:
    """Return stable output columns for toy-cell CSV files."""

    return [*METADATA_COLUMNS, *_require_list(config, "genes")]


def write_toy_cells(rows: Iterable[dict[str, Any]], path: str | Path, columns: list[str]) -> Path:
    """Write generated toy cells to CSV."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def read_toy_cells(path: str | Path) -> list[dict[str, str]]:
    """Read toy cells from CSV."""

    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_toy_npz(
    path: str | Path,
    *,
    n_cells: int,
    n_genes: int,
    seed: int = 1729,
) -> Path:
    """Write a deterministic dense toy expression matrix to compressed NPZ.

    This mode exists for packaging and loader smoke checks. It is still toy
    engineering data and does not represent real cellular measurements.
    """

    if n_cells <= 0:
        raise ValueError("n_cells must be positive")
    if n_genes <= 0:
        raise ValueError("n_genes must be positive")

    import numpy as np

    rng = np.random.default_rng(seed)
    gene_names = np.array([f"TOY_GENE_{idx:04d}" for idx in range(n_genes)])
    cell_ids = np.array([f"toy_cell_{idx:06d}" for idx in range(n_cells)])
    actions = np.array(
        ["control", "aging_stress", "regeneration", "partial_reprogramming"]
    )
    timepoints = np.array(["t0", "t1", "t2"])
    action_index = np.arange(n_cells) % len(actions)
    timepoint_index = (np.arange(n_cells) // len(actions)) % len(timepoints)

    expression = rng.normal(loc=1.0, scale=0.15, size=(n_cells, n_genes)).astype("float32")
    expression = np.clip(expression, 0.0, None)

    marker_width = min(50, n_genes)
    if marker_width:
        aging_mask = action_index == 1
        regeneration_mask = action_index == 2
        reprogramming_mask = action_index == 3
        expression[aging_mask, :marker_width] += 0.6
        expression[regeneration_mask, marker_width : marker_width * 2] += 0.4
        expression[reprogramming_mask, marker_width * 2 : marker_width * 3] += 0.5

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output_path,
        expression=expression,
        gene_names=gene_names,
        cell_ids=cell_ids,
        actions=actions[action_index],
        timepoints=timepoints[timepoint_index],
        is_toy=np.array(True),
        note=np.array(
            "Toy engineering validation data only; not biological evidence."
        ),
    )
    return output_path


def default_output_path(config: dict[str, Any]) -> Path:
    """Return the configured toy-cell output path."""

    return Path(config.get("output_dir", "outputs/toy_data")) / str(
        config.get("output_filename", "toy_cells.csv")
    )


def _require_list(config: dict[str, Any], key: str) -> list[str]:
    value = config.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"config field {key!r} must be a non-empty list")
    return [str(item) for item in value]


def _require_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"config field {key!r} must be an object")
    return value
