"""Train compact HyCell-JEPA toy encoders and write local artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.training import train_toy_encoder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Path to local training config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = train_toy_encoder(load_config(args.config))
    metrics = result["metrics"]
    print(
        "Trained toy encoders "
        f"for {metrics['n_transitions']} transitions with embedding shape "
        f"{tuple(metrics['embedding_shape'])}."
    )
    print(f"Encoder checkpoint: {result['encoder_checkpoint']}")
    print(f"Embeddings: {result['embeddings_path']}")
    print(f"Metrics: {result['metrics_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
