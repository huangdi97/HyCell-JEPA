"""Generate deterministic HyCell-JEPA toy single-cell perturbation data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.toy_data import (
    default_output_path,
    generate_toy_cells,
    toy_cell_columns,
    write_toy_cells,
    write_toy_npz,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", help="Path to toy data config for CSV mode.")
    parser.add_argument("--output", help="Optional output CSV path.")
    parser.add_argument("--n_cells", type=int, help="Number of toy cells for NPZ mode.")
    parser.add_argument("--n_genes", type=int, help="Number of toy genes for NPZ mode.")
    parser.add_argument("--out", help="Output NPZ path for explicit matrix mode.")
    parser.add_argument("--seed", type=int, default=1729, help="Random seed for NPZ mode.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.out or args.n_cells or args.n_genes:
        if not args.out or args.n_cells is None or args.n_genes is None:
            raise SystemExit("--out, --n_cells, and --n_genes are required together")
        output = write_toy_npz(
            args.out,
            n_cells=args.n_cells,
            n_genes=args.n_genes,
            seed=args.seed,
        )
        print(f"Wrote toy NPZ matrix ({args.n_cells} cells x {args.n_genes} genes) to {output}")
        return 0

    if not args.config:
        raise SystemExit("--config is required for CSV mode")

    config = load_config(args.config)
    rows = generate_toy_cells(config)
    output = Path(args.output) if args.output else default_output_path(config)
    write_toy_cells(rows, output, toy_cell_columns(config))
    print(f"Wrote {len(rows)} toy cells to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
