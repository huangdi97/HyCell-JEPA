# Cloud RTX 4090 Guide

## Purpose
This guide describes a reproducible cloud smoke workflow for the current HyCell-JEPA MVP on an RTX 4090 instance. It runs toy/fixture-based engineering checks only. It does not download real datasets, train a biological discovery model, or reproduce Lingshu-Cell.

## Cost Assumption
- Target GPU: RTX 4090.
- Estimated rental cost: about 2 CNY/hour.
- Start with verification and short smoke runs, then stop the instance as soon as artifacts are packaged and downloaded.

## Clone The Repo

```bash
git clone <repo-url> HyCell-JEPA
cd HyCell-JEPA
```

Use the actual repository URL for `<repo-url>`.

## Create A Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## Install Dependencies

```bash
pip install -e .
pip install -r requirements.txt
```

If the cloud image already has CUDA/PyTorch installed, keep that environment. The current MVP does not require PyTorch for training, but `scripts/run_cloud_experiment.sh` will report whether `torch.cuda.is_available()` is true if torch is installed.

## Run Local Verification

```bash
pytest
bash scripts/verify_goal5.sh
```

The Goal 5 verifier packages small result artifacts and runs tests. It does not run the full cloud experiment.

## Run The Cloud Experiment In tmux

Start a tmux session:

```bash
tmux new -s hycell-cloud
```

Run the workflow:

```bash
bash scripts/run_cloud_experiment.sh
```

The script writes logs to:

```text
outputs/cloud_run/logs/cloud_experiment.log
```

Detach from tmux:

```bash
Ctrl-b d
```

Reattach later:

```bash
tmux attach -t hycell-cloud
```

## Package Results

```bash
python scripts/package_results.py --out outputs/hycell_cloud_results.zip
```

The package includes small configs, docs, metrics, and markdown reports when present. It intentionally avoids raw data, checkpoints, `.pt`, `.ckpt`, `.npy`, `.npz`, `.h5ad`, and large data directories.

## Download Results

From your local machine:

```bash
scp user@cloud-host:/path/to/HyCell-JEPA/outputs/hycell_cloud_results.zip .
scp user@cloud-host:/path/to/HyCell-JEPA/outputs/cloud_run/logs/cloud_experiment.log .
```

Replace `user`, `cloud-host`, and `/path/to/HyCell-JEPA` with the actual cloud connection details.

## What Not To Commit
- `outputs/`
- `data/raw/`
- `data/processed/`
- Checkpoints such as `*.pt`, `*.pth`, `*.ckpt`
- Arrays and dataset files such as `*.npy`, `*.npz`, `*.h5ad`
- Packaged archives such as `*.zip`
- `*.egg-info/`
- `__pycache__/`

## Current MVP Limitation
`configs/train_cloud_4090.yaml` includes cloud-intent fields such as `n_cells`, `n_genes`, `latent_dim`, `hidden_dim`, `batch_size`, `epochs`, and `precision`. The current compact NumPy trainer only consumes the existing toy training fields and embedding dimensions. `scripts/run_cloud_experiment.sh` generates a larger toy NPZ matrix for cloud I/O smoke readiness, while the compact JEPA trainer still trains on configured toy gene-set scores.

This is an engineering workflow limitation, not a biological result.

## Common Failure Fixes
- `python: command not found`: activate the virtual environment or set `PYTHON=/path/to/python`.
- `pytest` missing: run `pip install -r requirements.txt`.
- `streamlit` missing for demo work: run `pip install -r requirements.txt`.
- `nvidia-smi not available`: confirm the cloud instance has GPU drivers attached; the current toy workflow can still run on CPU.
- Package is too large: confirm you used `scripts/package_results.py` and did not manually zip `outputs/` or checkpoints.
- Cloud bill growing: detach only when needed, monitor the run, download the zip/logs, then stop or destroy the instance.
