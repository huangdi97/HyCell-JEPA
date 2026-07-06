"""Inspect a local candidate real-data dataset without downloading anything."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hycell.config import load_config
from hycell.data_loaders import load_dataset
from hycell.schema import AnnDataSchemaValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect a small local dataset for the HyCell real-data smoke path.")
    parser.add_argument("--input", help="Local dataset path: csv, npz, or h5ad.")
    parser.add_argument("--format", choices=["csv", "npz", "h5ad"], help="Override file format detection.")
    parser.add_argument("--schema", default="configs/real_data_schema.yaml", help="Schema config path.")
    parser.add_argument("--output", default="outputs/reports/real_data_inspection.json", help="Inspection JSON path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.input:
        print("No --input provided. Supply a small local csv, npz, or h5ad file; no dataset is downloaded automatically.")
        return 2

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Dataset not found: {input_path}. Provide a small local fixture or candidate dataset; no download was attempted.")
        return 2

    dataset = load_dataset(input_path, args.format)
    result = AnnDataSchemaValidator(load_config(args.schema)).validate(dataset)
    perturbations = sorted({str(row.get("perturbation", "")) for row in dataset.obs if row.get("perturbation")})
    cell_systems = sorted({str(row.get("cell_system", "")) for row in dataset.obs if row.get("cell_system")})

    report = {
        "data_status": "inspection_only_not_biological_validation",
        "input": str(input_path),
        "format": dataset.file_format,
        "n_cells": dataset.n_cells,
        "n_genes": dataset.n_genes,
        "var_names_preview": dataset.var_names[:10],
        "perturbations": perturbations,
        "cell_systems": cell_systems,
        "validation": result.to_dict(),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Inspected {dataset.n_cells} cells x {dataset.n_genes} genes from {dataset.source_path}")
    print(f"Report: {output}")
    if not result.valid:
        print("Inspection completed with schema errors; see report for details.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
