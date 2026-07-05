"""Evaluate the compact HyCell-JEPA toy JEPA transition core."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.training import evaluate_toy_jepa


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to JEPA toy config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = evaluate_toy_jepa(load_config(args.config))
    print(
        "Evaluated toy JEPA transition core "
        f"on {metrics['n_transitions']} transitions. mse={metrics['mse']:.6f}"
    )
    print(f"Metrics: {metrics['metrics_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
