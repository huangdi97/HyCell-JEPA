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

test -f configs/train_gse130973_smoke.yaml
test -f scripts/train_real_smoke.py
test -f scripts/eval_real_smoke.py
test -f docs/gse130973_smoke_report.md
test -f src/hycell/real_training.py
test -f tests/test_real_training_smoke.py

$PYTHON_BIN -m pytest

processed="data/processed/gse130973/gse130973_smoke.npz"
if [[ -f "$processed" ]]; then
  echo "Found processed GSE130973 smoke NPZ; running real-data evaluation and training smoke."
  $PYTHON_BIN scripts/eval_real_smoke.py --input "$processed"
  $PYTHON_BIN scripts/train_real_smoke.py --config configs/train_gse130973_smoke.yaml
  test -f outputs/gse130973_smoke/real_smoke_metrics.json
  test -f outputs/gse130973_smoke/real_smoke_embeddings.npy
  test -f outputs/reports/gse130973_real_smoke_report.md
  test -f outputs/reports/gse130973_real_matrix_summary.json
  test -f outputs/reports/gse130973_real_matrix_summary.md
  git check-ignore -q outputs/gse130973_smoke/real_smoke_metrics.json
  git check-ignore -q outputs/gse130973_smoke/real_smoke_embeddings.npy
  git check-ignore -q outputs/reports/gse130973_real_smoke_report.md
else
  echo "Processed GSE130973 smoke NPZ not found at $processed."
  echo "Create it with: python scripts/prepare_gse130973.py --raw-dir data/raw/gse130973 --out $processed --max-cells 5000 --max-genes 2000"
  echo "Fixture tests still verify real smoke loading, training, evaluation, and missing-input behavior."
fi

echo "Goal 7 real-data training smoke acceptance passed."
