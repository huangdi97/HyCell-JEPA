"""Dataset builders for compact toy belief-state transitions."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

SCORE_METADATA_COLUMNS = {
    "cell_id",
    "action",
    "action_label",
    "timepoint",
    "cell_system",
    "is_toy",
}


@dataclass(frozen=True)
class TransitionDataset:
    """Compact transition table for b_t + a_t + c_t + h_t -> b_{t+1}."""

    current_states: np.ndarray
    next_states: np.ndarray
    actions: np.ndarray
    context_labels: np.ndarray
    adapter_labels: np.ndarray
    feature_names: list[str]

    @property
    def n_examples(self) -> int:
        return int(self.current_states.shape[0])


def load_score_rows(path: str | Path) -> list[dict[str, str]]:
    """Load gene-set score CSV rows."""

    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def infer_belief_features(rows: list[dict[str, str]]) -> list[str]:
    """Infer compact belief-state feature columns from score rows."""

    if not rows:
        raise ValueError("cannot infer features from an empty score table")
    return [
        column
        for column in rows[0]
        if column not in SCORE_METADATA_COLUMNS
    ]


def build_transition_dataset(
    rows: list[dict[str, str]],
    *,
    feature_names: list[str] | None = None,
    timepoints: list[str] | None = None,
) -> TransitionDataset:
    """Aggregate per-cell scores and build adjacent-timepoint transitions."""

    if not rows:
        raise ValueError("cannot build transitions from an empty score table")
    features = feature_names or infer_belief_features(rows)
    ordered_timepoints = timepoints or _ordered_unique(row["timepoint"] for row in rows)

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    for row in rows:
        key = (
            row["action"],
            row["timepoint"],
            row.get("cell_system", "toy_hdf"),
        )
        grouped.setdefault(key, []).append(row)

    means: dict[tuple[str, str, str], np.ndarray] = {}
    for key, group_rows in grouped.items():
        matrix = np.asarray(
            [[float(row[feature]) for feature in features] for row in group_rows],
            dtype=np.float64,
        )
        means[key] = matrix.mean(axis=0)

    current_states: list[np.ndarray] = []
    next_states: list[np.ndarray] = []
    actions: list[str] = []
    contexts: list[str] = []
    adapters: list[str] = []

    for action in _ordered_unique(row["action"] for row in rows):
        systems = _ordered_unique(
            row.get("cell_system", "toy_hdf")
            for row in rows
            if row["action"] == action
        )
        for cell_system in systems:
            for source, target in zip(ordered_timepoints, ordered_timepoints[1:]):
                source_key = (action, source, cell_system)
                target_key = (action, target, cell_system)
                if source_key not in means or target_key not in means:
                    continue
                current_states.append(means[source_key])
                next_states.append(means[target_key])
                actions.append(action)
                contexts.append(f"{source}->{target}|{cell_system}")
                adapters.append(cell_system)

    if not current_states:
        raise ValueError("no adjacent transitions could be built from score rows")

    return TransitionDataset(
        current_states=np.vstack(current_states),
        next_states=np.vstack(next_states),
        actions=np.asarray(actions),
        context_labels=np.asarray(contexts),
        adapter_labels=np.asarray(adapters),
        feature_names=features,
    )


def train_eval_split(
    dataset: TransitionDataset,
    *,
    train_fraction: float,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return deterministic train/eval indices."""

    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between 0 and 1")
    rng = np.random.default_rng(seed)
    indices = np.arange(dataset.n_examples)
    rng.shuffle(indices)
    split = max(1, min(dataset.n_examples - 1, int(round(dataset.n_examples * train_fraction))))
    return np.sort(indices[:split]), np.sort(indices[split:])


def _ordered_unique(values: Any) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            ordered.append(text)
    return ordered
