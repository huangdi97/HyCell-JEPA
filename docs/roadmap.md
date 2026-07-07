# Roadmap

## v0.1 - Engineering MVP And Real-Data Smoke

Status: current release target.

- Deterministic toy HDF-like perturbation workflow.
- Compact encoders and JEPA transition core.
- HDF adapter, verifier, planner, benchmark, and Streamlit demo.
- Real-data schema validation.
- GSE130973 Matrix Market ingestion.
- GSE130973 real-matrix evaluation and encoder smoke.
- Cloud RTX 4090 workflow scaffold.
- Goal-level and release-level verifier scripts.

## v0.2 - GSE130973 Metadata And HDF Subset

- Add reliable sample metadata if available.
- Add cell-type annotation or a documented annotation workflow.
- Create a documented HDF/fibroblast subset only when supported by metadata.
- Preserve unknown labels when metadata is absent.

## v0.3 - Small scPerturb Integration

- Add a small, controlled perturbation dataset.
- Validate perturbation labels against the real-data schema.
- Keep fixtures tiny and deterministic.

## v0.4 - Real Perturbation Benchmark

- Evaluate real perturbation labels with compact belief-state readouts.
- Add baseline comparisons.
- Track runtime and memory budgets.

## v0.5 - Stronger Verifier And Evidence Grounding

- Connect verifier rules to explicit evidence records.
- Add richer failure modes for unsupported claims.
- Improve reportability for biological uncertainty.

## v1.0 - Reproducible AI4LifeScience Research Prototype

- Reproducible real-data benchmark suite.
- Documented metadata provenance.
- Stronger evidence graph.
- Clear model cards, data cards, and release contracts.
- Still no clinical or wet-lab claims without external validation.
