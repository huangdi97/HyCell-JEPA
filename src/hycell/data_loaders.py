"""Small real-data loader interfaces for candidate single-cell datasets."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


KNOWN_OBS_FIELDS = {
    "cell_id",
    "cell_ids",
    "perturbation",
    "perturbations",
    "action",
    "actions",
    "timepoint",
    "timepoints",
    "cell_system",
    "cell_type",
    "condition",
    "batch",
    "donor_id",
    "age_group",
}


@dataclass(frozen=True)
class SingleCellDataset:
    """Minimal AnnData-like in-memory representation used by validators."""

    expression: np.ndarray
    obs: list[dict[str, Any]]
    var_names: list[str]
    source_path: str
    file_format: str

    @property
    def n_cells(self) -> int:
        return int(self.expression.shape[0])

    @property
    def n_genes(self) -> int:
        return int(self.expression.shape[1])


def load_dataset(path: str | Path, file_format: str | None = None) -> SingleCellDataset:
    """Load a small candidate dataset by extension or explicit format."""

    dataset_path = Path(path)
    fmt = (file_format or dataset_path.suffix.lstrip(".")).lower()
    if fmt == "csv":
        return load_csv_dataset(dataset_path)
    if fmt == "npz":
        return load_npz_dataset(dataset_path)
    if fmt == "h5ad":
        return load_h5ad_dataset(dataset_path)
    raise ValueError(f"unsupported dataset format {fmt!r}; expected one of csv, npz, h5ad")


def load_csv_dataset(path: str | Path) -> SingleCellDataset:
    """Load CSV metadata columns plus numeric gene-expression columns."""

    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{dataset_path} has no header row")
        fieldnames = list(reader.fieldnames)
        gene_columns = [name for name in fieldnames if name not in KNOWN_OBS_FIELDS]
        obs_columns = [name for name in fieldnames if name in KNOWN_OBS_FIELDS]
        if not gene_columns:
            raise ValueError(f"{dataset_path} has no numeric gene-expression columns")

        obs: list[dict[str, Any]] = []
        matrix: list[list[float]] = []
        for row_index, row in enumerate(reader, start=2):
            obs.append(_normalize_obs_row({key: row[key] for key in obs_columns if key in row}))
            values: list[float] = []
            for gene in gene_columns:
                try:
                    values.append(float(row[gene]))
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{dataset_path}:{row_index} gene column {gene!r} is not numeric") from exc
            matrix.append(values)

    if not matrix:
        raise ValueError(f"{dataset_path} has no data rows")
    return SingleCellDataset(
        expression=np.asarray(matrix, dtype=np.float64),
        obs=obs,
        var_names=gene_columns,
        source_path=str(dataset_path),
        file_format="csv",
    )


def load_npz_dataset(path: str | Path) -> SingleCellDataset:
    """Load a small NPZ dataset with `expression` or `X` plus metadata arrays."""

    dataset_path = Path(path)
    data = np.load(dataset_path, allow_pickle=False)
    if "expression" in data:
        expression = data["expression"]
    elif "X" in data:
        expression = data["X"]
    else:
        raise ValueError(f"{dataset_path} must contain an 'expression' or 'X' array")

    expression = np.asarray(expression, dtype=np.float64)
    if expression.ndim != 2:
        raise ValueError(f"{dataset_path} expression matrix must be 2-dimensional")

    if "gene_names" in data:
        var_names = _string_list(data["gene_names"])
    elif "var_names" in data:
        var_names = _string_list(data["var_names"])
    else:
        raise ValueError(f"{dataset_path} must contain 'gene_names' or 'var_names'")

    n_cells = expression.shape[0]
    obs: list[dict[str, Any]] = [dict() for _ in range(n_cells)]
    skip = {"expression", "X", "gene_names", "var_names", "is_toy"}
    for key in data.files:
        if key in skip:
            continue
        values = data[key]
        if values.shape == ():
            continue
        if len(values) != n_cells:
            raise ValueError(f"{dataset_path} metadata array {key!r} has {len(values)} rows, expected {n_cells}")
        canonical_key = _metadata_key_alias(key)
        for row, value in zip(obs, values):
            row[canonical_key] = _to_python_scalar(value)
            if canonical_key != key:
                row[key] = _to_python_scalar(value)

    for idx, row in enumerate(obs):
        row.setdefault("cell_id", f"cell_{idx:06d}")

    return SingleCellDataset(
        expression=expression,
        obs=[_normalize_obs_row(row) for row in obs],
        var_names=var_names,
        source_path=str(dataset_path),
        file_format="npz",
    )


def load_h5ad_dataset(path: str | Path) -> SingleCellDataset:
    """Load an H5AD dataset if optional `anndata` is installed."""

    dataset_path = Path(path)
    try:
        import anndata as ad
    except ImportError as exc:
        raise ImportError("H5AD loading requires optional dependency 'anndata'. Install it to read .h5ad files.") from exc

    adata = ad.read_h5ad(dataset_path)
    expression = adata.X
    if hasattr(expression, "toarray"):
        expression = expression.toarray()
    expression = np.asarray(expression, dtype=np.float64)
    obs = [
        _normalize_obs_row({column: _to_python_scalar(value) for column, value in row.items()})
        for row in adata.obs.to_dict(orient="records")
    ]
    var_names = [str(name) for name in adata.var_names]
    return SingleCellDataset(
        expression=expression,
        obs=obs,
        var_names=var_names,
        source_path=str(dataset_path),
        file_format="h5ad",
    )


def _metadata_key_alias(key: str) -> str:
    aliases = {
        "cell_ids": "cell_id",
        "actions": "perturbation",
        "action": "perturbation",
        "perturbations": "perturbation",
        "timepoints": "timepoint",
        "cell_type": "cell_system",
    }
    return aliases.get(key, key)


def _normalize_obs_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    for source, target in (
        ("cell_ids", "cell_id"),
        ("actions", "perturbation"),
        ("action", "perturbation"),
        ("perturbations", "perturbation"),
        ("timepoints", "timepoint"),
        ("cell_type", "cell_system"),
    ):
        if target not in normalized and source in normalized:
            normalized[target] = normalized[source]
    return normalized


def _string_list(values: np.ndarray) -> list[str]:
    return [str(_to_python_scalar(value)) for value in values.tolist()]


def _to_python_scalar(value: Any) -> Any:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value
