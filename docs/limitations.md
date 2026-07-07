# Limitations

## Not Clinical Advice

HyCell-JEPA is not a clinical, diagnostic, therapeutic, dosing, or patient-care system. It must not be used to guide treatment, biological intervention decisions, or wet-lab protocols.

## Not Wet-Lab Validated

No HyCell-JEPA output has been validated experimentally. The repository contains software smoke workflows and toy benchmarks only.

## Not A Complete Virtual Cell

The MVP models compact biological belief states and toy perturbation transitions. It does not simulate all cellular processes or represent a complete virtual cell.

## Not Lingshu-Cell-Scale

The MVP does not reproduce Lingshu-Cell and does not implement full 18,000-gene transcriptome diffusion. It is intentionally small enough to run on modest local hardware.

## Toy Data Is Engineering Validation Only

Toy data exists to validate file formats, gene-set scoring, model plumbing, verifier behavior, planner behavior, benchmark scripts, and demo flows. Toy results are not biological discoveries.

## GSE130973 Smoke Is Real-Matrix Engineering Validation Only

The GSE130973 workflows prove that the project can inspect, prepare, validate, summarize, and run a lightweight encoder-style smoke pass on a real public single-cell matrix.

They do not prove biological mechanisms, aging biology, rejuvenation, regeneration, or intervention effects.

## Current GSE130973 Labels Are Unknown

The three processed GEO matrix files used by the smoke workflow do not provide reliable donor age or sample-state metadata. The processed smoke file therefore uses:

- `age_label = unknown`
- `state_label = unknown`

No age or state labels are inferred.

## Current GSE130973 Is Not HDF-Only

The processed smoke file is unfiltered human skin single-cell data:

```text
cell_system = skin_single_cell_unfiltered
```

It is not fibroblast-only and not HDF-only. Downstream HDF filtering requires reliable metadata or cell-type annotation.

## Planner Outputs Are Demonstrations

Planner outputs operate on toy compact readout states. They are demonstration outputs for software validation, not therapy recommendations, experimental protocols, or biological advice.

## Generated Data Should Stay Out Of Git

Do not commit raw datasets, processed data, checkpoints, embeddings, outputs, `.npz`, `.npy`, `.h5ad`, `.pt`, `.ckpt`, or `.zip` artifacts.
