"""Perturbation and metadata adapters for real-data scaffolding."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hycell.data_loaders import SingleCellDataset


@dataclass(frozen=True)
class PerturbationMapping:
    original_label: str
    canonical_action: str
    mapping_status: str


class PerturbationAdapter:
    """Map dataset-specific perturbation labels while preserving originals."""

    def __init__(self, aliases: dict[str, list[str]] | None = None) -> None:
        aliases = aliases or {}
        self._lookup: dict[str, str] = {}
        for canonical, labels in aliases.items():
            self._lookup[_normalize_label(canonical)] = canonical
            for label in labels:
                self._lookup[_normalize_label(label)] = canonical

    def map_label(self, label: Any) -> PerturbationMapping:
        original = "" if label is None else str(label)
        normalized = _normalize_label(original)
        if not normalized:
            return PerturbationMapping(original, "unknown", "missing")
        canonical = self._lookup.get(normalized)
        if canonical is None:
            return PerturbationMapping(original, "unknown", "unknown")
        return PerturbationMapping(original, canonical, "mapped")

    def map_dataset(self, dataset: SingleCellDataset) -> list[PerturbationMapping]:
        return [self.map_label(row.get("perturbation")) for row in dataset.obs]


class HDFAgingMetadataAdapter:
    """Map validated metadata rows into MVP context conventions."""

    def __init__(self, perturbation_adapter: PerturbationAdapter, adapter_label: str = "hdf_aging") -> None:
        self.perturbation_adapter = perturbation_adapter
        self.adapter_label_value = adapter_label

    def map_row(self, row: dict[str, Any]) -> dict[str, Any]:
        mapping = self.perturbation_adapter.map_label(row.get("perturbation"))
        timepoint = str(row.get("timepoint", "unknown"))
        cell_system = str(row.get("cell_system", "unknown"))
        return {
            "cell_id": str(row.get("cell_id", "")),
            "original_perturbation": mapping.original_label,
            "canonical_action": mapping.canonical_action,
            "mapping_status": mapping.mapping_status,
            "timepoint": timepoint,
            "cell_system": cell_system,
            "adapter_label": self.adapter_label_value,
            "context_label": f"{cell_system}|{timepoint}|{mapping.canonical_action}",
        }

    def map_dataset(self, dataset: SingleCellDataset) -> list[dict[str, Any]]:
        return [self.map_row(row) for row in dataset.obs]


def aliases_from_config(config: dict[str, Any]) -> dict[str, list[str]]:
    aliases = config.get("canonical_actions", {})
    if not isinstance(aliases, dict):
        raise ValueError("canonical_actions must be a mapping of canonical action to aliases")
    return {str(key): [str(value) for value in values] for key, values in aliases.items()}


def _normalize_label(label: str) -> str:
    return label.strip().lower().replace("-", "_").replace(" ", "_")
