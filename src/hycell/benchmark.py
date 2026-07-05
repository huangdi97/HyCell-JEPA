"""End-to-end toy benchmark for adapter, verifier, planner, and JEPA."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from hycell.datasets import build_transition_dataset, load_score_rows
from hycell.hdf_adapter import HDFAdapter
from hycell.jepa import mean_squared_error
from hycell.planner import TargetStatePlanner
from hycell.training import load_model_npz
from hycell.verifier import BiologicalVerifier


def run_toy_benchmark(config: dict[str, Any]) -> dict[str, Any]:
    rows = load_score_rows(config["scores_path"])
    dataset = build_transition_dataset(
        rows,
        feature_names=[str(item) for item in config.get("belief_features", [])] or None,
        timepoints=[str(item) for item in config.get("timepoints", [])] or None,
    )
    encoders, core = load_model_npz(config["model_path"])
    adapter = HDFAdapter()
    verifier = BiologicalVerifier(dataset.feature_names)

    predictions = core.predict(
        encoders,
        dataset.current_states,
        dataset.actions,
        dataset.context_labels,
        dataset.adapter_labels,
    )
    verification_results = [
        verifier.verify_transition(current, predicted, action=str(action)).to_dict()
        for current, predicted, action in zip(dataset.current_states, predictions, dataset.actions)
    ]
    status_counts: dict[str, int] = {}
    for result in verification_results:
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1

    planner_config = dict(config.get("planner", {}))
    start_state = adapter.state_for(
        dataset,
        action=str(planner_config.get("start_action", "control")),
        source_timepoint=str(planner_config.get("start_timepoint", "t0")),
    )
    target_state = np.asarray(
        [float(planner_config.get("target_state", {}).get(feature, start_state[idx])) for idx, feature in enumerate(dataset.feature_names)],
        dtype=np.float64,
    )
    planner = TargetStatePlanner(
        encoders=encoders,
        core=core,
        adapter=adapter,
        verifier=verifier,
        feature_names=dataset.feature_names,
    )
    plan = planner.plan(
        start_state,
        target_state,
        horizon=int(planner_config.get("horizon", 2)),
        start_timepoint=str(planner_config.get("start_timepoint", "t0")),
    )

    report = {
        "data_status": "toy_engineering_validation_only",
        "n_transitions": dataset.n_examples,
        "transition_mse": mean_squared_error(predictions, dataset.next_states),
        "verification_status_counts": status_counts,
        "planner": plan.to_dict(),
        "adapter_actions": adapter.describe_actions(),
        "limitations": [
            "Toy benchmark only; not biological validation.",
            "Planner output is not a recommendation.",
            "Model predicts compact readout features only.",
        ],
    }
    output_dir = Path(config.get("output_dir", "outputs/benchmark_toy"))
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / str(config.get("report_filename", "benchmark_report.json"))
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    return report
