"""Lightweight real-matrix smoke training helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


REQUIRED_REAL_NPZ_KEYS = {
    "expression",
    "gene_names",
    "cell_ids",
    "dataset_id",
    "source",
    "is_real_data",
    "note",
}


def load_real_smoke_npz(path: str | Path) -> dict[str, Any]:
    """Load and validate a project-compatible real-data smoke NPZ."""

    input_path = Path(path)
    if not input_path.is_file():
        raise FileNotFoundError(
            f"Processed real-data NPZ not found: {input_path}. "
            "Run scripts/prepare_gse130973.py first to create it."
        )
    data = np.load(input_path, allow_pickle=False)
    missing = sorted(REQUIRED_REAL_NPZ_KEYS.difference(data.files))
    if missing:
        raise ValueError(f"{input_path} is missing required keys: {missing}")

    expression = np.asarray(data["expression"], dtype=np.float32)
    if expression.ndim != 2:
        raise ValueError(f"{input_path} expression must be a 2D cells x genes matrix")

    gene_names = _string_list(data["gene_names"])
    cell_ids = _string_list(data["cell_ids"])
    if expression.shape[0] != len(cell_ids):
        raise ValueError(f"{input_path} cell_ids length {len(cell_ids)} does not match expression rows {expression.shape[0]}")
    if expression.shape[1] != len(gene_names):
        raise ValueError(f"{input_path} gene_names length {len(gene_names)} does not match expression columns {expression.shape[1]}")

    return {
        "path": input_path,
        "expression": expression,
        "gene_names": gene_names,
        "cell_ids": cell_ids,
        "dataset_id": str(_scalar(data["dataset_id"])),
        "source": str(_scalar(data["source"])),
        "is_real_data": bool(_scalar(data["is_real_data"])),
        "note": str(_scalar(data["note"])),
    }


def evaluate_real_matrix(input_path: str | Path, *, output_dir: str | Path = "outputs/reports") -> dict[str, Any]:
    """Write descriptive matrix summaries for a real-data smoke NPZ."""

    dataset = load_real_smoke_npz(input_path)
    expression = dataset["expression"]
    gene_names = dataset["gene_names"]
    n_cells, n_genes = expression.shape
    zero_fraction = float(np.mean(expression == 0.0))
    mean_expression = float(np.mean(expression))
    gene_variances = np.var(expression, axis=0)
    top_indices = np.argsort(gene_variances)[::-1][: min(10, n_genes)]
    top_variable_genes = [
        {"gene": gene_names[int(idx)], "variance": float(gene_variances[int(idx)])}
        for idx in top_indices
    ]

    summary = {
        "data_status": "real_matrix_engineering_smoke_only_not_biological_validation",
        "input": str(dataset["path"]),
        "dataset_id": dataset["dataset_id"],
        "is_real_data": dataset["is_real_data"],
        "n_cells": int(n_cells),
        "n_genes": int(n_genes),
        "zero_fraction": zero_fraction,
        "sparsity": zero_fraction,
        "mean_expression": mean_expression,
        "top_variable_genes": top_variable_genes,
        "limitations": [
            "Descriptive matrix summary only.",
            "No donor age metadata is inferred.",
            "No HDF-only or fibroblast-only conclusion is claimed.",
            "Not biological discovery evidence.",
        ],
    }
    reports = Path(output_dir)
    reports.mkdir(parents=True, exist_ok=True)
    json_path = reports / "gse130973_real_matrix_summary.json"
    md_path = reports / "gse130973_real_matrix_summary.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_matrix_summary_markdown(summary), encoding="utf-8")
    summary["json_path"] = str(json_path)
    summary["report_path"] = str(md_path)
    return summary


def train_real_smoke_encoder(config: dict[str, Any]) -> dict[str, Any]:
    """Fit a deterministic encoder-style projection over a real expression matrix."""

    input_path = Path(str(config.get("input", "")))
    dataset = load_real_smoke_npz(input_path)
    expression = dataset["expression"]
    max_cells = int(config.get("max_cells", expression.shape[0]))
    max_genes = int(config.get("max_genes", expression.shape[1]))
    latent_dim = int(config.get("latent_dim", 64))
    seed = int(config.get("seed", 0))
    if max_cells <= 0 or max_genes <= 0 or latent_dim <= 0:
        raise ValueError("max_cells, max_genes, and latent_dim must be positive")

    matrix = expression[: min(max_cells, expression.shape[0]), : min(max_genes, expression.shape[1])]
    transformed = np.log1p(matrix)
    mean = transformed.mean(axis=0)
    scale = transformed.std(axis=0)
    scale = np.where(scale < 1e-6, 1.0, scale)
    normalized = (transformed - mean) / scale
    rng = np.random.default_rng(seed)
    projection = rng.normal(0.0, 1.0 / np.sqrt(normalized.shape[1]), size=(normalized.shape[1], latent_dim))
    embeddings = normalized @ projection

    output_dir = Path(str(config.get("output_dir", "outputs/gse130973_smoke")))
    reports_dir = Path(str(config.get("reports_dir", "outputs/reports")))
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = output_dir / "real_smoke_embeddings.npy"
    metrics_path = output_dir / "real_smoke_metrics.json"
    report_path = reports_dir / "gse130973_real_smoke_report.md"
    np.save(embeddings_path, embeddings.astype(np.float32))

    metrics = {
        "data_status": "real_matrix_encoder_smoke_only_not_biological_validation",
        "input": str(dataset["path"]),
        "dataset_id": dataset["dataset_id"],
        "source": dataset["source"],
        "is_real_data": dataset["is_real_data"],
        "n_cells": int(matrix.shape[0]),
        "n_genes": int(matrix.shape[1]),
        "latent_dim": int(latent_dim),
        "batch_size": int(config.get("batch_size", 256)),
        "epochs": int(config.get("epochs", 1)),
        "seed": seed,
        "embedding_shape": [int(embeddings.shape[0]), int(embeddings.shape[1])],
        "mean_abs_embedding": float(np.mean(np.abs(embeddings))),
        "embedding_std": float(np.std(embeddings)),
        "limitations": [
            "Encoder-style smoke projection over an unfiltered real skin single-cell matrix.",
            "No perturbation transitions are trained because labels are observational or unknown.",
            "No age labels are inferred.",
            "No HDF-only, fibroblast-only, rejuvenation, or biological discovery claim is made.",
        ],
    }
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_training_report_markdown(metrics), encoding="utf-8")
    return {
        "metrics": metrics,
        "metrics_path": metrics_path,
        "embeddings_path": embeddings_path,
        "report_path": report_path,
    }


def _matrix_summary_markdown(summary: dict[str, Any]) -> str:
    top_genes = "\n".join(
        f"- `{item['gene']}`: variance {item['variance']:.6f}"
        for item in summary["top_variable_genes"][:10]
    )
    return (
        "# GSE130973 Real Matrix Summary\n\n"
        "This is an engineering smoke summary only. It is not biological validation.\n\n"
        f"- Dataset: `{summary['dataset_id']}`\n"
        f"- Shape: {summary['n_cells']} cells x {summary['n_genes']} genes\n"
        f"- Zero fraction: {summary['zero_fraction']:.6f}\n"
        f"- Mean expression: {summary['mean_expression']:.6f}\n\n"
        "## Top Variable Genes\n\n"
        f"{top_genes}\n\n"
        "## Limitations\n\n"
        "- The matrix is unfiltered human skin single-cell smoke data.\n"
        "- Donor age labels are not available from the three GEO matrix files alone.\n"
        "- This does not prove HDF-specific behavior, rejuvenation, or biological discovery.\n"
    )


def _training_report_markdown(metrics: dict[str, Any]) -> str:
    return (
        "# GSE130973 Real Training Smoke Report\n\n"
        "This run validates that HyCell-JEPA can execute a lightweight encoder-style smoke pass on a real "
        "single-cell expression matrix. It is not a biological result.\n\n"
        "## What Ran\n\n"
        f"- Input: `{metrics['input']}`\n"
        f"- Dataset: `{metrics['dataset_id']}`\n"
        f"- Matrix used: {metrics['n_cells']} cells x {metrics['n_genes']} genes\n"
        f"- Latent dimension: {metrics['latent_dim']}\n"
        f"- Embedding shape: {metrics['embedding_shape']}\n\n"
        "## What This Validates\n\n"
        "- The processed NPZ can be loaded with required keys.\n"
        "- A deterministic, lightweight encoder-style projection can run on the real matrix.\n"
        "- Small metrics, embeddings, and a report can be written to ignored output paths.\n\n"
        "## What This Does Not Validate\n\n"
        "- No perturbation transitions are trained.\n"
        "- No planner is trained on unknown labels.\n"
        "- No donor age labels, fibroblast labels, HDF-only subset, rejuvenation signal, or biological mechanism is inferred.\n\n"
        "## Next Step\n\n"
        "Add reliable metadata or cell-type annotations, then create an explicitly documented HDF/fibroblast subset before "
        "attempting HDF-specific modeling.\n"
    )


def _string_list(values: np.ndarray) -> list[str]:
    return [str(_scalar(value)) for value in values.tolist()]


def _scalar(value: Any) -> Any:
    if isinstance(value, np.ndarray) and value.shape == ():
        value = value.item()
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value
