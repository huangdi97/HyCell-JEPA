# Real Data Integration Plan

## Status
Real data integration scaffolding exists. The repository can validate tiny candidate `.csv`, `.npz`, and optionally `.h5ad` files against a minimal AnnData-like schema, map perturbation labels to canonical MVP actions, and map HDF aging metadata into MVP context conventions.

No real datasets are included. No dataset downloads happen automatically.

## Supported Formats
Current loader interfaces:
- `.csv` via `src/hycell/data_loaders.py`
- `.npz` via `src/hycell/data_loaders.py`
- `.h5ad` via optional `anndata`; if `anndata` is missing, the loader raises an actionable dependency message.

Validation CLI:

```bash
python scripts/validate_dataset.py --input path/to/dataset.csv --schema configs/real_data_schema.yaml
```

## Required Validation
- AnnData-like schema validation through `AnnDataSchemaValidator`.
- Required observation fields: `cell_id`, `perturbation`, `timepoint`, and `cell_system`.
- Required gene/variable identifiers through `var_names` or CSV gene columns.
- Perturbation/action label mapping through `PerturbationAdapter`.
- HDF context mapping through `HDFAgingMetadataAdapter`.
- Explicit errors for missing required fields, empty perturbations, shape mismatches, duplicate IDs, duplicate gene names, and ambiguous perturbation labels.
- Explicit warnings for unexpected cell-system values.
- Allowed cell-system values include HDF labels for HDF-specific fixtures and unfiltered human skin single-cell labels for dataset-level smoke artifacts such as GSE130973.

## GSE130973 Skin Smoke Label
GSE130973 smoke output uses `cell_system = skin_single_cell_unfiltered`. This is intentional: the three processed GEO matrix files provide expression values, genes, and barcodes, but they do not provide enough metadata to claim HDF-only or fibroblast-only filtering.

The smoke artifact should be treated as unfiltered human skin single-cell data. Downstream HDF-specific filtering requires reliable metadata or cell-type annotation before any cell can be labeled as HDF or fibroblast. Age labels also remain `unknown` from the three GEO matrix files alone.

## HDF Aging Adapter
`HDFAgingMetadataAdapter` maps validated metadata into:
- `cell_id`
- `original_perturbation`
- `canonical_action`
- `mapping_status`
- `timepoint`
- `cell_system`
- `adapter_label`
- `context_label`

## Perturbation Adapter
`PerturbationAdapter` translates dataset-specific perturbation labels into canonical MVP action labels while preserving the original label. Unknown labels map to `canonical_action = "unknown"` with `mapping_status = "unknown"` so downstream code can fail or warn explicitly.

## Data Safety
- Do not download large datasets automatically.
- Do not commit large real datasets.
- Keep derived outputs in `outputs/`.
- Document data source, license, preprocessing, and limitations before use.
- Validation success only means the file has the expected shape and metadata fields; it does not imply biological quality.
