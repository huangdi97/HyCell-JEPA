# Model Card

## Model Status
Goal 2 implements the first compact toy JEPA transition model. It is a deterministic NumPy-based engineering model over gene-set readout features, not a full biological model.

## Implemented Components
- Bio-State Encoder: standardizes compact gene-set readout features and projects them to a small embedding.
- Action Encoder: one-hot encodes canonical toy perturbation labels and projects them to a small embedding.
- Context Encoder: encodes adjacent toy timepoint/cell-system context labels.
- Adapter placeholder encoder: encodes the toy cell-system label as `h_t`.
- JEPA Transition Core: ridge-regression linear head predicting next compact belief-state features from encoded `b_t + a_t + c_t + h_t`.
- HDF Adapter: maps toy HDF actions and adjacent timepoint contexts into model inputs.
- Biological Verifier: returns structured pass/warn/fail results with toy-only warnings and basic sanity checks.
- Target-State Planner: searches tiny toy action sequences toward a compact target state.

The current model predicts six compact toy readouts: senescence, proliferation, ECM/remodeling, stress/inflammation, reprogramming/plasticity, and viability/QC proxy.

## Intended Use
Engineering validation of a cellular world model prototype using toy data first, then carefully validated real data.

## Out-of-Scope Use
- Clinical recommendations.
- Biological discovery claims from toy data.
- Full transcriptome generation.
- Lingshu-Cell-scale modeling.

## Current Toy Evaluation
Latest Goal 2 smoke run:
- Training transitions: 6
- Held-out eval transitions: 2
- Training MSE: `0.000000375`
- Held-out eval MSE: `0.058339536`
- All-transition evaluation MSE: `0.014585165`
- Goal 3 benchmark transition MSE: `0.014585165`
- Goal 3 benchmark planner sequence: `regeneration -> control`
- Verifier status counts in benchmark: 8 warnings, 0 failures

These metrics are software smoke-test metrics only. They are not biological validation.

## Evaluation Plan
Future benchmark reports should add verifier behavior, planner sanity checks, demo smoke tests, real-data schema validation, and runtime constraints.
