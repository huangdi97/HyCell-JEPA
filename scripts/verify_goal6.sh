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

test -f scripts/prepare_gse130973.py
test -f scripts/inspect_gse130973.py
test -f configs/gse130973_smoke.yaml
test -f docs/datasets_registry.md
test -f docs/gse130973_integration.md
test -f src/hycell/real_datasets.py
test -f tests/test_gse130973_loader.py

$PYTHON_BIN -m pytest
$PYTHON_BIN -m pytest tests/test_gse130973_loader.py

raw_dir="data/raw/gse130973"
barcodes="$raw_dir/GSE130973_barcodes_filtered.tsv.gz"
genes="$raw_dir/GSE130973_genes_filtered.tsv.gz"
matrix="$raw_dir/GSE130973_matrix_filtered.mtx.gz"

if [[ -f "$barcodes" && -f "$genes" && -f "$matrix" ]]; then
  echo "Found local GSE130973 raw files; running real-data smoke prepare path."
  $PYTHON_BIN scripts/inspect_gse130973.py --raw-dir "$raw_dir"
  $PYTHON_BIN scripts/prepare_gse130973.py \
    --raw-dir "$raw_dir" \
    --out data/processed/gse130973/gse130973_smoke.npz \
    --max-cells 5000 \
    --max-genes 2000
  $PYTHON_BIN scripts/validate_dataset.py --input data/processed/gse130973/gse130973_smoke.npz
  git check-ignore -q data/processed/gse130973/gse130973_smoke.npz
else
  echo "Local GSE130973 raw files not found; skipping real-data prepare path."
  echo "Fixture tests still verify Matrix Market loading, orientation handling, and NPZ writing."
fi

echo "Goal 6 GSE130973 acceptance passed."
