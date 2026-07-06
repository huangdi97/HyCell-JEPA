"""Validate a candidate real-data dataset against the HyCell schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hycell.config import load_config
from hycell.data_loaders import load_dataset
from hycell.perturbation_adapter import HDFAgingMetadataAdapter, PerturbationAdapter, aliases_from_config
from hycell.schema import AnnDataSchemaValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a small real-data candidate dataset against HyCell schema.")
    parser.add_argument("--input", help="Dataset path: csv, npz, or h5ad.")
    parser.add_argument("--schema", default="configs/real_data_schema.yaml", help="Schema config path.")
    parser.add_argument("--format", choices=["csv", "npz", "h5ad"], help="Override file format detection.")
    parser.add_argument("--output", default="outputs/reports/real_data_validation.json", help="Validation report path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config = load_config(args.schema)

    if not args.input:
        print("No --input provided; schema loaded and CLI is ready.")
        print(f"Schema: {args.schema}")
        return 0

    dataset = load_dataset(args.input, args.format)
    validator = AnnDataSchemaValidator(config)
    result = validator.validate(dataset)
    perturbation_adapter = PerturbationAdapter(aliases_from_config(config))
    hdf_adapter = HDFAgingMetadataAdapter(perturbation_adapter)
    mapped_rows = hdf_adapter.map_dataset(dataset)

    report = {
        "data_status": "schema_validation_only_not_biological_interpretation",
        "input": str(args.input),
        "format": dataset.file_format,
        "n_cells": dataset.n_cells,
        "n_genes": dataset.n_genes,
        "validation": result.to_dict(),
        "mapped_metadata_preview": mapped_rows[:5],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Validated {dataset.n_cells} cells x {dataset.n_genes} genes from {dataset.source_path}")
    print(f"Report: {output}")
    if not result.valid:
        for issue in result.errors:
            print(f"ERROR {issue.field}: {issue.message}")
        return 1
    for issue in result.warnings:
        print(f"WARNING {issue.field}: {issue.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
