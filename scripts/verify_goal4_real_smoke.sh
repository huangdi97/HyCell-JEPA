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

test -f scripts/inspect_dataset.py
test -f scripts/preprocess_data.py
test -f scripts/validate_dataset.py
test -f docs/real_data_smoke_test.md
test -f docs/real_data_integration.md

$PYTHON_BIN -m pytest tests/test_real_data_smoke.py tests/test_data_loaders.py tests/test_schema.py
$PYTHON_BIN scripts/make_toy_data.py --config configs/toy_data.yaml
$PYTHON_BIN scripts/validate_dataset.py --help

mkdir -p outputs/test_tmp outputs/real_data_smoke outputs/reports
cat > outputs/test_tmp/goal45_smoke_cells.csv <<'CSV'
cell_id,perturbation,timepoint,cell_system,GENE_A,GENE_B
c1,vehicle,t0,hdf,1.0,2.0
c2,repair,t1,hdf,3.0,4.0
CSV

$PYTHON_BIN scripts/inspect_dataset.py \
  --input outputs/test_tmp/goal45_smoke_cells.csv \
  --output outputs/test_tmp/goal45_inspection.json
test -f outputs/test_tmp/goal45_inspection.json

$PYTHON_BIN scripts/preprocess_data.py \
  --input outputs/test_tmp/goal45_smoke_cells.csv \
  --output outputs/real_data_smoke/goal45_preprocessed_cells.csv \
  --report outputs/real_data_smoke/goal45_preprocess_report.json
test -f outputs/real_data_smoke/goal45_preprocessed_cells.csv
test -f outputs/real_data_smoke/goal45_preprocess_report.json

if $PYTHON_BIN scripts/inspect_dataset.py --input outputs/test_tmp/does_not_exist.csv > outputs/test_tmp/goal45_missing_input.txt 2>&1; then
  echo "inspect_dataset.py unexpectedly succeeded for a missing dataset" >&2
  exit 1
fi
grep -q "Dataset not found" outputs/test_tmp/goal45_missing_input.txt

git check-ignore -q outputs/test_tmp/goal45_smoke_cells.csv
git check-ignore -q outputs/test_tmp/goal45_inspection.json
git check-ignore -q outputs/real_data_smoke/goal45_preprocessed_cells.csv
git check-ignore -q outputs/real_data_smoke/goal45_preprocess_report.json

echo "Goal 4.5 real-data smoke acceptance passed."
