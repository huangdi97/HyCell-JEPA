# HyCell-JEPA

Universal-to-Specific Cellular World Model prototype for HDF aging, regeneration, and partial reprogramming.

## Current Status
This repository is currently a scaffold and planned MVP workspace. It is not yet a completed biological discovery system, not a clinical tool, and not a full virtual cell model.

The immediate purpose of this repository is to preserve project context and prepare a runnable toy engineering pipeline. Future goals will add toy perturbation data, gene set scoring, model components, benchmarks, a Streamlit demo, and eventually real-data integration.

## Core Idea

```text
b_t + a_t + c_t + h_t -> b_{t+1}
```

HyCell-JEPA will model transitions from a current biological belief state, action, context, and HDF-specific adapter state into a predicted next biological belief state.

## MVP Direction
- Start with small toy single-cell perturbation data.
- Score compact gene sets for engineering validation.
- Build encoders and a JEPA-style transition core.
- Add an HDF adapter, biological verifier, planner, benchmark, and demo.
- Integrate real h5ad/csv/npz data only after the toy pipeline is stable.

## Limitations
- Toy data is for engineering validation only.
- Outputs must not be interpreted as biological discoveries.
- This project does not provide medical or clinical recommendations.
- This MVP does not reproduce Lingshu-Cell or train an 18,000-gene transcriptome diffusion model.

## Repository Map
- `00_Control/` - Obsidian project control notes.
- `01_Design/` - design notes and sketches.
- `02_Codex_Goals/` - copy-pasteable Codex goal prompts.
- `03_Progress/` - daily notes.
- `04_Data/` - data notes and small metadata only.
- `05_Experiments/` - experiment logs.
- `06_Bugs/` - bug reports.
- `07_Reading/` - paper and reading notes.
- `08_Decisions/` - design decision records.
- `docs/` - project documentation.
- `configs/` - configuration files.
- `scripts/` - CLI scripts.
- `src/hycell/` - Python package source.
- `tests/` - tests.
- `outputs/` - generated outputs.

## Planned Verification
The final MVP should eventually support:

```bash
pytest
streamlit run scripts/demo_app.py
```

For now, the bootstrap verification is:

```bash
find . -maxdepth 3 -type f | sort
git status
```
