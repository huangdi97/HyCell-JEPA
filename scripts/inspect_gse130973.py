"""Inspect local GSE130973 processed GEO files without downloading data."""

from __future__ import annotations

import argparse

from hycell.real_datasets import GSE130973_REQUIRED_FILES, inspect_gse130973


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect local GSE130973 processed GEO Matrix Market files.")
    parser.add_argument("--raw-dir", default="data/raw/gse130973", help="Directory containing processed GEO files.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inspection = inspect_gse130973(args.raw_dir)

    print(f"GSE130973 raw directory: {inspection.paths.raw_dir}")
    for key in ("barcodes", "genes", "matrix"):
        filename = GSE130973_REQUIRED_FILES[key]
        exists = inspection.file_exists[key]
        size = inspection.file_sizes[key]
        size_text = f"{size} bytes" if size is not None else "missing"
        print(f"{filename}: exists={str(exists).lower()} size={size_text}")

    if inspection.matrix_shape is not None:
        rows, cols = inspection.matrix_shape
        print(f"matrix shape: {rows} x {cols}")
        print(f"matrix nonzero entries: {inspection.matrix_entries}")
    else:
        print("matrix shape: unavailable")
    print(f"number of genes: {inspection.gene_count if inspection.gene_count is not None else 'unavailable'}")
    print(f"number of barcodes: {inspection.barcode_count if inspection.barcode_count is not None else 'unavailable'}")
    print(f"first genes: {inspection.first_genes}")
    print(f"first barcodes: {inspection.first_barcodes}")
    print(f"orientation: {inspection.orientation or 'unavailable'}")

    missing = [name for name, exists in inspection.file_exists.items() if not exists]
    for mismatch in inspection.mismatches:
        print(f"MISMATCH: {mismatch}")
    if missing:
        print(f"Missing required files: {', '.join(missing)}")
        return 1
    if inspection.mismatches:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
