from __future__ import annotations

import numpy as np

from hycell.verifier import BiologicalVerifier


def test_verifier_returns_structured_warning_for_toy_output() -> None:
    verifier = BiologicalVerifier(["senescence", "proliferation"])

    result = verifier.verify_transition(
        np.asarray([1.0, 2.0]),
        np.asarray([1.1, 1.8]),
        action="aging_stress",
    )

    payload = result.to_dict()
    assert payload["status"] == "warn"
    assert payload["issues"][0]["code"] == "toy_engineering_only"


def test_verifier_fails_negative_prediction() -> None:
    verifier = BiologicalVerifier(["senescence"])

    result = verifier.verify_transition(np.asarray([1.0]), np.asarray([-1.0]), action="control")

    assert result.status == "fail"
    assert any(issue.code == "negative_readout" for issue in result.issues)
