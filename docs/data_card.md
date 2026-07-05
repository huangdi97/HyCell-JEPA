# Data Card

## Dataset Status
The project will begin with a small toy single-cell perturbation dataset. Real data integration is planned for a later goal.

## Toy Data Purpose
Toy data is for engineering validation only. It should test data loading, gene set scoring, encoders, transition modeling, benchmarking, and demo flows.

## Planned Toy Data Contents
- HDF-like cells.
- Small marker gene panel.
- Perturbation labels for control, aging-like stress, regeneration-like action, and partial reprogramming-like action.
- Timepoint or pseudo-time metadata.
- Compact readout scores.

## Real Data Plan
Future goals will add loaders for h5ad, csv, and npz formats, plus an AnnData schema validator and dataset-specific adapters.

## Restrictions
- Do not download large datasets automatically.
- Do not commit large data files.
- Clearly mark toy data as synthetic or toy.
- Do not claim toy-data behavior is biological evidence.
