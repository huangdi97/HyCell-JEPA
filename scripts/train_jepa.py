"""Train the compact HyCell-JEPA toy JEPA transition core."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.training import train_toy_jepa


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to JEPA toy config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = train_toy_jepa(load_config(args.config))
    metrics = result["metrics"]
    print(
        "Trained toy JEPA transition core "
        f"({metrics['n_train']} train / {metrics['n_eval']} eval transitions). "
        f"train_mse={metrics['train_mse']:.6f} eval_mse={metrics['eval_mse']:.6f}"
    )
    print(f"Model: {result['model_path']}")
    if result.get("jepa_checkpoint"):
        print(f"JEPA checkpoint: {result['jepa_checkpoint']}")
    print(f"Metrics: {result['metrics_path']}")
    if result.get("jepa_metrics_path"):
        print(f"JEPA report metrics: {result['jepa_metrics_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
