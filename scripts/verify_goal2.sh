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

required_files=(
  "configs/jepa_toy.yaml"
  "configs/train_local.yaml"
  "scripts/train_encoder.py"
  "scripts/train_jepa.py"
  "scripts/evaluate_jepa.py"
  "src/hycell/datasets.py"
  "src/hycell/encoders.py"
  "src/hycell/jepa.py"
  "src/hycell/training.py"
  "tests/test_encoders.py"
  "tests/test_jepa.py"
  "tests/test_training_smoke.py"
)

for path in "${required_files[@]}"; do
  test -f "$path"
done

$PYTHON_BIN scripts/make_toy_data.py --config configs/toy_data.yaml
$PYTHON_BIN scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
$PYTHON_BIN scripts/train_encoder.py --config configs/train_local.yaml
$PYTHON_BIN scripts/train_jepa.py --config configs/train_local.yaml
$PYTHON_BIN scripts/train_jepa.py --config configs/jepa_toy.yaml
$PYTHON_BIN scripts/evaluate_jepa.py --config configs/jepa_toy.yaml

test -f outputs/checkpoints/best_encoder.pt
test -f outputs/checkpoints/best_jepa.pt
test -f outputs/embeddings/embeddings.npy
test -f outputs/reports/metrics.json
test -f outputs/reports/jepa_metrics.json

git check-ignore -q outputs/checkpoints/best_encoder.pt
git check-ignore -q outputs/checkpoints/best_jepa.pt
git check-ignore -q outputs/embeddings/embeddings.npy
git check-ignore -q outputs/reports/metrics.json
git check-ignore -q outputs/reports/jepa_metrics.json

$PYTHON_BIN -m pytest tests/test_encoders.py tests/test_jepa.py tests/test_training_smoke.py

echo "Goal 2 acceptance passed."
