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
  "configs/real_data_schema.yaml"
  "scripts/validate_dataset.py"
  "docs/real_data_integration.md"
  "src/hycell/data_loaders.py"
  "src/hycell/schema.py"
  "src/hycell/perturbation_adapter.py"
  "tests/test_data_loaders.py"
  "tests/test_schema.py"
  "tests/test_perturbation_adapter.py"
)

for path in "${required_files[@]}"; do
  test -f "$path"
done

$PYTHON_BIN -c "import hycell; print('hycell import ok')"
$PYTHON_BIN -c "from hycell.config import load_config; print('config import ok')"
$PYTHON_BIN -c "from hycell.data_loaders import load_dataset, load_csv_dataset, load_npz_dataset; from hycell.schema import AnnDataSchemaValidator; from hycell.perturbation_adapter import PerturbationAdapter, HDFAgingMetadataAdapter; print('goal4 imports ok')"

$PYTHON_BIN -m pytest

$PYTHON_BIN scripts/make_toy_data.py --n_cells 64 --n_genes 32 --out data/processed/toy_cells_goal4_smoke.npz
test -f data/processed/toy_cells_goal4_smoke.npz
git check-ignore -q data/processed/toy_cells_goal4_smoke.npz

$PYTHON_BIN scripts/validate_dataset.py --help
test -f scripts/validate_dataset.py
test -f docs/real_data_integration.md

mkdir -p outputs/test_tmp
cat > outputs/test_tmp/goal4_verify_cells.csv <<'CSV'
cell_id,perturbation,timepoint,cell_system,GENE_A,GENE_B
c1,vehicle,t0,hdf,1.0,2.0
c2,repair,t1,hdf,3.0,4.0
CSV

$PYTHON_BIN scripts/validate_dataset.py \
  --input outputs/test_tmp/goal4_verify_cells.csv \
  --output outputs/test_tmp/goal4_verify_report.json
test -f outputs/test_tmp/goal4_verify_report.json
git check-ignore -q outputs/test_tmp/goal4_verify_cells.csv
git check-ignore -q outputs/test_tmp/goal4_verify_report.json

echo "Goal 4 acceptance passed."
