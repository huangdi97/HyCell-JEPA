"""Dataset-specific loaders for local real-data smoke workflows."""

from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from hycell.data_loaders import SingleCellDataset


GSE130973_DATASET_ID = "gse130973"
GSE130973_SOURCE = "GSE130973 processed GEO filtered Matrix Market files"
GSE130973_REQUIRED_FILES = {
    "barcodes": "GSE130973_barcodes_filtered.tsv.gz",
    "genes": "GSE130973_genes_filtered.tsv.gz",
    "matrix": "GSE130973_matrix_filtered.mtx.gz",
}


@dataclass(frozen=True)
class GSE130973Paths:
    raw_dir: Path
    barcodes: Path
    genes: Path
    matrix: Path


@dataclass(frozen=True)
class GSE130973Inspection:
    paths: GSE130973Paths
    file_exists: dict[str, bool]
    file_sizes: dict[str, int | None]
    matrix_shape: tuple[int, int] | None
    matrix_entries: int | None
    gene_count: int | None
    barcode_count: int | None
    first_genes: list[str]
    first_barcodes: list[str]
    orientation: str | None
    mismatches: list[str]


def gse130973_paths(raw_dir: str | Path) -> GSE130973Paths:
    """Return the expected local GEO processed-file paths."""

    root = Path(raw_dir)
    return GSE130973Paths(
        raw_dir=root,
        barcodes=root / GSE130973_REQUIRED_FILES["barcodes"],
        genes=root / GSE130973_REQUIRED_FILES["genes"],
        matrix=root / GSE130973_REQUIRED_FILES["matrix"],
    )


def inspect_gse130973(raw_dir: str | Path, *, preview: int = 5) -> GSE130973Inspection:
    """Inspect local GSE130973 raw files without loading the full matrix."""

    paths = gse130973_paths(raw_dir)
    file_map = {
        "barcodes": paths.barcodes,
        "genes": paths.genes,
        "matrix": paths.matrix,
    }
    file_exists = {name: path.is_file() for name, path in file_map.items()}
    file_sizes = {name: path.stat().st_size if path.is_file() else None for name, path in file_map.items()}

    first_genes: list[str] = []
    first_barcodes: list[str] = []
    gene_count: int | None = None
    barcode_count: int | None = None
    matrix_shape: tuple[int, int] | None = None
    matrix_entries: int | None = None
    mismatches: list[str] = []

    if paths.genes.is_file():
        genes = read_gse130973_genes(paths.genes)
        gene_count = len(genes)
        first_genes = genes[:preview]
    if paths.barcodes.is_file():
        barcodes = read_gse130973_barcodes(paths.barcodes)
        barcode_count = len(barcodes)
        first_barcodes = barcodes[:preview]
    if paths.matrix.is_file():
        rows, cols, entries = read_matrix_market_shape(paths.matrix)
        matrix_shape = (rows, cols)
        matrix_entries = entries

    orientation = _infer_orientation(matrix_shape, gene_count, barcode_count)
    if matrix_shape is not None and gene_count is not None and barcode_count is not None and orientation is None:
        mismatches.append(
            "matrix dimensions do not match genes/barcodes in either genes x cells or cells x genes orientation"
        )
    if gene_count == 0:
        mismatches.append("gene file has no rows")
    if barcode_count == 0:
        mismatches.append("barcode file has no rows")

    return GSE130973Inspection(
        paths=paths,
        file_exists=file_exists,
        file_sizes=file_sizes,
        matrix_shape=matrix_shape,
        matrix_entries=matrix_entries,
        gene_count=gene_count,
        barcode_count=barcode_count,
        first_genes=first_genes,
        first_barcodes=first_barcodes,
        orientation=orientation,
        mismatches=mismatches,
    )


