from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


def test_inspect_dataset_fails_gracefully_for_missing_input() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/inspect_dataset.py", "--input", "outputs/test_tmp/missing_smoke.csv"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "Dataset not found" in result.stdout
    assert "no download was attempted" in result.stdout


def test_inspect_and_preprocess_tiny_csv_smoke() -> None:
    input_path = Path("outputs/test_tmp/real_smoke_cells.csv")
    inspect_report = Path("outputs/test_tmp/real_smoke_inspection.json")
    preprocessed = Path("outputs/test_tmp/real_smoke_preprocessed.csv")
    preprocess_report = Path("outputs/test_tmp/real_smoke_preprocess_report.json")
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(
        "\n".join(
            [
                "cell_id,perturbation,timepoint,cell_system,GENE_A,GENE_B",
                "c1,vehicle,t0,hdf,1.0,2.0",
                "c2,repair,t1,hdf,3.0,4.0",
            ]
        ),
        encoding="utf-8",
    )

    inspect = subprocess.run(
        [
            sys.executable,
            "scripts/inspect_dataset.py",
            "--input",
            str(input_path),
            "--output",
            str(inspect_report),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    preprocess = subprocess.run(
        [
            sys.executable,
            "scripts/preprocess_data.py",
            "--input",
            str(input_path),
            "--output",
            str(preprocessed),
            "--report",
            str(preprocess_report),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    inspection = json.loads(inspect_report.read_text(encoding="utf-8"))
    report = json.loads(preprocess_report.read_text(encoding="utf-8"))
    with preprocessed.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert "Inspected 2 cells x 2 genes" in inspect.stdout
    assert "Wrote normalized smoke artifact" in preprocess.stdout
    assert inspection["validation"]["valid"] is True
    assert report["status"] == "ok"
    assert rows[1]["original_perturbation"] == "repair"
    assert rows[1]["canonical_action"] == "regeneration"
