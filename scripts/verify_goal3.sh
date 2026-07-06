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
  "configs/benchmark_toy.yaml"
  "configs/demo.yaml"
  "scripts/benchmark_toy.py"
  "scripts/eval_benchmark.py"
  "scripts/run_planner.py"
  "scripts/demo_app.py"
  "src/hycell/hdf_adapter.py"
  "src/hycell/verifier.py"
  "src/hycell/planner.py"
  "src/hycell/benchmark.py"
  "src/hycell/demo/app.py"
  "tests/test_hdf_adapter.py"
  "tests/test_verifier.py"
  "tests/test_planner.py"
  "tests/test_benchmark_smoke.py"
)

for path in "${required_files[@]}"; do
  test -f "$path"
done

$PYTHON_BIN scripts/make_toy_data.py --config configs/toy_data.yaml
$PYTHON_BIN scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
$PYTHON_BIN scripts/train_encoder.py --config configs/train_local.yaml
$PYTHON_BIN scripts/train_jepa.py --config configs/train_local.yaml
$PYTHON_BIN scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
$PYTHON_BIN scripts/eval_benchmark.py --checkpoint outputs/checkpoints/best_jepa.pt
$PYTHON_BIN scripts/run_planner.py --checkpoint outputs/checkpoints/best_jepa.pt --state aged_hdf --target rejuvenated_repair
$PYTHON_BIN -m compileall scripts src
$PYTHON_BIN -c "import streamlit; import hycell.demo.app; print(streamlit.__version__)"

test -f outputs/benchmark_toy/benchmark_report.json
test -f outputs/reports/benchmark_report.md
test -f outputs/reports/benchmark_metrics.json
test -f outputs/reports/planner_report.md
test -f outputs/reports/top_k_actions.json

git check-ignore -q outputs/benchmark_toy/benchmark_report.json
git check-ignore -q outputs/reports/benchmark_report.md
git check-ignore -q outputs/reports/benchmark_metrics.json
git check-ignore -q outputs/reports/planner_report.md
git check-ignore -q outputs/reports/top_k_actions.json

$PYTHON_BIN -m pytest tests/test_hdf_adapter.py tests/test_verifier.py tests/test_planner.py tests/test_benchmark_smoke.py

echo "Goal 3 acceptance passed."
