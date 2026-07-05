"""Small target-state planner for toy compact belief states."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np

from hycell.hdf_adapter import HDFAdapter
from hycell.jepa import JEPAEncoderStack, JEPATransitionCore
from hycell.verifier import BiologicalVerifier


@dataclass(frozen=True)
class PlanResult:
    actions: list[str]
    distance: float
    final_state: list[float]
    steps: list[dict[str, Any]]
    verification: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "actions": self.actions,
            "distance": self.distance,
            "final_state": self.final_state,
            "steps": self.steps,
            "verification": self.verification,
        }


class TargetStatePlanner:
    """Exhaustive planner over tiny toy action sequences."""

    def __init__(
        self,
        *,
        encoders: JEPAEncoderStack,
        core: JEPATransitionCore,
        adapter: HDFAdapter,
        verifier: BiologicalVerifier,
        feature_names: list[str],
    ) -> None:
        self.encoders = encoders
        self.core = core
        self.adapter = adapter
        self.verifier = verifier
        self.feature_names = feature_names

    def plan(
        self,
        start_state: np.ndarray,
        target_state: np.ndarray,
        *,
        horizon: int = 2,
        start_timepoint: str = "t0",
        candidate_actions: list[str] | None = None,
    ) -> PlanResult:
        if horizon <= 0:
            raise ValueError("horizon must be positive")
        actions = candidate_actions or self.adapter.actions
        timepoints = ["t0", "t1", "t2", "t3", "t4"]
        if start_timepoint not in timepoints:
            raise ValueError(f"unsupported toy start_timepoint: {start_timepoint}")
        start_index = timepoints.index(start_timepoint)

        best: PlanResult | None = None
        for sequence in product(actions, repeat=horizon):
            result = self._evaluate_sequence(
                start_state=start_state,
                target_state=target_state,
                sequence=list(sequence),
                start_index=start_index,
                timepoints=timepoints,
            )
            if best is None or result.distance < best.distance:
                best = result
        if best is None:
            raise ValueError("no plan candidates were evaluated")
        return best

    def plan_top_k(
        self,
        start_state: np.ndarray,
        target_state: np.ndarray,
        *,
        horizon: int = 2,
        start_timepoint: str = "t0",
        candidate_actions: list[str] | None = None,
        k: int = 3,
    ) -> list[PlanResult]:
        """Return the top-k shortest toy action sequences."""

        if k <= 0:
            raise ValueError("k must be positive")
        actions = candidate_actions or self.adapter.actions
        results = [
            self._evaluate_sequence(
                start_state,
                target_state,
                sequence=list(sequence),
                start_index=["t0", "t1", "t2", "t3", "t4"].index(start_timepoint),
                timepoints=["t0", "t1", "t2", "t3", "t4"],
            )
            for sequence in product(actions, repeat=horizon)
        ]
        results.sort(key=lambda result: result.distance)
        return results[:k]

    def _evaluate_sequence(
        self,
        start_state: np.ndarray,
        target_state: np.ndarray,
        *,
        sequence: list[str],
        start_index: int,
        timepoints: list[str],
    ) -> PlanResult:
        state = np.asarray(start_state, dtype=np.float64)
        steps: list[dict[str, Any]] = []
        for step_index, action in enumerate(sequence):
            source = timepoints[min(start_index + step_index, len(timepoints) - 2)]
            target = timepoints[min(start_index + step_index + 1, len(timepoints) - 1)]
            model_inputs = self.adapter.model_inputs(
                state,
                action=action,
                source_timepoint=source,
                target_timepoint=target,
            )
            predicted = self.core.predict(self.encoders, *model_inputs)[0]
            verification = self.verifier.verify_transition(state, predicted, action=action)
            steps.append(
                {
                    "action": action,
                    "source_timepoint": source,
                    "target_timepoint": target,
                    "predicted_state": _state_dict(self.feature_names, predicted),
                    "verification": verification.to_dict(),
                }
            )
            state = predicted
        distance = float(np.linalg.norm(state - target_state))
        return PlanResult(
            actions=list(sequence),
            distance=distance,
            final_state=[float(value) for value in state],
            steps=steps,
            verification=self.verifier.verify_plan(steps).to_dict(),
        )


def _state_dict(feature_names: list[str], state: np.ndarray) -> dict[str, float]:
    return {feature: float(value) for feature, value in zip(feature_names, state)}