def load_gse130973(
    raw_dir: str | Path,
    *,
    max_cells: int = 5000,
    max_genes: int = 2000,
    seed: int = 20260706,
) -> SingleCellDataset:
    """Load a deterministic cells x genes smoke matrix from local GSE130973 files."""

    paths = gse130973_paths(raw_dir)
    _require_files(paths)
    genes = read_gse130973_genes(paths.genes)
    barcodes = read_gse130973_barcodes(paths.barcodes)
    matrix_shape = read_matrix_market_shape(paths.matrix)[:2]
    orientation = _infer_orientation(matrix_shape, len(genes), len(barcodes))
    if orientation is None:
        raise ValueError(
            "GSE130973 matrix shape does not match gene/barcode counts; "
            f"matrix={matrix_shape}, genes={len(genes)}, barcodes={len(barcodes)}"
        )

    cell_indices = _deterministic_indices(len(barcodes), max_cells, seed=seed)
    gene_indices = _deterministic_indices(len(genes), max_genes, seed=seed + 1)
    expression = _read_subsampled_matrix(
        paths.matrix,
        orientation=orientation,
        cell_indices=cell_indices,
        gene_indices=gene_indices,
    )
    selected_barcodes = [barcodes[idx] for idx in cell_indices]
    selected_genes = [genes[idx] for idx in gene_indices]
    obs = [
        {
            "cell_id": cell_id,
            "perturbation": "observational_unlabeled",
            "timepoint": "not_available",
            "cell_system": "skin_single_cell_unfiltered",
            "state_label": "unknown",
            "age_label": "unknown",
        }
        for cell_id in selected_barcodes
    ]
    return SingleCellDataset(
        expression=expression,
        obs=obs,
        var_names=selected_genes,
        source_path=str(paths.raw_dir),
        file_format="gse130973_mtx",
    )


def save_gse130973_smoke_npz(
    raw_dir: str | Path,
    out: str | Path,
    *,
    max_cells: int = 5000,
    max_genes: int = 2000,
    seed: int = 20260706,
) -> SingleCellDataset:
    """Prepare a small project-compatible NPZ from local GSE130973 raw files."""

    dataset = load_gse130973(raw_dir, max_cells=max_cells, max_genes=max_genes, seed=seed)
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    cell_ids = np.asarray([str(row["cell_id"]) for row in dataset.obs])
    state_labels = np.asarray([str(row["state_label"]) for row in dataset.obs])
    age_labels = np.asarray([str(row["age_label"]) for row in dataset.obs])
    perturbations = np.asarray([str(row["perturbation"]) for row in dataset.obs])
    timepoints = np.asarray([str(row["timepoint"]) for row in dataset.obs])
    cell_systems = np.asarray([str(row["cell_system"]) for row in dataset.obs])
    note = (
        "Real public skin aging single-cell smoke artifact. The three processed GEO files do not include "
        "sample age or donor metadata here, so state and age labels are set to unknown. "
        "No fibroblast-only filtering or biological interpretation is claimed."
    )
    np.savez_compressed(
        output,
        expression=np.asarray(dataset.expression, dtype=np.float32),
        gene_names=np.asarray(dataset.var_names),
        cell_ids=cell_ids,
        perturbation=perturbations,
        timepoint=timepoints,
        cell_system=cell_systems,
        state_label=state_labels,
        age_label=age_labels,
        dataset_id=np.asarray(GSE130973_DATASET_ID),
        source=np.asarray(GSE130973_SOURCE),
        is_real_data=np.asarray(True),
        note=np.asarray(note),
    )
    return dataset


def read_gse130973_genes(path: str | Path) -> list[str]:
    """Read GEO genes/features, preferring the second column when present."""

    genes: list[str] = []
    for fields in _read_gzip_tsv(path):
        if not fields:
            continue
        gene = fields[1].strip() if len(fields) > 1 and fields[1].strip() else fields[0].strip()
        if gene:
            genes.append(gene)
    return _make_unique_names(genes)


def read_gse130973_barcodes(path: str | Path) -> list[str]:
    """Read GEO barcode identifiers from the first TSV column."""

    return [fields[0].strip() for fields in _read_gzip_tsv(path) if fields and fields[0].strip()]


