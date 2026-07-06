#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "No Python executable found. Set PYTHON=/path/to/python and rerun." >&2
  exit 127
fi

mkdir -p outputs/cloud_run outputs/cloud_run/logs outputs/cloud_run/reports
LOG_PATH="outputs/cloud_run/logs/cloud_experiment.log"

exec > >(tee "$LOG_PATH") 2>&1

echo "HyCell-JEPA cloud RTX 4090 workflow"
date
echo "Git commit: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo "Python version:"
$PYTHON_BIN --version
echo "Torch availability:"
$PYTHON_BIN - <<'PY'
try:
    import torch
    print(f"torch={torch.__version__} cuda_available={torch.cuda.is_available()}")
except Exception as exc:
    print(f"torch unavailable: {exc}")
PY
echo "nvidia-smi:"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not available"
fi
echo "Disk usage:"
df -h . || true

echo "Generating cloud-sized toy NPZ smoke matrix."
$PYTHON_BIN scripts/make_toy_data.py \
  --n_cells 20000 \
  --n_genes 4000 \
  --out outputs/cloud_run/cloud_toy_cells.npz \
  --seed 20260706

echo "Training compact encoders with cloud config."
$PYTHON_BIN scripts/train_encoder.py --config configs/train_cloud_4090.yaml

echo "Training compact JEPA transition core with cloud config."
$PYTHON_BIN scripts/train_jepa.py --config configs/train_cloud_4090.yaml

echo "Running benchmark."
$PYTHON_BIN scripts/eval_benchmark.py --checkpoint outputs/checkpoints/best_jepa.pt

echo "Running planner."
$PYTHON_BIN scripts/run_planner.py \
  --checkpoint outputs/checkpoints/best_jepa.pt \
  --state aged_hdf \
  --target rejuvenated_repair

echo "Cloud workflow complete. Logs: $LOG_PATH"
