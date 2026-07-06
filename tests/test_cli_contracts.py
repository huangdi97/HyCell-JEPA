from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


COMPLETED_GOAL_CLI_FILES = {
    "goal1": [
        "scripts/make_toy_data.py",
        "scripts/score_gene_sets.py",
        "scripts/build_evidence_graph.py",
    ],
    "goal2": [
        "scripts/train_encoder.py",
        "scripts/train_jepa.py",
        "scripts/evaluate_jepa.py",
    ],
    "goal3": [
        "scripts/benchmark_toy.py",
        "scripts/eval_benchmark.py",
        "scripts/run_planner.py",
        "scripts/demo_app.py",
        "src/hycell/demo/app.py",
    ],
    "goal4": [
        "scripts/validate_dataset.py",
        "scripts/inspect_dataset.py",
        "scripts/preprocess_data.py",
    ],
    "goal5": [
        "scripts/package_results.py",
        "scripts/run_cloud_experiment.sh",
    ],
    "goal6": [
        "scripts/inspect_gse130973.py",
        "scripts/prepare_gse130973.py",
    ],
    "goal7": [
        "scripts/eval_real_smoke.py",
        "scripts/train_real_smoke.py",
    ],
}


def test_completed_goal_cli_files_exist() -> None:
    missing = [
        path
        for paths in COMPLETED_GOAL_CLI_FILES.values()
        for path in paths
        if not (ROOT / path).is_file()
    ]
    assert missing == []


def test_acceptance_verifier_scripts_exist_and_use_strict_bash() -> None:
    for script_name in (
        "verify_goal1.sh",
        "verify_goal2.sh",
        "verify_goal3.sh",
        "verify_goal4.sh",
        "verify_goal4_real_smoke.sh",
        "verify_goal5.sh",
        "verify_goal6.sh",
        "verify_goal7.sh",
    ):
        path = ROOT / "scripts" / script_name
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert "set -euo pipefail" in text


def test_validate_dataset_help_runs() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "scripts/validate_dataset.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--input INPUT" in result.stdout


def test_gse130973_cli_help_runs() -> None:
    import subprocess
    import sys

    for script in ("scripts/inspect_gse130973.py", "scripts/prepare_gse130973.py"):
        result = subprocess.run(
            [sys.executable, script, "--help"],
            check=True,
            capture_output=True,
            text=True,
        )

        assert "--raw-dir RAW_DIR" in result.stdout


def test_real_smoke_cli_help_runs() -> None:
    import subprocess
    import sys

    train = subprocess.run(
        [sys.executable, "scripts/train_real_smoke.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    evaluate = subprocess.run(
        [sys.executable, "scripts/eval_real_smoke.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--config CONFIG" in train.stdout
    assert "--input INPUT" in evaluate.stdout
