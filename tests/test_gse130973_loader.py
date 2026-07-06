from __future__ import annotations

import gzip
import subprocess
import sys
from pathlib import Path

import numpy as np

from hycell.real_datasets import (
    inspect_gse130973,
    load_gse130973,
    read_gse130973_genes,
    save_gse130973_smoke_npz,
)


def test_gse130973_loader_reads_matrix_market_as_cells_by_genes() -> None:
    raw_dir = _write_tiny_gse130973_fixture(Path("outputs/test_tmp/gse130973_loader_fixture"))

    dataset = load_gse130973(raw_dir, max_cells=10, max_genes=10, seed=7)

    assert dataset.expression.shape == (2, 3)
    assert dataset.var_names == ["GENE_A", "GENE_B", "GENE_C"]
    assert [row["cell_id"] for row in dataset.obs] == ["cell_a", "cell_b"]
    assert dataset.expression.tolist() == [[1.0, 0.0, 3.0], [0.0, 2.0, 4.0]]
    assert {row["state_label"] for row in dataset.obs} == {"unknown"}


def test_gse130973_prepare_saves_required_npz_keys() -> None:
    root = Path("outputs/test_tmp/gse130973_prepare_fixture")
    raw_dir = _write_tiny_gse130973_fixture(root)
    out = root / "processed" / "gse130973_smoke.npz"

    save_gse130973_smoke_npz(raw_dir, out, max_cells=1, max_genes=2, seed=11)

    data = np.load(out, allow_pickle=False)
    assert data["expression"].shape == (1, 2)
    for key in (
        "expression",
        "gene_names",
        "cell_ids",
        "dataset_id",
        "source",
        "is_real_data",
        "note",
        "state_label",
        "age_label",
    ):
        assert key in data.files
    assert str(data["dataset_id"]) == "gse130973"
    assert bool(data["is_real_data"]) is True
    assert set(data["state_label"].tolist()) == {"unknown"}


def test_gse130973_inspect_reports_shape_and_orientation() -> None:
    raw_dir = _write_tiny_gse130973_fixture(Path("outputs/test_tmp/gse130973_inspect_fixture"))

    inspection = inspect_gse130973(raw_dir)

    assert inspection.matrix_shape == (3, 2)
    assert inspection.gene_count == 3
    assert inspection.barcode_count == 2
    assert inspection.orientation == "genes_x_cells"
    assert inspection.mismatches == []


def test_gse130973_gene_reader_disambiguates_duplicate_symbols() -> None:
    root = Path("outputs/test_tmp/gse130973_duplicate_genes")
    root.mkdir(parents=True, exist_ok=True)
    path = root / "GSE130973_genes_filtered.tsv.gz"
    _write_gzip(path, "ENSG1\tDCAF8\nENSG2\tDCAF8\nENSG3\tGENE_C\n")

    assert read_gse130973_genes(path) == ["DCAF8", "DCAF8__dup2", "GENE_C"]


def test_prepare_gse130973_cli_writes_fixture_npz() -> None:
    root = Path("outputs/test_tmp/gse130973_cli_fixture")
    raw_dir = _write_tiny_gse130973_fixture(root)
    out = root / "prepared.npz"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_gse130973.py",
            "--raw-dir",
            str(raw_dir),
            "--out",
            str(out),
            "--max-cells",
            "2",
            "--max-genes",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert out.is_file()
    assert "Prepared GSE130973 smoke NPZ" in result.stdout
    assert "state_label and age_label are set to unknown" in result.stdout


def _write_tiny_gse130973_fixture(root: Path) -> Path:
    raw_dir = root / "gse130973"
    raw_dir.mkdir(parents=True, exist_ok=True)
    _write_gzip(
        raw_dir / "GSE130973_genes_filtered.tsv.gz",
        "ENSG000001\tGENE_A\nENSG000002\tGENE_B\nENSG000003\tGENE_C\n",
    )
    _write_gzip(raw_dir / "GSE130973_barcodes_filtered.tsv.gz", "cell_a\ncell_b\n")
    _write_gzip(
        raw_dir / "GSE130973_matrix_filtered.mtx.gz",
        "\n".join(
            [
                "%%MatrixMarket matrix coordinate real general",
                "% tiny genes x cells fixture",
                "3 2 4",
                "1 1 1.0",
                "2 2 2.0",
                "3 1 3.0",
                "3 2 4.0",
                "",
            ]
        ),
    )
    return raw_dir


def _write_gzip(path: Path, text: str) -> None:
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(text)
