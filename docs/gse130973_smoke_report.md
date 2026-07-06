# GSE130973 Real-Data Training Smoke

This report describes the Goal 7 smoke workflow for the processed GSE130973 subset. The workflow is engineering validation only: it checks that HyCell-JEPA can load the real processed NPZ, summarize the matrix, and run a deterministic lightweight encoder-style pass over expression values.

## What Was Run

```bash
python scripts/eval_real_smoke.py --input data/processed/gse130973/gse130973_smoke.npz
python scripts/train_real_smoke.py --config configs/train_gse130973_smoke.yaml
```

The training smoke writes:
- `outputs/gse130973_smoke/real_smoke_metrics.json`
- `outputs/gse130973_smoke/real_smoke_embeddings.npy`
- `outputs/reports/gse130973_real_smoke_report.md`

The matrix summary writes:
- `outputs/reports/gse130973_real_matrix_summary.json`
- `outputs/reports/gse130973_real_matrix_summary.md`

## What Is Validated

- The processed GSE130973 NPZ contains the required project keys.
- The matrix can be loaded as cells x genes.
- Descriptive matrix statistics can be computed.
- A deterministic, lightweight encoder-style projection can create embeddings from the real expression matrix.
- Output artifacts are written to ignored generated-output paths.

## What Is Not Validated

- This is not biological validation.
- This does not train a perturbation-transition model.
- This does not train or validate a planner.
- This does not infer donor ages, rejuvenation, HDF-specific behavior, fibroblast-only state, or treatment effects.
- This does not reproduce Lingshu-Cell or train a full transcriptome model.

## Current Limitation

The three processed GEO files used for Goal 6 provide expression values, genes, and barcodes only. The resulting Goal 7 smoke workflow therefore runs on unfiltered human skin single-cell data with `age_label = unknown` and `state_label = unknown`.

## Next Step

Add reliable metadata or cell-type annotations, then create a documented HDF/fibroblast subset before attempting HDF-specific modeling or biological interpretation.
