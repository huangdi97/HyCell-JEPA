"""Package small HyCell-JEPA cloud result artifacts."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKAGE_CANDIDATES = [
    "configs/train_cloud_4090.yaml",
    "outputs/reports/metrics.json",
    "outputs/reports/jepa_metrics.json",
    "outputs/reports/benchmark_metrics.json",
    "outputs/reports/benchmark_report.md",
    "outputs/reports/planner_report.md",
    "outputs/reports/top_k_actions.json",
    "docs/progress_log.md",
    "docs/benchmark_report.md",
    "docs/model_card.md",
    "docs/data_card.md",
]

EXCLUDED_SUFFIXES = {".pt", ".pth", ".ckpt", ".npy", ".npz", ".h5ad"}
EXCLUDED_PREFIXES = ("data/raw/", "data/processed/", "outputs/checkpoints/")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package small HyCell-JEPA cloud result artifacts.")
    parser.add_argument("--out", default="outputs/hycell_cloud_results.zip", help="Output zip path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    packaged: list[str] = []
    warnings: list[str] = []
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for candidate in PACKAGE_CANDIDATES:
            path = Path(candidate)
            if not path.exists():
                message = f"missing optional artifact: {candidate}"
                warnings.append(message)
                print(f"WARNING: {message}")
                continue
            if _is_excluded(path):
                message = f"skipped excluded artifact: {candidate}"
                warnings.append(message)
                print(f"WARNING: {message}")
                continue
            archive.write(path, arcname=candidate)
            packaged.append(candidate)

        manifest = _manifest(packaged, warnings)
        archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    print(f"Packaged {len(packaged)} files into {out_path}")
    return 0


def _is_excluded(path: Path) -> bool:
    normalized = path.as_posix()
    return path.suffix in EXCLUDED_SUFFIXES or any(normalized.startswith(prefix) for prefix in EXCLUDED_PREFIXES)


def _manifest(packaged: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "git_commit": _run_text(["git", "rev-parse", "--short", "HEAD"]),
        "python_version": sys.version,
        "platform": platform.platform(),
        "cuda_available": _cuda_available(),
        "packaged_files": packaged,
        "warnings": warnings,
        "exclusions": {
            "prefixes": list(EXCLUDED_PREFIXES),
            "suffixes": sorted(EXCLUDED_SUFFIXES),
        },
        "data_status": "toy_engineering_validation_only_not_biological_validation",
    }


def _run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except Exception:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _cuda_available() -> bool | str:
    try:
        import torch
    except Exception:
        return "torch_unavailable"
    return bool(torch.cuda.is_available())


if __name__ == "__main__":
    raise SystemExit(main())
