"""Preprocess a small local candidate dataset for HyCell smoke validation."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from hycell.config import load_config
from hycell.data_loaders import load_dataset
from hycell.perturbation_adapter import HDFAgingMetadataAdapter, PerturbationAdapter, aliases_from_config
from hycell.schema import AnnDataSchemaValidator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preprocess a small local dataset into normalized smoke-test artifacts.")
    parser.add_argument("--input", help="Local dataset path: csv, npz, or h5ad.")
    parser.add_argument("--format", choices=["csv", "npz", "h5ad"], help="Override file format detection.")
    parser.add_argument("--schema", default="configs/real_data_schema.yaml", help="Schema config path.")
    parser.add_argument("--output", default="outputs/real_data_smoke/preprocessed_cells.csv", help="Normalized CSV output path.")
    parser.add_argument("--report", default="outputs/real_data_smoke/preprocess_report.json", help="Preprocess report path.")
    parser.add_argument("--max-cells", type=int, default=128, help="Maximum cells to write for a local smoke artifact.")
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

    config = load_config(args.schema)
    dataset = load_dataset(input_path, args.format)
    result = AnnDataSchemaValidator(config).validate(dataset)
    if not result.valid:
        _write_report(args.report, input_path, dataset, result.to_dict(), [], "failed_schema_validation")
        print("Preprocess aborted: dataset failed schema validation. See report for details.")
        return 1

    mapped_rows = HDFAgingMetadataAdapter(PerturbationAdapter(aliases_from_config(config))).map_dataset(dataset)
    written_rows = _write_normalized_csv(Path(args.output), dataset, mapped_rows, max_cells=args.max_cells)
    _write_report(args.report, input_path, dataset, result.to_dict(), mapped_rows[:5], "ok", written_rows=written_rows)

    print(f"Wrote normalized smoke artifact with {written_rows} cells to {args.output}")
    print(f"Report: {args.report}")
    return 0


def _write_normalized_csv(output: Path, dataset, mapped_rows: list[dict[str, str]], *, max_cells: int) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    n_rows = min(dataset.n_cells, max_cells)
    gene_columns = dataset.var_names
    fieldnames = [
        "cell_id",
        "original_perturbation",
        "canonical_action",
        "mapping_status",
        "timepoint",
        "cell_system",
        "adapter_label",
        "context_label",
        *gene_columns,
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx in range(n_rows):
            row = dict(mapped_rows[idx])
            for gene_idx, gene_name in enumerate(gene_columns):
                row[gene_name] = float(dataset.expression[idx, gene_idx])
            writer.writerow(row)
    return n_rows


def _write_report(
    report_path: str,
    input_path: Path,
    dataset,
    validation: dict,
    mapped_preview: list[dict[str, str]],
    status: str,
    *,
    written_rows: int = 0,
) -> None:
    report = {
        "data_status": "preprocess_smoke_only_not_biological_validation",
        "status": status,
        "input": str(input_path),
        "format": dataset.file_format,
        "n_cells": dataset.n_cells,
        "n_genes": dataset.n_genes,
        "written_rows": written_rows,
        "validation": validation,
        "mapped_metadata_preview": mapped_preview,
    }
    output = Path(report_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
