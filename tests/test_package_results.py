from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path


def test_package_results_help_runs() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/package_results.py", "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "--out OUT" in result.stdout


def test_package_results_creates_manifest_without_large_artifacts() -> None:
    out = Path("outputs/test_tmp/package_results_smoke.zip")

    result = subprocess.run(
        [sys.executable, "scripts/package_results.py", "--out", str(out)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Packaged" in result.stdout
    assert out.exists()
    with zipfile.ZipFile(out) as archive:
        names = set(archive.namelist())
        manifest = json.loads(archive.read("manifest.json"))

    assert "manifest.json" in names
    assert "configs/train_cloud_4090.yaml" in names
    assert manifest["data_status"] == "toy_engineering_validation_only_not_biological_validation"
    assert not any(name.startswith("outputs/checkpoints/") for name in names)
    assert not any(Path(name).suffix in {".pt", ".npz", ".npy", ".h5ad"} for name in names)
