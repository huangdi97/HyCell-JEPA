"""Package-level Streamlit app for the HyCell-JEPA toy MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from hycell.config import load_config
from hycell.datasets import build_transition_dataset, load_score_rows
from hycell.hdf_adapter import HDFAdapter
from hycell.planner import TargetStatePlanner
from hycell.training import load_model_npz
from hycell.verifier import BiologicalVerifier

STATE_PRESETS = {
    "baseline_hdf": {"source_action": "control", "source_timepoint": "t0"},
    "aged_hdf": {"source_action": "aging_stress", "source_timepoint": "t1"},
    "repairing_hdf": {"source_action": "regeneration", "source_timepoint": "t1"},
}


def load_demo_state(config_path: str = "configs/demo.yaml") -> dict[str, Any]:
    config = load_config(config_path)
    rows = load_score_rows(config["scores_path"])
    dataset = build_transition_dataset(rows)
    encoders, core = load_model_npz(config["model_path"])
    adapter = HDFAdapter()
    verifier = BiologicalVerifier(dataset.feature_names)
    return {
        "config": config,
        "dataset": dataset,
        "encoders": encoders,
        "core": core,
        "adapter": adapter,
        "verifier": verifier,
    }


def predict_for_selection(
    state: dict[str, Any],
    *,
    initial_state: str,
    action: str,
    target_timepoint: str = "t2",
) -> dict[str, Any]:
    preset = STATE_PRESETS[initial_state]
    dataset = state["dataset"]
    adapter = state["adapter"]
    current = adapter.state_for(
        dataset,
        action=preset["source_action"],
        source_timepoint=preset["source_timepoint"],
    )
    source_timepoint = preset["source_timepoint"]
    if source_timepoint == target_timepoint:
        target_timepoint = "t2" if source_timepoint == "t1" else "t1"
    model_inputs = adapter.model_inputs(
        current,
        action=action,
        source_timepoint=source_timepoint,
        target_timepoint=target_timepoint,
    )
    predicted = state["core"].predict(state["encoders"], *model_inputs)[0]
    verification = state["verifier"].verify_transition(current, predicted, action=action)
    return {
        "current": _state_dict(dataset.feature_names, current),
        "predicted": _state_dict(dataset.feature_names, predicted),
        "verification": verification.to_dict(),
    }


def plan_top_k_for_target(
    state: dict[str, Any],
    *,
    initial_state: str = "aged_hdf",
    target_state: dict[str, float] | None = None,
    k: int = 3,
) -> list[dict[str, Any]]:
    dataset = state["dataset"]
    adapter = state["adapter"]
    preset = STATE_PRESETS[initial_state]
    current = adapter.state_for(
        dataset,
        action=preset["source_action"],
        source_timepoint=preset["source_timepoint"],
    )
    target = target_state or state["config"]["target_state"]
    target_vector = np.asarray([float(target[feature]) for feature in dataset.feature_names])
    planner = TargetStatePlanner(
        encoders=state["encoders"],
        core=state["core"],
        adapter=adapter,
        verifier=state["verifier"],
        feature_names=dataset.feature_names,
    )
    plans = planner.plan_top_k(
        current,
        target_vector,
        horizon=2,
        start_timepoint=preset["source_timepoint"],
        k=k,
    )
    return [plan.to_dict() for plan in plans]


def render_app() -> None:
    import streamlit as st

    st.set_page_config(page_title="HyCell-JEPA Toy Demo", layout="wide")
    st.title("HyCell-JEPA Toy HDF MVP")
    st.warning(
        "Toy data is engineering validation only. Outputs are not biological "
        "discoveries, clinical guidance, or intervention recommendations."
    )

    state = load_demo_state()
    adapter = state["adapter"]
    initial_state = st.selectbox("Initial toy state", list(STATE_PRESETS), index=1)
    action = st.selectbox("Toy action", adapter.actions, index=adapter.actions.index("regeneration"))

    prediction = predict_for_selection(state, initial_state=initial_state, action=action)
    left, right = st.columns(2)
    with left:
        st.subheader("Current HDF Toy Readouts")
        st.json(prediction["current"])
    with right:
        st.subheader("Predicted HDF Toy Readouts")
        st.json(prediction["predicted"])

    st.subheader("Verifier Warnings")
    st.json(prediction["verification"])

    st.subheader("Planner Top-K Toy Actions")
    st.json(plan_top_k_for_target(state, initial_state=initial_state, k=3))


def _state_dict(feature_names: list[str], state: np.ndarray) -> dict[str, float]:
    return {feature: float(value) for feature, value in zip(feature_names, state)}


if __name__ == "__main__":
    render_app()
