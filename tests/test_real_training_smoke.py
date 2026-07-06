from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from hycell.real_training import evaluate_real_matrix, train_real_smoke_encoder


def test_train_real_smoke_creates_outputs_for_tiny_npz() -> None:
    root = Path("outputs/test_tmp/real_training_smoke")
    input_path = _write_tiny_real_npz(root / "tiny_real.npz")
    output_dir = root / "train"
    reports_dir = root / "reports"

    result = train_real_smoke_encoder(
        {
            "input": str(input_path),
            "output_dir": str(output_dir),
            "reports_dir": str(reports_dir),
            "max_cells": 3,
            "max_genes": 4,
            "latent_dim": 2,
            "batch_size": 2,
            "epochs": 1,
            "seed": 17,
        }
    )

    embeddings = np.load(result["embeddings_path"])
    metrics = json.loads(result["metrics_path"].read_text(encoding="utf-8"))
    assert embeddings.shape == (3, 2)
    assert metrics["data_status"] == "real_matrix_encoder_smoke_only_not_biological_validation"
    assert metrics["dataset_id"] == "gse130973"
    assert result["report_path"].is_file()


def test_eval_real_smoke_creates_summary_outputs_for_tiny_npz() -> None:
    root = Path("outputs/test_tmp/real_eval_smoke")
    input_path = _write_tiny_real_npz(root / "tiny_real.npz")

    summary = evaluate_real_matrix(input_path, output_dir=root / "reports")

    assert summary["n_cells"] == 3
    assert summary["n_genes"] == 4
    assert 0.0 <= summary["zero_fraction"] <= 1.0
    assert len(summary["top_variable_genes"]) == 4
    assert Path(summary["json_path"]).is_file()
    assert Path(summary["report_path"]).is_file()


def test_train_real_smoke_cli_reports_missing_input_clearly() -> None:
    config = Path("outputs/test_tmp/real_training_missing/config.yaml")
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "\n".join(
            [
                "input: outputs/test_tmp/real_training_missing/missing.npz",
                "output_dir: outputs/test_tmp/real_training_missing/out",
                "max_cells: 3",
                "max_genes: 4",
                "latent_dim: 2",
                "seed: 1",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "scripts/train_real_smoke.py", "--config", str(config)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "Run scripts/prepare_gse130973.py first" in result.stderr


def test_eval_real_smoke_cli_writes_default_reports() -> None:
    root = Path("outputs/test_tmp/real_eval_cli")
    input_path = _write_tiny_real_npz(root / "tiny_real.npz")

    result = subprocess.run(
        [sys.executable, "scripts/eval_real_smoke.py", "--input", str(input_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Evaluated real matrix: 3 cells x 4 genes" in result.stdout
    assert Path("outputs/reports/gse130973_real_matrix_summary.json").is_file()
    assert Path("outputs/reports/gse130973_real_matrix_summary.md").is_file()


def _write_tiny_real_npz(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        expression=np.asarray(
            [
                [0.0, 1.0, 0.0, 3.0],
                [2.0, 0.0, 0.0, 4.0],
                [1.0, 1.0, 5.0, 0.0],
            ],
            dtype=np.float32,
        ),
        gene_names=np.asarray(["GENE_A", "GENE_B", "GENE_C", "GENE_D"]),
        cell_ids=np.asarray(["cell_a", "cell_b", "cell_c"]),
        perturbation=np.asarray(["observational_unlabeled"] * 3),
        timepoint=np.asarray(["not_available"] * 3),
        cell_system=np.asarray(["skin_single_cell_unfiltered"] * 3),
        state_label=np.asarray(["unknown"] * 3),
        age_label=np.asarray(["unknown"] * 3),
        dataset_id=np.asarray("gse130973"),
        source=np.asarray("tiny synthetic fixture"),
        is_real_data=np.asarray(True),
        note=np.asarray("fixture only"),
    )
    return path
