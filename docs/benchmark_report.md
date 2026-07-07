# Benchmark Report

## Summary

HyCell-JEPA v0.1 has three benchmark-style checks:

- Toy transition benchmark over compact gene-set readouts.
- Toy planner/verifier smoke benchmark.
- GSE130973 real-matrix evaluation and encoder smoke.

All metrics below are engineering smoke metrics. They do not establish biological validity.

## What This Proves

- The toy transition pipeline can generate, score, train, evaluate, and report compact readout transitions reproducibly.
- The verifier and planner CLIs run against the toy compact-state workflow and produce structured reports.
- The GSE130973 workflow can inspect, prepare, validate, summarize, and run an encoder-style smoke pass on a real single-cell matrix.
- Release verification can rerun the project contracts end to end.

## What This Does Not Prove

- Biological mechanisms.
- Rejuvenation or regeneration.
- HDF-specific behavior in GSE130973.
- Fibroblast-only or HDF-only real-data conclusions.
- Wet-lab validity.
- Clinical usefulness.
- Correct intervention planning.
- Full virtual-cell or transcriptome foundation-model capability.

## Toy Benchmark

Command:

```bash
python scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
```

Accepted toy metrics:

- Toy score transitions: 8.
- Training transitions: 6.
- Held-out eval transitions: 2.
- Training MSE: `0.000000375`.
- Held-out eval MSE: `0.058339536`.
- All-transition evaluation MSE: `0.014585165`.
- Goal 3 benchmark transition MSE: `0.014585165`.
- Verifier status counts: `{"warn": 8}`.

Per-feature all-transition MSE:

- `ecm_remodeling`: `0.005293832`.
- `proliferation`: `0.012120207`.
- `reprogramming_plasticity`: `0.025554769`.
- `senescence`: `0.033552743`.
- `stress_inflammation`: `0.010538928`.
- `viability_qc_proxy`: `0.000450512`.

## Planner Example

Command:

```bash
python scripts/run_planner.py --checkpoint outputs/checkpoints/best_jepa.pt --state aged_hdf --target rejuvenated_repair
```

Example accepted output:

```text
1. aging_stress -> regeneration | distance=0.458229
2. partial_reprogramming -> regeneration | distance=0.497030
3. control -> regeneration | distance=0.620774
```

Planner sequences are toy software outputs, not recommended interventions.

## Real-Data Smoke Training Summary

Commands:

```bash
python scripts/eval_real_smoke.py --input data/processed/gse130973/gse130973_smoke.npz
python scripts/train_real_smoke.py --config configs/train_gse130973_smoke.yaml
```

Observed GSE130973 smoke values:

- Shape: 5000 cells x 2000 genes.
- Zero fraction: `0.960690`.
- Mean expression: `0.126344`.
- Encoder latent dimension: 64.
- Outputs: metrics JSON, embeddings `.npy`, and Markdown reports under ignored `outputs/` paths.

## What Metrics Mean

The toy MSE values show that the deterministic compact transition pipeline can fit and evaluate a tiny synthetic transition table.

The planner distances show that the search code can rank toy action sequences under a compact target-state distance.

The real-data smoke metrics show that the project can load, summarize, and project a real expression matrix.

## Next Evaluation Plan

- Add reliable GSE130973 metadata and cell-type annotation.
- Create a documented HDF/fibroblast subset only when supported by metadata.
- Add a small perturbation dataset such as scPerturb for real perturbation labels.
- Add verifier checks grounded in documented evidence rather than toy assumptions.
- Track runtime and memory budgets on local 4060 Ti and cloud RTX 4090.
