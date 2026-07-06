"""Evaluate descriptive statistics for a real-data smoke NPZ."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.real_training import evaluate_real_matrix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Processed real-data smoke NPZ path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        summary = evaluate_real_matrix(args.input)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Evaluated real matrix: {summary['n_cells']} cells x {summary['n_genes']} genes")
    print(f"Zero fraction: {summary['zero_fraction']:.6f}")
    print(f"Mean expression: {summary['mean_expression']:.6f}")
    print(f"Summary JSON: {summary['json_path']}")
    print(f"Summary report: {summary['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
