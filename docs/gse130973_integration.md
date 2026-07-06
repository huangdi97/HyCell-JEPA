# GSE130973 Integration

GSE130973 is a public single-cell human skin aging dataset. HyCell-JEPA uses it only as a first real-data smoke workflow: can the project inspect local GEO processed files, read a sparse Matrix Market expression matrix, and write a small project-compatible NPZ?

This workflow does not download data and does not make biological claims.

## Files To Download Manually

Place these processed GEO files here:

```text
data/raw/gse130973/GSE130973_barcodes_filtered.tsv.gz
data/raw/gse130973/GSE130973_genes_filtered.tsv.gz
data/raw/gse130973/GSE130973_matrix_filtered.mtx.gz
```

The expected source is the GEO GSE130973 supplementary processed files.

## Inspect Local Files

```bash
python scripts/inspect_gse130973.py --raw-dir data/raw/gse130973
```

This prints file existence, file sizes, matrix shape, gene and barcode counts, previews, orientation, and obvious mismatches.

## Prepare Smoke NPZ

```bash
python scripts/prepare_gse130973.py \
  --raw-dir data/raw/gse130973 \
  --out data/processed/gse130973/gse130973_smoke.npz \
  --max-cells 5000 \
  --max-genes 2000
```

The prepared file contains:
- `expression`
- `gene_names`
- `cell_ids`
- `dataset_id`
- `source`
- `is_real_data`
- `note`
- `state_label`
- `age_label`

Because the three filtered files do not include donor age or sample metadata, state and age labels are set to `unknown`.
Duplicate gene symbols are disambiguated with deterministic suffixes such as `__dup2` so the project schema can validate unique gene identifiers.
The prepared artifact uses `cell_system = skin_single_cell_unfiltered` because the smoke matrix is unfiltered human skin single-cell data, not yet HDF-only data.

## Validate Prepared Artifact

```bash
python scripts/validate_dataset.py --input data/processed/gse130973/gse130973_smoke.npz
```

The validator checks the project-compatible shape and metadata contract. It does not validate biological quality.

## Goal 6 Acceptance

```bash
bash scripts/verify_goal6.sh
```

If the real raw files are missing, the verifier prints a clear skip message and still runs fixture tests that exercise Matrix Market loading, orientation handling, and NPZ writing.

## Limitations

- No data is downloaded by scripts or tests.
- Real raw and processed files remain ignored and must not be committed.
- The matrix is capped deterministically for a smoke artifact, not for analysis.
- No donor age labels are invented.
- No fibroblast-only or HDF-only filtering is claimed from the three raw files.
- Downstream HDF filtering requires reliable metadata or cell-type annotation that is not present in the three GEO matrix files alone.
- Age labels remain `unknown` from the three GEO matrix files alone.
- No rejuvenation, aging mechanism, or treatment conclusion can be drawn from this workflow.
