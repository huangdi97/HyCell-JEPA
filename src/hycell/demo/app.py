"""Package-level Streamlit app for the HyCell-JEPA toy MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from hycell.benchmark import run_toy_benchmark
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

    st.set_page_config(page_title="HyCell-JEPA v0.1 Demo", layout="wide")
    st.title("HyCell-JEPA v0.1 Demo")
    st.caption(
        "Universal-to-Specific Cellular World Model Prototype for HDF Aging, "
        "Regeneration, and Perturbation Planning."
    )
    st.warning(
        "Engineering validation only. Not biological discovery, not clinical advice, "
        "not therapy recommendation."
    )

    state = load_demo_state()
    config = state["config"]
    dataset = state["dataset"]
    adapter = state["adapter"]
    benchmark_config = load_config(config.get("benchmark_config", "configs/benchmark_toy.yaml"))
    report = run_toy_benchmark(benchmark_config)

    metric_columns = st.columns(5)
    metric_columns[0].metric("Toy transitions", dataset.n_examples)
    metric_columns[1].metric("Compact readouts", len(dataset.feature_names))
    metric_columns[2].metric("Verifier status", _status_from_counts(report["verification_status_counts"]))
    metric_columns[3].metric("Real-data smoke dataset", "GSE130973")
    metric_columns[4].metric("Release version", "v0.1.1")

    toy_tab, planner_tab, verifier_tab, real_data_tab, about_tab = st.tabs(
        ["Toy Transition", "Planner", "Verifier", "Real-Data Smoke", "About"]
    )

    with toy_tab:
        initial_state = st.selectbox("Source condition", list(STATE_PRESETS), index=1)
        action = st.selectbox("Action", adapter.actions, index=adapter.actions.index("regeneration"))
        transition = st.selectbox("Transition", ["preset->t2"], index=0)

        prediction = predict_for_selection(state, initial_state=initial_state, action=action)
        st.subheader("Compact State Transition")
        st.dataframe(
            _comparison_rows(prediction["current"], prediction["predicted"]),
            use_container_width=True,
            hide_index=True,
        )
        with st.expander("Raw transition JSON"):
            st.json(
                {
                    "source_condition": initial_state,
                    "action": action,
                    "transition": transition,
                    "current": prediction["current"],
                    "predicted": prediction["predicted"],
                }
            )

    with planner_tab:
        st.info(
            "Planner output is a toy demonstration over compact readouts, not a therapy "
            "recommendation or protocol."
        )
        plans = plan_top_k_for_target(state, initial_state=initial_state, k=3)
        st.subheader("Top-K Toy Action Sequences")
        st.dataframe(_plan_rows(plans), use_container_width=True, hide_index=True)
        with st.expander("Raw planner JSON"):
            st.json(plans)

    with verifier_tab:
        verification = prediction["verification"]
        _render_status_badge(st, verification.get("status", "warn"))
        for issue in verification.get("issues", []):
            severity = str(issue.get("severity", "warn")).upper()
            st.write(f"**{severity} - {issue.get('code', 'unknown')}:** {issue.get('message', '')}")
        with st.expander("Raw verifier JSON"):
            st.json(verification)

    with real_data_tab:
        st.subheader("GSE130973 Smoke Status")
        st.write("Real single-cell matrix smoke workflow.")
        st.dataframe(
            [
                {"field": "default processed shape", "value": "5000 cells x 2000 genes"},
                {"field": "cell_system", "value": "skin_single_cell_unfiltered"},
                {"field": "age_label", "value": "unknown"},
                {"field": "state_label", "value": "unknown"},
                {"field": "scope", "value": "not HDF-only"},
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.code(
            "\n".join(
                [
                    "python scripts/inspect_gse130973.py --raw-dir data/raw/gse130973",
                    "python scripts/prepare_gse130973.py --raw-dir data/raw/gse130973 --out data/processed/gse130973/gse130973_smoke.npz --max-cells 5000 --max-genes 2000",
                    "python scripts/train_real_smoke.py --config configs/train_gse130973_smoke.yaml",
                ]
            ),
            language="bash",
        )

    with about_tab:
        st.subheader("What HyCell-JEPA Is")
        st.write(
            "HyCell-JEPA is a Universal-to-Specific cellular world model prototype for "
            "compact cellular belief-state transitions."
        )
        st.subheader("What v0.1 Proves")
        st.write(
            "v0.1 proves a runnable engineering path across toy data, compact transition "
            "modeling, verifier checks, planner demos, real-matrix smoke ingestion, and "
            "release verification."
        )
        st.subheader("What It Does Not Prove")
        st.write(
            "v0.1 does not prove biological rejuvenation, therapy safety, clinical utility, "
            "HDF-only real-data conclusions, or full virtual-cell behavior."
        )
        st.markdown("Read more in [README.md](README.md) and [docs/limitations.md](docs/limitations.md).")


def _comparison_rows(current: dict[str, float], predicted: dict[str, float]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for readout, current_value in current.items():
        predicted_value = predicted[readout]
        rows.append(
            {
                "readout": readout,
                "current": round(float(current_value), 4),
                "predicted": round(float(predicted_value), 4),
                "delta": round(float(predicted_value - current_value), 4),
            }
        )
    return rows


def _plan_rows(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for rank, plan in enumerate(plans, start=1):
        rows.append(
            {
                "rank": rank,
                "action_sequence": " -> ".join(plan["actions"]),
                "distance_to_target": round(float(plan["distance"]), 6),
                "verifier_status": plan.get("verification", {}).get("status", "unknown"),
            }
        )
    return rows


def _render_status_badge(st: Any, status: str) -> None:
    normalized = status.lower()
    if normalized == "pass":
        st.success("Status: pass")
    elif normalized == "fail":
        st.error("Status: fail")
    else:
        st.warning("Status: warn")


def _status_from_counts(status_counts: dict[str, int]) -> str:
    if status_counts.get("fail", 0):
        return "fail"
    if status_counts.get("warn", 0):
        return "warn"
    return "pass"


def _state_dict(feature_names: list[str], state: np.ndarray) -> dict[str, float]:
    return {feature: float(value) for feature, value in zip(feature_names, state)}


if __name__ == "__main__":
    render_app()
