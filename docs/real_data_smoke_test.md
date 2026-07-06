# Real Data Smoke Test

## Purpose
The Goal 4.5 smoke workflow checks that HyCell-JEPA can inspect, validate, and lightly preprocess a small local single-cell-like dataset without downloading data or making biological claims.

This workflow is for engineering validation only. Passing it means the local file has the expected shape and metadata fields; it does not mean the dataset is biologically valid.

## Required Local Input
Use a small local `.csv`, `.npz`, or `.h5ad` candidate dataset. The repository does not download data automatically.

Expected metadata fields:
- `cell_id`
- `perturbation`
- `timepoint`
- `cell_system`

CSV files should include those metadata columns plus numeric gene-expression columns. NPZ files should include `expression` or `X`, `gene_names` or `var_names`, and per-cell metadata arrays.

## Inspect A Dataset

```bash
python scripts/inspect_dataset.py --input path/to/small_dataset.csv --output outputs/reports/real_data_inspection.json
```

If no input is provided or the file is missing, the script exits with a clear message and does not download anything.

## Preprocess A Dataset

```bash
python scripts/preprocess_data.py \
  --input path/to/small_dataset.csv \
  --output outputs/real_data_smoke/preprocessed_cells.csv \
  --report outputs/real_data_smoke/preprocess_report.json
```

The normalized output preserves original perturbation labels alongside canonical action labels.

## Verification

```bash
bash scripts/verify_goal4_real_smoke.sh
```

The verifier creates a tiny local fixture under `outputs/test_tmp/`, runs the inspect and preprocess CLIs, checks the graceful missing-file path, and confirms the existing toy and Goal 4 acceptance paths still pass.
