"""Compatibility benchmark CLI for toy JEPA checkpoints."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.benchmark import run_toy_benchmark
from hycell.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, help="Toy JEPA checkpoint path.")
    parser.add_argument("--config", default="configs/benchmark_toy.yaml", help="Benchmark config path.")
    parser.add_argument("--report-dir", default="outputs/reports", help="Output report directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = Path(args.checkpoint)
    if not checkpoint.exists():
        raise SystemExit(f"Checkpoint not found: {checkpoint}")

    config = dict(load_config(args.config))
    config["model_path"] = str(checkpoint)
    config["output_dir"] = args.report_dir
    config["report_filename"] = "benchmark_metrics.json"
    report = run_toy_benchmark(config)

    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = report_dir / "benchmark_metrics.json"
    md_path = report_dir / "benchmark_report.md"
    metrics_path.write_text(json.dumps(_json_safe(report), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_benchmark_markdown(report), encoding="utf-8")

    print(
        "Toy benchmark complete: "
        f"mse={report['transition_mse']:.6f}, "
        f"planner={report['planner']['actions']}, "
        f"metrics={metrics_path}, report={md_path}"
    )
    return 0


def _benchmark_markdown(report: dict) -> str:
    return (
        "# HyCell-JEPA Toy Benchmark\n\n"
        "Toy engineering validation only. This is not biological evidence or clinical guidance.\n\n"
        f"- Transitions: {report['n_transitions']}\n"
        f"- Transition MSE: {report['transition_mse']:.9f}\n"
        f"- Verifier statuses: `{json.dumps(report['verification_status_counts'], sort_keys=True)}`\n"
        f"- Planner actions: `{' -> '.join(report['planner']['actions'])}`\n"
        f"- Planner distance: `{report['planner']['distance']:.9f}`\n"
    )


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items() if key != "report_path"}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
