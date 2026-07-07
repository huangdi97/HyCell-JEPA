# Design Summary

HyCell-JEPA v0.1 is a Universal-to-Specific cellular world model engineering prototype for HDF aging, regeneration, and perturbation-planning workflows. It keeps the first system small enough to inspect and run locally while preserving the architectural shape needed for future real biological datasets.

The project is a portfolio-quality engineering MVP, not a biological discovery product. v0.1.1 polishes the documentation and Streamlit presentation around the existing verified v0.1 system without changing the model math.

## 30-Second Architecture Summary

HyCell-JEPA models cell-state change as a transition over compact biological belief states:

- toy HDF-like cells are generated and scored into compact readouts;
- encoders convert state, action, context, and adapter labels into model inputs;
- a small JEPA-style transition core predicts the next compact state;
- a verifier flags overclaim and sanity risks;
- a planner ranks toy action sequences for demonstration only;
- real-data smoke workflows test ingestion, schema validation, and encoder-style projection on GSE130973 without inventing labels.

## Universal-To-Specific CellWorld Idea

The project separates a general transition idea from cell-system-specific adapters:

```text
b_t + a_t + c_t + h_t -> b_{t+1}
```

- `b_t`: compact biological belief state.
- `a_t`: action or perturbation label.
- `c_t`: context, such as timepoint transition or dataset context.
- `h_t`: adapter state for a specific cell system.

The v0.1 implementation uses toy HDF-like states for transition learning and GSE130973 real single-cell matrix smoke workflows for ingestion and encoder plumbing.

## Relationship To Virtual Cell And Transcriptome Foundation Models

HyCell-JEPA is not a complete virtual cell, does not generate whole transcriptomes, and does not reproduce Lingshu-Cell-scale diffusion. It is a compact transition prototype that focuses on the engineering shell around a cellular world model: data contracts, adapter routing, verifier outputs, planner reporting, reproducible scripts, and visible limitations.

Future versions could replace the toy compact readouts or small encoder with stronger biological representations. v0.1 deliberately proves only that the local software path and review surface are coherent.

## Bio-State Encoder

The Bio-State Encoder standardizes compact gene-set readouts and projects them into a small embedding. In the toy workflow, these readouts include senescence, proliferation, ECM/remodeling, stress/inflammation, reprogramming/plasticity, and viability/QC proxy.

The real-data training smoke does not train the JEPA transition core. It runs a deterministic encoder-style projection over the GSE130973 expression matrix to validate real-matrix loading and artifact writing.

## Action Encoder

The Action Encoder encodes toy canonical perturbation labels such as control, aging stress, regeneration, and partial reprogramming. It is used only in the toy transition workflow. Goal 7 does not invent actions or transitions for GSE130973 because the processed matrix has observational or unknown labels.

## Context Encoder

The Context Encoder represents adjacent toy timepoint and cell-system context. This allows the toy transition core to distinguish simple context strings such as timepoint movement within a toy HDF-like system.

## JEPA Transition Core

The JEPA Transition Core is a compact deterministic NumPy ridge-regression head that predicts next compact belief-state features from encoded `b_t + a_t + c_t + h_t`. It is intentionally small and inspectable.

It does not generate full transcriptomes and does not reproduce Lingshu-Cell-scale diffusion.

## HDF Aging/Regeneration Adapter

The HDF adapter maps toy HDF aging, regeneration, and partial-reprogramming scenarios into the transition stack. It is an MVP adapter for toy data, not a validated HDF biological model.

## EvidenceGraph

The EvidenceGraph links toy actions, readouts, assumptions, and limitations. It is a lightweight software evidence object, not a curated biological knowledge graph.

## Biological Verifier

The Biological Verifier returns structured pass/warn/fail outputs and flags overclaim risk. In v0.1, it is a sanity and communication guardrail for toy predictions. It is not biological validation.

## Target-State Planner

The Target-State Planner searches over short toy action sequences to approach a compact target state. Planner outputs are demonstration outputs only and must not be interpreted as recommended interventions or experimental protocols.

## Real-Data Schema

The real-data schema supports small `.csv`, `.npz`, and optional `.h5ad` candidates through a minimal AnnData-like contract:

- expression matrix shape checks
- gene identifier checks
- observation metadata checks
- duplicate and ambiguous-label checks
- allowed cell-system warnings

Schema validation means the file is structurally usable. It does not mean the file is biologically high quality.

## GSE130973 Smoke Integration

Goal 6 added GSE130973 processed GEO Matrix Market ingestion:

- reads `matrix_filtered.mtx.gz`
- reads `genes_filtered.tsv.gz`
- reads `barcodes_filtered.tsv.gz`
- handles genes x cells orientation
- writes a capped cells x genes NPZ

The output is a real single-cell matrix smoke artifact. It is unfiltered human skin single-cell data with unknown age and state labels from the three GEO files alone. It is not HDF-only or fibroblast-only.

Goal 7 added a real-matrix smoke workflow:

- descriptive matrix summary
- deterministic encoder-style projection
- metrics, embeddings, and reports under ignored output paths

## Cloud RTX 4090 Workflow

Goal 5 added a cloud-safe workflow scaffold for RTX 4090 experimentation:

- cloud config with safe defaults
- environment logging
- toy workflow execution
- small result packaging

It does not start remote jobs automatically and does not download large datasets.

## What v0.1 Proves And Does Not Prove

v0.1 proves that the repository has a runnable, testable engineering path from toy compact states through transition modeling, verifier/planner reporting, demo presentation, real-matrix smoke ingestion, and release verification.

v0.1 does not prove biological mechanisms, rejuvenation, regeneration, clinical utility, HDF-specific behavior in GSE130973, full virtual-cell simulation, or intervention recommendations.
