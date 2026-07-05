"""Minimal JEPA transition core for compact toy belief states."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from hycell.encoders import AdapterEncoder, ActionEncoder, BioStateEncoder, ContextEncoder


@dataclass(frozen=True)
class EncodedInputs:
    """Encoded b_t, a_t, c_t, and h_t blocks."""

    bio_state: np.ndarray
    action: np.ndarray
    context: np.ndarray
    adapter: np.ndarray

    def concatenate(self) -> np.ndarray:
        return np.hstack([self.bio_state, self.action, self.context, self.adapter])


@dataclass(frozen=True)
class JEPAEncoderStack:
    """Bundle of encoders for b_t + a_t + c_t + h_t."""

    bio_state: BioStateEncoder
    action: ActionEncoder
    context: ContextEncoder
    adapter: AdapterEncoder

    def encode(
        self,
        states: np.ndarray,
        actions: np.ndarray,
        contexts: np.ndarray,
        adapters: np.ndarray,
    ) -> EncodedInputs:
        return EncodedInputs(
            bio_state=self.bio_state.transform(states),
            action=self.action.transform(actions),
            context=self.context.transform(contexts),
            adapter=self.adapter.transform(adapters),
        )


@dataclass(frozen=True)
class JEPATransitionCore:
    """Linear transition head from encoded inputs to next belief-state features."""

    weights: np.ndarray
    bias: np.ndarray

    def predict_from_encoded(self, encoded: EncodedInputs) -> np.ndarray:
        design = encoded.concatenate()
        return design @ self.weights + self.bias

    def predict(
        self,
        encoders: JEPAEncoderStack,
        states: np.ndarray,
        actions: np.ndarray,
        contexts: np.ndarray,
        adapters: np.ndarray,
    ) -> np.ndarray:
        return self.predict_from_encoded(encoders.encode(states, actions, contexts, adapters))


def fit_transition_core(
    encoded: EncodedInputs,
    targets: np.ndarray,
    *,
    ridge_lambda: float,
) -> JEPATransitionCore:
    """Fit a deterministic ridge-regression transition head."""

    if ridge_lambda < 0:
        raise ValueError("ridge_lambda must be non-negative")
    design = encoded.concatenate()
    augmented = np.hstack([design, np.ones((design.shape[0], 1), dtype=design.dtype)])
    regularizer = ridge_lambda * np.eye(augmented.shape[1], dtype=design.dtype)
    regularizer[-1, -1] = 0.0
    solution = np.linalg.solve(augmented.T @ augmented + regularizer, augmented.T @ targets)
    return JEPATransitionCore(weights=solution[:-1, :], bias=solution[-1, :])


def mean_squared_error(predictions: np.ndarray, targets: np.ndarray) -> float:
    """Compute MSE over compact belief-state predictions."""

    return float(np.mean((predictions - targets) ** 2))
