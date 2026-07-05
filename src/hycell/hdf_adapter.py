"""Toy HDF adapter for action and context conventions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from hycell.datasets import TransitionDataset


@dataclass(frozen=True)
class HDFActionSpec:
    action: str
    label: str
    scenario: str
    expected_direction: dict[str, str]
    caution: str


class HDFAdapter:
    """Map toy HDF scenarios into canonical model action/context inputs."""

    cell_system = "toy_hdf"

    def __init__(self) -> None:
        self._actions = {
            "control": HDFActionSpec(
                action="control",
                label="Control no-op",
                scenario="Toy HDF baseline",
                expected_direction={},
                caution="Baseline toy reference only.",
            ),
            "aging_stress": HDFActionSpec(
                action="aging_stress",
                label="Aging-like stress",
                scenario="Toy HDF aging/stress scenario",
                expected_direction={"senescence": "up", "stress_inflammation": "up", "proliferation": "down"},
                caution="Toy stress behavior is configured, not discovered.",
            ),
            "regeneration": HDFActionSpec(
                action="regeneration",
                label="Regeneration-supporting",
                scenario="Toy HDF regeneration scenario",
                expected_direction={"proliferation": "up", "ecm_remodeling": "up", "viability_qc_proxy": "up"},
                caution="Toy regeneration behavior is engineering validation only.",
            ),
            "partial_reprogramming": HDFActionSpec(
                action="partial_reprogramming",
                label="Partial reprogramming-inspired",
                scenario="Toy HDF plasticity scenario",
                expected_direction={"reprogramming_plasticity": "up", "senescence": "down"},
                caution="Toy plasticity behavior must not be read as real reprogramming evidence.",
            ),
        }

    @property
    def actions(self) -> list[str]:
        return list(self._actions)

    def action_spec(self, action: str) -> HDFActionSpec:
        if action not in self._actions:
            raise ValueError(f"unknown toy HDF action: {action}")
        return self._actions[action]

    def context_label(self, source_timepoint: str, target_timepoint: str) -> str:
        return f"{source_timepoint}->{target_timepoint}|{self.cell_system}"

    def adapter_label(self) -> str:
        return self.cell_system

    def model_inputs(
        self,
        state: np.ndarray,
        *,
        action: str,
        source_timepoint: str,
        target_timepoint: str,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        self.action_spec(action)
        return (
            np.asarray(state, dtype=np.float64).reshape(1, -1),
            np.asarray([action]),
            np.asarray([self.context_label(source_timepoint, target_timepoint)]),
            np.asarray([self.adapter_label()]),
        )

    def state_for(self, dataset: TransitionDataset, *, action: str, source_timepoint: str) -> np.ndarray:
        """Return an aggregate source state from the transition dataset."""

        for state, row_action, context in zip(
            dataset.current_states,
            dataset.actions,
            dataset.context_labels,
        ):
            if row_action == action and str(context).startswith(f"{source_timepoint}->"):
                return np.asarray(state, dtype=np.float64)
        raise ValueError(f"no state found for action={action!r}, source_timepoint={source_timepoint!r}")

    def describe_actions(self) -> list[dict[str, Any]]:
        return [
            {
                "action": spec.action,
                "label": spec.label,
                "scenario": spec.scenario,
                "expected_direction": spec.expected_direction,
                "caution": spec.caution,
            }
            for spec in self._actions.values()
        ]
