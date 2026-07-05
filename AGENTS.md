# HyCell-JEPA Agent Guide

## Project Purpose
HyCell-JEPA is a Universal-to-Specific Cellular World Model prototype for HDF aging, regeneration, and partial reprogramming. The MVP is an engineering prototype, not a biological discovery product. It should keep a runnable toy pipeline while gradually adding data loaders, encoders, transition modeling, verification, planning, benchmarks, and a Streamlit demo.

Core transition idea:

```text
b_t + a_t + c_t + h_t -> b_{t+1}
```

Where `b_t` is the biological belief state, `a_t` is an intervention/action, `c_t` is context, and `h_t` is cell-system-specific adapter state.

## Hardware Constraints
- Primary local machine: Windows 11, WSL2, RTX 4060 Ti 16GB, 32GB RAM.
- Cloud option: RTX 4090, approximately 2 CNY/hour.
- Keep local defaults modest enough to run on the local machine.
- Do not add workflows that require very large datasets, long training runs, or unavailable GPU memory by default.

## Implementation Constraints
- Do not reproduce Lingshu-Cell.
- Do not implement 18,000-gene transcriptome diffusion in the MVP.
- Do not download huge datasets automatically.
- Do not claim toy-data results are biological discoveries.
- Keep the toy pipeline runnable at all times.
- Every future major module should have focused tests.
- Every script should expose a CLI entry point.
- Keep configs in `configs/`.
- Keep generated outputs in `outputs/`.
- Avoid committing large generated files, datasets, checkpoints, or caches.

## Testing Policy
- Run the smallest relevant tests after each change.
- Add or update tests for each major module.
- Keep toy fixtures small and deterministic.
- Prefer explicit CLI verification commands in documentation and goal files.
- If tests cannot be run, record why in `docs/progress_log.md`.

## Documentation Requirements
- Keep `docs/progress_log.md` current after meaningful work.
- Update `docs/PROJECT_BRIEF.md` when project scope, success criteria, or architecture changes.
- Add design decisions to `08_Decisions/` when choices affect future implementation.
- Keep user-facing limitations visible in `README.md` and `docs/limitations.md`.

## Final Required Commands
Before finishing a future goal, run the relevant checks plus:

```bash
find . -maxdepth 3 -type f | sort
git status
```

When Python modules, scripts, or tests exist, future goals should also run the project-specific verification commands documented in the active goal file.
