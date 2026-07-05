"""Score configured gene sets over a HyCell-JEPA toy expression table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.config import load_config
from hycell.gene_sets import (
    default_output_path,
    gene_sets_from_config,
    read_csv_rows,
    score_gene_sets,
    write_score_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input toy-cell CSV path.")
    parser.add_argument("--config", required=True, help="Path to gene-set config.")
    parser.add_argument("--output", help="Optional score CSV path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    gene_sets = gene_sets_from_config(config)
    rows = read_csv_rows(args.input)
    scored = score_gene_sets(
        rows,
        gene_sets,
        missing_gene_policy=str(config.get("missing_gene_policy", "error")),
    )
    output = Path(args.output) if args.output else default_output_path(config)
    write_score_rows(scored, output)
    print(f"Wrote {len(scored)} scored cells to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
