"""Gene set scoring for toy single-cell expression tables."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

SCORE_METADATA_COLUMNS = [
    "cell_id",
    "action",
    "action_label",
    "timepoint",
    "cell_system",
    "is_toy",
]


def score_gene_sets(
    cell_rows: Iterable[dict[str, Any]],
    gene_sets: dict[str, list[str]],
    *,
    missing_gene_policy: str = "error",
) -> list[dict[str, Any]]:
    """Compute per-cell mean-expression scores for configured gene sets."""

    rows = list(cell_rows)
    if not rows:
        raise ValueError("cannot score an empty cell table")
    available = set(rows[0].keys())
    missing = {
        gene_set: [gene for gene in genes if gene not in available]
        for gene_set, genes in gene_sets.items()
    }
    missing = {name: genes for name, genes in missing.items() if genes}
    if missing and missing_gene_policy == "error":
        details = "; ".join(f"{name}: {', '.join(genes)}" for name, genes in missing.items())
        raise ValueError(f"missing genes for configured gene sets: {details}")

    scored_rows: list[dict[str, Any]] = []
    for row in rows:
        scored: dict[str, Any] = {
            column: row.get(column, "") for column in SCORE_METADATA_COLUMNS
        }
        for gene_set, genes in gene_sets.items():
            present_genes = [gene for gene in genes if gene in row]
            if not present_genes:
                scored[gene_set] = ""
                continue
            values = [float(row[gene]) for gene in present_genes]
            scored[gene_set] = round(sum(values) / len(values), 4)
        scored_rows.append(scored)
    return scored_rows


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    """Read CSV rows as dictionaries."""

    with Path(path).open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_score_rows(rows: Iterable[dict[str, Any]], path: str | Path) -> Path:
    """Write scored rows to CSV with stable columns."""

    rows = list(rows)
    if not rows:
        raise ValueError("cannot write an empty score table")
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def gene_sets_from_config(config: dict[str, Any]) -> dict[str, list[str]]:
    """Extract and validate configured gene sets."""

    gene_sets = config.get("gene_sets")
    if not isinstance(gene_sets, dict) or not gene_sets:
        raise ValueError("config field 'gene_sets' must be a non-empty object")
    parsed: dict[str, list[str]] = {}
    for name, genes in gene_sets.items():
        if not isinstance(genes, list) or not genes:
            raise ValueError(f"gene set {name!r} must be a non-empty list")
        parsed[str(name)] = [str(gene) for gene in genes]
    return parsed


def default_output_path(config: dict[str, Any]) -> Path:
    """Return the configured gene-set score output path."""

    return Path(config.get("output_dir", "outputs/toy_data")) / str(
        config.get("output_filename", "gene_set_scores.csv")
    )
