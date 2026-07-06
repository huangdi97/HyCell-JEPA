#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python.exe >/dev/null 2>&1; then
  PYTHON_BIN="python.exe"
elif command -v py.exe >/dev/null 2>&1; then
  PYTHON_BIN="py.exe -3"
else
  echo "No Python executable found. Set PYTHON=/path/to/python and rerun." >&2
  exit 127
fi

test -f configs/train_cloud_4090.yaml
test -f scripts/run_cloud_experiment.sh
test -x scripts/run_cloud_experiment.sh
test -f scripts/package_results.py
test -f docs/cloud_4090_guide.md

$PYTHON_BIN scripts/package_results.py --out outputs/goal5_package_smoke.zip
test -f outputs/goal5_package_smoke.zip
git check-ignore -q outputs/goal5_package_smoke.zip

$PYTHON_BIN -m pytest

echo "Goal 5 acceptance passed."
