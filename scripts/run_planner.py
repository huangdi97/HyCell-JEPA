"""Compatibility planner CLI for toy JEPA checkpoints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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

TARGET_PRESETS = {
    "rejuvenated_repair": {
        "senescence": 0.85,
        "proliferation": 2.25,
        "ecm_remodeling": 2.70,
        "stress_inflammation": 0.50,
        "reprogramming_plasticity": 0.35,
        "viability_qc_proxy": 2.25,
    },
    "low_stress": {
        "senescence": 0.90,
        "proliferation": 2.00,
        "ecm_remodeling": 2.50,
        "stress_inflammation": 0.40,
        "reprogramming_plasticity": 0.25,
        "viability_qc_proxy": 2.20,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, help="Toy JEPA checkpoint path.")
    parser.add_argument("--state", default="aged_hdf", choices=sorted(STATE_PRESETS), help="Initial toy state preset.")
    parser.add_argument("--target", default="rejuvenated_repair", choices=sorted(TARGET_PRESETS), help="Target toy state preset.")
    parser.add_argument("--config", default="configs/benchmark_toy.yaml", help="Planner/benchmark config path.")
    parser.add_argument("--top-k", type=int, default=3, help="Number of toy action sequences to report.")
    parser.add_argument("--report-dir", default="outputs/reports", help="Output report directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = Path(args.checkpoint)
    if not checkpoint.exists():
        raise SystemExit(f"Checkpoint not found: {checkpoint}")

    config = load_config(args.config)
    rows = load_score_rows(config["scores_path"])
    dataset = build_transition_dataset(
        rows,
        feature_names=[str(item) for item in config.get("belief_features", [])] or None,
        timepoints=[str(item) for item in config.get("timepoints", [])] or None,
    )
    encoders, core = load_model_npz(checkpoint)
    adapter = HDFAdapter()
    verifier = BiologicalVerifier(dataset.feature_names)
    planner = TargetStatePlanner(
        encoders=encoders,
        core=core,
        adapter=adapter,
        verifier=verifier,
        feature_names=dataset.feature_names,
    )

    state_preset = STATE_PRESETS[args.state]
    start_state = adapter.state_for(
        dataset,
        action=state_preset["source_action"],
        source_timepoint=state_preset["source_timepoint"],
    )
    target_preset = TARGET_PRESETS[args.target]
    target = np.asarray([float(target_preset[feature]) for feature in dataset.feature_names])
    plans = planner.plan_top_k(
        start_state,
        target,
        horizon=2,
        start_timepoint=state_preset["source_timepoint"],
        k=args.top_k,
    )
    payload = {
        "data_status": "toy_engineering_validation_only",
        "initial_state": args.state,
        "target": args.target,
        "top_k": [plan.to_dict() for plan in plans],
        "limitations": [
            "Toy planner output is not a recommendation.",
            "No biological discovery claim is made.",
        ],
    }

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    actions_path = report_dir / "top_k_actions.json"
    report_path = report_dir / "planner_report.md"
    actions_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_planner_markdown(payload), encoding="utf-8")

    print("Top-K toy action sequences:")
    for rank, plan in enumerate(plans, start=1):
        print(f"{rank}. {' -> '.join(plan.actions)} | distance={plan.distance:.6f}")
    print(f"Actions: {actions_path}")
    print(f"Report: {report_path}")
    return 0


def _planner_markdown(payload: dict) -> str:
    lines = [
        "# HyCell-JEPA Toy Planner",
        "",
        "Toy engineering validation only. These action sequences are not recommendations.",
        "",
        f"- Initial state: `{payload['initial_state']}`",
        f"- Target: `{payload['target']}`",
        "",
        "## Top-K Actions",
    ]
    for rank, plan in enumerate(payload["top_k"], start=1):
        lines.append(f"{rank}. `{' -> '.join(plan['actions'])}` distance=`{plan['distance']:.9f}`")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
