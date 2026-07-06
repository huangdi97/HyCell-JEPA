from __future__ import annotations

import builtins
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from hycell.data_loaders import load_csv_dataset, load_h5ad_dataset, load_npz_dataset


def test_load_csv_dataset_with_metadata_and_gene_columns() -> None:
    path = Path("outputs/test_tmp/real_loader_cells.csv")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "cell_id,perturbation,timepoint,cell_system,GENE_A,GENE_B",
                "c1,vehicle,t0,hdf,1.0,2.0",
                "c2,senescence,t1,hdf,3.0,4.0",
            ]
        ),
        encoding="utf-8",
    )

    dataset = load_csv_dataset(path)

    assert dataset.file_format == "csv"
    assert dataset.expression.shape == (2, 2)
    assert dataset.var_names == ["GENE_A", "GENE_B"]
    assert dataset.obs[0]["cell_id"] == "c1"
    assert dataset.obs[1]["perturbation"] == "senescence"


def test_load_npz_dataset_normalizes_alias_metadata() -> None:
    path = Path("outputs/test_tmp/real_loader_cells.npz")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        X=np.asarray([[1.0, 2.0], [3.0, 4.0]]),
        var_names=np.asarray(["GENE_A", "GENE_B"]),
        cell_ids=np.asarray(["c1", "c2"]),
        actions=np.asarray(["vehicle", "repair"]),
        timepoints=np.asarray(["t0", "t1"]),
        cell_type=np.asarray(["hdf", "hdf"]),
    )

    dataset = load_npz_dataset(path)

    assert dataset.file_format == "npz"
    assert dataset.expression.shape == (2, 2)
    assert dataset.obs[0]["cell_id"] == "c1"
    assert dataset.obs[0]["perturbation"] == "vehicle"
    assert dataset.obs[0]["actions"] == "vehicle"
    assert dataset.obs[1]["cell_system"] == "hdf"


def test_h5ad_loader_has_clear_optional_dependency_message(monkeypatch: pytest.MonkeyPatch) -> None:
    original_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "anndata":
            raise ImportError("blocked for test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match="requires optional dependency 'anndata'"):
        load_h5ad_dataset("outputs/test_tmp/real_loader_cells.h5ad")


def test_validate_dataset_cli_writes_report_for_tiny_csv() -> None:
    input_path = Path("outputs/test_tmp/real_loader_cli_cells.csv")
    report_path = Path("outputs/test_tmp/real_loader_cli_report.json")
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(
        "\n".join(
            [
                "cell_id,perturbation,timepoint,cell_system,GENE_A",
                "c1,vehicle,t0,hdf,1.0",
                "c2,repair,t1,hdf,2.0",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/validate_dataset.py",
            "--input",
            str(input_path),
            "--output",
            str(report_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "Validated 2 cells x 1 genes" in result.stdout
    assert report["validation"]["valid"] is True
    assert report["mapped_metadata_preview"][1]["canonical_action"] == "regeneration"
