"""Prepare a small local GSE130973 smoke NPZ artifact."""

from __future__ import annotations

import argparse

from hycell.real_datasets import save_gse130973_smoke_npz


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert local GSE130973 processed GEO Matrix Market files into a small HyCell smoke NPZ."
    )
    parser.add_argument("--raw-dir", default="data/raw/gse130973", help="Directory containing processed GEO files.")
    parser.add_argument(
        "--out",
        default="data/processed/gse130973/gse130973_smoke.npz",
        help="Output NPZ path.",
    )
    parser.add_argument("--max-cells", type=int, default=5000, help="Deterministic maximum number of cells to keep.")
    parser.add_argument("--max-genes", type=int, default=2000, help="Deterministic maximum number of genes to keep.")
    parser.add_argument("--seed", type=int, default=20260706, help="Fixed subsampling seed.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    dataset = save_gse130973_smoke_npz(
        args.raw_dir,
        args.out,
        max_cells=args.max_cells,
        max_genes=args.max_genes,
        seed=args.seed,
    )
    print(f"Prepared GSE130973 smoke NPZ: {args.out}")
    print(f"Shape: {dataset.n_cells} cells x {dataset.n_genes} genes")
    print(
        "WARNING: sample age/donor metadata is not available from the three filtered GEO files; "
        "state_label and age_label are set to unknown."
    )
    print("WARNING: no fibroblast-only filtering or biological interpretation is claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
