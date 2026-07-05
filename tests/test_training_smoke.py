from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hycell.config import load_config
from hycell.gene_sets import gene_sets_from_config, score_gene_sets, write_score_rows
from hycell.toy_data import generate_toy_cells
from hycell.training import evaluate_toy_jepa, train_toy_jepa


def test_jepa_config_loads() -> None:
    config = load_config("configs/jepa_toy.yaml")

    assert config["scores_path"] == "outputs/toy_data/gene_set_scores.csv"
    assert config["bio_state_embedding_dim"] > 0


def test_train_local_yaml_config_loads() -> None:
    config = load_config("configs/train_local.yaml")

    assert config["encoder_checkpoint"] == "outputs/checkpoints/best_encoder.pt"
    assert config["jepa_checkpoint"] == "outputs/checkpoints/best_jepa.pt"
    assert config["auto_prepare_toy_scores"] is True


def test_train_and_evaluate_smoke() -> None:
    config = _smoke_config("outputs/test_tmp/jepa_smoke")

    train_result = train_toy_jepa(config)
    eval_metrics = evaluate_toy_jepa(config)

    assert train_result["metrics"]["n_transitions"] == 8
    assert train_result["metrics"]["train_mse"] >= 0.0
    assert eval_metrics["mse"] >= 0.0
    assert Path(train_result["model_path"]).exists()

    metrics_path = Path(eval_metrics["metrics_path"])
    loaded = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert loaded["data_status"] == "toy_engineering_validation_only"


def test_training_is_deterministic_for_same_config() -> None:
    first_config = _smoke_config("outputs/test_tmp/jepa_deterministic_a")
    second_config = dict(first_config)
    second_config["output_dir"] = "outputs/test_tmp/jepa_deterministic_b"

    first = train_toy_jepa(first_config)["metrics"]
    second = train_toy_jepa(second_config)["metrics"]

    assert first["train_mse"] == second["train_mse"]
    assert first["eval_mse"] == second["eval_mse"]


def test_train_encoder_writes_local_artifacts() -> None:
    config = _smoke_config("outputs/test_tmp/jepa_encoder_artifacts")
    config["encoder_checkpoint"] = "outputs/test_tmp/jepa_encoder_artifacts/best_encoder.pt"
    config["embeddings_path"] = "outputs/test_tmp/jepa_encoder_artifacts/embeddings.npy"
    config["metrics_path"] = "outputs/test_tmp/jepa_encoder_artifacts/metrics.json"

    from hycell.training import train_toy_encoder

    result = train_toy_encoder(config)

    assert Path(result["encoder_checkpoint"]).exists()
    assert Path(result["embeddings_path"]).exists()
    assert Path(result["metrics_path"]).exists()


def test_train_and_evaluate_cli_smoke() -> None:
    config = _smoke_config("outputs/test_tmp/jepa_cli_smoke")
    config_path = Path("outputs/test_tmp/jepa_cli_config.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    train = subprocess.run(
        [sys.executable, "scripts/train_jepa.py", "--config", str(config_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    evaluate = subprocess.run(
        [sys.executable, "scripts/evaluate_jepa.py", "--config", str(config_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Trained toy JEPA transition core" in train.stdout
    assert "Evaluated toy JEPA transition core" in evaluate.stdout


def _smoke_config(output_dir: str) -> dict:
    toy_config = load_config("configs/toy_data.yaml")
    score_config = load_config("configs/gene_sets.yaml")
    rows = generate_toy_cells(toy_config)
    scored = score_gene_sets(rows, gene_sets_from_config(score_config))
    score_path = Path(output_dir) / "gene_set_scores.csv"
    write_score_rows(scored, score_path)

    config = dict(load_config("configs/jepa_toy.yaml"))
    config["scores_path"] = str(score_path)
    config["output_dir"] = output_dir
    return config
