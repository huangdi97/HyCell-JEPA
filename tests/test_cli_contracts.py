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
    for script_name in ("verify_goal1.sh", "verify_goal2.sh", "verify_goal3.sh", "verify_goal4.sh"):
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
