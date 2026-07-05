"""Run the HyCell-JEPA toy end-to-end benchmark."""

from __future__ import annotations

import argparse
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
    parser.add_argument("--config", required=True, help="Path to toy benchmark config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_toy_benchmark(load_config(args.config))
    print(
        "Ran toy benchmark "
        f"on {report['n_transitions']} transitions. "
        f"mse={report['transition_mse']:.6f} "
        f"best_plan={report['planner']['actions']}"
    )
    print(f"Report: {report['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
