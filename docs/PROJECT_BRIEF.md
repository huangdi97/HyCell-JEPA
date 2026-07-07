# HyCell-JEPA Project Brief

## One-Line Project Goal
Build a runnable MVP engineering prototype of a Universal-to-Specific Cellular World Model for HDF aging, regeneration, and partial reprogramming.

## Scientific Positioning
HyCell-JEPA explores whether cellular perturbation dynamics can be represented as a transition over compact biological belief states rather than as full transcriptome generation. The MVP focuses on small, inspectable, toy single-cell perturbation data and gene set readouts so the software architecture can be validated before real biological claims are attempted.

This project is not a full virtual cell, not a clinical recommendation system, and not a Lingshu-Cell-scale model.

## MVP Scope
- Toy single-cell perturbation dataset for HDF-like aging, regeneration, and partial reprogramming scenarios.
- Gene set scoring over small curated marker groups.
- Evidence graph linking actions, readouts, states, and assumptions.
- Bio-State Encoder, Action Encoder, Context Encoder, and JEPA Transition Core.
- HDF Adapter for cell-system-specific conditioning.
- Biological Verifier to check consistency and reject overclaims.
- Target-State Planner for selecting plausible action sequences.
- Benchmark scripts and a Streamlit demo.
- Documentation, configs, tests, and CLI entry points.

## Not In MVP Scope
- Reproducing Lingshu-Cell.
- Modeling an 18,000-gene transcriptome diffusion system.
- Downloading huge datasets automatically.
- Treating toy-data outputs as biological discoveries.
- Clinical, diagnostic, therapeutic, or dosing recommendations.
- Large-scale cloud training by default.

## HDF Cell System
The first target cell system is human dermal fibroblast-like data focused on aging, regeneration, and partial reprogramming. The MVP should use a small synthetic/toy dataset first, then later support real h5ad/csv/npz inputs with explicit schema validation.

## Main Actions
- Aging-like stress or senescence induction.
- Regeneration-supporting perturbations.
- Partial reprogramming-inspired perturbations.
- Control/no-op action.
- Future real-data adapters may map these actions to dataset-specific perturbation labels.

## Main Readouts
- Cell cycle/proliferation score.
- Senescence score.
- ECM/remodeling score.
- Stress/inflammatory score.
- Reprogramming/plasticity score.
- Viability or quality-control proxy score.

## Final MVP Success Commands
The final MVP should support commands similar to:

```bash
python scripts/make_toy_data.py --config configs/toy_data.yaml
python scripts/score_gene_sets.py --input outputs/toy_data/toy_cells.csv --config configs/gene_sets.yaml
python scripts/train_jepa.py --config configs/jepa_toy.yaml
python scripts/benchmark_toy.py --config configs/benchmark_toy.yaml
python -m streamlit run scripts/demo_app.py
pytest
```

Exact command names may evolve, but each major script must keep a CLI entry point and documentation.
