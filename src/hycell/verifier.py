"""Structured verifier rules for toy compact biological states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class VerificationIssue:
    severity: str
    code: str
    message: str


@dataclass(frozen=True)
class VerificationResult:
    status: str
    issues: list[VerificationIssue]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "issues": [issue.__dict__ for issue in self.issues],
        }


class BiologicalVerifier:
    """Verifier for toy engineering constraints and overclaim warnings."""

    def __init__(self, feature_names: list[str]) -> None:
        self.feature_names = feature_names

    def verify_transition(
        self,
        current_state: np.ndarray,
        predicted_state: np.ndarray,
        *,
        action: str,
    ) -> VerificationResult:
        issues: list[VerificationIssue] = [
            VerificationIssue(
                "warn",
                "toy_engineering_only",
                "Toy transition output is for engineering validation only, not biological discovery.",
            )
        ]
        current = np.asarray(current_state, dtype=np.float64)
        predicted = np.asarray(predicted_state, dtype=np.float64)
        if predicted.shape != current.shape:
            issues.append(
                VerificationIssue("fail", "shape_mismatch", f"Predicted shape {predicted.shape} does not match current shape {current.shape}.")
            )
        if np.any(~np.isfinite(predicted)):
            issues.append(VerificationIssue("fail", "non_finite", "Predicted state contains non-finite values."))
        if np.any(predicted < -0.05):
            issues.append(VerificationIssue("fail", "negative_readout", "Predicted readout fell below the allowed toy lower bound."))
        if np.any(predicted > 5.0):
            issues.append(VerificationIssue("warn", "high_readout", "Predicted readout exceeded the toy high-readout caution bound."))

        feature_index = {name: idx for idx, name in enumerate(self.feature_names)}
        if action == "aging_stress" and "senescence" in feature_index and "proliferation" in feature_index:
            if predicted[feature_index["senescence"]] < current[feature_index["senescence"]]:
                issues.append(VerificationIssue("warn", "aging_senescence_direction", "Aging-like toy action did not increase senescence score."))
            if predicted[feature_index["proliferation"]] > current[feature_index["proliferation"]] + 0.5:
                issues.append(VerificationIssue("warn", "aging_proliferation_direction", "Aging-like toy action increased proliferation more than expected."))
        if action == "partial_reprogramming" and "reprogramming_plasticity" in feature_index:
            if predicted[feature_index["reprogramming_plasticity"]] > 2.0:
                issues.append(VerificationIssue("warn", "plasticity_overclaim", "Toy plasticity score is high; do not describe it as real reprogramming."))

        if any(issue.severity == "fail" for issue in issues):
            status = "fail"
        elif any(issue.severity == "warn" for issue in issues):
            status = "warn"
        else:
            status = "pass"
        return VerificationResult(status=status, issues=issues)

    def verify_plan(self, steps: list[dict[str, Any]]) -> VerificationResult:
        issues = [
            VerificationIssue(
                "warn",
                "toy_plan_only",
                "Planner output is a toy action sequence for software validation, not an intervention recommendation.",
            )
        ]
        if not steps:
            issues.append(VerificationIssue("fail", "empty_plan", "Planner returned no steps."))
        if any(step.get("verification", {}).get("status") == "fail" for step in steps):
            issues.append(VerificationIssue("fail", "failed_step", "At least one planned step failed verification."))
        status = "fail" if any(issue.severity == "fail" for issue in issues) else "warn"
        return VerificationResult(status=status, issues=issues)
