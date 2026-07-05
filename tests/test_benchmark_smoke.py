from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from hycell.benchmark import run_toy_benchmark
from hycell.config import load_config
from hycell.gene_sets import gene_sets_from_config, score_gene_sets, write_score_rows
from hycell.toy_data import generate_toy_cells
from hycell.training import train_toy_jepa


def test_benchmark_writes_report() -> None:
    config = dict(load_config("configs/benchmark_toy.yaml"))
    config["output_dir"] = "outputs/test_tmp/benchmark"
    config["scores_path"] = _write_scores("outputs/test_tmp/benchmark_scores.csv")
    train_config = dict(load_config("configs/jepa_toy.yaml"))
    train_config["output_dir"] = "outputs/test_tmp/benchmark_model"
    train_config["scores_path"] = config["scores_path"]
    train_toy_jepa(train_config)
    config["model_path"] = "outputs/test_tmp/benchmark_model/toy_jepa_model.npz"

    report = run_toy_benchmark(config)

    assert report["n_transitions"] == 8
    assert report["transition_mse"] >= 0.0
    assert Path(report["report_path"]).exists()
    assert report["planner"]["actions"]


def test_demo_app_imports_cleanly() -> None:
    spec = importlib.util.spec_from_file_location("demo_app", "scripts/demo_app.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "load_demo_state")
    assert hasattr(module, "render_app")


def test_package_demo_app_imports_cleanly() -> None:
    import hycell.demo.app as app

    assert hasattr(app, "render_app")
    assert hasattr(app, "predict_for_selection")


def test_eval_benchmark_cli_writes_compat_reports() -> None:
    score_path = _write_scores("outputs/test_tmp/eval_benchmark_scores.csv")
    train_config = dict(load_config("configs/jepa_toy.yaml"))
    train_config["scores_path"] = score_path
    train_config["output_dir"] = "outputs/test_tmp/eval_benchmark_model"
    train_config["jepa_checkpoint"] = "outputs/test_tmp/eval_benchmark_model/best_jepa.pt"
    train_toy_jepa(train_config)

    config = dict(load_config("configs/benchmark_toy.yaml"))
    config["scores_path"] = score_path
    config_path = Path("outputs/test_tmp/eval_benchmark_config.json")
    config_path.write_text(json.dumps(config), encoding="utf-8")
    report_dir = "outputs/test_tmp/eval_benchmark_reports"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/eval_benchmark.py",
            "--checkpoint",
            train_config["jepa_checkpoint"],
            "--config",
            str(config_path),
            "--report-dir",
            report_dir,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Toy benchmark complete" in result.stdout
    assert Path(report_dir, "benchmark_report.md").exists()
    assert Path(report_dir, "benchmark_metrics.json").exists()


def test_run_planner_cli_writes_top_k_reports() -> None:
    score_path = _write_scores("outputs/test_tmp/run_planner_scores.csv")
    train_config = dict(load_config("configs/jepa_toy.yaml"))
    train_config["scores_path"] = score_path
    train_config["output_dir"] = "outputs/test_tmp/run_planner_model"
    train_config["jepa_checkpoint"] = "outputs/test_tmp/run_planner_model/best_jepa.pt"
    train_toy_jepa(train_config)

    config = dict(load_config("configs/benchmark_toy.yaml"))
    config["scores_path"] = score_path
    config_path = Path("outputs/test_tmp/run_planner_config.json")
    config_path.write_text(json.dumps(config), encoding="utf-8")
    report_dir = "outputs/test_tmp/run_planner_reports"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_planner.py",
            "--checkpoint",
            train_config["jepa_checkpoint"],
            "--state",
            "aged_hdf",
            "--target",
            "rejuvenated_repair",
            "--config",
            str(config_path),
            "--report-dir",
            report_dir,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Top-K toy action sequences" in result.stdout
    assert Path(report_dir, "planner_report.md").exists()
    assert Path(report_dir, "top_k_actions.json").exists()


def _write_scores(path: str) -> str:
    toy_config = load_config("configs/toy_data.yaml")
    score_config = load_config("configs/gene_sets.yaml")
    rows = generate_toy_cells(toy_config)
    scored = score_gene_sets(rows, gene_sets_from_config(score_config))
    write_score_rows(scored, path)
    return path
