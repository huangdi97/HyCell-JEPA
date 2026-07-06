"""Run a lightweight real-data encoder smoke training pass."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.real_training import train_real_smoke_encoder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to real-data smoke training config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = train_real_smoke_encoder(load_config(args.config))
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    metrics = result["metrics"]
    print(
        "Ran real-data encoder smoke "
        f"on {metrics['n_cells']} cells x {metrics['n_genes']} genes "
        f"with latent_dim={metrics['latent_dim']}."
    )
    print(f"Metrics: {result['metrics_path']}")
    print(f"Embeddings: {result['embeddings_path']}")
    print(f"Report: {result['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
