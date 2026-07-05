# Real Data Integration Plan

## Status
Real data integration is planned after the toy pipeline is stable.

## Supported Formats
Future loaders should support:
- `.h5ad`
- `.csv`
- `.npz`

## Required Validation
- AnnData schema validation.
- Required observation fields.
- Required variable/gene identifiers.
- Perturbation/action label mapping.
- Timepoint or condition metadata when available.
- Explicit warnings for missing or ambiguous fields.

## HDF Aging Adapter
The HDF aging adapter should map real dataset metadata into the MVP action, context, and readout conventions.

## Perturbation Adapter
The perturbation adapter should translate dataset-specific perturbation names into canonical MVP action labels while preserving original labels.

## Data Safety
- Do not download large datasets automatically.
- Do not commit large real datasets.
- Keep derived outputs in `outputs/`.
- Document data source, license, preprocessing, and limitations before use.
