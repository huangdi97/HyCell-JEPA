"""Compact deterministic encoders for toy belief-state transitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class BioStateEncoder:
    """Standardize compact readout features and project them to an embedding."""

    feature_names: list[str]
    mean: np.ndarray
    scale: np.ndarray
    projection: np.ndarray

    @classmethod
    def fit(
        cls,
        states: np.ndarray,
        *,
        feature_names: list[str],
        embedding_dim: int,
        seed: int,
    ) -> "BioStateEncoder":
        if states.ndim != 2:
            raise ValueError("states must be a 2D matrix")
        mean = states.mean(axis=0)
        scale = states.std(axis=0)
        scale = np.where(scale < 1e-8, 1.0, scale)
        projection = deterministic_projection(states.shape[1], embedding_dim, seed)
        return cls(feature_names=list(feature_names), mean=mean, scale=scale, projection=projection)

    def transform(self, states: np.ndarray) -> np.ndarray:
        normalized = (states - self.mean) / self.scale
        return np.tanh(normalized @ self.projection)


@dataclass(frozen=True)
class CategoricalEncoder:
    """One-hot encode labels and project them to a compact embedding."""

    categories: list[str]
    projection: np.ndarray
    unknown_category: str = "__unknown__"

    @classmethod
    def fit(
        cls,
        labels: np.ndarray,
        *,
        embedding_dim: int,
        seed: int,
        extra_categories: list[str] | None = None,
    ) -> "CategoricalEncoder":
        categories = _ordered_unique(labels)
        for category in extra_categories or []:
            if category not in categories:
                categories.append(category)
        categories.append("__unknown__")
        projection = deterministic_projection(len(categories), embedding_dim, seed)
        return cls(categories=categories, projection=projection)

    def transform(self, labels: np.ndarray) -> np.ndarray:
        index = {category: idx for idx, category in enumerate(self.categories)}
        unknown_idx = index[self.unknown_category]
        one_hot = np.zeros((len(labels), len(self.categories)), dtype=np.float64)
        for row_idx, label in enumerate(labels):
            one_hot[row_idx, index.get(str(label), unknown_idx)] = 1.0
        return np.tanh(one_hot @ self.projection)


ActionEncoder = CategoricalEncoder
ContextEncoder = CategoricalEncoder
AdapterEncoder = CategoricalEncoder


def deterministic_projection(input_dim: int, output_dim: int, seed: int) -> np.ndarray:
    """Create a deterministic small random projection matrix."""

    if input_dim <= 0 or output_dim <= 0:
        raise ValueError("projection dimensions must be positive")
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=1.0 / max(1, input_dim) ** 0.5, size=(input_dim, output_dim))


def encoder_metadata(
    bio: BioStateEncoder,
    action: CategoricalEncoder,
    context: CategoricalEncoder,
    adapter: CategoricalEncoder,
) -> dict[str, Any]:
    """Return JSON-friendly encoder metadata."""

    return {
        "belief_features": bio.feature_names,
        "bio_state_embedding_dim": int(bio.projection.shape[1]),
        "action_categories": action.categories,
        "action_embedding_dim": int(action.projection.shape[1]),
        "context_categories": context.categories,
        "context_embedding_dim": int(context.projection.shape[1]),
        "adapter_categories": adapter.categories,
        "adapter_embedding_dim": int(adapter.projection.shape[1]),
    }


def _ordered_unique(labels: np.ndarray) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for label in labels:
        text = str(label)
        if text not in seen:
            seen.add(text)
            ordered.append(text)
    return ordered
