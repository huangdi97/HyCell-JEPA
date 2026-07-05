"""Build a lightweight HyCell-JEPA evidence graph from toy score rows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hycell.evidence_graph import build_evidence_graph, default_output_path, write_evidence_graph
from hycell.gene_sets import read_csv_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scores", required=True, help="Input gene-set score CSV path.")
    parser.add_argument("--output", help="Optional evidence graph JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = read_csv_rows(args.scores)
    graph = build_evidence_graph(rows)
    output = Path(args.output) if args.output else default_output_path(args.scores)
    write_evidence_graph(graph, output)
    print(
        f"Wrote evidence graph with {len(graph['nodes'])} nodes and "
        f"{len(graph['edges'])} edges to {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
