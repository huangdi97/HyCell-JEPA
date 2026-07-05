"""Streamlit demo for the HyCell-JEPA toy MVP loop."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np

from hycell.benchmark import run_toy_benchmark
from hycell.config import load_config
from hycell.datasets import build_transition_dataset, load_score_rows
from hycell.hdf_adapter import HDFAdapter
from hycell.planner import TargetStatePlanner
from hycell.training import load_model_npz
from hycell.verifier import BiologicalVerifier


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


def compute_demo_prediction(
    state: dict[str, Any],
    *,
    source_action: str,
    source_timepoint: str,
    action: str,
    target_timepoint: str,
) -> dict[str, Any]:
    dataset = state["dataset"]
    adapter = state["adapter"]
    current = adapter.state_for(dataset, action=source_action, source_timepoint=source_timepoint)
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


def compute_demo_plan(state: dict[str, Any], target_state: dict[str, float]) -> dict[str, Any]:
    dataset = state["dataset"]
    adapter = state["adapter"]
    planner = TargetStatePlanner(
        encoders=state["encoders"],
        core=state["core"],
        adapter=adapter,
        verifier=state["verifier"],
        feature_names=dataset.feature_names,
    )
    start = adapter.state_for(dataset, action="control", source_timepoint="t0")
    target = np.asarray([float(target_state[feature]) for feature in dataset.feature_names])
    return planner.plan(start, target, horizon=2, start_timepoint="t0").to_dict()


def render_app() -> None:
    try:
        import streamlit as st
    except ImportError as exc:
        raise SystemExit(
            "Streamlit is required to run the demo. Install requirements.txt first."
        ) from exc

    st.set_page_config(page_title="HyCell-JEPA Toy Demo", layout="wide")
    st.title("HyCell-JEPA Toy MVP")
    st.warning(
        "Toy engineering validation only. This demo is not biological evidence, "
        "not clinical guidance, and not a complete virtual cell."
    )

    state = load_demo_state()
    config = state["config"]
    adapter = state["adapter"]
    actions = adapter.actions

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        source_action = st.selectbox("Source toy condition", actions, index=actions.index(config.get("default_source_action", "control")))
    with col_b:
        action = st.selectbox("Toy action", actions, index=actions.index(config.get("default_action", "regeneration")))
    with col_c:
        transition = st.selectbox("Toy transition", ["t0->t1", "t1->t2"], index=0)
    source_timepoint, target_timepoint = transition.split("->")

    prediction = compute_demo_prediction(
        state,
        source_action=source_action,
        source_timepoint=source_timepoint,
        action=action,
        target_timepoint=target_timepoint,
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Current Compact State")
        st.json(prediction["current"])
    with right:
        st.subheader("Predicted Next Compact State")
        st.json(prediction["predicted"])

    st.subheader("Verifier")
    st.json(prediction["verification"])

    st.subheader("Planner")
    plan = compute_demo_plan(state, config["target_state"])
    st.json(plan)

    st.subheader("Benchmark Snapshot")
    benchmark_config = load_config(config.get("benchmark_config", "configs/benchmark_toy.yaml"))
    report = run_toy_benchmark(benchmark_config)
    st.json(
        {
            "transition_mse": report["transition_mse"],
            "verification_status_counts": report["verification_status_counts"],
            "report_path": report["report_path"],
        }
    )


def _state_dict(feature_names: list[str], state: np.ndarray) -> dict[str, float]:
    return {feature: float(value) for feature, value in zip(feature_names, state)}


if __name__ == "__main__":
    render_app()