def read_matrix_market_shape(path: str | Path) -> tuple[int, int, int]:
    """Return Matrix Market coordinate dimensions without materializing data."""

    with gzip.open(path, "rt", encoding="utf-8") as handle:
        header = handle.readline().strip().lower()
        if not header.startswith("%%matrixmarket") or "coordinate" not in header:
            raise ValueError(f"{path} is not a Matrix Market coordinate file")
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("%"):
                continue
            parts = stripped.split()
            if len(parts) < 3:
                raise ValueError(f"{path} has an invalid Matrix Market dimensions line: {stripped!r}")
            return int(parts[0]), int(parts[1]), int(parts[2])
    raise ValueError(f"{path} is missing a Matrix Market dimensions line")


def _read_subsampled_matrix(
    path: Path,
    *,
    orientation: str,
    cell_indices: list[int],
    gene_indices: list[int],
) -> np.ndarray:
    cell_lookup = {raw_idx: out_idx for out_idx, raw_idx in enumerate(cell_indices)}
    gene_lookup = {raw_idx: out_idx for out_idx, raw_idx in enumerate(gene_indices)}
    expression = np.zeros((len(cell_indices), len(gene_indices)), dtype=np.float32)
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        _skip_matrix_market_header(handle)
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) < 3:
                continue
            row_idx = int(parts[0]) - 1
            col_idx = int(parts[1]) - 1
            value = float(parts[2])
            if orientation == "genes_x_cells":
                gene_raw_idx, cell_raw_idx = row_idx, col_idx
            else:
                cell_raw_idx, gene_raw_idx = row_idx, col_idx
            if cell_raw_idx in cell_lookup and gene_raw_idx in gene_lookup:
                expression[cell_lookup[cell_raw_idx], gene_lookup[gene_raw_idx]] += value
    return expression


def _skip_matrix_market_header(lines: Iterable[str]) -> None:
    iterator = iter(lines)
    header = next(iterator, "").strip().lower()
    if not header.startswith("%%matrixmarket"):
        raise ValueError("matrix file is missing Matrix Market header")
    for line in iterator:
        stripped = line.strip()
        if stripped and not stripped.startswith("%"):
            return


def _read_gzip_tsv(path: str | Path) -> Iterable[list[str]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.rstrip("\n\r")
            if stripped:
                yield stripped.split("\t")


def _require_files(paths: GSE130973Paths) -> None:
    missing = [
        str(path)
        for path in (paths.barcodes, paths.genes, paths.matrix)
        if not path.is_file()
    ]
    if missing:
        raise FileNotFoundError("missing required GSE130973 raw files: " + ", ".join(missing))


def _infer_orientation(
    matrix_shape: tuple[int, int] | None,
    gene_count: int | None,
    barcode_count: int | None,
) -> str | None:
    if matrix_shape is None or gene_count is None or barcode_count is None:
        return None
    rows, cols = matrix_shape
    if rows == gene_count and cols == barcode_count:
        return "genes_x_cells"
    if rows == barcode_count and cols == gene_count:
        return "cells_x_genes"
    return None


def _deterministic_indices(count: int, maximum: int, *, seed: int) -> list[int]:
    if count <= 0:
        raise ValueError("cannot sample from an empty axis")
    if maximum <= 0:
        raise ValueError("max cells/genes must be positive")
    if count <= maximum:
        return list(range(count))
    rng = np.random.default_rng(seed)
    return sorted(int(idx) for idx in rng.choice(count, size=maximum, replace=False))


def _make_unique_names(names: list[str]) -> list[str]:
    counts: dict[str, int] = {}
    unique: list[str] = []
    for name in names:
        count = counts.get(name, 0)
        if count == 0:
            unique.append(name)
        else:
            unique.append(f"{name}__dup{count + 1}")
        counts[name] = count + 1
    return unique
