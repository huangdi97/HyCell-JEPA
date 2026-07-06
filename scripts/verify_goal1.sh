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
  "pyproject.toml"
  "requirements.txt"
  "configs/toy_data.yaml"
  "configs/gene_sets.yaml"
  "scripts/make_toy_data.py"
  "scripts/score_gene_sets.py"
  "scripts/build_evidence_graph.py"
  "src/hycell/toy_data.py"
  "src/hycell/gene_sets.py"
  "src/hycell/evidence_graph.py"
  "tests/test_toy_data.py"
  "tests/test_gene_sets.py"
  "tests/test_evidence_graph.py"
)

for path in "${required_files[@]}"; do
  test -f "$path"
done

$PYTHON_BIN scripts/make_toy_data.py --config configs/toy_data.yaml
test -f outputs/toy_data/toy_cells.csv

$PYTHON_BIN scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
test -f outputs/toy_data/gene_set_scores.csv

$PYTHON_BIN scripts/build_evidence_graph.py --scores outputs/toy_data/gene_set_scores.csv
test -f outputs/toy_data/evidence_graph.json

$PYTHON_BIN scripts/make_toy_data.py --n_cells 32 --n_genes 16 --out data/processed/toy_cells_contract_smoke.npz
test -f data/processed/toy_cells_contract_smoke.npz

git check-ignore -q outputs/toy_data/toy_cells.csv
git check-ignore -q outputs/toy_data/gene_set_scores.csv
git check-ignore -q outputs/toy_data/evidence_graph.json
git check-ignore -q data/processed/toy_cells_contract_smoke.npz

$PYTHON_BIN -m pytest tests/test_toy_data.py tests/test_gene_sets.py tests/test_evidence_graph.py

echo "Goal 1 acceptance passed."
